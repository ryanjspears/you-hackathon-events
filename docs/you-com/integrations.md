> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Integrations

Every integration wraps the same three APIs—**Web Search**, **Contents**, and **Research**. Switching frameworks is a transport change, not a capability change. One API key works across everything.

## AI Frameworks

#### [crewAI](/docs/integrations/crewai)

Connect You.com's remote MCP server to crewAI agents for real-time web search and content extraction.

#### [LangChain](/docs/integrations/langchain)

`langchain-youdotcom`: `YouSearchTool`, `YouContentsTool`, and `YouRetriever` for agents and RAG pipelines.

#### [LangGraph](/docs/integrations/langgraph)

`YouSearchTool` and `YouContentsTool` in stateful, multi-step workflows.

#### [LlamaIndex](/docs/integrations/llamaindex)

`llama-index-retrievers-you` for real-time web and news retrieval.

#### [Vercel AI SDK](/docs/integrations/vercel-ai-sdk)

`@youdotcom-oss/ai-sdk-plugin`: `youSearch()` and `youContents()` tools for any AI SDK app.

#### [Temporal](/docs/integrations/temporal)

`youdotcom-temporal`: durable activities for search, answer, research, finance research, and contents with crash recovery and automatic retry.

## Automation Platforms

#### [n8n](/docs/integrations/n8n)

`@youdotcom-oss/n8n-nodes-youdotcom` community node for workflows and AI agents.

#### [Zapier](/docs/integrations/zapier)

Connect Web Search, Contents, and Research to 8,000+ apps, no code required.

## Open Models

#### [OpenAI GPT OSS](/docs/integrations/gpt-oss)

You.com powers the default web browsing backend for OpenAI's open-weight GPT OSS models via `YouComBackend`.

## Agent Runtimes

#### [Daytona](/docs/integrations/daytona)

You.com is on Daytona's essential-services allow list. Covers Daytona Secrets, the two API hosts, and the `domain_allow_list` entries a locked-down sandbox needs.

## Also Available

First-party surfaces for connecting You.com to your tools:

[MCP Server](/docs/build-with-agents/mcp-server) · [Agent Skills](/docs/build-with-agents/skills) · [Agent Harnesses](/docs/build-with-agents/agent-harnesses/codex-cli) (Claude Code, Cursor, Windsurf, and more) · [Python SDK](/docs/sdks/python-sdk) · [TypeScript SDK](/docs/sdks/typescript-sdk)

## Don't See Your Stack?

[Request an integration](https://you.com/support)—or call the [REST API](/docs/api-reference/search/v1-search) directly. Anything you can do through an integration, you can do with an HTTP request.