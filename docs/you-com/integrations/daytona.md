> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Daytona

[Daytona](https://www.daytona.io) runs AI-generated code in isolated sandboxes, each one behind an outbound firewall. Sandboxes with full internet access, meaning Tier 3 and Tier 4, reach the You.com APIs with no configuration at all. On Tier 1 and Tier 2, where organization network policy takes precedence over per-sandbox settings, You.com is listed on Daytona's [essential-services allow list](https://www.daytona.io/docs/en/network-limits#aiml-services). Bring your own API key.

## API Hosts

Read this table before you configure anything. The You.com APIs are split across two hosts, and which one you hit decides what a firewall rule has to say.

| API                  | Host           |
| -------------------- | -------------- |
| Web Search API       | `ydc-index.io` |
| Contents API         | `ydc-index.io` |
| Answer API           | `api.you.com`  |
| Research API         | `api.you.com`  |
| Finance Research API | `api.you.com`  |
| MCP server           | `api.you.com`  |

Daytona's essential-services entry covers `you.com` and `*.you.com`, so anything on `api.you.com` is reachable on every tier. `ydc-index.io` is a separate domain and needs its own allow-list entry. A sandbox that can reach one host but not the other fails in a confusing way: Research and Answer keep working while Web Search and Contents time out.

Confirm reachability from a Tier 1 or Tier 2 sandbox before you build on it. Organization network policy on those tiers cannot be overridden per sandbox, so a blocked host has no per-sandbox workaround. The [verification step](#getting-started) below returns the status code you need.

---

## Getting Started

### Install the SDKs

```bash title="Python"
pip install daytona youdotcom
```

```bash title="TypeScript"
npm add @daytona/sdk @youdotcom-oss/sdk
```

Set `DAYTONA_API_KEY` in the environment where your control script runs. Get a You.com API key at [you.com/platform](https://you.com/platform).

### Store Your API Key as a Daytona Secret

Do not bake `YDC_API_KEY` into a snapshot or pass it as a plain sandbox environment variable. A [Daytona Secret](https://www.daytona.io/docs/en/secrets) keeps the plaintext out of the sandbox: the sandbox gets an opaque placeholder, and Daytona's outbound proxy swaps in the real key only for hosts you name.

```python title="create_secret.py"
from daytona import CreateSecretParams, Daytona

daytona = Daytona()

daytona.secret.create(CreateSecretParams(
    name="youdotcom-api-key",
    value="<YDC_API_KEY>",
    description="You.com API key for sandbox agents",
    hosts=["ydc-index.io", "api.you.com"],
))
```

```typescript title="create-secret.ts"
import { Daytona } from "@daytona/sdk";

const daytona = new Daytona();

await daytona.secret.create({
  name: "youdotcom-api-key",
  value: process.env.YDC_API_KEY,
  description: "You.com API key for sandbox agents",
  hosts: ["ydc-index.io", "api.you.com"],
});
```

`hosts` is the set of destinations the proxy will substitute the real value for, and it needs both entries. `ydc-index.io` covers the Web Search API and Contents API. `api.you.com` covers the Answer API, Research API, Finance Research API, and the [MCP server](/docs/build-with-agents/mcp-server). Drop either one and calls to that host go out carrying the placeholder instead of your key, which comes back as a `401`.

### Create a Sandbox and Verify the Path

Map the secret to the environment variable name the You.com SDKs already look for, then confirm the sandbox can actually reach the API before you build anything on top of it.

```python title="verify.py"
from daytona import CreateSandboxFromSnapshotParams, Daytona

daytona = Daytona()

sandbox = daytona.create(CreateSandboxFromSnapshotParams(
    language="python",
    secrets={"YDC_API_KEY": "youdotcom-api-key"},
))

response = sandbox.process.exec(
    'curl -sS -o /dev/null -w "ydc-index.io: %{http_code}\\n" '
    '-G https://ydc-index.io/v1/search '
    '-H "X-API-Key: $YDC_API_KEY" --data-urlencode "query=test"; '
    'curl -sS -o /dev/null -w "api.you.com:  %{http_code}\\n" '
    'https://api.you.com/v1/billing/account_balance '
    '-H "X-API-Key: $YDC_API_KEY"',
    timeout=60,
)
print(response.result)
```

```typescript title="verify.ts"
import { Daytona } from "@daytona/sdk";

const daytona = new Daytona();

const sandbox = await daytona.create({
  language: "typescript",
  secrets: { YDC_API_KEY: "youdotcom-api-key" },
});

const response = await sandbox.process.executeCommand(
  'curl -sS -o /dev/null -w "ydc-index.io: %{http_code}\\n" ' +
    '-G https://ydc-index.io/v1/search ' +
    '-H "X-API-Key: $YDC_API_KEY" --data-urlencode "query=test"; ' +
    'curl -sS -o /dev/null -w "api.you.com:  %{http_code}\\n" ' +
    "https://api.you.com/v1/billing/account_balance " +
    '-H "X-API-Key: $YDC_API_KEY"',
  undefined,
  undefined,
  60,
);
console.log(response.result);
```

Both lines should print `200`. The account balance endpoint is a free call, so it checks reachability and key substitution on `api.you.com` without spending credits. A `200` is the only proof that matters here: Daytona scrubs the real key out of responses, so an echo service will show you the placeholder whether substitution worked or not.

Daytona's default command timeout is 10 seconds. Pass an explicit `timeout` for anything that installs packages or runs a research call.

---

## Usage

Everything in this section runs inside the sandbox. The control script that creates the sandbox stays on your machine.

#### Python

Search the live web, then pull the full text of the top result.

```python title="agent.py"
from youdotcom import You
from youdotcom.models import ContentsFormats

# Reads YDC_API_KEY from the environment, which Daytona populated
# with the secret placeholder.
with You() as you:
    results = you.search(query="Daytona sandbox release notes", count=5)

    top = results.results.web[0]
    print(f"{top.title}\n{top.url}\n")

    pages = you.contents(urls=[top.url], formats=[ContentsFormats.MARKDOWN])
    print(pages[0].markdown[:1000])
```

Upload it and run it:

```python
sandbox.fs.upload_file("agent.py", "/home/daytona/agent.py")

result = sandbox.process.exec(
    "pip install -q youdotcom && python /home/daytona/agent.py",
    timeout=180,
)
print(result.result)
```

#### TypeScript

```typescript title="agent.ts"
import { You } from "@youdotcom-oss/sdk";
import { ContentsFormats } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const results = await you.search({
  query: "Daytona sandbox release notes",
  count: 5,
});

const top = results.results.web[0];
console.log(`${top.title}\n${top.url}\n`);

const pages = await you.contents({
  urls: [top.url],
  formats: [ContentsFormats.Markdown],
});
console.log(pages[0].markdown?.slice(0, 1000));
```

Upload it and run it:

```typescript
import { readFileSync } from "node:fs";

await sandbox.fs.uploadFile(readFileSync("agent.ts"), "/home/daytona/agent.ts");

const result = await sandbox.process.executeCommand(
  "npm install -s @youdotcom-oss/sdk && npx tsx /home/daytona/agent.ts",
  undefined,
  undefined,
  180,
);
console.log(result.result);
```

#### cURL

```bash
curl -sS -G https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  --data-urlencode "query=Daytona sandbox release notes" \
  --data-urlencode "count=5"

curl -sS -X POST https://ydc-index.io/v1/contents \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.daytona.io/docs/en/network-limits"], "formats": ["markdown"]}'
```

#### MCP, no key

For a sandbox with no You.com credential at all, point an MCP client at the free profile. It exposes `you-search` only and is capped at 100 queries per day. `api.you.com` is covered by the `*.you.com` entry on Daytona's essential-services allow list.

```json
{
  "mcpServers": {
    "you-com": {
      "url": "https://api.you.com/mcp?profile=free"
    }
  }
}
```

For `you-answer`, `you-contents`, `you-research`, and `you-finance`, use `https://api.you.com/mcp` with an API key. See the [MCP Server guide](/docs/build-with-agents/mcp-server).

---

## How the Secret Reaches You.com

Daytona substitutes secrets in the outbound proxy rather than inside the sandbox, and the rules are narrow enough to be worth stating outright.

| Behavior                                | What it means for You.com calls                                                                                         |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| HTTPS request headers only              | `X-API-Key: $YDC_API_KEY` works, and so does `Authorization: Bearer` against the MCP server                             |
| Plain HTTP is never substituted         | Always call `https://`, never `http://`, on both hosts                                                                  |
| Request bodies pass through unchanged   | Never put the key in a JSON body. Every You.com endpoint takes it as a header, so this costs you nothing                |
| Query parameters pass through unchanged | Same rule. Header auth only                                                                                             |
| Placeholders must be sent verbatim      | Anything that transforms the value before sending, such as Base64-encoding it, produces a header the proxy cannot match |
| Responses are scrubbed                  | If a service echoes the key back, the proxy rewrites it to the placeholder                                              |

---

## Custom Allow Lists

Daytona applies a default network policy based on your organization's billing tier.

| Tier              | Outbound access                                                                                                   | You.com                                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Tier 1 and Tier 2 | Restricted, and the restriction cannot be overridden per sandbox. Organization policy wins over `domainAllowList` | Listed on the essential-services allow list. Verify both hosts from a sandbox before you depend on either |
| Tier 3 and Tier 4 | Full internet by default, with per-sandbox network settings available                                             | Reachable by default                                                                                      |

On a tier with full internet access, no configuration is needed. The moment you narrow a sandbox with `domain_allow_list`, though, you replace the permissive default with your own list, and both You.com hosts have to be on it. Use this value:

```
ydc-index.io,*.ydc-index.io,you.com,*.you.com
```

```python title="Python"
from daytona import CreateSandboxFromSnapshotParams, Daytona

daytona = Daytona()

sandbox = daytona.create(CreateSandboxFromSnapshotParams(
    domain_allow_list="ydc-index.io,*.ydc-index.io,you.com,*.you.com",
    secrets={"YDC_API_KEY": "youdotcom-api-key"},
))
```

```typescript title="TypeScript"
const sandbox = await daytona.create({
  domainAllowList: "ydc-index.io,*.ydc-index.io,you.com,*.you.com",
  secrets: { YDC_API_KEY: "youdotcom-api-key" },
});
```

The list is comma-separated, domains only, with `*.` wildcards and a maximum of 20 entries. `domainAllowList`, `networkAllowList`, and `networkBlockAll` are mutually exclusive, and setting more than one non-empty value returns a `400`.

`you.com` and `*.you.com` cover everything on `api.you.com`, which is the Answer API, Research API, Finance Research API, and the MCP server. They do not cover the Web Search API or the Contents API, both of which are served from `ydc-index.io`. Include both pairs unless you are certain the sandbox will never call Web Search or Contents.

---

## Resources

#### [Daytona Network Limits](https://www.daytona.io/docs/en/network-limits)

Firewall tiers, allow-list parameters, and the essential-services list

#### [Daytona Secrets](https://www.daytona.io/docs/en/secrets)

Placeholder substitution, host allow lists, and substitution scope

#### [Daytona Sandboxes](https://www.daytona.io/docs/en/sandboxes)

Creating, configuring, and managing sandboxes

#### [Process and Code Execution](https://www.daytona.io/docs/en/process-code-execution)

Running commands and code inside a sandbox

#### [Python SDK](/docs/sdks/python-sdk)

You.com Python SDK, reads the key from YDC\_API\_KEY

#### [TypeScript SDK](/docs/sdks/typescript-sdk)

You.com TypeScript SDK for Node and edge runtimes

#### [MCP Server](/docs/build-with-agents/mcp-server)

Remote MCP server at api.you.com, including the keyless free profile

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema