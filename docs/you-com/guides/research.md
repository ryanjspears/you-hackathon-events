> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Research API Overview

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

---

## What Is the Research API?

The Research API returns grounded, natural language answers to questions of varying complexity.
It runs multiple searches, processes the results, cross-references sources, and synthesizes everything into a thorough, Markdown-formatted answer with inline citations.
When you need a typed response, you can also get structured JSON by defining an `output_schema`.

Ask a hard question, get a researched answer with sources.

---

## How It's Different From Search

The Web Search API and the Research API serve different purposes by delivering different outputs:

|                | Web Search API                                                      | Research API                                                                                   |
| -------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Input**      | Query, several search parameters (count, language, extraction etc.) | Query, research effort, source controls, optional output schema                                |
| **You get**    | Raw search results (URLs, snippets, metadata)                       | A natural language answer or structured JSON object with inline citations, plus search results |
| **Processing** | Returns results as-is for you to process                            | Reads, reasons over, and synthesizes results for you                                           |
| **Speed**      | Fast—single search round trip                                       | Varies—multiple searches and reasoning steps                                                   |
| **Control**    | Full control over how results are used                              | Control depth, sources, recency, geography, and response shape                                 |
| **Best for**   | RAG pipelines, building your own search UI, data gathering          | Answering questions of varying complexity using multiple sources                               |

Use the Web Search API when you want raw results to feed into your own pipeline. Use the Research API when you want a ready-to-use answer backed by sources.

---

## How It Works

Research operates as an agentic system that autonomously plans and executes a multi-step research strategy for your question.

### Search, Contents, and Live News as retrieval primitives

Research uses You.com's Search, Contents, and Live News APIs as its core tools.
Rather than firing generic web queries, the system selects the right tool for each sub-question—search for discovery, contents for deep page reads, live news for time-sensitive information, and several other internal tools to aid in generating the best possible answer.
This targeted tool selection reduces wasted calls and gives the reasoning model cleaner inputs at each step.

The system also evaluates retrieved sources for freshness, diversity, and relevance before incorporating them into the answer.

### Context management at scale

Deep research generates far more information than any single LLM context window can hold. Research uses context-masking and compaction strategies that let it operate well beyond those limits—maintaining coherent reasoning across hundreds or thousands of turns without losing track of what it found, what it verified, and what remains unresolved.

At higher effort levels, a single query can run more than 1,000 reasoning turns and process up to 10 million tokens.

### Budget-based planning

The system receives a compute budget determined by the `research_effort` tier you choose. It plans its approach around that budget, allocating more effort to verifying ambiguous or high-stakes claims and moving quickly through well-sourced facts. This is the mechanism that enables the range of latency, accuracy, and cost tradeoffs across tiers.

---

## What You Get

Every Research API response includes:

* **`content`**: A Markdown-formatted answer by default, or a JSON object when you provide `output_schema`. Inline citations such as `[[1, 2]]` reference items in the `sources` array.
* **`content_type`**: The format of the content field. `text` is returned for default Markdown responses. `object` is returned for structured output.
* **`sources`**: The web pages the API read and cited in the answer—each with a URL, title, and relevant snippets.

```json maxLines=25
{
  "output": {
    "content": "## RISC-V vs ARM: Key Architectural Differences\n\nRISC-V and ARM are both reduced instruction set architectures, but they differ in licensing, extensibility, and ecosystem maturity [[1, 2]].\n\n### Licensing\nARM requires per-chip licensing fees, while RISC-V is open-source and royalty-free [[1, 3]]...",
    "content_type": "text",
    "sources": [
      {
        "url": "https://example.com/risc-v-vs-arm",
        "title": "RISC-V vs ARM: A Technical Comparison",
        "snippets": [
          "RISC-V's open ISA allows custom extensions without licensing negotiations, making it attractive for specialized hardware."
        ]
      },
      {
        "url": "https://example.com/processor-architectures",
        "title": "Modern Processor Architectures Explained",
        "snippets": [
          "ARM's mature ecosystem includes extensive tooling and vendor support built over three decades."
        ]
      }
    ]
  }
}
```

---

## Key Features

### Research effort levels

The `research_effort` parameter controls how much compute the API allocates to your question. Higher effort means more searches, deeper source reading, and more cross-referencing—at the cost of longer response times.

| Level        | Price per 1k | Latency                                 | Use case                                                       |
| ------------ | ------------ | --------------------------------------- | -------------------------------------------------------------- |
| `lite`       | \$12         | \< 10s                                  | Quick factual lookups, simple searches                         |
| `standard`   | \$50         | \~10–30s                                | Balanced depth for most production use (default)               |
| `deep`       | \$100        | \< 120s                                 | Complex multi-source research and synthesis                    |
| `exhaustive` | \$450        | \< 300s                                 | Comprehensive analysis across dozens of sources                |
| `frontier`   | \$1,200      | Background only. 30s–12000s (p50: 300s) | Long-running deep research tasks. Requires `background: true`. |

For the same query, the difference between tiers is substantial. Here's an abridged comparison for the question *"Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?"*:

#### research\_effort = standard

```json maxLines=40 wordWrap
{
  "output": {
    "content": "Global assessments show that the largest recent urban air-quality improvements are concentrated in East China, parts of the eastern United States, Europe, and Japan, with especially strong gains in Chinese megacities and cities with aggressive traffic-emissions controls such as London [[1, 2, 3]].\n\n1) Beijing (China) — PM2.5 fell from ~89–90 µg/m³ in 2013 to ~58 µg/m³ in 2017 (about 35–36% in five years), with evidence from both satellite and surface observations [[4, 5]].\nKey drivers included coal phase-down, industrial controls, stricter vehicle/fuel standards, and regional enforcement [[6, 7, 8]].\n\n2) Chinese city clusters (BTH / YRD / PRD) — China's population-weighted PM2.5 fell ~32% from 2013–2017, with the largest modeled decline in Beijing–Tianjin–Hebei (~38%); across 367 cities, observed PM2.5 fell ~44% from 2013–2019 [[9, 10]].\nThe main drivers were national clean-air action plans, coal controls, industrial restructuring, and transport emissions standards [[7, 9, 10]].\n\n3) London (UK) — London achieved major NO2 reductions linked to LEZ/ULEZ policies, with monitoring and modeling studies showing accelerated declines after ULEZ implementation and meaningful reductions versus no-ULEZ scenarios [[11, 12, 13, 14]].",
    "content_type": "text",
    "sources": [
      {
        "url": "https://pubmed.ncbi.nlm.nih.gov/36356738/",
        "title": "Trends in urban air pollution over the last two decades: A global perspective - PubMed",
        "snippets": [
          "At global scale, PM2.5 exposures declined slightly from 2000 to 2019 ... Improvements were observed in the Eastern US, Europe, Southeast China, and Japan..."
        ]
      }
    ]
  }
}
```

#### research\_effort = exhaustive

