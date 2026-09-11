> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Contents API Overview

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

---

## What Is the Contents API?

The Contents API extracts clean HTML or Markdown content from a given URL. Pass it a list of URLs and get back the full page content for each, ready for LLM consumption—no parsing, no HTML noise, no browser automation required.

---

## How It's Different From Full Page Extraction

The Contents API and full page extraction in the Web Search API both extract full page content, but they serve different workflows:

|                    | Contents API                | Web Search API + full page extraction                    |
| ------------------ | --------------------------- | -------------------------------------------------------- |
| **Starting point** | You already know the URLs   | You have a query, not URLs                               |
| **Use case**       | Fetch known pages on demand | Enrich search results with full content                  |
| **URL source**     | You provide them            | You.com search discovers them                            |
| **Batch size**     | 10 URLs per request         | Up to 100 results per search                             |
| **Pricing**        | \$1.00 per 1000 pages       | \$5.00 per 1000 searches + \$1.00 per 1000 pages crawled |

Use the Contents API when you have a list of specific URLs you want to read. Use `extraction_mode: "full_page"` when you want full content returned alongside search results in one go.

---

## What You Get

Each URL in your request returns a structured object:

```json
[
  {
    "url": "https://competitor.com/pricing",
    "title": "Pricing — Competitor Inc.",
    "markdown": "# Pricing\n\n## Starter Plan\n$49/month...",
    "html": "<html>...</html>",
    "metadata": {
      "site_name": "Competitor Inc.",
      "favicon_url": "https://ydc-index.io/favicon?domain=competitor.com&size=128"
    }
  }
]
```

You control which formats are returned via the `formats` parameter—request `markdown`, `html`, and/or `metadata` in any combination.

---

## Key Features

### Any URL, on demand

Pass up to 10 URLs in a single request. The API crawls them all in parallel and returns the content. No need to manage a headless browser or deal with raw HTML yourself.

### LLM-ready Markdown

The `markdown` format strips navigation menus, ads, footers, and other boilerplate. You get actual content of the page—ready to drop into a prompt.

### Configurable timeout

Use `crawl_timeout` (1–60 seconds) to balance speed vs. completeness. For fast pages: 5–10 seconds. For heavy JavaScript-rendered pages: 20–30 seconds.

### Cache Freshness Control

By default, the Contents API may return cached page content to improve latency. Use `max_age` to control how fresh that cache must be. Pass a value in seconds and any cached content older than the threshold is ignored, forcing a fresh fetch of the page.

For example, `max_age=86400` ensures content is no older than 24 hours, while `max_age=0` always bypasses the cache and re-fetches the page. Leave `max_age` unset (the default) to accept cached content regardless of age.

### Metadata extraction

Request `metadata` alongside content to get the page's site name and favicon URL—useful for building UIs that display source attribution.

---

## Quickstart

```python
from youdotcom import You
from youdotcom.models import ContentsFormats

with You() as you:
    pages = you.contents(
        urls=["https://you.com/about"],
        formats=[ContentsFormats.MARKDOWN],
    )

    for page in pages:
        print(f"Title: {page.title}")
        print(f"Content preview: {page.markdown[:300]}\n")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ContentsFormats } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const pages = await you.contents({
  urls: ["https://you.com/about"],
  formats: [ContentsFormats.Markdown],
});

for (const page of pages) {
  console.log(`Title: ${page.title}`);
  console.log(`Preview: ${page.markdown?.slice(0, 300)}\n`);
}
```

```curl
curl -X POST https://ydc-index.io/v1/contents \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://you.com/about"],
    "formats": ["markdown"]
  }'
```

#### [Try in Postman](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-037d5564-c4b5-4e11-9cea-1e41a5eba4aa)

Fork the Contents API collection, add your API key to the `production` environment, and hit Send.

---

## Parameters

| Parameter       | Type             | Required | Description                                                                                                                                                                                      |
| --------------- | ---------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `urls`          | array of strings | Yes      | The URLs to fetch content from                                                                                                                                                                   |
| `formats`       | array of strings | No       | Content formats to return: `markdown`, `html`, `metadata` (default: `markdown`)                                                                                                                  |
| `crawl_timeout` | number           | No       | Per-URL timeout in seconds, between 1 and 60 (default: 10)                                                                                                                                       |
| `max_age`       | integer          | No       | Maximum allowed age of cached content in seconds. Must be 0 or greater. When set, cached content older than this threshold is ignored and the page is re-fetched. Default: `null` (no age limit) |

