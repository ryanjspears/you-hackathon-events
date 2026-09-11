> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Finance Research API Overview

**Add You.com to your agent or IDE via MCP**—every API in these docs is available on `https://api.you.com/mcp` (new accounts get \$100 in free credits), and Search is free to try via `https://api.you.com/mcp?profile=free`, no signup required. [MCP Server guide →](/docs/build-with-agents/mcp-server)

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

---

## What Is the Finance Research API?

The Finance Research API delivers grounded, citation-backed answers to financial questions.

It works the same way as the [Research API](/docs/guides/research): it runs multiple searches, reads through sources, and synthesizes everything into a thorough, Markdown-formatted answer with inline citations. The key difference is the index. Instead of the open web, the Finance Research API searches a purpose-built financial index—covering structured company fundamentals, equity and commodity price data, private company metrics, alternative signals, macroeconomic indicators, SEC filings, and financial news.

Ask a financial question, get a sourced answer backed by the right data.

---

## How It's Different From the Research API

Both APIs follow the same request-response pattern and return the same response shape. The difference is what each API searches.

|                | Research API                                                  | Finance Research API                                                                                                                                              |
| -------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Index**      | Open web                                                      | Finance-optimized: structured fundamentals, equity and commodity prices, private company data, alternative signals, macro indicators, SEC filings, financial news |
| **Input**      | Any research question                                         | Financial questions—company analysis, market research, earnings, macroeconomics                                                                                   |
| **Parameters** | `input`, `research_effort`, `source_control`, `output_schema` | `input`, `research_effort`                                                                                                                                        |
| **Response**   | Markdown answer with citations                                | Markdown answer with citations (same shape)                                                                                                                       |
| **Best for**   | General-purpose research                                      | Financial analysis, due diligence, earnings summaries, market research                                                                                            |

The Finance Research API does not support `source_control` or `output_schema`. If you need domain filtering or structured JSON output, use the [Research API](/docs/guides/research).

---

## What You Get

Every Finance Research API response includes:

* **`content`**: A Markdown-formatted answer with inline citations such as `[[1, 2]]` that reference items in the `sources` array.
* **`content_type`**: Always `text`.
* **`sources`**: The financial sources the API read and cited—each with a URL, title, and relevant excerpts.

```json maxLines=25
{
  "output": {
    "content": "For fiscal year 2025, ended January 26, 2025, NVIDIA's revenue rose to **$130.5 billion, up 114% year over year**.[[1]] The main drivers were:\n\n- **Data Center demand**, especially accelerated computing and AI platforms: Data Center revenue was **up 142%**, driven by demand for NVIDIA's **Hopper architecture** for large language models, recommendation engines, and generative AI applications; NVIDIA also began shipping **Blackwell** production systems in Q4 FY2025.[[1]]\n- **Compute & Networking segment growth**: revenue increased **145%**, with Data Center compute up **162%** on Hopper demand and Data Center networking up **51%**, driven by Ethernet for AI, including Spectrum-X.[[1]]\n- Smaller but positive contributions from other markets: **Gaming revenue rose 9%** on GeForce RTX 40 Series GPUs, **Professional Visualization rose 21%** on Ada RTX workstation adoption, and **Automotive rose 55%** from self-driving platform sales.[[1]]\n\nIn short, NVIDIA's FY2025 growth was overwhelmingly driven by **AI-related Data Center compute and networking demand**, with additional support from gaming, professional visualization, and automotive.",
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

---

## Key Features

### Research effort levels

The `research_effort` parameter controls how much compute the API allocates to your question. Higher effort means more searches, deeper source reading, and more cross-referencing—at the cost of longer response times.

| Level        | Price per 1k | Latency | Use case                                                                                                                |
| ------------ | ------------ | ------- | ----------------------------------------------------------------------------------------------------------------------- |
| `deep`       | \$110        | \< 120s | Multi-source analysis—earnings summaries, competitive benchmarking, regulatory research, multi-quarter trends (default) |
| `exhaustive` | \$500        | \< 300s | Comprehensive research—deep due diligence, full 10-K analysis, cross-market research                                    |

### Citation-backed answers

Every claim in the response links back to a specific source. Citations reference SEC filings, earnings press releases, financial news, and analyst reports—sources your users or compliance teams can actually verify.

### Finance-optimized index

The Finance Research API searches a dedicated financial index. Not just the open web. This means retrieval is focused on structured financial data—not general-interest content that happens to mention a ticker. The index covers:

* **Company fundamentals**—earnings, estimates, valuation ratios, industry-normalized financials, competitor benchmarks, segment metrics
* **Market activity**—M\&A transactions, buybacks, capital raises, IPOs, shelf registrations, VC funding for both public and private companies
* **Prices and rates**—equity prices and volume across 42 global exchanges, cryptocurrency, foreign exchange, metals, commodities, interest rates, inflation, and real estate
* **Alternative signals**—web traffic and app analytics, non-GAAP operating metrics, LLM benchmarks
* **Macroeconomic data**—employment metrics, energy imports and exports, money supply, and economic indicators
* **Financial content**—SEC filings, earnings transcripts, analyst coverage, and financial news

---

## Quickstart

```python maxLines=0
from youdotcom import You
from youdotcom.models import FinanceResearchEffort

