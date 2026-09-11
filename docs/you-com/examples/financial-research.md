> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Financial Research Example

A portable [Agent Skill](/docs/build-with-agents/skills) for company financials and market data. It routes finance-specific questions to the standard [You.com MCP server](/docs/build-with-agents/mcp-server)'s `you-finance` tool, supplements narrative context with `you-research` when needed, and reports figures with periods and sources so stale data is visible.

---

## What You'll Build

A `SKILL.md` package for finance-specific research. The skill sends filings, fundamentals, market data, and ticker comparison requests to `you-finance`, supplements narrative context with `you-research`, and reports every figure with its period and source so stale numbers are visible.

## When It Fires

The question is about filings, fundamentals, or market data for a named company or ticker.

---

## Prerequisites

#### [You.com API key](https://you.com/platform)

Required for the research, contents, and finance tools.

#### [You.com MCP server](/docs/build-with-agents/mcp-server)

Connect your agent harness to the remote MCP server at `https://api.you.com/mcp`.

If `you-finance` isn't visible in your harness, enable it with the MCP server's `?tools=` parameter or the `YDC_ALLOWED_TOOLS` environment variable.

## Install the Skill

1. Connect your agent harness to the You.com MCP server—see the [MCP server guide](/docs/build-with-agents/mcp-server).
2. Save the skill below as `SKILL.md` in your harness's skills directory (or download it).
3. The agent invokes `you-finance` (and `you-research` for context) whenever the trigger fires.

#### Download SKILL.md

Grab the ready-to-use skill file.

## The Skill

```markdown title="SKILL.md"
---
name: financial-research
description: Use when the user asks about company financials, filings, or market data - "pull X's fundamentals", "what did Y report", "compare these tickers". For finance topics specifically.
---

# Financial research (You.com)

## When This Fires
The question is about filings, fundamentals, or market data for a named
company or ticker.

## How to Retrieve
1. Call the standard You.com MCP server's `you-finance` tool. If it is not
   visible, tell the user to enable it with the MCP server `?tools=` parameter
   or `YDC_ALLOWED_TOOLS`.
2. For narrative context around the numbers, supplement with `you-research`.
3. Return figures with their reporting period and source. Flag anything stale.
```

## Example Output

```markdown
# Financial research: ACME

## Latest Reported Period
Fiscal Q2 2026.

## Key Figures
- Revenue: $1.42B, up 18% year over year.
- Gross margin: 64.1%, down 90 bps year over year.

Staleness check: figures are from the latest reported quarter available in the
retrieval results.

Sources:
[1] Company filing
[2] Earnings release
```

---

## Next Steps

#### [Competitive Intel Example](/docs/examples/competitive-intel)

Structured company and market briefs.

#### [Finance Research API](/docs/guides/finance-research)

The deep financial research endpoint.

#### [MCP Server](/docs/build-with-agents/mcp-server)

All tools, setup, and configuration.