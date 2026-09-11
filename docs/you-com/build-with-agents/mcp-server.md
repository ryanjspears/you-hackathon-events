> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# MCP Server

## Introduction

The You.com MCP Server is **the fastest path from zero to web-grounded AI agents**. Give your agents real-time access to the latest web information through the [Model Context Protocol](https://modelcontextprotocol.io/). Search current content, get up-to-date answers, and extract live web pages—whether in your IDE or deployed agentic workflows. Built on MCP to **work everywhere your agents do**—one integration, unlimited compatibility across IDEs, frameworks, and production systems.

#### Free to start

Use `you-search` without credentials on the remote server (`?profile=free`) or the local NPM package.

#### Search and contents

Search web and news results, then extract full page content in markdown or HTML.

#### Research tools

Use `you-research` for citation-backed synthesis and `you-finance` for finance-optimized research.

#### Remote or local

Connect to the hosted server or run the local NPM package over STDIO transport.

#### OAuth or API key

Use OAuth 2.1 on supported remote clients, or pass an API key for higher rate limits.

#### Works across IDEs and CLIs

Connect Windsurf, Claude Code, Cursor, VS Code, JetBrains, Factory Droid, and other MCP-enabled clients.

## Getting Started

Get up and running with the You.com MCP Server in three simple steps:

### Choose your setup

You can discover this server in the [Anthropic MCP Registry](https://registry.modelcontextprotocol.io/?q=io.github.youdotcom-oss%2Fmcp) as `io.github.youdotcom-oss/mcp`, or configure it manually:

#### Remote server (recommended)

Always up-to-date with the latest features. Just add the URL
`https://api.you.com/mcp` to your agent's configuration.

#### Local NPM package

For self-hosting or offline development. Install via `npx
    @youdotcom-oss/mcp` to run locally on your machine with STDIO transport.

### Configure your client

Choose from Windsurf, Claude Code, Cursor, VS Code, JetBrains, or other supported editors. See the [Setup guides](#setup-guides) below for IDE-specific configuration.

#### Standard Configuration Templates

#### Remote server

Remote server requires an API key or OAuth 2.1. If your MCP client supports OAuth 2.1, connect without credentials and the authorization flow starts automatically. Otherwise, pass an API key:

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

#### Free tier

Append `?profile=free` to access `you-search` without authentication. `you-answer`, `you-contents`, `you-research`, `you-finance`, `you-balance`, and `you-discover` are not available on the free tier:

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

#### Local NPM package

Web search is available without credentials. Live page crawl (`you-contents`) and research (`you-research`) require an API key. Set `YDC_API_KEY` to unlock all tools:

```json
{
  "mcpServers": {
    "ydc-server": {
      "command": "npx",
      "args": ["@youdotcom-oss/mcp"]
    }
  }
}
```

With an API key:

```json
{
  "mcpServers": {
    "ydc-server": {
      "command": "npx",
      "args": ["@youdotcom-oss/mcp"],
      "env": {
        "YDC_API_KEY": "<YDC_API_KEY>"
      }
    }
  }
}
```

With an API key and specific tools:

```json
{
  "mcpServers": {
    "ydc-server": {
      "command": "npx",
      "args": ["@youdotcom-oss/mcp"],
      "env": {
        "YDC_API_KEY": "<YDC_API_KEY>",
        "YDC_ALLOWED_TOOLS": "you-search,you-finance"
      }
    }
  }
}
```

Get an API key at [you.com/platform](https://you.com/platform).

### Test your setup

Once configured, try these natural language queries with your AI assistant:

* "Search the web for the latest news about artificial intelligence"
* "What is the capital of France?" (with web search)
* "Extract the content from [https://example.com](https://example.com)"
* "Research the pros and cons of WebAssembly vs JavaScript for performance-critical applications"

Your AI assistant will ask for permission to use the You.com MCP tools the first time, then automatically use them for future requests.

## Docs MCP Server

These docs also ship with a separate, read-only **Docs MCP Server** that searches this documentation—a `searchDocs` tool your agent can call to find any page here, with source URLs, no API key. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup, example prompts, and sample responses.

## Authentication

**Remote server** (`https://api.you.com/mcp`) supports one of:

* **Bearer token**—pass `Authorization: Bearer <YDC_API_KEY>` as a request header. Get a key at [you.com/platform](https://you.com/platform).
* **OAuth 2.1**—no API key needed. Any MCP client that implements [MCP Authorization](https://modelcontextprotocol.io/specification/draft/basic/authorization) will automatically handle the flow. When you connect without credentials, the server responds with `401 Unauthorized` and a `WWW-Authenticate` header pointing to the You.com authorization server. Your client opens a browser for you to sign in, then retries the connection with the issued token.
* **Free tier**—no credentials required. Connect to `https://api.you.com/mcp?profile=free` for unauthenticated access to `you-search` only. `you-answer`, `you-contents`, `you-research`, `you-finance`, `you-balance`, and `you-discover` are excluded from this profile. Limited to 100 queries per day.
* **Payment-aware (x402 or MPP)**—no credentials required, and no daily cap. The server passes payment headers (`PAYMENT-SIGNATURE` for x402, `Authorization: Payment` for MPP) through to the upstream API, so a payment-capable client can treat a `402` as a challenge, settle the charge with its own wallet, and retry the tool call. Applies to `you-search` only. See [Machine Payments](/docs/administration/machine-payments) for protocol details.

**Local NPM package** (`npx @youdotcom-oss/mcp`) uses STDIO transport:

* **Free tier**—run without any `YDC_API_KEY` env var. Subject to free-tier rate limits.
* **API key**—set `YDC_API_KEY=<YDC_API_KEY>` in the environment for higher rate limits.
* **Tool scoping**—set `YDC_ALLOWED_TOOLS` to a comma-separated list of tool ids to expose. For example, `YDC_ALLOWED_TOOLS=you-search,you-finance` makes only those two tools available.
* **Free profile**—set `YDC_PROFILE=free` for search-only mode with no authentication. This overrides `YDC_ALLOWED_TOOLS` and does not expose `you-answer`, `you-research`, `you-contents`, `you-finance`, `you-balance`, `you-discover`, or livecrawl.

OAuth is only available for the HTTP remote server. The local NPM package does not support OAuth.

## Available Tools

The You.com MCP Server provides seven tools. Six are enabled by default. `you-finance` is optional and must be requested explicitly. Simply ask in natural language what you want to do—your MCP client automatically handles the rest.

### you-search

Comprehensive web and news search with advanced filtering capabilities. Use this when you need to search the web for information, filter by specific sites or file types, or get the latest news on a topic.

### you-contents

Extract full page content from URLs in markdown or HTML format. Use this when you need to extract and analyze content from web pages for reading or processing in your workflow.

### you-research

Comprehensive web research that returns synthesized, citation-backed answers. Use this when you need in-depth analysis of a topic rather than raw search results. Supports configurable effort levels—`lite`, `standard`, `deep`, `exhaustive`, and `frontier`—so you can balance speed against thoroughness.

### you-answer

Fast, citation-backed answers from real-time web results in a single call. Use this when you need a quick synthesized answer with inline citations rather than the multi-step depth or effort control of `you-research`. Supports freshness, country, language, and domain filters.

### you-finance (optional)

Finance-optimized research with a dedicated financial index covering structured company fundamentals, equity and commodity price data, private company metrics, SEC filings, and financial news. Use this when you need citation-backed answers to financial questions—earnings analysis, market research, due diligence, and macroeconomic research. `you-finance` is not included in the default tool set. Request it explicitly with `?tools=` on the remote server or `YDC_ALLOWED_TOOLS` on the local package (see [Scoping tools](#scoping-tools) below).

### you-discover

Find the right You.com integration path for an agentic project—API, MCP server, SDK, docs page, plugin, or framework. Use this when deciding how to wire You.com into a new agent and you want pointed recommendations instead of browsing the docs yourself.

### you-balance

Return the remaining credit balance for the API key in use. The balance comes back in cents. Divide by 100 for USD. Use this to check usage or remaining quota from inside an agent workflow.

## Scoping Tools

The default MCP endpoint (`https://api.you.com/mcp`) exposes six tools: `you-search`, `you-contents`, `you-research`, `you-answer`, `you-balance`, and `you-discover`. `you-finance` is not included by default. You can control which tools are visible in two ways.

### Using the `?tools=` query parameter (recommended)

Append `?tools=` with a comma-separated list of tool ids to scope the visible tool set. This is the simplest approach and works with any HTTP MCP client.

**Finance only:**

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp?tools=you-finance",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

**Search plus finance:**

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp?tools=you-search,you-finance",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

**Research base (search plus contents, no managed research):**

Scoping to `you-search` and `you-contents` is a cost-control pattern for agent-led research: the agent runs its own search-read-synthesize loop with the two cheap retrieval tools, and the slower, higher-cost `you-research` tool stays out of the tool list entirely. The `you-research` [agent skill](/docs/build-with-agents/skills) pins this profile for exactly that reason.

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp?tools=you-search,you-contents",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

**All seven tools:**

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp?tools=you-search,you-contents,you-research,you-answer,you-finance,you-balance,you-discover",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

### Using the `X-Allowed-Tools` header

When you use HTTP transport, you can restrict which tools are exposed in the MCP session by sending the `X-Allowed-Tools` header on each request. List tool names as a comma-separated allowlist. Omit the header to use the default tool set (`you-search`, `you-contents`, `you-research`, `you-answer`, `you-balance`, `you-discover`).

Add the header in your MCP client configuration alongside any other headers (for example `Authorization`):

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>",
        "X-Allowed-Tools": "you-search,you-finance"
      }
    }
  }
}
```

This applies to Streamable HTTP connections. The local NPM package uses STDIO transport and does not use this header.

### Local NPM package tool scoping

For the local NPM package (`npx @youdotcom-oss/mcp`), use the `YDC_ALLOWED_TOOLS` environment variable instead of `?tools=`:

```json
{
  "mcpServers": {
    "ydc-server": {
      "command": "npx",
      "args": ["@youdotcom-oss/mcp"],
      "env": {
        "YDC_API_KEY": "<YDC_API_KEY>",
        "YDC_ALLOWED_TOOLS": "you-search,you-finance"
      }
    }
  }
}
```

You can also set `YDC_PROFILE=free` for search-only mode with no authentication. `YDC_PROFILE` takes precedence over `YDC_ALLOWED_TOOLS`.

## Use Cases & Examples

Here are practical examples showing how to use the You.com MCP tools in your daily workflow:

### Research & information gathering

**Finding specific information:**

* "Find recent research papers about quantum computing on arxiv.org"
* "Search for TypeScript documentation about generics"
* "Get the latest news about renewable energy from the past week"
* "Find PDF files about machine learning algorithms"

### Content extraction & analysis

**Extracting web content:**

* "Extract the content from this blog post: [https://example.com/article](https://example.com/article)"
* "Get the documentation from these three URLs in markdown format"
* "Pull the HTML content from this page preserving the layout"
* "Batch extract content from these 5 documentation pages"

### Combined workflows

Your AI assistant can orchestrate multiple tools to complete complex tasks:

1. **Research + extract**: "Search for the best TypeScript tutorials, then extract the content from the top 3 results"
2. **Question + deep dive**: "What is WebAssembly? Then search for real-world examples and extract code samples"
3. **News + analysis**: "Find recent articles about AI regulation, then summarize the key points"

### Financial research (requires `you-finance`)

When `you-finance` is enabled, your AI assistant can answer financial questions with citation-backed sources from a finance-optimized index:

* "What were the key drivers of NVIDIA's revenue growth in fiscal year 2025?"
* "Compare the gross margins of Apple, Microsoft, and Google over the past three fiscal years"
* "What are the key risk factors disclosed in Palantir's most recent 10-K filing?"
* "How has the Federal Reserve's rate path affected commercial real estate valuations since 2022?"

`you-finance` is not included in the default tool set. Request it with `?tools=you-finance` on the remote server or `YDC_ALLOWED_TOOLS=you-finance` on the local package. See [Scoping tools](#scoping-tools) for details.

### Pro tips

* **Be specific**: Include domains, date ranges, or file types when searching for more precise results
* **Use natural language**: You don't need to memorize parameters - just describe what you want
* **Ask follow-up questions**: Refine results and dig deeper by asking your AI assistant to clarify or expand
* **Let your agent orchestrate**: For complex workflows, your AI assistant will automatically use multiple tools together

## Setup Guides

#### Windsurf

For setup, follow the MCP installation [guide](https://docs.windsurf.com/windsurf/cascade/mcp#adding-a-new-mcp-plugin).

#### Claude Code

**Quick setup (API key):**

```bash
claude mcp add --transport http ydc-server https://api.you.com/mcp --header "Authorization: Bearer <YDC_API_KEY>"
```

**OAuth 2.1 (no API key):** Connect without credentials and Claude Code will initiate the OAuth flow automatically:

```bash
claude mcp add --transport http ydc-server https://api.you.com/mcp
```

For setup, follow the MCP installation [guide](https://code.claude.com/docs/en/mcp).

#### Claude Desktop

For setup, follow the MCP installation [guide](https://modelcontextprotocol.io/docs/develop/connect-local-servers).

#### Cursor IDE

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=ydc-server\&config=eyJ1cmwiOiJodHRwczovL2FwaS55b3UuY29tL21jcCIsImhlYWRlcnMiOnsiQXV0aG9yaXphdGlvbiI6IkJlYXJlciA8eW91LWFwaS1rZXk%2BIn19)

For setup, follow the MCP installation [guide](https://cursor.com/docs/context/mcp#installing-mcp-servers). Use the configuration template above **without** the `type` field.

To avoid conflicts, go to Settings → Agents tab and turn off Cursor's built-in
web search tool.

#### VS Code

**Quick setup (command line):**

```bash
code --add-mcp '{"name":"ydc-server","url":"https://api.you.com/mcp","type":"http","headers":{"Authorization":"Bearer <YDC_API_KEY>"}}'
```

For setup, follow the MCP installation [guide](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_add-an-mcp-server). Use the configuration template above.

**Requirements:** GitHub Copilot extension must be installed

#### JetBrains IDEs

For setup, follow the MCP installation [guide](https://www.jetbrains.com/help/ai-assistant/mcp.html#connect-to-an-mcp-server). Use the configuration template above.

**Supported IDEs:** IntelliJ IDEA, PyCharm, WebStorm, GoLand, RubyMine, PhpStorm, and more (requires AI Assistant enabled)

#### Zed Editor

For setup, follow the MCP installation [guide](https://zed.dev/docs/ai/mcp#as-custom-servers). Use the configuration template above **without** the `type` field.

#### Factory Droid

**Quick setup (OAuth, no API key):**

```bash
droid mcp add you https://api.you.com/mcp --type http
```

Droid initiates the OAuth 2.1 flow automatically. Run `/mcp` inside a Droid session to complete the browser sign-in.

**API key with env injection (recommended for secrets):**

```bash
droid mcp add you https://api.you.com/mcp --type http \
  --header 'Authorization: Bearer ${YDC_API_KEY}' --no-oauth
```

Droid expands `${YDC_API_KEY}` at connection time, so the key stays out of the config file. Add `--no-oauth` to prevent Droid from attempting OAuth alongside the header.

**Hardcoded API key:**

```bash
droid mcp add you https://api.you.com/mcp --type http \
  --header 'Authorization: Bearer <YDC_API_KEY>' --no-oauth
```

**Free tier (no account):**

```bash
droid mcp add you https://api.you.com/mcp?profile=free --type http --no-oauth
```

**Verify:** `droid mcp list` or `/mcp` inside a Droid session.

For setup, follow the [Factory MCP guide](https://docs.factory.ai/harness/mcp).

#### Other editors

**Codex:**

For setup, follow the MCP installation [guide](https://github.com/openai/codex/blob/main/docs/config.md#streamable-http).

**opencode:**

For setup, follow the MCP installation [guide](https://opencode.ai/docs/mcp-servers/#remote). Use the configuration template above.

**LM Studio:**

For setup, follow the MCP installation [guide](https://lmstudio.ai/docs/app/mcp). Use the configuration template above but **without** the `type` field.

**Gemini CLI:**

Follow the [MCP server setup guide](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html) using the standard configuration template.

## Additional Resources

For complete details on search parameters, response formats, and advanced usage, see the [Web Search API Reference](/docs/api-reference/search/v1-search).

## Troubleshooting

#### API key issues

**Symptoms:** Authentication errors, "Invalid API key" messages

**Solutions:**

1. Verify your API key is active at [you.com/platform](https://you.com/platform)
2. Check for extra spaces or quotes in your configuration
3. Ensure the API key has the correct scopes enabled
4. For the local NPM package, verify the `YDC_API_KEY` environment variable is properly exported
5. If using the remote server, try OAuth 2.1 as an alternative (see the Authentication section)

#### OAuth issues

**Symptoms:** Browser window doesn't open, OAuth flow fails, "Invalid token" errors

**Solutions:**

1. Confirm your MCP client supports OAuth 2.1—check your client's documentation
2. If the browser window opens but authorization fails, try signing in to [you.com](https://you.com) first in the same browser
3. If the flow completes but the client still receives 401, restart the MCP client to clear cached token state
4. As a fallback, use an API key from [you.com/platform](https://you.com/platform) instead

#### Connection issues

**Symptoms:** "Connection refused", timeout errors

**Solutions:**

1. **Remote server:** Check your internet connection and firewall settings
2. **Local package:** Ensure `npx` and Node.js are installed and in your PATH
3. **HTTP mode:** Confirm the server is listening on the correct port
4. Check your MCP client logs for detailed error messages

#### IDE integration issues

**Symptoms:** MCP server not appearing in IDE, tools not available

**Solutions:**

1. Restart your IDE after configuration changes
2. Check the IDE's MCP logs for error messages (Claude Code: terminal output, Claude Desktop: application menu, Cursor: MCP server logs in settings, VS Code: output panel)
3. Verify the configuration file is in the correct location
4. For STDIO transport, ensure the command is executable
5. Try the remote server option if local installation fails

### Report an issue

If you're experiencing issues, we're here to help:

* **Email:** [support@you.com](mailto:support@you.com)
* **Web:** [You.com Support](https://you.com/support/contact-us)
* **GitHub:** [Report an issue](https://github.com/youdotcom-oss/dx-toolkit/issues)

**Pro tip:** When errors occur, check your MCP client logs - they include a
pre-filled mailto link with error details for easy reporting.

## For Contributors

Interested in contributing to the You.com MCP Server? We'd love your help!

Need technical details? Check [AGENTS.md](https://github.com/youdotcom-oss/dx-toolkit/blob/main/AGENTS.md) for complete development setup, architecture overview, code patterns, and testing guidelines.

1. Fork the repository
2. Create a feature branch following naming conventions in [CONTRIBUTING.md](https://github.com/youdotcom-oss/dx-toolkit/blob/main/CONTRIBUTING.md)
3. Follow the code style guidelines and use conventional commits
4. Write tests for your changes (maintain >80% coverage)
5. Run quality checks: `bun run check && bun test`
6. Submit a pull request with a clear description

We appreciate all contributions, whether it's:

* Bug fixes
* New features
* Documentation improvements
* Performance optimizations
* Test coverage improvements

## Transport Protocols

The MCP server supports two transport protocols:

#### HTTP transport

**Use for:**

* Remote server connections
* Web applications
* Production deployments

**Authentication:** Bearer token, OAuth 2.1, or free tier (`?profile=free`, search only)

**Default tools:** `you-search`, `you-contents`, `you-research`, `you-answer`, `you-balance`, `you-discover`

**Optional tools:** `you-finance` (request with `?tools=you-finance`)

**Endpoint:** `https://api.you.com/mcp`

#### STDIO transport

**Use for:**

* Local NPM package installations
* Development environments
* IDEs that only support STDIO

**Authentication:** `YDC_API_KEY` environment variable, or free tier (no env var)

**Default tools:** `you-search`, `you-contents`, `you-research`, `you-answer`, `you-balance`, `you-discover`

**Optional tools:** `you-finance` (request with `YDC_ALLOWED_TOOLS`)

**Command:** `npx @youdotcom-oss/mcp`

## Resources

#### [NPM package](https://www.npmjs.com/package/@youdotcom-oss/mcp)

Official package on npm

#### [GitHub repository](https://github.com/youdotcom-oss/dx-toolkit/tree/main/packages/mcp)

Source code and issues

#### [MCP specification](https://modelcontextprotocol.io/)

Model Context Protocol docs

## Framework Integrations

The You.com MCP server also powers native framework integrations. These packages connect to the same hosted MCP server at `https://api.you.com/mcp` and expose the same tools through framework-specific APIs:

#### [Vercel AI SDK](https://www.npmjs.com/package/@youdotcom-oss/ai-sdk-plugin)

`@youdotcom-oss/ai-sdk-plugin`—async tools for AI SDK applications

#### [LangChain](https://www.npmjs.com/package/@youdotcom-oss/langchain)

`@youdotcom-oss/langchain`—tools for LangChain.js agents

#### [CLI](https://www.npmjs.com/package/@youdotcom-oss/cli)

`@youdotcom-oss/cli`—agent-first CLI for testing and scripting

## Explore Further

#### [Quickstart guide](/docs/quickstart)

Get started with You.com API

#### [Web Search API reference](/docs/api-reference/search/v1-search)

Detailed API documentation

#### [Finance Research API](/docs/guides/finance-research)

Finance-optimized research with citations

#### [SDKs & tools overview](/docs/integrations-overview)

Python, TypeScript, and framework integrations