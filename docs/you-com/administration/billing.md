> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Billing

## Credits Overview

You.com uses a pay-as-you-go credit system for API access. You only pay for what you use.

All new accounts receive **\$100 in free API credits** to explore and test the APIs. No credit card required.

Credits are one of two ways to pay. If you are building an agent rather than provisioning access for a person, [machine payments](/docs/administration/machine-payments) let it call the Web Search API with no account and no key, settling each request on-chain instead of drawing down a balance.

---

## API Pricing

### Web Search API

| Pricing    | Details                                      |
| ---------- | -------------------------------------------- |
| **\$5.00** | per 1,000 calls (up to 100 results per call) |

**What's included:**

* Web and news results in a single unified request
* Up to 100 results per call
* News endpoint at no extra cost
* LLM-ready snippets or highlights with rich metadata
* Country and language targeting filters

**Full page extraction add-on:**

| Pricing    | Details                      |
| ---------- | ---------------------------- |
| **\$1.00** | per 1,000 pages fetched live |

Full page content (HTML or Markdown) is billed separately. It is invoked via the `extraction` parameter on the Web Search API, with `extraction_mode` set to `full_page`.

Only pages crawled live are billed. The `extraction_source` field on the `extraction` object decides how many of those there are:

| Source            | What you pay                                                                    |
| ----------------- | ------------------------------------------------------------------------------- |
| `blend` (default) | \$1.00 per 1,000 pages crawled live. Pages served from cache are free           |
| `cache`           | Nothing beyond the base call price. Cached content carries no extraction charge |
| `fetch`           | \$1.00 per 1,000 pages. Every result is crawled live                            |

**Example:** A single call with `count=10` and `extraction_mode: "full_page"` returns 10 web results and 10 news results—20 pages total. This call leaves `extraction_source` unset, so it runs `blend`. Say 2 of the 20 pages are already cached and the other 18 are crawled live.

| Line item                          | Calculation               | Cost        |
| ---------------------------------- | ------------------------- | ----------- |
| Web Search API call                | 1 call × \$5.00 / 1,000   | \$0.005     |
| Full page extraction, crawled live | 18 pages × \$1.00 / 1,000 | \$0.018     |
| Full page extraction, from cache   | 2 pages × \$0.00          | \$0.000     |
| **Total**                          |                           | **\$0.023** |

Cache coverage varies by query and by how recently the pages were crawled, so treat the split above as one outcome rather than a rate to budget against. The ceiling for this call is \$0.025, when all 20 pages are crawled live. The floor is \$0.005, which is what `extraction_source: "cache"` costs on any call, with no extraction charge at all.

### Contents API

| Pricing    | Details         |
| ---------- | --------------- |
| **\$1.00** | per 1,000 pages |

**What's included:**

* Batch multiple URLs per request
* Clean Markdown or raw HTML output
* Python SDK, MCP Server, and REST API access
* No browser automation or HTML parsing required

### Answer API

| Pricing    | Details         |
| ---------- | --------------- |
| **\$5.00** | per 1,000 calls |

**What's included:**

* Synthesized, citation-backed answers from real-time web results
* Inline numbered citations linked to source URLs with verbatim excerpts
* Web results used during synthesis, whether cited or not
* Freshness, locale, domain, and safesearch controls

### Research API

Research effort tiers control the depth of analysis. Higher tiers allocate more compute for deeper reasoning and more sources.

| Tier         | Pricing        | Latency                                 | Use case                                                       |
| ------------ | -------------- | --------------------------------------- | -------------------------------------------------------------- |
| `lite`       | **\$12/1k**    | \< 10s                                  | Quick factual lookups, simple searches                         |
| `standard`   | **\$50/1k**    | \~10–30s                                | Balanced depth for most production use (default)               |
| `deep`       | **\$100/1k**   | \< 120s                                 | Complex multi-source research and synthesis                    |
| `exhaustive` | **\$450/1k**   | \< 300s                                 | Comprehensive analysis across dozens of sources                |
| `frontier`   | **\$1,200/1k** | Background only. 30s–12000s (p50: 300s) | Long-running deep research tasks. Requires `background: true`. |

**What's included:**

* Cited, source-backed answers with inline references
* Multi-step search and synthesis pipeline
* Higher tiers = more sources, deeper reasoning, higher accuracy

### Finance Research API

