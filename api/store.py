"""SQLite store: users, events, searches, interactions, recommendations."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from contextlib import contextmanager

DB_PATH = os.environ.get("EVENTS_DB", os.path.join(os.path.dirname(__file__), "..", "events.db"))
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, created REAL);
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY, title TEXT, start TEXT, end TEXT, venue TEXT, address TEXT, city TEXT,
  url TEXT, platform TEXT, price TEXT, tags TEXT, summary TEXT, first_seen REAL, last_seen REAL);
CREATE TABLE IF NOT EXISTS searches (id INTEGER PRIMARY KEY, user TEXT, message TEXT, plan TEXT, event_ids TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS interactions (id INTEGER PRIMARY KEY, user TEXT, event_id TEXT, kind TEXT, ts REAL,
  UNIQUE(user, event_id, kind));
CREATE TABLE IF NOT EXISTS recommendations (user TEXT, event_id TEXT, score REAL, reason TEXT, ts REAL,
  PRIMARY KEY(user, event_id));
"""


@contextmanager
def conn():
    with _lock:
        c = sqlite3.connect(DB_PATH)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        finally:
            c.close()


def init():
    with conn() as c:
        c.executescript(SCHEMA)


def _row(r) -> dict:
    d = dict(r)
    if "tags" in d and isinstance(d["tags"], str):
        d["tags"] = json.loads(d["tags"] or "[]")
    return d


def ensure_user(name: str):
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO users(name, created) VALUES(?, ?)", (name, time.time()))


def upsert_events(events: list[dict]):
    now = time.time()
    with conn() as c:
        for e in events:
            c.execute(
                """INSERT INTO events(id,title,start,end,venue,address,city,url,platform,price,tags,summary,first_seen,last_seen)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET title=excluded.title,start=excluded.start,end=excluded.end,venue=excluded.venue,
                   address=excluded.address,city=excluded.city,url=excluded.url,platform=excluded.platform,price=excluded.price,
                   tags=excluded.tags,summary=excluded.summary,last_seen=excluded.last_seen""",
                (e["id"], e.get("title"), e.get("start"), e.get("end"), e.get("venue"), e.get("address"), e.get("city"),
                 e.get("url"), e.get("platform"), e.get("price"), json.dumps(e.get("tags") or []), e.get("summary"), now, now))


def get_event(event_id: str) -> dict | None:
    with conn() as c:
        r = c.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        return _row(r) if r else None


def record_search(user: str, message: str, plan: dict, event_ids: list[str]):
    with conn() as c:
        c.execute("INSERT INTO searches(user,message,plan,event_ids,ts) VALUES(?,?,?,?,?)",
                  (user, message, json.dumps(plan), json.dumps(event_ids), time.time()))


def recent_searches(user: str, limit: int = 10) -> list[dict]:
    with conn() as c:
        rows = c.execute("SELECT * FROM searches WHERE user=? ORDER BY ts DESC LIMIT ?", (user, limit)).fetchall()
        return [{**dict(r), "plan": json.loads(r["plan"] or "{}"), "event_ids": json.loads(r["event_ids"] or "[]")} for r in rows]


def record_interaction(user: str, event_id: str, kind: str):
    with conn() as c:
        c.execute("INSERT OR REPLACE INTO interactions(user,event_id,kind,ts) VALUES(?,?,?,?)", (user, event_id, kind, time.time()))


def interactions(user: str, kind: str | None = None) -> list[dict]:
    with conn() as c:
        q = "SELECT i.kind, i.ts, e.* FROM interactions i JOIN events e ON e.id=i.event_id WHERE i.user=?"
        args: list = [user]
        if kind:
            q += " AND i.kind=?"
            args.append(kind)
        return [_row(r) for r in c.execute(q + " ORDER BY i.ts DESC", args).fetchall()]


def going(user: str) -> list[dict]:
    """Events the user is going to, soonest first. An event marked going and later skipped drops out
    (the latest interaction wins); undated events sort last."""
    with conn() as c:
        rows = c.execute(
            """SELECT i.kind, i.ts, e.* FROM interactions i JOIN events e ON e.id=i.event_id
               WHERE i.user=? AND i.kind='going'
                 AND i.ts >= COALESCE((SELECT MAX(s.ts) FROM interactions s
                                       WHERE s.user=i.user AND s.event_id=i.event_id AND s.kind='skip'), 0)
               ORDER BY (e.start IS NULL OR e.start=''), e.start, i.ts DESC""", (user,)).fetchall()
        return [_row(r) for r in rows]


_NYC = ["new york", "nyc", "manhattan", "brooklyn", "queens", "bronx"]
CITY_ALIASES = {  # the scanner keeps whatever the listing said, so one city has many spellings
    **{k: _NYC for k in ("new york city", "new york", "manhattan", "brooklyn", "queens", "bronx")},
    "san francisco": ["sf", "bay area"],
    "los angeles": ["la"],
}


def city_keywords(cities: list[str] | str | None) -> list[str]:
    """'Brooklyn, NY' → ['brooklyn', 'new york', 'nyc']: substrings that match every spelling of the city."""
    out: list[str] = []
    for c in ([cities] if isinstance(cities, str) else cities or []):
        base = (c or "").lower().split(",")[0].strip()
        if not base:
            continue
        for k in [base, *CITY_ALIASES.get(base, [])]:
            if k not in out:
                out.append(k)
    return out


def future_events(cities: list[str] | str | None, now_iso: str, limit: int = 150) -> list[dict]:
    """Upcoming events in any of `cities` (all cities when empty), soonest first."""
    keys = city_keywords(cities)
    with conn() as c:
        if keys:
            where = " OR ".join("lower(city) LIKE ?" for _ in keys)
            rows = c.execute(f"SELECT * FROM events WHERE start >= ? AND ({where}) ORDER BY start LIMIT ?",
                             (now_iso, *[f"%{k}%" for k in keys], limit)).fetchall()
        else:
            rows = c.execute("SELECT * FROM events WHERE start >= ? ORDER BY start LIMIT ?", (now_iso, limit)).fetchall()
        return [_row(r) for r in rows]


def recommendations_ts(user: str) -> float | None:
    """When the user's ranking was last written (None = never)."""
    with conn() as c:
        r = c.execute("SELECT MAX(ts) AS ts FROM recommendations WHERE user=?", (user,)).fetchone()
        return r["ts"] if r and r["ts"] is not None else None


def last_activity_ts(user: str) -> float | None:
    """Latest search or interaction: anything after the ranking was written makes it stale."""
    with conn() as c:
        r = c.execute("""SELECT MAX(ts) AS ts FROM (SELECT ts FROM searches WHERE user=?
                                                  UNION ALL SELECT ts FROM interactions WHERE user=?)""", (user, user)).fetchone()
        return r["ts"] if r and r["ts"] is not None else None


def save_recommendations(user: str, recs: list[dict]):
    with conn() as c:
        c.execute("DELETE FROM recommendations WHERE user=?", (user,))
        c.executemany("INSERT INTO recommendations(user,event_id,score,reason,ts) VALUES(?,?,?,?,?)",
                      [(user, r["id"], r.get("score", 0), r.get("reason", ""), time.time()) for r in recs])


def get_recommendations(user: str, limit: int = 12) -> list[dict]:
    with conn() as c:
        rows = c.execute("""SELECT e.*, r.score, r.reason FROM recommendations r JOIN events e ON e.id=r.event_id
                            WHERE r.user=? ORDER BY r.score DESC LIMIT ?""", (user, limit)).fetchall()
        return [_row(r) for r in rows]
