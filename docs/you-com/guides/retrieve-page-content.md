> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Retrieve page content

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

## Overview

By default, search results include snippets—100–200 words of extracted text per result. Pass the `extraction` parameter to ask for richer content: full-page Markdown and HTML, or query-relevant highlights.

This unlocks:

* Deep RAG with full document context
* Knowledge base construction from live web data
* Comprehensive content synthesis across sources
* Full article bodies for news results

Two modes are available. Pick the one that matches the latency and token budget of your pipeline.

| Mode                            |                   Token cost | Returns                                                   | Best for                                                           |
| ------------------------------- | ---------------------------: | --------------------------------------------------------- | ------------------------------------------------------------------ |
| `extraction_mode: "highlights"` |                          Low | `contents.highlights` (a list of query-relevant excerpts) | Large `count`, RAG with citation chunks, latency-sensitive callers |
| `extraction_mode: "full_page"`  | High (whole page per result) | `contents.markdown` and/or `contents.html`                | Knowledge base ingestion, content synthesis, downstream indexing   |

If you want query-ranked excerpts rather than whole pages, use `extraction_mode: "highlights"`. The two modes are mutually exclusive—pick one per request.

## How It Works

Add the `extraction` object to a `POST /v1/search` request. The API fetches each result in real time and attaches a `contents` object to it. The `crawl_timeout` parameter is a sibling of `extraction` at the top level of the request body.

| Parameter                                 | Type    | Options                   | Description                                                                                        |
| ----------------------------------------- | ------- | ------------------------- | -------------------------------------------------------------------------------------------------- |
| `extraction.extraction_mode`              | string  | `full_page`, `highlights` | Required. Sets which mode the response populates                                                   |
| `extraction.highlights`                   | `{}`    | —                         | Optional container for `extraction_mode == "highlights"`. Reserved for future sub-fields           |
| `extraction.extraction_source`            | string  | `blend`, `cache`, `fetch` | Optional. Defaults to `blend`. Sets where `full_page` content comes from. Ignored for `highlights` |
| `extraction.full_page.extraction_formats` | array   | `markdown`, `html`        | Optional. Defaults to `["markdown"]`. Pass both to receive `contents.markdown` and `contents.html` |
| `crawl_timeout`                           | integer | `1`–`60` (default `10`)   | Top-level sibling. Max seconds to wait per page                                                    |

When `extraction_mode: "highlights"`, the server rejects `crawl_timeout` (it only applies to `full_page`). The Python SDK strips it automatically with a warning before the request goes out, so you can ignore the constraint unless you call the API directly.

Full-page extraction crawls every web and news result in the response. There is no per-section switch. Control the volume with `count`. With the default `count=10`, a call returns up to 10 web + 10 news pages.

`markdown` is recommended for LLM use cases—it strips navigation, ads, and boilerplate HTML, leaving only the core content.

`highlights` and `full_page` are two ways to attach content to search results. Use `highlights` when tokens are tight. Use `full_page` when you need whole documents.

## Get Highlights

Set `extraction_mode` to `highlights`. Each result gains a `contents.highlights` array of query-relevant excerpts. Snippets are omitted in this mode—the search returns the ranked highlights instead.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionMode

with You() as you:
  res = you.search(
    query="transformer architecture explained",
    count=5,
    extraction=Extraction(extraction_mode=ExtractionMode.HIGHLIGHTS),
  )

  if res.results and res.results.web:
    for result in res.results.web:
      highlights = result.contents.highlights if result.contents else None
      print(f"{result.title}")
      print(f"  URL: {result.url}")
      if highlights:
        print(f"  Highlights: {len(highlights)} excerpts")
        for h in highlights[:3]:
          print(f"    - {h[:140]}…")
      else:
        print("  (No highlights returned)\n")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionMode } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

async function run() {
  const result = await you.search({
    query: "transformer architecture explained",
    count: 5,
    extraction: { extraction_mode: ExtractionMode.Highlights },
  });

  result.results?.web?.forEach((r) => {
    console.log(r.title);
    console.log(`  URL: ${r.url}`);
    const highlights = r.contents?.highlights ?? [];
    console.log(`  Highlights: ${highlights.length} excerpts`);
    highlights.slice(0, 3).forEach((h) => console.log(`    - ${h.slice(0, 140)}…`));
  });
}

