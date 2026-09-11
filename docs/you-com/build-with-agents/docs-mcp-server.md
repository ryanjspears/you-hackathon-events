> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Docs MCP Server

The You.com Docs MCP Server gives AI agents instant access to all of You.com's developer documentation—API references, guides, code examples, and feature explanations—searchable in real time. Connect it to Claude Code, Cursor, VS Code, or any MCP-compatible client, and your agent can ask questions about You.com APIs and get accurate, sourced answers without leaving its workflow.

It is separate from the [You.com API MCP Server](/docs/build-with-agents/mcp-server), which searches the live web. This one searches these docs.

**Server URL:** `https://you.com/docs/_mcp/server`  ·  **Transport:** streamable HTTP  ·  **Auth:** none—publicly accessible, no API key

## Available Tools

### searchDocs

Search across the You.com developer docs to find relevant information, code examples, API references, and guides. Returns contextual passages with titles and direct links to the documentation pages.

| Property  | Value                                       |
| --------- | ------------------------------------------- |
| Tool name | `searchDocs`                                |
| Input     | `query` (string, required)—the search query |
| Output    | Matching doc passages with source URLs      |
| Access    | Read-only, no API key                       |

## Setup

No authentication required. Add the server URL to your preferred AI tool.

#### Claude Code

Run this command in your terminal:

```bash
claude mcp add --transport http fern_mcp_you-com-docs https://you.com/docs/_mcp/server
```

The server is available in all Claude Code sessions immediately.

#### Cursor

Open **Cursor settings → MCP → Add new server**, and paste:

```json
{
  "mcpServers": {
    "fern_mcp_you-com-docs": {
      "url": "https://you.com/docs/_mcp/server"
    }
  }
}
```

Restart Cursor for changes to take effect.

#### VS Code

Create or open `.vscode/mcp.json` in your project, and add:

```json
{
  "servers": {
    "fern_mcp_you-com-docs": {
      "type": "http",
      "url": "https://you.com/docs/_mcp/server"
    }
  }
}
```

#### Other clients

Add `https://you.com/docs/_mcp/server` to your MCP server configuration. Any client that supports streamable HTTP transport—Claude Desktop, JetBrains, Zed, Windsurf, Gemini CLI, and others—can connect. No headers or credentials needed.

## Example Prompts

Once connected, ask your AI tool questions like:

* "How do I use livecrawl with the Web Search API?"
* "Show me the Python SDK quickstart."
* "What does the Research API `output_schema` parameter do?"
* "How do I authenticate my API requests?"
* "How do I filter Web Search results by date?"
* "What's the difference between the Contents API and livecrawl?"

## Example Responses

Here is what `searchDocs` returns for a few real queries:

* *"how do I use livecrawl?"* → Add `livecrawl` to any `/v1/search` request to attach full page content (markdown or html) to each result; `markdown` is recommended for LLMs. `/docs/guides/retrieve-page-content`
* *"Python SDK quickstart"* → `pip install youdotcom`, then `You()` and `you.search(query=...)`. `/docs/sdks/python-sdk`
* *"Research API output schema"* → Pass `output_schema` in the request; the API returns typed JSON with `content_type: "object"`. `/docs/guides/research`
* *"how do I authenticate my API requests?"* → Pass an API key as the `X-API-Key` header (store it in `YDC_API_KEY`); get one at you.com/platform/api-keys. `/docs/administration/api-keys`
* *"filter search results by date"* → Use the `freshness` parameter: `day`, `week`, `month`, `year`, or `YYYY-MM-DDtoYYYY-MM-DD`. `/docs/guides/live-news`

Every response includes a source URL pointing back to the exact documentation page, so your agent (or you) can verify the answer and read more.

## When to Use It

Use the Docs MCP Server as a first step in You.com API discovery. Point your agent at this server, have it `searchDocs` for what you need, then use the [You.com API MCP Server](/docs/build-with-agents/mcp-server) to run real searches, extractions, and research against the live web. The two servers are complementary—one searches the docs, the other searches the web.

## Next Steps

#### [You.com API MCP Server](/docs/build-with-agents/mcp-server)

Give your agent `you-search`, `you-contents`, `you-answer`, `you-research`, and `you-finance` against the live web.

#### [Quickstart](/docs/quickstart)

Get an API key and make your first call in under five minutes.

#### [Agent Skills](/docs/build-with-agents/skills)

Token-efficient skills for Claude Code, Cursor, and other harnesses.