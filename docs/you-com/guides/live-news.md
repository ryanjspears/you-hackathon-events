> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Get live news

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

## Overview

The Web Search API automatically returns news articles alongside web results whenever your query has news intent—[breaking events, recent announcements, trending topics](https://you.com/resources/ai-with-real-time-data). You don't need a separate endpoint or special configuration: just send your query and our classification system determines if news results are relevant.

When news results are returned, they appear in the `results.news` array alongside `results.web`.

## News-Specific Fields

Each news result includes:

| Field           | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `title`         | Article headline                                             |
| `description`   | Article summary                                              |
| `url`           | Link to the article                                          |
| `page_age`      | Publication timestamp (ISO 8601)                             |
| `thumbnail_url` | Associated image                                             |
| `contents`      | Full article content (when `extraction_mode` is `full_page`) |

## Parameters That Improve News Results

These parameters tune your news queries for relevance, recency, and safety:

| Parameter    | Type    | Description                                                                             |
| ------------ | ------- | --------------------------------------------------------------------------------------- |
| `count`      | integer | Max results per section (default 10, max 100)                                           |
| `freshness`  | string  | `day`, `week`, `month`, `year`, or a date range `YYYY-MM-DDtoYYYY-MM-DD`                |
| `country`    | string  | ISO 3166-1 alpha-2 country code—focuses results geographically (e.g., `US`, `GB`, `DE`) |
| `language`   | string  | BCP 47 language code—filters by article language (e.g., `EN`, `FR`, `JA`)               |
| `safesearch` | string  | Content moderation: `off`, `moderate` (default), or `strict`                            |

### `freshness`—control recency

`freshness` is the most important parameter for news use cases. Breaking news requires `day`; trend analysis might use `week` or `month`. You can also specify an exact date range.

```python
from youdotcom.models import Freshness

freshness=Freshness.DAY          # Last 24 hours
freshness=Freshness.WEEK         # Last 7 days
freshness=Freshness.MONTH        # Last 30 days
freshness=Freshness.YEAR         # Last 365 days
freshness="2025-01-01to2025-03-01"  # Custom range
```

## Basic News Query

```python
from youdotcom import You
from youdotcom.models import Freshness

with You() as you:
  res = you.search(
    query="AI regulation news",
    freshness=Freshness.DAY,
    count=10,
  )

  if res.results and res.results.news:
    for article in res.results.news:
      print(f"{article.title}")
      print(f"  {article.url}")
      print(f"  Published: {article.page_age}\n")
  else:
    print("No news results returned for this query.")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { Freshness } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  const result = await you.search({
    query: "AI regulation news",
    freshness: Freshness.Day,
    count: 10,
  });

  result.results?.news?.forEach((article) => {
    console.log(article.title);
    console.log(`  ${article.url}`);
    console.log(`  Published: ${article.pageAge}\n`);
  });
}

run();
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI regulation news",
    "freshness": "day",
    "count": 10
  }'
```

## Filter by Country and Language

Use `country` and `language` together to narrow results to a specific region and language. This is useful for monitoring local news, international media, or non-English markets.

```python
from youdotcom import You
from youdotcom.models import Freshness, Country

with You() as you:
  # Get French-language news from France, published this week
  res = you.search(
    query="élections",
    freshness=Freshness.WEEK,
    country=Country.FR,
    language="FR",
    count=10,
  )

  if res.results and res.results.news:
    for article in res.results.news:
      print(f"{article.title} — {article.page_age}")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { Freshness, Country } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  // Get French-language news from France, published this week
  const result = await you.search({
    query: "élections",
    freshness: Freshness.Week,
    country: Country.Fr,
    language: "FR",
    count: 10,
  });

  result.results?.news?.forEach((article) => {
    console.log(`${article.title} — ${article.pageAge}`);
  });
}

run();
```

```curl
# Get French-language news from France, published this week
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "élections",
    "freshness": "week",
    "country": "FR",
    "language": "FR",
    "count": 10
  }'
```

## Custom Date Range

Use a date range string in `YYYY-MM-DDtoYYYY-MM-DD` format to target a specific window—useful for historical monitoring or scheduled digests.

```python
from youdotcom import You

with You() as you:
  res = you.search(
    query="federal reserve interest rates",
    freshness="2025-01-01to2025-03-01",
    count=20,
  )

  if res.results and res.results.news:
    for article in res.results.news:
      print(f"{article.page_age}  {article.title}")
```

```typescript
import { You } from "@youdotcom-oss/sdk";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  const result = await you.search({
    query: "federal reserve interest rates",
    freshness: "2025-01-01to2025-03-01",
    count: 20,
  });

  result.results?.news?.forEach((article) => {
    console.log(`${article.pageAge}  ${article.title}`);
  });
}

run();
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "federal reserve interest rates",
    "freshness": "2025-01-01to2025-03-01",
    "count": 20
  }'
```

## Get Full Article Content

Set `extraction.extraction_mode` to `full_page` on a `POST /v1/search` request to retrieve the full page content of every search result, web and news alike.

Set `extraction.full_page.extraction_formats` to `["markdown"]` or `["html"]` based on your needs. Use `["markdown"]` for LLM-ready output.

Full page extraction is billed at **\$1.00 per 1,000 pages** on top of the base Web Search API rate—the same price as the Contents API. Each article body fetched counts as one page.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode, Freshness

with You() as you:
  res = you.search(
    query="climate policy summit",
    freshness=Freshness.DAY,
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
        print(article.contents.markdown[:300])
      print()
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode, Freshness } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  const result = await you.search({
    query: "climate policy summit",
    freshness: Freshness.Day,
    count: 5,
    extraction: {
      extraction_mode: ExtractionMode.FullPage,
      full_page: { extraction_formats: [ExtractionFormat.Markdown] },
    },
  });

  result.results?.news?.forEach((article) => {
    console.log(article.title);
    if (article.contents?.markdown) {
      console.log(article.contents.markdown.slice(0, 300));
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
    "query": "climate policy summit",
    "freshness": "day",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    }
  }'
```

For news monitoring pipelines that need full article bodies, combine `extraction_mode: "full_page"` with `freshness=day` and schedule recurring calls. See [Retrieve page content](/docs/guides/retrieve-page-content) for more on full page extraction.

---

## Next Steps

#### [Retrieve page content](/docs/guides/retrieve-page-content)

Get full HTML or Markdown from any result with full page extraction

#### [API reference](/docs/api-reference/search/v1-search)

View all parameters and response schemas