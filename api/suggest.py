"""Home-page prompt chips built from what the user searched and picked (SPEC §3c).

Pure templates over SQLite data: no LLM, no memory call, answers in milliseconds. The phrasing
mirrors what the Planner already parses ("jazz shows in Brooklyn, NY next week"), so a chip
never triggers a clarifying question.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from api import recommender, store

GENERIC = ["jazz shows in Brooklyn this weekend", "AI meetups in NYC next week", "techno parties in Manhattan Friday night"]
WINDOWS = ["tonight", "this weekend", "next week", "next weekend"]
SHOWS = {"jazz", "techno", "house", "indie", "comedy", "blues", "punk", "folk"}
MEETUPS = {"ai", "startup", "tech", "founders", "python", "crypto"}
UPPER = {"ai": "AI", "nyc": "NYC"}


def _norm(s: str | None) -> str:
    return recommender._norm(s)


def phrase(topic: str) -> str:
    """'live-music' → 'live music', 'jazz' → 'jazz shows', 'ai' → 'AI meetups'."""
    t = _norm(topic.replace("-", " "))
    if not t:
        return ""
    if t in SHOWS:
        return f"{t} shows"
    if t in MEETUPS:
        return f"{UPPER.get(t, t)} meetups"
    return " ".join(UPPER.get(w, w) for w in t.split())


def _topic(plan: dict) -> str | None:
    cats = plan.get("categories") or []
    return cats[0] if cats else (plan.get("keywords") or None)


def _day(iso: str | None) -> date | None:
    if not iso or len(iso) < 10:
        return None
    try:
        return date.fromisoformat(iso[:10])
    except ValueError:
        return None


def previous_window(plan: dict) -> str:
    """The window a past search covered, from its label or its resolved dates."""
    w = (plan.get("date_window") or "").strip().lower()
    if w in WINDOWS:
        return w
    a, b = _day(plan.get("date_from")), _day(plan.get("date_to"))
    if a and b:
        span = (b - a).days + 1
        return "tonight" if span <= 1 else "this weekend" if span <= 3 else "next week"
    return "this weekend"


def shift_window(w: str) -> str:
    """Next window after the one already searched; never cycles back to 'tonight'."""
    i = WINDOWS.index(w) if w in WINDOWS else 1
    return WINDOWS[i + 1] if i + 1 < len(WINDOWS) else "this weekend"


def suggest(searches: list[dict], going: list[dict], profile: dict, today: date, limit: int = 4) -> list[dict]:
    """Ranked chips: what they're going to → tags they keep picking → past searches shifted forward."""
    limit = max(3, min(limit, 5))
    plans = [s for s in searches if s.get("plan", {}).get("city") and _topic(s["plan"])]
    home = profile.get("city") or next((e.get("city") for e in going if e.get("city")), None)
    if not home and not going:
        return [{"text": t, "why": "", "kind": "search"} for t in GENERIC[:limit]]

    out: list[dict] = []
    seen: set[tuple[str, str]] = set()
    latest_msg = (searches[0].get("message") or "").strip().lower() if searches else ""

    def add(topic: str, city: str | None, window: str, why: str, kind: str) -> bool:
        text_topic = phrase(topic)
        if not text_topic or not city or len(out) >= limit:
            return False
        key = (_norm(topic), _norm(city))
        text = f"{text_topic} in {city} {window}"
        if key in seen or text.lower() == latest_msg:
            return False
        seen.add(key)
        out.append({"text": text, "why": why, "kind": kind})
        return True

    # 1. The event they're going to next: same kind of thing, a little later.
    upcoming = [e for e in going if (_day(e.get("start")) or date.min) >= today]
    pick = upcoming[0] if upcoming else (going[0] if going else None)
    if pick and (pick.get("tags") or []):
        start = _day(pick.get("start"))
        window = "next week" if start and start - today <= timedelta(days=7) else "this weekend"
        add(pick["tags"][0], pick.get("city") or home, window, f"because you're going to {pick.get('title')}", "going")

    # 2. Tags they keep picking: weight > 2 means more than one 'going' (a single pick is already
    #    covered above). Topics they searched for come back in step 3 with their own city.
    searched = {_norm(c) for s in plans for c in [*(s["plan"].get("categories") or []), s["plan"].get("keywords") or ""]}
    used_topics = {k[0] for k in seen}
    liked = sorted(((t, w) for t, w in (profile.get("tags") or {}).items()
                    if w > 2 and _norm(t) not in searched and _norm(t) not in used_topics),
                   key=lambda tw: (-tw[1], tw[0]))
    n_tags = 0
    for tag, _ in liked:
        if n_tags >= 2:
            break
        if add(tag, home, WINDOWS[1 + n_tags], f"you keep picking {phrase(tag)}", "tag"):
            n_tags += 1

    # 3. Past searches, moved forward in time.
    for s in plans:
        p = s["plan"]
        window = shift_window(previous_window(p))  # always later than what they already saw
        when = datetime.fromtimestamp(s["ts"]).strftime("%A") if s.get("ts") else "before"
        add(_topic(p) or "", p["city"], window, f"you searched this on {when}", "search")

    # 4. Two liked tags together, if the list is still thin.
    if len(out) < 3 and len(liked) >= 2:
        a, b = phrase(liked[0][0]), phrase(liked[1][0])
        if home and a and b:
            out.append({"text": f"{a} and {b} in {home} this weekend", "why": "two things you like, together", "kind": "tag"})

    # Spread the windows so the list doesn't say "next week" four times.
    if out and len({_window_of(o["text"]) for o in out}) < 2:
        for i, o in enumerate(out[1:], 1):
            cur = _window_of(o["text"])
            o["text"] = o["text"][: -len(cur)] + shift_window(cur)
            if len({_window_of(x["text"]) for x in out}) >= 2:
                break

    for t in GENERIC:
        if len(out) >= 3:
            break
        if all(_norm(t.split(" in ")[0]) != _norm(o["text"].split(" in ")[0]) for o in out):
            out.append({"text": t, "why": "", "kind": "search"})
    return out[:limit]


def _window_of(text: str) -> str:
    for w in sorted(WINDOWS, key=len, reverse=True):
        if text.endswith(w):
            return w
    return ""


def for_user(user: str, limit: int = 4) -> tuple[list[dict], bool]:
    """(chips, personalized). Reads SQLite only."""
    searches = store.recent_searches(user, 10)
    going = store.going(user)
    profile = recommender.build_profile(user)
    items = suggest(searches, going, profile, date.today(), limit)
    personalized = any(i["kind"] != "search" or i["why"] for i in items)
    return items, personalized
