import time
from datetime import date

from api import store, suggest
from api.suggest import GENERIC, suggest as build

TODAY = date(2026, 9, 11)  # a Friday
EMPTY_PROFILE = {"tags": {}, "platforms": {}, "venues": {}, "city": None}


def _search(city, cats, window=None, date_from=None, date_to=None, ts=1_757_500_000.0, message=None):
    return {"message": message or f"{cats[0]} in {city}", "ts": ts,
            "plan": {"city": city, "categories": cats, "keywords": None, "date_window": window,
                     "date_from": date_from, "date_to": date_to}}


def texts(items):
    return [i["text"] for i in items]


def test_new_user_gets_generic():
    items = build([], [], EMPTY_PROFILE, TODAY)
    assert texts(items) == GENERIC
    assert all(i["why"] == "" for i in items)


def test_repeat_search_shifts_window():
    s = _search("Brooklyn, NY", ["jazz"], "this weekend", "2026-09-11", "2026-09-13")
    items = build([s], [], {**EMPTY_PROFILE, "city": "Brooklyn, NY"}, TODAY)
    assert "jazz shows in Brooklyn, NY next week" in texts(items)
    assert not any(t.endswith("Brooklyn, NY this weekend") and t.startswith("jazz") for t in texts(items))


def test_past_window_derived_from_dates_and_shifted():
    s = _search("Queens, NY", ["comedy"], None, "2026-09-01", "2026-09-01")  # one day → 'tonight' → shifted
    items = build([s], [], {**EMPTY_PROFILE, "city": "Queens, NY"}, TODAY)
    assert "comedy shows in Queens, NY this weekend" in texts(items)


def test_going_event_comes_first():
    going = [{"title": "Blue Note Late Set", "tags": ["jazz", "live-music"], "city": "New York, NY",
              "start": "2026-09-13T22:00:00-04:00"}]
    items = build([], going, {**EMPTY_PROFILE, "tags": {"jazz": 2, "live-music": 2}}, TODAY)
    assert items[0]["kind"] == "going"
    assert items[0]["text"].startswith("jazz shows in New York, NY")
    assert "Blue Note Late Set" in items[0]["why"]


def test_liked_tag_combines_with_home_city():
    profile = {**EMPTY_PROFILE, "tags": {"techno": 4}, "city": "Manhattan, NY"}
    items = build([_search("Manhattan, NY", ["jazz"], "this weekend")], [], profile, TODAY)
    assert any(t.startswith("techno shows in Manhattan, NY") for t in texts(items))
    assert all(i["kind"] != "going" for i in items)


def test_dedupe_cap_and_window_spread():
    searches = [_search("Brooklyn, NY", ["jazz"], "next week", ts=1_757_500_000.0 - i) for i in range(6)]
    items = build(searches, [], {**EMPTY_PROFILE, "city": "Brooklyn, NY"}, TODAY, limit=4)
    jazz = [t for t in texts(items) if t.startswith("jazz shows in Brooklyn")]
    assert len(jazz) == 1
    assert 3 <= len(items) <= 4
    assert len({suggest._window_of(t) for t in texts(items)}) >= 2


def test_skips_clarify_turns():
    s = {"message": "running events", "ts": 1.0, "plan": {"city": None, "categories": ["running"]}}
    items = build([s], [], EMPTY_PROFILE, TODAY)
    assert texts(items) == GENERIC


def test_phrasing():
    assert suggest.phrase("live-music") == "live music"
    assert suggest.phrase("ai") == "AI meetups"
    assert suggest.phrase("pokemon events") == "pokemon events"


def test_for_user_reads_store(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DB_PATH", str(tmp_path / "t.db"))
    store.init()
    store.ensure_user("ryan")
    now = time.time()
    with store.conn() as c:
        c.execute("INSERT INTO events(id,title,start,city,tags,first_seen,last_seen) VALUES(?,?,?,?,?,?,?)",
                  ("a", "Jazz Vespers", "2026-09-14T17:00:00-04:00", "Brooklyn, NY", '["jazz","live-music"]', now, now))
    store.record_search("ryan", "jazz in Brooklyn this weekend",
                        {"city": "Brooklyn, NY", "categories": ["jazz"], "date_window": "this weekend"}, ["a"])
    store.record_interaction("ryan", "a", "going")
    items, personalized = suggest.for_user("ryan")
    assert personalized
    assert items[0]["kind"] == "going"
    assert "Jazz Vespers" in items[0]["why"]
    assert suggest.for_user("nobody")[1] is False
