> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# LangGraph

LangGraph is a framework for building stateful, multi-step agent applications as graphs. It gives you fine-grained control over agent behavior—tool routing, state management, cycles, and human-in-the-loop patterns—while staying compatible with the LangChain ecosystem.

The [`langchain-youdotcom`](https://pypi.org/project/langchain-youdotcom/) package provides `YouSearchTool` and `YouContentsTool`, which plug directly into LangGraph agents to give them real-time web access.

---

## Getting Started

### Install the Packages

```bash
pip install -U langchain-youdotcom langgraph langchain langchain-openai
```

### Set Your API Keys

```bash
export YDC_API_KEY="<YDC_API_KEY>"
export OPENAI_API_KEY=your_openai_key
```

Get your You.com API key at [you.com/platform](https://you.com/platform).

The examples below use OpenAI as the LLM provider, but any LangChain-compatible chat model works—Anthropic, Google, Mistral, local models, etc.

---

## ReAct Agent

The fastest way to get started is `create_agent`, a prebuilt LangGraph agent that handles tool calling and message routing automatically.

```python
from langchain_openai import ChatOpenAI
from langchain_youdotcom import YouSearchTool, YouContentsTool
from langchain.agents import create_agent

llm = ChatOpenAI(model="gpt-4o-mini")
tools = [YouSearchTool(), YouContentsTool()]

agent = create_agent(llm, tools)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What are the top AI stories this week?"}]}
)
print(response["messages"][-1].content)
```

### Customizing Search Parameters

Pass an `api_wrapper` to control search behavior:

```python
from langchain_youdotcom import YouSearchAPIWrapper, YouSearchTool

tool = YouSearchTool(
    api_wrapper=YouSearchAPIWrapper(
        count=5,
        livecrawl="web",
        freshness="day",
        safesearch="moderate",
    )
)
```

---

## Streaming

LangGraph supports token-level streaming out of the box. Use `astream_events` to stream agent responses as they're generated:

```python
import asyncio
from langchain_openai import ChatOpenAI
from langchain_youdotcom import YouSearchTool
from langchain.agents import create_agent

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(llm, [YouSearchTool()])


async def main():
    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": "What is the current price of Bitcoin?"}]},
        version="v2",
    ):
        if event["event"] == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token:
                print(token, end="", flush=True)
    print()


asyncio.run(main())
```

---

## Custom Graph With a Search Node

For more control, build a custom `StateGraph`. This example creates a simple search-then-summarize pipeline where the agent searches the web, then synthesizes an answer from the results:

```python
from langchain_openai import ChatOpenAI
from langchain_youdotcom import YouSearchTool
from langgraph.graph import START, END, StateGraph, MessagesState

llm = ChatOpenAI(model="gpt-4o-mini")
search = YouSearchTool()


def search_web(state: MessagesState):
    """Search the web for the user's query."""
    user_message = state["messages"][-1].content
    results = search.invoke(user_message)
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Search results:\n\n{results}",
            }
        ]
    }


def summarize(state: MessagesState):
    """Summarize the search results into a final answer."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(MessagesState)
graph.add_node("search", search_web)
graph.add_node("summarize", summarize)

graph.add_edge(START, "search")
graph.add_edge("search", "summarize")
graph.add_edge("summarize", END)

app = graph.compile()

response = app.invoke(
    {"messages": [{"role": "user", "content": "What happened in tech this week?"}]}
)
print(response["messages"][-1].content)
```

---

## Search and Extract Pattern

Combine `YouSearchAPIWrapper` methods in a multi-step graph that searches the web, extracts full page content from the top results, and generates a comprehensive answer. The search step returns snippets and URLs (without `livecrawl`), then the extract step calls the Contents API to fetch full page content for the top results. This avoids fetching full content for every search result—only the most relevant URLs get crawled:

```python
from langchain_openai import ChatOpenAI
from langchain_youdotcom import YouSearchAPIWrapper
from langgraph.graph import START, END, StateGraph, MessagesState

llm = ChatOpenAI(model="gpt-4o-mini")
wrapper = YouSearchAPIWrapper(count=5)


class SearchState(MessagesState):
    urls: list[str]


def search_web(state: SearchState):
    """Search the web and extract URLs from the results."""
    query = state["messages"][-1].content
    docs = wrapper.results(query)
    urls = [doc.metadata["url"] for doc in docs if "url" in doc.metadata]
    results_text = "\n\n".join(
        f"{doc.metadata.get('title', 'Untitled')}: {doc.page_content[:200]}"
        for doc in docs
    )
    return {
        "messages": [
            {"role": "system", "content": f"Search results:\n\n{results_text}"}
        ],
        "urls": urls,
    }


def extract_content(state: SearchState):
    """Extract full content from the URLs found in search."""
    urls = state.get("urls", [])[:3]
    if not urls:
        return {"messages": []}
    docs = wrapper.contents(urls)
    content = "\n\n".join(doc.page_content for doc in docs)
    return {
        "messages": [
            {"role": "system", "content": f"Extracted content:\n\n{content}"}
        ]
    }


def synthesize(state: SearchState):
    """Generate a final answer from all gathered context."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(SearchState)
graph.add_node("search", search_web)
graph.add_node("extract", extract_content)
graph.add_node("synthesize", synthesize)

graph.add_edge(START, "search")
graph.add_edge("search", "extract")
graph.add_edge("extract", "synthesize")
graph.add_edge("synthesize", END)

app = graph.compile()

response = app.invoke(
    {"messages": [{"role": "user", "content": "Explain the latest advances in quantum computing"}]}
)
print(response["messages"][-1].content)
```

---

## Configuration Reference

Both tools accept a `YouSearchAPIWrapper` via the `api_wrapper` parameter. Here are the key options:

### Search Options

#### Result volume

`count` sets the max results per section. `offset` controls pagination in multiples of `count`. `k` limits max documents after the API response.

#### Filtering

`freshness`, `country`, `safesearch`, and `language` narrow results by age, location, moderation level, and BCP 47 language code.

#### Live page content

`livecrawl` fetches live page content from `web`, `news`, or `all` results. `livecrawl_formats` controls whether that content is returned as `html` or `markdown`.

#### Wrapper behavior

`n_snippets_per_hit` controls snippets per search result at the wrapper layer, after the API response.

### Contents Options

`YouContentsTool` accepts `urls: list[str]` at invocation. To control the output format or crawl timeout, call `api_wrapper.contents()` directly:

```python
from langchain_youdotcom import YouSearchAPIWrapper

wrapper = YouSearchAPIWrapper()
docs = wrapper.contents(
    ["https://example.com"],
    formats=["markdown", "metadata"],  # default
    crawl_timeout=30,                  # seconds (1–60)
)
```

For full parameter details, see the [Web Search API reference](/docs/api-reference/search/v1-search) and [Contents API reference](/docs/api-reference/contents).

---

## Resources

#### [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

Official LangGraph documentation

#### [LangChain Integration](/docs/integrations/langchain)

Full langchain-youdotcom tool and retriever reference

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Contents API Reference](/docs/api-reference/contents)

Full Contents API parameters and response schema