"""FastAPI app: chat stream (SSE), interactions, recommendations."""
from __future__ import annotations

import asyncio
import json
import time
import traceback
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from api import crew, favicon, mem, one_client, progress, recommender, sandbox, store, suggest, trace
from api.progress import emit

_crew_slot = asyncio.Semaphore(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, one_client.start)
    await loop.run_in_executor(None, mem.warm)
    yield
    sandbox.teardown()
    one_client.stop()


app = FastAPI(title="Events Scanner", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   allow_methods=["*"], allow_headers=["*"])


def _scan(user: str, message: str, chaos: bool, history: list[dict] | None = None) -> dict:
    """Runs on a worker thread. Emits progress; returns the final payload for the `done` event."""
    trace.begin("chat", user=user, message=message, chaos=chaos, history_turns=len(history or []))
    try:
        payload = _scan_traced(user, message, chaos, history)
    except BaseException:
        payload = None
        raise
    finally:
        summary = trace.finish()
        if payload is not None and summary:
            payload["trace"] = summary
    return payload


def _scan_traced(user: str, message: str, chaos: bool, history: list[dict] | None) -> dict:
    store.ensure_user(user)
    with trace.span("mem.recall"):
        recalled = mem.recall(user, message)
    with trace.span("crew.plan", history_turns=len(history or [])):
        plan = crew.plan_only(message, recalled, history)
    emit("plan", text=f"plan: {plan.model_dump_json()}", plan=plan.model_dump())
    if not plan.city:
        return {"clarify": plan.clarifying_question or "Which city should I search in?", "plan": plan.model_dump()}
    with trace.span("crew.scan") as s:
        result = crew.run_scan(message, plan, chaos=chaos)
        s["events"] = len(result.get("events", [])); s["attempts"] = result.get("attempts")
    events = result.get("events", [])
    with trace.span("store.save", events=len(events)):
        store.upsert_events(events)
        store.record_search(user, message, plan.model_dump(), [e["id"] for e in events])
    if plan.categories or plan.city:
        with trace.span("mem.learn"):
            mem.learn(user, f"Searched for {', '.join(plan.categories) or plan.keywords or message} in {plan.city}"
                            f"{' ' + plan.date_window if plan.date_window else ''}"
                            f"{' on ' + crew.source_names(plan.sources) if plan.sources else ''}", tags=["search"], weight=4)
    if plan.sources:  # a named site becomes a soft preference for later requests that name none
        with trace.span("mem.learn_sources"):
            mem.learn_sources(user, crew.source_names(plan.sources))
    if events:  # new listings are in the pool now: re-rank "For you" while the user reads the results
        recommender.refresh_in_background(user)
    return {"events": events, "reply": result.get("reply"), "dropped": result.get("dropped"), "attempts": result.get("attempts"),
            "hits": result.get("hits"), "pages": result.get("pages"), "stats": result.get("stats"),
            "plan": plan.model_dump(), "recalled": recalled}


@app.get("/api/chat/stream")
async def chat_stream(user: str = Query(..., min_length=1), message: str = Query(..., min_length=1), chaos: bool = False,
                      history: str | None = Query(None, max_length=20_000)):
    """`history`: JSON list of earlier turns in this chat, oldest first — {role:"user", text} and
    {role:"agent", plan, clarify?} — so a follow-up like "how about jazz" keeps the previous city and dates."""
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    turns: list[dict] | None = None
    if history:
        try:
            parsed = json.loads(history)
            turns = [t for t in parsed if isinstance(t, dict)] if isinstance(parsed, list) else None
        except json.JSONDecodeError:
            turns = None

    async def gen():
        t_req = time.perf_counter()
        async with _crew_slot:
            waited = time.perf_counter() - t_req
            if waited > 0.05:
                print(f"[trace] request waited {waited:.2f}s for the crew slot", flush=True)
            progress.set_emitter(queue, loop)
            fut = loop.run_in_executor(None, _scan, user.strip().lower(), message, chaos, turns)
            try:
                while True:
                    if fut.done() and queue.empty():
                        break
                    try:
                        item = await asyncio.wait_for(queue.get(), timeout=10)
                        yield {"event": item["stage"], "data": json.dumps(item)}
                    except asyncio.TimeoutError:
                        yield {"event": "ping", "data": "{}"}
                try:
                    payload = fut.result()
                    yield {"event": "clarify" if "clarify" in payload else "done", "data": json.dumps(payload)}
                except Exception as e:  # surface crew failures to the UI
                    traceback.print_exc()
                    yield {"event": "error", "data": json.dumps({"error": str(e)[:500]})}
            finally:
                progress.set_emitter(None, None)

    return EventSourceResponse(gen())


