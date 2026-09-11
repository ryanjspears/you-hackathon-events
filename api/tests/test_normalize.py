import importlib.util, json, pathlib, subprocess, sys, tempfile
from datetime import datetime

SCRIPTS = pathlib.Path(__file__).parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("scan", SCRIPTS / "scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)  # does not run main(): __name__ != "__main__"
NOW = datetime.fromisoformat("2026-09-11T12:00:00-04:00")  # a Friday


def test_dedupe_and_dates():
    cands = [
        {"title": "Jazz Night at Smalls", "start": "Sat Sep 12 2026 9pm", "venue": "Smalls", "url": "https://dice.fm/a", "platform": "Dice", "price": 20},
        {"title": "JAZZ NIGHT at Smalls!", "start": "2026-09-12T21:00", "venue": "Smalls Jazz Club", "url": "https://eventbrite.com/b", "platform": "Eventbrite"},
        {"title": "Old show", "start": "2026-01-01T20:00", "url": "https://x/y"},
        {"title": "No date", "start": "TBD", "url": "https://x/z"},
        {"title": "Weird", "start": {"raw": None}, "url": "https://x/w"},
    ]
    body = scan.normalize(cands, NOW, "Brooklyn, NY", "2026-09-11", "2026-09-13")
    assert [e["title"] for e in body["events"]] in (["Jazz Night at Smalls"], ["JAZZ NIGHT at Smalls!"])
    assert body["events"][0]["start"].startswith("2026-09-12T21:00") and body["events"][0]["in_window"]
    assert body["dropped"]["past"] == 1 and body["dropped"]["no_date"] == 2


def test_relative_dates():
    cands = [{"title": "A", "start": "Tomorrow at 5:30 PM", "url": "https://x/a"},
             {"title": "B", "start": "Sunday at 2:00 PM", "url": "https://x/b"},
             {"title": "C", "start": "Sun, Sep 13 · 3:00 PM EDT", "url": "https://x/c"},
             {"title": "D", "start": "Today at 11:00 PM", "url": "https://x/d"}]
    starts = {e["title"]: e["start"] for e in scan.normalize(cands, NOW)["events"]}
    assert starts["A"].startswith("2026-09-12T17:30")
    assert starts["B"].startswith("2026-09-13T14:00")
    assert starts["C"].startswith("2026-09-13T15:00")
    assert starts["D"].startswith("2026-09-11T23:00")


def test_chaos_candidate_crashes_normalize():
    try:
        scan.normalize([{"title": 12345, "start": "Tomorrow at 8:00 PM"}], NOW)
    except AttributeError:
        return
    raise AssertionError("chaos candidate should crash normalize() so the repair loop has something to fix")


def test_harness_reports_traceback():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as s, tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as i:
        s.write("x = INPUT['missing']\n"); s.flush(); json.dump({}, i); i.flush()
        out = subprocess.run([sys.executable, str(SCRIPTS / "harness.py"), s.name, i.name], capture_output=True, text=True).stdout
    res = json.loads(out.split("@@RESULT@@", 1)[1])
    assert res["exit_code"] == 1 and "KeyError" in res["stderr"]
