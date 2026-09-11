"""The CrewAI crew: Planner → Scanner → Curator.

- Planner turns the chat message into a SearchPlan (asks for a city if missing).
- Scanner runs scripts/scan.py in a Daytona sandbox through One. The script itself calls
  You.com (search + contents) and OpenAI (extraction) and prints clean events. If it
  fails, the Scanner reads the traceback, patches the script and reruns (≤3 attempts).
- Curator ranks the clean events for the request and writes the reply shown in the chat.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
from datetime import datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool
from pydantic import BaseModel, Field

from api import sandbox, trace
from api.progress import emit

SCAN_SRC = (pathlib.Path(__file__).parent / "scripts" / "scan.py").read_text()
TZ = ZoneInfo(os.environ.get("EVENTS_TZ", "America/New_York"))
MODEL = os.environ.get("CREW_MODEL", "openai/gpt-5.6-luna")  # $0.20/1M in; gpt-4o ($2.50) and gpt-5.6-sol ($4) tested equal for these agents
MAX_SANDBOX_CALLS = 3
# Display names for the sites the scanner knows. Mirrors scan.py PLATFORMS and web SITES — keep the three identical.
SOURCE_NAMES = {"eventbrite.com": "Eventbrite", "meetup.com": "Meetup", "lu.ma": "Luma", "dice.fm": "Dice",
                "ra.co": "Resident Advisor", "songkick.com": "Songkick", "timeout.com": "Time Out"}
trace.install_crewai_listener()  # every LLM call / tool call / task becomes a trace span


class SearchPlan(BaseModel):
    city: str | None = Field(None, description="Canonical city name + region, e.g. 'Brooklyn, NY', 'San Francisco, CA' — expand nicknames "
                                               "and abbreviations ('san fran', 'SF', 'NYC'). null if the user did not say.")
    date_window: str | None = Field(None, description="Natural-language window, e.g. 'this weekend', 'Sep 12-14'")
    date_from: str | None = Field(None, description="First day of the window as YYYY-MM-DD (resolve relative phrases using today's date)")
    date_to: str | None = Field(None, description="Last day of the window as YYYY-MM-DD; null if open-ended")
    categories: list[str] = Field(default_factory=list, description="Event categories, e.g. ['jazz', 'live music']")
    keywords: str | None = Field(None, description="Other search terms from the request")
    state_code: str | None = Field(None, description="Two-letter US state code for the city (e.g. 'NY'); null outside the US")
    clarifying_question: str | None = Field(None, description="If city is missing, the question to ask the user. Otherwise null.")
    sources: list[str] = Field(default_factory=list, description="Sites the user explicitly asked to look at, as bare hostnames (no www., "
                                                                  "no path): eventbrite.com, meetup.com, lu.ma, dice.fm, ra.co, songkick.com, "
                                                                  "timeout.com, or any other site they name (instagram.com, nycgo.com). [] if none. Max 3.")


def source_names(sources: list[str]) -> str:
    """'eventbrite.com, nycgo.com' → 'Eventbrite, nycgo.com'."""
    return ", ".join(SOURCE_NAMES.get(s, s) for s in sources)


def _norm_source(s: str) -> str:
    """'https://www.Eventbrite.com/d/ny--brooklyn/' → 'eventbrite.com'. Name→domain mapping ('luma') is the Planner's job."""
    s = str(s).strip()
    host = urlparse(s if "://" in s else "//" + s).netloc.lower().strip(".")
    return host[4:] if host.startswith("www.") else host


def _llm() -> LLM:
    # GPT-5-series models reject a non-default temperature, and on chat completions they only
    # allow function tools with reasoning_effort="none" (or none at all; CREW_REASONING to override).
    if "gpt-5" in MODEL or MODEL.startswith("openai/o"):
        # CrewAI only forwards `reasoning_effort` for o1 models, so pass it as a raw request param.
        return LLM(model=MODEL, additional_params={"reasoning_effort": os.environ.get("CREW_REASONING", "none")})
    return LLM(model=MODEL, temperature=0.2)


def _now_iso() -> str:
    return datetime.now(TZ).isoformat()


# ---- tools ---------------------------------------------------------------

