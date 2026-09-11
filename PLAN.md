# Hackathon plan — Build with YOU: The Live Web Agent Hackathon

> **2026-09-11 pivot:** the project is now **Events Scanner** (chat → You.com event search via One → Daytona-cleaned events → learned preferences + recommendations). Architecture and status live in `ARCH.md`; the Dep Doctor material below is kept for reference only.

NYC, 2026-09-11. **Theme: self-repairing & learning agents.** Required vendors: **You.com, One, Daytona, CrewAI.** Official brief (requirements + judging rubric): `docs/hackathon-brief.md`. Sources: `docs/one-skill.md`, `docs/one-hackathon-page.md`, `docs/you-com/`, `docs/daytona/`.

## Hard constraints (from the One skill — verified 2026-09-10)

- The **crew runs on the laptop**. It gets One's four tools via `npx -y @withone/mcp` (CrewAI `MCPServerAdapter`) and drives **You.com and Daytona through One**. Sandbox egress blocks `*.withone.ai`, so nothing One-driven can run *inside* a sandbox. `api.you.com` **is** reachable from inside a sandbox.
- CrewAI needs **Python 3.10–3.13** locally (3.14 breaks). Pins: `crewai[anthropic]==1.15.2`, `crewai-tools[mcp]==1.15.2`, `mcp~=1.26.0`, `mcpadapt>=0.1.9,<0.2`. Apply the skill's `dropping_nulls` + `harden_execute` wrappers or tool calls fail.
- Daytona default image ships Python 3.14; inside the sandbox use `uv python install 3.12` if a lib needs it. Always set `ttlMinutes` on create; pass `timeout` (seconds) on execute for anything slow (default 10s). Sandbox ids: `sandboxIdOrName` for lifecycle actions, `sandboxId` for in-sandbox actions.
- Never hardcode One `actionId`s — resolve at runtime via `search_one_platform_actions`, read knowledge, then execute. GET `/v1/search` and POST share a title; pick by method.
- `.env` for the crew: `ANTHROPIC_API_KEY`, `ONE_SECRET` (same key the CLI uses), `ONE_CONNECTION_KEYS=live::you::…,live::daytona::…,…`.
- Learning: `one mem add note '{"content": …}' --tags … --weight N` after each run; `one mem search` before the next. First `one mem` call bootstraps embedded Postgres (~25s).
- Demo convention judges expect: run twice; print `Recalled:` and `Learned:` lines so the second run visibly benefits.

## Deliverables (from `docs/hackathon-brief.md`)

- [ ] Public GitHub repo, organized, README covers setup end-to-end
- [ ] 1–3 min YouTube demo video (show run 1 → `Learned:`, run 2 → `Recalled:`, and the real-system side effect)
- [ ] 200-word description: problem, tech stack, API use
- [ ] ≥1 You.com endpoint + CrewAI + Daytona + One all load-bearing
- [ ] "Clean Data" requirement — confirm with organizers what this means (a partner? no scraped/PII data?)

Rubric (1–5 each): completed the loop (changed something in a real system), technical implementation, innovation, impact, presentation/docs. "Completed the loop" is why the Publisher step (PR / email) is not optional.

## What "all four vendors" looks like in one loop

```
CrewAI crew (laptop)
  ├─ Researcher ──One──▶ you: /v1/search, /v1/contents, /v1/research   (find facts / docs / changelogs)
  ├─ Builder ─────One──▶ daytona: create sandbox, write files, execute, read exitCode+result
  │        ◀── error ──┘  fix → execute again   (the self-repair loop)
  ├─ Publisher ───One──▶ gmail / slack / github / notion / linear   (a real side effect)
  └─ Memory ──────one mem add / one mem search   (the learning loop)
```

## Candidate projects (all use the loop above)

