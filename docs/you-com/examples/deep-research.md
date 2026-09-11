> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Deep Research Example

A portable [Agent Skill](/docs/build-with-agents/skills) that decides when a user needs thorough web research and routes retrieval through the standard [You.com MCP server](/docs/build-with-agents/mcp-server). Use it for open-ended briefings, deep dives, and cited synthesis across multiple sources.

---

## What You'll Build

A `SKILL.md` package that teaches an agent when a request needs multi-source research instead of a single lookup. The skill sends the user's question and relevant thread context to the standard You.com MCP server's `you-research` tool and preserves inline citations in the final answer.

## When It Fires

The task needs synthesis across several sources, not one fact. Trigger signals: "research", "briefing", "deep dive", "literature on", open-ended "what's known about". For single-fact lookups, a plain search is the better fit.

---

## Prerequisites

#### [You.com API key](https://you.com/platform)

Required for the research, contents, and finance tools.

#### [You.com MCP server](/docs/build-with-agents/mcp-server)

Connect your agent harness to the remote MCP server at `https://api.you.com/mcp`.

## Install the Skill

1. Connect your agent harness to the You.com MCP server—see the [MCP server guide](/docs/build-with-agents/mcp-server).
2. Save the skill below as `SKILL.md` in your harness's skills directory (or download it).
3. The agent loads the skill and invokes `you-research` whenever the trigger fires.

#### Download SKILL.md

Grab the ready-to-use skill file.

## The Skill

```markdown title="SKILL.md"
---
name: deep-research
description: Use when the user needs a thorough, multi-source answer with citations - "research X", "give me a briefing on Y", "what's the state of Z". Not for single-fact lookups; use a plain search for those.
---

# Deep research (You.com)

## When This Fires
The task needs synthesis across several sources, not one fact. Signals:
"research", "briefing", "deep dive", "literature on", open-ended "what's
known about".

## How to Retrieve
1. Call the standard You.com MCP server's `you-research` tool.
2. Pass the user's question plus any relevant context already in the thread.
3. Return the synthesized answer with inline citations preserved. Never strip
   sources.
```

## Example Output

```markdown
# Deep research: agentic browser automation

## Summary
Agentic browser automation is moving from brittle scripts toward goal-directed
agents that can inspect pages, use tools, recover from DOM changes, and cite
the sources behind their conclusions.

Sources:
[1] Vendor docs - browser automation architecture
[2] Recent coverage - enterprise adoption patterns
```

---

## Next Steps

#### [Competitive Intel Example](/docs/examples/competitive-intel)

Turn a company or market into a structured brief.

#### [Research Recipe Example](/docs/examples/research-recipe)

Build your own research skill from a template.

#### [MCP Server](/docs/build-with-agents/mcp-server)

All tools, setup, and configuration.