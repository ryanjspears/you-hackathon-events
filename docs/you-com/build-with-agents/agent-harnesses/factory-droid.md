> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Factory Droid

Give Factory Droid real-time web search, content extraction, and citation-backed research through the [You.com MCP Server](/docs/build-with-agents/mcp-server).

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quick Setup

## Add You.com to Droid (No API Key)

```bash
droid mcp add you https://api.you.com/mcp --type http
```

Droid initiates the OAuth 2.1 flow automatically. Run `/mcp` inside a Droid session, then sign in to You.com in the browser window that opens. No API key, no copy-pasting tokens.

## Verify the Tools Are Loaded

Inside a Droid session:

```bash
/mcp
```

You should see `you` listed with `you-search`, `you-contents`, `you-answer`, `you-research`, `you-balance`, and `you-discover`.

## Try It

```text
Search the web for the latest news about artificial intelligence and summarize the top three results.
```

## Skip OAuth (Use an API Key)

If you'd rather pass an API key directly—useful for CI, scripts, or shared dev containers:

```bash
droid mcp add you https://api.you.com/mcp --type http \
  --header 'Authorization: Bearer <YDC_API_KEY>' --no-oauth
```

The `--no-oauth` flag prevents Droid from attempting OAuth alongside the header. Get a key at [you.com/platform](https://you.com/platform).

### Keep the Key Out of the Config File

Droid expands `${NAME}` references in `mcp.json` at connection time. Use single quotes so the shell passes the variable through literally, and Droid resolves it from your environment when it connects:

```bash
droid mcp add you https://api.you.com/mcp --type http \
  --header 'Authorization: Bearer ${YDC_API_KEY}' --no-oauth
```

The raw config file never stores the expanded value, so secrets stay out of disk and version control. If `YDC_API_KEY` is unset, the connection fails with an error naming the missing variable.

## Free Tier (No Account, No OAuth)

```bash
droid mcp add you https://api.you.com/mcp?profile=free --type http --no-oauth
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

Run `/mcp` inside a Droid session and select the `you` server to trigger the browser sign-in flow. Confirm Droid is on the latest version with `droid --version`.

#### Invalid token after sign-in

Run `/mcp`, select the `you` server, and choose **Clear Auth** to remove stored credentials, then retry the connection.

#### 401 with API key

Add `--no-oauth` to prevent Droid from attempting OAuth alongside your header. Check for extra spaces or smart quotes in the `--header` value.

#### Tools don't show up in /mcp

List configured servers with `droid mcp list`. If `you` is there but tools are missing, restart Droid. Remove and re-add the server with `droid mcp remove you` if the connection state is stuck.

## Resources

#### [MCP Server Reference](/docs/build-with-agents/mcp-server)

Endpoint, authentication, and full tool reference.

#### [SDKs & Tools Overview](/docs/integrations-overview)

Browse every You.com SDK, agent tool, and integration.