> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# JetBrains IDEs

Give AI Assistant and Junie real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

**Supported IDEs:** IntelliJ IDEA, PyCharm, WebStorm, GoLand, RubyMine, PhpStorm, RustRover, CLion, DataGrip, and other JetBrains IDEs with AI Assistant enabled.

**Requirements:** AI Assistant plugin installed and active subscription (or trial).

## Quick Setup

## Open MCP Settings

Go to **Settings → Tools → AI Assistant → Model Context Protocol (MCP)**, then click **+** to add a new server.

## Add the You.com Server

Select **As JSON** and paste:

```json
{
  "mcpServers": {
    "you-com": {
      "url": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

Click **OK**. The server appears in your MCP list with a status indicator.

This uses our free tier: 100 web searches per day, no signup.

## Verify in AI Assistant Chat

Open the AI Assistant chat panel. Tool calls will route through MCP automatically when relevant. To force a tool call:

```text
Use the you-com MCP server to search for the latest Kotlin Multiplatform release.
```

## Higher Rate Limits + Full Toolset

For unlimited queries plus `you-contents` and `you-research`:

```json
{
  "mcpServers": {
    "you-com": {
      "url": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

Get a key at [you.com/platform](https://you.com/platform).

## Quick Demo

```text
Search for benchmarks comparing Kotlin coroutines vs Java virtual threads, with citations.
```

```text
Extract the content from https://kotlinlang.org/docs/multiplatform.html and summarize the main concepts.
```

## Troubleshooting

#### MCP option missing from settings

Confirm AI Assistant plugin is installed and you have an active subscription. MCP support requires a recent AI Assistant version (2024.3+).

#### Server connects but tools don't fire

JetBrains AI Assistant prefers built-in tools by default. Explicitly mention the server in your prompt to route through MCP.

#### 401 with API key

Verify `Authorization` header is exactly `Bearer YDC-...` with one space. Watch for smart quotes from copy-paste.

#### Server status red after add

Restart the IDE. JetBrains' in-app reload of MCP config is unreliable. Full restart resolves most issues.

For team-wide setup, JetBrains supports project-scoped MCP config in `.idea/mcp.xml`. See the JetBrains MCP docs for sharing config across a repo.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.