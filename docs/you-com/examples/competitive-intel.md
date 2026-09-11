> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Competitive Intel Example

A portable [Agent Skill](/docs/build-with-agents/skills) for sizing up a company, product, or market. It combines `you-research` synthesis with `you-contents` page extraction through the standard [You.com MCP server](/docs/build-with-agents/mcp-server) so the agent produces a consistent brief covering positioning, traction, pricing, recent moves, and sources.

---

## What You'll Build

A `SKILL.md` package that turns company, product, or market prompts into a fixed competitive brief. The skill uses `you-research` for synthesis and `you-contents` for high-signal primary pages such as pricing, product docs, and recent company announcements.

## When It Fires

The user names a company or market and wants it structured: positioning, traction, pricing, and recent moves.

---

## Prerequisites

#### [You.com API key](https://you.com/platform)

Required for the research, contents, and finance tools.

#### [You.com MCP server](/docs/build-with-agents/mcp-server)

Connect your agent harness to the remote MCP server at `https://api.you.com/mcp`.

## Install the Skill

1. Connect your agent harness to the You.com MCP server—see the [MCP server guide](/docs/build-with-agents/mcp-server).
2. Save the skill below as `SKILL.md` in your harness's skills directory (or download it).
3. The agent invokes `you-research` and `you-contents` whenever the trigger fires.

#### Download SKILL.md

Grab the ready-to-use skill file.

## The Skill

```markdown title="SKILL.md"
---
name: competitive-intel
description: Use when the user wants a structured read on a company, product, or market - "size up competitor X", "what's the landscape for Y", "build me a battlecard". Produces a brief, not a chat answer.
---

# Competitive intelligence (You.com)

## When This Fires
The user names a company or market and wants it structured: positioning,
traction, pricing, recent moves.

## How to Retrieve
1. Run `you-research` through the standard You.com MCP server for the entity
   and its category.
2. Use `you-contents` to pull full text from the highest-signal sources - the
   company's own pages, recent coverage.
3. Output a fixed brief: one-line summary, what they sell, signals of traction,
   recent moves, sources.
```

## Example Output

```markdown
# Competitive brief: Acme AI

## One-Line Summary
Acme AI sells workflow automation for regulated support teams, with recent
positioning focused on compliance and auditability.

## What They Sell
- AI case triage and response drafting
- Supervisor review queues

## Signals of Traction
- New enterprise case studies in financial services

Sources:
[1] Company pricing page
[2] Company changelog
```

---

## Next Steps

#### [Deep Research Example](/docs/examples/deep-research)

Open-ended, multi-source synthesis with citations.

#### [Financial Research Example](/docs/examples/financial-research)

Filings, fundamentals, and ticker comparisons.

#### [MCP Server](/docs/build-with-agents/mcp-server)

All tools, setup, and configuration.