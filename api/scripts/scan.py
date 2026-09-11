# scan.py — runs INSIDE the Daytona sandbox (via harness.py). Self-contained: stdlib + requests + dateutil only.
#
#   INPUT  = {"city", "state_code", "categories", "keywords", "date_from", "date_to", "date_window", "sources", "now"}
#            sources = hostnames the user asked to search ("on Eventbrite") — searched first and ranked first, never exclusive
#   env    = YDC_API_KEY (You.com), OPENAI_API_KEY, SCAN_MODEL (default gpt-5.6-luna: ~95% of gpt-5.6-sol yield at $0.20/1M in vs $4; gpt-5.4-mini is the accuracy fallback)
#   output = one JSON line {"events": [...], "dropped": {...}, "stats": {...}}
#
# Pipeline: You.com /v1/search fan-out (general + site: per platform) -> pick listing pages + directory seeds
#           -> You.com /v1/contents -> clean markdown -> OpenAI extraction per page (parallel) -> normalize/dedupe.
# The crew agent runs this script through One -> Daytona and repairs it from the traceback when it fails.
import hashlib
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlparse

import requests
from dateutil import parser as dtparse

YOU = "https://ydc-index.io/v1"
OPENAI = "https://api.openai.com/v1/chat/completions"
PLATFORMS = {"eventbrite.com": "Eventbrite", "meetup.com": "Meetup", "lu.ma": "Luma", "dice.fm": "Dice",
             "ra.co": "Resident Advisor", "songkick.com": "Songkick", "timeout.com": "Time Out"}
LISTING_HINTS = ("/d/", "things-to-do", "/events", "/find/", "/browse", "this-weekend", "this-week", "calendar", "whats-on")
NOISE = re.compile(r"^\s*(!\[|\[!\[|_?(Promoted|Save this event|Share this event|Promoted event actions)|Filters?$|Date$|Price$|Category$|Format$|Language$|Currency$|Neighborhood$)")
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

STATS = {"queries": 0, "hits": 0, "pages": 0, "chunks": 0, "candidates": 0, "sources": {}, "timing": {}}
T0 = time.time()


def log(msg):
    print(f"[scan] +{time.time() - T0:.1f}s {msg}", file=sys.stderr, flush=True)


def timed(phase, fn, *args):
    """Run fn, record its wall time in STATS['timing'][phase] and log it."""
    t = time.time()
    out = fn(*args)
    STATS["timing"][phase] = round(time.time() - t, 2)
    log(f"{phase} took {STATS['timing'][phase]}s")
    return out


# ---------------------------------------------------------------- You.com
def you_headers():
    key = os.environ.get("YDC_API_KEY")
    if not key:
        raise RuntimeError("YDC_API_KEY missing in sandbox env")
    return {"X-API-Key": key, "Content-Type": "application/json"}


