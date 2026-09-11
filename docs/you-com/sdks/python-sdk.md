> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Python SDK

We offer a Python SDK to make interacting with our APIs simple and predictable. It covers the Web Search, Answer, Contents, Research, and Finance Research APIs, and is available on PyPI [here](https://pypi.org/project/youdotcom/).
Now you can get started with our APIs with just a few lines of code.

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quickstart

### Get an API Key

Get one for free on the [You.com platform](https://you.com/platform/).

### Install the SDK

```bash
pip install youdotcom
```

### Run a Search

Perform a simple search to retrieve results from general web and news sources.

```python
from youdotcom import You

# Initialize the SDK — it reads your key from YDC_API_KEY
you = You()

# Perform a search
results = you.search(
    query="latest AI developments"
)

# Access the results
print(results)
```

That's it. You now have a comprehensive set of search results combining web and news sources.

## What's next?

The Web Search API offers filters that can help you find exactly what you need, whether you want to go broader or narrower. For example, to find recent information in the United States about renewable energy from the past week limited to 10 results per source type, either `web` or `news`, write:

```python
from youdotcom import You
from youdotcom.models import Freshness, Country

with You() as you:
    results = you.search(
        query="renewable energy",
        count=10,
        freshness=Freshness.WEEK,
        country=Country.US,
    )
```

Learn more about the Web Search API in the [Web Search API reference](/docs/api-reference/search/v1-search), and the Python SDK by visiting the open source repository on [GitHub](https://github.com/youdotcom-oss/youdotcom-python-sdk/).

## Response Structure

The Web Search API returns a `SearchResponse` object (see [documentation](https://github.com/youdotcom-oss/youdotcom-python-sdk/blob/main/docs/models/searchresponse.md)):

#### results.web

An array of web result objects. Each object may include `url`, `title`, `description`, `snippets`, `thumbnail_url`, `page_age`, and `favicon_url`.

#### results.news

An array of news article objects. Each object may include `url`, `title`, `description`, `thumbnail_url`, and `page_age`.

#### metadata

Information about the search query and response, including `query`, `search_uuid`, and `latency`.

## Long-Running Research

Research at `deep`, `exhaustive`, or `frontier` effort can run for minutes, which is long enough to exceed a client timeout or tie up a worker. Run those in background mode and let the SDK handle the task lifecycle. The helpers live in `youdotcom.research_helpers`, which is a separate import from the client itself.

```python
from youdotcom import You
from youdotcom.models import ResearchEffort
from youdotcom.research_helpers import research_and_wait

with You() as you:
    task = research_and_wait(
        you,
        input="Which global cities improved air quality the most over the past 10 years?",
        research_effort=ResearchEffort.FRONTIER,
        timeout_s=600,
    )
    print(task.status)
    print(task.result.output["content"])
```

Pick the helper that matches how your code is shaped:

| Helper                                  | Use it when                                                                           |
| --------------------------------------- | ------------------------------------------------------------------------------------- |
| `research_and_wait(client, **kwargs)`   | You want one blocking call and only care about the final result.                      |
| `research_background(client, **kwargs)` | You want the task handle immediately—returns `task_id` and `stream_url`.              |
| `poll_research_task(client, task_id)`   | You already have a `task_id`, possibly from another process, and want to wait for it. |
| `stream_research(client, task_id)`      | You want progress events as they happen. Yields `id`, `event`, and `data`.            |

Every helper has an `_async` counterpart (`research_and_wait_async`, `poll_research_task_async`, `stream_research_async`, `research_background_async`) for use with `asyncio`.

For the full background task lifecycle, including the raw endpoints behind these helpers, see the [Research API guide](/docs/guides/research).

## Error Handling

Always handle potential errors when making API requests:

```python
from youdotcom import You, errors

try:
    with You() as you:
        results = you.search(query="your query")
        print(results)
except errors.YouError as e:
    print(f"Search failed: {e.message}")
    print(f"Status code: {e.status_code}")
```

## Learn More

#### [PyPI Package](https://pypi.org/project/youdotcom/)

Install and inspect the published Python SDK package.

#### [GitHub Repository](https://github.com/youdotcom-oss/youdotcom-python-sdk/)

Read the source, generated model docs, and release history.

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema.

#### [Answer API Reference](/docs/api-reference/answer/v1-answer)

Full Answer API parameters and response schema.