with You() as you:
    res = you.finance_research(
        input="What were the key drivers of NVIDIA's revenue growth in fiscal year 2025?",
        research_effort=FinanceResearchEffort.DEEP,
    )

    # The complete, sourced answer to your financial question
    print(res.output.content)

    # Dive into the sources (title and URL)
    for i, source in enumerate(res.output.sources, 1):
        print(f"[{i}] {source.title or 'Untitled'}: {source.url}")
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

// The complete, sourced answer to your financial question
console.log(data.output.content);

// Dive into the sources
(data.output.sources as { title?: string; url: string }[]).forEach((s, i) => {
  console.log(`[${i + 1}] ${s.title ?? "Untitled"}: ${s.url}`);
});
```

```curl
curl -X POST https://api.you.com/v1/finance_research \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What were the key drivers of NVIDIA'\''s (NVDA) revenue growth in fiscal year 2025?",
    "research_effort": "deep"
  }'
```

---

## Parameters

| Parameter         | Type   | Required | Description                                             |
| ----------------- | ------ | -------- | ------------------------------------------------------- |
| `input`           | string | Yes      | The financial research question (max 40,000 characters) |
| `research_effort` | string | No       | Depth of research: `deep` (default), `exhaustive`       |

[View full API reference](/docs/api-reference/finance-research/v1-finance_research)

---

## Common Use Cases

### Earnings analysis

Quickly summarize what happened in a company's most recent quarter—revenue, segment performance, guidance, and analyst reaction—without manually reading the press release and earnings call transcript.

***"Summarize Microsoft's Q2 FY2025 earnings results and key guidance updates"***

### Competitive benchmarking

Compare multiple companies across financial metrics and business model characteristics to assess relative positioning in a market.

***"Compare the gross margins of Apple, Microsoft, and Google over the past three fiscal years"***

```json maxLines=40 wordWrap
{
  "output": {
    "content": "**Gross margin comparison (gross margin % = gross profit / revenue) for the last three fiscal years:**\n\n| Company | FY2025 | FY2024 | FY2023 | Takeaway |\n|---|---:|---:|---:|---|\n| **Microsoft** | **68.8%** — $193.893B gross margin / $281.724B revenue [[2]] | **69.8%** — $171.008B / $245.122B [[2]] | **68.9%** — $146.052B / $211.915B [[2]] | Highest margins, broadly stable. |\n| **Google / Alphabet** | **59.7%** — ($402.836B revenue − $162.535B cost of revenues) / $402.836B [[3]] | **58.2%** — ($350.018B − $146.306B) / $350.018B [[3]] | **56.6%** — ($307.394B − $133.332B) / $307.394B [[3]] | Middle, improving each year. |\n| **Apple** | **46.9%** [[1]] | **46.2%** [[1]] | **44.1%** [[1]] | Lowest of the three, but steadily improving. |\n\n**Bottom line:** Microsoft had the strongest gross margins in all three fiscal years, Google/Alphabet was second and improving, and Apple was lowest but also improved from FY2023 to FY2025.",
    "content_type": "text",
    "sources": [
      {
        "url": "https://fintel.io/doc/sec-apple-inc-320193-10k-2025-october-31-20392-514",
        "title": "Apple Inc. - 10K - Annual Report - October 31, 2025"
      },
      {
        "url": "https://s2.q4cdn.com/470004039/files/doc_financials/2025/ar/_10-K-2025-As-Filed.pdf",
        "title": "UNITED STATES SECURITIES AND EXCHANGE COMMISSION Washington, D.C. ..."
      },
      {
        "url": "https://www.studocu.com/en-us/document/miami-university/intro-to-financial-accounting/apple-inc-2025-consolidated-financial-statements-analysis/149162812",
        "title": "Apple Inc. 2025 Consolidated Financial Statements Analysis - Studocu"
      }
    ]
  }
}
```

### Due diligence research

Gather sourced, verifiable information about a company's financial health, capital structure, or risk factors—with citations you can trace back to primary sources.

***"What are the key risk factors disclosed in Palantir's most recent 10-K filing?"***

### Macroeconomic research

Research macro trends, central bank policy, inflation dynamics, and their impact on specific sectors or asset classes.

***"How has the Federal Reserve's rate path affected commercial real estate valuations since 2022?"***

### Regulatory and filing analysis

Dig into SEC filings, regulatory disclosures, or financial restatements to understand what a company has reported and how it has changed over time.

***"What changes did Boeing make to its revenue recognition policies in its most recent annual report?"***

---

## Best Practices

### Match research effort to the question

`deep` handles most financial questions well—earnings summaries, sector comparisons, multi-company benchmarks. Use `exhaustive` when you need the highest quality result and response time isn't a constraint, such as full 10-K analysis or complex cross-market research.

### Write specific, scoped questions

The `input` field supports up to 40,000 characters. Include context that narrows the question: the company name, the time period, the specific metric or event you care about. A vague question like "tell me about Microsoft" produces a broad summary. A specific question like "what drove Microsoft's Azure growth acceleration in Q2 FY2025" produces a more useful answer.

### Verify citations for compliance-sensitive use cases

The Finance Research API returns citations for every claim. For use cases where the sourced data will inform investment decisions, client reports, or regulatory filings, treat the citations as starting points—follow them to the primary source and confirm the numbers before acting on them. The API is a research accelerator, not a substitute for primary source verification.

### Use it for synthesis, not programmatic data pipelines

The Finance Research API produces research answers—it reads, cross-references, and synthesizes data into a sourced response. It is not a structured data feed or time series API. If you need raw OHLCV exports, tick-by-tick price streams, or JSON-formatted financial data for quantitative modeling, use a dedicated data provider. The Finance Research API is best suited for questions where the value is in the analysis, not just the raw numbers.

---

## Pricing

Finance Research API pricing is tiered by effort level. All new accounts receive \$100 in free credits. See the [Billing page](/docs/administration/billing#finance-research-api) for complete pricing and latency by tier.

See the [effort levels table](#research-effort-levels) above for how each tier performs.

For volume discounts, annual pricing, or enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).

Agents can also pay per call without an account. `POST /v1/finance_research` accepts [machine payments](/docs/administration/machine-payments) at the same per-tier prices, settling each request in USDC from a funded wallet instead of drawing down credits.

---

## Next Steps

#### [API Reference](/docs/api-reference/finance-research/v1-finance_research)

Full parameter reference, request/response schemas, and interactive playground

#### [Research API](/docs/guides/research)

General-purpose research with source controls, structured output, and open web access

#### [Quickstart](/docs/quickstart)

Get your API key and try all our APIs in under five minutes

#### [Try in Postman](https://www.postman.com/youdotcom/you-com-api-workspace)

Fork the collection, add your API key, and send your first request