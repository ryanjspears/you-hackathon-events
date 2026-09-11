# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Events Scanner** — entry for **"Build with YOU: The Live Web Agent Hackathon"** (You.com, New York, 2026-09-11). **Theme: self-improving & learning agents.** A chat where a **CrewAI** crew (Planner → Scanner → Curator) runs `api/scripts/scan.py` in a **Daytona** sandbox through **One**; the script calls **You.com** (search + contents) to find events, the Scanner repairs it if it crashes, and preferences are learned in `one mem`. **Read `ARCH.md` first** — topology, request flows, data model, and the rules every component follows. `PLAN.md` has the build plan; `docs/hackathon-brief.md` the requirements + rubric; `docs/one-hackathon-page.md` the One hackathon page.

Layout: `api/` (FastAPI + CrewAI; `one_client.py`, `sandbox.py`, `crew.py`, `mem.py`, `recommender.py`, `store.py`, `main.py`, `progress.py`, `trace.py`, `scripts/{harness,scan,recommend_v0}.py`), `web/` (Next.js 16 + shadcn/ui; contract in `SPEC.md`), `scripts/demo.sh`.

Commands (from repo root, `.venv` = Python 3.12):
- Install: `python3.12 -m venv .venv && .venv/bin/pip install -r api/requirements.txt`; `cd web && npm install`
- Selftest (One → You.com search + Daytona sandbox): `.venv/bin/python -m api.one_client --selftest`
- Tests: `.venv/bin/pytest api/tests`
- Run API: `.venv/bin/uvicorn api.main:app --port 8000` (health: `GET /api/health`); UI: `cd web && npm run dev` → http://localhost:3000
- Demo (two-run story): `scripts/demo.sh <user>`
- Frontend checks: `cd web && npx tsc --noEmit -p . && npx eslint src`

Frontend components: `web/` is shadcn/ui (base-ui variant — `Button`/`Badge` take a `render` prop, there is no `asChild`). For chat/agent UI (messages, attachments, tool/worklog, prompt input, etc.) use **AI Elements** — https://elements.ai-sdk.dev (e.g. https://elements.ai-sdk.dev/components/attachments). They are shadcn-style components added into `web/src/components/ai-elements/` with `npx ai-elements@latest add <component>`; check the component's page for its API before using it, and prefer them over hand-rolling equivalents. Backend contract for the UI is `SPEC.md`.

Secrets live in `.env` (git-ignored): `YDC_API_KEY`, `DAYTONA_API_KEY` (SDK fallback only), `ONE_SECRET`, `ONE_CONNECTION_KEYS`, `OPENAI_API_KEY`. See `.env.example`.

## Reference docs (local, offline)

Three doc mirrors live under `docs/`. **Read these before answering questions about these products instead of guessing or searching the web.**

- `docs/you-com/` — full mirror of https://you.com/docs (snapshot 2026-09-11). Table below.
- `docs/daytona/` — mirror of https://www.daytona.io/docs (snapshot 2026-09-10; Ruby/Java/Go SDK pages omitted). Index: `docs/daytona/llms.txt`. Start at `en.md` (intro + quickstart), `sandboxes.md`, `process-code-execution.md`, `file-system-operations.md`, `snapshots.md`, `typescript-sdk/` and `python-sdk/` (per-class reference), `guides/` (49 how-tos), `mcp.md`, `agent-skills.md`. OpenAPI: `openapi.json` (control plane), `toolbox-openapi.json` (in-sandbox toolbox).
- `docs/one-skill.md` — the One hackathon skill (https://hackathon.withone.ai/skill.md): setup paths, the list → search → knowledge → execute loop, You.com and Daytona via One, CrewAI, One Connect, troubleshooting.

### You.com docs map

| Need | File |
| --- | --- |
| Index of every page | `docs/you-com/llms.txt` |
| Zero-to-first-call, all 5 APIs, pricing | `docs/you-com/quickstart.md` |
| Per-endpoint request/response reference | `docs/you-com/api-reference/**/*.md` (index: `api-reference/llms.txt`) |
| OpenAPI 3.1 specs, one per API | `docs/you-com/api-reference/openapi/*.yaml` |
| Deep guides per API (all params, examples, best practices) | `docs/you-com/guides/{search,answer,contents,research,finance-research,live-news,search-operators}.md` |
| Copy-and-customize patterns (deep search, research agent, fact check, competitive intel, news…) | `docs/you-com/examples/*.md` |
| SDK usage | `docs/you-com/sdks/{python-sdk,typescript-sdk}.md` |
| Framework integrations (LangChain, LangGraph, Vercel AI SDK, LlamaIndex, crewAI, n8n, Temporal…) | `docs/you-com/integrations/*.md` |
| Auth, errors, rate limits | `docs/you-com/using-the-api/*.md`, `docs/you-com/rate-limits.md` |
| MCP server / agent skills | `docs/you-com/build-with-agents/*.md` |

Refresh a page with `curl -sL https://you.com/docs/<path>.md -o docs/you-com/<path>.md`.

## You.com API cheat sheet

Auth: `X-API-Key: $YDC_API_KEY` header on every request. `YDC_API_KEY` is the canonical env var name (SDKs read it automatically). Keys are **scoped per product** — a 403 `Missing required scopes` means the key wasn't created with that API enabled. Get keys at https://you.com/platform/api-keys ($100 free credits).

Note the **two hosts**:

| API | Endpoint | Price / 1k | Notes |
| --- | --- | --- | --- |
| Web Search | `POST https://ydc-index.io/v1/search` | $5 | `query`, `count` (≤100), `freshness`, `country`, `language`, `offset` (0–9), `safesearch`, `include/exclude/boost_domains`, `extraction: {extraction_mode: "full_page"\|"highlights", …}` (+$1/1k pages for full_page). Returns `results.web[]` and `results.news[]` with `snippets`. |
| Contents | `POST https://ydc-index.io/v1/contents` | $1 / page | `urls[]`, `formats: ["markdown"\|"html"]`. Returns array of `{url, title, markdown, metadata}`. |
| Answer | `POST https://api.you.com/v1/answer` | $5 | Single-call cited answer. `query` ≤400 chars + same steering params as Search. Returns `answer` (Markdown with `[[n]]` cites), `citations[{source, excerpts}]`, `results`. |
| Research | `POST https://api.you.com/v1/research` | $12–$1,200 | `input`, `research_effort`: `lite`(<10s) / `standard`(default, 10–30s) / `deep`(<120s) / `exhaustive`(<300s) / `frontier`(background only). Also `source_control`, `output_schema` (structured JSON), `background: true` → poll `GET /v1/research/{task_id}` or SSE `GET /v1/research/{task_id}/stream`. Returns `output.{content, content_type, sources[]}`. |
| Finance Research | `POST https://api.you.com/v1/finance_research` | $110 / $500 | Same shape as Research; only `input` + `research_effort` (`deep`\|`exhaustive`). No `source_control`/`output_schema`. |
| Balance | `GET https://api.you.com/v1/billing/account_balance` | — | |

Rate limits: 10 req/s per endpoint (5 for finance). Honor `Retry-After` on 429; read `X-RateLimit-*` headers.

SDKs: `pip install youdotcom` (`from youdotcom import You` — covers all 5 APIs) and `npm add @youdotcom-oss/sdk` (`import { You } from "@youdotcom-oss/sdk"` — Search, Contents, Research only; call Answer and Finance Research with plain `fetch`).

Hackathon guidance: for demos, `Answer` is the fastest path to a grounded, cited response in one call; `Search` + `extraction_mode: "full_page"` when you need to feed pages to your own LLM; `Research` at `standard` for a "wow" multi-source report (use `background: true` for `deep`+ so the UI doesn't hang on a timeout).

## Daytona cheat sheet

Auth: `DAYTONA_API_KEY` (dashboard: https://app.daytona.io/dashboard/keys). SDKs: `npm install @daytona/sdk` / `pip install daytona`. Core loop: `daytona.create()` → `sandbox.process.codeRun(code)` / `sandbox.process.executeCommand(cmd)` → `sandbox.fs.*` for files → `sandbox.delete()`. Sandboxes start in <90 ms, auto-pause/auto-delete are configurable, `snapshots.md` covers persistent images, `preview.md` covers exposing ports. Also reachable through One as platform `daytona`. Claude Code plugin available: `claude plugin marketplace add daytona/skills && claude plugin install daytona@daytona --scope user`.

## MCP servers (`.mcp.json`, project scope)

- **`you-com-docs`** (https://you.com/docs/_mcp/server, no auth) — `searchDocs` tool returning doc passages with source URLs. Use it for anything not covered by the local mirror or when the mirror may be stale.
- **`you-com`** (https://api.you.com/mcp, OAuth 2.1 — sign in with a You.com account on first use; credentials are stored per-user, nothing in the repo) — live tools `you-search`, `you-contents`, `you-answer`, `you-research`, `you-finance`. These hit the billed APIs, so prefer them for verifying real response shapes and prototyping queries, not for bulk work. `you-discover` is an Agentic Resource Discovery search over GitHub/Hugging Face agent catalogs (third-party MCP servers and skills) — not an ideation tool and it does not surface You.com's own resources.
- **`one`** (https://mcp.withone.ai/mcp, OAuth) — One's four tools: `list_one_integrations`, `search_one_platform_actions`, `get_one_action_knowledge`, `execute_one_action`. Remote server uses **snake_case** params. Always run the loop in order (list → search → knowledge → execute); never invent an `action_id` or connection key; confirm before any write. The `one@one` plugin (user scope) and the `one` CLI (`@withone/cli`, `one --agent …` for JSON) are also installed. Platform slugs: `you`, `daytona`, `gmail`, `slack`, …

All need one-time approval in Claude Code (`/mcp`). Setup details: `docs/you-com/build-with-agents/agent-harnesses/claude-code.md`, `docs/one-skill.md`.

The official **`you@you-com` plugin** (user-scoped, from marketplace `youdotcom-oss/agent-skills`) is also installed on this machine. It adds skills `you-web` (search / URL reads / cited synthesis), `you-research`, `you-finance`, `you-discover` (picks the right You.com API/SDK/integration for a task), `you-free`, and its own MCP servers `you` (same URL as `you-com` above), `you-finance`, `you-research`. Prefer those skills over raw tool calls. Onboarding skill source: `docs/you-com/skill.md` (from https://you.com/skill.md).

## One CLI — Platform Integrations

The One CLI (`one`) is installed and authenticated on this machine (account: 18rspears@gmail.com, `live` env, global config). It gives agents a single interface to 750+ third-party platforms (Gmail, Slack, GitHub, Notion, Stripe, You.com, Daytona, …). **Whenever you need to act on a third-party app or external service, use One** — never a raw HTTP call or a scraped page.

- Always put `--agent` right after `one` for JSON output: `one --agent <command>`.
- Workflow, every time, in order: `one --agent list` (get the connection key) → `one --agent actions search <platform> "<outcome>"` → `one --agent actions knowledge <platform> <actionId>` (REQUIRED before execute) → `one --agent actions execute <platform> <actionId> <connectionKey> [-d '<json>' | --query-params '<json>' | --path-vars '<json>']`.
- Never invent an `actionId` or connection key; resolve them at run time. Omit optional params rather than sending `null`.
- Confirm with the user before any write (send, create, update, delete, pay). Reads need no confirmation.
- Before using flows or relay, read the bundled skill first: `one --agent guide flows` / `one --agent guide relay`. Full reference: `one --agent guide`.
- Connect a new platform with `one add <platform>` (interactive, no `--agent` — the user must run it).
- Gotcha: One's composite actions (paths like `/v1/gmail/get-emails`) list `connectionKey` as a required **body** field — include it in `-d` as well as the positional arg, or validation fails with "missing required parameters".
