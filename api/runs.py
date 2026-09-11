"""Search runs detached from the SSE connection: heartbeat, watchdog, respawn.

A run is the agent job behind one chat message. It lives in a registry, buffers every progress
event it emits, and is *followed* by SSE streams — so a dropped connection resumes with
`?run=<id>&after=<seq>` instead of losing the search, and a server-side stall is handled here
rather than surfacing as "the connection dropped".

Heartbeat: every `progress.emit` (plan, scan lines, trace spans, the sandbox's 9 s heartbeat)
bumps `last_beat`. The driver checks it while the worker thread runs; if the agent goes quiet
for `RUN_STALL_S` it is cancelled (cooperatively — see `progress.check`) and a fresh run of the
same search is spawned in its place, up to `RUN_MAX_RESPAWNS` times. Streams following the
dead run switch to the replacement automatically, so the UI just sees a note and keeps going.
"""
from __future__ import annotations

import asyncio
import json
import os
import threading
import time
import traceback
import uuid
import weakref
from typing import Callable

from api import progress

STALL_S = float(os.environ.get("RUN_STALL_S", "90"))        # a healthy run emits something every ≤30 s
MAX_RESPAWNS = int(os.environ.get("RUN_MAX_RESPAWNS", "2"))  # fresh runs spawned after a stall, per search
KEEP_S = 900        # finished runs stay attachable this long (a client that reconnects late still gets its result)
PING_S = 10         # keep-alive `ping` event when a followed run is silent (queued, or mid LLM call)

Work = Callable[["Run"], dict]

_runs: dict[str, "Run"] = {}
_slots: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Semaphore]" = weakref.WeakKeyDictionary()


def crew_slot() -> asyncio.Semaphore:
    """One crew at a time (ARCH rule 4). Per event loop so tests can use fresh loops."""
    loop = asyncio.get_running_loop()
    slot = _slots.get(loop)
    if slot is None:
        slot = _slots[loop] = asyncio.Semaphore(1)
    return slot


class Run:
    def __init__(self, work: Work, user: str, message: str, chaos: bool, history: list[dict] | None, attempt: int):
        self.id = uuid.uuid4().hex[:12]
        self.work, self.user, self.message, self.chaos, self.history, self.attempt = work, user, message, chaos, history, attempt
        self.events: list[dict] = []             # every progress payload, in order; `seq` = 1-based index
        self.terminal: dict | None = None        # {"event": done|clarify|error, "data": {...}}
        self.replaced_by: Run | None = None      # the respawned run, when this one stalled
        self.cancel = threading.Event()          # cooperative stop for the worker thread
        self.created = time.time()
        self.started: float | None = None
        self.finished: float | None = None
        self.last_beat = self.created
        self.task: asyncio.Task | None = None
        self._loop = asyncio.get_running_loop()
        self._changed = asyncio.Event()

    # ---- worker side (any thread) ---------------------------------------------------------

    def push(self, payload: dict) -> None:
        """Append a progress event (called by `progress.emit`). A cancelled run's late events are dropped."""
        if self.cancel.is_set():
            return
        payload["seq"] = len(self.events) + 1
        self.events.append(payload)
        self.last_beat = time.time()
        self._wake()

    def beat(self) -> None:
        self.last_beat = time.time()

    def finish(self, event: str, data: dict) -> None:
        self.terminal = {"event": event, "data": data}
        self.finished = time.time()
        self._wake()

    def _wake(self) -> None:
        try:
            self._loop.call_soon_threadsafe(self._notify)
        except RuntimeError:  # loop closed
            pass

    def _notify(self) -> None:
        ev, self._changed = self._changed, asyncio.Event()  # swap so every follower sees exactly one wake-up
        ev.set()

    # ---- stream side (event loop) ---------------------------------------------------------

    @property
    def quiet_s(self) -> float:
        return time.time() - self.last_beat

    def describe(self) -> dict:
        return {"run": self.id, "attempt": self.attempt, "message": self.message}

    async def follow(self, after: int = 0):
        """Yield SSE messages: buffered events from index `after`, then live ones, then the terminal event.
        A stalled run hands the follower over to its replacement."""
        run = self
        yield {"event": "run", "data": json.dumps(run.describe())}
        while True:
            while after < len(run.events):
                ev = run.events[after]
                after += 1
                yield {"event": ev["stage"], "data": json.dumps(ev), "id": f"{run.id}:{after}"}
            if run.terminal is not None:
                if run.replaced_by is not None:
                    run, after = run.replaced_by, 0
                    yield {"event": "run", "data": json.dumps(run.describe())}
                    continue
                yield {"event": run.terminal["event"], "data": json.dumps(run.terminal["data"])}
                return
            changed = run._changed
            try:
                await asyncio.wait_for(changed.wait(), PING_S)
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "{}"}