Finance Research effort tiers control the depth of financial analysis. Higher tiers allocate more compute for deeper reasoning and more sources. The API searches a purpose-built financial index covering company fundamentals, equity and commodity prices, SEC filings, and financial news.

| Tier         | Pricing      | Latency | Use case                                                                                                                |
| ------------ | ------------ | ------- | ----------------------------------------------------------------------------------------------------------------------- |
| `deep`       | **\$110/1k** | \< 120s | Multi-source analysis—earnings summaries, competitive benchmarking, regulatory research, multi-quarter trends (default) |
| `exhaustive` | **\$500/1k** | \< 300s | Comprehensive research—deep due diligence, full 10-K analysis, cross-market research                                    |

**What's included:**

* Cited, source-backed answers from a finance-optimized index
* Multi-step search and synthesis pipeline
* Higher tiers = more sources, deeper reasoning, higher accuracy
* Same request-response pattern and response shape as the Research API

*See [you.com/pricing](https://you.com/pricing) for more details.*

---

## Managing Your Account

### Viewing your usage and balance

To view your current credit balance and usage:

1. Sign in to [you.com/platform](https://you.com/platform)
2. Navigate to the billing section of your dashboard
3. View your remaining credits and usage history

You can also retrieve your balance programmatically using the [Account Balance API](/docs/api-reference/billing/get-account-balance).

```bash
curl -sS -X GET "https://api.you.com/v1/billing/account_balance" \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Accept: application/json"
```

The response contains a `balance` field expressed in cents. Divide by 100 to convert to USD (e.g., `744300.0` = \$7,443.00):

```json
{
  "data": {
    "type": "account",
    "id": "<hashed-account-id>",
    "attributes": {
      "balance": 744300.0
    }
  }
}
```

The billing entity depends on your account type:

* **Organization members**—the balance reflects the shared credit pool for your entire organization.
* **Individual users**—the balance reflects credits on your personal account.

### Adding credits

To add credits to your account:

1. Go to [you.com/platform](https://you.com/platform)
2. Navigate to the billing section
3. Select the amount you'd like to add and confirm payment

### Payment methods

You can add and manage payment methods from the billing section of your dashboard. You.com accepts major credit and debit cards.

---

## Auto Top-Up

Auto Top-Up automatically purchases credits when your balance falls below a configured threshold. This is the recommended way to prevent service interruptions on production workloads.

### Overview

| Property     | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| Scope        | Organization (tenant-level)                                           |
| Permissions  | Admin or Owner only to configure; all members can view                |
| Payment      | Default payment method on file                                        |
| Trigger      | Balance falls below the configured threshold                          |
| Notification | Email to organization admins on enable, disable, success, and failure |

### Requirements

Auto Top-Up requires:

1. **A payment method on file.** Managed under **Billing → Payment methods**.
2. **A designated default payment method.** If multiple cards are on file, one must be marked as the default. With a single card, it is treated as default automatically.
3. **An [Admin or Owner role](/docs/administration/team-management)** on the organization.

The **Enable Auto Top-Up** control is disabled in the UI until a default payment method is set.

### Configuring Auto Top-Up

**Fields**

| Field              | Description                                                     | Constraints                               |
| ------------------ | --------------------------------------------------------------- | ----------------------------------------- |
| **Enabled**        | Toggles Auto Top-Up on or off.                                  | —                                         |
| **Threshold**      | The credit balance at or below which a top-up is triggered.     | Positive, whole-dollar amount.            |
| **Top-up amount**  | The amount to charge when a top-up is triggered.                | Must be **≥ threshold**.                  |
| **Payment method** | The card to charge. Read-only; managed via **Payment methods**. | Must be the org's default payment method. |

**Enable flow**

1. Navigate to **Billing**.
2. In the **Credit balance** card, select **Enable Auto Top-Up**.
3. Enter the threshold and top-up amount.
4. Confirm the default payment method shown.
5. Review and confirm. An explicit confirmation step is required before the setting is saved, because enabling authorizes future off-session charges.

**Immediate execution on enable.** If your current balance is already below the threshold when you enable Auto Top-Up—or if you later raise the threshold above your current balance—a top-up fires immediately. The system charges an amount sufficient to bring the balance up to the threshold (or the top-up amount, whichever is greater), so you are never left below your configured minimum.

**Example:** Balance `$10`, threshold `$100`, top-up amount `$50` → **charged on enable: `$90`** (brings balance to exactly `$100`). Subsequent automatic top-ups, once the balance is above the threshold, charge the configured top-up amount as normal.

**Validation**

The following validation applies in both the UI and the backend:

* `top_up_amount >= threshold`—if violated, the form shows an error and the API returns a 4xx.
* Both values must be positive, whole-dollar amounts.
* Configuration is rejected if no default payment method is set.

### Runtime behavior

**Detection.** Balance monitoring is real-time. When credit usage causes the balance to cross the threshold, a top-up is scheduled immediately—there is no polling delay.

**Payment execution.** The charge is attempted off-session against the organization's default payment method. Successful charges produce:

* A credit grant in your account (credits available immediately)
* An email receipt to all organization admins
* An entry in your billing history

**Failure handling.** If a payment fails, the top-up does not complete, no credits are granted, and all organization admins receive a failure notification by email. The system re-attempts the next time the balance crosses the threshold—typically after the payment method is corrected.

Failure reasons reported in the notification:

* `card_expired`
* `insufficient_funds`
* `card_declined`
* `authentication_required`

### Notifications

Emails are sent to all organization admins on the following events:

| Event                     | Trigger                                     |
| ------------------------- | ------------------------------------------- |
| **Auto Top-Up enabled**   | Configuration is turned on                  |
| **Auto Top-Up disabled**  | Configuration is turned off                 |
| **Auto Top-Up succeeded** | A charge completed and credits were granted |
| **Auto Top-Up failed**    | A charge was attempted and failed           |

Success notifications include the amount charged, the new balance, and a link to the receipt.

### Permissions

| Role   | View setting | Enable / edit / disable |
| ------ | ------------ | ----------------------- |
| Owner  | ✅            | ✅                       |
| Admin  | ✅            | ✅                       |
| Member | ✅            | ❌                       |

Attempting to modify the setting without sufficient permissions returns `403 Forbidden`.

### Disabling Auto Top-Up

From **Billing → Credit balance**, toggle **Auto Top-Up** off and confirm. No further automatic charges will occur. Your existing credit balance is unaffected.

### Limitations in the current release

* **Organization-level only.** Individual users cannot configure their own Auto Top-Up. Consumer billing is not supported.
* **Fixed top-up amount.** The system charges the configured amount (or the amount needed to reach the threshold on the first fire; see above). Usage-based sizing is not available.
* **No spending caps.** Monthly caps, frequency limits, and per-charge maximums are planned but not yet exposed. Today, you control spend via the threshold and top-up amount.

### Troubleshooting

**I don't see the "Enable Auto Top-Up" button.**
You likely don't have a default payment method set. Go to **Billing → Payment methods**, confirm a card is on file, and set one as the default. The enable button will appear once a default is in place.

**My Auto Top-Up failed—what happened?**
The most common reasons are an expired card, insufficient funds, or a declined charge from your bank. You'll receive an email when a top-up fails. To resolve:

1. Go to **Billing → Payment methods** and verify your default card is current.
2. Add a new payment method if needed and set it as the default.
3. Contact your bank if the card is valid but the charge was declined.

Auto Top-Up will try again the next time your balance crosses the threshold once your payment method is fixed.

**Can I get a refund for an auto top-up I didn't want?**
Credits added via Auto Top-Up follow the same policy as manually purchased credits. Contact [api@you.com](mailto:api@you.com) with your receipt and we'll help.

**Can I set a monthly spending cap?**
Not in the current release. Today, you control spend by setting your top-up amount and threshold. Spending caps are on the roadmap.

---

## Enterprise & Volume Pricing

### Volume discounts

Enjoy lower rates as your usage scales, without lengthy negotiations. Contact sales for custom rates based on your volume.

### Annual savings

Commit to annual usage for deeper discounts and predictable costs—ideal for production deployments.

### Enterprise features

**Zero Data Retention**—All queries and data can be automatically purged, giving you complete control over data storage and retention.

**SOC 2 Certified**—Our infrastructure is independently audited to ensure data security, privacy, and availability.

**DPA-Ready**—Data Processing Agreements supported for enterprise compliance requirements.

**Custom QPS Limits**—Enterprise-grade concurrency with performance optimization for high-volume usage.

---

## Questions & Support

For billing questions, custom pricing, or enterprise features, contact [api@you.com](mailto:api@you.com).