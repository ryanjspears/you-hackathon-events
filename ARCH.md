# ARCH.md — Events Scanner architecture

Hand this file to any agent working on the project. It describes what exists, why, and the rules every component follows. `CLAUDE.md` has vendor docs + CLI conventions; `docs/hackathon-brief.md` has the rubric.

## One-paragraph summary

**Events Scanner** is a chat app: the user types what they want to do ("jazz in Brooklyn this weekend"), a three-agent CrewAI crew (Planner → Scanner → Curator) answers. The Scanner runs `scan.py` inside a **Daytona sandbox through One**; that script calls **You.com** (search fan-out + Contents on listing pages across Eventbrite, Meetup, Luma, Dice, RA, Songkick, Time Out) and OpenAI (extraction), normalizes the results and prints clean events. If the script crashes, the Scanner reads the traceback, patches it and reruns. The Curator ranks the events and writes the reply shown as cards. Every search and every "I'm going" click is recorded; the app builds a preference profile, stores it in **One memory** (`one mem`), and shows a personalised "For you" list next time the user logs in. The self-improving story: the agent repairs its own normalizer when it crashes, and the recommender gets better as the user interacts.

## Vendors and where each one is load-bearing

| Vendor | Role | Where in code |
| --- | --- | --- |
| **One** (withone.ai) | The gateway from the crew to Daytona (and later Google Calendar): CrewAI gets One's four MCP tools from the local server `npx -y @withone/mcp`; every sandbox create/execute/delete is a One action, resolved at startup by title/method/path, never hardcoded. `one mem` is the learning store. | `api/one_client.py`, `api/sandbox.py`, `api/mem.py` |
| **You.com** | Called from *inside the sandbox* by `scan.py`: `POST /v1/search` (highlights, one general + one `site:` query per platform, parallel) to discover listing pages, then `POST /v1/contents` to read up to 10 of them as markdown. `YDC_API_KEY` is passed into the sandbox env. | `api/scripts/scan.py` |
| **Daytona** | Runs the code the agent runs and repairs — never on the laptop. One sandbox per API process (`ttlMinutes: 120`, egress allow-list: You.com, OpenAI, PyPI), `harness.py` inside it returns `{exit_code, stdout, stderr}` for any script. Runs `scan.py` (search → extract → normalize) and `recommend_v0.py` (ranking). | `api/sandbox.py`, `api/scripts/*` |
| **CrewAI** | Orchestration. Planner (chat → SearchPlan) → Scanner (tool `run_scan_script`, repair loop ≤3) → Curator (ranks, writes reply). All three run on the laptop. | `api/crew.py` |
| **OpenAI** | LLM for the agents (`openai/gpt-4o`, `CREW_MODEL` env to override — any LiteLLM model id works). | `api/crew.py` |

Hard constraint: Daytona sandboxes cannot reach `*.withone.ai`, so the crew always runs on the laptop; sandboxes only run pure-Python scripts on JSON we hand them. Free-tier sandbox egress is allow-listed (PyPI, GitHub, `*.you.com`) — no scraping inside sandboxes.

## Runtime topology

```
┌─────────────────────────── web/ (Next.js 16 + shadcn/ui, :3000) ───────────────────────────┐
│ /login  pick a name (cookie)   /chat  prompt → progress chips → EventCards   /  "For you"    │
└──────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                           │ HTTP + SSE (NEXT_PUBLIC_API_URL)
┌──────────────────────────────────────────▼──────────────── api/ (FastAPI, :8000) ───────────┐
│ GET  /api/chat/stream?user&message[&chaos=1]   SSE: recalled → plan → search → sandbox → done │
│ POST /api/events/{id}/interact {user, kind: going|skip}   → mem.learn → recommender.refresh   │
│ GET  /api/recommendations?user                 cached ranking + "Because you like …"           │
│ GET  /api/events/{id}                                                                          │
│                                                                                                │
│  main.py ── asyncio.Semaphore(1) ── run_in_executor ──▶ crew.py                               │
│     │                                                    ├─ Planner  (LLM, output_pydantic)    │
│     │  progress.py: emit() → asyncio.Queue → SSE          ├─ Scanner  (tool: run_scan_script)   │
│     │                                                    └─ Curator  (tool: get_events)        │
│  store.py (SQLite events.db): users, events, searches, interactions, recommendations           │
│  mem.py  (`one --agent mem add/search`, type = pref_<user>)  → "Learned:" / "Recalled:"        │
│  recommender.py: profile from interactions+searches → recommend_v0.py in sandbox → cache       │
└───────────────┬──────────────────────────────────────────────┬─────────────────────────────────┘
                │ one_client.py (MCPServerAdapter, 4 tools)      │ subprocess
        npx -y @withone/mcp  (ONE_SECRET, ONE_CONNECTION_KEYS)   one CLI (mem)
                │
                ▼
  daytona: POST /api/sandbox · POST /toolbox/{id}/process/execute · DELETE /api/sandbox/{id}
           └─ /home/daytona: harness.py + script.py (= scan.py) + input.json (= SearchPlan)
                 scan.py ──▶ ydc-index.io/v1/search, /v1/contents   (YDC_API_KEY from sandbox env)
                         ──▶ api.openai.com (extraction, OPENAI_API_KEY from sandbox env)
```

