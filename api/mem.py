"""Learning loop over One's memory (`one mem`). Type = namespace per user: pref_<user>."""
from __future__ import annotations

import json
import shutil
import subprocess

from api import trace
from api.progress import emit

ONE = shutil.which("one") or "one"


def _mem(*args: str, timeout: int = 60) -> dict | list | None:
    with trace.span(f"one.mem.{args[0]}", arg=(args[1] if len(args) > 1 else "")[:40]) as s:
        try:
            p = subprocess.run([ONE, "--agent", "mem", *args], capture_output=True, text=True, timeout=timeout)
            s["rc"] = p.returncode; s["out_chars"] = len(p.stdout)
            if p.returncode != 0:
                emit("mem", text=f"one mem {args[0]} failed: {p.stderr.strip()[:200] or p.stdout.strip()[:200]}")
                return None
            return json.loads(p.stdout) if p.stdout.strip().startswith(("{", "[")) else None
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
            emit("mem", text=f"one mem unavailable: {e}")
            return None


def warm() -> None:
    """First `one mem` call bootstraps embedded Postgres (~25s); do it at startup."""
    _mem("status", timeout=90)


def learn(user: str, content: str, tags: list[str] | None = None, weight: int = 6) -> None:
    res = _mem("add", f"pref_{user}", json.dumps({"content": content, "user": user}),
               "--tags", ",".join(["events", f"user:{user}", *(tags or [])]), "--weight", str(weight))
    emit("learned", text=f"Learned: {content}", ok=res is not None)


def learn_profile(user: str, content: str) -> None:
    """Keep ONE profile note per user: merge key profile:<user> → update in place, else create."""
    key = f"profile:{user}"
    found = _mem("find-by-key", key)
    existing = None
    for group in ((found or {}).get("byType") or {}).values():
        for item in group.get("items") or []:
            if item.get("status", "active") == "active":
                existing = item.get("id")
    if existing:
        res = _mem("update", existing, json.dumps({"content": content}))
    else:
        res = _mem("add", f"pref_{user}", json.dumps({"content": content, "user": user}),
                   "--keys", key, "--tags", ",".join(["events", f"user:{user}", "profile"]), "--weight", "6")
    emit("learned", text=f"Learned: {content}", ok=res is not None)


def learn_sources(user: str, names: str) -> None:
    """One 'Prefers events from …' note per user (merge key sources:<user>), rewritten to the latest request.

    Unchanged content is not rewritten and prints no Learned: line, so a plan whose sources came
    from this very note does not loop back into memory.
    """
    key, content = f"sources:{user}", f"Prefers events from {names}"
    found = _mem("find-by-key", key)
    existing, same = None, False
    for group in ((found or {}).get("byType") or {}).values():
        for item in group.get("items") or []:
            if item.get("status", "active") == "active":
                existing, same = item.get("id"), (item.get("data") or {}).get("content") == content
    if same:
        return
    if existing:
        res = _mem("update", existing, json.dumps({"content": content}))
    else:
        res = _mem("add", f"pref_{user}", json.dumps({"content": content, "user": user}),
                   "--keys", key, "--tags", ",".join(["events", f"user:{user}", "source"]), "--weight", "5")
    emit("learned", text=f"Learned: {content}", ok=res is not None)


def recall(user: str, query: str, limit: int = 3) -> list[str]:
    res = _mem("search", query or "events", "--type", f"pref_{user}", "--limit", str(limit))
    notes: list[str] = []
    rows = res.get("items") if isinstance(res, dict) else res
    for r in rows or []:
        data = r.get("data") if isinstance(r, dict) else None
        if isinstance(data, dict) and data.get("content"):
            notes.append(data["content"])
    if not notes:
        listed = _mem("list", f"pref_{user}", "--limit", str(limit))
        rows = listed.get("items") if isinstance(listed, dict) else listed
        for r in rows or []:
            data = r.get("data") if isinstance(r, dict) else None
            if isinstance(data, dict) and data.get("content"):
                notes.append(data["content"])
    # standing preferences are keyed, not searched: the source note must reach the Planner even when the
    # semantic search ranks it out ("jazz in brooklyn" ≠ "Prefers events from Eventbrite")
    found = _mem("find-by-key", f"sources:{user}")
    for group in ((found or {}).get("byType") or {}).values():
        for item in group.get("items") or []:
            content = (item.get("data") or {}).get("content")
            if item.get("status", "active") == "active" and content and content not in notes:
                notes.append(content)
    emit("recalled", text=("Recalled: " + " | ".join(notes)) if notes else f"Recalled: nothing yet for {user}", notes=notes)
    return notes
