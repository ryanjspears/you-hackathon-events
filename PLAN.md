# Hackathon plan — You.com

Drafted 2026-09-11 from `you-discover` results, the Docs MCP, and live smoke tests of the key.

## What discovery established

- **Key scope verified:** Search (0.6s), Answer (2.8s), Research `lite` (3.8s), Contents (0.5s) all return 200. Balance: $100.
- **`you-discover` is an ARD catalog search** (GitHub + Hugging Face agent finders), not an ideation tool. It surfaces third-party MCP servers/skills; it does not surface You.com's own resources. Useful later if we need a non-You.com building block (e.g. a news-sentiment MCP), not for choosing the project.
- **Smallest verified integration paths** (from Docs MCP + local mirror):
  - TypeScript: `@youdotcom-oss/sdk` (Search, Contents, Research) + `@youdotcom-oss/ai-sdk-plugin` (`youSearch`, `youContents`, `youResearch` as Vercel AI SDK tools). Answer and Finance Research: plain `fetch`.
  - Python: `youdotcom` SDK covers all five APIs.
- **Differentiators worth building the demo around** (things a generic "chat with search" demo won't show):
  1. **Answer API citations are verified against source text** — `citations[].excerpts` are the verbatim passages. Nobody else hands you receipts.
  2. **Research API `background: true` + SSE stream** — progress events you can render live, plus `output_schema` for structured JSON.
  3. **Finance Research API** — a separate finance-optimized index (filings, fundamentals).
  4. **Search `extraction_mode: "full_page"`** — full Markdown per result in one call.

## Candidate projects

| # | Idea | You.com APIs | Why it demos well | Risk |
|---|------|--------------|-------------------|------|
| **A** | **Receipts** — paste a tweet / article / paragraph; each factual claim gets an evidence card: supporting & contradicting verbatim excerpts, confidence, sources. | Answer (per claim), Search news mode (recency), Contents (primary source) | Uses the *verified excerpts* feature literally on screen; 2–3s per claim; ~$0.01 per claim; fits the official `fact-check` pattern. Universally understood in 10 seconds. | Claim extraction needs an LLM step (Claude); keep it to ≤6 claims per paste. |
| B | **Live Research Console** — type a hard question, watch the research agent's progress stream in, get a cited report with a structured "key facts" sidebar. | Research (`deep`, background + SSE, `output_schema`) | Shows the flagship API's newest features; visually dramatic. | `deep` is <120s — long for a stage demo; use `standard` for demo, `deep` toggle. |
| C | **Battlecard** — company or product name → one-page competitive brief (positioning, pricing, traction, recent moves) with pricing pulled live from their site. | Research + Contents (pricing page) + `output_schema` | Official `competitive-intel` pattern; structured JSON renders into a clean card. | Less novel; overlaps B. |
| D | **Earnings Brief** — ticker → what moved, why, with filing citations. | Finance Research (`deep`) | Only API of its kind; judges may not have seen it. | $0.11/call, 30–120s latency; narrower audience. |

## Recommendation: A (Receipts), with B's streaming as a stretch goal

Reasoning: A is the only idea where You.com's specific advantage (verified excerpts) *is* the UI, not plumbing behind it. It's cheap, fast, and demoable on anyone's paste. If time remains, add a "Go deeper" button on any claim that fires Research in background mode and streams progress (B) — that shows two APIs without a second app.

### Stack

Next.js (App Router) + Vercel AI SDK + `@ai-sdk/anthropic` for claim extraction, `@youdotcom-oss/sdk` for Search/Contents, `fetch` for Answer. Deploy to Vercel. `YDC_API_KEY` + `ANTHROPIC_API_KEY` in `.env`.

### Build order (MVP first)

1. `POST /api/claims` — Claude extracts ≤6 checkable claims from pasted text (structured output).
2. `POST /api/verify` — for each claim, Answer API with `freshness` heuristic; map `citations[].excerpts` to support / contradict via a short Claude judgment; return confidence.
3. UI: paste box → claim cards streaming in as each verifies; excerpt highlights; source favicons (`favicon_url` comes back from Search/Answer).
4. Stretch: "Go deeper" → Research `background: true`, SSE progress in a drawer, final cited report.
5. Stretch: news mode toggle for recency-sensitive claims (`results.news`).

### Open questions

- Actual hackathon theme / judging criteria (not found on you.com/resources/hackathon — it's a blog index).
- Team size and time budget — B as stretch assumes >1 day.
