> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# API Keys

## Overview

API keys authenticate your requests to the You.com API. You can create and manage your keys from the [API Keys page](https://you.com/platform/api-keys) on the Platform.

An agent can also reach the Web Search API without a key at all. [Machine payments](/docs/administration/machine-payments) settle each request from a funded wallet, which suits callers you cannot provision a credential for. Keys remain the right choice when you need [Zero Data Retention](/docs/administration/zero-data-retention), usage analytics, or team roles.

## Creating an API Key

1. Go to [you.com/platform/api-keys](https://you.com/platform/api-keys)
2. Click **Create API Key**
3. Give your key a descriptive name (e.g., "Production", "Development")
4. Copy the key immediately -- it will only be shown once

Store your API key securely as soon as it's created. You won't be able to view the full key again after leaving the page.

## Using Your Key in Code

We use `YDC_API_KEY` as the canonical environment variable name throughout this documentation, our SDKs, and every integration example. Store your key in that variable once, then read it in your code instead of hardcoding the value.

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

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "global birth rate trends"}'
```

Runnable code samples throughout these docs read the key from the `YDC_API_KEY` environment variable, as shown above. Configuration files and setup snippets use `<YDC_API_KEY>` as a placeholder for the key value—replace it with your real key.

## Viewing and Managing Keys

The [API Keys page](https://you.com/platform/api-keys) shows all your active keys with:

* Key name
* Creation date
* Last used date
* A partially masked key value

You can rename or delete keys from this page at any time. If you belong to an organization, your [role](/docs/administration/team-management) determines which keys you can see—Owners and Admins see every key in the organization, while Developers see only the keys they created.

## Rotating and Revoking Keys

To rotate a key, create a new key, update your applications to use the new key, and then delete the old one.

To revoke a key immediately, click **Delete** next to the key on the [API Keys page](https://you.com/platform/api-keys). Revoked keys stop working immediately.

If you suspect a key has been compromised, revoke it immediately and create a new one.

## Security Best Practices

* **Use environment variables**—Store API keys in environment variables, not in your source code. We use `YDC_API_KEY` as the canonical variable name.
* **Never commit keys to version control** -- Add `.env` files to your `.gitignore`.
* **Use separate keys for each environment** -- Create distinct keys for development, staging, and production.
* **Rotate keys regularly** -- Periodically rotate keys to limit the impact of any potential exposure.
* **Apply least privilege** -- Only share keys with team members and services that need them.