class Interact(BaseModel):
    user: str
    kind: str  # going | skip


@app.post("/api/events/{event_id}/interact")
async def interact(event_id: str, body: Interact, tasks: BackgroundTasks):
    if body.kind not in ("going", "skip"):
        raise HTTPException(400, "kind must be going|skip")
    event = store.get_event(event_id)
    if not event:
        raise HTTPException(404, "unknown event")
    user = body.user.strip().lower()
    store.ensure_user(user)
    store.record_interaction(user, event_id, body.kind)
    tasks.add_task(_interaction_traced, user, event, body.kind)
    return {"ok": True, "event": event, "kind": body.kind}


def _interaction_traced(user: str, event: dict, kind: str) -> None:
    trace.begin("interact", user=user, kind=kind, event=event.get("title"))
    try:
        recommender.on_interaction(user, event, kind)
    finally:
        trace.finish()


@app.get("/api/recommendations")
async def recommendations(user: str, refresh: bool = False):
    user = user.strip().lower()
    store.ensure_user(user)
    loop = asyncio.get_running_loop()
    recalled = await loop.run_in_executor(None, mem.recall, user, "events I like")
    if refresh:
        async with _crew_slot:
            await loop.run_in_executor(None, recommender.refresh, user)
    recs = store.get_recommendations(user)
    going = store.interactions(user, "going")
    return {"user": user, "recalled": recalled, "recommendations": recs, "going": going,
            "profile": recommender.describe(recommender.build_profile(user))}


@app.get("/api/going")
async def going(user: str):
    """The user's timeline: every event they marked going, soonest first (SPEC §3b). No memory call, so it's instant."""
    user = user.strip().lower()
    store.ensure_user(user)
    return {"user": user, "going": store.going(user)}


@app.get("/api/for-you")
async def for_you(user: str, limit: int = Query(4, ge=1, le=12), refresh: bool = False):
    """The home page's targeted picks (SPEC §3d): cached ranking, instant. A stale or empty ranking is
    rebuilt in the sandbox on a background thread; poll while `refreshing` is true."""
    user = user.strip().lower()
    store.ensure_user(user)
    profile = recommender.build_profile(user)
    recs = store.get_recommendations(user, limit)
    has_taste = bool(profile["tags"] or profile["platforms"])
    if has_taste and not recommender.is_refreshing(user) and (refresh or recommender.is_stale(user) or not recs):
        recommender.refresh_in_background(user)
    return {"user": user, "profile": recommender.describe(profile), "recommendations": recs,
            "refreshing": recommender.is_refreshing(user)}


@app.get("/api/suggestions")
async def suggestions(user: str, limit: int = Query(4, ge=3, le=5)):
    """Home-page prompt chips from what the user searched and picked (SPEC §3c). SQLite only: instant, never queues behind a search."""
    user = user.strip().lower()
    store.ensure_user(user)
    with trace.span("suggest", user=user):
        items, personalized = suggest.for_user(user, limit)
    return {"user": user, "suggestions": items, "personalized": personalized}


@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    e = store.get_event(event_id)
    if not e:
        raise HTTPException(404)
    return e


@app.get("/api/favicon")
async def favicon_for(domain: str = Query(..., min_length=3, max_length=253)):
    """The provider's own favicon, fetched from the site once and cached on disk (see api/favicon.py)."""
    loop = asyncio.get_running_loop()
    hit = await loop.run_in_executor(None, favicon.get, domain)
    if not hit:
        return Response(status_code=404, headers={"Cache-Control": "public, max-age=3600"})
    data, ctype = hit
    return Response(content=data, media_type=ctype, headers={"Cache-Control": "public, max-age=604800, immutable"})


@app.get("/api/health")
async def health():
    c = one_client.get()
    return {"ok": True, "connections": list(c.connections), "actions": {k: a.path for k, a in c.actions.items()}}