[View full API reference](/docs/api-reference/contents)

---

## Common Use Cases

### Competitive intelligence

Monitor competitor pricing, feature, or blog pages. Fetch the content on a schedule, feed it to an LLM, and surface meaningful changes—without manual checking.

```python
from youdotcom import You
from youdotcom.models import ContentsFormats

competitor_pages = [
    "https://competitor-a.com/pricing",
    "https://competitor-b.com/pricing",
    "https://competitor-c.com/features",
]

with You() as you:
    pages = you.contents(
        urls=competitor_pages,
        formats=[ContentsFormats.MARKDOWN],
        crawl_timeout=15,
    )

    for page in pages:
        print(f"\n--- {page.title} ---")
        # Feed page.markdown into your LLM for summarization or diff
        print(page.markdown[:500])
```

### Knowledge base ingestion

You have a list of authoritative sources—documentation pages, whitepapers, internal wikis. Fetch them all, convert to clean Markdown, and index into your vector store.

```python
from youdotcom import You
from youdotcom.models import ContentsFormats

# Known authoritative sources to index
source_urls = [
    "https://docs.example.com/api-reference",
    "https://docs.example.com/authentication",
    "https://docs.example.com/rate-limits",
]

with You() as you:
    pages = you.contents(
        urls=source_urls,
        formats=[ContentsFormats.MARKDOWN, ContentsFormats.METADATA],
    )

    documents = []
    for page in pages:
        documents.append({
            "source": page.url,
            "title": page.title,
            "content": page.markdown,
        })
        # Index document into your vector store here
```

### Research assistant

Give users the ability to ask questions about specific URLs. Fetch the page content on the fly and feed it as context into your LLM—turning any URL into a searchable document.

```python
from youdotcom import You
from youdotcom.models import ContentsFormats

def fetch_url_context(url: str) -> str:
    with You() as you:
        pages = you.contents(urls=[url], formats=[ContentsFormats.MARKDOWN])
        return pages[0].markdown if pages else ""

# User asks: "Summarize this page for me"
url = "https://example.com/long-report"
context = fetch_url_context(url)

prompt = f"Summarize the following page content:\n\n{context}"
# Pass prompt to your LLM
```

---

## Best Practices

### Request only the formats you need

Each format adds processing time. If you only need Markdown for LLM consumption, don't request `html`. If you don't need site metadata for your UI, skip `metadata`.

### Batch your URLs

A single request with 10 URLs is faster than 10 separate requests. The API processes them in parallel.

### Set `crawl_timeout` based on the target site

For simple static pages, 5–10 seconds is usually enough. For JavaScript-heavy pages (SPAs, dashboards), increase to 20–30 seconds to give the renderer time to complete.

### Handle partial failures gracefully

If one URL in a batch fails to crawl (e.g., it's behind a login wall or returns a 404), the API returns `null` for its `markdown` and `html` fields. Always check before processing:

```python
for page in pages:
    if page.markdown:
        # Process content
        pass
    else:
        print(f"Failed to fetch: {page.url}")
```

---

## Pricing

**\$1.00 per 1,000 pages**

All new accounts receive \$100 in free credits to get started. See the [Billing page](/docs/administration/billing#contents-api) for complete pricing details.

**What's included:**

* Batch multiple URLs per request
* Clean Markdown or raw HTML output
* Python SDK, MCP Server, and REST API access
* No browser automation or HTML parsing required

For volume discounts, annual pricing, or enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).

---

## Next Steps

#### [API Reference](/docs/api-reference/contents)

Full parameter reference, request/response schemas, and error codes

#### [Web Search API Overview](/docs/guides/search)

Pair search results with full page extraction to get full content alongside real-time web data

#### [Quickstart](/docs/quickstart)

Get your API key and make your first call in under five minutes

#### [Python SDK](/docs/sdks/python-sdk)

Use the official SDK for cleaner integration