```json maxLines=40 wordWrap
{
  "output": {
    "content": "There is no single definitive \"top 10\" ranking, but several independent datasets and case studies point to a small group of cities — especially in China plus a few in Europe and North America — that have seen the largest, clearly measured air-quality gains in roughly the last decade. Below are the clearest examples where both (1) large, quantified reductions in PM2.5 or NO2 are documented and (2) specific policies can be tied to those improvements.\n\n1) Beijing (and other major Chinese cities)\nBeijing shows one of the strongest documented improvements globally. Annual mean PM2.5 fell from roughly 89–102 µg/m³ in 2013 to about 32–39 µg/m³ by 2023, implying an approximately 60–65% reduction over about a decade [[1, 2, 3, 4]]. National analyses also show large PM2.5 declines across hundreds of Chinese cities, and EPIC/AQLI attributes a major share of global PM2.5 reduction since 2013 to China's air-quality policies [[5, 6, 7]].\nThe key drivers were policy-led and multi-sector: coal-to-clean energy transition, coal boiler controls, industrial restructuring, tighter emissions standards, vehicle standards and scrappage, fuel quality improvements, and regional coordination across Beijing–Tianjin–Hebei [[8, 9, 10, 11, 12, 13]]. Atmospheric modeling indicates most of Beijing's 2013–2017 PM2.5 improvement was due to emissions reductions rather than weather variation [[2, 8]].\n\n2) Seoul metropolitan area (Seoul, Incheon, Gyeonggi)\nThe Seoul metropolitan region shows strong evidence of long-term emissions reductions tied to policy. Joint Seoul/UNEP assessments report very large reductions in fine particulate emissions (including about a 75% reduction in Seoul's emitted PM2.5 mass and substantial reductions in Gyeonggi) over 2005–2020 [[14]]. Additional studies indicate stricter vehicle-emissions regulations contributed to lower particulate concentrations in the 2010s compared with the 2000s [[15]], while UNEP reports national PM2.5 emissions declines with even greater reductions in Seoul and Gyeonggi [[16]].\nKey actions included tightening vehicle standards, replacing diesel buses with CNG buses, incentivizing after-treatment systems and cleaner vehicles, emissions-cap regulation and trading in the Seoul metropolitan area, fuel switching, and stronger industrial controls [[15, 17, 18, 19]]. Seoul still experiences episodic pollution due in part to transboundary transport, especially from upwind regions [[20, 21, 22]].\n\n3) London (ULEZ, LEZ, congestion charging)...",
    "content_type": "text",
    "sources": [
      {
        "url": "https://sustainablemobility.iclei.org/air-pollution-beijing/",
        "title": "Clearing the skies: how Beijing tackled air pollution & what lies ahead - ICLEI Sustainable Mobility",
        "snippets": [
          "China played a vital role, accounting for three-quarters of global air pollution reductions from 2013-2020...",
          "The annual average PM2.5 concentrations ... decreased..."
        ]
      }
    ]
  }
}
```

The `exhaustive` response identifies additional cities (Seoul, with specific UNEP data), includes more granular measurements (µg/m³ ranges, percentage reductions over specific date ranges), and cross-references more sources to verify claims.

### Citation-backed answers

Every claim in the response links back to a specific source via inline citations. Your users (or your system) can verify any statement by following the numbered references to the `sources` array.

### Markdown output

The `content` field is formatted in Markdown with headers, lists, and inline citations—ready to render in a UI or feed into downstream processing.

### Source Control

`source_control` lets you constrain which web sources the research agent searches and visits. Use it when you want results from trusted domains only, need to block specific sites, want recent content, or need results focused on a specific country.

`source_control` is a top-level request field alongside `input` and `research_effort`.

| Field             | Type       | Description                                                                                                                                                                                                                                                            |
| ----------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `include_domains` | `string[]` | Only return results from these domains. Max 500 domains. Cannot be used with `exclude_domains` or `boost_domains`.                                                                                                                                                     |
| `exclude_domains` | `string[]` | Never return results from these domains. Max 500 domains. Also blocks the research agent from visiting pages on those domains during browsing.                                                                                                                         |
| `boost_domains`   | `string[]` | Boost results from these domains without excluding other domains. Max 500 domains. Cannot be used with `include_domains`. Boosted domains are not guaranteed to appear in the final answer—the research agent may still select other sources if they are a better fit. |
| `freshness`       | `string`   | Filter results by recency. Accepts `day`, `week`, `month`, `year`, or a custom date range in `YYYY-MM-DDtoYYYY-MM-DD` format.                                                                                                                                          |
| `country`         | `string`   | ISO 3166-1 alpha-2 country code, such as `US`, `GB`, or `DE`, to geographically focus web results.                                                                                                                                                                     |

`include_domains` and `exclude_domains` cannot be used together in the same request. `boost_domains` can be combined with `exclude_domains`, but not with `include_domains`.

```curl
curl -X POST https://api.you.com/v1/research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What are the latest developments in quantum computing?",
    "research_effort": "deep",
    "source_control": {
      "include_domains": ["nature.com", "arxiv.org", "science.org"]
    }
  }'
```

You can also combine filters:

```curl
curl -X POST https://api.you.com/v1/research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "New fintech regulations",
    "research_effort": "standard",
    "source_control": {
      "country": "GB",
      "freshness": "2026-01-01to2026-04-01"
    }
  }'
```

