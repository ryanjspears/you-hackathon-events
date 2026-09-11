> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# VS Code

Give GitHub Copilot's agent mode real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

**Requirements:** GitHub Copilot extension installed and signed in. MCP servers in VS Code run inside Copilot's agent mode.

## Quick Setup

## One-Command Install

Fastest path—drop this in your terminal:

```bash
code --add-mcp '{"name":"you-com","url":"https://api.you.com/mcp?profile=free","type":"http"}'
```

VS Code opens, prompts you to confirm, and the server is live. Free tier—no signup, 100 searches/day.

## Manual Setup

If you'd rather configure by hand: open **Settings → Search → "mcp"**, click **Edit in settings.json**, and add:

```json
{
  "mcp": {
    "servers": {
      "you-com": {
        "type": "http",
        "url": "https://api.you.com/mcp?profile=free"
      }
    }
  }
}
```

**VS Code gotcha:** the top-level key is `mcp.servers`, not `mcpServers`. This is different from Claude Desktop and Cursor's format.

## Higher Rate Limits + Full Toolset

With an API key, you get unlimited queries plus `you-contents` and `you-research`:

```json
{
  "mcp": {
    "servers": {
      "you-com": {
        "type": "http",
        "url": "https://api.you.com/mcp",
        "headers": {
          "Authorization": "Bearer <YDC_API_KEY>"
        }
      }
    }
  }
}
```

Get a key at [you.com/platform](https://you.com/platform).

## Verify in Copilot

Open the Copilot chat panel, switch to **Agent mode**, and click the tools icon. You should see `you-com` listed with its three tools. Tick the tools you want available for the session.

## Quick Demo

In Copilot agent mode:

```text
Search the web for the latest VS Code release notes and tell me what's new in the agent mode.
```

```text
Research which AI code editors support custom MCP servers in 2026, with citations.
```

## Troubleshooting

#### No MCP servers found

Confirm you used `mcp.servers`, not `mcpServers`. VS Code's schema is namespaced differently from other clients.

#### Tools not appearing in Copilot agent mode

Make sure you're in **Agent mode**, not Ask or Edit. MCP tools only surface in Agent mode.

#### Server connects but tools never trigger

In the Copilot tools picker, confirm the You.com tools are ticked. They default to enabled, but a long server list can push them off-screen.

#### 401 with API key

Verify the `Authorization` header is exactly `Bearer YDC-...` with one space.

#### Copilot extension not installed

Install GitHub Copilot from the VS Code marketplace and sign in before configuring MCP.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.