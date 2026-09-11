> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Vercel AI SDK

Integrate You.com's real-time web search and webpage content extraction capabilities into any application you've built with Vercel's AI SDK.

The `@youdotcom-oss/ai-sdk-plugin` package provides three ready-made tools for the [Vercel AI SDK](https://sdk.vercel.ai/):

1. `youSearch()` for real-time web and news search
2. `youContents()` for page content extraction
3. `youResearch()` for comprehensive web research with citations

Drop all three into any `generateText`, `streamText`, or `generateObject` call to give your AI application real-time web access.

Starting from scratch? We recommend using Skills, so your agent can build this integration for you. [Learn how](/docs/build-with-agents/skills).

---

## Getting Started

### Install the Package

```bash
npm install @youdotcom-oss/ai-sdk-plugin
```

### Set Your API Key

```bash
export YDC_API_KEY="<YDC_API_KEY>"
```

Get your API key at [you.com/platform](https://you.com/platform).

---

## Usage

#### youSearch

Use `youSearch()` to give a model access to structured real-time web and news results.

```typescript
import { generateText, isStepCount } from "ai";
import { youSearch } from "@youdotcom-oss/ai-sdk-plugin";
import { anthropic } from "@ai-sdk/anthropic";

const { text } = await generateText({
  model: anthropic("claude-sonnet-4-5"),
  prompt: "What happened in San Francisco last week?",
  tools: {
    search: youSearch(),
  },
  stopWhen: isStepCount(3),
});

console.log(text);
```

#### youContents

Use `youContents()` when the model needs to retrieve entire web page content as HTML or markdown.

```typescript
import { generateText, isStepCount } from "ai";
import { youContents } from "@youdotcom-oss/ai-sdk-plugin";
import { anthropic } from "@ai-sdk/anthropic";

const { text } = await generateText({
  model: anthropic("claude-sonnet-4-5"),
  prompt: "Summarize the content from vercel.com/blog",
  tools: {
    extract: youContents(),
  },
  stopWhen: isStepCount(3),
});

console.log(text);
```

#### youResearch

Use `youResearch()` when the model needs comprehensive, synthesized answers with inline citations. The Research API supports effort levels (`lite`, `standard`, `deep`, `exhaustive`, `frontier`) to balance speed against thoroughness—the model selects the appropriate level automatically.

```typescript
import { generateText, isStepCount } from "ai";
import { youResearch } from "@youdotcom-oss/ai-sdk-plugin";
import { anthropic } from "@ai-sdk/anthropic";

const { text } = await generateText({
  model: anthropic("claude-sonnet-4-5"),
  prompt: "What are the tradeoffs between WebSockets and Server-Sent Events for real-time applications?",
  tools: {
    research: youResearch(),
  },
  stopWhen: isStepCount(3),
});

console.log(text);
```

#### All tools

You can provide all three tools at once and let the model decide which to use:

```typescript
import { generateText, isStepCount } from "ai";
import { youSearch, youContents, youResearch } from "@youdotcom-oss/ai-sdk-plugin";
import { anthropic } from "@ai-sdk/anthropic";

const { text } = await generateText({
  model: anthropic("claude-sonnet-4-5"),
  prompt: "Find recent blog posts about the Vercel AI SDK, then extract and summarize the top result.",
  tools: {
    search: youSearch(),
    extract: youContents(),
    research: youResearch(),
  },
  stopWhen: isStepCount(5),
});

console.log(text);
```

#### Explicit API key

If you prefer not to use environment variables, pass the key directly:

```typescript
import { youSearch, youContents, youResearch } from "@youdotcom-oss/ai-sdk-plugin";

const searchTool = youSearch({ apiKey: process.env.YDC_API_KEY });
const contentsTool = youContents({ apiKey: process.env.YDC_API_KEY });
const researchTool = youResearch({ apiKey: process.env.YDC_API_KEY });
```

---

## Resources

#### [GitHub Repository](https://github.com/youdotcom-oss/dx-toolkit/tree/main/packages/ai-sdk-plugin)

Source code for the AI SDK plugin

#### [Vercel AI SDK Docs](https://sdk.vercel.ai/)

Official Vercel AI SDK documentation

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Contents API Reference](/docs/api-reference/contents)

Full Contents API parameters and response schema

#### [Research API Reference](/docs/api-reference/research/v1-research)

Full Research API parameters and response schema