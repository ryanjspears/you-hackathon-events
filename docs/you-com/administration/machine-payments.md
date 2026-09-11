> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Machine Payments

The Web Search and Finance Research APIs accept machine payments. A client can call either one and settle payment for that call inside the same HTTP exchange, with no signup, no API key, and no prepaid credit balance.

The index, the latency, and the response shape are identical to key-authenticated requests. Only the way you pay changes.

Machine payments are built for programmatic consumption. If a human is provisioning access once and using it repeatedly, an [API key](/docs/administration/api-keys) with [credits](/docs/administration/billing) costs less to operate and gives you usage analytics, team roles, and Zero Data Retention. ZDR is [not available](/docs/administration/machine-payments/x402#data-retention) on keyless requests.

---

## Supported Protocols

| Protocol                                           | Maintainer                                                                | Settles in             | Web Search per call |
| -------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------- | ------------------- |
| [x402](/docs/administration/machine-payments/x402) | x402 Foundation, founded by Coinbase and Cloudflare                       | USDC on Base or Solana | **\$0.005**         |
| [MPP](/docs/administration/machine-payments/mpp)   | Tempo and Stripe, specified at [paymentauth.org](https://paymentauth.org) | USDC on Tempo          | **\$0.01**          |

Both protocols use HTTP `402 Payment Required`, both complete in two round trips, and both are advertised on the same endpoint. A single unpaid request returns terms for both, so your client picks whichever it can satisfy.

---

## Choosing a Protocol

Today the practical question is where your agent already holds funds, because both protocols settle in USDC.

**Use x402 if** your wallet is on Base or Solana. It costs half as much on Web Search, the same on Finance Research, and it is the shortest path to a first paid request: one wallet, one stablecoin, one signature.

**Use MPP if** your wallet is on Tempo, or if you want the client integration that will pick up additional payment methods as we enable them. MPP is payment-method neutral by design, so a card or fiat rail can be added later without changing your code.

Cards and fiat are not currently enabled on either protocol. MPP supports them at the protocol level, but the only method we advertise today is `tempo`. If you need to pay by card, use an [API key](/docs/administration/api-keys) with [credits](/docs/administration/billing).

If you already have a working x402 client, there is no reason to migrate. Both remain supported.

---

## Pricing

| Endpoint                       | x402        | MPP        | Per 1,000 calls (x402) |
| ------------------------------ | ----------- | ---------- | ---------------------- |
| Web Search                     | **\$0.005** | **\$0.01** | \$5.00                 |
| Finance Research, `deep`       | **\$0.11**  | **\$0.11** | \$110.00               |
| Finance Research, `exhaustive` | **\$0.50**  | **\$0.50** | \$500.00               |

Both protocols match the standard [credit prices](/docs/administration/billing), so machine payments are not a surcharge.

The two protocols differ on Web Search only, and the reason is the rail. MPP settles through Stripe, where one cent is the smallest chargeable amount, so it rounds the underlying price up to the next whole cent. A half-cent Web Search call becomes one cent. Finance Research already lands on a whole cent at both tiers, so there is nothing to round and the prices match.

Adding `livecrawl` raises the Web Search quote by \$0.001 per result on both protocols, and the same rounding applies, which is why a \$0.015 x402 call is \$0.02 on MPP. Always read the amount out of the terms you were handed rather than assuming the base price.

The deprecated `livecrawl` parameter still works on the Web Search API. POST callers should prefer the `extraction` parameter—see the [Retrieve page content](/docs/guides/retrieve-page-content) guide.

If per-call cost is the thing you are optimizing, use x402 for Web Search. For Finance Research, pick on where your funds are.

Machine payments settle to the payment rail directly. They do not consume credits, they do not trigger [Auto Top-Up](/docs/administration/billing#auto-top-up), and they do not appear in your credit balance.

---

## Supported Endpoints

Machine payments cover the Web Search and Finance Research APIs. The method matters: `/v1/search` offers terms on GET only, and `/v1/finance_research` on POST only. The agent search endpoint, `/v1/agents/search`, is the exception—it accepts payment on both GET and POST.

| Endpoint                    | Machine payments | Notes                                                      |
| --------------------------- | ---------------- | ---------------------------------------------------------- |
| `GET /v1/search`            | Yes              | Web Search. Query-string parameters                        |
| `GET /v1/agents/search`     | Yes              | Web Search for agents. Query-string parameters             |
| `POST /v1/agents/search`    | Yes              | Same as GET, JSON body                                     |
| `POST /v1/finance_research` | Yes              | Finance Research. JSON body, `deep` or `exhaustive`        |
| `POST /v1/search`           | No               | Returns `401`. Use `GET /v1/search` or `/v1/agents/search` |
| `GET /v1/finance_research`  | No               | Returns `401`. Use the POST form                           |
| `POST /v1/contents`         | No               | API key required                                           |
| `POST /v1/research`         | No               | API key required                                           |

x402 gating is endpoint-scoped, not method-scoped. When x402 is enabled for an endpoint, it is available on every method that endpoint offers for machine payments. That is why `/v1/agents/search` accepts x402 on both verbs while `/v1/search` accepts it on GET only.

---

## What You Need

* **A funded wallet.** USDC on Base or Solana for x402, or USDC on Tempo for MPP.
* **A client that speaks the protocol.** Both protocols ship official SDKs that wrap `fetch` and handle the 402 retry for you, so you never implement the handshake by hand.
* **No You.com account.** That is the point. Nothing to provision, nothing to rotate.

---

## Free Access Without Payment

If you are evaluating rather than running production traffic, the keyless MCP endpoint is free and needs no wallet:

```
https://api.you.com/mcp?profile=free
```

It exposes `you-search` at 100 queries per day with no credentials. See the [MCP Server for Web Search](/docs/capabilities/mcp-server-for-web-search) guide.

---

## Next Steps

#### [x402](/docs/administration/machine-payments/x402)

Pay per request in USDC on Base or Solana. Wallet, signature, retry.

#### [MPP](/docs/administration/machine-payments/mpp)

Pay per request in USDC on Tempo, through one method-neutral handshake.

---

## Questions & Support

For machine payments questions, reach us in [Discord](https://you.com/discord) or contact [api@you.com](mailto:api@you.com).