run();
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformer architecture explained",
    "count": 5,
    "extraction": {
      "extraction_mode": "highlights"
    }
  }'
```

## Get Full Page Content

Set `extraction_mode` to `full_page`. Each successfully crawled result gains a `contents.markdown` (or `contents.html`) field.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode

with You() as you:
  res = you.search(
    query="transformer architecture explained",
    count=5,
    extraction=Extraction(
      extraction_mode=ExtractionMode.FULL_PAGE,
      full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
  )

  if res.results and res.results.web:
    for result in res.results.web:
      print(f"{result.title}")
      print(f"  URL: {result.url}")
      if result.contents and result.contents.markdown:
        print(f"  Content ({len(result.contents.markdown)} chars)")
        print(f"  Preview: {result.contents.markdown[:200]}…\n")
      else:
        print("  (No content retrieved)\n")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

async function run() {
  const result = await you.search({
    query: "transformer architecture explained",
    count: 5,
    extraction: {
      extraction_mode: ExtractionMode.FullPage,
      full_page: { extraction_formats: [ExtractionFormat.Markdown] },
    },
  });

  result.results?.web?.forEach((r) => {
    console.log(r.title);
    console.log(`  URL: ${r.url}`);
    if (r.contents?.markdown) {
      console.log(`  Content (${r.contents.markdown.length} chars)`);
      console.log(`  Preview: ${r.contents.markdown.slice(0, 200)}…\n`);
    } else {
      console.log("  (No content retrieved)\n");
    }
  });
}

run();
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformer architecture explained",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    }
  }'
```

## Choose a Content Source

`extraction_source` decides whether full-page content comes from the You.com cache, a live crawl, or a mix of the two. Leave it unset to get `blend`, which is the right default for most pipelines.

| Source  | Behavior                                                                                        | Best for                                                                           |
| ------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `blend` | Serves cached content when it is available and crawls the page live when it is not. The default | General use, balanced latency and freshness                                        |
| `cache` | Returns cached content only. `contents` is omitted for results with nothing cached              | Latency-sensitive callers, large `count`, backfills where partial coverage is fine |
| `fetch` | Always crawls the page live                                                                     | Breaking news, prices, and anything else where staleness is a correctness problem  |

`cache` is the fastest of the three because it never waits on a crawl, and it trades coverage for that speed—expect some results to come back without a `contents` object. `fetch` is the slowest and the freshest.

Only pages crawled live are billed, at \$1.00 per 1,000 pages. Cached content carries no extraction charge, so `cache` costs nothing beyond the base call price and `blend` bills only the pages it crawls live. See [Billing](/docs/administration/billing) for worked examples.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode, ExtractionSource

with You() as you:
  res = you.search(
    query="nvidia earnings",
    count=5,
    extraction=Extraction(
      extraction_mode=ExtractionMode.FULL_PAGE,
      extraction_source=ExtractionSource.FETCH,
      full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
  )
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode, ExtractionSource } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const result = await you.search({
  query: "nvidia earnings",
  count: 5,
  extraction: {
    extraction_mode: ExtractionMode.FullPage,
    extraction_source: ExtractionSource.Fetch,
    full_page: { extraction_formats: [ExtractionFormat.Markdown] },
  },
});
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "nvidia earnings",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "extraction_source": "fetch",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    }
  }'
```

## Full Article Bodies for News

Combine full-page extraction with `freshness` for breaking news pipelines. Web results are crawled in the same call, so read `results.news` if articles are all you need.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode, Freshness

with You() as you:
  res = you.search(
    query="semiconductor supply chain",
    freshness=Freshness.WEEK,
    count=5,
    extraction=Extraction(
      extraction_mode=ExtractionMode.FULL_PAGE,
      full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
  )

  if res.results and res.results.news:
    for article in res.results.news:
      print(f"{article.title}")
      if article.contents and article.contents.markdown:
        print(article.contents.markdown[:400])
      print()
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode, Freshness } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

async function run() {
  const result = await you.search({
    query: "semiconductor supply chain",
    freshness: Freshness.Week,
    count: 5,
    extraction: {
      extraction_mode: ExtractionMode.FullPage,
      full_page: { extraction_formats: [ExtractionFormat.Markdown] },
    },
  });

  result.results?.news?.forEach((article) => {
    console.log(article.title);
    if (article.contents?.markdown) {
      console.log(article.contents.markdown.slice(0, 400));
    }
    console.log();
  });
}

run();
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "semiconductor supply chain",
    "freshness": "week",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    }
  }'
```

