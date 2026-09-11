> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Zed

Give Zed's AI assistant real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Open Zed Settings

Press `⌘ ,` (macOS) or `Ctrl ,` (Linux) to open `settings.json`. Add the You.com server under `context_servers`:

```json
{
  "context_servers": {
    "you-com": {
      "source": "custom",
      "url": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

**Zed gotcha:** Zed calls MCP servers **context servers** in its settings schema. The key is `context_servers`, not `mcpServers` or `mcp.servers`. Also: no `"type": "http"` field—Zed infers transport from the presence of `url` vs `command`.

This uses our free tier: 100 web searches per day, no signup.

## Reload Zed

Zed picks up MCP config changes on save, but a restart (`⌘ Q` then reopen) is more reliable.

## Verify the Tools Are Available

Open the assistant panel (`⌘ ?`) and check the tools menu. `you-com` should appear with `you-search` available.

## Higher Rate Limits + Full Toolset

For unlimited queries plus `you-contents` and `you-research`:

```json
{
  "context_servers": {
    "you-com": {
      "source": "custom",
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

For offline development:

```json
{
  "context_servers": {
    "you-com": {
      "source": "custom",
      "command": {
        "path": "npx",
        "args": ["-y", "@youdotcom-oss/mcp"],
        "env": {
          "YDC_API_KEY": "<YDC_API_KEY>"
        }
      }
    }
  }
}
```

**Zed gotcha:** for stdio servers, `command` is an **object** with `path`, `args`, and `env` fields—not a string. This is different from Claude Desktop's format.

Omit `YDC_API_KEY` for free-tier behavior.

## Quick Demo

```text
Search for the latest Zed editor release notes and tell me what's new.
```

```text
Research which Rust-based code editors support MCP in 2026, with citations.
```

## Troubleshooting

#### Server not appearing in assistant

Confirm the key is `context_servers` and you didn't add a `"type"` field. Zed's schema is stricter than most clients.

#### Failed to spawn command

For local installs, Zed's `command` is an object with `path`, `args`, and `env`, not a string. This is a common copy-paste mistake from other clients' configs.

#### Tools never get called

Zed's AI assistant requires you to enable tools explicitly in the panel UI. Click the tools dropdown and tick You.com's tools.

#### 401 with API key

Verify `Authorization` header is exactly `Bearer YDC-...` with one space.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.