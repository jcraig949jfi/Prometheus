"""Failure-injection regression tests for prometheus.cosmos.supervise (incident 2026-10-08: EXP-04 hung 58 h with
zero results because a spawn Pool was launched from stdin and the waiter watched only the PID)."""
import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

from prometheus.cosmos import supervise as SV

ROOT = Path(__file__).resolve().parents[3]
ENV = {**os.environ, "PYTHONPATH": str(ROOT), "OPENBLAS_NUM_THREADS": "1"}
PY = sys.executable


def _script(tmp_path, body, name="run.py"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body))
    return p


def _driver(fn, rundir, n=6, extra="", **kw):
    args = ", ".join(f"{k}={v!r}" for k, v in kw.items())
    return f"""
        from prometheus.cosmos import supervise as SV
        from prometheus.cosmos.tests import _supervise_jobs as J
        if __name__ == "__main__":
            jobs = [{{"i": i{extra}}} for i in range({n})]
            SV.run_jobs(J.{fn}, jobs, {str(rundir)!r}, key="i", workers=2{", " + args if args else ""})
        """


def _rows(rundir):
    p = Path(rundir) / "results.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def _no_strays(tag):
    out = subprocess.run(["pgrep", "-f", tag], capture_output=True, text=True).stdout.split()
    return [p for p in out if int(p) != os.getpid()]


def test_stdin_launch_is_refused_before_any_worker(tmp_path):
    body = textwrap.dedent(_driver("ok", tmp_path / "r"))
    t0 = time.time()
    r = subprocess.run([PY, "-"], input=body, capture_output=True, text=True, env=ENV, timeout=60, cwd=ROOT)
    assert r.returncode != 0 and "SpawnUnsafe" in r.stderr
    assert time.time() - t0 < 30
    r = subprocess.run([PY, "-c", body], capture_output=True, text=True, env=ENV, timeout=60, cwd=ROOT)
    assert r.returncode != 0 and "SpawnUnsafe" in r.stderr
    assert not (tmp_path / "r" / "results.jsonl").exists()


def test_happy_path_and_resume(tmp_path):
    rd = tmp_path / "r"
    s = _script(tmp_path, _driver("ok", rd, n=8))
    subprocess.run([PY, str(s)], check=True, env=ENV, timeout=120, cwd=ROOT)
    assert sorted(r["i"] for r in _rows(rd)) == list(range(8))
    prog = json.loads((rd / SV.PROGRESS).read_text())
    assert prog["status"] == "DONE" and prog["n_done"] == 8 and prog["last_result_utc"]
    subprocess.run([PY, str(s)], check=True, env=ENV, timeout=120, cwd=ROOT)      # resume: nothing re-run
    assert len(_rows(rd)) == 8


def test_child_that_cannot_start_is_failed_not_waited_on(tmp_path, monkeypatch):
    monkeypatch.delenv("PYTHONPATH", raising=False)
    rd = tmp_path / "r"
    s = _script(tmp_path, _driver("ok", rd))
    assert SV.launch(rd, [PY, str(s)], stall_s=30, max_restarts=0, poll_s=1) == "FAILED"


def test_worker_death_fails_fast(tmp_path):
    rd = tmp_path / "r"
    s = _script(tmp_path, _driver("dies_on_3", rd, n=10))
    t0 = time.time()
    r = subprocess.run([PY, str(s)], capture_output=True, text=True, env=ENV, timeout=120, cwd=ROOT)
    assert r.returncode != 0 and "RunFailed" in r.stderr
    assert time.time() - t0 < 60
    assert json.loads((rd / SV.PROGRESS).read_text())["status"] == "FAILED"


def test_job_exceptions_are_counted_and_bounded(tmp_path):
    rd = tmp_path / "strict"
    s = _script(tmp_path, _driver("raises_on_odd", rd, n=6), "strict.py")
    r = subprocess.run([PY, str(s)], capture_output=True, text=True, env=ENV, timeout=120, cwd=ROOT)
    assert r.returncode != 0 and json.loads((rd / SV.PROGRESS).read_text())["status"] == "FAILED"
    rd2 = tmp_path / "tolerant"
    s = _script(tmp_path, _driver("raises_on_odd", rd2, n=6, max_failures=5), "tolerant.py")
    subprocess.run([PY, str(s)], check=True, env=ENV, timeout=120, cwd=ROOT)
    prog = json.loads((rd2 / SV.PROGRESS).read_text())
    assert prog["status"] == "DONE_WITH_FAILURES" and prog["n_failed"] == 3 and prog["n_done"] == 3
    assert len((rd2 / SV.FAILURES).read_text().splitlines()) == 3


