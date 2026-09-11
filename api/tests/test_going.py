import time

from api import store


def _seed(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DB_PATH", str(tmp_path / "t.db"))
    store.init()
    now = time.time()
    with store.conn() as c:
        c.executemany(
            "INSERT INTO events(id,title,start,tags,first_seen,last_seen) VALUES(?,?,?,?,?,?)",
            [("a", "Late show", "2026-09-20T21:00:00-04:00", "[]", now, now),
             ("b", "Early show", "2026-09-12T19:00:00-04:00", "[]", now, now),
             ("c", "Undated", None, "[]", now, now),
             ("d", "Changed mind", "2026-09-15T19:00:00-04:00", "[]", now, now)],
        )


def test_going_is_soonest_first_and_latest_kind_wins(monkeypatch, tmp_path):
    _seed(monkeypatch, tmp_path)
    store.ensure_user("ryan")
    for eid in ("a", "c", "b", "d"):
        store.record_interaction("ryan", eid, "going")
    time.sleep(0.01)
    store.record_interaction("ryan", "d", "skip")  # going → skip drops it
    got = [e["id"] for e in store.going("ryan")]
    assert got == ["b", "a", "c"]
    assert all(e["kind"] == "going" for e in store.going("ryan"))

    time.sleep(0.01)
    store.record_interaction("ryan", "d", "going")  # skip → going brings it back
    assert [e["id"] for e in store.going("ryan")] == ["b", "d", "a", "c"]