## Request flow: a chat message

1. `GET /api/chat/stream` → `mem.recall(user, message)` → SSE `recalled` (`Recalled: …` or "nothing yet").
2. `crew.plan_only(message, recalled, history)` — Planner returns `SearchPlan{city, state_code, date_window, date_from, date_to, categories, keywords, sources, clarifying_question}`. `sources` = bare hostnames the user asked to search ("jazz on Eventbrite" → `["eventbrite.com"]`; also free-form sites like `nycgo.com`); a recalled `Prefers events from X` note fills it only when the message names none, and `_tidy_sources` drops any source that neither the message, such a note, nor an earlier plan in the chat mentioned. Earlier turns come in as `history` so follow-ups keep city/dates/sources. **City is required**: if missing, SSE `clarify` and the stream ends. Recalled preferences bias categories when the request is vague.
3. `crew.run_scan(message, plan)` — one crew, two agents:
   - **Scanner** calls `run_scan_script(script)` with `scripts/scan.py` verbatim. The tool writes `script.py` + `input.json` (the plan + `now` + `chaos`) into the sandbox and runs `python3 harness.py script.py input.json` (timeout 240 s). Inside the sandbox `scan.py`: 8 You.com searches (one `site:` query per requested source first with `count: 30`, then the general query with `boost_domains` = sources, then one `site:` per known platform) → hits ranked source → known platform → other → picks listing pages (+3 directory seeds built from city/state/category; only the requested sites' seeds when sources are set) → You.com Contents → per-page OpenAI extraction (parallel) → `normalize()` (dateutil + relative phrases like "Tomorrow at 5:30 PM", drop past/>60 d, dedupe by title+day preferring the requested site's copy, `in_window` + `from_source` flags, source events first within the window; `stats.sources` = hits per requested site) → prints one JSON line. Its `[scan] …` log lines are re-emitted as SSE `scan` events.
   - **Repair loop**: on `exit_code != 0` the Scanner reads the traceback in `stderr`, edits the script and calls the tool again (≤3). `?chaos=1` makes `scan.py` append a candidate with a numeric title so `normalize()` raises `AttributeError` on attempt 1 — the repair is visible in the demo. The chaos artifact is filtered out of the final events.
   - **Curator** reads the clean events via `get_events` and returns `{reply, top_ids}`; events are reordered by `top_ids`.
4. `store.upsert_events`, `store.record_search`, `mem.learn("Searched for … on Eventbrite")`, and when sources were named `mem.learn_sources` (one `Prefers events from …` note per user, merge key `sources:<user>`, rewritten on change, silent when unchanged so memory-derived sources don't loop), SSE `done` with `{events, reply, attempts, hits, pages, dropped, stats, plan, recalled}` (exact shapes in `SPEC.md`).

## Request flow: "I'm going"

`POST /api/events/{id}/interact {user, kind}` → `store.record_interaction` → background: `mem.learn(user, "Went to '<title>' (<platform>, <venue>); likes <tags>")` + `mem.learn_profile` (one `Profile: …` note per user, upserted via merge key `profile:<user>`) — both print `Learned:` → `recommender.refresh(user)` scores future events in the user's city with `recommend_v0.py` **in the sandbox** and caches the ranking. *(Parked: also create the event on the user's Google Calendar via One — see "Later".)*

## Data model (SQLite `events.db`)

- `events(id=sha1(url)[:16], title, start ISO8601, end, venue, address, city, url, platform, price, tags JSON, summary, first_seen, last_seen)`
- `searches(user, message, plan JSON, event_ids JSON, ts)`
- `interactions(user, event_id, kind ∈ {going, skip}, ts)` — unique per (user, event, kind)
- `recommendations(user, event_id, score, reason, ts)` — cache written by `recommender.refresh`
- `users(name, created)` — named users only, no auth (hackathon-grade)