| # | Idea | Repair loop | Learning loop | Side effect | Stands out because |
|---|------|-------------|---------------|-------------|--------------------|
| **A** | **Dep Doctor** — point it at a repo; it upgrades outdated dependencies safely. Researcher pulls each package's changelog / migration guide / CVEs with You.com; Builder clones the repo into a sandbox, bumps versions, runs the tests, reads failures, patches, reruns. | Test failures → targeted fix (e.g. pydantic `.dict()`→`.model_dump()`) → rerun until green | Per-package fixes saved to `one mem`; on the next repo the Builder applies known migrations *before* running tests and reports `Recalled:` | Opens a GitHub PR via One with a changelog citing the You.com sources | Every judge has felt this pain; the "second repo upgrades first try" moment is a clean learning demo; ends in a real PR |
| B | **Docs → Working Example** — give it a library + task ("use Temporal to schedule a job"); Contents API reads the docs, crew writes a runnable example, runs it in a sandbox, repairs until it exits 0. | Runtime error → re-read the relevant doc section via Contents → fix | Remembers per-library gotchas (env vars, version pins, Python 3.14 issues) | Pushes the example to a GitHub repo / gist; posts link to Slack | Shows You.com Contents doing something only it can do (clean Markdown of any docs page) |
| C | **Issue Reproducer** — paste a GitHub issue URL; crew reads the issue and linked discussion (Contents + Search), writes a minimal repro in a sandbox, confirms it fails, tries candidate fixes, comments on the issue with the confirmed repro and a patch. | "Doesn't reproduce" → search for related issues/versions → adjust env → retry | Remembers which repro strategies worked per language/framework | Comments on the GitHub issue via One | Very "self-repairing"; maintainers would use it tomorrow |
| D | **Benchmark Bot** — "is X faster than Y for Z?"; Research API finds candidate approaches, crew writes benchmark scripts, runs them in a sandbox, charts results, posts to Slack/Notion. | Script crashes / harness bugs → fix from stderr | Remembers harness fixes and which libraries need pins | Slack post with PNG + Notion page | Closest to template #1 (research→chart→email) but with a more useful question |

## Recommendation: A (Dep Doctor)

- **Clearest learning story.** Run 1 on `demo-repo-a`: pydantic 1→2 breaks tests, Builder repairs, `Learned: pydantic>=2 renames .dict()→.model_dump()`. Run 2 on `demo-repo-b` (same dep): `Recalled: …`, applies the fix pre-emptively, tests green on first execute. Judges see the difference in under a minute.
- **Every vendor is load-bearing**, not decorative: You.com supplies the migration knowledge (Search + Contents on changelogs; Research for "what breaks when upgrading X from 1 to 2"), Daytona is the only safe place to run someone else's tests, One is the single interface to all of it plus GitHub, CrewAI orchestrates Researcher → Builder → Publisher.
- **Scope-controllable.** Ship with two tiny demo repos whose breakages are known. Real-world repos are a stretch goal.

### Build order

1. **Plumbing (do first, it's where time goes):** `one add you`, `one add daytona`, `one add github`; `one --agent list` and copy keys into `ONE_CONNECTION_KEYS`. Python 3.12 venv, pinned requirements, run the skill's CrewAI example once end-to-end to prove tools work.
2. **Sandbox harness:** create (with `ttlMinutes`) → `git/clone` demo repo → install → run tests → parse `exitCode` + `result` → delete. Verify from the CLI before the crew touches it.
3. **Researcher task:** for each outdated dep (parse `requirements.txt`/`package.json`), You.com Search for "`<pkg>` `<old>` to `<new>` migration guide breaking changes", Contents on the top hit, summarize the breaking changes with URLs.
4. **Builder task:** bump, run tests, on failure feed error + Researcher notes to the LLM, patch via a `cat > file <<'EOF'` execute, rerun. Cap at N iterations.
5. **Memory:** after success, `one mem add` `{package, from, to, symptom, fix}` with `--tags depdoctor,<pkg>`; at start, `one mem search "<pkg> <new version>"` and inject hits into the Builder's context. Print `Recalled:` / `Learned:`.
6. **Publisher:** GitHub create-branch + commit + open PR via One, body cites the You.com sources.
7. Demo repos: `demo-repo-a` (pydantic 1.x + requests pin), `demo-repo-b` (pydantic 1.x + a second known-breaking upgrade).
8. Stretch: a small web UI or Slack post showing the run log; Relay trigger on "PR opened" so the loop runs unattended.

## Fallbacks

- If One↔Daytona is flaky on the day: the Builder can call Daytona's SDK directly (`pip install daytona`, `DAYTONA_API_KEY`) — still uses Daytona, One still covers You.com + GitHub.
- If GitHub PR creation eats time: Publisher emails the diff via Gmail (the template pattern, known to work).
- If Dep Doctor stalls on plumbing by early afternoon: pivot to B, which reuses everything except the git clone + test run.
