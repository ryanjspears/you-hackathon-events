# Events Scanner

Hackathon entry for **Build with YOU: The Live Web Agent Hackathon** (theme: self-improving agents).

A chat that finds events for you. A CrewAI crew (Planner → Scanner → Curator) runs a scraper script in a **Daytona** sandbox through **One**; the script uses **You.com** search + contents to find events. If the script crashes, the agent repairs it and retries. Your preferences are learned in One memory, so results get better over time.

Details: [`ARCH.md`](ARCH.md) (architecture), [`SPEC.md`](SPEC.md) (API contract).

## Prerequisites

- Python 3.12
- Node 18+
- [One CLI](https://withone.ai) signed in with You.com and Daytona connected:
  ```bash
  npm i -g @withone/cli && one init
  one add you
  one add daytona
  ```

## Env setup

```bash
cp .env.example .env
```

Fill in `.env`:

| Var | Where to get it |
| --- | --- |
| `ONE_SECRET` | https://app.withone.ai/settings/api-keys |
| `ONE_CONNECTION_KEYS` | run `one --agent list`, copy the `key` for `you` and `daytona`, comma-separated |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys (LLM for the agents) |
| `YDC_API_KEY` | https://you.com/platform/api-keys (optional, direct-SDK fallback) |
| `DAYTONA_API_KEY` | https://app.daytona.io/dashboard/keys (optional, direct-SDK fallback) |

## Install

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r api/requirements.txt
cd web && npm install && cd ..
```

Check everything is wired up (One → You.com search + Daytona sandbox):

```bash
python -m api.one_client --selftest
```

## Run

```bash
# terminal 1: API on http://localhost:8000
source .venv/bin/activate && uvicorn api.main:app --port 8000

# terminal 2: UI on http://localhost:3000
cd web && npm run dev
```

Or run the two-run demo from the terminal: `scripts/demo.sh <username>`.

## Tests

```bash
pytest api/tests
```
