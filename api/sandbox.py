"""Daytona sandbox harness, driven entirely through One.

One sandbox per API process (cached), created with a TTL so it self-destructs.
`sandbox_run(script, input_json)` executes agent-written Python inside it and
returns {exit_code, stdout, stderr} — the raw material for the repair loop.
"""
from __future__ import annotations

import json
import os
import pathlib
import threading
import time

from api import one_client, trace
from api.progress import emit

HOME = "/home/daytona"
MARK = "@@RESULT@@"
HARNESS = pathlib.Path(__file__).parent / "scripts" / "harness.py"

_sandbox_id: str | None = None
_lock = threading.Lock()


def _exec(sandbox_id: str, command: str, timeout: int = 60, cwd: str = HOME) -> dict:
    c = one_client.get()
    res = c.execute(c.actions["daytona.execute"], path_vars={"sandboxId": sandbox_id},
                    data={"command": command, "cwd": cwd, "timeout": timeout})
    if not isinstance(res, dict) or "exitCode" not in res:
        raise RuntimeError(f"unexpected execute response: {str(res)[:300]}")
    return res


def _write_file(sandbox_id: str, path: str, content: str) -> None:
    if any(line.strip() == "EOF" for line in content.splitlines()):
        raise ValueError("script may not contain a bare 'EOF' line")
    res = _exec(sandbox_id, f"cat > {path} <<'EOF'\n{content}\nEOF", timeout=30)
    if res["exitCode"] != 0:
        raise RuntimeError(f"write {path} failed: {res.get('result')}")


def ensure_sandbox() -> str:
    with trace.span("sandbox.ensure") as s:
        return _ensure_sandbox(s)


def _ensure_sandbox(s: dict) -> str:
    global _sandbox_id
    with _lock:
        if _sandbox_id:
            try:
                if _exec(_sandbox_id, "echo ok", timeout=10)["exitCode"] == 0:
                    s["reused"] = True
                    return _sandbox_id
            except Exception:
                pass
            _sandbox_id = None
        s["created"] = True
        c = one_client.get()
        emit("sandbox", text="creating Daytona sandbox via One")
        env = {k: os.environ[k] for k in ("YDC_API_KEY", "OPENAI_API_KEY", "SCAN_MODEL") if os.environ.get(k)}
        res = c.execute(c.actions["daytona.create"], data={
            "name": f"events-{os.getpid()}-{int(time.time())}",
            "ttlMinutes": 120,
            "env": env,  # the scan script calls You.com and OpenAI directly from inside the sandbox
            "domainAllowList": "ydc-index.io,api.you.com,api.openai.com,pypi.org,files.pythonhosted.org",
        })
        sid = res.get("id") if isinstance(res, dict) else None
        if not sid:
            raise RuntimeError(f"sandbox create failed: {str(res)[:300]}")
        # wait until the toolbox answers
        with trace.span("sandbox.wait_ready") as w:
            for i in range(30):
                w["probes"] = i + 1
                try:
                    if _exec(sid, "echo ok", timeout=10)["exitCode"] == 0:
                        break
                except Exception:
                    pass
                time.sleep(1)
        _write_file(sid, f"{HOME}/harness.py", HARNESS.read_text())
        _sandbox_id = sid
        emit("sandbox", text=f"sandbox {sid[:8]} ready")
        return sid


def sandbox_run(script: str, input_data, timeout: int = 240) -> dict:
    """Run `script` (Python source; `INPUT` holds input_data) inside the sandbox.

    The script is started in the background and polled with short execs: a single long
    execute call through One's passthrough proxy returns 502 after ~60 s, and a scan
    can take longer than that.
    """
    with trace.span("sandbox.run", script_chars=len(script), timeout=timeout) as s:
        return _sandbox_run(script, input_data, timeout, s)


def _sandbox_run(script: str, input_data, timeout: int, s: dict) -> dict:
    sid = ensure_sandbox()
    with _lock:
        with trace.span("sandbox.upload", script_chars=len(script), input_chars=len(json.dumps(input_data))):
            _write_file(sid, f"{HOME}/script.py", script)
            _write_file(sid, f"{HOME}/input.json", json.dumps(input_data))
        with trace.span("sandbox.start"):
            _exec(sid, "rm -f out.txt done.flag; nohup sh -c 'python3 harness.py script.py input.json > out.txt 2>&1; echo $? > done.flag' >/dev/null 2>&1 &", timeout=15)
    started, deadline = time.time(), time.time() + timeout
    text, finished, streamed, last_beat = "", False, 0, 0.0
    polls, poll_ms, poll_errors, poll_bytes = 0, 0, 0, 0
    while time.time() < deadline:
        time.sleep(3)
        t_poll = time.perf_counter()
        try:
            with _lock:
                res = _exec(sid, "if [ -f done.flag ]; then echo __DONE__; fi; cat out.txt 2>/dev/null | tail -c 200000", timeout=20)
        except Exception as e:  # transient proxy hiccup: keep polling
            poll_errors += 1
            emit("sandbox", text=f"poll error, retrying: {str(e)[:80]}")
            continue
        finally:
            polls += 1
            poll_ms += int((time.perf_counter() - t_poll) * 1000)
        text = res.get("result") or ""
        poll_bytes += len(text)
        if text.startswith("__DONE__"):
            text, finished = text[len("__DONE__"):].lstrip("\n"), True
            s["script_wall_s"] = round(time.time() - started, 1)  # start → done.flag seen (includes up to 3 s poll lag)
        # stream the script's progress log ([scan] lines) as it is written
        lines = [l[7:] for l in text.splitlines() if l.startswith("[scan] ")]
        for line in lines[streamed:]:
            emit("scan", text=line)
        streamed = len(lines)
        if finished:
            break
        elapsed = int(time.time() - started)
        if time.time() - last_beat >= 9:
            emit("sandbox", text=f"scan.py running in Daytona · {elapsed}s", elapsed=elapsed)
            last_beat = time.time()
    s.update(polls=polls, poll_avg_ms=poll_ms // max(polls, 1), poll_errors=poll_errors, poll_kb=poll_bytes // 1024)
    if not finished:
        with _lock:
            _exec(sid, "pkill -f harness.py || true", timeout=10)
        return {"exit_code": 124, "stdout": "", "stderr": f"script did not finish within {timeout}s\n" + text[-3000:], "sandbox_id": sid}
    if MARK in text:
        payload = json.loads(text.split(MARK, 1)[1].strip().splitlines()[0])
    else:
        payload = {"exit_code": 1, "stdout": "", "stderr": text[-4000:]}
    payload["sandbox_id"] = sid
    return payload


def teardown() -> None:
    global _sandbox_id
    if not _sandbox_id:
        return
    try:
        c = one_client.get()
        c.execute(c.actions["daytona.delete"], path_vars={"sandboxIdOrName": _sandbox_id})
    except Exception:
        pass
    _sandbox_id = None
