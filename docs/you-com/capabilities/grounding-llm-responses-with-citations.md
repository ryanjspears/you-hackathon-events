> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# The Best API for Grounding LLM Responses with Citations

Large language models hallucinate. They confidently invent facts, misattribute quotes, and cite papers that don't exist. The fix is **grounding**—constraining model output to evidence retrieved from a trusted source at inference time, and surfacing that evidence to the user as **citations**.

This guide explains how grounding works, what to look for in a grounding API, and how to implement it end-to-end using the You.com Web Search API. Every passage we return is citation-ready: each result includes the source URL, title, and extracted text that your LLM can quote and attribute.

**TL;DR**—Call the Web Search API with the user's query, inject the returned snippets into your prompt, instruct the model to cite each claim by source index, and render the citations in your UI. Full code below.

## What "Grounding With Citations" Actually Means

Grounding is often conflated with RAG (retrieval-augmented generation), but they're not identical. RAG is a pattern; grounding is a property.

An LLM response is **grounded** when:

1. Every factual claim in the response maps to a specific passage in a retrieved source.
2. The user can click through from the claim to the source to verify it.
3. The retrieval step happens at query time, not at training time.

A response is **cited** when the mapping in (1) is made explicit in the output—typically as inline references like `[1]` or as a structured list of sources.

The API you use for the retrieval step determines the ceiling on both. A grounding API needs three things:

* **Fresh, broad-coverage index.** If the source isn't indexed, it can't ground anything.
* **Passage-level extraction.** You need the specific sentence, not the whole page—LLMs can't effectively ground on 20KB of raw HTML.
* **Stable source metadata.** URL, title, and publisher need to be consistent enough to render as a citation.

The You.com Web Search API is built for this workflow. Each result in the response includes a `url`, `title`, and extracted passages that are small enough to fit in a prompt and specific enough to cite—`snippets` by default, or query-relevant `contents.highlights` when you ask for them.

## Why a Web Search API (Not a Vector Database) Is the Right Grounding Primitive

Teams new to grounding often reach for a vector database first. That's the right choice when your knowledge base is **bounded and private**—internal docs, a product catalog, a support knowledge base.

For everything else—current events, recent research, public facts, anything that changes—a **web search API is the correct primitive**:

| Requirement                  | Web search API     | Vector DB             |
| ---------------------------- | ------------------ | --------------------- |
| Real-time freshness          | Crawled on request | Stale after ingest    |
| Broad-domain coverage        | Public web         | Only what you indexed |
| Zero ingestion pipeline      | Just call the API  | Chunk, embed, upsert  |
| Attribution back to a URL    | Native             | Only if you stored it |
| Scales to millions of topics | Yes                | Prohibitive           |

For consumer assistants, research agents, and coding agents that answer open-domain questions, a web search API is almost always the better grounding backend. Vector DBs are complementary, not competitive—use both when the use case calls for both.

## The Minimal Grounding Loop

Every grounded-with-citations system is the same four-step loop:

```
user query
   │
   ▼
[1] call Web Search API    ← You.com Web Search API
   │
   ▼
[2] format snippets as context
   │
   ▼
[3] prompt LLM with citation instructions
   │
   ▼
[4] render response + source list
```

Everything else—reranking, caching, deduplication, domain filtering—is an optimization on top of this loop.

## Implementation: Grounded Answers in \~40 Lines of Python

Here's the entire loop end-to-end. This uses the You.com Web Search API for retrieval and OpenAI's chat completions for generation, but the pattern is model-agnostic—swap in Anthropic, Gemini, or any other provider.

```python
from openai import OpenAI
from youdotcom import You

client = OpenAI()
you = You()

def search(query: str, count: int = 5):
    """Retrieve web results from the You.com Web Search API."""
    res = you.search(query=query, count=count)
    return res.results.web if res.results and res.results.web else []

def build_context(hits: list) -> str:
    """Format hits as a numbered source list the LLM can cite."""
    blocks = []
    for i, hit in enumerate(hits, start=1):
        passages = " ".join(hit.snippets or [])
        blocks.append(f"[{i}] {hit.title} — {hit.url}\n{passages}")
    return "\n\n".join(blocks)

def grounded_answer(question: str) -> dict:
    hits = search(question)
    context = build_context(hits)

    system = (
        "Answer the user's question using ONLY the numbered sources below. "
        "Cite every factual claim inline using [N] where N is the source number. "
        "If the sources do not contain the answer, say so explicitly."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"},
        ],
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [
            {"n": i + 1, "url": h.url, "title": h.title}
            for i, h in enumerate(hits)
        ],
    }

print(grounded_answer("What did the Fed decide at their most recent meeting?"))
```

Run this and you'll get structured output with inline `[1]`, `[2]`, `[3]` citations keyed to a source list. That's grounding with citations—working, in production, in under a minute.

