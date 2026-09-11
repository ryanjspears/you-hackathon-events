> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Answer API Overview

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

---

## What Is the Answer API?

The Answer API returns a synthesized natural-language answer with citations and the web results used to generate it.
Send a `query` with optional freshness, locale, domain, and explicit-content controls. The API retrieves web results and synthesizes an answer with inline citations.

Unknown or extra request fields are rejected.

---

## How It Works

The Answer API runs a managed pipeline over the same retrieval and extraction infrastructure as the Web Search API and Contents API. For each query, it retrieves web results, pulls the most relevant supporting content, and synthesizes a cited answer in a single request. You don't configure search strategy, page reads, prompts, or model selection.

The API verifies that every citation exists in the source text and supports the answer before returning it. The `excerpts` in each citation are the verbatim passages the LLM used to construct the answer, so you can confirm accuracy without trusting the model alone.

On the SimpleQA benchmark, the Answer API reports 93.48% accuracy. Typical p50 latency is 2.67 seconds. There are no effort tiers to tune, so latency and cost stay predictable across queries.

---

## When to Use the Answer API

Three options get you from a question to a cited, web-grounded answer: wire the Web Search API and Contents API into your own LLM, use the Answer API, or use the Research API. Which one fits depends on how much of the pipeline you want to own.

|                  | Build Your Own                                              | Answer API                                | Research API                                          |
| ---------------- | ----------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------- |
| **You assemble** | Retrieval, page reads, prompt, model, dedup, citation logic | Nothing (one call)                        | Nothing (one call)                                    |
| **You get**      | Whatever you build                                          | Answer + citations + web results          | Answer or structured JSON + sources                   |
| **Control**      | Full                                                        | Query, freshness, locale, domains         | Depth (`lite` → `frontier`), schema, background mode  |
| **Speed**        | Depends on your stack                                       | A few seconds                             | Varies by effort                                      |
| **Best for**     | Custom orchestration you want to own                        | Fast grounded answers, simple integration | Depth control, structured output, multi-step research |

**Build your own** when you want full control over retrieval, prompting, and model choice. The tradeoff is owning the orchestration: deduplicating sources, extracting the right passages, generating consistent inline citations, and keeping the answer grounded. Teams that build this in-house often hit hallucinations, rising LLM token costs, self-contradictory answers, and inefficient use of retrieved sources.

**Answer** when you want a citation-backed answer from real-time web results in a single call, without configuring research depth or defining an output schema. It's the right choice for questions that can be answered from a single, high-quality search rather than multi-step reasoning.

**Research** when you need control over depth. The `research_effort` parameter (`lite` through `frontier`) lets you trade cost and latency against thoroughness, and `output_schema` returns structured JSON. Research `lite` and `standard` cover the middle ground: fast enough for production, deeper than a single retrieval pass.

---

## What You Get

Every Answer API response includes:

* **`answer`**: A Markdown-formatted answer with numbered inline citations, such as `[[1, 2]]`, that reference items in the `citations` array.
* **`citations`**: The sources cited in the answer, in citation order. Each item contains a `source` URL and the verbatim `excerpts` the LLM used to construct the answer.
* **`results.web`**: All web results considered during answer synthesis, whether cited or not.

Each item in `results.web` includes a URL, title, and snippets. Source metadata can include `description`, `thumbnail_url`, and `page_age`, an ISO 8601 publication timestamp.

```json maxLines=30
{
  "answer": "The aurora borealis is caused by charged particles ejected from the Sun—carried by the solar wind and often intensified by solar flares or coronal mass ejections—that travel to Earth, are funneled by Earth's magnetic field toward the polar regions, and collide with oxygen and nitrogen atoms in the upper atmosphere. These collisions excite the atoms, which then release photons of light, creating the visible northern lights. [[1, 2]]",
  "citations": [
    {
      "source": "https://www.jpl.nasa.gov/nmp/st5/SCIENCE/aurora.html",
      "excerpts": [
        "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions. These natural light shows are caused by magnetic storms that have been triggered by solar activity."
      ]
    },
    {
      "source": "https://www.valofinland.com/what-causes-the-colours-in-aurora-borealis/",
      "excerpts": [
        "When these particles reach Earth, they collide with gases in our atmosphere, such as oxygen and nitrogen. These collisions excite the gas particles, causing them to emit light."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.jpl.nasa.gov/nmp/st5/SCIENCE/aurora.html",
        "title": "How Auroras Form",
        "snippets": [
          "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions."
        ]
      }
    ]
  }
}
```

