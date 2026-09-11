Building a product your users connect their own apps to?

One Connect: each user grants your app scoped, revocable access to their own tools. One button, two backend routes.

    npx skills add withoneai/connect

    // Any action, through One's passthrough proxy. One injects the platform's
    // credentials; your code never sees an OAuth token. All three headers are required.
    const res = await fetch(
      "https://api.withone.ai/v1/passthrough/v1/search?query=self-repairing+agents&count=5",
      {
        headers: {
          "x-one-secret": process.env.ONE_SECRET!,
          "x-one-connection-key": process.env.ONE_YOU_CONNECTION_KEY!,
          "x-one-action-id": process.env.ONE_YOU_SEARCH_ACTION_ID!, // from `one actions search`
        },
      },
    );
    const { results } = await res.json();


    import { One } from "@withone/sdk";
    import * as gmail from "@withone/sdk/gmail"; // typed actions live on per-platform subpaths

    const one = new One(process.env.ONE_SECRET!);

    // Every action is typed: inputs, output, and the auth it needs.
    const res = await one
      .connection(process.env.ONE_GMAIL_CONNECTION_KEY!)
      .run(
        gmail.createUsersDraft({
          path: { userId: "me" },
          body: { message: { raw: base64Email } },
        }),
      );

    console.log(res.status, res.data);


Build with the sponsors

You.com and Daytona are platforms on One. CrewAI runs One's four tools as a local MCP server.

Live web search, research, and page reading.

The

    you

platform: Search, Research, Finance Research and Get Web Page Contents through the same four tools.

    one add you

Throwaway Linux sandboxes your agent can fail safely in.

The

    daytona

platform: create a sandbox, run commands, move files, delete it. No Daytona SDK in your code.

    one add daytona

Orchestrate a crew of agents that act on real apps.

Hand a crew One's four tools through MCPServerAdapter and

    npx -y @withone/mcp

. Two small helpers make the calls reliable.

    npx -y @withone/mcp --help

Also in partnership with

…and 780+ more apps

Browse every platform

Works in

Use-case templates

Four working templates. Clone one, fill in .env, run it twice and watch the second run use what the first one learned.

Researches with You.com, charts the result in a Daytona sandbox, repairs the script from the error, emails the PNG, and remembers the fix so the next run passes first time.
> “Research the most cited papers on self-repairing agents, chart their citation counts in a sandbox, and email me the PNG.”Read the guide

A crew reads the inbox, skips reports it already filed, reproduces each new bug in a sandbox through One's MCP tools, files it in Linear and posts to Slack.
> “Triage every unread support email, file real bugs in Linear with repro steps, and post the list to #support.”Read the guide

Finance Research on a watchlist, written to Notion and digested in Slack. Tell it what you prefer and the next brief follows it, with a section on what changed since the last one.
> “Every morning at 8, research what moved for my watchlist, save the sourced brief to Notion, and ping #markets.”Read the guide

Reviews a pull request, then turns your replies into rules it applies on the next one. Every review lists which learned rules it used.
> “When a PR is opened, review it using the rules you learned from my earlier feedback, and remember the outcome.”Read the guide

Get help

One engineers answer setup and action questions in real time. Bring the exact command and the error.