def get(run_id: str) -> Run | None:
    return _runs.get(run_id)


def spawn(work: Work, user: str, message: str, chaos: bool = False, history: list[dict] | None = None, attempt: int = 1) -> Run:
    """Register a run and start driving it (must be called on the event loop)."""
    _prune()
    run = Run(work, user, message, chaos, history, attempt)
    _runs[run.id] = run
    run.task = asyncio.get_running_loop().create_task(_drive(run), name=f"run-{run.id}")
    return run


def _prune() -> None:
    now = time.time()
    for rid, r in list(_runs.items()):
        if r.finished and now - r.finished > KEEP_S:
            del _runs[rid]


def _worker(run: Run) -> dict:
    progress.bind(run)
    try:
        return run.work(run)
    finally:
        progress.bind(None)


async def _drive(run: Run) -> None:
    t0 = time.time()
    async with crew_slot():
        waited = time.time() - t0
        if waited > 0.5:
            run.push({"stage": "agent", "t": round(time.time(), 3), "text": f"waited {waited:.0f}s for the previous search to finish"})
            print(f"[agent] run {run.id} waited {waited:.1f}s for the crew slot", flush=True)
        run.started = run.last_beat = time.time()
        progress.set_current(run)
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(None, _worker, run)
        tick = min(2.0, max(0.05, STALL_S / 3))
        while True:
            done, _ = await asyncio.wait({fut}, timeout=tick)
            if done:
                break
            if run.quiet_s > STALL_S:
                fut.add_done_callback(_swallow)
                _stall(run)
                return  # releases the crew slot; the orphan thread stops at its next progress.check()
        try:
            payload = fut.result()
            run.finish("clarify" if "clarify" in payload else "done", payload)
        except progress.Cancelled:
            run.finish("error", {"error": "The search was cancelled."})
        except Exception as e:  # surface crew failures to the UI
            traceback.print_exc()
            run.finish("error", {"error": str(e)[:500]})


def _stall(run: Run) -> None:
    """The worker went quiet: cancel it and, if allowed, spawn a fresh run of the same search."""
    quiet = int(run.quiet_s)
    respawn = run.attempt <= MAX_RESPAWNS
    text = (f"agent went quiet for {quiet}s — spawning a new one (attempt {run.attempt + 1} of {MAX_RESPAWNS + 1})" if respawn
            else f"agent went quiet for {quiet}s after {run.attempt} attempts — giving up")
    print(f"[agent] run {run.id}: {text}", flush=True)
    run.push({"stage": "agent", "t": round(time.time(), 3), "text": text, "stalled": True})
    run.cancel.set()
    if respawn:
        run.replaced_by = spawn(run.work, run.user, run.message, run.chaos, run.history, attempt=run.attempt + 1)
    run.finish("error", {"error": f"The agent stopped responding for {quiet}s.", "stalled": True,
                         "respawned": run.replaced_by.id if run.replaced_by else None})


def _swallow(fut: asyncio.Future) -> None:
    """An abandoned worker may still raise later; retrieve it so asyncio doesn't log 'exception never retrieved'."""
    if not fut.cancelled():
        fut.exception()
