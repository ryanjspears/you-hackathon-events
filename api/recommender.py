"""Phase 2: build a preference profile from what the user did, score future events in the sandbox."""
from __future__ import annotations

import json
import pathlib
import re
import threading
import time
from collections import Counter
from datetime import datetime

from api import mem, sandbox, store, trace
from api.progress import emit

RECOMMEND_SRC = (pathlib.Path(__file__).parent / "scripts" / "recommend_v0.py").read_text()


def _norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def build_profile(user: str) -> dict:
    """Weights from 'going' (strong), searches (weak), 'skip' (negative)."""
    tags: Counter = Counter()
    platforms: Counter = Counter()
    venues: Counter = Counter()
    for e in store.interactions(user, "going"):
        for t in e.get("tags") or []:
            tags[t] += 2
        if e.get("platform"):
            platforms[e["platform"]] += 1
        if e.get("venue"):
            venues[_norm(e["venue"])] += 1
    for e in store.interactions(user, "skip"):
        for t in e.get("tags") or []:
            tags[t] -= 1
    for s in store.recent_searches(user, 10):
        for c in s["plan"].get("categories") or []:
            tags[_norm(c).replace(" ", "-")] += 0.5
    city = next((s["plan"].get("city") for s in store.recent_searches(user, 5) if s["plan"].get("city")), None)
    cities: list[str] = []  # everywhere they've looked or are going, most recent first
    for c in [*(s["plan"].get("city") for s in store.recent_searches(user, 10)),
              *(e.get("city") for e in store.interactions(user, "going"))]:
        if c and c not in cities:
            cities.append(c)
    return {"tags": {k: v for k, v in tags.items() if v > 0}, "platforms": dict(platforms),
            "venues": dict(venues), "price_free_bias": 0.0, "city": city, "cities": cities[:4]}


def describe(profile: dict) -> str | None:
    top = [t for t, _ in Counter(profile["tags"]).most_common(4)]
    plats = [p for p, _ in Counter(profile["platforms"]).most_common(2)]
    if not top and not plats:
        return None
    bits = []
    if top:
        bits.append("likes " + ", ".join(top))
    if plats:
        bits.append("finds events on " + ", ".join(plats))
    if profile.get("city"):
        bits.append(f"in {profile['city']}")
    return "; ".join(bits)


_refresh_lock = threading.Lock()  # sandbox runs share script.py/input.json, so re-ranks go one at a time
_inflight: set[str] = set()


def is_refreshing(user: str) -> bool:
    return user in _inflight


def is_stale(user: str) -> bool:
    """True when the user did something (search, going, skip) after the ranking was last written."""
    ranked, acted = store.recommendations_ts(user), store.last_activity_ts(user)
    return acted is not None and (ranked is None or acted > ranked)


def refresh_in_background(user: str) -> bool:
    """Re-rank on a thread unless one is already queued for this user. Returns whether one was started."""
    if user in _inflight:
        return False
    _inflight.add(user)

    def run():
        trace.begin("refresh", user=user)
        try:
            with _refresh_lock:
                refresh(user)
        except Exception as e:  # never let a background re-rank take the API down
            emit("recommend", text=f"recommender failed: {str(e)[:200]}")
        finally:
            _inflight.discard(user)
            trace.finish()

    threading.Thread(target=run, name=f"refresh-{user}", daemon=True).start()
    return True


def refresh(user: str, now_iso: str | None = None) -> list[dict]:
    now_iso = now_iso or datetime.now().astimezone().isoformat()
    profile = build_profile(user)
    exclude = [e["id"] for e in store.interactions(user)]
    candidates = store.future_events(profile.get("cities") or profile.get("city"), now_iso)
    if not candidates or not (profile["tags"] or profile["platforms"]):
        store.save_recommendations(user, [])
        return []
    emit("recommend", text=f"scoring {len(candidates)} events for {user} in the sandbox")
    with trace.span("recommender.score", candidates=len(candidates)):
        res = sandbox.sandbox_run(RECOMMEND_SRC, {"profile": profile, "candidates": candidates, "exclude": exclude})
    if res["exit_code"] != 0:
        emit("recommend", text=f"recommender failed: {res['stderr'][-300:]}")
        return []
    ranked = json.loads(res["stdout"]).get("ranked", [])
    store.save_recommendations(user, ranked)
    return store.get_recommendations(user)


def on_interaction(user: str, event: dict, kind: str) -> None:
    """Record the preference signal in One's memory, then re-rank."""
    profile = build_profile(user)
    if kind == "going":
        tags = ", ".join((event.get("tags") or [])[:3]) or "this kind of event"
        mem.learn(user, f"Went to '{event.get('title')}' ({event.get('platform') or 'web'}"
                        f"{', ' + event['venue'] if event.get('venue') else ''}); likes {tags}", tags=["going"], weight=7)
    summary = describe(profile)
    if summary:
        mem.learn_profile(user, f"Profile: {summary}")
    with _refresh_lock:
        refresh(user)