`one mem` records: type `pref_<user>`, data `{content, user}`, tags `events,user:<name>,search|going|profile`, weight 4–7; the profile note carries merge key `profile:<user>` and the source-preference note `sources:<user>` (`find-by-key` → `update`). Search with `one --agent mem search "<q>" --type pref_<user>`.

## Rules for any agent editing this repo

1. **The crew reaches Daytona only through One** (no Daytona SDK in app code; the SDK is a documented fallback). Resolve action ids at runtime with `OneClient.resolve_actions()`; extend `wanted` there for new actions. You.com is called from inside the sandbox by `scan.py` (it is on Daytona's egress allow-list; `*.withone.ai` is not, which is why the crew stays on the laptop).
2. **Code the agent runs or repairs executes only in the Daytona sandbox** via `sandbox.sandbox_run`. Scripts read `INPUT` and print one JSON line; they must not contain a bare `EOF` line (heredoc upload). `scan.py` must stay self-contained (stdlib + `requests` + `dateutil`, all in Daytona's default image) so the agent can edit it as one file.
3. **Keep LLM steps minimal.** The plan, ranking and repair are LLM work; everything inside `scan.py` except extraction is deterministic. Agents get typed `@tool`s, never raw `execute_one_action`.
4. **One crew at a time** (`asyncio.Semaphore(1)` in `main.py`); the MCP adapter is opened once in the FastAPI lifespan. Tool calls into One are serialized by `OneClient._lock`.
5. **Progress is a side channel.** Call `progress.emit(stage, text=…)` from anywhere in the worker; it prints to stdout and forwards to the active SSE stream. Stages: `recalled, plan, clarify, crew, search, sandbox, task, learned, recommend, trace, done, error`.
6. **Every request is traced** (`api/trace.py`). Wrap anything that can be slow in `with trace.span("name", **attrs):`; One actions, `one mem` subprocesses, sandbox phases and every CrewAI LLM/tool/task call are already spans. Spans print `[trace] > name` / `[trace] < name 1.23s attrs` to stdout, stream to the UI as `trace` events, and end in a summary table (`[trace] === chat [id] total …`) plus `done.trace`. Inside the sandbox `scan.py` times its phases into `stats.timing`. `TRACE=0` turns it off.
7. **Print `Recalled:` / `Learned:`** on every run — judges look for them.
8. Never commit `.env`; `.env.example` lists every variable.
9. The known-platform map (domain → display name) exists three times on purpose — `scan.py PLATFORMS` (the sandbox script must be self-contained), `crew.py SOURCE_NAMES`, `web/src/lib/api.ts SITES` — keep them identical.

## Environment

`.env`: `YDC_API_KEY` (passed into the sandbox for `scan.py`), `DAYTONA_API_KEY` (fallback only), `ONE_SECRET` (One API key; same as the CLI's), `ONE_CONNECTION_KEYS` (comma list from `one --agent list`), `OPENAI_API_KEY` (crew on the laptop + extraction in the sandbox), optional `CREW_MODEL` (default `openai/gpt-5.6-luna`; GPT-5 models get `reasoning_effort=none` so tool calling works on chat completions), `SCAN_MODEL` (extraction model inside the sandbox, default `gpt-5.6-luna` — measured ~95% of gpt-5.6-sol yield at 1/20th the price; `gpt-5.4-mini` if accuracy matters more), `EVENTS_TZ` (default America/New_York), `EVENTS_DB`.

Run: `source .venv/bin/activate && uvicorn api.main:app --port 8000` and `cd web && npm run dev`. Selftest: `python -m api.one_client --selftest`. Tests: `pytest api/tests`. Try the scanner without the crew: `set -a; . ./.env; set +a; python api/scripts/harness.py api/scripts/scan.py plan.json` (plan shape in `SPEC.md` §5 plus `now`). Frontend contract: `SPEC.md`.

## Later (parked, in priority order)

1. **Google Calendar on "I'm going"** — the "completed the loop" rubric item. Fast path: `one add google-calendar` on the builder account, resolve "Create an Event in a Calendar" (`POST /v3/calendars/primary/events`, body `summary, location, description, start/end {dateTime, timeZone}`), call it from the interact route.
2. **One Connect** for per-user calendars: OAuth app at app.withone.ai (confidential, https redirect via `cloudflared tunnel`), routes `GET /api/one/authorize` + `GET /api/one/callback`, tokens per user, then the same create-event call with the user's bearer over One's passthrough API. Playbook: `npx skills add withoneai/connect`.
3. **Tuner**: an agent task that rewrites `score()` in the recommender when the user's "going" events aren't in the top 10, evaluates in the sandbox, keeps the better version.
4. **Deep scan** button: You.com Research `standard` + `output_schema` → `events[]`.