## The Response Shape That Makes This Work

The reason the loop above is so short is that the You.com Web Search API returns data already shaped for LLM consumption. Abbreviated response:

```json
{
  "results": {
    "web": [
      {
        "url": "https://www.federalreserve.gov/...",
        "title": "Federal Reserve issues FOMC statement",
        "description": "The Federal Open Market Committee decided to maintain...",
        "snippets": [
          "The Committee decided to maintain the target range for the federal funds rate at 4-1/4 to 4-1/2 percent.",
          "In support of its goals, the Committee will continue reducing its holdings..."
        ],
        "favicon_url": "https://ydc-index.io/favicon?domain=federalreserve.gov&size=128"
      }
    ]
  },
  "metadata": {
    "query": "fomc most recent meeting",
    "search_uuid": "a1b2c3d4-0000-0000-0000-000000000000",
    "latency": 0.38
  }
}
```

Three things about this shape matter for grounding:

* **Snippets are pre-extracted.** You don't need to scrape the page, run a readability parser, or chunk the text yourself. Each snippet is short enough to fit many of them in a prompt.
* **URL and title are always present.** Every result can be rendered as a citation with zero post-processing.
* **Snippets are the most query-relevant passages.** They're not the first N sentences of the page—they're the sentences most likely to answer the query, which is exactly what you want the LLM to see.

This is the difference between a search API designed for humans (SERPs) and one designed for LLMs (structured, extractive, passage-level).

## Prompting for Faithful Citations

The retrieval half is solved by the API. The generation half is solved by the prompt. Three rules hold up in production:

1. **Be explicit about the citation format.** Don't assume the model knows what you want. Say `"cite every factual claim inline using [N]"`.
2. **Constrain the model to the sources.** Say `"ONLY the sources below"` and `"if the sources do not contain the answer, say so."` This reduces hallucinated citations—claims that look cited but aren't actually in the source.
3. **Number sources, don't name them.** `[1]` is a stable reference. `[Federal Reserve]` is not—the model will eventually drop the brackets, abbreviate, or misquote.

A production-grade grounding prompt looks like:

```
You are answering a user question using retrieved web sources.

Rules:
- Use ONLY the numbered sources below.
- Cite every factual claim inline with [N], where N is the source number.
- A single claim may cite multiple sources: [1][3].
- If the sources do not contain the answer, say "The available sources do not answer this question" and stop.
- Do not invent URLs, titles, or statistics.

Sources:
{context}

Question: {question}
```

## Production Patterns

Once the basic loop is running, four upgrades pay for themselves:

**Dedupe by domain.** Search results frequently repeat the same publisher. Keep the highest-ranked hit per domain unless you have a reason not to—citations from five different sources are more credible than five from the same one.

**Cache by query.** For agents that reuse subqueries (research agents especially), a 15-minute TTL cache on the search call removes most of your latency and cost.

**Set a freshness filter for time-sensitive queries.** If the query mentions "today", "this week", or a year, narrow the search window. The You.com Web Search API supports recency filtering on the request.

**Post-validate citations.** After the LLM produces its answer, programmatically verify every `[N]` refers to a source you actually sent. Strip any that don't. This catches the rare hallucinated reference.

## When to Reach for Other You.com APIs

The Web Search API is the right grounding primitive for the vast majority of cases. Two adjacent scenarios where a different surface fits better:

* **Long-horizon research.** If your agent needs to synthesize dozens of sources over several minutes—a research workflow rather than a Q\&A—the [Research API](/docs/guides/research) handles the multi-step retrieval and synthesis for you.
* **Full-page content, not passages.** If your use case needs the entire cleaned body of a page (for summarization over a known URL, for example), use the [Contents API](/docs/guides/contents). Grounding typically doesn't need this—snippets are enough—but some workflows do.

## Why You.com for Grounding Specifically

Three things make this API a good fit for LLM grounding, as opposed to traditional search:

* **Purpose-built passages.** Every result is returned with pre-extracted text optimized for model consumption—keyword-centered snippets by default, or query-relevant highlights on request. No scraping, no readability parsing, no chunking.
* **Independent index.** You.com operates its own crawler and index, so grounding isn't dependent on a third party's rate limits or terms of service.
* **Built for AI workloads.** The API is already powering grounded answers inside agent frameworks like LangChain, LlamaIndex, Vercel AI SDK, and smolagents. The response shape is what those frameworks expect.

## Next Steps

#### [Quickstart](/docs/quickstart)

Get an API key and your first response in two minutes.

#### [Web Search API reference](/docs/guides/search)

Full parameter and response documentation.

#### [How to Evaluate the Web Search API](/docs/guides/evaluate-us)

Measure grounding quality on your workload.

#### [Web Search API for AI Agents](/docs/capabilities/web-search-api-for-ai-agents)

The retrieval-side companion to this guide.