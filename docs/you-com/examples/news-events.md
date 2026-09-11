> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# News & Events Example

A portable [Agent Skill](/docs/build-with-agents/skills) for recency-sensitive questions. It routes "latest", "breaking", "this week", and "as of today" requests to [You.com](/docs/build-with-agents/mcp-server) Search in news mode, constrains retrieval to the requested window, and returns dated results with sources.

---

## What You'll Build

A `SKILL.md` package for recency-sensitive questions. The skill detects phrases such as latest, this week, breaking, and as of today, routes the request to `you-search` in news mode, applies the requested date window, and states the as-of time explicitly.

## When It Fires

The answer depends on recency. Trigger signals: "latest", "this week", "breaking", and "as of today".

---

## Prerequisites

#### [You.com API key](https://you.com/platform)

Required for the research, contents, and finance tools.

#### [You.com MCP server](/docs/build-with-agents/mcp-server)

Connect your agent harness to the remote MCP server at `https://api.you.com/mcp`.

## Install the Skill

1. Connect your agent harness to the You.com MCP server—see the [MCP server guide](/docs/build-with-agents/mcp-server).
2. Save the skill below as `SKILL.md` in your harness's skills directory (or download it).
3. The agent invokes `you-search` in news mode whenever the trigger fires.

#### Download SKILL.md

Grab the ready-to-use skill file.

## The Skill

```markdown title="SKILL.md"
---
name: news-events
description: Use when the user asks about recent or breaking developments - "what happened with X this week", "latest on Y", anything time-bounded. Prioritizes freshness over depth.
---

# News & events (You.com)

## When This Fires
The answer depends on recency. Signals: "latest", "this week", "breaking",
"as of today".

## How to Retrieve
1. Call the standard You.com MCP server's `you-search` tool in news mode.
2. Constrain to the requested window; lead with the most recent items.
3. Return dated, cited results. State the as-of time explicitly.
```

## Example Output

```markdown
As of June 18, 2026, 2:00 PM ET:

## Latest on the Requested Topic
- June 18, 2026 - The most recent report says the rollout expanded to three
  additional markets.
- June 17, 2026 - Company leadership confirmed the timeline.

Sources:
[1] News source - June 18, 2026
[2] Company update - June 17, 2026
```

---

## Next Steps

#### [Deep Research Example](/docs/examples/deep-research)

When depth matters more than recency.

#### [Fact Check Example](/docs/examples/fact-check)

Verify a discrete claim against evidence.

#### [MCP Server](/docs/build-with-agents/mcp-server)

All tools, setup, and configuration.