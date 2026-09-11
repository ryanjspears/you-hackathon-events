> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Authentication

## How Authentication Works

Every You.com API request requires an API key, passed in the `X-API-Key` header. Get a key from the [Platform API Keys page](https://you.com/platform/api-keys)—new accounts start with \$100 in complimentary credits.

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "global birth rate trends"}'
```

For key creation, rotation, and revocation, see [API Key Management](/docs/administration/api-keys). This page covers how a request is authenticated, not how the key itself is managed.

## The YDC\_API\_KEY Convention

All code samples in these docs read the key from an environment variable named `YDC_API_KEY`. It is the canonical variable name across the docs, the SDKs, and every integration example. Set it once and the samples pick it up.

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

```python
import os
from youdotcom import You

with You(api_key_auth=os.environ["YDC_API_KEY"]) as you:
    results = you.search(query="global birth rate trends")
```

```typescript
import { You } from "@youdotcom-oss/sdk";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });
```

Never hardcode the key in source. Keep it in an environment variable or a secrets manager, and add `.env` files to `.gitignore`.

## Scopes and 403 Responses

API keys are scoped per product. A key without access to a given path returns `403 Forbidden` with `{"detail": "Missing required scopes"}`—for example, calling `/v1/contents` with a key that only has Web Search API access.

If you need access to an API your current key does not cover, create a new key with the right scope from the [Platform](https://you.com/platform/api-keys).

## Keyless Access via the Free MCP Profile

You can try the Web Search API without an API key by connecting any MCP-enabled client to `api.you.com/mcp?profile=free` and using the `you-search` tool. The free profile is limited to 100 queries per day and does not include `you-answer`, `you-contents`, `you-research`, or `you-finance`. For setup, see the [MCP Server guide](/docs/build-with-agents/mcp-server).

For everything beyond evaluation, use an API key.