def host_of(url):
    host = urlparse(url if "://" in url else "//" + url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def in_domains(url, doms):
    """The domain in `doms` that owns `url` (subdomains count), else None."""
    host = host_of(url)
    return next((d for d in doms if host == d or host.endswith("." + d)), None)


def platform_for(url):
    dom = in_domains(url, PLATFORMS)
    return PLATFORMS[dom] if dom else host_of(url) or "web"


def date_phrase(plan):
    try:
        d0 = datetime.fromisoformat(plan["date_from"]) if plan.get("date_from") else None
        d1 = datetime.fromisoformat(plan["date_to"]) if plan.get("date_to") else None
    except (TypeError, ValueError):
        d0 = d1 = None
    if d0 and d1 and d1 != d0:
        return f"{d0:%B} {d0.day}-{d1.day} {d0.year}" if d0.month == d1.month else f"{d0:%B} {d0.day} - {d1:%B} {d1.day} {d0.year}"
    if d0:
        return f"{d0:%B} {d0.day} {d0.year}"
    return plan.get("date_window") or ""


def build_queries(plan):
    parts = [plan.get("keywords") or "", " ".join(plan.get("categories") or []), "events", plan.get("city") or "", date_phrase(plan)]
    base = " ".join(p for p in parts if p).strip()
    src = plan.get("sources") or []  # the user's named sites get their own query, run first
    return [f"{base} site:{s}" for s in src] + [base] + [f"{base} site:{dom}" for dom in PLATFORMS if dom not in src]


def search_one(query, sources=()):
    site = query.split("site:")[-1] if "site:" in query else None
    body = {"query": query, "count": 30 if site in sources else 20, "freshness": "month" if site else "week", "country": "US",
            "extraction": {"extraction_mode": "highlights"}}
    if sources and not site:
        body["boost_domains"] = list(sources)  # relative ranking boost on the general query, not a filter
    t = time.time()
    try:
        r = requests.post(f"{YOU}/search", headers=you_headers(), json=body, timeout=30)
        r.raise_for_status()
        web = (r.json().get("results") or {}).get("web") or []
    except Exception as e:
        log(f"search failed for {query[:50]!r} after {time.time() - t:.1f}s: {e}")
        return []
    STATS["timing"].setdefault("search_calls", []).append(round(time.time() - t, 2))
    hits = []
    for x in web:
        url = x.get("url") or ""
        if not url or any(h in url for h in ("/login", "/signin", "/help", "/support", "/privacy", "/terms")):
            continue
        text = (x.get("contents") or {}).get("highlights") or x.get("snippets") or []
        hits.append({"url": url, "title": x.get("title") or "", "description": x.get("description") or "",
                     "platform": platform_for(url), "text": [t[:400] for t in text[:3]]})
    return hits


def hit_rank(h, sources=()):
    """0 = a site the user asked for, 1 = a known event platform, 2 = anything else."""
    return 0 if in_domains(h["url"], sources) else 1 if h["platform"] in PLATFORMS.values() else 2


def run_searches(plan):
    sources = plan.get("sources") or []
    queries = build_queries(plan)
    STATS["queries"] = len(queries)
    seen = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for q, hits in zip(queries, pool.map(lambda q: search_one(q, sources), queries)):
            site = q.split("site:")[-1] if "site:" in q else None
            log(f"{site or 'web'}: {len(hits)} results" + (" (priority)" if site in sources else ""))
            for h in hits:
                seen.setdefault(h["url"], h)
    ordered = sorted(seen.values(), key=lambda h: hit_rank(h, sources))[:40]  # stable: source queries came first
    STATS["hits"] = len(ordered)
    STATS["sources"] = {s: sum(1 for h in ordered if in_domains(h["url"], [s])) for s in sources}
    return ordered


def seed_listing_urls(plan):
    city = (plan.get("city") or "").split(",")[0].strip()
    st = (plan.get("state_code") or "").lower()
    cat = (plan.get("categories") or [None])[0] or plan.get("keywords") or "events"
    cat_slug = re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")
    if not (city and st):
        return []
    city_slug = re.sub(r"[^a-z0-9]+", "-", city.lower()).strip("-")
    seeds = [f"https://www.eventbrite.com/d/{st}--{city_slug}/{cat_slug}--this-weekend/",
             f"https://www.eventbrite.com/d/{st}--{city_slug}/{cat_slug}/",
             f"https://www.meetup.com/find/?location=us--{st}--{quote(city)}&source=EVENTS&keywords={quote(cat)}"]
    sources = plan.get("sources") or []
    return [u for u in seeds if in_domains(u, sources)] if sources else seeds  # named sites keep the page budget


def select_listing_urls(hits, city, limit=7, sources=()):
    city_slug = re.sub(r"[^a-z]+", "-", (city or "").lower().split(",")[0]).strip("-")

    def other_city(url):
        m = re.search(r"/(?:d|find)/(?:us--)?[a-z]{2}--([a-z-]+)", url.lower())  # meetup /find/?location=us--ny--x, eventbrite /d/ny--x/
        return bool(m and city_slug and city_slug not in m.group(1) and m.group(1) != "new-york")

    listing = [h["url"] for h in hits if not other_city(h["url"]) and (any(k in h["url"].lower() for k in LISTING_HINTS) or
               any(k in h["title"].lower() for k in ("things to do", "this weekend", "this week", "events in", "calendar")))]
    platform = [h["url"] for h in hits if h["platform"] in PLATFORMS.values() and h["url"] not in listing]
    src_listing = [u for u in listing if in_domains(u, sources)]
    src_other = [h["url"] for h in hits if in_domains(h["url"], sources) and h["url"] not in listing and not other_city(h["url"])][:3]
    picked = []
    for u in src_listing + src_other + listing + platform:
        if u not in picked:
            picked.append(u)
        if len(picked) >= limit:
            break
    return picked


def clean_markdown(md, limit=8000):
    out, prev = [], None
    for line in md.splitlines():
        line = line.rstrip()
        if not line.strip() or NOISE.match(line):
            continue
        line = re.sub(r"\(https?://img\.[^)]+\)", "()", line)
        if line != prev:
            out.append(line)
        prev = line
    text = "\n".join(out)
    first_heading = text.find("\n#")
    if 0 < first_heading < 2500:
        text = text[first_heading + 1:]
    return text[:limit]


def fetch_contents(urls):
    if not urls:
        return []
    t = time.time()
    try:
        r = requests.post(f"{YOU}/contents", headers=you_headers(), json={"urls": urls[:10], "formats": ["markdown"], "max_age": 3600}, timeout=60)
        r.raise_for_status()
        pages = r.json()
    except Exception as e:
        log(f"contents failed after {time.time() - t:.1f}s: {e}")
        return []
    log(f"contents call for {len(urls[:10])} urls took {time.time() - t:.1f}s")
    out = []
    for p in pages if isinstance(pages, list) else []:
        md = clean_markdown(p.get("markdown") or "")
        if len(md) > 200:
            out.append({"url": p.get("url"), "platform": platform_for(p.get("url") or ""), "markdown": md})
    STATS["pages"] = len(out)
    log(f"{len(out)} listing pages read ({sum(len(p['markdown']) for p in out) // 1000}k chars)")
    return out


# ---------------------------------------------------------------- extraction (OpenAI)
EXTRACT_SYSTEM = (
    "You extract event listings from web page text into JSON. Reply with ONLY a JSON array (no prose, no code fences). "
    'Each element: {"title","start","end","venue","address","city","url","platform","price","tags","summary"}. '
    "Copy dates exactly as written (e.g. 'Sat, Sep 12, 8:00 PM', 'Tomorrow at 5:30 PM'). Use the event's own link as url when present, "
    "otherwise the page url. tags: 2-5 short lowercase words (genre, type, neighborhood). Use null for fields you cannot see. "
    "Return [] if the text has no specific dated events."
)


def llm_json(system, user):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY missing in sandbox env")
    model = os.environ.get("SCAN_MODEL", "gpt-5.6-luna")
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if "gpt-5" in model:
        body["reasoning_effort"] = "none"
    r = requests.post(OPENAI, headers={"Authorization": f"Bearer {key}"}, json=body, timeout=120)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"].strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def extract_chunk(label, url, platform, text, plan, now_iso):
    topic = ", ".join(plan.get("categories") or []) or plan.get("keywords") or "any"
    user = (f"Today is {now_iso}. The user is in {plan.get('city')} and wants: {topic} (window {plan.get('date_from') or '?'} to {plan.get('date_to') or '?'}).\n"
            f"Extract EVERY event on this page that is on or after today AND related to '{topic}' (include closely related kinds, "
            f"e.g. live music for jazz; exclude unrelated events). Include events after the window too.\n\nPAGE url={url} platform={platform}\n{text}")
    t = time.time()
    try:
        items = llm_json(EXTRACT_SYSTEM, user)
        items = [i for i in items if isinstance(i, dict) and i.get("title")]
    except Exception as e:
        log(f"{label}: extraction failed after {time.time() - t:.1f}s ({str(e)[:80]})")
        return []
    for i in items:
        i.setdefault("platform", platform)
        i.setdefault("url", url)
    STATS["timing"].setdefault("extract_calls", []).append(round(time.time() - t, 2))
    log(f"{label}: {len(items)} candidates ({len(text) // 1000}k chars, {time.time() - t:.1f}s)")
    return items


def extract_candidates(pages, hits, plan, now_iso):
    chunks = [(f"page {p['platform']}", p["url"], p["platform"], p["markdown"]) for p in pages]
    compact = [{"url": h["url"], "title": h["title"], "platform": h["platform"], "text": h["text"] or [h["description"]]} for h in hits]
    chunks.append(("search snippets", "", "web", json.dumps(compact, ensure_ascii=False)))
    STATS["chunks"] = len(chunks)
    out = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for items in pool.map(lambda c: extract_chunk(c[0], c[1], c[2], c[3], plan, now_iso), chunks):
            out.extend(items)
    STATS["candidates"] = len(out)
    return out


# ---------------------------------------------------------------- normalize
def slug(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def parse_dt(value, now):
    if not value:
        return None
    if isinstance(value, dict):
        value = value.get("raw") or value.get("dateTime") or ""
    value = str(value).strip()
    if not value or value.lower() in {"tbd", "tba", "unknown", "null", "none"}:
        return None
    value = re.sub(r"\s+(EDT|EST|PDT|PST|CDT|CST|ET|PT)$", "", value).replace("·", " ")
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)
    m = re.match(r"^(today|tonight|tomorrow|" + "|".join(WEEKDAYS) + r")\s*(?:at\s+)?(.*)$", value, re.I)
    if m:  # relative phrases used by listing sites
        word, rest = m.group(1).lower(), m.group(2).strip()
        if word in ("today", "tonight"):
            day = base
        elif word == "tomorrow":
            day = base + timedelta(days=1)
        else:
            day = base + timedelta(days=(WEEKDAYS.index(word) - base.weekday()) % 7)
        try:
            return dtparse.parse(rest, default=day) if rest else day
        except (ValueError, OverflowError):
            return day
    try:
        dt = dtparse.parse(value, default=base)
    except (ValueError, OverflowError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=now.tzinfo)


def parse_day(value):
    try:
        return dtparse.isoparse(value).date() if value else None
    except (TypeError, ValueError):
        return None


def order_key(e):
    """In-window first, then events from a requested site, then by start time."""
    return (not e["in_window"], not e.get("from_source"), e["start"])


def normalize(candidates, now, city=None, date_from=None, date_to=None, sources=()):
    horizon = now + timedelta(days=60)
    win_from, win_to = parse_day(date_from), parse_day(date_to)
    events, dropped, unparsed = {}, {"no_date": 0, "past": 0, "too_far": 0, "dupe": 0, "no_title": 0}, []
    for c in candidates:
        title = (c.get("title") or "").strip()
        if not title:
            dropped["no_title"] += 1
            continue
        start = parse_dt(c.get("start"), now)
        if start is None:
            dropped["no_date"] += 1
            if len(unparsed) < 5:
                unparsed.append(str(c.get("start"))[:60])
            continue
        if start < now - timedelta(hours=6):
            dropped["past"] += 1
            continue
        if start > horizon:
            dropped["too_far"] += 1
            continue
        in_window = not ((win_from and start.date() < win_from) or (win_to and start.date() > win_to))
        end = parse_dt(c.get("end"), now)
        if end is not None and end < start:
            end = None
        url = (c.get("url") or "").strip()
        fs = bool(url and in_domains(url, sources))  # from a site the user asked for
        key = (slug(title)[:40], start.date().isoformat())  # same title + day across platforms = same event
        if key in events:
            dropped["dupe"] += 1
            if (fs, len(json.dumps(c))) <= (events[key]["from_source"], len(json.dumps(events[key]["_raw"]))):
                continue  # keep the copy from the requested site, else the richer one
        price = c.get("price")
        if isinstance(price, (int, float)):
            price = f"${price:g}"
        events[key] = {
            # url + title + day: several events can share a listing-page URL (extractor fallback) and recurring
            # events share one URL across dates — the id must be unique per distinct event (it is the React key)
            "id": hashlib.sha1(f"{url}|{slug(title)[:40]}|{start.date().isoformat()}".encode()).hexdigest()[:16],
            "title": title, "start": start.isoformat(), "end": end.isoformat() if end else None,
            "venue": (c.get("venue") or "").strip() or None, "address": (c.get("address") or "").strip() or None,
            "city": (c.get("city") or city or "").strip() or None, "url": url or None,
            "platform": (c.get("platform") or "").strip() or None,
            "price": str(price).strip() if price not in (None, "") else None,
            "tags": sorted({slug(t).replace(" ", "-") for t in (c.get("tags") or []) if t})[:8],
            "summary": (c.get("summary") or "").strip()[:280] or None,
            "in_window": in_window, "from_source": fs, "_raw": c,
        }
    out, seen_ids = [], set()
    for e in sorted(events.values(), key=order_key):
        e.pop("_raw", None)
        if e["id"] in seen_ids:  # belt and braces: never emit two events with the same id
            dropped["dupe"] += 1
            continue
        seen_ids.add(e["id"])
        out.append(e)
    return {"events": out, "dropped": dropped, "unparsed_samples": unparsed, "count": len(out)}


# ---------------------------------------------------------------- main
def main(plan):
    now = dtparse.isoparse(plan["now"]) if plan.get("now") else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    plan["sources"] = [h for h in (host_of(str(s)) for s in plan.get("sources") or []) if "." in h][:3]
    hits = timed("search", run_searches, plan)
    seeds = seed_listing_urls(plan)
    limit = 10 - len(seeds) if plan["sources"] else 7
    pages = timed("contents", fetch_contents, seeds + [u for u in select_listing_urls(hits, plan.get("city"), limit, plan["sources"]) if u not in seeds])
    candidates = timed("extract", extract_candidates, pages, hits, plan, now.isoformat())
    if plan.get("chaos"):  # demo lever: a malformed candidate that older versions of normalize() crash on
        candidates.append({"title": 12345, "start": "Tomorrow at 8:00 PM", "url": "https://example.com/chaos"})
    result = timed("normalize", normalize, candidates, now, plan.get("city"), plan.get("date_from"), plan.get("date_to"), plan["sources"])
    STATS["timing"]["total"] = round(time.time() - T0, 2)
    result["stats"] = STATS
    print(json.dumps(result))


if __name__ == "__main__":
    main(INPUT)  # noqa: F821 — injected by harness.py