## Get Both Markdown and HTML

Pass both formats in `extraction_formats` to receive `contents.markdown` and `contents.html` on every crawled result.

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing breakthroughs",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown", "html"]
      }
    }
  }'
```

## Control Crawl Timeout

By default the crawler waits up to 10 seconds per page. For latency-sensitive applications, reduce `crawl_timeout`. For complex or slow-loading pages, increase it (up to 60 seconds). `crawl_timeout` sits at the top level of the request, not inside `extraction`, and only applies when `extraction_mode: "full_page"`. Combining it with `highlights` is invalid.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode

with You() as you:
  # Low-latency pipeline: only wait 3 seconds per page
  res = you.search(
    query="latest Python releases",
    count=5,
    extraction=Extraction(
      extraction_mode=ExtractionMode.FULL_PAGE,
      full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
    crawl_timeout=3,
  )

  if res.results and res.results.web:
    for result in res.results.web:
      status = "crawled" if result.contents and result.contents.markdown else "skipped (timeout)"
      print(f"{result.title} — {status}")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

async function run() {
  const response = await fetch("https://ydc-index.io/v1/search", {
    method: "POST",
    headers: {
      "X-API-Key": process.env.YDC_API_KEY!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: "latest Python releases",
      count: 5,
      extraction: {
        extraction_mode: ExtractionMode.FullPage,
        full_page: { extraction_formats: [ExtractionFormat.Markdown] },
      },
      // Low-latency pipeline: only wait 3 seconds per page
      crawl_timeout: 3,
    }),
  });

  const result = await response.json();

  result.results?.web?.forEach((r) => {
    const status = r.contents?.markdown ? "crawled" : "skipped (timeout)";
    console.log(`${r.title} — ${status}`);
  });
}

run();
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest Python releases",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    },
    "crawl_timeout": 3
  }'
```

## HTML vs Markdown

| Format     | Best for                                                    |
| ---------- | ----------------------------------------------------------- |
| `markdown` | LLM prompts, RAG, text analysis—clean, no boilerplate       |
| `html`     | Rendering, scraping structured data, preserving page layout |

## Highlights or Full Page?

A few rules of thumb:

* **You want fast, citation-anchored snippets.** Use `highlights` with a moderate `count` (10–25). Excerpts land in `contents.highlights`.
* **You need the document body to feed a downstream indexer or synthesizer.** Use `full_page` with `extraction_formats: ["markdown"]`.
* **You need rendered HTML for scraping or both formats in the same response.** Use `full_page` with `extraction_formats: ["html", "markdown"]` to receive both `contents.markdown` and `contents.html` per result.
* **You already know the URLs.** Use the [Contents API](/docs/guides/contents) directly. There is no need to search first.

## Already Have URLs?

If you have a list of URLs and don't need to search first, use the [Contents API](/docs/guides/contents) directly. It accepts URLs without a query and returns the same `markdown` or `html` content.

## Legacy: `livecrawl`

Before `extraction`, page content came from the `livecrawl` parameter. It still works on both `GET` and `POST /v1/search`, so existing integrations keep running. It is deprecated and no longer developed. `extraction` covers the same job and adds query-relevant `highlights`, so new integrations should use it.

Moving off `livecrawl` on `POST /v1/search`:

| Legacy `livecrawl`                              | Use instead                                                                       |
| ----------------------------------------------- | --------------------------------------------------------------------------------- |
| `livecrawl=web`, `news`, or `all`               | `extraction.extraction_mode: "full_page"`, which crawls every web and news result |
| `livecrawl_formats: ["markdown"]` or `["html"]` | `extraction.full_page.extraction_formats: ["markdown"]` or `["html"]`             |
| No equivalent                                   | `extraction.extraction_mode: "highlights"` for token-efficient excerpts           |

`extraction` is available on `POST /v1/search` only. `GET /v1/search` keeps `livecrawl` for backward compatibility but receives no new features.

---

## Next Steps

#### [Contents API](/docs/guides/contents)

Fetch page content directly from URLs, no search query needed

#### [Get live news](/docs/guides/live-news)

Retrieve and filter real-time news results

#### [API reference](/docs/api-reference/search/v1-search)

View all parameters and response schemas

#### [Web Search API overview](/docs/guides/search)

Back to Web Search API overview