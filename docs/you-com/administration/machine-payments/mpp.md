> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# MPP

The Machine Payments Protocol (MPP) is an open standard for machine-to-machine payments over HTTP, co-authored by Tempo and Stripe and specified as an IETF draft at [paymentauth.org](https://paymentauth.org).

Like x402, MPP uses the HTTP `402 Payment Required` status code. It adds payment-method neutrality: one client integration can settle in a stablecoin, on a card, or in fiat, and the wire format does not change. The handshake is Challenge, then Credential, then Receipt, built on the standard HTTP authentication headers.

The You.com Web Search and Finance Research APIs accept MPP. A client can call either one with no API key and no You.com account.

Web Search costs \$0.01 per call and Finance Research \$0.11 or \$0.50 depending on the effort tier. None of it draws down your credit balance. If your wallet is on Base or Solana rather than Tempo, [x402](/docs/administration/machine-payments/x402) is half the price on Web Search and identical on Finance Research.

The only method we currently advertise is `tempo`, settling in USDC. Cards and fiat are supported by the protocol but are not enabled on this endpoint yet. If you need to pay by card, use an [API key](/docs/administration/api-keys) with [credits](/docs/administration/billing).

---

## How It Works

1. **The client makes a normal request.** No `X-API-Key`, no `Authorization` header.
2. **You.com responds `402 Payment Required`** with a Challenge in the `WWW-Authenticate` header, using the `Payment` authentication scheme. The Challenge names the price, the payment method, the intent, and when the offer expires.
3. **The client fulfills the payment** by signing a transaction on the named chain.
4. **The client retries the same request** with a Credential in the `Authorization` header. The Credential echoes the Challenge and carries method-specific proof of payment.
5. **You.com verifies the Credential, runs the request, and responds `200 OK`** with a Receipt in the `Payment-Receipt` header.

### Headers

| Header             | Direction        | Contents                               |
| ------------------ | ---------------- | -------------------------------------- |
| `WWW-Authenticate` | You.com → client | Challenge, using the `Payment` scheme  |
| `Authorization`    | Client → You.com | Credential, using the `Payment` scheme |
| `Payment-Receipt`  | You.com → client | Base64url-encoded Receipt              |

---

## Supported Endpoints

| Endpoint                                   | Price per call | Amount in token base units |
| ------------------------------------------ | -------------- | -------------------------- |
| `GET /v1/search`                           | \$0.01         | `10000`                    |
| `GET` or `POST /v1/agents/search`          | \$0.01         | `10000`                    |
| `POST /v1/finance_research` (`deep`)       | \$0.11         | `110000`                   |
| `POST /v1/finance_research` (`exhaustive`) | \$0.50         | `500000`                   |

MPP amounts are expressed in the base units of the token named by `currency`. USDC has six decimals, so `10000` is \$0.01.

The HTTP method differs per endpoint. `/v1/search` offers payment on **GET** only—`POST /v1/search` returns `401`. Finance Research offers payment on **POST** only—`GET /v1/finance_research` returns `401`. The agent search endpoint, `/v1/agents/search`, accepts payment on **both GET and POST**.

The Contents and Research APIs return `401` on every method and do not offer payment terms.

### Web Search

Two endpoints accept MPP for Web Search. `/v1/search` and `/v1/agents/search` share the same pricing, response shape, and parameters. Use `/v1/agents/search` when you need POST, since `POST /v1/search` does not accept machine payments.

One cent is a floor rather than a coincidence. MPP settles through Stripe, and one cent is the smallest amount a Stripe-hosted payment can charge, so the per-call price is exactly one cent. [x402](/docs/administration/machine-payments/x402) has no such minimum and charges \$0.005 for the same call.

Query parameters and the response body are the same as the key-authenticated GET endpoint. See the [Web Search API reference](/docs/api-reference/search/v1-search). Result count is `count`, and an unrecognized parameter is ignored rather than rejected, so a misspelled one silently returns defaults.

`livecrawl` is supported and priced into the Challenge. It adds \$0.001 per result to the underlying price, and MPP then rounds up to the next whole cent:

| Request                             | Challenge amount | Base units |
| ----------------------------------- | ---------------- | ---------- |
| `?query=...&count=10`               | \$0.01           | `10000`    |
| `?query=...&count=10&livecrawl=web` | \$0.02           | `20000`    |
| `?query=...&count=50&livecrawl=web` | \$0.06           | `60000`    |

`count` sets how many pages are charged for, and the crawl mode does not change the price. Because of the cent rounding, small `count` values absorb into the base price: `count=5&livecrawl=web` still quotes `10000`.

The deprecated `livecrawl` parameter still works on the Web Search API. POST callers should prefer the `extraction` parameter—see the [Retrieve page content](/docs/guides/retrieve-page-content) guide.

If you are comparing costs against a key-authenticated integration, machine payments charge per `count` regardless of crawl mode, where [credit billing](/docs/administration/billing) charges per page fetched. At `count=10` with `livecrawl=all` that is 10 pages here and 20 there. Budget from the amount in the Challenge, which is what you actually pay on this path.

Read the amount out of the Challenge rather than computing it. A Challenge issued for one `count` and `livecrawl` combination does not carry over to a different one.

### Finance Research

Finance Research takes a JSON body on POST, so there is no query-string form. The financial question goes in `input`, and `research_effort` selects the tier:

```bash
curl -X POST https://api.you.com/v1/finance_research \
  -H "Content-Type: application/json" \
  -d '{"input": "NVDA Q2 guidance vs consensus", "research_effort": "deep"}'
```

The price is fixed per tier rather than scaling with the request, and `deep` is the default when `research_effort` is omitted. Both tiers land on a whole cent already, so the rounding above does not apply and MPP costs the same as [x402](/docs/administration/machine-payments/x402) here. See the [Finance Research API reference](/docs/api-reference/finance-research/v1-finance_research) for the response shape.

Send `deep` or `exhaustive` and nothing else. Those are the only values the [Finance Research API reference](/docs/api-reference/finance-research/v1-finance_research) accepts, and it returns `422` for anything else. The Challenge is issued before the body is validated, so it will quote a price for an unsupported tier rather than refusing it. Paying against that quote risks spending on a request the endpoint will reject.

Latency is the other thing to plan for. A `deep` call takes under 120 seconds and `exhaustive` under 300, well beyond a typical HTTP client default, so raise your timeout before the payment round trip rather than after.

---

## Payment Methods and Intents

| `method` | Settles through | Notes                                 |
| -------- | --------------- | ------------------------------------- |
| `tempo`  | Tempo L1, USDC  | The only method currently advertised. |

| `intent`       | Supported | Behavior                                                                  |
| -------------- | --------- | ------------------------------------------------------------------------- |
| `charge`       | Yes       | One payment per request. The only intent we advertise.                    |
| `session`      | No        | Pay-as-you-go across many requests, settled in aggregate. On the roadmap. |
| `subscription` | No        | Not applicable to per-query search. Use an API key and credits instead.   |

---

## Reading the Challenge

```http title="402 Payment Required"
HTTP/1.1 402 Payment Required
WWW-Authenticate: Payment id="IptU2AvkLwJDGuVYmu6UADhNiPvcPb1Ln5fmC54lswU",
    realm="api.you.com",
    method="tempo",
    intent="charge",
    description="You.com pay-per-call (Tempo USDC)",
    expires="2026-08-03T14:24:11Z",
    request="eyJhbW91bnQiOiIxMDAwMCIsImN1cnJlbmN5IjoiMHgyMGMwMDAwMDAwMDAwMDAwMDAwMDAwMDBiOTUzN2QxMWM2MGU4YjUwIiwibWV0aG9kRGV0YWlscyI6eyJjaGFpbklkIjo0MjE3fSwicmVjaXBpZW50IjoiMHguLi4ifQ"
```

| Parameter     | Meaning                                                                       |
| ------------- | ----------------------------------------------------------------------------- |
| `id`          | Unique challenge identifier. Echo it back in the Credential.                  |
| `realm`       | Protection space, per RFC 9110. Always `api.you.com`.                         |
| `method`      | Payment method the Challenge applies to. Currently always `tempo`.            |
| `intent`      | Charge shape. Currently always `charge`.                                      |
| `description` | Human-readable description of what is being paid for.                         |
| `expires`     | ISO 8601 expiry, 10 minutes after issue. Pay and retry before this timestamp. |
| `request`     | Base64url-encoded JSON with the method-specific payment details.              |

The spec also defines optional `opaque` and `digest` parameters. Neither is currently emitted, so there is nothing extra to echo back and no integrity digest to verify.

The decoded `request` object:

```json
{
  "amount": "10000",
  "currency": "0x20c000000000000000000000b9537d11c60e8b50",
  "methodDetails": {
    "chainId": 4217
  },
  "recipient": "0x..."
}
```

| Field                   | Meaning                                                             |
| ----------------------- | ------------------------------------------------------------------- |
| `amount`                | Price in the token's base units. `10000` is \$0.01 at six decimals. |
| `currency`              | Contract address of the token to pay in, not a fiat currency code.  |
| `methodDetails.chainId` | Chain to settle on. `4217` is Tempo.                                |
| `recipient`             | The You.com receiving address.                                      |

The `recipient` value is redacted above, and it changes between challenges. Take it from the Challenge you were issued rather than from these docs or from a previous response. A client that caches a recipient will pay the wrong address.

Do not modify a Challenge and resubmit it. Pass the parameters back exactly as they arrived, including the `request` string, which must be echoed byte for byte rather than decoded and re-encoded.

---

## Submitting a Credential

```http
Authorization: Payment eyJjaGFsbGVuZ2UiOnsiaWQiOiJJcHRVMkF2a0x3SkRHdVZZbXU2VUFEaE5pUHZjUGIxTG41Zm1DNTRsc3dVIiwi...
```

Decoded, a Credential looks like this:

```json
{
  "challenge": {
    "id": "IptU2AvkLwJDGuVYmu6UADhNiPvcPb1Ln5fmC54lswU",
    "realm": "api.you.com",
    "method": "tempo",
    "intent": "charge",
    "expires": "2026-08-03T14:24:11Z",
    "request": "eyJhbW91bnQiOiIxMDAwMCIsImN1cnJlbmN5IjoiMHgyMGMwMDAwMDAwMDAwMDAwMDAwMDAwMDBiOTUzN2QxMWM2MGU4YjUwIiwibWV0aG9kRGV0YWlscyI6eyJjaGFpbklkIjo0MjE3fSwicmVjaXBpZW50IjoiMHguLi4ifQ"
  },
  "payload": {
    "type": "transaction",
    "signature": "0x1b2c3d4e5f6a7b8c9d0e..."
  },
  "source": "did:pkh:eip155:4217:0x1234567890abcdef1234567890abcdef12345678"
}
```

| Field       | Contents                                                          |
| ----------- | ----------------------------------------------------------------- |
| `challenge` | The Challenge being answered, with wire values preserved exactly. |
| `payload`   | Method-specific proof of payment.                                 |
| `source`    | Identity of the payer, as an address, DID, or account ID.         |

Each Credential is valid for exactly one request. Replays are rejected.

---

## Making a Paid Request

The `mppx` SDK polyfills `fetch`, so your existing code works unchanged. The 402, the payment, and the retry all happen underneath.

#### TypeScript

```bash
npm install mppx
```

```typescript
import { Mppx, tempo } from "mppx/client";
import { privateKeyToAccount } from "viem/accounts";

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);

Mppx.create({
  methods: [tempo({ account })],
});

const params = new URLSearchParams({
  query: "best practices for scaling microservices in production",
  count: "10",
});

// Mppx.create() polyfills global fetch, so this is a normal fetch call.
const response = await fetch(`https://api.you.com/v1/search?${params}`);

const data = await response.json();
console.log(data.results.web.map((r) => r.url));
```

#### mppx CLI

```bash
# One-time wallet setup
npx mppx account create

# Smoke-test the paid endpoint
npx mppx "https://api.you.com/v1/search?query=nvidia+earnings&count=10"
```

Official SDKs are also available for Python (`pympp`), Rust (`mpp-rs`), Go (`mpp-go`), and Ruby (`mpp-rb`). See the [MPP SDK documentation](https://mpp.dev/sdk).

### Agent Wallets

If you are wiring up an autonomous agent rather than an application, several managed wallets handle funding and spend controls for you, including [Tempo Wallet](https://wallet.tempo.xyz) and the [Privy Agent CLI](https://docs.privy.io/recipes/agent-integrations/agent-cli). Both let a human set spend limits and revoke access without the agent holding a private key directly.

---

## Receipts

On success we return a base64url-encoded Receipt in the `Payment-Receipt` header:

```json
{
  "challengeId": "IptU2AvkLwJDGuVYmu6UADhNiPvcPb1Ln5fmC54lswU",
  "method": "tempo",
  "reference": "0xtx789abc...",
  "settlement": {
    "amount": "10000",
    "currency": "0x20c000000000000000000000b9537d11c60e8b50"
  },
  "status": "success",
  "timestamp": "2026-08-03T14:24:11Z"
}
```

The `reference` field is the Tempo transaction hash. Log it if you need an audit trail. There is no invoice and no credit-history line item, because there is no account.

The field names above follow the MPP specification. Reading a Receipt requires settling a real payment, so parse defensively rather than asserting on this exact shape, and [tell us](https://you.com/support) if a live Receipt disagrees.

---

## Limits and Safeguards

**Expiry.** Challenges expire at `expires`, 10 minutes after issue. Request a fresh Challenge rather than reusing an expired one.

**Single use.** One Credential satisfies one request.

**Rate limits.** Challenge issuance is capped at 10 per minute per caller. An 11th unpaid request inside the same minute returns `429` with a `Retry-After` header and a `https://paymentauth.org/problems/rate-limited` problem type instead of a fresh Challenge. Hold the Challenge you were issued rather than minting one per attempt. Keyless requests cannot inherit an organization's custom QPS limit.

**Finality.** Stablecoin settlement is final, and there is no testnet to rehearse on.

---

## Data Retention

[Zero Data Retention](/docs/administration/zero-data-retention) is not available on MPP requests.

ZDR is an account-level configuration. It is added to an enterprise agreement and enforced against a specific organization's API keys. An MPP request presents no API key and no account, so there is no agreement to attach ZDR to and no identity to enforce it against. Keyless requests fall outside ZDR and are handled under You.com's general terms.

Two consequences to plan around:

* **There is no account-scoped deletion path.** Deletion and data subject requests are handled per organization. An MPP request has no organization, so there is no established route to scope such a request to your traffic.
* **Routing end-user queries through this path is a decision you own.** If you have a retention, residency, or compliance commitment to your own users, send those queries with an API key on an enterprise agreement that has ZDR enabled.

The payer identity in a Credential's `source` field is a wallet address, DID, or account ID on the payment rail. It is not a You.com account and does not carry any data handling configuration with it.

If ZDR is a requirement, use [API key authentication](/docs/administration/api-keys) and ask your account team about adding ZDR to your agreement.

---

## Errors

A 402 response body is `application/problem+json`:

```json
{
  "type": "https://paymentauth.org/problems/payment-required",
  "title": "Payment Required",
  "status": 402,
  "detail": "Payment is required.",
  "challengeId": "N4YKVcT-d0n6XgCTNZQV9sruH-JdA1LhJh-2fyU1Z_A"
}
```

| Status | Condition                                          | What to do                                                                                                                                               |
| ------ | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `402`  | No `Authorization` header                          | Expected on the first call. Read the Challenge and retry.                                                                                                |
| `402`  | Credential present but not valid                   | A malformed, expired, or unverifiable Credential re-issues a fresh Challenge rather than returning a distinct status. Pay against the new `challengeId`. |
| `401`  | Right endpoint, wrong verb                         | `/v1/search` offers payment on GET, Finance Research on POST. Switch the method, or use `/v1/agents/search` which accepts both.                          |
| `401`  | Invalid `X-API-Key` sent                           | The key path and the payment path are separate. Send a Credential and no key, or a valid key and no Credential.                                          |
| `429`  | More than 10 unpaid Challenge requests in a minute | Honor `Retry-After`. Reuse the Challenge you already hold instead of minting a new one per attempt.                                                      |
| `5xx`  | Settlement or upstream failure                     | Retry with backoff. See troubleshooting below.                                                                                                           |

---

## Troubleshooting

**I get a 402 loop.** Your client is most likely re-encoding the `request` string instead of echoing it. Pass the Challenge parameters back exactly as they arrived.

**I am getting 401 instead of 402.** Check the verb before anything else. `/v1/search` offers payment terms on GET only and Finance Research on POST only. The inverse of either returns `401` with no hint that the method is the problem. If you need POST for Web Search, use `/v1/agents/search`, which accepts payment on both GET and POST. The Contents and Research APIs return `401` on every method, since they do not accept machine payments at all.

**My wallet has USDC but verification fails.** Confirm the balance is on Tempo, chain ID `4217`, in the token named by `currency`. USDC on Base or Solana cannot satisfy a Tempo Challenge. If your funds are on Base or Solana, use [x402](/docs/administration/machine-payments/x402) instead.

**Payment settled but the request returned a 5xx.** A Challenge is valid for exactly one request, so a retry needs a fresh Challenge and settles a second payment. Keep the Receipt from the failed call and [contact support](https://you.com/support) with it rather than absorbing the double charge.

**Can I use MPP and an API key on the same endpoint?** Yes, on the same route, but not in the same request. Requests are routed by what they present.

**Should I use MPP or x402?** Pick by where your funds are. x402 covers Base and Solana, MPP covers Tempo, and both reach the same two endpoints. Price only separates them on Web Search, where x402 charges \$0.005 against MPP's \$0.01. Finance Research costs the same on either. So if you are starting from scratch and most of your traffic is search, x402 is cheaper today. Reach for MPP when your agent is on Tempo, or when you want the integration that will pick up card and fiat rails as we enable them. Both are supported and neither is being deprecated.

---

## Related

#### [x402](/docs/administration/machine-payments/x402)

Pay per request in USDC on Base or Solana. Cheaper on Web Search.

#### [Billing & Credits](/docs/administration/billing)

The standard credit model, for key-authenticated access.

---

## Questions & Support

For MPP questions, reach us in [Discord](https://you.com/discord) or contact [api@you.com](mailto:api@you.com).