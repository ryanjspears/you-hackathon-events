# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Hackathon project built on the **You.com APIs** (real-time web search, content extraction, cited answers/research). No application code exists yet — the stack will be chosen as the project takes shape. Update this file with build/test/run commands once they exist.

## You.com reference docs (local, offline)

`docs/you-com/` is a full mirror of https://you.com/docs (snapshot 2026-09-11), fetched as Markdown. **Read these before answering any question about the You.com API instead of guessing or searching the web.**

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

## MCP servers (`.mcp.json`, project scope)

- **`you-com-docs`** (https://you.com/docs/_mcp/server, no auth) — `searchDocs` tool returning doc passages with source URLs. Use it for anything not covered by the local mirror or when the mirror may be stale.
- **`you-com`** (https://api.you.com/mcp, OAuth 2.1 — sign in with a You.com account on first use; credentials are stored per-user, nothing in the repo) — live tools `you-search`, `you-contents`, `you-answer`, `you-research`, `you-finance`. These hit the billed APIs, so prefer them for verifying real response shapes and prototyping queries, not for bulk work. `you-discover` recommends which You.com API/SDK/integration fits a task.

Both need one-time approval in Claude Code (`/mcp`). Setup details: `docs/you-com/build-with-agents/agent-harnesses/claude-code.md`.
