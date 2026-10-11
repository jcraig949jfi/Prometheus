"""Progress-supervised job runner and watchdog (incident 2026-10-08: EXP-04 hung 58 h producing zero results).

The incident: a spawn Pool launched from a stdin heredoc could not re-import `<stdin>` in its workers; Pool silently
respawned crashing workers (4,683,366 times) while the parent stayed alive, and the waiter watched only the PID.

Rules enforced here:
1. SPAWN-SAFE LAUNCH. run_jobs refuses to start unless __main__ is importable by a spawned child (a real file or
   `python -m`). A stdin / `-c` launch raises SpawnUnsafe before any worker exists.
2. FAIL FAST ON WORKER DEATH. Jobs run in a ProcessPoolExecutor (spawn): a worker that dies breaks the pool and the
   run ends FAILED, instead of Pool's silent respawn loop. A job that RAISES is recorded in failures.jsonl and the
   run continues until max_failures, then ends FAILED.
3. PROGRESS, NOT LIVENESS. PROGRESS.json records n_done / n_total / n_failed, last_result_utc (science) and
   heartbeat_utc (liveness) separately. The watchdog judges a run by time since the LAST RESULT. A live process
   producing no results past the stall limit is STALLED, is killed (whole process group), and is recorded as an
   incident; it is relaunched (the run resumes from its checkpoint) up to max_restarts, then FAILED.

    python -m prometheus.cosmos.supervise launch <rundir> --stall S [--restarts R] [--poll P] -- <cmd ...>
    python -m prometheus.cosmos.supervise status <rundir> [--stall S]

`launch` runs <cmd> in its own session, watches it, and exits 0 only on DONE (non-zero on FAILED / STALLED), so a
caller waiting on `launch` is woken by the outcome of the science, not by the death of a PID.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from concurrent.futures.process import BrokenProcessPool
from multiprocessing import get_context
from pathlib import Path
from typing import Callable, Iterable, Optional

PROGRESS = "PROGRESS.json"
EVENTS = "EVENTS.jsonl"
FAILURES = "failures.jsonl"


class SpawnUnsafe(RuntimeError):
    pass


class RunFailed(RuntimeError):
    pass


def utc(t: Optional[float] = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() if t is None else t))


def _atomic_json(p: Path, obj: dict):
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True, default=float))
    os.replace(tmp, p)


def _event(rundir: Path, kind: str, **kw):
    with open(rundir / EVENTS, "a") as fh:
        fh.write(json.dumps({"utc": utc(), "event": kind, **kw}, sort_keys=True, default=str) + "\n")


def assert_spawn_safe():
    """A spawned child re-imports __main__ from its file. stdin / -c / interactive mains cannot be re-imported."""
    main = sys.modules.get("__main__")
    spec = getattr(main, "__spec__", None)
    if spec is not None and getattr(spec, "name", None):
        return                                           # python -m pkg.mod: re-imported by module name
    f = getattr(main, "__file__", None)
    if not f or f.startswith("<") or not Path(f).is_file():
        raise SpawnUnsafe(f"__main__ is not importable by a spawned worker (file={f!r}); "
                          "launch a script file or `python -m`, never stdin / -c")


def run_jobs(fn: Callable[[dict], dict], jobs: Iterable[dict], rundir, key: str, out: str = "results.jsonl",
             workers: int = 3, max_failures: int = 0, max_tasks_per_child: Optional[int] = 20,
             heartbeat_s: float = 30.0) -> dict:
    """Run fn over jobs in spawn workers; append each result row to rundir/out (resumable on `key`).
    Returns the final PROGRESS record; raises RunFailed on worker death or too many job failures."""
    assert_spawn_safe()
    rundir = Path(rundir)
    rundir.mkdir(parents=True, exist_ok=True)
    outp = rundir / out
    done = set()
    if outp.exists():
        done = {json.loads(x)[key] for x in outp.read_text().splitlines() if x.strip()}
    jobs = list(jobs)
    todo = [j for j in jobs if j[key] not in done]
    prog = {"status": "RUNNING", "pid": os.getpid(), "start_utc": utc(), "heartbeat_utc": utc(),
            "last_result_utc": None, "n_total": len(jobs), "n_done": len(done), "n_failed": 0,
            "n_todo_at_start": len(todo)}
    lock = threading.Lock()
    stop = threading.Event()

    def _write():
        with lock:
            prog["heartbeat_utc"] = utc()
            _atomic_json(rundir / PROGRESS, prog)

    def _beat():
        while not stop.wait(heartbeat_s):
            _write()

    _write()
    _event(rundir, "start", n_total=len(jobs), n_todo=len(todo), pid=os.getpid())
    hb = threading.Thread(target=_beat, daemon=True)
    hb.start()
    kw = {"max_tasks_per_child": max_tasks_per_child} if max_tasks_per_child else {}
    try:
        with ProcessPoolExecutor(workers, mp_context=get_context("spawn"), **kw) as ex, open(outp, "a") as fh:
            pending = {ex.submit(fn, j): j for j in todo}
            while pending:
                fin, _ = wait(pending, return_when=FIRST_COMPLETED)
                for f in fin:
                    j = pending.pop(f)
                    try:
                        r = f.result()
                    except BrokenProcessPool as e:
                        raise RunFailed(f"worker process died ({e}); job {j[key]!r}") from e
                    except Exception as e:                       # the job raised: record, continue
                        with lock:
                            prog["n_failed"] += 1
                        with open(rundir / FAILURES, "a") as ff:
                            ff.write(json.dumps({"utc": utc(), key: j[key], "error": repr(e)[:2000]}) + "\n")
                        if prog["n_failed"] > max_failures:
                            raise RunFailed(f"{prog['n_failed']} job failures > max_failures {max_failures}")
                        continue
                    fh.write(json.dumps(r, default=float) + "\n")
                    fh.flush()
                    with lock:
                        prog["n_done"] += 1
                        prog["last_result_utc"] = utc()
                    _write()
    except BaseException as e:
        stop.set()
        with lock:
            prog["status"] = "FAILED"
            prog["error"] = repr(e)[:2000]
        _write()
        _event(rundir, "failed", error=repr(e)[:500])
        raise
    stop.set()
    with lock:
        prog["status"] = "DONE" if prog["n_failed"] == 0 else "DONE_WITH_FAILURES"
    _write()
    _event(rundir, "done", n_done=prog["n_done"], n_failed=prog["n_failed"])
    return prog


# -- watchdog ----------------------------------------------------------------------------------------------------
def _parse(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    import calendar
    return float(calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")))


def status(rundir, stall_s: float, now: Optional[float] = None, alive: Optional[bool] = None) -> dict:
    """Judge a run by its science. DONE / FAILED from PROGRESS; else STALLED if no new result (or no start) within
    stall_s, DEAD if the process is gone without a terminal status, OK otherwise."""
    rundir = Path(rundir)
    now = time.time() if now is None else now
    p = rundir / PROGRESS
    if not p.exists():
        return {"verdict": "NO_PROGRESS_FILE"}
    prog = json.loads(p.read_text())
    if prog["status"] in ("DONE", "DONE_WITH_FAILURES", "FAILED"):
        return {"verdict": prog["status"], **prog}
    if alive is None:
        try:
            os.kill(int(prog["pid"]), 0)
            alive = True
        except OSError:
            alive = False
    last = _parse(prog.get("last_result_utc")) or _parse(prog.get("start_utc"))
    since = now - last
    if not alive:
        return {"verdict": "DEAD", "since_last_result_s": since, **prog}
    if since > stall_s:
        return {"verdict": "STALLED", "since_last_result_s": since, **prog}
    return {"verdict": "OK", "since_last_result_s": since, **prog}


def _kill_group(proc: subprocess.Popen, grace: float = 10.0):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(grace)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def launch(rundir, cmd, stall_s: float, max_restarts: int = 1, poll_s: float = 10.0,
           start_grace_s: Optional[float] = None) -> str:
    """Run cmd (its own session / process group) under the progress watchdog. Returns the final verdict."""
    rundir = Path(rundir)
    rundir.mkdir(parents=True, exist_ok=True)
    start_grace_s = stall_s if start_grace_s is None else start_grace_s
    restarts = 0
    while True:
        t_launch = time.time()
        (rundir / PROGRESS).unlink(missing_ok=True)
        log = open(rundir / "run.log", "ab")
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        (rundir / "PID").write_text(str(proc.pid))
        _event(rundir, "launch", cmd=cmd, pid=proc.pid, attempt=restarts)
        verdict = None
        while verdict is None:
            time.sleep(poll_s)
            rc = proc.poll()
            if not (rundir / PROGRESS).exists():
                if rc is not None:
                    verdict = "FAILED"                           # died before reporting any progress
                    _event(rundir, "exit_without_progress", rc=rc)
                elif time.time() - t_launch > start_grace_s:
                    verdict = "STALLED"
                    _event(rundir, "stalled", reason="no PROGRESS.json within start grace")
                continue
            s = status(rundir, stall_s, alive=rc is None)
            v = s["verdict"]
            if v in ("DONE", "DONE_WITH_FAILURES"):
                if rc is None:
                    try:
                        proc.wait(60)
                    except subprocess.TimeoutExpired:
                        pass
                verdict = v
            elif v in ("FAILED", "DEAD"):
                verdict = "FAILED"
                _event(rundir, "failed", rc=rc, progress_verdict=v)
            elif v == "STALLED":
                verdict = "STALLED"
                _event(rundir, "stalled", since_last_result_s=round(s["since_last_result_s"]),
                       n_done=s["n_done"], n_total=s["n_total"])
        log.close()
        if verdict == "STALLED" or proc.poll() is None:
            _kill_group(proc)
            _event(rundir, "killed", pid=proc.pid)
        if verdict == "STALLED" and restarts < max_restarts:
            restarts += 1
            _event(rundir, "restart", attempt=restarts)
            continue
        if verdict == "STALLED":
            # leave a terminal record: a stalled run whose restarts are exhausted is FAILED, never "running"
            p = rundir / PROGRESS
            prog = json.loads(p.read_text()) if p.exists() else {}
            prog.update({"status": "FAILED", "error": "STALLED; restarts exhausted"})
            _atomic_json(p, prog)
        _event(rundir, "final", verdict=verdict, restarts=restarts)
        return verdict


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m prometheus.cosmos.supervise")
    sub = ap.add_subparsers(dest="op", required=True)
    a = sub.add_parser("launch")
    a.add_argument("rundir")
    a.add_argument("--stall", type=float, required=True, help="seconds without a new result => STALLED")
    a.add_argument("--restarts", type=int, default=1)
    a.add_argument("--poll", type=float, default=10.0)
    a.add_argument("cmd", nargs=argparse.REMAINDER)
    s = sub.add_parser("status")
    s.add_argument("rundir")
    s.add_argument("--stall", type=float, default=900.0)
    ns = ap.parse_args(argv)
    if ns.op == "launch":
        cmd = ns.cmd[1:] if ns.cmd[:1] == ["--"] else ns.cmd
        if not cmd:
            ap.error("launch needs -- <cmd ...>")
        v = launch(ns.rundir, cmd, ns.stall, ns.restarts, ns.poll)
        print(json.dumps({"verdict": v, "rundir": ns.rundir}))
        return 0 if v in ("DONE",) else 1
    print(json.dumps(status(ns.rundir, ns.stall), default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
