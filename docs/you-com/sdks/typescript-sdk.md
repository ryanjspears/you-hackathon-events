> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# TypeScript SDK

We offer a TypeScript SDK to make interacting with our APIs simple and predictable. It is available on npm [here](https://www.npmjs.com/package/@youdotcom-oss/sdk).
Now you can get started with our APIs with just a few lines of code.

#### Install our docs MCP server

This documentation ships with a Docs MCP Server that gives any MCP-enabled agent a `searchDocs` tool to search every page here and get back relevant passages with source URLs—no API key required. Point your client at `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/build-with-agents/docs-mcp-server) for setup and examples.

## Quickstart

### Get an API Key

Get one for free on the [You.com platform](https://you.com/platform/).

### Install the SDK

```bash
npm add @youdotcom-oss/sdk
```

### Run a Search

Perform a simple search to retrieve results from general web and news sources.

```typescript
import { You } from "@youdotcom-oss/sdk";

// Initialize the SDK with your API key
const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function main() {
  // Perform a search
  const results = await you.search({
    query: "latest AI developments",
  });

  // Access the results
  console.log(results);
}

main();
```

That's it. You now have a comprehensive set of search results combining web and news sources.

## What's next?

The Web Search API offers filters that can help you find exactly what you need, whether you want to go broader or narrower. For example, to find recent information in the United States about renewable energy from the past week limited to 10 results per source type, either `web` or `news`, write:

```typescript
import { You } from "@youdotcom-oss/sdk";
import { Freshness, Country } from "@youdotcom-oss/sdk/models";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function main() {
  const results = await you.search({
    query: "renewable energy",
    count: 10,
    freshness: Freshness.Week,
    country: Country.Us,
  });

  console.log(results);
}

main();
```

Learn more about the Web Search API in the [Web Search API reference](/docs/api-reference/search/v1-search), and the TypeScript SDK by visiting the open source repository on [GitHub](https://github.com/youdotcom-oss/youdotcom-typescript-sdk/).

## Response Structure

The Web Search API returns a `SearchResponse` object (see [documentation](https://github.com/youdotcom-oss/youdotcom-typescript-sdk/blob/main/docs/models/operations/searchresponse.md)):

#### results.web

An array of web result objects. Each object may include `url`, `title`, `description`, `snippets`, `thumbnailUrl`, `pageAge`, and `faviconUrl`.

#### results.news

An array of news article objects. Each object may include `url`, `title`, `description`, `thumbnailUrl`, and `pageAge`.

#### metadata

Information about the search query and response, including `query`, `searchUuid`, and `latency`.

## Error Handling

Always handle potential errors when making API requests:

```typescript
import { You } from "@youdotcom-oss/sdk";
import { YouError } from "@youdotcom-oss/sdk/models/errors";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

async function main() {
  try {
    const results = await you.search({ query: "your query" });
    console.log(results);
  } catch (error) {
    if (error instanceof YouError) {
      console.error(`Search failed: ${error.message}`);
      console.error(`Status code: ${error.statusCode}`);
    } else {
      console.error("An unexpected error occurred:", error);
    }
  }
}

main();
```

## Learn More

#### [npm Package](https://www.npmjs.com/package/@youdotcom-oss/sdk)

Install and inspect the published TypeScript SDK package.

#### [GitHub Repository](https://github.com/youdotcom-oss/youdotcom-typescript-sdk)

Read the source, generated model docs, and release history.

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema.