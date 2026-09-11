> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Temporal

Integrate You.com's APIs into [Temporal](https://temporal.io) workflows as durable activities that survive crashes and automatically resume where they left off.

The `youdotcom-temporal` package provides six activities covering every You.com API, wrapped in a `YouPlugin` (a Temporal `SimplePlugin`) for one-line worker setup:

1. `youdotcom_search` for real-time web and news search
2. `youdotcom_answer` for synthesized answers with inline citations
3. `youdotcom_research` for multi-step research with citations
4. `youdotcom_research_background` for long-running background research
5. `youdotcom_finance_research` for finance-focused research
6. `youdotcom_contents` for webpage content extraction

Every activity returns JSON-serializable dicts, maps SDK errors to Temporal error types with correct retryability, and disables the SDK's built-in HTTP retries so Temporal is the single retry authority.

---

## Getting Started

### Install the Package

```bash
pip install youdotcom-temporal
```

### Set Your API Key

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

Get your API key at [you.com/platform](https://you.com/platform).

### Start a Local Temporal Server

```bash
temporal server start-dev
```

---

## Configure Credentials

The plugin reads the API key from the `YDC_API_KEY` environment variable on the worker. Never pass the key as a workflow or activity argument—Temporal records workflow inputs in event history in plaintext.

To override the resolved key programmatically on the worker:

```python
from youdotcom_temporal import YouConfig, set_config

set_config(YouConfig(api_key="your-api-key"))
```

`YouConfig` also accepts `server_url` and `timeout_seconds` (defaults to 300 seconds).

---

## Usage

#### Plugin path (recommended)

Add `YouPlugin()` to your worker and all six activities are auto-registered. The plugin also configures the workflow sandbox to pass through the SDK's runtime modules.

```python
from temporalio.client import Client
from temporalio.worker import Worker
from youdotcom_temporal import YouPlugin

from hello_search_workflow import HelloSearch  # see examples/

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="you-search",
        workflows=[HelloSearch],
        plugins=[YouPlugin()],
    )
    await worker.run()
```

#### Manual path

If you prefer to manage your own worker wiring:

```python
from temporalio.worker import Worker
from youdotcom_temporal import you_activities

worker = Worker(
    client,
    task_queue="you-search",
    workflows=[HelloSearch],
    activities=you_activities(),
)
```

#### Search activity

Pass `extraction` to control livecrawl output format. It takes priority over the deprecated `livecrawl` and `livecrawl_formats` fields.

```python
from datetime import timedelta

from youdotcom_temporal import SearchInput, youdotcom_search

result = await workflow.execute_activity(
    youdotcom_search,
    SearchInput(query="latest AI news", count=5),
    start_to_close_timeout=timedelta(seconds=30),
)
```

#### Answer activity

```python
from datetime import timedelta

from youdotcom_temporal import AnswerInput, youdotcom_answer

result = await workflow.execute_activity(
    youdotcom_answer,
    AnswerInput(query="What caused the 2008 financial crisis?"),
    start_to_close_timeout=timedelta(seconds=30),
)
```

#### Research activity

Multi-step research with citations. Choose an effort level to balance latency against quality: `lite` is fastest, `standard` and `deep` are balanced, and `exhaustive` and `frontier` are the most thorough.

```python
from datetime import timedelta

from youdotcom_temporal import ResearchInput, youdotcom_research

result = await workflow.execute_activity(
    youdotcom_research,
    ResearchInput(input="Compare quantum computing approaches", research_effort="standard"),
    start_to_close_timeout=timedelta(minutes=2),
)
```

#### Background research

Long-running research that submits, streams via SSE, and polls until completion. Valid effort levels are `lite`, `standard`, `deep`, `exhaustive`, and `frontier`—`frontier` can run up to 4 hours. When `timeout_s` is omitted, the SDK derives a default from the effort level—600 seconds for standard, 14,400 seconds for frontier.

```python
from datetime import timedelta

from youdotcom_temporal import ResearchInput, youdotcom_research_background

result = await workflow.execute_activity(
    youdotcom_research_background,
    ResearchInput(
        input="Compare quantum computing approaches",
        research_effort="lite",
        timeout_s=120.0,
    ),
    start_to_close_timeout=timedelta(minutes=5),
)
```

#### Finance research activity

Finance-focused research with citations. Accepts `deep` or `exhaustive` effort.

```python
from datetime import timedelta

from youdotcom_temporal import FinanceResearchInput, youdotcom_finance_research

result = await workflow.execute_activity(
    youdotcom_finance_research,
    FinanceResearchInput(input="Analyze AAPL earnings trends", research_effort="deep"),
    start_to_close_timeout=timedelta(minutes=5),
)
```

#### Webpage contents

Fetch one or more URLs as HTML, markdown, or metadata.

```python
from datetime import timedelta

from youdotcom_temporal import ContentsInput, youdotcom_contents

result = await workflow.execute_activity(
    youdotcom_contents,
    ContentsInput(urls=["https://example.com"], formats=["markdown"]),
    start_to_close_timeout=timedelta(seconds=60),
)
```

---

## Activities

| Activity                        | Input                  | Description                                                               |
| ------------------------------- | ---------------------- | ------------------------------------------------------------------------- |
| `youdotcom_search`              | `SearchInput`          | Web and news search results                                               |
| `youdotcom_answer`              | `AnswerInput`          | Synthesized answer with inline citations                                  |
| `youdotcom_research`            | `ResearchInput`        | Multi-step research with citations                                        |
| `youdotcom_research_background` | `ResearchInput`        | Long-running background research (submits, streams, polls until complete) |
| `youdotcom_finance_research`    | `FinanceResearchInput` | Finance-focused research with citations                                   |
| `youdotcom_contents`            | `ContentsInput`        | Webpage content as HTML, markdown, or metadata                            |

## Error Handling

| HTTP status  | Error type           | Retryable?              |
| ------------ | -------------------- | ----------------------- |
| 401, 403     | `YouAuthError`       | No                      |
| 422          | `YouValidationError` | No                      |
| 402          | `YouQuotaExhausted`  | No                      |
| 429          | (passthrough)        | Yes, Temporal backs off |
| 5xx          | (passthrough)        | Yes, Temporal backs off |
| HTTP timeout | `YouTimeoutError`    | Yes, Temporal backs off |

The SDK's built-in HTTP retries are disabled so Temporal is the single retry authority. Set `RetryPolicy` on `workflow.execute_activity` to control backoff and max attempts.

---

## Resources

#### [GitHub Repository](https://github.com/youdotcom-oss/youdotcom-temporal)

Source code, examples, and CHANGELOG

#### [PyPI](https://pypi.org/project/youdotcom-temporal/)

Install with pip install youdotcom-temporal

#### [Temporal Docs](https://docs.temporal.io/develop/python)

Official Temporal Python SDK documentation

#### [Python SDK](/docs/sdks/python-sdk)

You.com Python SDK used by the plugin

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Research API Reference](/docs/api-reference/research/v1-research)

Full Research API parameters and response schema

#### [Answer API Reference](/docs/api-reference/answer/v1-answer)

Full Answer API parameters and response schema

#### [Contents API Reference](/docs/api-reference/contents)

Full Contents API parameters and response schema

#### [Finance Research API Reference](/docs/api-reference/finance-research/v1-finance_research)

Full Finance Research API parameters and response schema