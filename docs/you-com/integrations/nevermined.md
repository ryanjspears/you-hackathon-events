> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Nevermined

You.com allows autonomous agent payments using [Nevermined](https://nevermined.ai) as one option for using [x402](https://nevermined.ai/glossary/x402/). It lets an autonomous agent purchase a You.com API key for \$5 with a delegated credit card, or top up an existing API key with no human provisioning a key by hand.

The steps below cover getting a Nevermined API key, funding a payment method, and settling a purchase against the plan. The result is a standard You.com API key, valid on every API.
Additional information can be found at [Nevermined Agentic Instructions](https://api.live.nevermined.app/api/v1/organizations/org-cf34dc7b-ec18-48f4-98fb-1697aafe0586/agentic-instructions.md).

Each purchase using a Nevermined x402 card-delegation will return a You.com API key or top up the existing token with credits.

The Production Nevermined Plan ID is `29778596298820876231214801015161463950677497795586711453924479772330133054735`.
[paygo: \$5.00 per request](https://api.live.nevermined.app/api/v1/protocol/plans/29778596298820876231214801015161463950677497795586711453924479772330133054735)
This plan ID is used to purchase API credits, which can be used to make API requests.

## Purchase a You.com API Key

\$5 is charged to the card used to create the x402 token for each purchase request: `POST https://api.you.com/payments/v1/nevermined/purchase-key` with the `payment-signature` header set to your x402 settlement token.

* A successful call returns a real You.com API key:
  ```json
  {
    "status": "ok",
    "apiKey": "ydc-sk-...",
    "toppedUp": false
  }
  ```
* A returning payer will top up the existing You.com API key:
  ```json
    {
      "status": "ok",
      "apiKey": null,
      "toppedUp": true
    }
  ```
* A replayed token never charges twice, but what it returns depends on the original purchase: replaying a first purchase mints a new key (the original's plaintext can't be recovered from cache), while replaying a top-up returns the same `apiKey: null` response again.
* 402 Payment Required if credentials are missing.

## How to Purchase Access as an Autonomous Agent

**Agentic Payments are supported by You.com using x402 standards, where the x402 token is used to purchase a You.com API key.**
A human is only needed the first time—to enroll a payment method and create a Nevermined API key. Everything after that is programmatic and reusable.

1. **Get a Nevermined API key (one-time, needs a human) in the Nevermined app.** You cannot mint the first key yourself. A human signs in once via the web app:
   * The card owner must register a card at [https://nevermined.app](https://nevermined.app).
   * Issue a Nevermined API key to be used by the agent.
     **Store the key and reuse it**—send it as `Authorization: Bearer <api-key>` on every call below.

2. **Create a delegation**: `POST https://api.live.nevermined.app/api/v1/delegation/create` with `{ provider, providerPaymentMethodId, spendingLimitCents, durationSecs, currency }`. A delegation authorizes you to spend within a fixed budget and time window—reuse it until it is spent or expires.

3. **Mint an x402 access token.** For a plain plan top-up there is no protected endpoint to call, so you build the `paymentRequired` object yourself from the plan ID.
   * `POST https://api.live.nevermined.app/api/v1/x402/permissions` with `{ "accepted": { "scheme": "nvm:card-delegation", "network": "stripe", "planId": "<plan>" }, "delegationConfig": { "delegationId": "<your delegation>" } }` → returns an `accessToken`.
   * Build the `paymentRequired` object—`resource.url` must be a non-empty URL identifying what you're buying (for a plan top-up, use the plan's URL): `{ "x402Version": 2, "resource": { "url": "<plan-url>" }, "accepts": [{ "scheme": "nvm:card-delegation", "network": "stripe", "planId": "<plan>", "extra": {} }], "extensions": {} }`.
   * **Do not call `POST /x402/settle` yourself for this flow.** On this paygo plan, settling directly against Nevermined charges the card and hands back a bare settlement receipt—no You.com API key. Send the same token to `/purchase-key` afterward and you've paid twice for one key. `/x402/settle` and `/x402/verify` exist for calling a generic Nevermined-metered resource yourself; the You.com purchase flow doesn't use them.

4. **Send the access token to You.com's purchase endpoint.** Skip settling it yourself—send the `accessToken` from step 3 straight to the `/purchase-key` endpoint described in "Purchase a You.com API Key" above, in the `payment-signature` header. That endpoint verifies and settles the token on your behalf and returns the key in one call.
   * Use the returned `apiKey` the same way as any account-issued key: pass it in the `X-API-Key` header on Web Search, Contents, Answer, Research, Finance Research requests, and more. See [Authentication](/docs/using-the-api/authentication). Because it's a standard API key, it works anywhere an account-issued key does.

## What Does a You.com API Key Allow Agents to Do?

Pricing for APIs is detailed on the [Billing page](/docs/administration/billing).
The paygo plan above redeems for a standard You.com API key, which works on any You.com API including:

Refer to API documentation on how to exercise these endpoints.

* [Web Search API](/docs/api-reference/search/v1-search): real-time web and news results for grounding LLM responses.
* [Contents API](/docs/api-reference/contents): fetches clean HTML or Markdown for a target webpage.
* [Answer API](/docs/api-reference/answer/v1-answer): single-call cited answer to a query.
* [Research API](/docs/api-reference/research/v1-research): multi-step web research with a synthesized, cited answer.
* [Finance Research API](/docs/api-reference/finance-research/v1-finance_research): the Research API's multi-step approach over a financial-data index.

Every request goes to `https://api.you.com`, with the key in the same `X-API-Key` header regardless of which API you call:

```bash
curl "https://api.you.com/v1/search?query=nvidia+earnings" \
  -H "X-API-Key: $YDC_API_KEY"
```

## What to Do When a Key Is Exhausted?

* HTTP 402, indicating more funds are needed.
* Mint a new Nevermined x402 token using the same Plan ID, and POST to the /purchase-key endpoint to add another \$5 of credits to your You.com API key.

## Learn More

* [Nevermined SDK and API docs](https://nevermined.ai/docs/llms.txt)
* [x402 card delegation](https://nevermined.ai/docs/specs/x402-card-delegation)
* [You.com integration on Nevermined.com](https://nevermined.ai/docs/integrations/youdotcom)