def make_tools(state: dict):
    """Tools close over per-request `state` so sandbox attempts are capped and the result captured."""

    @tool("run_scan_script")
    def run_scan_script(script: str = "") -> str:
        """Run the event scanner script in the Daytona sandbox (via One). Call with NO arguments to run the current
        scanner script; pass `script` (the full corrected Python source) only after you fixed a bug in it. The script
        receives the search plan as `INPUT` and must print one JSON object {"events": [...], "dropped": {...}, "count": n}.
        Returns JSON {exit_code, stdout, stderr}; exit_code 0 means success. stderr carries the progress log and any traceback."""
        if script and script.strip():
            state["script"] = script  # a repaired version becomes the current script for further attempts
        script = state.get("script") or SCAN_SRC
        state["attempts"] = state.get("attempts", 0) + 1
        if state["attempts"] > MAX_SANDBOX_CALLS:
            return json.dumps({"exit_code": 2, "stdout": "", "stderr": "attempt limit reached; stop and reply DONE"})
        emit("sandbox", text=f"attempt {state['attempts']}: running scan.py in Daytona via One")
        payload = {**state["plan"], "now": _now_iso(), "chaos": bool(state.get("chaos"))}
        try:
            res = sandbox.sandbox_run(script, payload, timeout=300)
        except Exception as e:  # One/Daytona transport problem — not a script bug; tell the agent to simply retry
            emit("sandbox", text=f"sandbox call failed ({str(e)[:80]}) — retrying")
            return json.dumps({"exit_code": 503, "stdout": "",
                               "stderr": f"TRANSPORT ERROR (not a script bug): {str(e)[:300]}. Call run_scan_script again with the SAME script."})
        if res["exit_code"] == 0:
            try:
                state["result"] = json.loads(res["stdout"].strip().splitlines()[-1])
                emit("sandbox", text=f"exit 0 — {state['result'].get('count', 0)} clean events")
                timing = (state["result"].get("stats") or {}).get("timing") or {}  # phase timings measured inside scan.py
                trace.event("scan.timing", **{k: (f"n={len(v)} max={max(v)}s" if isinstance(v, list) and v else v) for k, v in timing.items()})
            except (json.JSONDecodeError, IndexError):
                res = {**res, "exit_code": 4, "stderr": res["stderr"] + "\nstdout was not the expected JSON: " + res["stdout"][:300]}
        if res["exit_code"] != 0:
            tb = "\n".join(l for l in res["stderr"].splitlines() if not l.startswith("[scan] "))
            emit("sandbox", text=f"exit {res['exit_code']} — repairing", stderr=tb[-600:])
        return json.dumps({"exit_code": res["exit_code"], "stdout": res["stdout"][:800], "stderr": res["stderr"][-3500:]})

    return run_scan_script


# ---- crew ----------------------------------------------------------------

def _conversation(history: list[dict] | None) -> str:
    """Earlier turns of this chat, oldest first, as the Planner sees them (last 8 turns, trimmed)."""
    lines = []
    for h in (history or [])[-8:]:
        if not isinstance(h, dict):
            continue
        if h.get("role") == "user" and h.get("text"):
            lines.append(f"user: {str(h['text'])[:200]}")
        elif h.get("role") == "agent" and isinstance(h.get("plan"), dict):
            p = h["plan"]
            if h.get("clarify"):
                lines.append(f"assistant asked: {str(h['clarify'])[:120]}")
            else:
                lines.append(f"assistant searched: city={p.get('city')}, state_code={p.get('state_code')}, "
                             f"dates={p.get('date_window')} ({p.get('date_from')} to {p.get('date_to')}), "
                             f"categories={p.get('categories')}, keywords={p.get('keywords')}, sources={p.get('sources') or []}")
    if not lines:
        return ""
    return "Conversation so far, oldest first:\n" + "\n".join(lines) + "\n\n"


