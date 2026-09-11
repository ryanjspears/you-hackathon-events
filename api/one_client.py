"""One MCP client: a single local `@withone/mcp` adapter shared by the whole app.

Everything external (You.com search, Daytona sandboxes) goes through One's four
tools. Action ids are resolved at startup by title/method/path — never hardcoded.
Wrappers `dropping_nulls` / `harden_execute` come from docs/one-skill.md.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from dataclasses import dataclass, field

from crewai.tools import tool
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from mcp import StdioServerParameters

from api import trace

load_dotenv()


def one_mcp_params() -> StdioServerParameters:
    return StdioServerParameters(command="npx", args=["-y", "@withone/mcp"], env={**os.environ})


def dropping_nulls(tools):
    for t in tools:
        inner = t._run
        object.__setattr__(t, "_run", (lambda f: lambda **kw: f(**{k: v for k, v in kw.items() if v is not None}))(inner))
    return tools


def harden_execute(tools):
    mcp_execute = next(t for t in tools if t.name == "execute_one_action")

    @tool("execute_one_action")
    def execute_one_action(platform: str, actionId: str, connectionKey: str, dataJson: str = "", pathVariablesJson: str = "",
                           queryParamsJson: str = "", headersJson: str = "", isFormData: bool = False, isFormUrlEncoded: bool = False) -> str:
        """Execute an API action on a connected platform via One. Pass request parts as JSON-encoded STRINGS. Omit or pass "" for parts the action does not need."""
        kwargs = {"platform": platform, "actionId": actionId, "connectionKey": connectionKey}
        for key, raw in (("data", dataJson), ("pathVariables", pathVariablesJson), ("queryParams", queryParamsJson), ("headers", headersJson)):
            if raw and raw.strip() and raw.strip() != "{}":
                kwargs[key] = json.loads(raw)
        if "headers" in kwargs:  # never let the model override One's own headers (connection key, action id, secret)
            kwargs["headers"] = {k: v for k, v in kwargs["headers"].items() if not k.lower().startswith("x-one-")}
        if isFormData:
            kwargs["isFormData"] = True
        if isFormUrlEncoded:
            kwargs["isFormUrlEncoded"] = True
        return mcp_execute._run(**kwargs)

    return [t for t in tools if t.name != "execute_one_action"] + [execute_one_action]


def _parse_json(raw: str):
    """MCP tool results are text; some carry a prose preamble before the JSON body."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    start = min((i for i in (raw.find("{"), raw.find("[")) if i >= 0), default=-1)
    if start >= 0:
        try:
            obj, _ = json.JSONDecoder().raw_decode(raw[start:])  # ignores trailing prose ("NEXT STEP: ...")
            return obj
        except json.JSONDecodeError:
            pass
    return {"raw": raw}


@dataclass
class Action:
    platform: str
    action_id: str
    title: str
    method: str
    path: str


@dataclass
class OneClient:
    """Holds the adapter, the hardened tools, connection keys and resolved actions."""

    adapter: MCPServerAdapter
    tools: list
    connections: dict[str, str] = field(default_factory=dict)  # platform -> connectionKey
    actions: dict[str, Action] = field(default_factory=dict)   # logical name -> Action
    _lock: threading.Lock = field(default_factory=threading.Lock)

    # ---- raw tool access -------------------------------------------------
    def _tool(self, name: str):
        return next(t for t in self.tools if t.name == name)

    def _run_json(self, name: str, **kw):
        # mcpadapt marshals sync calls onto its own loop; serialize to be safe.
        t0 = time.perf_counter()
        with self._lock:
            waited = time.perf_counter() - t0
            with trace.span(f"one.{name}", lock_wait_ms=int(waited * 1000) if waited > 0.01 else None) as s:
                raw = self._tool(name)._run(**kw)
                s["resp_chars"] = len(str(raw))
        return _parse_json(str(raw))

    def list_integrations(self) -> dict[str, str]:
        res = self._run_json("list_one_integrations")
        conns = res.get("connections") or res.get("integrations") or []
        self.connections = {c["platform"]: c["key"] for c in conns if "platform" in c and "key" in c}
        return self.connections

    def search_actions(self, platform: str, query: str) -> list[Action]:
        res = self._run_json("search_one_platform_actions", platform=platform, query=query, agentType="execute")
        out = []
        for a in res.get("actions", []):
            out.append(Action(platform, a["actionId"], a.get("title", ""), a.get("method", "").upper(), a.get("path", "")))
        return out

    def knowledge(self, platform: str, action_id: str) -> str:
        with self._lock:
            return str(self._tool("get_one_action_knowledge")._run(platform=platform, actionId=action_id))

    def execute(self, action: Action, data=None, path_vars=None, query=None, timeout_note: str | None = None):
        """Execute a resolved action; returns One's `responseData` (or the whole envelope if absent)."""
        kw = {"platform": action.platform, "actionId": action.action_id, "connectionKey": self.connections[action.platform]}
        if data:
            kw["dataJson"] = json.dumps(data)
        if path_vars:
            kw["pathVariablesJson"] = json.dumps(path_vars)
        if query:
            kw["queryParamsJson"] = json.dumps(query)
        # name the span after the action so the trace reads "one.daytona.execute" not "one.execute_one_action"
        label = next((n for n, a in self.actions.items() if a is action), f"{action.platform}.{action.method}")
        cmd = (data or {}).get("command") if isinstance(data, dict) else None
        with trace.span(f"one.{label}", cmd=(cmd.split("\n", 1)[0][:50] if cmd else None)):
            res = self._run_json("execute_one_action", **kw)
        if isinstance(res, dict) and "responseData" in res:
            return res["responseData"]
        return res

    # ---- resolution ------------------------------------------------------
    def resolve_actions(self) -> dict[str, Action]:
        """Find the actions the app needs by (platform, query, method, path-substring)."""
        wanted = {
            "you.search": ("you", "search web and news", "POST", "/v1/search"),
            "you.contents": ("you", "get web page contents", "POST", "/v1/contents"),
            "daytona.create": ("daytona", "create a sandbox", "POST", "/api/sandbox"),
            "daytona.execute": ("daytona", "execute a command in a sandbox", "POST", "/process/execute"),
            "daytona.delete": ("daytona", "delete sandbox", "DELETE", "/api/sandbox/"),
        }
        for name, (platform, q, method, path) in wanted.items():
            candidates = self.search_actions(platform, q)
            match = next((a for a in candidates if a.method == method and a.path.endswith(path) or
                          (a.method == method and path in a.path and name != "daytona.create")), None)
            if name == "daytona.create":
                match = next((a for a in candidates if a.method == "POST" and a.path.rstrip("/") == "/api/sandbox"), None)
            if not match:
                raise RuntimeError(f"Could not resolve One action {name!r}; candidates: {[(a.title, a.method, a.path) for a in candidates]}")
            self.actions[name] = match
        return self.actions


_client: OneClient | None = None


def start() -> OneClient:
    """Open the adapter once per process."""
    global _client
    if _client is not None:
        return _client
    adapter = MCPServerAdapter(one_mcp_params(), connect_timeout=120)
    tools = harden_execute(dropping_nulls(list(adapter.tools)))
    _client = OneClient(adapter=adapter, tools=tools)
    _client.list_integrations()
    for p in ("you", "daytona"):
        if p not in _client.connections:
            raise RuntimeError(f"One connection for {p!r} not visible. Connected: {list(_client.connections)}. Check ONE_CONNECTION_KEYS.")
    _client.resolve_actions()
    return _client


def stop():
    global _client
    if _client is not None:
        try:
            _client.adapter.stop()
        finally:
            _client = None


def get() -> OneClient:
    if _client is None:
        raise RuntimeError("One client not started")
    return _client


if __name__ == "__main__" and "--selftest" in sys.argv:
    # run via `python -m api.one_client`; import the package module so sandbox.py shares the same global client
    from api import one_client as _self
    start, stop = _self.start, _self.stop
    c = start()
    print("connections:", c.connections)
    for k, a in c.actions.items():
        print(f"  {k:16} {a.method:6} {a.path:45} {a.action_id}")
    res = c.execute(c.actions["you.search"], data={"query": "jazz shows Brooklyn this weekend", "count": 3})
    web = (res.get("results") or {}).get("web") or []
    print("search ok:", len(web), "web results;", web[0]["title"] if web else "(none)")
    from api import sandbox  # noqa: E402
    out = sandbox.sandbox_run("print(1 + 1)", {})
    print("sandbox:", out)
    sandbox.teardown()
    stop()
