> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Windsurf

Give Windsurf's Cascade agent real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Open Windsurf MCP Settings

In Windsurf, open **Settings → Cascade → Model Context Protocol Servers**, click **Add Server**, then paste:

```json
{
  "mcpServers": {
    "you-com": {
      "serverUrl": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

**Windsurf gotcha:** Windsurf uses `serverUrl` (not `url`) for remote MCP servers. Copy-pasting the JSON template from the MCP Server overview page won't work without this rename.

This uses our free tier: 100 web searches per day, no signup.

## Reload Cascade

Click the refresh icon in the MCP panel, or restart Windsurf. The `you-com` server should appear with a green status indicator.

## Try It in Cascade

Open Cascade and prompt:

```text
Search for the latest Astro 5 release notes and summarize the new features.
```

Cascade will request permission to use `you-search` on first call.

## Higher Rate Limits + Full Toolset

For unlimited queries plus `you-contents` (page extraction) and `you-research` (citation-backed deep research):

```json
{
  "mcpServers": {
    "you-com": {
      "serverUrl": "https://api.you.com/mcp",
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
Research which JavaScript runtimes support native TypeScript execution in 2026, with citations.
```

```text
Extract https://docs.astro.build/en/guides/upgrade-to/v5/ and summarize the breaking changes section.
```

## Troubleshooting

#### Server shows red status

Check `serverUrl`, not `url`. Windsurf's config format diverges from Claude Desktop's here.

#### Tools never get called

Cascade may be deferring to its built-in tools. In a prompt, explicitly ask: *"Use the you-com MCP server to search..."*

#### 401 errors with API key

Verify the `Authorization` header is exactly `Bearer YDC-...` with one space. Do not add extra quotes around the value in the JSON.

#### Server loads but tools missing

Restart Windsurf entirely. In-app refresh is unreliable for tool re-discovery.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.