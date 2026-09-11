> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Quickstart

You.com gives you real-time web intelligence through five APIs: Web Search, Answer, Contents, Research, and Finance Research. Two ways to get started—write code, or connect your agent.

#### [Make API Calls](#get-your-api-key)

Get an API key and run your first request in minutes. Try each API in the flow below.

#### [Use Your AI Agent](#give-your-agent-access)

Connect your IDE or agent to You.com with no code—Docs MCP server, You.com MCP server, or Agent Skills.

The five APIs:

* **[Web Search API](/docs/guides/search)**—real-time web and news results as LLM-ready JSON
* **[Answer API](/docs/guides/answer)**—a cited, synthesized answer from a single query
* **[Contents API](/docs/guides/contents)**—clean Markdown or HTML from URLs you specify
* **[Research API](/docs/guides/research)**—multi-step, cited answers to complex questions
* **[Finance Research API](/docs/guides/finance-research)**—cited answers from a finance-optimized index

---

## Get Your API Key

Sign in or create an account, then get an API key here: [https://you.com/platform](https://you.com/platform). You'll start with \$100 in complimentary credits—no credit card required.

The code samples below read your key from an environment variable named `YDC_API_KEY`—the canonical variable name across our docs, SDKs, and integrations. Set it once (`export YDC_API_KEY="your-key"`) and the examples will pick it up. See [API key management](/docs/administration/api-keys) for best practices.

## Try the Web Search API

The Web Search API returns real-time web and news results as structured, LLM-ready JSON. Feed the results directly into your prompt to ground your AI in fresh information.

```python
from youdotcom import You

with You() as you:
    results = you.search(query="global birth rate trends", count=5)

    for result in results.results.web:
        print(result.title)
        print(result.url)
        if result.snippets:
            print(result.snippets[0])
```

```typescript
import { You } from "@youdotcom-oss/sdk";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const result = await you.search({ query: "global birth rate trends", count: 5 });

result.results?.web?.forEach((r) => {
  console.log(r.title, r.url);
  console.log(r.snippets?.[0]);
});
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "global birth rate trends",
    "count": 5
  }'
```

You'll get back structured JSON like this:

```json maxLines=20
{
  "results": {
    "web": [
      {
        "url": "https://www.worldbank.org/en/topic/population",
        "title": "Population | World Bank",
        "description": "The World Bank tracks global birth rate and population trends.",
        "snippets": [
          "Global fertility rates have declined significantly over the past five decades, falling from an average of 5 births per woman in 1960 to around 2.3 today."
        ],
        "page_age": "2025-10-01T00:00:00",
        "favicon_url": "https://ydc-index.io/favicon?domain=worldbank.org&size=128"
      }
    ]
  },
  "metadata": {
    "query": "global birth rate trends",
    "search_uuid": "a1b2c3d4-0000-0000-0000-000000000000",
    "latency": 0.38
  }
}
```

The [Python SDK](/docs/sdks/python-sdk) covers the Web Search, Answer, Contents, Research, and Finance Research APIs. The [TypeScript SDK](/docs/sdks/typescript-sdk) covers the Web Search, Contents, and Research APIs—call the Answer and Finance Research APIs directly over HTTP with the same `X-API-Key` header.

### Improve Accuracy with Full Page Extraction

Search results already include snippets—short, query-relevant text extracts from target pages. Use the `extraction` parameter with `extraction_mode: "full_page"` to fetch full page content for each result as clean Markdown or HTML.

This will naturally increase latency, but massively improves knowledge accuracy.

Full page extraction is billed at \$1.00 per 1,000 pages fetched live on top of the base Web Search API rate—the same price as the Contents API. With the default `count=10`, a call using `extraction_mode: "full_page"` crawls up to 20 pages and adds up to \$0.02 to the \$0.005 base cost. Pages served from cache are free. See [Billing](/docs/administration/billing) for how `extraction_source` changes the charge.

```python
from youdotcom import You
from youdotcom.models import Extraction, ExtractionFormat, ExtractionMode

with You() as you:
    results = you.search(
        query="global birth rate trends",
        count=5,
        extraction=Extraction(
            extraction_mode=ExtractionMode.FULL_PAGE,
            full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
        ),
    )

    for result in results.results.web:
        if result.contents and result.contents.markdown:
            print(result.title)
            print(result.contents.markdown[:400])
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ExtractionFormat, ExtractionMode } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const result = await you.search({
  query: "global birth rate trends",
  count: 5,
  extraction: {
    extraction_mode: ExtractionMode.FullPage,
    full_page: { extraction_formats: [ExtractionFormat.Markdown] },
  },
});

result.results?.web?.forEach((r) => {
  if (r.contents?.markdown) {
    console.log(r.title);
    console.log(r.contents.markdown.slice(0, 400));
  }
});
```

```curl
curl -X POST https://ydc-index.io/v1/search \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "global birth rate trends",
    "count": 5,
    "extraction": {
      "extraction_mode": "full_page",
      "full_page": {
        "extraction_formats": ["markdown"]
      }
    }
  }'
```

Results that support extraction will include a `contents.markdown` field with the full page. For RAG pipelines that need deep context rather than surface-level snippets, this is the parameter to reach for.

[Full Web Search API reference and all parameters](/docs/guides/search)

## Try the Answer API

The Web Search API gives you the raw results. The Answer API does the next step—it retrieves web results, verifies every citation against the source text, and returns a Markdown answer with inline citations in one call. The fastest path from a question to a grounded answer, with no orchestration on your end.

```python
from youdotcom import You

with You() as you:
    response = you.answer(
        query="What are the main drivers of the global decline in birth rates?",
    )

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
    query: "What are the main drivers of the global decline in birth rates?",
  }),
});

if (!response.ok) {
  throw new Error(`HTTP error: ${response.status}`);
}

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
    "query": "What are the main drivers of the global decline in birth rates?"
  }'
```

The response includes a Markdown answer with numbered inline citations, the sources cited, and the web results considered during synthesis:

```json maxLines=20
{
  "answer": "Global fertility rates have declined over the past five decades due to a combination of increased access to contraception, rising female education and labor force participation, higher costs of raising children, and urbanization. [[1, 2, 3]]",
  "citations": [
    {
      "source": "https://www.worldbank.org/en/topic/population",
      "excerpts": [
        "Global fertility rates have declined significantly over the past five decades, falling from an average of 5 births per woman in 1960 to around 2.3 today."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.worldbank.org/en/topic/population",
        "title": "Population | World Bank",
        "snippets": ["Global fertility rates have declined significantly over the past five decades..."]
      }
    ]
  }
}
```

Every citation is verified against the source text before the answer is returned—the `excerpts` are the verbatim passages the model used, so you can confirm accuracy without trusting the model alone. Use `freshness`, `country`, `language`, `include_domains`, `exclude_domains`, and `boost_domains` to steer results, same as the Web Search API.

[Full Answer API reference and all parameters](/docs/guides/answer)

## Try the Contents API

The Contents API fetches content from URLs you specify as clean Markdown or HTML—no browser automation, no HTML parsing. One use: pass your competitors' pricing page URLs to a daily job and feed the Markdown to an LLM to monitor what changed.

```python
from youdotcom import You
from youdotcom.models import ContentsFormats

with You() as you:
    pages = you.contents(
        urls=[
            "https://competitor-a.com/pricing",
            "https://competitor-b.com/pricing",
        ],
        formats=[ContentsFormats.MARKDOWN],
    )

    for page in pages:
        print(f"=== {page.title} ===")
        print(page.markdown)
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import { ContentsFormats } from "@youdotcom-oss/sdk/models";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const pages = await you.contents({
  urls: [
    "https://competitor-a.com/pricing",
    "https://competitor-b.com/pricing",
  ],
  formats: [ContentsFormats.Markdown],
});

for (const page of pages) {
  console.log(`=== ${page.title} ===`);
  console.log(page.markdown?.slice(0, 500));
}
```

```curl
curl -X POST https://ydc-index.io/v1/contents \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://competitor-a.com/pricing", "https://competitor-b.com/pricing"],
    "formats": ["markdown"]
  }'
```

Each URL comes back as a structured object:

```json maxLines=20
[
  {
    "url": "https://competitor-a.com/pricing",
    "title": "Pricing — Competitor A",
    "markdown": "# Pricing\n\n## Starter\n$49/month...",
    "metadata": {
      "site_name": "Competitor A",
      "favicon_url": "https://ydc-index.io/favicon?domain=competitor-a.com&size=128"
    }
  }
]
```

[Full Contents API reference and all parameters](/docs/guides/contents)

## Try the Research API

The Research API goes beyond a single web search. Give it a complex question and it runs multiple searches, reads through the sources, and synthesizes a thorough, citation-backed answer—so you don't have to. Control the depth with `research_effort` from `lite` to `frontier`.

```python
from youdotcom import You
from youdotcom.models import ResearchEffort

you = You()

res = you.research(
    input="What are the tradeoffs between microservices and monolithic architectures for high-traffic applications?",
    research_effort=ResearchEffort.STANDARD,
)

print(res.output.content[:500])
print(f"\nSources: {len(res.output.sources)}")
for source in res.output.sources:
    print(f"  - {source.title or 'Untitled'}: {source.url}")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import type { ResearchRequest } from "@youdotcom-oss/sdk/models/operations";
import { ResearchEffort } from "@youdotcom-oss/sdk/models/operations";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request: ResearchRequest = {
  input: "What are the tradeoffs between microservices and monolithic architectures for high-traffic applications?",
  researchEffort: ResearchEffort.Standard,
};

const result = await you.research(request);

console.log(result.output.content.slice(0, 500));
console.log(`\nSources: ${result.output.sources.length}`);
result.output.sources.forEach((s) => {
  console.log(`  - ${s.title ?? s.url}: ${s.url}`);
});
```

```curl
curl -X POST https://api.you.com/v1/research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What are the tradeoffs between microservices and monolithic architectures for high-traffic applications?",
    "research_effort": "standard"
  }'
```

The response includes a Markdown-formatted answer with inline citations and the list of sources used:

```json maxLines=20
{
  "output": {
    "content": "## Microservices vs Monolithic Architectures\n\nThe choice between microservices and monolithic architectures involves several key tradeoffs...\n\n### Scalability\nMicroservices allow independent scaling of individual components [[1, 3]]...",
    "content_type": "text",
    "sources": [
      {
        "url": "https://example.com/architecture-patterns",
        "title": "Architecture Patterns for High-Traffic Systems",
        "snippets": [
          "Microservices enable teams to scale individual services independently, reducing infrastructure costs for components with uneven load."
        ]
      }
    ]
  }
}
```

Use `research_effort` to control how deep the API digs—`lite` for quick answers, `standard` for a good balance, `deep` or `exhaustive` when thoroughness matters more than speed, or `frontier` for long-running deep research that requires [background mode](/docs/guides/research#background-mode). The Research API also supports `source_control` and `output_schema` for domain filtering and structured JSON output.

[Full Research API reference and all parameters](/docs/guides/research)

## Try the Finance Research API

The Finance Research API works just like the Research API—same request shape, same response shape—but it searches a finance-optimized index instead of the open web: SEC filings, equity prices, fundamentals, macro indicators, and financial news. Use it for earnings analysis, due diligence, and market research.

It accepts two parameters: `input` (your financial question) and `research_effort` (`deep` or `exhaustive`).

```python
from youdotcom import You
from youdotcom.models import FinanceResearchEffort

with You() as you:
    res = you.finance_research(
        input="What were the key drivers of NVIDIA's revenue growth in fiscal year 2025?",
        research_effort=FinanceResearchEffort.DEEP,
    )

    print(res.output.content[:500])
    print(f"\nSources: {len(res.output.sources)}")
    for source in res.output.sources:
        print(f"  - {source.title or 'Untitled'}: {source.url}")
```

```typescript
const response = await fetch("https://api.you.com/v1/finance_research", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    input: "What were the key drivers of NVIDIA's revenue growth in fiscal year 2025?",
    research_effort: "deep",
  }),
});

if (!response.ok) {
  throw new Error(`HTTP error: ${response.status}`);
}

const data = await response.json();

console.log(data.output.content.slice(0, 500));
console.log(`\nSources: ${data.output.sources.length}`);
(data.output.sources as { title?: string; url: string }[]).forEach((s) => {
  console.log(`  - ${s.title ?? "Untitled"}: ${s.url}`);
});
```

```curl
curl -X POST https://api.you.com/v1/finance_research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What were the key drivers of NVIDIA'\''s revenue growth in fiscal year 2025?",
    "research_effort": "deep"
  }'
```

The response is the same shape as the Research API—a Markdown answer with inline citations and a list of sources, but every source comes from the financial index:

```json maxLines=20
{
  "output": {
    "content": "For fiscal year 2025, NVIDIA's revenue rose to **$130.5 billion, up 114% year over year**.[[1]] The main driver was Data Center demand...",
    "content_type": "text",
    "sources": [
      {
        "url": "https://investor.nvidia.com/financial-info/financial-reports/default.aspx",
        "title": "NVIDIA Corporation - Financial Reports"
      }
    ]
  }
}
```

The Finance Research API does not support `source_control` or `output_schema`. If you need domain filtering or structured JSON output, use the [Research API](/docs/guides/research).

[Full Finance Research API reference and all parameters](/docs/guides/finance-research)

---

## Give Your Agent Access

Four ways to give your agent access to You.com, from zero-setup to installable skills.

1. **Read these docs in any agent.** Append `.md` to any page URL to get that page's full content as plain-text Markdown—for example, `you.com/docs/quickstart.md`. For a complete index of the documentation, use `you.com/docs/llms.txt`. Each section also has its own index—append `/llms.txt` to any section URL (for example, `you.com/docs/api-reference/llms.txt`).

2. **Search these docs from an agent with the Docs MCP server.** Point any MCP-enabled client at `https://you.com/docs/_mcp/server`—no API key—and your agent gets a `searchDocs` tool that returns relevant passages with source URLs. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup.

```json
{
  "mcpServers": {
    "fern_mcp_you-com-docs": {
      "url": "https://you.com/docs/_mcp/server"
    }
  }
}
```

3. **Call the You.com APIs from an agent with the You.com MCP server.** The hosted server gives your agent `you-search`, `you-contents`, `you-answer`, `you-research`, and `you-finance` against the live web. Connect without credentials to the free tier for `you-search` only (100 queries per day), or pass your API key for the full tool set. See the [MCP Server guide](/docs/build-with-agents/mcp-server) for IDE-specific setup.

```json
{
  "mcpServers": {
    "ydc-server": {
      "type": "http",
      "url": "https://api.you.com/mcp",
      "headers": {
        "Authorization": "Bearer <YDC_API_KEY>"
      }
    }
  }
}
```

For keyless `you-search`, use `https://api.you.com/mcp?profile=free`.

4. **Install Agent Skills for task-specific routing.** Skills are instruction packs that tell your agent which tool or API to reach for and how to use it—current web search, URL content extraction, cited research, finance research, and integration discovery. Install all of them with one command, or pick the ones you need.

```bash
npx skills add youdotcom-oss/agent-skills
```

See the [Agent Skills page](/docs/build-with-agents/skills) for the full list, platform plugins, and what each skill routes to.

---

## More Ways to Explore

### Explore the APIs Interactively

* [Web Search API playground](/docs/api-reference/search/v1-search?explorer=true)
* [Answer API playground](/docs/api-reference/answer/v1-answer?explorer=true)
* [Contents API playground](/docs/api-reference/contents?explorer=true)
* [Research API playground](/docs/api-reference/research/v1-research?explorer=true)
* [Finance Research API playground](/docs/api-reference/finance-research/v1-finance_research?explorer=true)

### Use the SDKs

Ergonomic, typed access to our APIs. The Python SDK covers Web Search, Answer, Contents, Research, and Finance Research. The TypeScript SDK covers Web Search, Contents, and Research.

* [Python SDK](/docs/sdks/python-sdk)
* [TypeScript SDK](/docs/sdks/typescript-sdk)

### Try in Postman

Fork one of our pre-built collections, add your API key to the `production` environment, and send your first request without writing code.

#### [Web Search API](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-83118dc1-7279-49f6-893d-4c18b8163008)

#### [Research API](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-b2f6290f-99e7-46e0-9a73-1e5fcd0e81a3)

#### [Contents API](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-037d5564-c4b5-4e11-9cea-1e41a5eba4aa)

#### [Finance Research API](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-08727c0f-48d4-4a47-bf44-1841fbe13b03)

---

## Evaluate You.com

You.com provides an [open-source evaluation framework](https://github.com/youdotcom-oss/web-search-api-evals) and a reproducible methodology for [benchmarking search APIs](https://you.com/resources/the-you-dot-com-web-search-eval-harness)—so you can measure what actually matters: accuracy, latency, and information retrieval quality.

We're the only search API provider with peer-reviewed evaluation research. Our methodology was presented at the Association for the Advancement of Artificial Intelligence (AAAI) 2026 conference and received the Best Paper Award. Read the research:

1. [Stochasticity in Agentic Evaluations: Quantifying Inconsistency with Intraclass Correlation](https://arxiv.org/abs/2512.06710)
2. [Randomness in AI Benchmarks: What Makes an Eval Trustworthy?](https://you.com/resources/randomness-in-ai-benchmarks)

When starting your own evaluation, keep it simple: run `count=10` with no filters on a representative query set, then layer in full page extraction if snippets aren't providing enough context.

* [How to Evaluate the Web Search API](/docs/guides/evaluate-us)—methodology, dataset recommendations (SimpleQA, FRAMES, FreshQA), latency benchmarking, and a production checklist
* [Agentic Web Search Playoffs](https://github.com/youdotcom-oss/agentic-web-search-playoffs)—open-source benchmark comparing web search providers in agentic workflows

Our team can also design and run custom benchmarks tailored to your domain and quality bar. [Talk to us](https://you.com/book-a-demo)

---

## Use Cases

Ready-to-run sample apps built on You.com APIs. Each comes with a live demo and a fully forkable open-source GitHub repo—clone it, extend it, or use it as a starting point for your own project.

#### [Simple Search](/docs/examples/simple-search)

Runs a web search and returns the top results.

#### [Deep Search](/docs/examples/deep-search)

Multi-pass query expansion that surfaces sources a single search would miss.

#### [Contents Extraction](/docs/examples/contents)

Pull clean Markdown or HTML from any URL—ideal for LLM ingestion.

#### [Research Agent](/docs/examples/research)

A multi-step agent that plans, searches, reads, and writes a cited report.

---

## Pricing

You.com uses pay-as-you-go pricing based on the API and usage. All new accounts include **\$100 in free credits**. See the [Billing page](/docs/administration/billing) for complete pricing across all APIs.

### Quick Pricing Overview

* **Web Search API**: \$5.00 per 1,000 calls (up to 100 results per call)
* **Web Search API full page extraction add-on**: \$1.00 per 1,000 pages
* **Contents API**: \$1.00 per 1,000 pages
* **Answer API**: \$5.00 per 1,000 calls
* **Research API**: Starts at \$12 per 1,000 calls (varies per effort tier)
* **Finance Research API**: Starts at \$110 per 1,000 calls (`deep`)—\$500 per 1,000 calls (`exhaustive`)

Track your usage and spending from the [analytics dashboard](https://you.com/platform/analytics). For volume discounts, annual pricing, and enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).