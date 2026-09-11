"""Progress events from worker threads (crew/tools) to the run being streamed.

`emit()` prints the line and appends it to the current run (see api/runs.py) — the run bound to
this thread by `bind()`, else the most recently started run: CrewAI's event bus fires trace
spans from its own thread pool, and the recommender re-ranks on a background thread. Every
emit is also the run's heartbeat; a worker that emits nothing for RUN_STALL_S is respawned.
"""
from __future__ import annotations

import threading
import time

_local = threading.local()
_global: dict = {}


class Cancelled(Exception):
    """Raised by `check()` inside a worker whose run was abandoned (stalled and respawned)."""


def bind(run) -> None:
    """Route this thread's emits to `run` (the worker thread of api/runs.py)."""
    _local.run = run


def set_current(run) -> None:
    """Fallback target for threads that were never bound (CrewAI event bus, recommender)."""
    _global["run"] = run


def current():
    return getattr(_local, "run", None) or _global.get("run")


def cancelled() -> bool:
    run = current()
    return run is not None and run.cancel.is_set()


def check() -> None:
    """Cooperative cancellation point for long loops (sandbox polling) and between steps."""
    if cancelled():
        raise Cancelled("run was abandoned")


def beat() -> None:
    """Heartbeat without a log line (for tight loops that are alive but have nothing to say)."""
    run = current()
    if run is not None:
        run.beat()


def emit(stage: str, *, _print: bool = True, **data) -> None:
    payload = {"stage": stage, "t": round(time.time(), 3), **data}
    if _print:  # trace.py prints its own indented line
        print(f"[{stage}] {data.get('text', '')}".rstrip(), flush=True)
    run = current()
    if run is not None:
        run.push(payload)
