> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# LlamaIndex

LlamaIndex includes a You.com retriever integration through the `llama-index-retrievers-you` package. It uses You.com's Web Search API to retrieve relevant web and news results, converting them into LlamaIndex's standard `NodeWithScore` format for use with query engines, agents, and other components.

**Run this entire example as a [Jupyter Notebook](https://github.com/youdotcom-oss/llama_index/blob/main/docs/examples/retrievers/you_retriever.ipynb).**

---

## Getting Started

### Install the Package

```bash
pip install llama-index-retrievers-you
```

### Set Your API Key

```python
import os

os.environ["YDC_API_KEY"] = "<YDC_API_KEY>"
```

Get your API key at [you.com/platform](https://you.com/platform).

---

## Usage

#### Basic

Set up the retriever and retrieve web results:

```python
import os
from llama_index.retrievers.you import YouRetriever

retriever = YouRetriever(api_key=os.environ["YDC_API_KEY"])
retrieved_results = retriever.retrieve("national parks in the US")

print(f"Retrieved {len(retrieved_results)} results")

for i, result in enumerate(retrieved_results):
    print(f"\nResult {i+1}:")
    print(f"  Text: {result.node.text}...")
    print("Metadata:")
    for key, value in result.node.metadata.items():
        print(f"  {key}: {value}")
```

Each result includes the page text along with metadata such as `url`, `title`, `description`, `page_age`, `thumbnail_url`, and `source_type` (either `"web"` or `"news"`).

#### Async

The retriever also supports async operations:

```python
retrieved_results = await retriever.aretrieve("national parks in the US")
```

#### News

The Web Search API automatically includes news results based on your query. You can control how many results are returned per type and filter by country:

```python
import os
retriever = YouRetriever(api_key=os.environ["YDC_API_KEY"], count=5, country="US")

retrieved_results = retriever.retrieve("latest geopolitical updates")

for result in retrieved_results:
    print(result.node.metadata.get("source_type"))  # "web" or "news"
```

#### Query engine

Combine the retriever with an LLM to synthesize natural language answers from search results:

```python
import os
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.anthropic import Anthropic
from llama_index.retrievers.you import YouRetriever

llm = Anthropic(model="claude-haiku-4-5-20251001", api_key="your_anthropic_key")

retriever = YouRetriever(api_key=os.environ["YDC_API_KEY"])
query_engine = RetrieverQueryEngine.from_args(retriever, llm)

response = query_engine.query(
    "What are the most visited national parks in the US and why?"
)
print(str(response))
```

The query engine retrieves relevant search results from You.com, passes them as context to the LLM, and returns a synthesized answer.

## Customizing Search Parameters

You can pass optional parameters to control the search behavior:

```python
import os
from llama_index.retrievers.you import YouRetriever

retriever = YouRetriever(
    api_key=os.environ["YDC_API_KEY"],
    count=20,         # Up to 20 results per section (web/news)
    country="US",     # Focus on US results
    language="en",    # English results
    freshness="week", # Results from the past week
    safesearch="moderate",
)

retrieved_results = retriever.retrieve("renewable energy breakthroughs")
```

---

## Resources

#### [LlamaIndex Notebook](https://developers.llamaindex.ai/python/framework/integrations/retrievers/you_retriever/)

Full notebook in the LlamaIndex docs, with full response examples

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Get an API Key](https://you.com/platform)

Sign up to get your You.com API key