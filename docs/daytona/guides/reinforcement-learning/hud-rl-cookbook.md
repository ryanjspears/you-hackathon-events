# Run an RL Coding Environment at Scale with HUD and Daytona

import { Image } from 'astro:assets'

import headerFigure from '../../../../../assets/docs/images/hud-daytona-header.png'
import trainingCurve from '../../../../../assets/docs/images/hud-daytona-training-curve.png'

RL environments became the most debated part of AI this year. Labs are spending billions on them, and most public talks focus on funding and design plans.

This guide follows one tiny coding task through the whole loop. It starts on a laptop, moves to Daytona, scales to 256 parallel sandboxes, and ends with a model that improves from 35.9% to 81.2% on held-out bugs.

<Image
  src={headerFigure}
  alt="Overview of the HUD and Daytona rollout loop: one environment definition running locally, at scale on Daytona sandboxes, and feeding training."
  width={1200}
  style="max-width: 100%; height: auto; margin: 1rem 0;"
/>

---

### 1. What we're building

An [environment](https://docs.hud.ai/v6/reference/environment?utm_source=daytona&utm_medium=partner&utm_content=cookbook) is the world an agent operates in. In this case, it's a small Python repo with failing tests. A task is a prompt for the agent to try, along with a reward that measures its performance. A taskset is the group of tasks you use for evaluation or training. These are the only terms you need for this guide.

Here's the plan: first, define the environment. Next, watch an agent fix a bug on your local machine. Then move the same file to Daytona and run it at scale.

The scale is not for show. One attempt mostly tells you whether the agent got lucky. Many attempts per task give you a pass rate you can trust, and training needs the volume even more: the algorithm learns by comparing groups of attempts on the same task, so a single training step is hundreds of rollouts. The rest of this guide is about making those hundreds fast and cheap.

### 2. The environment

Everything lives in one file, `env.py`. It does three things: declares the environment, gives the agent a place to work, and defines the task.

```python
from hud.environment import Environment

env = Environment(name="smoke")
ws = env.workspace(WORKSPACE, network=True)
```

The workspace is a directory the agent reaches through a shell. Into it we seed two files at the start of every attempt: `calc.py` with a known bug, and `test_calc.py` that catches it. Seeding on every attempt matters, because later we run this 256 times in parallel and each rollout has to begin from the same broken state.

The task itself is one function:

```python
@env.template(id="fix_calc")
async def fix_calc(variant: int = 0):
    seed_bug(variant)
    yield (
        f"`pytest` fails in `{WORKSPACE}`. Fix `calc.py` so it passes. "
        f"Don't edit `test_calc.py`."
    )
    passed, total = await run_pytest()
    yield 1.0 if passed == total else 0.0
```

Read it top to bottom and you have the whole contract. Seed the bug, hand the agent one instruction, wait for it to finish, rerun pytest, and let the [grader](https://docs.hud.ai/v6/reference/graders?utm_source=daytona&utm_medium=partner&utm_content=cookbook) pay 1.0 only if every test passes. The `variant` argument picks which bug gets seeded, which is how one template becomes many tasks later.

One design note: the reward is deliberately all-or-nothing. We tried partial credit first (fraction of tests passing) and it backfired. Most attempts landed between 0.75 and 1.0, so to the training algorithm the attempts in a group looked nearly identical and there was nothing to learn from. Binary is harsher and carries more signal. The [FinQA guide](https://www.daytona.io/docs/guides/reinforcement-learning/openenv-finqa.md) on this site made the same call for the same reason.

### 3. Run it locally

```bash
uv tool install hud-python
hud init            # or follow the quickstart below
hud eval tasks.py claude
```

No API key needed for a local run. The rollout prints the agent's steps, the grader's verdict, and a reward. This is the whole loop, one attempt at a time. If you want the full setup path, use the [quickstart](https://docs.hud.ai/v6/start/quickstart?utm_source=daytona&utm_medium=partner&utm_content=cookbook). Everything after this section is about width.

### 4. Ship it to Daytona

The environment is packaged as a Docker image. The Dockerfile has four lines; the key one installs the required software before copying the source code, so the image's virtual environment stays intact.

`DaytonaRuntime` builds the image into a Daytona snapshot the first time and reuses it after. We name snapshots after a hash of the environment's content, so editing `env.py` produces a new snapshot instead of silently rerunning the old one.

```python
runtime = DaytonaRuntime(SNAPSHOT, image=Image.from_dockerfile("Dockerfile.hud"))
# same task, same agent — only the runtime changed
```

The first run pays for the snapshot build, about 74 seconds. After that, a fresh sandbox takes roughly 1.2 seconds to create and about 3 seconds to be fully usable: create, then our SSH tunnel, then the environment server booting inside. Those measurements are from the SDK's point of view, the time you actually wait.

### 5. Scale it

Same script, 256 rollouts at once.

| **concurrent** | **created** | **time to usable, p50** |
| -------------- | ----------- | ----------------------- |
| 8              | 8/8         | 2.8s                    |
| 32             | 32/32       | 3.3s                    |
| 128            | 128/128     | 5.1s                    |
| 256            | 256/256     | 9.9s                    |

Medians of three repetitions each. This is the default path, nothing enabled.

Across the full ladder, Daytona created 1,272 sandboxes without a single failure. We probed past this: at 512 about 1% of creates fail mid-request, so past 256, batch your waves.

**Tighter batches with warm pools.** For frequent bursts, Daytona can hold sandboxes started ahead of time. You create a warm pool for your snapshot, and each request claims a running sandbox instead of booting one.

Claiming took about half a second at 128 wide. The number that matters more is time to rollout. Warm pools brought that to 4.4s at 128 and 7.3s at 256, compared with 5.1s and 9.9s cold.

The tail improved too. At 256 wide, the spread fell from 2.6s to 1.3s. That matters because a training step waits for the slowest rollout. Reliability held: 768 warm rollouts at 256, one failure.

Two sizing rules from running it. Make the pool at least as large as your batch: a drained pool serves cold until it refills, and refilling after a full drain takes about 13s at 128 and about 28s at 256 (building a pool from empty at 256 takes 38 to 45s). And back-to-back batches with zero gap can outrun the pool, though a real training step leaves minutes of agent time between batches, so in practice it stays full. Claim rules (same snapshot, region, and default resources) are in the [warm-pool docs](https://www.daytona.io/docs/en/warm-pools.md).

### 6. Fork a running sandbox

Everything so far starts from a snapshot. Create the sandbox, open the tunnel, wait for the environment server. Forking changes the unit you copy. Instead of starting from an image, you start from a sandbox that is already warm. `sandbox.fork()` makes a copy-on-write clone with the same disk contents, and in our rollout path the child comes up with the environment ready in under two seconds.

For rollouts, that means you pay the cold-boot cost once. Start one parent, get it fully ready, then fork per attempt. A parent handles one fork at a time, so create forks sequentially, or fan out as a tree once you have several parents. On the current SDK a fork took 0.66s and the child was serving real graded rollouts at 1.78s (p50), against about 3 seconds for the cold create path in section 4.

The more expensive a cold boot is, the more time you save by forking. Nothing downstream changes. A fork is an ordinary sandbox with its own ID, and you reach it the same way as a created one: same SSH tunnel, same access flow.

Forking is available on Daytona's [VM Sandboxes](https://www.daytona.io/docs/en/sandboxes.md).

### 7. Train on the rollouts you just graded

Every rollout above already carries what [training on the HUD](https://docs.hud.ai/v6/guides/training-agents?utm_source=daytona&utm_medium=partner&utm_content=cookbook) needs: the tokens the model produced and the reward the grader paid. So training is not a second pipeline. It's a few lines against the runs you just watched.

```python
GROUP, WIDTH, CHUNK = 8, 128, 16  # 16 variants x 8 attempts = 128 rollouts/step

agent = create_agent(MODEL, completion_kwargs={"extra_body": {"return_token_ids": True}})
trainer = TrainingClient(MODEL)
taskset = Taskset("calc", [fix_calc(variant=v) for v in range(16)])
runtime = DaytonaRuntime(SNAPSHOT, image=Image.from_dockerfile("Dockerfile.hud"))

session = await Job.start("calc-rl", group=GROUP)
for step in range(10):
    start = len(session.runs)
    await taskset.run(agent, runtime=runtime, job=session,
                      group=GROUP, max_concurrent=WIDTH)
    batch = session.runs[start:]  # the 128 runs this step just produced

    # One call with 128 runs is ~37MB of inline tokens and the API rejects it.
    # Successive forward_backward calls accumulate, so chunk on group boundaries
    # and take a single optim_step at the end.
    for i in range(0, len(batch), CHUNK):
        await trainer.forward_backward(batch[i:i + CHUNK], loss_fn="importance_sampling", group_size=GROUP)
    await trainer.optim_step(learning_rate=1e-5)
```

A few things to know before you run it. The `return_token_ids` flag matters because without it, runs come back with no tokens attached, and training quietly learns nothing. Keep chunks aligned to whole groups, since the algorithm compares attempts within each group of 8, and 16 is exactly two groups. And if every reward in a batch comes back the same, the optimizer has nothing to compare, so it skips the step. At 128 rollouts per step that never happens. At 8 it will.

This is why width matters. A single training step needs the whole group of attempts before it can compare them. In this setup, that means 128 rollouts have to finish before one optimizer step can happen.

One calibration note worth stealing regardless of stack: watch the reward spread within each group, not the average. A group where every attempt scores the same teaches nothing, no matter what the average says. Our task calibrates at 35.9% for the base model, a fresh Qwen3.5-4B fork, measured at group size 8 on held-out variants, inside the band where groups disagree and training has signal.

The same runs served three purposes. They tested the environment, measured the model, and became the training batch.

Training on the collected rollouts took the model's held-out pass rate from 35.9% to 81.2% over ten steps. The evaluation bugs were never seen during training, so the curve measures whether the rollouts taught the model the pattern, not whether it memorized the training variants.

<Image
  src={trainingCurve}
  alt="Training curve showing held-out pass rate improving from 35.9% to 81.2% over ten optimizer steps."
  width={1200}
  style="max-width: 100%; height: auto; margin: 1rem 0;"
/>

### 8. Reference

Per-sandbox sizing, measured during live rollouts: 256 MiB peak memory of 1 GB granted, about 5.5 CPU-seconds per 50-second rollout, 247 MB disk of 3 GB. Daytona's default sandbox size is the right one for this environment.

Practical defaults:

- Batch creates at 256.
- Pool at least as large as your batch.
- Name snapshots by content hash.
- Leave rewards binary until group spread tells you otherwise.

#### Configuration reference

| **knob**                          | **value we ran**                                                             |
| --------------------------------- | ---------------------------------------------------------------------------- |
| `hud`                             | **`v0.6.15`**                                                                 |
| `daytona`                         | **`v0.205.1`**                                                                |
| `DaytonaRuntime(snapshot_name=...)` | content-hashed name                                                         |
| sandbox resources                 | 1 vCPU, 1 GB RAM, 3 GB disk (default)                                         |
| `ephemeral`                       | **`True`** (`DaytonaRuntime` default)                                         |
| `auto_stop_interval`              | **`0`** (`DaytonaRuntime` default)                                            |
| create concurrency                | 128 per client                                                                |
| warm pool size                    | ≥ your batch size                                                             |
| warm pool claim                   | same snapshot, region, default resources; no custom env, volumes, or secrets  |
| fork                              | `sandbox.fork()`, one in-flight fork per parent                               |
| group size                        | 8                                                                             |
| tasks per step                    | 16 (128 rollouts)                                                             |

Repo: [hud-python/cookbooks/daytona-rl](https://github.com/hud-evals/hud-python/tree/main/cookbooks/daytona-rl)

HUD quickstart: [docs.hud.ai/v6/start](https://docs.hud.ai/v6/start?utm_source=daytona&utm_medium=partner&utm_content=cookbook)

Daytona: [Documentation](https://www.daytona.io/docs/en.md)