### Structured Output

Use `output_schema` when you want `output.content` returned as a JSON object instead of free-form text. This is useful for returning predictable fields, extracting entities, or feeding Research API output into another typed system.

`output_schema` is supported with `standard`, `deep`, `exhaustive`, and `frontier` research effort. It is not supported with `lite`. Sending `output_schema` with `research_effort: "lite"` returns `422`.

```curl
curl -X POST https://api.you.com/v1/research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What are OpenAI structured output schema constraints?",
    "research_effort": "standard",
    "output_schema": {
      "type": "object",
      "properties": {
        "summary": {
          "type": "string"
        },
        "verdict": {
          "type": "string",
          "enum": ["supported", "mixed", "unsupported"]
        }
      },
      "required": ["summary", "verdict"],
      "additionalProperties": false
    }
  }'
```

When `output_schema` is provided, the structured result is returned in `output.content` and `output.content_type` is `object`. Sources remain in `output.sources`. The API does not add citation fields into your schema object automatically.

```json maxLines=25
{
  "output": {
    "content": {
      "summary": "The schema must be object-rooted and require all declared properties.",
      "verdict": "supported"
    },
    "content_type": "object",
    "sources": []
  }
}
```

#### Schema Rules

`output_schema` follows a narrow JSON Schema subset designed for reliable structured generation.

Required rules:

* The root must be an object.
* The root must not use top-level `anyOf`.
* Every object must define `properties`.
* Every object must set `additionalProperties: false`.
* Every property must be listed in `required`. To make a field optional, keep it in `required` and make it nullable—see [Optional and nullable fields](#optional-and-nullable-fields).
* Recursive schemas are not supported.
* A property's type must not be a bare `{"type": "null"}`. Use a nullable union such as `{"type": ["string", "null"]}` instead.

Supported patterns include nested objects, arrays, enums, nested `anyOf`, and non-recursive `$defs` and `$ref`.

Unsupported keywords:

* `allOf`
* `contains`
* `not`
* `dependentRequired`
* `dependentSchemas`
* `format`
* `if` / `then` / `else`
* `maxContains` / `minContains`
* `maxItems` / `minItems`
* `maxLength` / `minLength`
* `maxProperties` / `minProperties`
* `maximum` / `minimum`
* `multipleOf`
* `pattern`
* `patternProperties`
* `propertyNames`
* `unevaluatedItems` / `unevaluatedProperties`
* `uniqueItems`

Selected limits:

| Limit                                      | Value  |
| ------------------------------------------ | ------ |
| Max nesting depth                          | 5      |
| Max total properties                       | 100    |
| Max total enum values                      | 500    |
| Max large-enum string budget (>250 values) | 7,500  |
| Max total schema string budget             | 25,000 |

If the schema is invalid, the request fails validation before model execution. The schema string budget counts property names, `$defs` names, enum values, and `const` values. It applies to schema shape only. Request-level limits such as total task spec size are enforced separately at the request layer.

There is no separate raw byte-size limit on the schema. What matters is the **25,000-character string budget**, which counts only property names, `$defs` names, `enum` values, and `const` values—not structural JSON (`{}`, `"type"`, whitespace). A 30 KB schema file can still pass if its counted strings stay under budget—a much smaller file can fail if it has many long enum values.

A schema is rejected with `422` **before any model execution** if it exceeds any limit above (depth, property count, enum count, or string budget) or violates a [Schema Rule](#schema-rules). The error message names the specific limit or rule.

#### Optional and Nullable Fields

Every property you declare must appear in `required`. This is what makes structured generation reliable—the model always emits every field—and it matches OpenAI Structured Outputs.

To express a value that **may be unknown or not applicable**, keep the field in `required` but make its type **nullable** by adding `"null"`. The model returns `null` when the value isn't available instead of guessing.

Use the concise form (equivalent to `string | null`):

```json
"gtin": { "type": ["string", "null"] }
```

An `anyOf` spelling is also valid but more verbose—prefer the concise form above:

```json
"gtin": { "anyOf": [{ "type": "string" }, { "type": "null" }] }
```

A property's type may **not** be a bare `{"type": "null"}` (a field that can only ever be null). Make the field nullable instead, as shown above. A `null` branch *inside* an `anyOf` is fine.

Omitting a field from `required` produces an invalid schema—the request fails validation before execution. Nullability is the only mechanism for "may be absent."

**Response behavior**

* A nullable field with no available value is returned as `null`.
* A non-nullable required field with no available value forces the model to emit something anyway (typically an empty string `""` for strings). Required fields are **never omitted** from the response, and the model does not fabricate a citation-backed value to fill them. If a field can legitimately be unknown, make it nullable so you get a clean `null` instead of `""`.

**Example**

```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "gtin": { "type": ["string", "null"] }
  },
  "required": ["name", "gtin"],
  "additionalProperties": false
}
```

#### Conditional Structure

Conditional keywords (`if` / `then` / `else`, `dependentRequired`, `dependentSchemas`) are not supported. To express "field Y is required only when X"—for example, `price_usd` is required only when `in_stock` is `true`—model the object as a **discriminated `anyOf` union**: one branch per case, with a shared field pinned to a distinct value via `enum`.

```json
{
  "type": "object",
  "properties": {
    "product": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "in_stock":  { "type": "boolean", "enum": [true] },
            "name":      { "type": "string" },
            "price_usd": { "type": ["number", "null"] }
          },
          "required": ["in_stock", "name", "price_usd"],
          "additionalProperties": false
        },
        {
          "type": "object",
          "properties": { "in_stock": { "type": "boolean", "enum": [false] } },
          "required": ["in_stock"],
          "additionalProperties": false
        }
      ]
    }
  },
  "required": ["product"],
  "additionalProperties": false
}
```

When `in_stock` is `true`, `name` is required—when `false`, only `in_stock` is allowed. This is the same pattern OpenAI Structured Outputs uses, so one schema works across both.

`anyOf` may not be used at the schema root—nest the union under a property (or array `items`), as shown above.

### Using Source Control and Structured Output Together

`source_control` and `output_schema` can be combined in a single request. For example, you can restrict research to specific domains while requesting a structured response:

```curl
curl -X POST https://api.you.com/v1/research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What are the FDA-approved GLP-1 receptor agonists and their indications?",
    "research_effort": "deep",
    "source_control": {
      "include_domains": ["fda.gov", "nih.gov", "pubmed.ncbi.nlm.nih.gov"],
      "freshness": "year"
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "drugs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "brand_name": { "type": "string" },
              "generic_name": { "type": "string" },
              "manufacturer": { "type": "string" },
              "approved_indications": {
                "type": "array",
                "items": { "type": "string" }
              },
              "approval_year": { "type": "string" }
            },
            "required": ["brand_name", "generic_name", "manufacturer", "approved_indications", "approval_year"],
            "additionalProperties": false
          }
        },
        "summary": { "type": "string" }
      },
      "required": ["drugs", "summary"],
      "additionalProperties": false
    }
  }'
```

### Background Mode

By default, `POST /v1/research` runs synchronously and blocks until the final answer is ready. For complex research at `deep` or `exhaustive` effort, that can exceed client-side timeouts or tie up a worker. Set `background: true` to run the request asynchronously and receive a task handle immediately. The `frontier` effort level requires background mode—synchronous requests with `research_effort: "frontier"` return `422`.

| Field        | Type      | Default | Description                                                                                           |
| :----------- | :-------- | :------ | :---------------------------------------------------------------------------------------------------- |
| `background` | `boolean` | `false` | When `true`, queues the request as a task and returns a handle immediately instead of waiting inline. |

In background mode, the response is a task object rather than the research result:

```json
{
  "task_id": "f1e2d3c4-0000-0000-0000-000000000000",
  "type": "research",
  "status": "queued",
  "stream_url": "/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream",
  "created_at": "2026-06-26T00:00:00Z"
}
```

A task moves through the following states: `queued` → `running` → `completed` | `failed` | `cancelled`.

#### Poll for the Result

Call `GET /v1/research/{task_id}` to check status. The `result` field is `null` until the task completes. If the task fails, `status` is `failed` and `error` contains a diagnostic message.

```curl
curl "https://api.you.com/v1/research/{task_id}" \
  -H "X-API-Key: $YDC_API_KEY"
```

#### Stream Progress

`GET /v1/research/{task_id}/stream` returns Server-Sent Events (SSE) with real-time progress. The stream starts with a `connected` event and closes when the task reaches a terminal status. Use `?from_id=N` to replay events after reconnecting. Once the stream closes, poll `GET /v1/research/{task_id}` to retrieve the full `result`.

```curl
curl "https://api.you.com/v1/research/{task_id}/stream" \
  -H "X-API-Key: $YDC_API_KEY"
```

#### End-to-End Python Example

The Python SDK ships helpers for background tasks in `youdotcom.research_helpers`, so you do not have to write the submit-and-poll loop yourself. `research_and_wait()` submits the task, polls until it reaches a terminal status, and raises if it fails or times out.

```python
from youdotcom import You
from youdotcom.models import ResearchEffort
from youdotcom.research_helpers import research_and_wait

with You() as you:
    task = research_and_wait(
        you,
        input="Are 'Acme Logistics LLC' (Delaware) and 'Acme Logistics' (Newark, NJ) the same business?",
        research_effort=ResearchEffort.FRONTIER,
        output_schema={
            "type": "object",
            "properties": {
                "same_entity": {"type": "boolean"},
                "confidence": {"type": "number"},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["same_entity", "confidence", "evidence"],
            "additionalProperties": False,
        },
        timeout_s=600,
    )

    verdict = task.result.output["content"]
    print(f"Same entity: {verdict['same_entity']} (confidence: {verdict['confidence']})")
```

To submit and poll as separate steps—for example, when the task handle is stored and picked up by another worker—use `research_background()` and `poll_research_task()`:

```python
from youdotcom import You
from youdotcom.models import ResearchEffort
from youdotcom.research_helpers import poll_research_task, research_background

with You() as you:
    handle = research_background(
        you,
        input="Which global cities improved air quality the most over the past 10 years?",
        research_effort=ResearchEffort.FRONTIER,
    )
    print(f"Queued {handle.task_id}, stream at {handle.stream_url}")

    # ... later, in the same process or another one
    task = poll_research_task(you, handle.task_id, interval_s=5, timeout_s=600)
    print(task.status)
    print(task.result.output["content"])
```

To follow progress as it happens, `stream_research()` yields the Server-Sent Events described above. Each event carries an `id`, an `event` name, and a `data` payload, and unknown event names pass through rather than raising, so new event types will not break your consumer.

```python
from youdotcom import You
from youdotcom.research_helpers import research_background, stream_research

with You() as you:
    handle = research_background(you, input="Summarize the 2025 EU AI Act implementation timeline")

    for event in stream_research(you, handle.task_id):
        print(f"[{event.id}] {event.event}: {event.data}")

    # The stream closes at a terminal status; fetch the full result afterwards
    task = you.get_research_task(task_id=handle.task_id)
    print(task.result.output["content"])
```

---

## Quickstart

```python maxLines=0
from youdotcom import You
from youdotcom.models import ResearchEffort

you = You()

res = you.research(
    input="Top 5 EV-selling companies worldwide in 2025 so far",
    research_effort=ResearchEffort.STANDARD,
)

# The complete, natural language answer to your query
print(res.output.content)

# Dive into the source data (title, URL and text snippets)
for i, source in enumerate(res.output.sources, 1):
    print(f"[{i}] {source.title or 'Untitled'}: {source.url}")
```

```typescript
import { You } from "@youdotcom-oss/sdk";
import type { ResearchRequest } from "@youdotcom-oss/sdk/models/operations";
import { ResearchEffort } from "@youdotcom-oss/sdk/models/operations";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request: ResearchRequest = {
  input: "Top 5 EV-selling companies worldwide in 2025 so far",
  researchEffort: ResearchEffort.Standard,
};

const result = await you.research(request);

// The complete, natural language answer to your query
console.log(result.output.content);

// Dive into the source data (title, URL and text snippets)
result.output.sources.forEach((s, i) => {
  console.log(`[${i + 1}] ${s.title ?? s.url}: ${s.url}`);
});
```

```curl
curl -X POST https://api.you.com/v1/research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Top 5 EV-selling companies worldwide in 2025 so far",
    "research_effort": "standard"
  }'
```

#### [Try in Postman](https://www.postman.com/youdotcom/you-com-api-workspace/collection/46015159-b2f6290f-99e7-46e0-9a73-1e5fcd0e81a3)

Fork the Research API collection, add your API key to the `production` environment, and hit Send.

---

## Parameters

| Parameter         | Type    | Required | Description                                                                                                           |
| ----------------- | ------- | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `input`           | string  | Yes      | The research question (max 40,000 characters)                                                                         |
| `research_effort` | string  | No       | Depth of research: `lite`, `standard` (default), `deep`, `exhaustive`, `frontier`                                     |
| `source_control`  | object  | No       | Beta. Controls which sources the research agent can use through domain, freshness, and country filters.               |
| `output_schema`   | object  | No       | Beta. Requests structured JSON output that follows a supported JSON Schema subset. Not available with `lite`.         |
| `background`      | boolean | No       | When `true`, runs the request asynchronously and returns a task handle. Poll or stream the task for the final result. |

[View full API reference](/docs/api-reference/research/v1-research)

---

## Common Use Cases

### Complex question answering

When a question can't be answered from a single source—comparative analyses, multi-factor evaluations, questions that span multiple domains—the Research API handles the synthesis for you.

***"Compare the pricing models of the top 3 vector databases and their tradeoffs for a 10M-document collection"***

### Due diligence and market research

Quickly gather verified, cited information about companies, markets, or technologies. The citation-backed output gives you traceability that raw LLM generation can't.

### Internal tools and knowledge assistants

Build internal research tools where employees can ask complex questions and get sourced answers—product comparisons, regulatory summaries, technical deep dives—without manually reading dozens of pages.

### Content creation pipelines

Use the Research API as the first step in a content pipeline: ask a research question, get a cited draft, then use it as source material for blog posts, reports, or briefings.

---

## Best Practices

### Match research effort to the question

Don't use `exhaustive` or `frontier` for simple factual questions—`lite` or `standard` will be faster and cheaper. Save `deep`, `exhaustive`, and `frontier` for questions where thoroughness and accuracy justify the longer response time.

### Verify citations for high-stakes use cases

The inline citations make verification straightforward. For legal, financial, or medical contexts, build a step that follows citation URLs to confirm claims before surfacing them to end users.

### Use structured inputs for better results

The `input` field supports up to 40,000 characters. For complex research tasks, include context, constraints, or specific angles you want covered. A well-scoped question produces a more focused answer.

### Use Background Mode for Long-Running Tasks

For `deep` or `exhaustive` research that may exceed client-side timeouts, set `background: true` to queue the request and poll or stream for the result. This decouples submission from retrieval and keeps workers responsive when research takes minutes rather than seconds. The `frontier` effort level requires background mode.

---

## Pricing

Research API pricing is tiered by effort level. All new accounts receive \$100 in free credits to get started. See the [Billing page](/docs/administration/billing#research-api) for complete pricing and latency by tier.

Higher effort tiers allocate more compute for deeper reasoning, more source verification, and higher accuracy. See the [research effort levels table](#research-effort-levels) above for how each tier performs.

For volume discounts, annual pricing, or enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).

---

## Try It

#### [Research Agent template](/docs/examples/research)

See a working agent that plans, searches, reads, and writes a cited report.

---

## Next Steps

#### [API Reference](/docs/api-reference/research/v1-research)

Full parameter reference, request/response schemas and interactive playground

#### [Try the Web Search API](/docs/guides/search)

Get raw search results for your own pipelines instead of synthesized answers

#### [Quickstart](/docs/quickstart)

Get your API key and try all our APIs in under five minutes