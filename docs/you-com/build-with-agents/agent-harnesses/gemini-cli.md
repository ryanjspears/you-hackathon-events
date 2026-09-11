> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Gemini CLI

Give Gemini CLI real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server). (Yes, Gemini's CLI can use You.com—that's what MCP is for.)

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Add You.com to Your Gemini CLI Settings

Edit `~/.gemini/settings.json` and add the You.com server under `mcpServers`:

```json
{
  "mcpServers": {
    "you-com": {
      "httpUrl": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

**Gemini CLI gotcha:** Gemini CLI uses `httpUrl` (not `url`) for streamable HTTP MCP servers. This is different from Claude Code, Cursor, and VS Code.

This uses our free tier: 100 web searches per day, no signup.

## Restart Gemini CLI

```bash
gemini
```

## Verify the Tools Are Loaded

Inside Gemini CLI:

```bash
/mcp list
```

You should see `you-com` listed with `you-search` available. (Upgrade to API key auth to unlock `you-contents` and `you-research`.)

## Higher Rate Limits + Full Toolset

For unlimited queries and the full tool set:

```json
{
  "mcpServers": {
    "you-com": {
      "httpUrl": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

Get a key at [you.com/platform](https://you.com/platform).

## Local Install (stdio)

For offline development or self-hosted use:

```json
{
  "mcpServers": {
    "you-com": {
      "command": "npx",
      "args": ["-y", "@youdotcom-oss/mcp"],
      "env": {
        "YDC_API_KEY": "<YDC_API_KEY>"
      }
    }
  }
}
```

Omit `YDC_API_KEY` for free-tier behavior.

## Quick Demo

```text
Search for the three latest changes to the Gemini API and summarize what's new.
```

```text
Research the differences between Vertex AI Search and Google's general web search API, with citations.
```

## Troubleshooting

#### /mcp list shows nothing

Confirm you used `httpUrl`, not `url` or `serverUrl`. Gemini CLI silently ignores unrecognized keys.

#### Server connects but tools fail

Gemini CLI requires tool name allowlisting in some configs. Check `~/.gemini/settings.json` for a `mcpServers.you-com.includeTools` field. Remove it to allow all tools, or add `"you-search"`, `"you-contents"`, and `"you-research"`.

#### 401 or invalid key

Regenerate at [you.com/platform](https://you.com/platform) and re-paste, watching for extra whitespace.

#### spawn npx ENOENT

For local installs, install Node.js 18+ and ensure `npx` is on your `PATH`.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.