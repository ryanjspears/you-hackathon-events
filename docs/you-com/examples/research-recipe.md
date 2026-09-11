> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Research Recipe Example

A portable [Agent Skill](/docs/build-with-agents/skills) template for teams that need a custom research workflow. Copy the recipe, define the trigger, choose the standard [You.com MCP server](/docs/build-with-agents/mcp-server) tools, and lock the output shape so agents retrieve and present evidence consistently.

---

## What You'll Build

A copy-and-customize `SKILL.md` template for teams that need a domain-specific research workflow. The recipe asks the author to define the trigger, choose the standard You.com MCP tools, and lock the output shape before publishing the skill.

## When to Use It

No stock skill fits the task. Start from this recipe when you need a tailored trigger, a specific mix of retrieval tools, or a fixed output template your agent fills.

This recipe is a copy-and-customize example. The same pattern ships as a maintained reference, [agent-led-deep-search.md](https://github.com/youdotcom-oss/agent-skills/blob/main/skills/you-research/references/agent-led-deep-search.md), inside the installable `you-research` skill in the [agent-skills repo](https://github.com/youdotcom-oss/agent-skills)—start there if you want the version that tracks the live skill set.

---

## Prerequisites

#### [You.com API key](https://you.com/platform)

Required for the research, contents, and finance tools.

#### [You.com MCP server](/docs/build-with-agents/mcp-server)

Connect your agent harness to the remote MCP server at `https://api.you.com/mcp`.

## Customize the Recipe

1. **Set the trigger**—define the task type and the phrases that should invoke it.
2. **Choose the endpoints**—`you-research` (synthesis), `you-search` (web/news), `you-finance` (markets), and `you-contents` (page text).
3. **Lock the output shape**—a freeform answer, or a fixed template your agent fills.

#### Download SKILL.md

Grab the template to copy and edit.

## The Template

```markdown title="SKILL.md"
---
name: research-recipe
description: A template for composing a custom research Skill on You.com endpoints. Copy this, set the trigger and the output shape, and wire the retrieval. Use when no stock skill fits the task.
---

# Research recipe (You.com) - template

## When This Fires
Define your trigger here: the task type and the phrases that should invoke it.

## How to Retrieve
1. Choose the endpoint(s): `you-research` (synthesis), `you-search` (web/news),
   `you-finance` (markets), `you-contents` (page text).
2. Call the standard You.com MCP server tools exposed by the agent harness.
3. Define the output shape - a freeform answer, or a fixed template your agent
   fills.
```

## Example: A Filled-In Skill

```markdown
---
name: my-research-skill
description: Use when the user needs a domain-specific research brief.
---

# My research skill

## When This Fires
Define the task type, trigger phrases, and exclusions.

## How to Retrieve
1. Choose the endpoint mix: you-research, you-search, you-finance, you-contents.
2. Call the standard You.com MCP server tools.
3. Include relevant thread context in the retrieval request.

## Output Shape
Return the exact sections your team needs, with citations preserved.
```

---

## Next Steps

#### [Deep Research Example](/docs/examples/deep-research)

A complete, ready-to-use research skill.

#### [Skills overview](/docs/build-with-agents/skills)

How Agent Skills work on You.com.

#### [MCP Server](/docs/build-with-agents/mcp-server)

All tools, setup, and configuration.