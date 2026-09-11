# Events Scanner

*Build with YOU: The Live Web Agent Hackathon — theme: self-improving & learning agents.*

Events are scattered across Eventbrite, Meetup, Luma, Dice, Resident Advisor, Songkick, venue sites… Events Scanner is one chat box: say what you want to do and where, and a three-agent CrewAI crew answers. The **Planner** turns the message into a search plan; the **Scanner** pushes `scan.py` into a **Daytona** sandbox through **One** — inside the sandbox the script sweeps the web with **You.com** (search fan-out, then Contents on the listing pages), extracts and normalizes the events — and repairs the script from the traceback if it crashes; the **Curator** ranks the results and writes the reply. The crew reaches Daytona, and its memory, only through One.

It learns: every search and every "I'm going" click is written to One memory. Next time you log in the crew prints `Recalled: …`, biases the search toward what you like, and a "For you" page ranks upcoming events with a scorer that runs in the sandbox. When the normalizer crashes on messy data, the Cleaner agent reads the traceback, patches the script and reruns it — the self-repair loop is visible in the UI (tick "chaos" to force it).

Architecture, rules and data model: [`ARCH.md`](ARCH.md). API contract for the UI: [`SPEC.md`](SPEC.md).

## Stack

| | |
| --- | --- |
| Orchestration | CrewAI 1.15 — Planner → Scanner → Curator (OpenAI gpt-4o by default, `CREW_MODEL` to swap) |
| Web search | You.com `POST /v1/search` (highlights, `site:` fan-out) + `POST /v1/contents` on listing pages — called by `scan.py` inside the sandbox |
| Code execution | Daytona sandbox (created/executed/deleted through One), runs `scan.py` and `recommend_v0.py` |
| Integration layer | One — local MCP server `npx -y @withone/mcp` (4 tools) + `one mem` for learning |
| Backend | FastAPI + SSE, SQLite |
| Frontend | Next.js 16, shadcn/ui, Tailwind |

## Setup

Prereqs: Python 3.12 or 3.13, Node 18+, the [One CLI](https://withone.ai) signed in (`npm i -g @withone/cli && one init`), with You.com and Daytona connected (`one add you`, `one add daytona`).

```bash
git clone <this repo> && cd You
cp .env.example .env            # fill in the keys below
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt
npx -y @withone/mcp --help      # pre-download One's MCP server
python -m api.one_client --selftest   # resolves actions, runs one search, one sandbox command
cd web && npm install && cd ..
```

`.env`:

| Var | Where from |
| --- | --- |
| `ONE_SECRET` | https://app.withone.ai/settings/api-keys (same key the CLI uses) |
| `ONE_CONNECTION_KEYS` | `one --agent list` → comma-separated `key`s for `you` and `daytona` |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `YDC_API_KEY`, `DAYTONA_API_KEY` | only for the direct-SDK fallback; the app itself goes through One |

## Run

```bash
source .venv/bin/activate && uvicorn api.main:app --port 8000     # API
cd web && npm run dev                                               # UI on http://localhost:3000
```

Or the two-run demo from the terminal: `scripts/demo.sh ryan`.

## How the loop closes

1. **Search** — `GET /api/chat/stream?user=ryan&message=jazz in Brooklyn this weekend` streams `Recalled:`, the plan, the sandbox attempts (with the script's own log: You.com queries, pages read, candidates per page), then the Curator's reply and the events. Add `&chaos=1` to watch the Scanner repair a crashing script.
2. **Act** — "I'm going" → `POST /api/events/{id}/interact` → `one mem add` (`Learned: …`) → the recommender re-ranks upcoming events in the sandbox.
3. **Improve** — next login: `Recalled: …` in the plan, "For you" list ranked by what you did. Missing dates, past events and cross-platform duplicates never reach the UI because normalization runs in the sandboxed script — and the agent fixes that script when it breaks.

## Tests

```bash
pytest api/tests            # normalizer + harness contract, runs locally
python -m api.one_client --selftest
```

## Roadmap

See the "Later" section of `ARCH.md`: Google Calendar write on "I'm going" (via One), One Connect so each user brings their own calendar, a Tuner agent that rewrites the scorer, and a Research-API deep scan.
