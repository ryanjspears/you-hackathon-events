> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# OpenAI GPT OSS

OpenAI's open-weight GPT OSS models (`gpt-oss-120b` and `gpt-oss-20b`) support a browser tool for real-time web access. You.com is the default backend for this browser tool—providing search, page retrieval, and content extraction via the Web Search API.

When a GPT OSS model needs to search the web, open a page, or find content, it calls You.com under the hood.

---

## Getting Started

### Install the Package

```bash
pip install gpt-oss
```

### Set Your API Key

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

Get your API key at [you.com/platform](https://you.com/platform).

---

## Usage

### Set up the browser tool with YouComBackend

`YouComBackend` connects GPT OSS's browser tool to You.com's Web Search API. The model uses three methods: `search` to find pages, `open` to load a URL, and `find` to locate content within a page.

```python
import datetime
from gpt_oss.tools.simple_browser import SimpleBrowserTool
from gpt_oss.tools.simple_browser.backend import YouComBackend
from openai_harmony import (
    SystemContent,
    Message,
    Conversation,
    Role,
    load_harmony_encoding,
    HarmonyEncodingName,
)

encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

backend = YouComBackend(source="web")
browser_tool = SimpleBrowserTool(backend=backend)

system_content = (
    SystemContent.new()
    .with_conversation_start_date(datetime.datetime.now().strftime("%Y-%m-%d"))
    .with_tools(browser_tool.tool_config)
)

system_message = Message.from_role_and_content(Role.SYSTEM, system_content)
user_message = Message.from_role_and_content(
    Role.USER, "What's the latest news on AI regulation?"
)

conversation = Conversation.from_messages([system_message, user_message])
token_ids = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

# Run inference with your chosen backend (triton, vLLM, etc.)
output_tokens = your_inference_engine(token_ids)

# Parse the model's response
messages = encoding.parse_messages_from_completion_tokens(output_tokens, Role.ASSISTANT)
last_message = messages[-1]

# If the model invokes the browser tool, process the call and re-run inference
if last_message.recipient.startswith("browser"):
    response_messages = await browser_tool.process(last_message)
    messages.extend(response_messages)
```

### How the browser tool works

The model interacts with the browser via three callable actions:

#### search

Searches for a query using You.com Web Search API.

#### open

Opens a specific URL and returns a scrollable window of content.

#### find

Looks for specific text on the currently open page.

The tool uses a scrollable content window to manage context length—the model can fetch an initial set of lines from a page, then scroll forward to load more. This keeps token usage under control while still giving the model access to full page content.

Requests are cached per session, so the model can revisit different sections of a page without triggering another fetch. For this reason, create a new `SimpleBrowserTool` instance for each request.

The model also uses citations from the browser tool in its answers, linking back to the sources it consulted.

---

## Resources

#### [GPT OSS Repository](https://github.com/openai/gpt-oss)

Source code and documentation for OpenAI's GPT OSS models

#### [Browser Tool Source](https://github.com/openai/gpt-oss/blob/main/gpt_oss/tools/simple_browser/backend.py)

YouComBackend implementation in the GPT OSS repo

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Get an API Key](https://you.com/platform)

Sign up to get your You.com API key