def plan_only(message: str, recalled: list[str], history: list[dict] | None = None) -> SearchPlan:
    """Planner as a single-task crew so a missing city can short-circuit before searching.

    `history` is the chat so far (user messages + the plans already searched); the new message is
    read as a follow-up, so "how about jazz" after "running events in nyc" keeps the city and dates.
    """
    planner = Agent(role="Event Planner", llm=_llm(), verbose=False,
                    goal="Turn a user's request into a precise event search plan.",
                    backstory="You parse what people want to do and where. You never invent a city.")
    memo = ("Known preferences for this user: " + "; ".join(recalled)) if recalled else "No stored preferences."
    convo = _conversation(history)
    follow_up = ("The new message is the latest turn of that conversation. Treat it as a follow-up: whatever it does not say "
                 "(city, state_code, dates) carries over from the most recent 'assistant searched' line; a new topic "
                 "('how about jazz') replaces categories and keywords, a new place replaces the city, new dates replace the dates. "
                 "If the assistant asked which city and the new message answers it, combine the answer with the earlier request. "
                 "A source named in the follow-up ('what about on meetup?') REPLACES sources; 'also'/'too'/'as well' ('also check luma') "
                 "ADDS to them; a follow-up that names no source keeps the previous sources; 'anywhere'/'any site' clears them. "
                 if convo else "")
    task = Task(agent=planner, output_pydantic=SearchPlan,
                description=(f"Today is {_now_iso()}. {convo}New user message: \"{message}\". {memo}\n{follow_up}"
                             "Extract city, date_window, date_from, date_to, categories, keywords, state_code, sources. Resolve relative dates "
                             "('this weekend' = the coming Fri-Sun, 'tonight' = today, 'next week' = Mon-Sun after this one) "
                             "into ISO dates. The city MUST come from the request or the conversation, never from preferences; "
                             "if no city appears anywhere set city=null and write a short clarifying_question asking which city. "
                             "If preferences are known and the request is vague, use them for categories. "
                             "SOURCES: if the message says where to look ('on Eventbrite', 'from luma', 'search Meetup for', 'anything on RA', "
                             "'check nycgo'), put each site in sources as a bare hostname: eventbrite -> eventbrite.com; meetup -> meetup.com; "
                             "luma/lu.ma -> lu.ma; dice -> dice.fm; RA/resident advisor -> ra.co; songkick -> songkick.com; "
                             "time out/timeout -> timeout.com; other sites by their obvious domain (instagram -> instagram.com, "
                             "nycgo -> nycgo.com); strip www., paths and query strings from pasted URLs. NEVER copy the source into keywords "
                             "or categories: 'jazz on Eventbrite in Brooklyn' is categories=['jazz'], sources=['eventbrite.com'], keywords=null. "
                             "A source is a preference, not a filter: other sites are still searched. If the message names no source but a "
                             "known preference says 'Prefers events from X', set sources from it (ignore 'finds events on' inside a Profile "
                             "note); a preference never overrides or adds to a source named in the message. sources=[] when nothing applies."),
                expected_output="A SearchPlan JSON object.")
    with trace.span("crew.kickoff", agents=1):
        out = Crew(agents=[planner], tasks=[task], process=Process.sequential, verbose=False).kickoff()
    plan = out.pydantic if out.pydantic else SearchPlan(**json.loads(out.raw))
    return _tidy_sources(plan, message, recalled, history)


def _mentions(text: str, domain: str) -> bool:
    """Does `text` name this site? Matches the domain, its first label ('eventbrite'), its display name, 'luma', 'RA'."""
    names = {domain, domain.split(".")[0], SOURCE_NAMES.get(domain, "")} - {""}
    if domain == "lu.ma":
        names.add("luma")
    if domain == "ra.co":
        names.add("ra")
    return any(re.search(r"(?<![a-z0-9])" + re.escape(n.lower()) + r"(?![a-z0-9])", text.lower()) for n in names)


def _tidy_sources(plan: SearchPlan, message: str = "", recalled: list[str] | None = None, history: list[dict] | None = None) -> SearchPlan:
    """Normalise sources to bare hostnames (max 3), drop any the conversation never named, and keep site names out of keywords.

    A source is legitimate only if the message mentions it, a 'Prefers events from …' note names it, or an earlier
    plan in this chat had it — so a Profile note like 'finds events on Dice' can never become a source on its own.
    """
    plan.sources = list(dict.fromkeys(h for h in (_norm_source(s) for s in plan.sources) if "." in h))[:3]
    prefs = " ".join(n for n in (recalled or []) if n.lower().startswith("prefers events from"))
    earlier = {str(x) for h in (history or []) if isinstance(h, dict) and isinstance(h.get("plan"), dict) for x in (h["plan"].get("sources") or [])}
    plan.sources = [s for s in plan.sources if s in earlier or _mentions(message, s) or _mentions(prefs, s)]
    if plan.keywords and plan.sources:
        names = {s.split(".")[0] for s in plan.sources} | {SOURCE_NAMES[s] for s in plan.sources if s in SOURCE_NAMES}
        if "lu.ma" in plan.sources:
            names.add("luma")
        pat = r"\b(?:on|from|via|at)?\s*(?:" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")\b"
        plan.keywords = re.sub(r"\s+", " ", re.sub(pat, " ", plan.keywords, flags=re.I)).strip() or None
    return plan


