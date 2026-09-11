> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Cursor

Give Cursor real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## One-Click Install

[![Add MCP Server to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=you-com\&config=eyJ1cmwiOiJodHRwczovL2FwaS55b3UuY29tL21jcCJ9)

Clicking the button opens Cursor and pre-fills the configuration. Cursor will trigger OAuth automatically—sign in to You.com in the browser window that opens, and the integration is live.

## Manual Setup

If you'd rather configure by hand, open **Cursor settings → MCP → Add new server**, and paste:

```json
{
  "mcpServers": {
    "you-com": {
      "url": "https://api.you.com/mcp"
    }
  }
}
```

**Cursor gotcha:** don't include a `"type": "http"` field. Cursor's MCP config format omits it.

## Use an API Key

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

## Use the Free Tier

```json
{
  "mcpServers": {
    "you-com": {
      "url": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

## Turn Off Cursor's Built-In Web Search

Go to **Settings → Agents** and turn off the built-in web search tool. This avoids the agent picking Cursor's lower-quality search when You.com is available, and prevents duplicate tool calls on the same query.

## Quick Demo

Open the agent panel and try:

```text
Find the official Next.js 15 migration guide and pull the breaking-changes section verbatim.
```

```text
Research which AI search APIs offer OAuth 2.1, with citations.
```

## Troubleshooting

#### Server not appearing

Restart Cursor after editing the MCP config. The reload-on-save behavior is unreliable in current builds.

#### OAuth window doesn't open

Check that you don't have a popup blocker active for `cursor://` deeplinks.

#### Tools show but never get called

Confirm Cursor's built-in web search is disabled. The agent may be preferring the cheaper local tool.

#### type field error

Remove the `type` field. Cursor doesn't use it.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.