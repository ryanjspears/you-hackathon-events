> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Cecli

Give Cecli real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

Cecli is the community-maintained Aider fork with native MCP support, so You.com plugs in without a wrapper or plugin.

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Add You.com to Your Cecli Config

Edit `.cecli.conf.yml` and add:

```yaml
mcp-servers:
  mcpServers:
    youcom:
      transport: http
      url: https://api.you.com/mcp?profile=free
```

This uses the free tier—100 web searches per day, no signup.

## Start Cecli

```bash
cecli
```

## Verify the Server Loaded

```text
/list-mcp
```

`youcom` appears under the loaded servers.

## Try It

```text
Search for the latest releases of Bun and summarize the performance improvements.
```

## Higher Rate Limits + Full Toolset

For unlimited queries plus `you-contents` (page extraction) and `you-research` (citation-backed deep research):

```yaml
mcp-servers:
  mcpServers:
    youcom:
      transport: http
      url: https://api.you.com/mcp
      headers:
        Authorization: "Bearer <YDC_API_KEY>"
```

Get a key at [you.com/platform](https://you.com/platform).

## Local Install (stdio)

If you'd prefer to run the MCP server locally:

```yaml
mcp-servers:
  mcpServers:
    youcom:
      transport: stdio
      command: npx
      args: ["-y", "@youdotcom-oss/mcp"]
      env:
        YDC_API_KEY: "<YDC_API_KEY>"
```

Omit `env` for free-tier behavior.

## Pair It With `/web`

Cecli's built-in `/web` scrapes one URL you already know. You.com finds the URL worth scraping. Together they cover the full loop:

```text
Search for the current recommended way to configure Ruff's import sorting, then /web the page you find.
```

This matters most when you run Cecli against a local or offline model. Those models cannot reach the web at all, so search is the only path to anything past their training cutoff.

## Keep Long Sessions Alive

Cecli can heartbeat HTTP servers so idle connections do not drop during long editing sessions:

```yaml
mcp-servers:
  mcpServers:
    youcom:
      transport: http
      url: https://api.you.com/mcp?profile=free
      keepalive_interval: 60
```

The interval accepts 5 to 300 seconds, and defaults to 300 when omitted.

## Quick Demo

```text
Research the Cecli project: who maintains it, what's the release cadence, and what's on the roadmap.
```

```text
Extract the README from https://github.com/cecli-dev/cecli and summarize the install methods.
```

## Troubleshooting

#### Server doesn't load

Run `cecli --verbose` to see MCP server loading details, then confirm `.cecli.conf.yml` is valid YAML.

#### Server is configured but inactive

`/list-mcp` separates loaded servers from configured-but-inactive ones. MCP servers are enabled by default, so an inactive entry usually means it was explicitly disabled with `enabled: false`, or excluded by a server include/exclude list.

#### 401 errors

Verify the `Authorization` header is exactly `Bearer YDC-...` with one space. The keyed endpoint is `https://api.you.com/mcp` with no `?profile=free`.

#### spawn npx ENOENT

For local installs, install Node.js 18+ and ensure `npx` is on your `PATH`.

#### Connection drops on long sessions

Set `keepalive_interval` on the server entry. See "Keep Long Sessions Alive" above.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.