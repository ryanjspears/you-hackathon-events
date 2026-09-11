> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# How to Evaluate You.com Web Search API

> A practical guide to benchmarking You.com's Web Search API: methodology, configurations, datasets, and real performance tradeoffs.

A practical guide to benchmarking You.com's Web Search API: methodology, datasets, and real performance tradeoffs.

New to the Web Search API? Start with the [Web Search API Overview](/docs/guides/search) for a full parameter reference and feature walkthrough, then come back here when you're ready to run a structured evaluation.

## Why This Guide Exists

Most developer docs treat evaluation like checking boxes. This guide treats it like shipping production code: you need real benchmarks, honest tradeoffs, and configurations that actually work.

We'll cover:

* **Retrieval Quality**—Does it actually find what you need?
* **Latency**—Fast enough for your users?
* **Freshness**—Can it handle "what happened today?"
* **Cost**—What's your burn rate per query?
* **Agent Performance**—Does it work in multi-step reasoning workflows?

---

**Want help running your eval?** Our team can design and run custom benchmarks for your use case. [Talk to us](https://you.com/book-a-demo)

## The Golden Rule: Start Simple, Stay Fair

**TL;DR: Use default settings. Don't over-engineer your first eval.**

Most failed evaluations have one thing in common: people add too many parameters too early.

### Recommended Starting Point

```python
from youdotcom import You

with You() as you:
    response = you.search(
        query=query,
        count=10
    )

# That's it. No date filters. No domain whitelists. Just search.
```

### When to Add Complexity

Add parameters ONLY when:

1. Your evaluation explicitly tests that feature (e.g., freshness requires the `freshness` parameter)
2. You've already run baseline evals and know what you're optimizing for
3. The parameter reflects actual production usage, not hypothetical edge cases

**Anti-pattern**: "Let me add every possible parameter to make this perfect"

**Better approach**: "Let me run this with defaults, measure performance, then iterate"

---

For a full reference of available parameters and their defaults, see the [Web Search API Overview](/docs/guides/search#all-optional-parameters-you-can-control).

---

## Latency: Compare Apples to Apples

**Critical insight: Never compare APIs with wildly different [latency](https://you.com/resources/why-api-latency-alone-is-a-misleading-metric) profiles.**

A 200ms API and a 3000ms API serve different use cases. Comparing them is like comparing a bicycle to a freight train.

### Latency Buckets

| Latency Class             | Use Cases                                       | Compare Within                     |
| ------------------------- | ----------------------------------------------- | ---------------------------------- |
| **Ultra-fast (\< 200ms)** | Autocomplete, real-time voice agents            | Other sub-200ms systems            |
| **Fast (200-800ms)**      | Chatbots, user-facing QA                        | Similar mid-latency APIs           |
| **Deep (>1000ms)**        | Research, multi-hop reasoning, batch processing | Other comprehensive search systems |

### Fair Comparison Framework

```python
# Good: Comparing within the same latency class
compare_systems([
    "You.com (350ms p50)",
    "Competitor A (380ms p50)",
    "Competitor B (290ms p50)"
])

# Bad: Comparing across latency classes
compare_systems([
    "You.com (350ms p50)",
    "Deep Research API (2800ms p50)"  # Meaningless comparison
])
```

---

## Evaluation Workflow: 4 Steps That Actually Work

### Define What You're Testing

Don't start with "let's evaluate everything." Start with:

* What capability matters? (speed? accuracy? freshness?)
* What latency can you tolerate?
* Single-step retrieval or multi-step reasoning?

**Example scope**: "We need 90%+ accuracy on customer support questions with \< 500ms latency"

### Pick Your Dataset

| Dataset            | Tests                    | Notes                                                  |
| ------------------ | ------------------------ | ------------------------------------------------------ |
| SimpleQA           | Fast factual QA          | Good baseline                                          |
| FRAMES             | Multi-step reasoning     | Agentic workflows                                      |
| FreshQA            | Time-sensitive queries   | Use with `freshness` param                             |
| Custom (your data) | Domain-specific accuracy | [Talk to us to learn how](https://you.com/book-a-demo) |

**Pro tip**: Start with public benchmarks, but your production queries are the real test.

**Need help building a custom dataset?** [We can help](https://you.com/book-a-demo)

### Run Your Eval

```python
from youdotcom import You
import time

def run_eval(dataset_path, config):
    results = []

    with You() as you:
        for item in load_dataset(dataset_path):
            query = item['question']
            expected = item['answer']

            # Step 1: Retrieve
            start = time.perf_counter()
            response = you.search(
                query=query,
                count=config.get('count', 10),
                extraction=config.get('extraction'),
                freshness=config.get('freshness')
            )
            latency = (time.perf_counter() - start) * 1000

            # Step 2: Synthesize answer using your LLM
            snippets = [r.snippets[0] for r in response.results.web if r.snippets]
            context = "\n".join(snippets)
            answer = llm.generate(
                f"Answer using only this context:\n{context}\n\n"
                f"Question: {query}\nAnswer:"
            )

            # Step 3: Grade
            grade = evaluate_answer(expected, answer)

            results.append({
                'correct': grade == 'correct',
                'latency_ms': latency
            })

    # Calculate metrics
    accuracy = sum(r['correct'] for r in results) / len(results)
    p50_latency = sorted([r['latency_ms'] for r in results])[len(results)//2]

    return {
        'accuracy': f"{accuracy:.1%}",
        'p50_latency': f"{p50_latency:.0f}ms"
    }
```

### Analyze & Iterate

Look at:

* **Accuracy vs latency tradeoff** - Can you get 95% accuracy at 300ms?
* **Failure modes** - Which queries fail? Is there a pattern?
* **Cost** - What's your \$/1000 queries?

Then iterate:

* Add full page content if snippets aren't giving enough context
* Add `freshness` if failures are due to stale content
* Compare against competitors in the same latency class

---

## Tool Calling for Agents

When evaluating You.com in agentic workflows, keep the tool definition minimal.

**Open-source evaluation framework**: Check out [Agentic Web Search Playoffs](https://github.com/youdotcom-oss/web-search-agent-evals) for a ready-to-use benchmark comparing web search providers in agentic contexts.

```python
search_tool = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web using You.com. Returns relevant snippets and URLs.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    }
}
```

**Note**: Don't expose `freshness`, `extraction`, or other parameters to the agent unless necessary. Let the agent focus on formulating good queries.

### Implementation

```python
import json

from youdotcom import You

def handle_tool_call(tool_call):
    query = tool_call.arguments["query"]

    with You() as you:
        response = you.search(query=query, count=10)

    # Format for agent consumption
    formatted = []
    for r in response.results.web[:5]:
        formatted.append({
            "title": r.title,
            "snippet": r.snippets[0] if r.snippets else r.description,
            "url": r.url
        })

    return json.dumps(formatted)
```

---

## Common Mistakes to Avoid

### 1. Over-Filtering Too Early

**Don't:**

```python
response = you.search(
    query=query,
    freshness="week",
    country="US",
    language="EN",
    safesearch="strict"
)
```

**Do:**

```python
response = you.search(query=query, count=10)  # Start simple
```

### 2. Ignoring Your Actual Queries

**Don't just run:** Public benchmarks

**Also run:** Your actual user queries from production logs

### 3. Not Measuring What Users Care About

**Don't only measure:** Technical accuracy

**Also measure:** Click-through rate, task completion, reformulation rate

### 4. Testing in Isolation

**Don't test:** Web Search API alone

**Test:** Full workflow (search -> synthesis -> grading) with your actual LLM and prompts

---

## Debugging Performance Issues

### If Accuracy is Low (\< 85%)

1. Are you requesting enough results? Try `count=15`
2. Enable full page content:

```python
response = you.search(
    query=query,
    count=15,
    extraction=Extraction(
        extraction_mode=ExtractionMode.FULL_PAGE,
        full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
)
```

3. Is your synthesis prompt good? Test with GPT-4
4. Is your grading fair? Manual review a sample

### If Results are Stale

```python
# Force fresh results
response = you.search(
    query=query,
    count=10,
    freshness="day"  # or "week", "month"
)
```

---

**Still stuck?** Our team has run hundreds of search evals. [Get hands-on help](https://you.com/book-a-demo)

## Production Checklist

### 1. Run Comparative Benchmarks

```python
configs = [
    {'count': 5},
    {'count': 10},
    {
        'count': 10,
        'extraction': {
            'extraction_mode': 'full_page',
            'full_page': {'extraction_formats': ['markdown']},
        },
    },
]

for config in configs:
    results = run_eval('your_dataset.json', config)
    print(f"{config}: {results}")
```

### 2. Set Up Monitoring

```python
# What to log
{
    'query': query,
    'latency_ms': latency,
    'num_results_returned': len(results.results.web),
    'used_extraction': bool(extraction),
    'freshness_filter': freshness,
    'timestamp': now()
}
```

### 3. Document Everything

```markdown
## Search Evaluation - 2025-01-26

**Dataset**: 500 customer support queries
**Config**: count=10, extraction={"extraction_mode": "full_page", "full_page": {"extraction_formats": ["markdown"]}}
**Results**:
- Accuracy: 91.2%
- P50 Latency: 445ms
- P95 Latency: 892ms

**Decision**: Ship with full page content enabled - improves synthesis quality
```

---

## Getting Help

* **[Run a custom evaluation](https://you.com/book-a-demo)** - Custom benchmarks designed and run by our team
* **[Agentic Web Search Playoffs](https://github.com/youdotcom-oss/web-search-agent-evals)** - Open-source benchmark for comparing web search in agentic workflows
* [API Documentation](https://you.com/docs/)
* [Discord Community](https://discord.gg/you)
* Email: [developers@you.com](mailto:developers@you.com)

---

**Remember**: The best evaluation is the one you actually run. Start simple, measure what matters, and iterate.