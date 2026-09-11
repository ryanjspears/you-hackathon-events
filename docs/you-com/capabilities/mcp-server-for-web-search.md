> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# MCP Server for Web Search

The **Model Context Protocol (MCP)** is the emerging standard for giving AI agents and assistants access to tools and data. Any MCP-compatible client—Claude Desktop, Cursor, Windsurf, Zed, or a custom agent you're building—can connect to any MCP server to pick up new capabilities. No SDK glue code, no custom tool definitions, no per-framework wrappers.

This guide covers how MCP works for web search specifically, why it's the right way to give an LLM access to the internet, and how to install and configure the You.com MCP server in the clients developers actually use.

**TL;DR**—MCP is the USB-C port for AI tools. The You.com MCP server is a web search plug that fits it. Install it in Claude, Cursor, or any MCP client, and your assistant can query the live web with structured, citation-ready results.

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## What MCP Is, in One Paragraph

Model Context Protocol is an open specification that defines how an LLM client talks to an external tool server. The client announces "here's what my model can call"; the server announces "here are the tools I expose"; the two communicate over stdio or HTTP using a small, stable JSON-RPC schema. The value is portability: one MCP server works in every MCP-compatible client, and one MCP client works with every MCP server. No bespoke integrations per pair.

For web search, this matters because every agent framework and every assistant historically re-implemented the same web-search tool, slightly differently, in their own SDK. MCP collapses that into one server that every client can use.

## Why Web Search Is the Highest-Value MCP Tool

Of the tools you can bolt onto an MCP client, web search punches above its weight. A few reasons:

* **It unlocks every other tool.** Most agent tasks start with "figure out what the current state of X is." File tools, code tools, and API tools all become more useful when the agent can first check the web for context.
* **It removes the training-cutoff ceiling.** Without web access, an assistant is bounded by what its model saw months or years ago. With it, yesterday's news is in scope.
* **It's the one tool every agent needs.** File I/O, database access, and code execution are workload-specific. Web search is universal.

If you're only going to install one MCP server, a search server is the one with the highest hit rate across tasks.

## What a "Good" MCP Search Server Looks Like

Not all MCP servers are equal. For a search server specifically, four things matter:

* **Structured results, not HTML.** The server should return JSON with titles, URLs, and pre-extracted snippets—not a rendered SERP. The LLM can't parse HTML efficiently.
* **Real index, not scraped SERPs.** Servers that scrape Google or Bing break frequently and violate ToS. A server backed by an independent index is stable.
* **Low latency.** MCP calls are in the critical path of every agent turn. A p95 above a couple of seconds makes the assistant feel sluggish.
* **Sensible tool surface.** One or two well-named tools beat ten overlapping ones. MCP clients pass every tool description to the model on every turn, so a bloated tool list taxes the context window.

The You.com MCP server is built against all four. It exposes a small set of tools backed by the You.com Search and Contents APIs—the same independent index that powers the rest of the platform.

## What the Server Exposes

For web search and grounding, the server exposes four tools. An MCP client also sees a few specialized tools for finance research, integration discovery, and account balance, documented in the [MCP Server reference](/docs/build-with-agents/mcp-server):

* `you-search`—web and news search with structured snippets. Input: `query` (string), plus optional filters. Output: list of results with `title`, `url`, and pre-extracted `snippets`.
* `you-contents`—extract the cleaned page content from a URL in Markdown or HTML format. Input: `url` (string). Output: full page content ready for LLM consumption.
* `you-research`—multi-step research for deeper questions. Input: `query` (string). Output: synthesized, citation-backed report with `lite`, `standard`, `deep`, `exhaustive`, and `frontier` effort levels.
* `you-answer`—fast, citation-backed answers from real-time web results in a single call. Input: `query` (string), plus optional freshness, country, language, and domain filters. Output: one synthesized answer with inline citations and supporting web results.

These four cover the full grounding → citation → deep-dive loop inside an assistant. The rest of the surface is opt-in or specialized, so it stays out of the way unless you reach for it.

## Install: Remote HTTP Server (Recommended)

The remote server at `https://api.you.com/mcp` is the fastest path—no install, always up to date. Authenticate with either a bearer API key or OAuth 2.1 (any MCP client that implements the authorization flow can connect without credentials and the flow starts automatically).

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

Get an API key at [you.com/platform](https://you.com/platform).

## Install: Claude Desktop (Local NPM Package)

Claude Desktop is the reference MCP client. If you prefer a local server—for offline use, self-hosting, or air-gapped environments—install via the NPM package. Configuration lives in `claude_desktop_config.json`.

* **macOS path:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows path:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the You.com server to the `mcpServers` block:

```json
{
  "mcpServers": {
    "ydc-server": {
      "command": "npx",
      "args": ["-y", "@youdotcom-oss/mcp"],
      "env": {
        "YDC_API_KEY": "<YDC_API_KEY>"
      }
    }
  }
}
```

Restart Claude Desktop. The `you-search` tool will appear in the tool picker, and Claude will call it automatically when a question needs fresh information.

## Install: Cursor

Cursor supports MCP through its settings UI or a config file at `~/.cursor/mcp.json`. The remote server is the recommended setup—paste this, without the `type` field:

```json
{
  "mcpServers": {
    "ydc-server": {
      "url": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

After saving, restart Cursor. The search tool is available inside Cursor's agent mode—useful for grounding code suggestions in current documentation (new library versions, recent RFCs, fresh Stack Overflow answers).

## Install: Custom MCP Client

If you're building your own MCP client, connect to the server over stdio using any MCP client library. Here's a Python example using the official `mcp` package:

```python
import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@youdotcom-oss/mcp"],
    env={"YDC_API_KEY": os.environ["YDC_API_KEY"]},
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print([t.name for t in tools.tools])
            # → ['you-search', 'you-contents', 'you-research', 'you-answer', 'you-balance', 'you-discover']

            # Call the search tool
            result = await session.call_tool(
                "you-search",
                arguments={"query": "latest transformer architecture papers"},
            )
            for block in result.content:
                print(block)

asyncio.run(main())
```

That's the full pattern. The MCP client library handles the JSON-RPC transport; you just call tools by name.

## Install: HTTP Transport (for Hosted Clients)

For MCP clients that prefer HTTP over stdio—hosted agents, serverless environments, browser-based clients—the You.com MCP server supports streamable HTTP at:

```
https://api.you.com/mcp
```

Authenticate with a standard bearer header:

```
Authorization: Bearer <YDC_API_KEY>
```

Point any MCP-over-HTTP client at that URL and it'll discover and call tools identically to the stdio transport.

## What a Typical Call Looks Like

Once installed, the MCP client handles invocation. Under the hood, a `you-search` call looks like this on the wire.

**Request (JSON-RPC):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "you-search",
    "arguments": {
      "query": "openai gpt-5 release date"
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"title\": \"...\", \"url\": \"...\", \"snippets\": [\"...\"]}]"
      }
    ]
  }
}
```

The `text` block is a JSON-encoded list of hits—the same structure the Web Search API returns directly. MCP clients parse that and hand the results to the model as an observation.

## Production Patterns

Four upgrades worth doing once the server is installed:

**Scope the tool description.** MCP clients pass every tool description to the model on every turn. If you're running multiple MCP servers, review the descriptions so the model picks the right tool. The search server's default description is tuned for this, but custom builds may need trimming.

**Cache identical queries.** Agents re-ask the same subquestions. A short-TTL cache at the server layer (or in the client) cuts repeated cost significantly on research-style tasks.

**Combine with `you-contents` for depth.** The pattern that works: `you-search` to discover relevant pages, then `you-contents` on the top result for full-page context when snippets aren't enough. This mirrors how a human researcher moves from SERP to article.

**Scope tools to what you need.** On HTTP transport, send `X-Allowed-Tools: you-search` (comma-separated allowlist) to expose only the tools your workflow requires. Smaller tool lists mean smaller prompts and faster tool selection.

## MCP vs. Framework-Native Tools

Most agent frameworks (LangChain, Vercel AI SDK, smolagents, Agno) also support a framework-native web search tool. When do you use MCP instead?

| Use framework-native when...      | Use MCP when...                               |
| --------------------------------- | --------------------------------------------- |
| Building a single-framework agent | Building across multiple frameworks           |
| Deep SDK integration needed       | Tool portability matters                      |
| Single-process, low-latency stdio | Need a hosted client (Claude Desktop, Cursor) |
| Python/TS only                    | Multi-language or polyglot agents             |

Both options use the same underlying Web Search API. MCP is the better choice when portability across clients matters, or when the end user—not the developer—is the one installing the tool (which is the whole Claude Desktop / Cursor story).

## Why You.com for MCP Search Specifically

Three things that matter for this use case:

* **Independent index.** The server isn't a scraper wrapping Google. It's backed by the You.com crawler and index, so it doesn't break when upstream engines change their terms.
* **LLM-native response shape.** Results come back as structured snippets with URLs—exactly the shape MCP clients hand to the model.
* **Built for the ecosystem.** You.com helped shape the early MCP search patterns. The server is designed to play nicely with Claude Desktop, Cursor, and any new MCP client that ships.

## Next Steps

#### [Quickstart](/docs/quickstart)

Get an API key in two minutes.

#### [Web Search API for AI Agents](/docs/capabilities/web-search-api-for-ai-agents)

The framework-native version of this pattern.

#### [Grounding LLM Responses with Citations](/docs/capabilities/grounding-llm-responses-with-citations)

Render MCP search results as cited answers.

#### [MCP Server reference](/docs/build-with-agents/mcp-server)

Full setup guide, IDE configs, and troubleshooting.