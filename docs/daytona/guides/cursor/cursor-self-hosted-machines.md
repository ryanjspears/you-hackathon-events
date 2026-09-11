# Run Cursor Self-Hosted Machines on Daytona

### Cursor Cloud Agents

Cursor Cloud Agents work asynchronously on repositories. They inspect code, edit files, run commands and tests, and respond to follow-up messages while users track progress in Cursor.

Self-Hosted Machines moves Cloud Agent tool execution to machines you manage. Cursor continues to host the agent control plane and user experience. You control where workers run and which operating system, tools, dependencies, and network access they use. For teams, a Self-Hosted Pool adds shared worker capacity with service-account authentication.

This guide shows how to run Cursor Self-Hosted Machines on Daytona through a Self-Hosted Pool.

### How it works

We provide a runnable reference implementation for running Cursor Self-Hosted Pool workers on Daytona. The code lives in [`python/cursor/self-hosted-machines/`](https://github.com/daytona/guides/tree/main/python/cursor/self-hosted-machines).

For example, a `daytona-windows` pool uses Cursor's controller to run our `spawn-cursor-self-hosted-worker` command. The command creates a Daytona sandbox from the configured Windows snapshot. The worker runs inside that sandbox until the request finishes.

The same sequence applies to every sandbox class:

1. A user selects a Daytona pool for a Cloud Agent request.
2. `agent worker controller` claims the request from Cursor.
3. The controller runs `spawn-cursor-self-hosted-worker`.
4. The spawn helper creates a sandbox from `SNAPSHOT_NAME` and sets the requested repository as the workspace `origin`.
5. The Cursor worker starts inside the sandbox and connects to Cursor.
6. Cursor mints a short-lived GitHub token for the run, and the checkout hook fetches the requested branch into the workspace.
7. `monitor-cursor-self-hosted-worker` deletes the sandbox after the worker exits.

Each claimed request gets one sandbox and one worker process. Follow-up messages can reuse that worker during `CURSOR_WORKER_IDLE_RELEASE_TIMEOUT`.

If worker startup fails, the spawn helper releases the request and deletes the sandbox.

### Set up

The setup combines two parts:

- Cursor provides `agent worker controller`, which claims requests from a Self-Hosted Pool. Cursor currently provides this command through the Cursor CLI lab channel.
- We provide the snapshot builders, spawn helper, and sandbox monitor in the Daytona guides repository.

Our spawn helper connects to Cursor's controller through the controller's `--spawn` option.

#### Requirements

You need:

- A Cursor Enterprise team.
- A Cursor service-account API key.
- A [Daytona API key](https://app.daytona.io/dashboard/keys).
- A macOS or Linux host with Python 3.12 or newer.
- Outbound HTTPS access from the controller host.

The controller host remains macOS or Linux for all sandbox classes. A Windows pool runs the worker inside a Windows sandbox.

#### Get the code

Clone the Daytona guides repository and install the package:

```bash
git clone https://github.com/daytona/guides.git
cd guides/python/cursor/self-hosted-machines

python3.12 -m venv .venv
source .venv/bin/activate

pip install -e .
cp .env.example .env
```

This package installs:

- `build-cursor-self-hosted-snapshot`
- `spawn-cursor-self-hosted-worker`
- `monitor-cursor-self-hosted-worker`

#### Install the Cursor controller

Install the Cursor CLI from its lab channel:

```bash
curl 'https://cursor.com/install?channel=lab' -fsS | bash
export PATH="$HOME/.local/bin:$PATH"

agent --version
agent worker controller --help
```

If the Cursor CLI is already installed, switch it to the lab channel:

```bash
agent set-channel lab
agent update
```

`agent worker controller --help` must include the `--spawn` option.

#### Configure Cursor

A Cursor team administrator must configure the team:

1. Open **Dashboard > Settings > API Keys > Service Accounts**.
2. Create a service account for the Daytona pool.
3. Copy the service-account API key.
4. Open **Dashboard > Cloud Agents > Self-Hosted**.
5. Enable **Allow Self-Hosted Agents**.
6. Enable GitHub token minting for self-hosted workers.
7. Open **Dashboard > Settings > Integrations**.
8. Connect the Cursor GitHub App at the team level.
9. Give the GitHub App access to each repository that the pool will use.

Set the service-account API key as `CURSOR_API_KEY`. Other Cursor API-key types cannot start pool workers.

The spawn command sets the requested repository as the workspace `origin`, and the worker starts with `agent worker --mint-github-token --on-session-start <checkout hook>`. When Cursor claims the worker, it mints a short-lived GitHub token for the run, and the checkout hook fetches the requested ref into the workspace. Do not add a GitHub personal access token to `.env`.

#### Build a Daytona snapshot

Add both API keys to `.env`. Leave `SNAPSHOT_NAME` empty for the first build.

```dotenv
DAYTONA_API_KEY=replace-with-your-daytona-api-key
DAYTONA_TARGET=us
SNAPSHOT_NAME=
CURSOR_API_KEY=replace-with-your-cursor-service-account-key
```

Choose the sandbox class for the pool:

| **Sandbox class** | **Guest OS** | **Default source**  | **Workspace**             |
| ----------------- | ------------ | ------------------- | ------------------------- |
| `container`       | Linux        | Included Dockerfile | `/home/daytona/workspace` |
| `linux-vm`        | Linux        | `daytona-vm-medium` | `/home/daytona/workspace` |
| `windows`         | Windows      | `windows-medium`    | `C:\cursor\workspace`     |

Build the snapshot:

```bash
# Linux container
build-cursor-self-hosted-snapshot --sandbox-class container --target us

# Linux VM
build-cursor-self-hosted-snapshot \
  --sandbox-class linux-vm \
  --target eu-central-1

# Windows
build-cursor-self-hosted-snapshot --sandbox-class windows --target us
```

The target must support the selected sandbox class. VM targets must also contain the required source snapshot.

The builder derives the snapshot name from the build recipe. It reuses an existing snapshot when the recipe is unchanged.

For a VM build, the builder:

1. Starts a temporary VM.
2. Installs the Cursor worker and required tools.
3. Captures a cold snapshot.
4. Starts a second VM from that snapshot.
5. Confirms that the worker can start.
6. Deletes both temporary VMs.

Copy the returned `snapshot_name` into `SNAPSHOT_NAME`. Keep `DAYTONA_TARGET` set to the target that contains the snapshot.

Each active worker uses one Daytona sandbox. Check your organization's [tier limits](https://www.daytona.io/docs/en/limits.md) before you set pool concurrency.

### Run the controller

Load `.env` and start the controller:

```bash
set -a
. ./.env
set +a

agent worker controller \
  --spawn "$(pwd)/.venv/bin/spawn-cursor-self-hosted-worker" \
  --pool daytona-container
```

The pool name must match the pool selected in Cursor.

Keep the controller process running. It claims requests from the pool and runs the spawn helper for each request.

One controller process uses one pool, one `SNAPSHOT_NAME`, and one `DAYTONA_TARGET`.

Use a separate working directory, `.env` file, and controller process for each sandbox class. For example:

- `daytona-container` uses a `container` snapshot.
- `daytona-linux-vm` uses a `linux-vm` snapshot.
- `daytona-windows` uses a `windows` snapshot.

The spawn helper reads the sandbox class from the snapshot metadata. Do not set a separate sandbox-class environment variable.

Open [Cursor Agents](https://cursor.com/agents), create an agent for an HTTPS GitHub repository, and select the Daytona pool.

The Daytona dashboard shows the sandbox while the worker runs. The monitor deletes the sandbox after the worker exits.

### Controller settings

| **Variable**                         | **Required** | **Purpose**                                                              |
| ------------------------------------ | ------------ | ------------------------------------------------------------------------ |
| `DAYTONA_API_KEY`                    | Yes          | Creates, finds, and deletes Daytona sandboxes.                           |
| `DAYTONA_TARGET`                     | Recommended  | Selects the target that contains the snapshot.                           |
| `SNAPSHOT_NAME`                      | Yes          | Selects the snapshot used for new workers.                               |
| `CURSOR_API_KEY`                     | Yes          | Authenticates the controller and workers with Cursor.                    |
| `CURSOR_WORKER_IDLE_RELEASE_TIMEOUT` | No           | Keeps a worker available for follow-up messages. Default: `900` seconds. |
| `MONITOR_POLL_SECONDS`               | No           | Sets the monitor interval. Default: `5` seconds.                         |
| `SANDBOX_CREATE_TIMEOUT_SECONDS`     | No           | Sets the Daytona create and delete timeout. Default: `120` seconds.      |
| `SANDBOX_LAUNCH_TIMEOUT_SECONDS`     | No           | Sets the worker startup timeout. Default: `60` seconds.                  |

Do not set `CURSOR_AGENT_WORKER_ID`, `CURSOR_POOL`, or `CURSOR_REQUEST_ID`. The Cursor controller sets them for each request.

### Network and credentials

The controller host needs outbound HTTPS access to:

- Cursor
- The Cursor download service
- The Python package index
- The Daytona API

Each sandbox needs outbound HTTPS access to:

- Cursor
- The requested Git host
- Artifact storage
- Package and tool hosts used by the workload

The sandbox does not need an inbound port. The worker management address, `0.0.0.0:8080`, stays inside the sandbox.

The controller holds `DAYTONA_API_KEY` and `CURSOR_API_KEY`. The sandbox receives `CURSOR_API_KEY`, but it never receives `DAYTONA_API_KEY`.

Code inside the sandbox runs as the same operating-system user as the Cursor worker. Use a dedicated, least-privilege Cursor service account for each customer or trust boundary.

The snapshots contain no API keys. The Windows launcher also deletes its temporary environment file after the worker starts.

### Conclusion

Running the workers on Daytona gives you:

- A fresh, isolated sandbox for each claimed request.
- Linux container, Linux VM, and Windows VM pools.
- Control over the operating system, tools, dependencies, and network access.
- Consistent worker environments built from reusable snapshots.
- Faster startup because snapshots can include the required tools and dependencies.
- No inbound network requirement for the worker sandboxes.
- Automatic sandbox cleanup after workers exit.
- Visibility into active workers through the Daytona dashboard.

### Further reading

- [Cursor Self-Hosted Machines](https://cursor.com/docs/cloud-agent/self-hosted)
- [Cursor Self-Hosted Pool](https://cursor.com/docs/cloud-agent/self-hosted/pool)
- [Cursor service accounts](https://cursor.com/docs/account/enterprise/service-accounts)
- [Cursor Cloud Agents API](https://cursor.com/docs/cloud-agent/api/endpoints)
- [Daytona snapshots](https://www.daytona.io/docs/en/snapshots.md)
- [Daytona documentation](https://www.daytona.io/docs/index.md)