> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Codex CLI

Give Codex CLI real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Add You.com to Codex

Codex reads MCP server config from `~/.codex/config.toml`. Add the You.com server—no API key required:

```toml
[mcp_servers.you-com]
url = "https://api.you.com/mcp?profile=free"
```

This uses our free tier: 100 web searches per day, no signup. Want higher limits and access to `you-contents` and `you-research`? See [Higher rate limits](#higher-rate-limits) below.

## Start Codex

```bash
codex
```

## Verify the Tools Are Loaded

Inside Codex, run:

```bash
/mcp
```

You should see `you-com` listed with the `you-search` tool available. (If you upgrade to API key auth, `you-contents` and `you-research` show up too.)

## Quick Demo

Try these prompts inside Codex:

```text
Search the web for the latest Next.js 15 release notes and summarize the breaking changes.
```

```text
Find three recent benchmarks comparing Claude Sonnet 4.6 and GPT-5 on coding tasks.
```

## Higher Rate Limits

For unlimited queries, page-content extraction (`you-contents`), and deep research (`you-research`), add an API key. Get one at [you.com/platform](https://you.com/platform), then update your config:

```toml
[mcp_servers.you-com]
url = "https://api.you.com/mcp"

[mcp_servers.you-com.http_headers]
Authorization = "Bearer <YDC_API_KEY>"
```

**Codex TOML gotcha:** HTTP headers in Codex's `config.toml` go in a separate `[mcp_servers.<name>.http_headers]` table, not inline. This is different from the JSON `headers` object used by Claude Code, Cursor, and VS Code.

## Local Install (No Network on Startup)

If you'd rather run the MCP server locally via stdio:

```toml
[mcp_servers.you-com]
command = "npx"
args = ["-y", "@youdotcom-oss/mcp"]

[mcp_servers.you-com.env]
YDC_API_KEY = "<YDC_API_KEY>"
```

Omit the `YDC_API_KEY` env var to run on the free tier.

## Troubleshooting

#### Codex doesn't see the tools

Run `codex --version` to confirm you're on a version with MCP support (0.20+), then restart Codex after editing `config.toml`.

#### spawn npx ENOENT

For local installs, install Node.js 18+ and ensure `npx` is on your `PATH`, or switch to the remote hosted URL above.

#### 401 or invalid key

Regenerate at [you.com/platform](https://you.com/platform). Confirm there are no extra spaces around `Bearer`.

#### TOML parse errors on headers

Headers must be under `[mcp_servers.you-com.http_headers]`, not inline as a JSON-style `headers = { ... }` object.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.