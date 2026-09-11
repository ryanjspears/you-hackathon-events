> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Agent Skills

## Overview

[Agent Skills](https://agentskills.io/what-are-skills) are pre-built instructions that tell an agent how to perform a specific task. Skills can also bundle scripts, templates, and reference materials.
Think of a skill as a structured, repeatable prompt that tells an agent how to complete a specific task in a specific way.

The [youdotcom-oss/agent-skills](https://github.com/youdotcom-oss/agent-skills) repository packages You.com skills for current web search, URL content extraction, cited research, finance research, and developer integration discovery. The shared skills work with Agent Skills-compatible clients and are also packaged for Claude Code, Cursor, Codex, GitHub Copilot CLI, Kimi Code, OpenCode, OpenClaw, Pi, and Hermes.

Have an idea for a Skill? We'd love for you to [contribute](https://github.com/youdotcom-oss/agent-skills/issues).

## How Skills Relate to MCP Tools

A skill is an instruction pack. It tells your agent how to approach a task and which tool or API to reach for, but it does not call anything itself. The MCP tools on the You.com server are the callable functions that do the work—`you-search` runs a web search, `you-contents` extracts a page, `you-answer` returns a fast cited answer, `you-research` synthesizes a cited answer, `you-finance` does finance research, and `you-discover` finds the right integration path.

A few skills share a name with the tool they route to. The `you-research` skill and the `you-research` MCP tool are different things: the skill is a set of routing instructions, and the tool is what runs when the agent follows them. Each skill routes to one or more of those tools:

| Skill                  | Routes To                                                                                |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| `you-web`              | `you-search`, `you-contents`, and `you-research` MCP tools                               |
| `you-free`             | `you-search` through the free MCP profile                                                |
| `you-research` (skill) | A local Research API script, a direct API request, or the `you-research` MCP tool        |
| `you-finance` (skill)  | A local Finance Research API script, a direct API request, or the `you-finance` MCP tool |
| `you-discover` (skill) | The `you-discover` MCP tool and the Docs MCP Server `searchDocs` tool                    |

## Available Skills

Pick the skill that matches the task. Search and URL reading route to the MCP tools by default. Research and finance prefer a local script or a direct API request when `YDC_API_KEY` is set, with the matching MCP tool as a fallback.

#### you-web

Web MCP

Route web search, URL reading, and cited synthesis to the `you-search`, `you-contents`, and `you-research` MCP tools.

#### you-free

Free Search

Use keyless basic web search through the `you-search` MCP tool only. No `YDC_API_KEY` or OAuth required.

#### you-research

Research

Route research tasks between agent-led search, a Research API script, and the `you-research` MCP tool as a fallback.

#### you-finance

Finance

Route finance questions to an existing script, a Finance Research API call, or the `you-finance` MCP tool as a fallback.

#### you-discover

Discovery

Find the right You.com API, MCP server, SDK, docs page, plugin, or integration path for an agentic project, using the `you-discover` MCP tool and the Docs MCP Server.

## Prerequisites

Most authenticated skills need a You.com API key. The `you-free` skill is the exception because it uses the free MCP profile with `you-search` only.

### Get an API Key

Get your key at [you.com/platform/api-keys](https://you.com/platform/api-keys).

### Set the Environment Variable

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

## Installation

#### Install all skills

Install the shared skills with the universal Agent Skills installer:

```bash
npx skills add youdotcom-oss/agent-skills
```

#### Install individual skills

Install one or more specific skills when you only need targeted guidance:

```bash
# Install a single skill
npx skills add youdotcom-oss/agent-skills --skill you-web

# Install multiple specific skills
npx skills add youdotcom-oss/agent-skills --skill you-web --skill you-discover
```

## Platform Plugins

Several agent platforms can install You.com skills through host-specific plugin paths.

| Platform           | Install Path                                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| Claude Code        | `/plugin marketplace add youdotcom-oss/agent-skills` then `/plugin install you@you-com`               |
| GitHub Copilot CLI | `copilot plugin marketplace add youdotcom-oss/agent-skills` then `copilot plugin install you@you-com` |
| Codex              | `codex plugin marketplace add youdotcom-oss/agent-skills --sparse .agents/plugins`                    |
| Cursor             | Install `youdotcom-oss/agent-skills` from the Cursor plugin UI or CLI.                                |
| OpenCode           | `opencode plugin @youdotcom-oss/opencode`                                                             |
| OpenClaw           | `openclaw plugins install clawhub:you` or `openclaw plugins install npm:@youdotcom-oss/openclaw`      |
| Pi                 | `pi install npm:@youdotcom-oss/pi`                                                                    |
| Hermes             | `pip install hermes-youdotcom`                                                                        |

## MCP Endpoints

The skills reference the same You.com MCP endpoints documented in the [MCP Server guide](/docs/build-with-agents/mcp-server) and the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server).

| Endpoint                                    | Use It For                                                                                                                 |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `https://api.you.com/mcp`                   | Authenticated You.com MCP tools, including `you-search`, `you-contents`, `you-answer`, `you-research`, and `you-discover`. |
| `https://api.you.com/mcp?profile=free`      | Keyless basic `you-search`.                                                                                                |
| `https://api.you.com/mcp?tools=you-finance` | Finance-only MCP setup with `you-finance`.                                                                                 |
| `https://you.com/docs/_mcp/server`          | You.com docs search through `searchDocs`.                                                                                  |

## Usage

Once installed, your AI coding agent will automatically activate the relevant skill when you describe what you want. For example:

* "Use you-web to find current docs and cite sources."
* "Use you-free for a quick web lookup without auth."
* "Use you-research to investigate this topic across multiple sources."
* "Use you-finance to research this company and cite market data."
* "Use you-discover to find the best You.com integration path for my TypeScript agent."

Each skill provides routing guidance, setup checks, safety rules, and validation steps tailored to the task.

## Resources

#### [GitHub Repository](https://github.com/youdotcom-oss/agent-skills)

Source code and all available skills

#### [API Keys](https://you.com/platform)

Get your You.com API key