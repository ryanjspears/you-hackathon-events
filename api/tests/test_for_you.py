import time

from api import recommender, store


def test_city_keywords_cover_spellings():
    keys = store.city_keywords(["Brooklyn, NY", "Tokyo"])
    assert "brooklyn" in keys and "new york" in keys and "nyc" in keys and "tokyo" in keys
    assert store.city_keywords(None) == []


def _seed(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DB_PATH", str(tmp_path / "t.db"))
    store.init()
    now = time.time()
    with store.conn() as c:
        c.executemany("INSERT INTO events(id,title,start,city,tags,first_seen,last_seen) VALUES(?,?,?,?,?,?,?)", [
            ("a", "Jazz at Smalls", "2026-09-20T21:00:00-04:00", "New York", '["jazz"]', now, now),
            ("b", "Brooklyn Jazz Night", "2026-09-21T20:00:00-04:00", "Brooklyn", '["jazz"]', now, now),
            ("c", "SF Jazz", "2026-09-22T20:00:00-07:00", "San Francisco, CA", '["jazz"]', now, now),
            ("d", "Old show", "2026-01-01T20:00:00-04:00", "Queens, NY", '["jazz"]', now, now),
        ])


def test_future_events_matches_any_spelling_of_the_users_cities(monkeypatch, tmp_path):
    _seed(monkeypatch, tmp_path)
    got = {e["id"] for e in store.future_events(["Queens, NY"], "2026-09-11T00:00:00-04:00")}
    assert got == {"a", "b"}  # NYC spellings, not SF, not the past
    assert {e["id"] for e in store.future_events(None, "2026-09-11T00:00:00-04:00")} == {"a", "b", "c"}


def test_profile_collects_cities_and_staleness(monkeypatch, tmp_path):
    _seed(monkeypatch, tmp_path)
    store.ensure_user("ryan")
    store.record_search("ryan", "jazz in queens", {"city": "Queens, NY", "categories": ["jazz"]}, [])
    store.record_interaction("ryan", "c", "going")
    profile = recommender.build_profile("ryan")
    assert profile["cities"] == ["Queens, NY", "San Francisco, CA"]
    assert recommender.is_stale("ryan")  # acted, never ranked
    time.sleep(0.01)
    store.save_recommendations("ryan", [{"id": "a", "score": 2, "reason": "Because you like jazz"}])
    assert not recommender.is_stale("ryan")
    time.sleep(0.01)
    store.record_interaction("ryan", "a", "skip")
    assert recommender.is_stale("ryan")
    assert not recommender.is_refreshing("ryan")
