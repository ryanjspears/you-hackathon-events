> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# SDKs & tools overview

You.com meets your agents wherever they run—MCP clients, Python and TypeScript codebases, agent skills and plugins, and the major agent frameworks. Every tool in this section wraps the same four APIs: **Search**, **Contents**, **Research**, and **Finance Research**. Switching between integrations is a transport change, not a capability change. One API key works across everything.

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Choose Your Path

#### [Build in an IDE or MCP client](/docs/build-with-agents/mcp-server)

No API key to start

Connect Claude Code, Cursor, Windsurf, VS Code, or any MCP client with minimal config.

#### [Use an official SDK](/docs/sdks/python-sdk)

Python and TypeScript

Add typed clients with async support, retries, and full Search, Contents, and Research coverage.

#### [Teach your agent the You.com surface](/docs/build-with-agents/skills)

Agent Skills

Install five host-agnostic skills for grounded search, cited research, finance, and integration discovery.

#### [Install through your platform's plugin system](/docs/build-with-agents/skills#platform-plugins)

Plugins

Host-native install paths for Claude Code, Copilot CLI, Codex, Cursor, OpenCode, OpenClaw, Pi, and Hermes.

#### [Connect a framework or automation tool](/docs/integrations)

Integrations

Use native tools and retrievers for crewAI, LangChain, LangGraph, LlamaIndex, Vercel AI SDK, Temporal, n8n, OpenAI GPT OSS, Zapier, and more.

#### [Procure through a marketplace](/docs/partnerships)

Partner network

Find You.com across MCP marketplaces, cloud marketplaces, AI frameworks, and developer tools.

## Most Common Setups

#### Building an agent in an IDE

Use the [MCP Server](/docs/build-with-agents/mcp-server). Five-line config, works with Claude Code and every major IDE. Run it locally without an API key to start, or connect to the remote server for OAuth 2.1 auth and higher rate limits.

#### Building a production agent in code

Use the [Python SDK](/docs/sdks/python-sdk) or [TypeScript SDK](/docs/sdks/typescript-sdk), depending on your stack. Layer in a framework integration if you're using [LangChain](/docs/integrations/langchain), [LangGraph](/docs/integrations/langgraph), or the [Vercel AI SDK](/docs/integrations/vercel-ai-sdk).

#### Adding web grounding to a coding agent

Use [Skills](/docs/build-with-agents/skills). The same five skills run in Claude Code, Cursor, Codex, GitHub Copilot CLI, Kimi Code, OpenCode, OpenClaw, Pi, and Hermes. Install them with `npx skills add youdotcom-oss/agent-skills` or through your platform's [plugin path](/docs/build-with-agents/skills#platform-plugins).

#### No-code or workflow automation

Use [n8n](/docs/integrations/n8n) or [Zapier](/docs/integrations/zapier).

## How It Works

Every integration in this section hits the same APIs:

* **Search**—web and news results with LLM-ready snippets, plus optional highlights or full page content
* **Contents**—full page content extraction from URLs you already have
* **Research**—multi-step synthesis for deep information gathering
* **Finance Research**—citation-backed answers from a finance-optimized index (available via MCP as `you-finance`)

That means:

* You get the same data, the same filtering controls, and the same rate limits regardless of which integration you pick
* Switching between MCP and the SDKs—or between frameworks—is a transport change, not a capability change

#### One API key works across every surface

You can start with MCP, move into an SDK, and add framework integrations later without changing the underlying API capabilities.

## Integrations

Third-party framework, platform, and open-model integrations live on the [Integrations](/docs/integrations) page—crewAI, LangChain, LangGraph, LlamaIndex, Vercel AI SDK, Temporal, n8n, Zapier, OpenAI GPT OSS, and more as they ship.

#### [Integrations](/docs/integrations)

Browse every integration by category—AI frameworks, automation platforms, and open models.

#### [Partnerships](/docs/partnerships)

Browse MCP marketplaces, cloud marketplaces, and partner directories where You.com is available.

## Developer Tools

#### [MCP Server](/docs/build-with-agents/mcp-server)

Connect You.com directly to any MCP-enabled IDE—Cursor, VS Code, Claude Code, Windsurf, and more.

#### [Agent Skills](/docs/build-with-agents/skills)

Five host-agnostic skills for grounded search, cited research, finance, and integration discovery.

#### [Docs MCP Server](/docs/build-with-agents/docs-mcp-server)

A searchDocs tool that lets any agent search this documentation.

## Official SDKs

#### [Python SDK](/docs/sdks/python-sdk)

Official Python SDK for Web Search, Answer, Contents, Research, and Finance Research APIs.

#### [TypeScript SDK](/docs/sdks/typescript-sdk)

Official TypeScript SDK for Web Search, Contents, and Research APIs.

## Next Steps

#### [Quickstart](/docs/quickstart)

Get an API key and run your first call in five minutes

#### [API reference](/docs/api-reference/search/v1-search)

Full parameter and schema docs for every endpoint

#### [Error reference](/docs/using-the-api/error-code-reference)

HTTP error codes, causes, and rate-limit handling