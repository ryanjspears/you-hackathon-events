"""Runs INSIDE the Daytona sandbox: python3 harness.py script.py input.json

Executes the agent-written script with `INPUT` bound to the parsed JSON, captures
stdout/stderr/traceback, and always prints one @@RESULT@@{json} line so the caller
gets exit_code + stderr even though Daytona's execute endpoint only returns
{exitCode, result}.
"""
import contextlib, io, json, sys, traceback

src = open(sys.argv[1]).read()
data = json.load(open(sys.argv[2]))


class Tee(io.StringIO):
    """Capture stderr for the result AND pass it through live, so progress lines stream while the script runs."""

    def write(self, text):
        sys.__stderr__.write(text)
        sys.__stderr__.flush()
        return super().write(text)


out, err, code = io.StringIO(), Tee(), 0
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    try:
        g = {"__name__": "__main__", "INPUT": data}
        exec(compile(src, "script.py", "exec"), g)
    except SystemExit as e:
        code = int(e.code or 0) if not isinstance(e.code, str) else 1
    except BaseException:
        code = 1
        traceback.print_exc()
print("@@RESULT@@" + json.dumps({"exit_code": code, "stdout": out.getvalue(), "stderr": err.getvalue()}))