---

## Quickstart

```python maxLines=0
from youdotcom import You

with You() as you:
    response = you.answer(query="Top 5 EV-selling companies worldwide in 2025 so far")

    print(response.answer)

    print(f"\n--- {len(response.citations or [])} citations ---")
    for i, citation in enumerate(response.citations or [], 1):
        print(f"[{i}] {citation.source}")
```

```typescript
const response = await fetch("https://api.you.com/v1/answer", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "Top 5 EV-selling companies worldwide in 2025 so far",
  }),
});

const data = await response.json();
console.log(data.answer);

console.log(`\n--- ${data.citations.length} citations ---`);
data.citations.forEach((citation, i) => {
  console.log(`[${i + 1}] ${citation.source}`);
});
```

```curl
curl -X POST https://api.you.com/v1/answer \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Top 5 EV-selling companies worldwide in 2025 so far"
  }'
```

---

## Parameters

`query` is required. All other fields are optional.

| Parameter         | Type      | Required | Description                                                                                                                                                         |
| ----------------- | --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `query`           | string    | Yes      | The question or prompt to answer. Limited to 400 characters. Cannot be blank.                                                                                       |
| `freshness`       | string    | No       | `day`, `week`, `month`, `year`, or a date range in `YYYY-MM-DDtoYYYY-MM-DD` format                                                                                  |
| `country`         | string    | No       | Country code from the [supported set](/docs/api-reference/answer/v1-answer), such as `US`, `GB`, or `FR`, that determines the geographical focus of the web results |
| `language`        | string    | No       | Language tag from the [supported set](/docs/api-reference/answer/v1-answer), such as `EN`, `EN-GB`, or `FR`, that determines the language of the web results        |
| `safesearch`      | string    | No       | Explicit-content filtering for web results: `off`, `moderate` (default), or `strict`                                                                                |
| `include_domains` | string\[] | No       | Only return results from these domains. Max 500 domains. Cannot be used with `exclude_domains` or `boost_domains`                                                   |
| `exclude_domains` | string\[] | No       | Exclude results from these domains. Max 500 domains. Cannot be used with `include_domains`. Can be used with `boost_domains`                                        |
| `boost_domains`   | string\[] | No       | Prefer results from these domains without excluding other domains. Max 500 domains. Can be used with `exclude_domains`, but not with `include_domains`              |

[View full API reference](/docs/api-reference/answer/v1-answer)

---

## Using Search Controls

The Answer API accepts the same freshness, locale, domain, and explicit-content controls as the Web Search API. All controls are optional and can be combined, except `include_domains` with `exclude_domains` or `boost_domains`.

`safesearch` defaults to `moderate`. Set it to `strict` for stronger explicit-content filtering or `off` to return unfiltered web results.

### Freshness

Restrict results to the last week for questions about recent events:

```python
from youdotcom import You

with You() as you:
    response = you.answer(
        query="What changed in the latest Fed interest rate decision?",
        freshness="week",
    )
```

```typescript
const response = await fetch("https://api.you.com/v1/answer", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What changed in the latest Fed interest rate decision?",
    freshness: "week",
  }),
});
```

```curl
curl -X POST https://api.you.com/v1/answer \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What changed in the latest Fed interest rate decision?",
    "freshness": "week"
  }'
```

Use a custom date range for questions bounded to a specific period:

```python
from youdotcom import You

with You() as you:
    response = you.answer(
        query="What were the major AI regulation developments in 2025?",
        freshness="2025-01-01to2025-12-31",
    )
```

```typescript
const response = await fetch("https://api.you.com/v1/answer", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What were the major AI regulation developments in 2025?",
    freshness: "2025-01-01to2025-12-31",
  }),
});
```

```curl
curl -X POST https://api.you.com/v1/answer \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What were the major AI regulation developments in 2025?",
    "freshness": "2025-01-01to2025-12-31"
  }'
```

### Domain Filters

Restrict results to trusted sources with `include_domains`:

