> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Zero Data Retention (ZDR)

## Overview

Zero Data Retention (ZDR) is an account-level data handling configuration for organizations operating under strict privacy, compliance, or security mandates. With ZDR enabled, You.com processes your request and response content in transit to serve each request and does not persist it beyond the short-term window necessary to fulfill the request.

ZDR is available for the **Web Search API** and the **Answer API** on enterprise agreements. It is enabled by You.com on request—there is no self-serve toggle.

To add ZDR to your agreement, contact your You.com account team. If you don't have an account team yet, email [api@you.com](mailto:api@you.com).

## What ZDR Does

When ZDR is enabled on your account:

* **Request and response content is not retained.** Queries and results are processed to serve your requests and are not stored or logged beyond the short-term window necessary to fulfill each request.
* **Your queries are not used to train models.**
* **Your data is not sold in downstream services**, and your queries do not go to Google or Bing.
* **ZDR applies account-wide and cannot be bypassed.** Once enabled, it covers all Web Search API and Answer API traffic on your account's API keys. It is enforced at the infrastructure level and cannot be switched off or subverted on a per-request basis, by you or by You.com tooling.

Two safeguards back this up:

* **Engineering standards.** Our code does not write search content to logs or analytics beyond what is required to operate the service.
* **Automated checks.** Every proposed code change is scanned automatically. A change that would cause search content to be logged is blocked before it ships.

## What ZDR Does Not Change

**Your integration.** Same endpoint, same request and response formats, same API keys. ZDR is applied server-side to your account and requires no code changes.

## Availability

ZDR is currently supported for the **Web Search API** (`/v1/search`) and the **Answer API** (`/v1/answer`). Support for additional APIs is on the roadmap. If ZDR for the Contents API or Research API is a requirement for you, let your account team know.

## How to Enable ZDR

### Contact Your Account Team

Reach out to your You.com account team. Without an account team, email [api@you.com](mailto:api@you.com).

### Add ZDR to Your Agreement

Your account team walks you through adding ZDR to your agreement.

### Confirm Enablement

Once applied, ZDR covers all Web Search API and Answer API traffic on your account automatically. Your account team confirms when it is active.

## FAQ

**Is ZDR enabled by default?**

No. ZDR is an optional configuration added to your agreement on request.

**Does ZDR require integration changes?**

No. Requests, responses, and authentication are unchanged.

**Which APIs support ZDR?**

The Web Search API and the Answer API. Additional APIs are on the roadmap. Tell your account team if you need ZDR for another product.

**How do I confirm ZDR is active on my account?**

Your account team confirms enablement in writing.

## Related

#### [Account](/docs/administration/account)

Manage your organization, team members, and account settings.

#### [API Keys](/docs/administration/api-keys)

Create, rotate, and secure the keys ZDR applies to.