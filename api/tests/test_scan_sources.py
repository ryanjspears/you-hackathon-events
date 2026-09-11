"""Priority-origin searching: the pure functions in scan.py that honour plan['sources']."""
import importlib.util, pathlib
from datetime import datetime

SCRIPTS = pathlib.Path(__file__).parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("scan_sources", SCRIPTS / "scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)
NOW = datetime.fromisoformat("2026-09-11T12:00:00-04:00")
PLAN = {"city": "Brooklyn, NY", "state_code": "NY", "categories": ["jazz"], "date_from": "2026-09-11", "date_to": "2026-09-13"}


def hit(url, platform=None, title=""):
    return {"url": url, "title": title, "platform": platform or scan.platform_for(url), "text": [], "description": ""}


def test_build_queries_orders_sources_first():
    base_only = scan.build_queries(PLAN)
    assert len(base_only) == 8 and "site:" not in base_only[0]
    q = scan.build_queries({**PLAN, "sources": ["eventbrite.com"]})
    assert len(q) == 8 and q[0].endswith("site:eventbrite.com") and "site:" not in q[1]
    assert sum(1 for x in q if x.endswith("site:eventbrite.com")) == 1
    q = scan.build_queries({**PLAN, "sources": ["nycgo.com"]})
    assert len(q) == 9 and q[0].endswith("site:nycgo.com")


def test_host_helpers_and_hit_rank():
    assert scan.host_of("https://www.Eventbrite.com/e/x") == "eventbrite.com"
    assert scan.host_of("nyc.eventbrite.com/d/") == "nyc.eventbrite.com"
    assert scan.in_domains("https://nyc.eventbrite.com/e/1", ["eventbrite.com"]) == "eventbrite.com"
    assert scan.in_domains("https://noteventbrite.com/e/1", ["eventbrite.com"]) is None
    src = ["eventbrite.com"]
    assert scan.hit_rank(hit("https://www.eventbrite.com/e/x"), src) == 0
    assert scan.hit_rank(hit("https://nyc.eventbrite.com/e/x"), src) == 0
    assert scan.hit_rank(hit("https://www.meetup.com/x"), src) == 1
    assert scan.hit_rank(hit("https://blog.example.org/x"), src) == 2
    assert scan.hit_rank(hit("https://www.meetup.com/x")) == 1 and scan.hit_rank(hit("https://blog.example.org/x")) == 2


def test_seed_listing_urls_follow_sources():
    assert len(scan.seed_listing_urls(PLAN)) == 3
    eb = scan.seed_listing_urls({**PLAN, "sources": ["eventbrite.com"]})
    assert len(eb) == 2 and all("eventbrite.com" in u for u in eb)
    assert scan.seed_listing_urls({**PLAN, "sources": ["nycgo.com"]}) == []


def test_select_listing_urls_puts_source_pages_first():
    hits = [
        hit("https://www.meetup.com/find/?location=us--ny--brooklyn", title="Jazz events in Brooklyn"),
        hit("https://dice.fm/event/one"),
        hit("https://www.eventbrite.com/e/single-1"), hit("https://www.eventbrite.com/e/single-2"),
        hit("https://www.eventbrite.com/e/single-3"), hit("https://www.eventbrite.com/e/single-4"),
        hit("https://www.eventbrite.com/d/ny--brooklyn/jazz/", title="Jazz Events in Brooklyn"),
        hit("https://www.eventbrite.com/d/ca--los-angeles/jazz/", title="Jazz Events in Los Angeles"),
    ]
    picked = scan.select_listing_urls(hits, "Brooklyn, NY", 7, ["eventbrite.com"])
    assert picked[0] == "https://www.eventbrite.com/d/ny--brooklyn/jazz/"          # source listing page first
    assert picked[1:4] == [f"https://www.eventbrite.com/e/single-{i}" for i in (1, 2, 3)]  # then up to 3 source pages
    assert "https://www.eventbrite.com/d/ca--los-angeles/jazz/" not in picked      # other-city filter still applies
    assert picked[4] == "https://www.meetup.com/find/?location=us--ny--brooklyn"   # then the usual listing pages
    default = scan.select_listing_urls(hits, "Brooklyn, NY")
    assert default[0] == "https://www.meetup.com/find/?location=us--ny--brooklyn"


def test_normalize_flags_and_prefers_source_copies():
    short_eb = {"title": "Jazz Night", "start": "2026-09-12T21:00", "url": "https://www.eventbrite.com/e/1", "platform": "Eventbrite"}
    long_dice = {"title": "Jazz Night!", "start": "2026-09-12T21:00", "url": "https://dice.fm/event/1", "platform": "Dice",
                 "venue": "Smalls", "summary": "a much longer description that makes this the richer candidate"}
    other = {"title": "Other Show", "start": "2026-09-12T20:00", "url": "https://dice.fm/event/2", "platform": "Dice"}
    body = scan.normalize([long_dice, short_eb, other], NOW, sources=["eventbrite.com"])
    assert [e["url"] for e in body["events"]] == ["https://www.eventbrite.com/e/1", "https://dice.fm/event/2"]  # source first, source copy wins
    assert body["events"][0]["from_source"] is True and body["events"][1]["from_source"] is False
    body = scan.normalize([long_dice, short_eb, other], NOW)
    assert body["events"][0]["url"] == "https://dice.fm/event/2" and body["events"][1]["url"] == "https://dice.fm/event/1"  # richer copy, by time
    assert not any(e["from_source"] for e in body["events"])


def test_chaos_candidate_still_crashes_with_sources():
    try:
        scan.normalize([{"title": 12345, "start": "Tomorrow at 8:00 PM"}], NOW, sources=["eventbrite.com"])
    except AttributeError:
        return
    raise AssertionError("the repair-loop demo relies on normalize() crashing on a numeric title")
