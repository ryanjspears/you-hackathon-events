> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# OpenCode

Give OpenCode real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Add You.com to Your OpenCode Config

Edit `~/.config/opencode/opencode.json` (or your project-local `opencode.json`) and add:

```json
{
  "mcp": {
    "you-com": {
      "type": "remote",
      "url": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

This uses the free tier—100 web searches per day, no signup.

## Restart OpenCode

```bash
opencode
```

The server loads on startup. You'll see `you-com` listed when you check connected MCP servers.

## Try It

```text
Search for the latest releases of Bun and summarize the performance improvements.
```

## Higher Rate Limits + Full Toolset

For unlimited queries plus `you-contents` (page extraction) and `you-research` (citation-backed deep research):

```json
{
  "mcp": {
    "you-com": {
      "type": "remote",
      "url": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

Get a key at [you.com/platform](https://you.com/platform).

## Local Install (stdio)

If you'd prefer to run the MCP server locally:

```json
{
  "mcp": {
    "you-com": {
      "type": "local",
      "command": ["npx", "-y", "@youdotcom-oss/mcp"],
      "environment": {
        "YDC_API_KEY": "<YDC_API_KEY>"
      }
    }
  }
}
```

Omit `YDC_API_KEY` for free-tier behavior.

## Quick Demo

```text
Research the OpenCode project: who maintains it, what's the release cadence, and what's on the roadmap.
```

```text
Extract the README from https://github.com/sst/opencode and summarize the install methods.
```

## Troubleshooting

#### Server doesn't load

Check `opencode.json` is valid JSON. OpenCode silently skips invalid MCP entries.

#### spawn npx ENOENT

For local installs, install Node.js 18+ and ensure `npx` is on your `PATH`.

#### 401 errors

Verify the `Authorization` header is exactly `Bearer YDC-...` with one space.

#### Tool calls fail with no error

Check OpenCode's logs (`opencode --debug`) for MCP server errors. Most failures are config-format mismatches.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.