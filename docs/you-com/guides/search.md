> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Web Search API Overview

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

---

## What Is the You.com Web Search API?

The You.com Web Search API delivers high-quality, [structured web and news results](https://you.com/resources/what-is-a-search-api-for-llms) optimized for programmatic access in AI applications. Designed for developers building RAG systems, AI agents, knowledge bases, and data-driven applications, our Web Search API returns clean, structured data with rich metadata, relevant snippets, and full-page content.

## How It Works

The Web Search API processes your query and returns unified results from both web and news sources in a single request. Every result carries **core information**—URL, title, and description—and **rich metadata** such as publication dates, thumbnails, and favicons.

The text that comes back with each result depends on the `extraction` parameter:

| Request                         | Text returned per result                                                           |
| ------------------------------- | ---------------------------------------------------------------------------------- |
| No `extraction`                 | `snippets`—short, keyword-centered fragments                                       |
| `extraction_mode: "full_page"`  | `snippets`, plus `contents.markdown` or `contents.html` carrying the whole page    |
| `extraction_mode: "highlights"` | `contents.highlights`—the passages that address your query. `snippets` are omitted |

Our intelligent classification system automatically determines when to include news results based on query intent, ensuring you get the most relevant information for your use case.

## What You Get

Every search returns structured JSON with two main result types:

**Web results**

* Relevant web pages from across the internet
* Multiple text snippets per result for context (replaced by highlights when you ask for them)
* Publication dates
* Thumbnail images and favicons for UI display

**News results** (when relevant)

* Recent news articles from authoritative sources
* Article summaries and headlines
* Publication timestamps for freshness
* Associated images and metadata
* Full article content (HTML or Markdown) via full page extraction

All results are returned in clean, structured JSON format requiring no HTML parsing or post-processing.

---

## Key Features

### Choosing a Content Level

Each result can carry three levels of text. The right one depends on whether a person or a model is reading it.

**Snippets** are short, keyword-centered fragments built for a human skimming a results page. They come back by default, with no `extraction` object.

**Highlights** upgrade that per-result text to the passages from each page most relevant to your query, sized for token-sensitive agentic workflows. This is the content an agent actually needs, in the response field it already parses. Request them with `extraction_mode: "highlights"`.

**Full page content** returns the complete page rather than a selection from it. Reach for it when the whole document is the point—archiving, full-text analysis, extracting a table or section that a query-relevant passage would miss, or feeding a long-context model. Request it with `extraction_mode: "full_page"`.

|                | Snippets                 | Highlights                       | Full page                             |
| -------------- | ------------------------ | -------------------------------- | ------------------------------------- |
| Returned by    | Default, no `extraction` | `extraction_mode: "highlights"`  | `extraction_mode: "full_page"`        |
| Response field | `snippets`               | `contents.highlights`            | `contents.markdown` / `contents.html` |
| Selected by    | Keyword match            | Relevance to your query          | Whole page                            |
| Best for       | Rendering a results UI   | Grounding an agent or RAG prompt | Archiving, full-document analysis     |

### Full page extraction—full page content per result

Add the `extraction` object to a `POST /v1/search` request with `extraction_mode` set to `full_page`, and every web and news result gains a `contents` object with the page content.
Set `extraction.full_page.extraction_formats` to `["markdown"]` (recommended for LLMs), `["html"]`, or both.
Set `extraction.extraction_source` to choose where that content comes from: `blend` (the default) serves cached content and crawls live on a miss, `cache` skips crawling entirely for the lowest latency, and `fetch` always crawls live for the freshest page. That choice sets the cost too, since only live crawls are billed. See [Retrieve page content](/docs/guides/retrieve-page-content) for the tradeoffs and [Pricing](#pricing) for the math.

```python startLine={5}
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode

with You() as you:
  # Crawl both web and news results
  res = you.search(
    query="latest AI developments",
    count=5,
    extraction=Extraction(
      extraction_mode=ExtractionMode.FULL_PAGE,
      full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
  )

  # Access extracted content from web results
  if res.results and res.results.web:
      for result in res.results.web:
          if result.contents and result.contents.markdown:
              print(f"Web: {result.title}")
              print(f"Content: {result.contents.markdown[:200]}...\n")

  # Access extracted content from news results
  if res.results and res.results.news:
      for result in res.results.news:
          if result.contents and result.contents.markdown:
              print(f"News: {result.title}")
              print(f"Content: {result.contents.markdown[:200]}...\n")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  // Crawl both web and news results
  const result = await you.search({
    query: "latest AI developments",
    count: 5,
    extraction: {
      extraction_mode: ExtractionMode.FullPage,
      full_page: { extraction_formats: [ExtractionFormat.Markdown] },
    },
  });

  // Access extracted content from both web and news results
  result.results?.web?.forEach((r) => {
    if (r.contents?.markdown) {
      console.log(`Web: ${r.title}`);
      console.log(`Content: ${r.contents.markdown.slice(0, 200)}...\n`);
    }
  });

  result.results?.news?.forEach((r) => {
    if (r.contents?.markdown) {
      console.log(`News: ${r.title}`);
      console.log(`Content: ${r.contents.markdown.slice(0, 200)}...\n`);
    }
  });
}

run();
```

```curl
# Extract full page content from web and news results
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest AI developments",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    }
  }'
```

**Need content from specific URLs you already have?** Use the [Contents API](/docs/guides/contents) instead—it takes a list of URLs directly, without requiring a search query.

### Unified web & news results

Get both web pages and news articles in a single API call. Our classification system automatically determines when to include news results based on query intent.

```json maxLines=20
{
  "results": {
    "web": [ // Web search results
      {
        "url": "https://example.com/article",
        "title": "Article Title",
        "description": "Brief description of the content",
        "snippets": [
          "Relevant excerpt from the page",
          "Another relevant passage"
        ],
        "thumbnail_url": "https://example.com/image.jpg",
        "page_age": "2025-11-15T10:30:00",
        "favicon_url": "https://example.com/favicon.ico",
        "contents": { // Included when extraction_mode is "full_page"
          "markdown": "# Article Title\n\nFull page content..."
        }
      }
    ],
    "news": [ // News articles (when relevant)
      {
        "title": "Breaking News Article",
        "description": "News article summary",
        "url": "https://news.com/article",
        "page_age": "2025-11-15T14:00:00",
        "thumbnail_url": "https://news.com/image.jpg",
        "contents": { // Included when extraction_mode is "full_page"
          "markdown": "# Breaking News\n\nFull article content..."
        }
      }
    ]
  },
  "metadata": {
    "search_uuid": "942ccbdd-7705-4d9c-9d37-4ef386658e90",
    "query": "your search query",
    "latency": 0.342
  }
}
```

### LLM-optimized output

Every result includes:

* **Snippets or highlights:** Pre-extracted text excerpts—keyword-centered snippets by default, query-relevant highlights on request
* **Descriptions:** Clean summaries without HTML clutter
* **Metadata:** Publication dates, thumbnails, and favicons
* **Structured JSON:** No parsing required, ready for AI consumption

### Advanced search operators

Build powerful and precise search queries using search operators:

* `site:domain.com` - Search within specific domains
* `filetype:pdf` - Filter by file type
* `+term` / `-term` - Include/exclude specific terms
* Boolean operators: `AND`, `OR`, `NOT`

[Learn more about search operators](/docs/guides/search-operators)

### Global coverage

Target results by geographic region using the `country` parameter (ISO 3166-1 alpha-2 country codes) and filter by language using the `language` parameter (BCP 47 language codes).

### Freshness controls

Filter results by recency:

* `day` - Last 24 hours
* `week` - Last 7 days
* `month` - Last 30 days
* `year` - Last 365 days
* `YYYY-MM-DDtoYYYY-MM-DD` - Custom date range

### All optional parameters you can control

| Parameter                                 | Type                        | Description                                                                                                                                                                        |
| ----------------------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `query`                                   | string                      | Your search query (supports [search operators](/docs/guides/search-operators))                                                                                                     |
| `count`                                   | integer                     | Max results per section (default varies, max 100)                                                                                                                                  |
| `freshness`                               | string                      | `day`, `week`, `month`, `year`, or date range                                                                                                                                      |
| `country`                                 | string                      | Country code (e.g., `US`, `GB`, `FR`)                                                                                                                                              |
| `language`                                | string                      | BCP 47 language code (e.g., `EN`, `JA`, `DE`)                                                                                                                                      |
| `offset`                                  | integer                     | For pagination (0-9)                                                                                                                                                               |
| `safesearch`                              | string                      | `off`, `moderate` (default), `strict`                                                                                                                                              |
| `extraction`                              | object                      | Content to extract per result. `extraction_mode` is `full_page` or `highlights`. POST only                                                                                         |
| `extraction.extraction_source`            | string                      | Where `full_page` content comes from: `blend` (default), `cache`, or `fetch`                                                                                                       |
| `extraction.full_page.extraction_formats` | array                       | `html`, `markdown`, or both. Defaults to `["markdown"]`                                                                                                                            |
| `crawl_timeout`                           | integer                     | Maximum crawl timeout in seconds (`1-60`, default `10`). Applies only when `extraction_mode` is `full_page`                                                                        |
| `include_domains`                         | string (GET) / array (POST) | Restrict results to these domains. GET: comma-separated string. POST: JSON array. Supports up to 500 domains                                                                       |
| `exclude_domains`                         | string (GET) / array (POST) | Exclude results from these domains. GET: comma-separated string. POST: JSON array. Supports up to 500 domains                                                                      |
| `boost_domains`                           | string (GET) / array (POST) | Boost results from these domains without excluding other domains. GET: comma-separated string. POST: JSON array. Supports up to 500 domains. Cannot be used with `include_domains` |

[View full API reference](/docs/api-reference/search/v1-search)

---

## Common Use Cases

### RAG (Retrieval-Augmented Generation)

Use search snippets to provide context to your LLM without [hallucination](https://you.com/resources/ai-hallucination-prevention-guide). The structured snippets are perfect for feeding directly into your prompt.

#### [Deep Search template](/docs/examples/deep-search)

See a working app that uses multi-pass query expansion to surface more relevant results.

```python
from youdotcom import You

# Initialize
you = You()

# Search and extract context
def get_context(query):
    res = you.search(query=query, count=5)
    snippets = []
    if res.results and res.results.web:
        for result in res.results.web:
            if result.snippets:
                snippets.extend(result.snippets)
    return "\n".join(snippets)

user_question = "What is the current state of quantum computing?"
context = get_context(user_question)

# Feed to your LLM
prompt = f"Based on this information:\n{context}\n\nAnswer: {user_question}"

```

### AI agent knowledge retrieval

Give your AI agents access to real-time web information. Perfect for building agents that need up-to-date facts, news, or specialized domain knowledge.

#### [Simple Search template](/docs/examples/simple-search)

See a working app that runs a web search and returns the top results.

### News monitoring & alerts

Track breaking news, competitor mentions, or industry trends. The automatic news classification ensures you get timely articles when relevant.

### Content research & analysis

Gather comprehensive information from multiple sources for content creation, competitive intelligence, or market research.

### Knowledge base construction

Use full page extraction to build comprehensive knowledge bases with full-page content in clean Markdown format.

---

## Examples of Advanced Search Capabilities

### Domain filtering

Restrict results to, exclude results from, or boost specific domains. Use `include_domains` for a strict allowlist, `exclude_domains` to filter out unwanted domains, and `boost_domains` to prefer matching domains without filtering out other results. For large domain lists, POST is strongly recommended.

```python
from youdotcom import You

with You() as you:
  # Only return results from trusted news sources
  res = you.search(
    query="federal reserve interest rate decision",
    include_domains=["reuters.com", "apnews.com", "ft.com", "bloomberg.com"],
  )

  if res.results and res.results.web:
      for result in res.results.web:
          print(f"{result.title} — {result.url}")
```

```typescript
// Only return results from trusted news sources.
// POST avoids URL length limits on long domain lists.
async function run() {
  const response = await fetch("https://ydc-index.io/v1/search", {
    method: "POST",
    headers: {
      "X-API-Key": process.env.YDC_API_KEY!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: "federal reserve interest rate decision",
      include_domains: ["reuters.com", "apnews.com", "ft.com", "bloomberg.com"],
    }),
  });

  const result = await response.json();

  result.results?.web?.forEach((r) => {
    console.log(`${r.title} — ${r.url}`);
  });
}

run();
```

```curl
# POST is recommended for domain lists — avoids URL length limits
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "federal reserve interest rate decision",
    "include_domains": ["reuters.com", "apnews.com", "ft.com", "bloomberg.com"]
  }'
```

Use `boost_domains` when you want to prefer sources without making them mandatory. Matching results from boosted domains receive a relative ranking boost, but the boost is not quantified. If boosted domains do not have matching results, results from other domains can still appear. `boost_domains` can be used with `exclude_domains`, but not with `include_domains`.

### Search operators

Combine operators for powerful, precise searches:

```python
from youdotcom import You
from youdotcom.models import Freshness

with You() as you:
  # Find PDFs about climate change from .edu sites published this year
  res = you.search(
      query="climate change site:.edu filetype:pdf",
      freshness=Freshness.YEAR,
  )

  # Print PDF results with their URLs
  if res.results and res.results.web:
      for result in res.results.web:
          print(f"{result.title}")
          print(f"  PDF URL: {result.url}")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { Freshness } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  // Find PDFs about climate change from .edu sites published this year
  const result = await you.search({
    query: "climate change site:.edu filetype:pdf",
    freshness: Freshness.Year,
  });

  console.log(result);
}

run();
```

```curl
# Find PDFs about climate change from .edu sites published this year
curl -X POST 'https://ydc-index.io/v1/search' \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "climate change site:.edu filetype:pdf",
    "freshness": "year"
  }'
```

### Pagination

Use `offset` to retrieve additional pages of results. The offset value (0-9) skips that many pages, so `offset=1` with `count=10` returns results 11-20.

```python
from youdotcom import You

with You() as you:
  # Get the second page of results
  res = you.search(
    query="machine learning",
    count=10,
    offset=1,
  )

  print(res.results.web)
```

```typescript
import { You } from "@youdotcom-oss/sdk";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  // Get the second page of results
  const result = await you.search({
    query: "machine learning",
    count: 10,
    offset: 1,
  });

  console.log(result);
}

run();
```

```curl
# Get the second page of results (results 11-20)
curl -X POST 'https://ydc-index.io/v1/search' \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "count": 10,
    "offset": 1
  }'
```

### Geographic targeting

Narrow down on results by country:

```python
from youdotcom import You
from youdotcom.models import Country

# Get Swiss results
with You() as you:
  res = you.search(
    query="best restaurants in geneva",
    country=Country.CH,
  )

  # Print restaurant results with descriptions
  if res.results and res.results.web:
      for result in res.results.web:
          print(f"{result.title}")
          if result.description:
              print(f"  {result.description}\n")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { Country } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  // Get Swiss results
  const result = await you.search({
    query: "best restaurants in geneva",
    country: Country.Ch,
  });

  console.log(result);
}

run();
```

```curl
# Get Swiss results
curl -X POST 'https://ydc-index.io/v1/search' \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "best restaurants in geneva",
    "country": "CH"
  }'
```

Refer to the [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) standard for a list of country codes.

---

## Best Practices

### 1. Use highlights for RAG

Request `extraction_mode: "highlights"` and read `contents.highlights`. You get the passages most relevant to your query, already sized for a prompt, without paying to crawl and process whole pages. Fall back to the `snippets` array when you are rendering results for a person rather than grounding a model.

### 2. Implement caching

Cache frequent queries to reduce API calls and improve response times. Consider a 5-15 minute TTL for most use cases.

### 3. Handle empty results

Always check if `results.web` or `results.news` arrays are empty before processing:

```python
if res.results and res.results.web:
    for result in res.results.web:
        process(result)
else:
    handle_no_results()
```

### 4. Use appropriate count values

* For RAG: `count=5-10` is usually sufficient
* For UI display: `count=20-50` for pagination
* For data gathering: `count=100` (max) for comprehensive coverage

### 5. Use search operators and query parameters

Use search operators and specify [request parameters](/docs/api-reference/search/v1-search) in the request to reduce noise and get more relevant results.

---

## Request Format

Send parameters as a JSON body on `POST /v1/search`. Array fields are plain JSON arrays, with no ambiguity between comma-separated values and repeated params.

| Field                                     | POST (JSON body)                             |
| ----------------------------------------- | -------------------------------------------- |
| `include_domains`                         | `"include_domains": ["a.com", "b.com"]`      |
| `exclude_domains`                         | `"exclude_domains": ["a.com", "b.com"]`      |
| `boost_domains`                           | `"boost_domains": ["a.com", "b.com"]`        |
| `extraction.full_page.extraction_formats` | `"extraction_formats": ["html", "markdown"]` |

`GET /v1/search` still works and existing integrations will keep running, but it will not receive new feature updates. New features will be added to `POST` only, and `extraction` is only available there. On GET, domain filters must also fit in a single comma-separated query string value and are subject to URL length limits.

---

## Pricing

**\$5.00 per 1,000 calls** (up to 100 results per call)

All new accounts receive \$100 in free credits to get started. See the [Billing page](/docs/administration/billing#web-search-api) for complete pricing details.

Agents can also pay per call without an account. `GET /v1/search` and both verbs of `/v1/agents/search` accept [machine payments](/docs/administration/machine-payments), settling each request in USDC from a funded wallet instead of drawing down credits.

**What's included:**

* Web and news results in a single unified request
* Up to 100 results per call
* News results at no extra cost
* LLM-ready snippets with rich metadata
* Country, language, recency, domain and more targeting filters

**Full page extraction add-on—\$1.00 per 1,000 pages fetched live**

Full page content via `extraction_mode: "full_page"` (HTML, Markdown, or both) is billed separately from the base Web Search API rate. Only pages crawled live are billed, so what you pay depends on `extraction_source`: `fetch` crawls every result, `blend` (the default) charges only for the pages it could not serve from cache, and `cache` adds no extraction charge at all.

**Example:** A single call with `count=10` and `extraction_mode: "full_page"` returns 10 web results and 10 news results—20 pages total. This call leaves `extraction_source` unset, so it runs `blend`. Say 2 of the 20 pages are already cached and the other 18 are crawled live.

| Line item                          | Calculation               | Cost        |
| ---------------------------------- | ------------------------- | ----------- |
| Web Search API call                | 1 call × \$5.00 / 1,000   | \$0.005     |
| Full page extraction, crawled live | 18 pages × \$1.00 / 1,000 | \$0.018     |
| Full page extraction, from cache   | 2 pages × \$0.00          | \$0.000     |
| **Total**                          |                           | **\$0.023** |

Cache coverage varies by query, so treat that split as one outcome rather than a rate to budget against. This call costs \$0.025 when all 20 pages are crawled live and \$0.005 with `extraction_source: "cache"`. See [Billing](/docs/administration/billing) for the full breakdown.

For volume discounts, annual pricing, or enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).

---

## Data Retention

Organizations operating under strict privacy, compliance, or security mandates can add Zero Data Retention (ZDR) to an enterprise agreement. ZDR restricts retention of Web Search API request and response content account-wide and requires no changes to your integration. See [Zero Data Retention](/docs/administration/zero-data-retention) for what it covers and how to enable it.

---

## Next Steps

#### [Run in Postman](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-83118dc1-7279-49f6-893d-4c18b8163008)

Use our Postman collections to learn and experiment on your own

![Run In Postman](https://run.pstmn.io/button.svg)

#### [API reference](/docs/api-reference/search/v1-search)

Explore the complete API documentation with all parameters and response schemas

#### [Search operators](/docs/guides/search-operators)

Master advanced search operators to refine your queries

#### [Quickstart guide](/docs/quickstart)

Get your API key and make your first search in 5 minutes

---