def run_scan(message: str, plan: SearchPlan, chaos: bool = False) -> dict:
    """Scanner agent: runs scan.py in the sandbox, repairs on failure. Returns the script's result dict."""
    state: dict = {"plan": plan.model_dump(), "chaos": chaos}
    run_scan_script = make_tools(state)
    scanner = Agent(role="Event Scanner", llm=_llm(), tools=[run_scan_script], verbose=True, max_iter=8,
                    goal="Produce a clean list of events by running the scanner script in a Daytona sandbox.",
                    backstory="You run code only inside the Daytona sandbox through One. The scanner calls You.com to search "
                              "and read listing pages, extracts events, and normalizes them. When it crashes you read the "
                              "traceback, fix the script, and rerun it.")
    task = Task(agent=scanner, tools=[run_scan_script],
                description=(
                    f"Find events for \"{message}\" in {plan.city} (window {plan.date_from or '?'} to {plan.date_to or '?'}). "
                    "The search plan is already loaded as INPUT in the sandbox tool, and so is the SCANNER SCRIPT below.\n"
                    "1. Call run_scan_script with no arguments.\n"
                    "2. If exit_code != 0, read the traceback in stderr, fix the bug in the script (keep its behaviour and output "
                    "contract) and call run_scan_script again with script = the full corrected source. If stderr says TRANSPORT ERROR, "
                    f"the script is fine: call run_scan_script with no arguments again. Never call it more than {MAX_SANDBOX_CALLS} times.\n"
                    "3. Reply with exactly the word DONE.\n\n"
                    "SCANNER SCRIPT (already loaded; shown so you can repair it):\n```python\n" + SCAN_SRC + "\n```"),
                expected_output="DONE")
    curator = Agent(role="Event Curator", llm=_llm(), verbose=True,
                    goal="Pick the events that best match what the user asked for and explain the picks briefly.",
                    backstory="You know the city's scene. You rank by fit to the request (topic, dates, neighborhood), "
                              "never invent events, and write like a knowledgeable friend, in two or three sentences.")

    class Curation(BaseModel):
        reply: str = Field(..., description="2-3 sentence reply to the user summarising what was found and the top picks")
        top_ids: list[str] = Field(default_factory=list, description="Event ids in ranked order, best match first (all events, best first)")

    names = source_names(plan.sources)
    src_rule = (f" The user asked for {names} specifically: in top_ids put every event with from_source=true first (then the rest, "
                f"still ranked by fit) and open the reply with what {names} had, e.g. 'On {names}: …; plus 9 more from other sites'. "
                f"If no event has from_source=true, say plainly that nothing matching turned up on {names} and that these are from other sites."
                if plan.sources else "")
    curate_task = Task(agent=curator, context=[task], output_pydantic=Curation,
                       description=(f"The user asked: \"{message}\" ({plan.city}, {plan.date_window or 'any time'}). "
                                    "Call get_events to read the clean events the Scanner produced, then rank ALL of them by fit to the "
                                    "request (in-window and on-topic first) and write the reply. Mention how many were found and name "
                                    "2-3 standouts with their day and venue. If there are no events, say so and suggest widening the search."
                                    + src_rule),
                       expected_output="Curation JSON with reply and top_ids.")

    @tool("get_events")
    def get_events() -> str:
        """Return the clean events produced by the Scanner as compact JSON (id, title, start, venue, platform, price, tags, in_window,
        from_source = it comes from a site the user asked for)."""
        evs = (state.get("result") or {}).get("events") or []
        evs = [e for e in evs if "example.com/chaos" not in (e.get("url") or "")]  # the chaos artifact is not an event
        keys = ("id", "title", "start", "venue", "platform", "price", "tags", "in_window", "from_source")
        return json.dumps([{k: e.get(k) for k in keys} for e in evs], ensure_ascii=False)

    curator.tools = [get_events]
    curate_task.tools = [get_events]

    emit("crew", text="crew started: Planner ✓ → Scanner (Daytona via One) → Curator")
    with trace.span("crew.kickoff", agents=2):
        out = Crew(agents=[scanner, curator], tasks=[task, curate_task], process=Process.sequential, verbose=True,
                   task_callback=lambda o: emit("task", text=f"{getattr(o, 'agent', '')} finished")).kickoff()
    result = state.get("result") or {"events": [], "dropped": {}, "count": 0}
    # the chaos candidate exists only to crash the script; whatever the repair did with it, keep it out of the UI
    result["events"] = [e for e in result.get("events", []) if "example.com/chaos" not in (e.get("url") or "")]
    result["attempts"] = state.get("attempts", 0)
    result["hits"] = (result.get("stats") or {}).get("hits", 0)
    result["pages"] = (result.get("stats") or {}).get("pages", 0)
    curation = None
    try:
        curation = out.pydantic or Curation(**json.loads(_strip_fences(out.raw)))
    except Exception:
        pass
    if curation:
        result["reply"] = curation.reply
        order = {eid: i for i, eid in enumerate(curation.top_ids)}
        result["events"] = sorted(result["events"], key=lambda e: order.get(e["id"], len(order)))
    return result


def _strip_fences(s: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip())
