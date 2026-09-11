"""Per-request tracing: named spans with wall-clock durations.

Every span prints `[trace] > name` when it starts and `[trace] < name 1.23s {attrs}` when it ends,
is forwarded to the SSE stream as a `trace` progress event, and is collected into the active
request's trace. `finish()` prints a summary table (every span, in order, indented by nesting) plus
the slowest spans, and returns the same data for the `done` payload.

    with trace.span("mem.recall", user=user) as s:
        ...
        s["hits"] = 3            # attrs added while running are kept

    trace.event("scan.stats", pages=10)   # a point event, no duration

CrewAI's LLM / tool / task events are turned into spans automatically (see `install_crewai_listener`),
so each model round-trip shows up with its agent, model, duration and token usage.

One request at a time is traced (main.py serializes the crew); spans that happen with no active
request (background recommender refresh, startup) still print, they are just not collected.
"""
from __future__ import annotations

import os
import threading
import time
import uuid
from contextlib import contextmanager

from api import progress

ENABLED = os.environ.get("TRACE", "1") not in ("0", "false", "no")
_lock = threading.RLock()
_current: "Trace | None" = None
_tls = threading.local()  # per-thread nesting depth for indentation


class Trace:
    def __init__(self, name: str, **attrs):
        self.id = uuid.uuid4().hex[:8]
        self.name = name
        self.attrs = attrs
        self.t0 = time.perf_counter()
        self.wall0 = time.time()
        self.spans: list[dict] = []
        self.open: dict[str, dict] = {}  # key -> span dict for spans started/ended from different threads

    def elapsed_ms(self) -> int:
        return int((time.perf_counter() - self.t0) * 1000)


def _depth() -> int:
    return getattr(_tls, "depth", 0)


def _fmt_attrs(attrs: dict) -> str:
    bits = []
    for k, v in attrs.items():
        if v is None or v == "" or v == []:
            continue
        s = str(v)
        bits.append(f"{k}={s[:60] + '…' if len(s) > 60 else s}")
    return " ".join(bits)


def _log(line: str) -> None:
    if ENABLED:
        print(f"[trace] {line}", flush=True)


def _record(sp: dict) -> None:
    """Close a span: log it, forward to the UI, and store it on the active trace."""
    sp["ms"] = int((time.perf_counter() - sp.pop("_t0")) * 1000)
    tr = _current
    sp["at_ms"] = int((sp.pop("_wall0") - tr.wall0) * 1000) if tr else 0
    _log(f"{'  ' * sp['depth']}< {sp['name']} {sp['ms'] / 1000:.2f}s {_fmt_attrs(sp['attrs'])}".rstrip())
    if ENABLED:
        progress.emit("trace", _print=False, text=f"{sp['name']} {sp['ms'] / 1000:.2f}s {_fmt_attrs(sp['attrs'])}".rstrip(),
                      span=sp["name"], ms=sp["ms"], at_ms=sp["at_ms"], attrs=sp["attrs"])
    if tr is not None:
        with _lock:
            tr.spans.append(sp)


def _new_span(name: str, attrs: dict) -> dict:
    sp = {"name": name, "attrs": attrs, "depth": _depth(), "_t0": time.perf_counter(), "_wall0": time.time()}
    _log(f"{'  ' * sp['depth']}> {name} {_fmt_attrs(attrs)}".rstrip())
    return sp


@contextmanager
def span(name: str, **attrs):
    """Time a block. Yields the attrs dict so the block can add measurements to it."""
    sp = _new_span(name, attrs)
    _tls.depth = _depth() + 1
    try:
        yield attrs
    except BaseException as e:
        attrs["error"] = f"{type(e).__name__}: {str(e)[:80]}"
        raise
    finally:
        _tls.depth = _depth() - 1
        _record(sp)


def start_span(key: str, name: str, **attrs) -> None:
    """Begin a span that another thread will end with `end_span(key)` (used for CrewAI event pairs)."""
    sp = _new_span(name, attrs)
    with _lock:
        (_current.open if _current else _orphans)[key] = sp


def end_span(key: str, **attrs) -> None:
    with _lock:
        sp = (_current.open if _current else _orphans).pop(key, None)
    if sp is None:
        return
    sp["attrs"].update(attrs)
    _record(sp)


_orphans: dict[str, dict] = {}


def event(name: str, **attrs) -> None:
    """A point in time with no duration (counts, sizes)."""
    tr = _current
    _log(f"{'  ' * _depth()}· {name} {_fmt_attrs(attrs)}".rstrip())
    if tr is not None:
        with _lock:
            tr.spans.append({"name": name, "attrs": attrs, "depth": _depth(), "ms": 0, "at_ms": tr.elapsed_ms(), "event": True})


def begin(name: str, **attrs) -> Trace:
    """Start collecting spans for a request. Returns the trace (its id is handy for log grepping)."""
    global _current
    with _lock:
        _current = Trace(name, **attrs)
    _log(f"=== {name} [{_current.id}] {_fmt_attrs(attrs)}")
    return _current