```python
from youdotcom import You

with You() as you:
    response = you.answer(
        query="What are the FDA-approved GLP-1 receptor agonists?",
        include_domains=["fda.gov", "nih.gov"],
    )
```

```typescript
const response = await fetch("https://api.you.com/v1/answer", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What are the FDA-approved GLP-1 receptor agonists?",
    include_domains: ["fda.gov", "nih.gov"],
  }),
});
```

```curl
curl -X POST https://api.you.com/v1/answer \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the FDA-approved GLP-1 receptor agonists?",
    "include_domains": ["fda.gov", "nih.gov"]
  }'
```

Exclude unreliable sources while boosting authoritative ones. `exclude_domains` and `boost_domains` can be used together:

```python
from youdotcom import You

with You() as you:
    response = you.answer(
        query="What is the current state of quantum computing?",
        exclude_domains=["reddit.com", "quora.com"],
        boost_domains=["nature.com", "science.org", "arxiv.org"],
    )
```

```typescript
const response = await fetch("https://api.you.com/v1/answer", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What is the current state of quantum computing?",
    exclude_domains: ["reddit.com", "quora.com"],
    boost_domains: ["nature.com", "science.org", "arxiv.org"],
  }),
});
```

```curl
curl -X POST https://api.you.com/v1/answer \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current state of quantum computing?",
    "exclude_domains": ["reddit.com", "quora.com"],
    "boost_domains": ["nature.com", "science.org", "arxiv.org"]
  }'
```

### Country and Language

Focus results on a specific region and language:

```python
from youdotcom import You

with You() as you:
    response = you.answer(
        query="What are the top startup hubs in Germany?",
        country="DE",
        language="DE",
    )
```

```typescript
const response = await fetch("https://api.you.com/v1/answer", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What are the top startup hubs in Germany?",
    country: "DE",
    language: "DE",
  }),
});
```

```curl
curl -X POST https://api.you.com/v1/answer \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the top startup hubs in Germany?",
    "country": "DE",
    "language": "DE"
  }'
```

---

## Common Use Cases

### Question Answering in AI Applications

Use the Answer API in applications that need grounded, cited responses, including chatbots, copilots, and research tools. Send a question and get a sourced answer without configuring research effort.

### Content Pipelines

Use the Answer API as a research step before writing: ask a question, get a well-cited answer, and use that as source material for reports, articles, or briefings.

### Internal Knowledge Tools

Let employees ask complex questions—product comparisons, regulatory summaries, technical deep dives—and get sourced answers without manually reading dozens of pages.

---

## Best Practices

### Write Specific Questions for Better Answers

For complex topics, include context, constraints, or the specific angle you want covered. "What are the tradeoffs between PostgreSQL and MongoDB for a write-heavy workload at 10M rows?" produces a more focused answer than "Compare databases."

### Target Results with Search Controls

Set `freshness` when you need recent information. Select `country` and `language` from the [supported values](/docs/api-reference/answer/v1-answer) to control the region and language of web results. Set `safesearch` to control explicit-content filtering. Use `include_domains` for a strict allowlist, `exclude_domains` to remove unwanted sources, or `boost_domains` to prefer selected sources without filtering out other results.

### Verify Citations for High-Stakes Use Cases

The inline citation numbers map to the `citations` array. For legal, financial, or medical contexts, build a step that follows each `source` URL and checks the supporting `excerpts` before surfacing claims to users.

### Use Research When Depth Matters More Than Speed

If your use case requires choosing between a quick factual answer and an exhaustive or frontier analysis, the Research API's `research_effort` parameter gives you that control.

---

## Pricing

See the [Billing page](/docs/administration/billing#answer-api) for complete pricing details.

For volume discounts, annual pricing, or enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).

---

## Data Retention

Organizations operating under strict privacy, compliance, or security mandates can add Zero Data Retention (ZDR) to an enterprise agreement. ZDR restricts retention of Answer API request and response content account-wide and requires no changes to your integration. See [Zero Data Retention](/docs/administration/zero-data-retention) for what it covers and how to enable it.

---

## Next Steps

#### [API Reference](/docs/api-reference/answer/v1-answer)

Full parameter reference, request/response schemas, and interactive playground

#### [Research API](/docs/guides/research)

Control research depth with effort levels when thoroughness matters

#### [Quickstart](/docs/quickstart)

Get your API key and try all our APIs in under five minutes