def test_status_alive_without_results_is_stalled(tmp_path):
    """The core rule: a live process producing no science past the stall limit is STALLED, not OK."""
    rd = tmp_path / "r"
    rd.mkdir()
    t0 = time.time() - 1000
    (rd / SV.PROGRESS).write_text(json.dumps({"status": "RUNNING", "pid": os.getpid(), "start_utc": SV.utc(t0),
                                              "heartbeat_utc": SV.utc(), "last_result_utc": None,
                                              "n_total": 5, "n_done": 0, "n_failed": 0}))
    assert SV.status(rd, stall_s=900, alive=True)["verdict"] == "STALLED"     # heartbeat fresh, science stale
    assert SV.status(rd, stall_s=2000, alive=True)["verdict"] == "OK"
    assert SV.status(rd, stall_s=2000, alive=False)["verdict"] == "DEAD"


def test_watchdog_kills_hung_run_and_resumes(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    rd = tmp_path / "r"
    marker = tmp_path / "marker"
    s = _script(tmp_path, _driver("hangs_once", rd, n=6, extra=f', "marker": {str(marker)!r}'))
    v = SV.launch(rd, [PY, str(s)], stall_s=6, max_restarts=1, poll_s=1)
    assert v == "DONE"
    ev = [json.loads(x)["event"] for x in (rd / SV.EVENTS).read_text().splitlines()]
    assert "stalled" in ev and "killed" in ev and "restart" in ev
    assert sorted(r["i"] for r in _rows(rd)) == list(range(6))


def test_watchdog_gives_up_and_records_failed(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    rd = tmp_path / "r"
    s = _script(tmp_path, _driver("hangs_always", rd, n=4))
    v = SV.launch(rd, [PY, str(s)], stall_s=5, max_restarts=1, poll_s=1)
    assert v == "STALLED"
    assert json.loads((rd / SV.PROGRESS).read_text())["status"] == "FAILED"
    time.sleep(1)
    assert not _no_strays(str(s))                                            # whole process group is gone


def test_replay_of_the_2026_10_08_incident(tmp_path, monkeypatch):
    """The original launch shape (spawn Pool from a stdin heredoc) under the watchdog: it never reports progress,
    so it is STALLED within the start grace and killed with its respawning workers -- minutes, not 58 hours."""
    rd = tmp_path / "r"
    tag = f"incident_replay_{os.getpid()}"
    heredoc = textwrap.dedent(f"""
        # {tag}
        from multiprocessing import get_context
        from prometheus.cosmos.tests import _supervise_jobs as J
        if __name__ == "__main__":
            with get_context("spawn").Pool(2) as p:
                print(list(p.imap_unordered(J.ok, [{{"i": i}} for i in range(4)])))
        """)
    cmd = ["bash", "-c", f"{PY} - <<'EOF'\n{heredoc}\nEOF"]
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    t0 = time.time()
    v = SV.launch(rd, cmd, stall_s=8, max_restarts=0, poll_s=1)
    assert v == "STALLED"
    assert time.time() - t0 < 60
    assert "FileNotFoundError" in (rd / "run.log").read_text()               # the original failure, reproduced
    time.sleep(1)
    pid = int((rd / "PID").read_text())
    assert subprocess.run(["pgrep", "-s", str(pid)], capture_output=True).returncode == 1   # session empty


def test_cli_launch_parses_options_and_command(tmp_path):
    rd = tmp_path / "r"
    s = _script(tmp_path, _driver("ok", rd, n=4))
    r = subprocess.run([PY, "-m", "prometheus.cosmos.supervise", "launch", str(rd), "--stall", "60", "--restarts",
                        "0", "--poll", "1", "--", PY, str(s)], capture_output=True, text=True, env=ENV,
                       timeout=120, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["verdict"] == "DONE" and len(_rows(rd)) == 4


def test_max_tasks_per_child_does_not_deadlock(tmp_path):
    """Regression (EXP-04 relaunch 2026-10-11): with all jobs submitted up front, retired workers were never replaced
    and the run stopped at workers x max_tasks_per_child results with a live parent."""
    rd = tmp_path / "r"
    s = _script(tmp_path, _driver("ok", rd, n=12, max_tasks_per_child=2))
    subprocess.run([PY, str(s)], check=True, env=ENV, timeout=120, cwd=ROOT)
    assert sorted(r["i"] for r in _rows(rd)) == list(range(12))
