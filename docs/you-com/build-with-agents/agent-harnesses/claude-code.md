> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Claude Code

Give Claude Code real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Add You.com to Claude Code (No API Key)

```bash
claude mcp add --transport http you-com https://api.you.com/mcp
```

Claude Code initiates the OAuth 2.1 flow automatically—sign in with your You.com account in the browser window that opens, and you're done. No API key, no copy-pasting tokens.

## Verify the Tools Are Loaded

Inside a Claude Code session:

```bash
/mcp
```

You should see `you-com` listed with `you-search`, `you-contents`, and `you-research`.

## Try It

```text
Search for the three latest TypeScript 5.5 features and show me code examples for each.
```

## Skip OAuth (Use an API Key)

If you'd rather pass an API key directly—useful for CI, scripts, or shared dev containers:

```bash
claude mcp add --transport http you-com https://api.you.com/mcp \
  --header "Authorization: Bearer <YDC_API_KEY>"
```

Get a key at [you.com/platform](https://you.com/platform).

## Free Tier (No Account, No OAuth)

Want to try it before signing in?

```bash
claude mcp add --transport http you-com https://api.you.com/mcp?profile=free
```

Free tier gives `you-search` only, 100 queries per day. No signup, no auth.

## Quick Demo

```text
Research the trade-offs between WebAssembly and JavaScript for performance-critical browser apps. Use citations.
```

```text
Extract the content from https://modelcontextprotocol.io/specification and summarize the authentication section.
```

## Troubleshooting

#### OAuth window doesn't open

Confirm Claude Code is on the latest version. Run `claude --version` and update if needed.

#### Invalid token after sign-in

Restart Claude Code to clear cached token state, then retry.

#### 401 with API key

Check for extra spaces or smart quotes in the `--header` value.

#### Tools don't show up in /mcp

List configured servers with `claude mcp list`. If `you-com` is there but tools are missing, restart Claude Code.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.