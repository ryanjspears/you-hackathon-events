> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Pi

Give Pi real-time web search, content extraction, and citation-backed research through the [You.com agent skills](/docs/build-with-agents/skills). [Pi](https://pi.dev/) is a minimal terminal coding harness from Earendil Inc. that uses [skills](https://agentskills.io/specification)—not MCP—for capability extension, so the same You.com skills that power Claude Code, Cursor, and Codex work in Pi too.

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Install the You.com Skills

From your Pi project root:

```bash
npx skills add youdotcom-oss/agent-skills
```

This installs the full You.com skill set from [github.com/youdotcom-oss/agent-skills](https://github.com/youdotcom-oss/agent-skills). The skills follow the [agentskills.io specification](https://agentskills.io/specification), which Pi reads natively—no Pi-specific package needed.

Only want one skill? Pin to a specific one:

```bash
npx skills add youdotcom-oss/agent-skills --skill youdotcom-cli
```

## Set Your API Key

The You.com skills read the `YDC_API_KEY` environment variable. Set it before launching Pi:

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

Get a key at [you.com/platform](https://you.com/platform).

## Start Pi

```bash
pi
```

## Try It

Inside a Pi session:

```text
Search the web for the latest TypeScript 5.5 release notes and summarize the breaking changes.
```

Pi activates the relevant skill automatically when a task involves search or page extraction.

## Keyless Tier

Want to try it without signing up? The `you-search` tool runs on a free tier (100 queries/day, no auth) when no API key is set—leave `YDC_API_KEY` unexported and Pi will fall back to the keyless endpoint. Page extraction and deep research require a key.

## Quick Demo

```text
Research the trade-offs between Pi's skill model and MCP for capability extension. Cite sources.
```

```text
Extract the install methods from https://pi.dev/docs/latest and turn them into a checklist.
```

## SDK users: OpenClaw

Building agents with an SDK rather than running them in a terminal harness? The same skills work with [OpenClaw](https://docs.openclaw.ai/tools/skills)—see the [agent-skills repo](https://github.com/youdotcom-oss/agent-skills) for SDK-side integration.

## Troubleshooting

#### pi: command not found

Install Pi from [pi.dev](https://pi.dev/docs/latest) and confirm with `pi --version`.

#### Skill doesn't activate

Confirm the skill files are present in your project. The `npx skills add` step writes them to disk. See [pi.dev/docs/latest](https://pi.dev/docs/latest) for Pi's skill-discovery rules.

#### 401 errors

Confirm `YDC_API_KEY` is exported in the shell that launched Pi, not just in a sub-shell, and starts with `YDC-`.

#### Hit the keyless rate limit

Set `YDC_API_KEY` to lift the cap and unlock `you-contents` and `you-research`.

## Resources

#### [Agent Skills](/docs/build-with-agents/skills)

Skill catalog, install commands, and usage examples.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.