> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# LangChain

LangChain is one of the most popular frameworks for building LLM-powered applications. By connecting You.com's search and content APIs to LangChain, you can ground your agents and RAG pipelines in real-time, accurate web data instead of relying on static training knowledge alone.

The [`langchain-youdotcom`](https://pypi.org/project/langchain-youdotcom/) package provides three integration points: a search tool (`YouSearchTool`), a content extraction tool (`YouContentsTool`), and a retriever (`YouRetriever`). Drop them into any LangChain agent or chain to give it live web access.

---

## Getting Started

### Install the Package

```bash
pip install -U langchain-youdotcom
```

### Set Your API Key

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

Get your API key at [you.com/platform](https://you.com/platform).

---

## Usage

#### YouSearchTool

`YouSearchTool` wraps the You.com Web Search API as a LangChain tool, making it available to any agent that uses tools.

```python
from langchain_youdotcom import YouSearchTool

tool = YouSearchTool()
result = tool.invoke("latest developments in quantum computing")
print(result)
```

To customize search parameters, pass them via `api_wrapper`:

```python
from langchain_youdotcom import YouSearchAPIWrapper, YouSearchTool

tool = YouSearchTool(
    api_wrapper=YouSearchAPIWrapper(
        count=5,
        livecrawl="web",       # "web", "news", or "all"
        freshness="day",       # "day", "week", "month", or "year"
        safesearch="moderate", # "off", "moderate", or "strict"
    )
)
result = tool.invoke("AI news today")
```

#### YouContentsTool

`YouContentsTool` fetches and extracts clean content from web pages.

```python
from langchain_youdotcom import YouContentsTool

tool = YouContentsTool()
result = tool.invoke({"urls": ["https://python.langchain.com"]})
print(result[:500])
```

#### YouRetriever

`YouRetriever` implements LangChain's retriever interface, making it a drop-in for any RAG pipeline.

```python
from langchain_youdotcom import YouRetriever

retriever = YouRetriever(count=5)
docs = retriever.invoke("climate change policy updates")

for doc in docs:
    print(doc.metadata["url"])
    print(doc.page_content[:300])
    print()
```

To use it in a retrieval chain:

```python
from langchain_youdotcom import YouRetriever
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

retriever = YouRetriever(count=5, livecrawl="web")
llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_template(
    """Answer based on the following context:

{context}

Question: {question}"""
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for chunk in chain.stream("What is the current state of fusion energy research?"):
    print(chunk, end="", flush=True)
```

#### Agent with LangGraph

Both tools work with any LangChain agent. Here's an example using `create_agent`:

```python
from langchain_openai import ChatOpenAI
from langchain_youdotcom import YouSearchTool, YouContentsTool
from langchain.agents import create_agent

llm = ChatOpenAI(model="gpt-4o-mini")
tools = [YouSearchTool(), YouContentsTool()]
agent = create_agent(llm, tools)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What are the top AI news stories this week?"}]}
)
print(response["messages"][-1].content)
```

---

## Community Package

You.com is also available via `langchain-community`:

```python
from langchain_community.retrievers import YouRetriever
from langchain_community.tools.you import YouSearchTool
```

The standalone `langchain-youdotcom` package is recommended for new projects as it stays up to date with the latest You.com API features.

---

## Resources

#### [LangChain Tool Docs](https://docs.langchain.com/oss/python/integrations/tools/you)

Official LangChain documentation for YouSearchTool

#### [LangChain Retriever Docs](https://docs.langchain.com/oss/python/integrations/retrievers/you-retriever)

Official LangChain documentation for YouRetriever

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Contents API Reference](/docs/api-reference/contents)

Full Contents API parameters and response schema