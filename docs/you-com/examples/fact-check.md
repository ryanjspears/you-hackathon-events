> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Fact Check Example

A portable [Agent Skill](/docs/build-with-agents/skills) for discrete, checkable claims. It searches the claim, pulls primary source text with `you-contents` where useful, compares supporting and contradicting evidence, and returns a calibrated confidence read with citations through the standard [You.com MCP server](/docs/build-with-agents/mcp-server).

---

## What You'll Build

A `SKILL.md` package that turns a discrete claim into an evidence table. The skill searches the claim with `you-search`, pulls primary sources with `you-contents` where useful, separates supporting and contradicting evidence, and returns calibrated confidence instead of an unsupported verdict.

## When It Fires

There is a discrete, checkable claim on the table.

---

## Prerequisites

#### [You.com API key](https://you.com/platform)

Required for the research, contents, and finance tools.

#### [You.com MCP server](/docs/build-with-agents/mcp-server)

Connect your agent harness to the remote MCP server at `https://api.you.com/mcp`.

## Install the Skill

1. Connect your agent harness to the You.com MCP server—see the [MCP server guide](/docs/build-with-agents/mcp-server).
2. Save the skill below as `SKILL.md` in your harness's skills directory (or download it).
3. The agent invokes `you-search` and `you-contents` whenever the trigger fires.

#### Download SKILL.md

Grab the ready-to-use skill file.

## The Skill

```markdown title="SKILL.md"
---
name: fact-check
description: Use when the user wants a specific claim verified - "is it true that X", "fact-check this", "does Y hold up". Returns evidence and a confidence read, not a verdict asserted from memory.
---

# Fact-check (You.com)

## When This Fires
There is a discrete, checkable claim on the table.

## How to Retrieve
1. Search the claim with `you-search`; pull primary sources with `you-contents`.
2. Line up supporting and contradicting evidence side by side.
3. Return the claim, what the evidence shows, a calibrated confidence, and the
   sources. Never assert a verdict the sources don't support.
```

## Example Output

```markdown
# Fact check

## Claim
The company opened its API to all developers this quarter.

## Evidence
Supports:
- The public changelog announced general API availability on May 12.

Complicates:
- Two enterprise-only endpoints remain behind account approval.

## Confidence
High for general API availability. Medium for the stronger claim that every API
surface is open to all developers.

Sources:
[1] Public changelog
[2] Developer docs
```

---

## Next Steps

#### [News & Events Example](/docs/examples/news-events)

Time-bounded, cited retrieval.

#### [Deep Research Example](/docs/examples/deep-research)

Multi-source synthesis with citations.

#### [MCP Server](/docs/build-with-agents/mcp-server)

All tools, setup, and configuration.