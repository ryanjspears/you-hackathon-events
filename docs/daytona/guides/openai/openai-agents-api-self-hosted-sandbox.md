# Run OpenAI Agents API Sessions in Daytona Sandboxes

This guide shows how to run an [OpenAI Agents API](https://developers.openai.com/api/docs/guides/agents-api/overview) session in a Daytona sandbox. OpenAI hosts the agent — the Codex harness that plans, calls tools, manages context, and recovers from failures — while Daytona provides the isolated sandbox where the agent runs commands, edits files, and produces artifacts.

Unlike the [OpenAI Agents SDK](https://www.daytona.io/docs/en/guides/openai/openai-agents-sdk-with-sandboxes.md), where you host the agent loop yourself, the Agents API runs the harness as a managed service. You provide only the sandbox. The sandbox runs `codex exec-server`, which dials out to OpenAI and registers as the session's execution environment — no inbound ports are exposed.

For the canonical reference, see OpenAI's [Daytona provider guide](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/daytona) and [self-hosted sandboxes](https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted).

---

### 1. Workflow Overview

Your application creates a session, connects a Daytona sandbox to it, submits a task, and streams the agent's output:

```
$ python application_managed.py
created session sess_004b53f8...
started sandbox f7e3b507-...

1. **Baseline current behavior:** Inventory entry points and blocking database/HTTP calls. Add regression tests for responses, errors, side effects, and transaction behavior.

2. **Define async boundaries:** Plan async request handling and I/O while preserving public API contracts and business rules. Retain a compatibility adapter if callers require synchronous interfaces.

3. **Migrate database access:** Adopt an async driver and connection pool; await database operations while preserving queries, transaction boundaries, and rollback behavior.

4. **Migrate HTTP access:** Use a shared async HTTP client; preserve timeouts, retries, authentication, and error mapping. Await calls in their existing order to avoid changing behavior.

5. **Validate and roll out:** Run regression, integration, and load tests; check for event-loop blocking and resource leaks. Deploy incrementally with monitoring and a tested rollback path.
```

The pieces that make this work:

- **Harness (OpenAI):** decides what the agent does and manages the session.
- **Sandbox (Daytona):** the computer where the agent runs commands and edits files.
- **Executor (`codex exec-server`):** a lightweight worker in the sandbox that connects it to the session over an outbound WebSocket.

When you create a self-hosted session you receive an environment ID and a session-specific `remote_url`. Whatever machine runs `codex exec-server --remote <remote_url> --environment-id <id>` becomes that session's environment.

### 2. Project Setup

#### Clone the Repository

```bash
git clone https://github.com/daytona/guides.git
cd guides/python/openai/agents-api
```

#### Configure Environment

The Agents API uses **two** OpenAI keys so the credential exposed to sandbox code is minimal:

- **`OPENAI_API_KEY`** — application key. Creates and streams sessions and runs model inference. Stays on your machine, never enters the sandbox. Grant it **`api.agents.read`**, **`api.agents.write`**, and **`api.responses.write`**.
- **`OPENAI_EXECUTOR_API_KEY`** — executor key. The only credential passed into the sandbox. Create it as a restricted **environment key** with **`api.agents.environments.connect`** and every other permission set to **None**.

Create the application key from the [OpenAI Developer Platform](https://platform.openai.com/api-keys) and the executor key on the [Agents tab](https://platform.openai.com/agents?tab=environments&environment_view=keys), both for the same organization, project, and user or service account that owns the session. Get your Daytona key from the [Daytona Dashboard](https://app.daytona.io/dashboard/keys).

Copy `.env.example` to `.env` and add your keys:

```bash
OPENAI_API_KEY=your_openai_application_key
OPENAI_EXECUTOR_API_KEY=your_openai_executor_key
DAYTONA_API_KEY=your_daytona_key
```

:::caution[The executor key is readable by agent code]
Agent-generated commands inherit the executor process environment and can read `CODEX_API_KEY`. Scope it to **`api.agents.environments.connect`** only so its exposure is harmless, and never place your application key in the sandbox.
:::

#### Install and Run

```bash
pip install openai daytona python-dotenv
python application_managed.py
```

### 3. Understanding the Integration

#### Create the session

Creating a session with `environment.type = "self_hosted"` returns an environment ID and a session-specific `remote_url`. The application key is used here and never leaves your machine:

```python
with OpenAI(api_key=application_api_key) as client:
    daytona = Daytona()

    session = client.beta.agents.sessions.create(
        agent={
            "model": "gpt-6-astra",
            "instructions": "Work from files in /home/daytona/workspace and answer concisely.",
        },
        environment={"type": "self_hosted", "workspace_directory": WORKSPACE},
    )
```

#### Start the sandbox and executor

The sandbox is created from a Debian image with Node.js and the Codex CLI. Only the restricted executor key is injected, and the executor is launched in a background process session with the environment ID and remote URL from the session:

```python
sandbox = daytona.create(
    CreateSandboxFromImageParams(
        image=build_image(),
        env_vars={"CODEX_API_KEY": executor_api_key},
        labels={"agents-api-environment-id": session.environment.id},
        auto_stop_interval=0,
        ttl_minutes=15,
    ),
    timeout=0,
)

command = shlex.join(
    [
        "codex",
        "exec-server",
        "--remote",
        session.environment.remote_url,
        "--environment-id",
        session.environment.id,
    ]
)
sandbox.process.create_session(EXEC_SESSION)
sandbox.process.execute_session_command(
    EXEC_SESSION,
    SessionExecuteRequest(command=f"cd {WORKSPACE} && exec {command}", run_async=True),
)
```

The executor connects outbound: HTTPS to `api.openai.com` to register, and a WebSocket to `codex-cloud-environments.chatgpt.com` for the agent's commands and results. Pass the `remote_url` through unchanged, including on reconnect.

#### Why `auto_stop_interval=0`

The executor's connection is an outbound, long-lived WebSocket that Daytona's inactivity tracking does not observe, so a running-but-quiet sandbox can look idle. Disabling auto-stop prevents the sandbox from being stopped mid-turn; `ttl_minutes` bounds its lifetime if a run is interrupted. To release compute between turns instead, use the webhook-managed pattern below.

#### Send input and stream

Start the sandbox before submitting input. Subscribe to the event stream, then send input on the same session. The turn waits for the environment to connect, reported by `agent.session.environment.connected`:

```python
with client.beta.agents.sessions.events.stream(session.id) as events:
    client.beta.agents.sessions.events.create(
        session.id,
        events=[
            {
                "type": "agent.session.input.message",
                "input": [{"role": "user", "content": [{"type": "input_text", "text": TASK}]}],
            }
        ],
    )
    for event in events:
        if event.type == "agent.session.turn.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "agent.session.turn.completed" and event.turn.subagent_id is None:
            break
```

Use `agent.session.turn.completed` to identify a successful turn. A failed or cancelled turn can also be followed by `agent.session.idle`, so do not treat an idle session as proof that the turn succeeded.

#### Clean up

The sandbox and session are server-side resources. Delete the session while its environment is still connected, then remove the sandbox:

```python
try:
    ...  # start the sandbox and stream the turn (shown above)
finally:
    client.beta.agents.sessions.delete(session.id)
    if sandbox is not None:
        sandbox.delete()
```

### 4. Application-managed vs Webhook-managed

The runnable example in this guide is **application-managed**: one process owns the whole session and keeps the sandbox up for its duration. It is the simplest shape and the right one for short, interactive runs.

For long-running or many-session workloads, use the **webhook-managed** pattern to release compute between turns:

- Stop the sandbox when the session goes idle. Daytona's stop/start preserves the sandbox filesystem across turns.
- When new input arrives for a disconnected environment, OpenAI emits an `agent.session.action_required` (`environment_connection`) webhook.
- A handler starts or resumes the sandbox and relaunches the executor with the same environment ID and remote URL.

The companion `webhook_managed.py` implements the core of that handler — `connect_worker(...)` creates or wakes the sandbox by label and relaunches the executor, and `delete_worker(session_id)` tears it down — ready to wire into your own webhook endpoint. See OpenAI's [Daytona provider guide](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/daytona) and [environment lifecycle](https://developers.openai.com/api/docs/guides/agents-api/environments/lifecycle) for the full webhook-managed flow.

### 5. Faster Connect with a Snapshot

Building the image on first use keeps this example self-contained. For regular use, bake Codex and ripgrep into a [Daytona snapshot](https://www.daytona.io/docs/en/snapshots.md) so the sandbox connects sooner instead of installing packages on every run.

### 6. A Note on Daytona Secrets

Other guides inject the OpenAI key with [Daytona Secrets](https://www.daytona.io/docs/en/secrets.md), which keep the raw value out of the sandbox and substitute it into outbound HTTPS request headers. That works for tools that call `https://api.openai.com` directly. It is **not** currently suitable for the Agents API executor: its data plane is a WebSocket to `codex-cloud-environments.chatgpt.com`, and Secret substitution on that upgraded connection is not yet supported. Pass the executor key as an environment variable and keep it least-privilege (`api.agents.environments.connect`) so its exposure to sandbox code is harmless.

**Key advantages:**

- OpenAI-hosted harness with durable sessions, context management, and recovery
- Agent code runs in an isolated Daytona sandbox you control
- Least-privilege executor credential, kept separate from your application key
- Bring-your-own image, with snapshots for fast connect
- Application-managed and webhook-managed provisioning for both interactive and long-running workloads