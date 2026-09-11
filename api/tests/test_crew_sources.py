"""Planner-side source handling that needs no LLM: hostname normalisation, keyword scrubbing, history carry-over."""
from api import crew


def test_norm_source():
    assert crew._norm_source("www.Eventbrite.com") == "eventbrite.com"
    assert crew._norm_source("https://www.eventbrite.com/d/ny--brooklyn/jazz/") == "eventbrite.com"
    assert crew._norm_source("lu.ma") == "lu.ma"
    assert crew._norm_source(" ra.co/events?x=1 ") == "ra.co"


def test_tidy_sources_dedupes_caps_and_scrubs_keywords():
    plan = crew.SearchPlan(city="Brooklyn, NY", keywords="on Eventbrite jazz brunch", sources=["www.eventbrite.com", "eventbrite.com", "luma", "lu.ma", "dice.fm", "ra.co"])
    plan = crew._tidy_sources(plan, "jazz brunch on eventbrite, luma, dice or RA in brooklyn")
    assert plan.sources == ["eventbrite.com", "lu.ma", "dice.fm"]
    assert plan.keywords == "jazz brunch"
    plan = crew._tidy_sources(crew.SearchPlan(keywords="from Luma", sources=["lu.ma"]), "anything from luma")
    assert plan.keywords is None


def test_tidy_sources_drops_sites_nobody_named():
    plan = crew.SearchPlan(city="Brooklyn, NY", sources=["dice.fm"])
    assert crew._tidy_sources(plan, "jazz shows in Brooklyn", ["Profile: likes jazz; finds events on Dice"]).sources == []
    assert crew._tidy_sources(crew.SearchPlan(sources=["dice.fm"]), "jazz in Brooklyn", ["Prefers events from Dice"]).sources == ["dice.fm"]
    assert crew._tidy_sources(crew.SearchPlan(sources=["ra.co", "lu.ma"]), "jazz on RA or luma in Brooklyn").sources == ["ra.co", "lu.ma"]
    assert crew._tidy_sources(crew.SearchPlan(sources=["nycgo.com"]), "running from nycgo.com").sources == ["nycgo.com"]
    assert crew._tidy_sources(crew.SearchPlan(sources=["nycgo.com"]), "running in nyc").sources == []
    hist = [{"role": "agent", "plan": {"sources": ["meetup.com"]}}]
    assert crew._tidy_sources(crew.SearchPlan(sources=["meetup.com"]), "how about techno", None, hist).sources == ["meetup.com"]


def test_source_names_and_conversation_carry_sources():
    assert crew.source_names(["ra.co", "nycgo.com"]) == "Resident Advisor, nycgo.com"
    convo = crew._conversation([{"role": "user", "text": "jazz on eventbrite in brooklyn"},
                                {"role": "agent", "plan": {"city": "Brooklyn, NY", "sources": ["eventbrite.com"]}}])
    assert "sources=['eventbrite.com']" in convo