def finish() -> dict | None:
    """Stop collecting, print the summary table, return the trace as a JSON-able dict."""
    global _current
    with _lock:
        tr, _current = _current, None
    if tr is None:
        return None
    total = tr.elapsed_ms()
    # anything still open (a crashed request) is closed as-is so it shows in the table
    for sp in list(tr.open.values()):
        sp["attrs"]["unfinished"] = True
        sp["ms"] = int((time.perf_counter() - sp.pop("_t0")) * 1000)
        sp["at_ms"] = int((sp.pop("_wall0") - tr.wall0) * 1000)
        tr.spans.append(sp)
    tr.open.clear()
    spans = sorted(tr.spans, key=lambda s: (s["at_ms"], s["depth"]))
    lines = [f"=== {tr.name} [{tr.id}] total {total / 1000:.2f}s", f"{'at':>7} {'dur':>7}  span"]
    for sp in spans:
        dur = "·" if sp.get("event") else f"{sp['ms'] / 1000:.2f}s"
        lines.append(f"{sp['at_ms'] / 1000:7.2f} {dur:>7}  {'  ' * sp['depth']}{sp['name']} {_fmt_attrs(sp['attrs'])}".rstrip())
    # where the time went: by span name, summed (nested spans overlap, so read this with the tree above)
    by_name: dict[str, list[int]] = {}
    for sp in spans:
        if sp["ms"]:
            by_name.setdefault(sp["name"], []).append(sp["ms"])
    top = sorted(by_name.items(), key=lambda kv: -sum(kv[1]))[:8]
    lines.append("slowest (summed by name, n=calls): " + ", ".join(f"{n} {sum(v) / 1000:.1f}s n={len(v)}" for n, v in top))
    for line in lines:
        _log(line)
    summary = {"id": tr.id, "name": tr.name, "total_ms": total, "spans": spans,
               "by_name": {n: {"ms": sum(v), "n": len(v)} for n, v in by_name.items()}}
    if ENABLED:
        progress.emit("trace", _print=False, text=f"total {total / 1000:.2f}s · " + ", ".join(f"{n} {sum(v) / 1000:.1f}s" for n, v in top[:5]),
                      span="total", ms=total, at_ms=0, attrs={}, summary=True)
    return summary


# ---- CrewAI: every LLM call, tool call and task becomes a span ------------------------------------

_installed = False


def install_crewai_listener() -> None:
    """Subscribe once to CrewAI's event bus. Handlers run on the bus's thread pool, hence start/end by key."""
    global _installed
    if _installed or not ENABLED:
        return
    _installed = True
    from crewai.events import crewai_event_bus
    from crewai.events.types.llm_events import LLMCallCompletedEvent, LLMCallFailedEvent, LLMCallStartedEvent
    from crewai.events.types.task_events import TaskCompletedEvent, TaskFailedEvent, TaskStartedEvent
    from crewai.events.types.tool_usage_events import ToolUsageErrorEvent, ToolUsageFinishedEvent, ToolUsageStartedEvent

    def _usage(u) -> dict:
        if not u:
            return {}
        get = (lambda k: u.get(k)) if isinstance(u, dict) else (lambda k: getattr(u, k, None))
        return {k: get(k) for k in ("prompt_tokens", "completion_tokens", "total_tokens") if get(k) is not None}

    @crewai_event_bus.on(LLMCallStartedEvent)
    def _llm_start(_source, e):
        n_msgs = len(e.messages) if isinstance(e.messages, list) else 1
        chars = sum(len(str(m.get("content", "") if isinstance(m, dict) else m)) for m in (e.messages if isinstance(e.messages, list) else [e.messages]))
        start_span(f"llm:{e.call_id}", "llm.call", agent=e.agent_role, model=e.model, messages=n_msgs, prompt_chars=chars,
                   tools=len(e.tools or []))

    @crewai_event_bus.on(LLMCallCompletedEvent)
    def _llm_done(_source, e):
        end_span(f"llm:{e.call_id}", call_type=str(getattr(e.call_type, "value", e.call_type) or ""), finish=e.finish_reason, **_usage(e.usage))

    @crewai_event_bus.on(LLMCallFailedEvent)
    def _llm_fail(_source, e):
        end_span(f"llm:{e.call_id}", error=str(e.error)[:80])

    @crewai_event_bus.on(ToolUsageStartedEvent)
    def _tool_start(_source, e):
        start_span(f"tool:{e.agent_key}:{e.tool_name}", f"tool.{e.tool_name}", agent=e.agent_role, attempt=e.run_attempts)

    @crewai_event_bus.on(ToolUsageFinishedEvent)
    def _tool_done(_source, e):
        end_span(f"tool:{e.agent_key}:{e.tool_name}", cached=bool(e.from_cache), output_chars=len(str(e.output or "")))

    @crewai_event_bus.on(ToolUsageErrorEvent)
    def _tool_fail(_source, e):
        end_span(f"tool:{e.agent_key}:{e.tool_name}", error=str(getattr(e, "error", ""))[:80])

    @crewai_event_bus.on(TaskStartedEvent)
    def _task_start(_source, e):
        start_span(f"task:{e.task_id}", "crew.task", agent=e.agent_role)

    @crewai_event_bus.on(TaskCompletedEvent)
    def _task_done(_source, e):
        end_span(f"task:{e.task_id}")

    @crewai_event_bus.on(TaskFailedEvent)
    def _task_fail(_source, e):
        end_span(f"task:{e.task_id}", error=str(getattr(e, "error", ""))[:80])
