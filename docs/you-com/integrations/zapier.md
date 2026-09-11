> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Zapier

The You.com Zapier integration connects the Search, Content, and News APIs to more than 8,000 apps—no code required. Build automated workflows that pull real-time web data and route results to Slack, Google Sheets, Notion, Airtable, Gmail, or anywhere else you work.

---

## Getting Started

### Go to the You.com Zapier integration

Visit [zapier.com/apps/youcom/integrations](https://zapier.com/apps/youcom/integrations) and click **Connect You.com**.

### Authenticate with your API key

When prompted, enter your You.com API key. Get one at [you.com/platform](https://you.com/platform).

### Create a Zap

Choose a trigger (any Zapier-supported app or schedule) and add a You.com action step. Configure your query and map the results to your destination app.

---

## Available Actions

#### Web Search

Runs a query against the You.com Web Search API and returns structured web results.

#### Content Extraction

Fetches the full text of one or more URLs as clean Markdown or HTML.

#### News Search

Returns breaking news articles from hundreds of publishers matching your query.

---

## Example Workflows

#### Research Digest to Slack

Trigger on a daily schedule → run a You.com web search → format results → post to a Slack channel.

#### Competitor Pricing Monitor

Trigger weekly → fetch competitor pricing pages → send Markdown to an LLM step → post a summary to Notion or Google Docs.

#### News Alert to Email

Trigger on a schedule → run a You.com News Search → filter results → send matching articles via Gmail.

#### Form-to-Research Pipeline

Trigger from a new Google Sheet row → run a You.com search → append top results back into the sheet.

---

## Resources

#### [You.com on Zapier](https://zapier.com/apps/youcom/integrations)

Browse all available triggers and actions

#### [Fact Checker Tutorial](https://you.com/resources/how-to-build-an-automated-fact-checker-with-you-com-search-api-and-n8n)

Step-by-step guide: build an automated fact checker

#### [Web Search API Reference](/docs/api-reference/search/v1-search)

Full Web Search API parameters and response schema

#### [Contents API Reference](/docs/api-reference/contents)

Full Contents API parameters and response schema