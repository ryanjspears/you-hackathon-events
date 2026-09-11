> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# n8n

[n8n](https://n8n.io) is a workflow automation platform that lets you connect APIs, build agents, and automate tasks with a visual editor or code. The You.com n8n node brings six operations—web search, content extraction, answer synthesis, research, finance research, and background task management—directly into your n8n workflows, so you can ground AI agents in fresh web data or pipe results into any downstream step.

The [`@youdotcom-oss/n8n-nodes-youdotcom`](https://www.npmjs.com/package/@youdotcom-oss/n8n-nodes-youdotcom) package provides a single node with six operations: **Search**, **Get Contents**, **Answer**, **Research**, **Finance Research**, and **Get Research Task**. It also works as an AI agent tool, so n8n's built-in AI agents can call You.com search on demand.

---

## Getting Started

### Add the Node

In an n8n workflow, hit `+` to add a step and search for **You.com**. Drag the **You.com** node onto the canvas to start a workflow.

### Set Up Credentials

1. In n8n, go to **Credentials > New Credential** and select **You.com API**
2. Paste your API key from [you.com/platform](https://you.com/platform)
3. Click **Test** to verify the key works

---

## Operations

#### Search

Search the web with the You.com Web Search API. Sends a POST request with a JSON body and returns structured results with titles, URLs, descriptions, and snippets.

**Required**: `query` (the search query)

**Optional parameters**:

| Parameter         | Description                                | Values                                                                       |
| ----------------- | ------------------------------------------ | ---------------------------------------------------------------------------- |
| `count`           | Max results per section                    | 1–100 (default: 10)                                                          |
| `country`         | Geographical focus                         | 36 country codes (US, GB, DE, FR, etc.)                                      |
| `freshness`       | Recency filter                             | `day`, `week`, `month`, `year`, or `YYYY-MM-DDtoYYYY-MM-DD` (via Expression) |
| `safesearch`      | Content moderation                         | `off`, `moderate`, or `strict` (default: `moderate`)                         |
| `language`        | Result language                            | BCP 47 codes (default: `EN`)                                                 |
| `offset`          | Pagination offset                          | 0–9 (default: 0)                                                             |
| `crawl_timeout`   | Crawl timeout in seconds                   | 1–60 (default: 10); omitted when Extraction Mode is Highlights               |
| `include_domains` | Restrict results to these domains          | Multi-string input, up to 500 domains                                        |
| `exclude_domains` | Exclude results from these domains         | Multi-string input, up to 500 domains                                        |
| `boost_domains`   | Prioritize results from these domains      | Multi-string input, up to 500 domains                                        |
| `extraction`      | Extract content inline with search results | Collection: see below                                                        |

**Domain filters**: Include Domains cannot combine with Exclude Domains or Boost Domains—either pairing returns a 422 at execution time. Exclude Domains and Boost Domains may be combined freely.

**Extraction collection**: Set `extraction_mode` to `highlights` (inline snippets) or `full_page` (full page content). When `full_page` is selected, a sub-collection exposes `extraction_formats` (markdown or html). When Extraction Mode is Highlights, `crawl_timeout` is omitted from the request body.

**Deprecated parameters**: `livecrawl` and `livecrawl_formats` are accepted but deprecated in favor of the `extraction` collection and will not receive further development.

#### Get Contents

Fetch and extract clean content from web pages using the You.com Contents API.

**Required**: `urls` (one or more URLs, with the + button for multi-input; comma-separated paste also accepted)

**Optional parameters**:

| Parameter       | Description                          | Values                                                                                               |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| `formats`       | Output formats                       | `markdown`, `html`, `metadata` (default: `markdown`)                                                 |
| `crawl_timeout` | Crawl timeout in seconds             | 1–60 (default: 10)                                                                                   |
| `max_age`       | Max age of cached content in seconds | 0 or greater (default: 0; set above 0 to enforce a freshness threshold, leave at 0 for no age limit) |

Returns cleaned page content in your chosen format, plus metadata (JSON-LD, OpenGraph, Twitter Cards) when requested.

#### Answer

Get a synthesized answer with citations using the You.com Answer API. Sends a POST request and returns a natural-language answer grounded in real-time web results.

**Required**: `query` (max 400 characters; search operators are not supported)

**Optional parameters**:

| Parameter         | Description                           | Values                                                                       |
| ----------------- | ------------------------------------- | ---------------------------------------------------------------------------- |
| `freshness`       | Recency filter                        | `day`, `week`, `month`, `year`, or `YYYY-MM-DDtoYYYY-MM-DD` (via Expression) |
| `country`         | Geographical focus                    | 36 country codes (dropdown)                                                  |
| `safesearch`      | Content moderation                    | `off`, `moderate`, or `strict`                                               |
| `language`        | Result language                       | BCP 47 codes (dropdown)                                                      |
| `include_domains` | Restrict results to these domains     | Multi-string input                                                           |
| `exclude_domains` | Exclude results from these domains    | Multi-string input                                                           |
| `boost_domains`   | Prioritize results from these domains | Multi-string input                                                           |

Returns an `answer` string with inline citation references, a `citations` array, and the supporting `results`.

#### Research

Run multi-step research using the You.com Research API. Sends a POST request and returns a cited, synthesized answer.

**Required**: `input` (the research question, max 40,000 characters)

**Optional parameters**:

| Parameter        | Description                                                 | Values                                                                                                |
| ---------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `researchEffort` | Depth of research                                           | `lite`, `standard`, `deep`, `exhaustive`, or `frontier` (default: `standard`)                         |
| `background`     | Queue the task and return a handle immediately              | Boolean (default: `false`)                                                                            |
| `source_control` | Domain filters, freshness, and country for source selection | Collection: see below                                                                                 |
| `output_schema`  | JSON Schema for structured output                           | JSON string (supported with standard, deep, exhaustive, and frontier effort; not supported with lite) |

**Research effort**: `frontier` requires `background` mode. If set without background, the node throws an error at execution time.

**Source control collection**: Includes `include_domains`, `exclude_domains`, `boost_domains` (with the same mutual exclusion rules as Search), plus `freshness` (day, week, month, year, or a custom date range via Expression) and `country` (dropdown of 36 country codes).

When `background` is `true`, the response includes a `task_id` and `status` instead of waiting for the full result. Use the Get Research Task operation to retrieve the result.

#### Finance Research

Run finance-focused research using the You.com Finance Research API. Retrieves data from a finance-optimized index covering earnings reports, SEC filings, analyst coverage, and market data.

**Required**: `input` (the finance research question, max 40,000 characters)

**Optional parameters**:

| Parameter               | Description       | Values                                   |
| ----------------------- | ----------------- | ---------------------------------------- |
| `financeResearchEffort` | Depth of research | `deep` or `exhaustive` (default: `deep`) |

Returns an `output` object with `content` (Markdown string), `content_type` (always `"text"`), and `sources` (array of URLs with optional titles and snippets).

#### Get Research Task

Poll the status of a background research task using the You.com Research API.

**Required**: `taskId` (the task ID returned by a background Research or Finance Research operation)

Returns the task object with `status` (`queued`, `running`, `completed`, `failed`, or `cancelled`), `input`, and `result` (populated when the task completes). When `status` is `failed`, the `error` field contains a diagnostic message.

---

## Use as an AI Agent Tool

The You.com node has `usableAsTool` enabled, which means [n8n's built-in AI agents](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/) can call it directly. Add the You.com node as a tool in any AI Agent workflow, and the agent will be able to search the web or extract page content on its own.

---

## Resources

#### [GitHub Repository](https://github.com/youdotcom-oss/n8n-nodes-youdotcom)

Source code for the You.com n8n node

#### [npm Package](https://www.npmjs.com/package/@youdotcom-oss/n8n-nodes-youdotcom)

Package on npm

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Contents API Reference](/docs/api-reference/contents)

Full Contents API parameters and response schema

#### [Answer API Reference](/docs/api-reference/answer/v1-answer)

Full Answer API parameters and response schema

#### [Research API Reference](/docs/api-reference/research/v1-research)

Full Research API parameters and response schema

#### [Finance Research API Reference](/docs/api-reference/finance-research/v1-finance_research)

Full Finance Research API parameters and response schema