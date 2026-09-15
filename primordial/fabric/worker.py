"""F7 (round 3): a warm worker per lane. The task TTL kills the job, never the session.

Round 1 paid ~17 s of fixed cost per experiment process (10 s Redis connect,
6.2 s JIT, ~0.7 s import/init; fabric/perf/PROFILE_ROUND1 s3), and a TTL had
no clean kill target. Here:

  supervisor  one per lane. Reads job specs from the stream pm:jobs:<L>
              (consumer group worker-<L>), owns the RowWriter for each job,
              drains rows from pm:rows:<L>, and watches the child's CPU time.
  child       one long-lived spawned process holding imports, compiled
              kernels, a Redis pool and `ctx.cache` (a dict kept across jobs).
              It runs `module:function(ctx, **kwargs)`; ctx.emit(row) XADDs
              the row to pm:rows:<L>.

A job whose child CPU time passes ttl_cpu_s is killed with its child. The
supervisor drains every row the job had already emitted, appends a
status=timeout row, commits the file, and spawns a fresh child for the next
job. Rows are committed by the supervisor's RowWriter, so a job cannot lose
its rows by dying. Each job's outcome goes to pm:jobs:<L>:done.

F14: while pm:jobs:<L>:stop exists the worker takes no job and reports
`stopped` in pm:worker:<L>; a job received before it saw the flag runs to
completion first, so no job spans an epoch's export and commit.

F9: a long job checkpoints across epochs. It polls ctx.should_pause() (the
stop flag) at safe points and calls ctx.pause(state): the state is pickled
atomically to <ckpt_dir>/<lane>/<job_key>.pkl, the segment ends `paused`,
and the supervisor requeues the same job (job_key, segment + 1, cumulative
CPU carried so ttl_cpu_s bounds the whole job). The next segment reads
ctx.load_checkpoint(). A finished job's checkpoint is removed.

    python -m primordial.fabric.worker serve --lane F
    python -m primordial.fabric.worker submit F primordial.fabric.selftest_jobs:jit_probe \\
        --exp F7-probe --rows primordial/ledger/rows/F/F7-probe.jsonl --ttl-cpu-s 60 --kwargs '{}'
"""
from __future__ import annotations

import argparse
import importlib
import json
import multiprocessing as mp
import os
import pathlib
import pickle
import tempfile
import sys
import time
import traceback
import uuid

from primordial.fabric.rows import RowWriter

JOBS, ROWS, DONE = "pm:jobs:{}", "pm:rows:{}", "pm:jobs:{}:done"
STOP = "pm:jobs:{}:stop"            # F14: set by the epoch controller; the worker takes no job while it exists
WSTATE = "pm:worker:{}"             # hash {state: idle|busy|stopped, job_id, ts}, TTL WSTATE_TTL
WSTATE_TTL = 30
CKPT_DIR = pathlib.Path(os.environ.get("PM_CKPT_DIR", "C:/Users/jcrai/lab/pm-data/ckpt"))


class JobPaused(Exception):
    pass


SOCKET_TIMEOUT_S = 30.0             # > serve's block_ms: redis-py 8 defaults socket_timeout to 5 s, which
                                    # raced XREADGROUP block=5000 and killed an idle worker (G, 2026-09-14)


def _redis(url):
    import redis
    return redis.Redis.from_url(url, decode_responses=True, socket_timeout=SOCKET_TIMEOUT_S)


def submit(lane: str, fn: str, exp_id: str, rows_path, ttl_cpu_s: float, kwargs: dict | None = None,
           url: str | None = None, r=None, job_key: str = "", segment: int = 0, cpu_prior: float = 0.0) -> str:
    """Queue a job (or the next segment of a checkpointed one). -> job_id."""
    from primordial.bus import bus
    r = r or _redis(url or bus.URL)
    job_id = uuid.uuid4().hex[:12]
    r.xadd(JOBS.format(lane), {"job_id": job_id, "fn": fn, "exp_id": exp_id, "rows": str(rows_path),
                               "ttl_cpu_s": str(float(ttl_cpu_s)), "kwargs": json.dumps(kwargs or {}),
                               "job_key": job_key or job_id, "segment": str(int(segment)),
                               "cpu_prior": f"{float(cpu_prior):.6f}", "ts": f"{time.time():.3f}"})
    return job_id


# ------------------------------------------------------------------ child

class Ctx:
    def __init__(self, r, lane):
        self.r, self.lane, self.cache = r, lane, {}
        self.job_id = self.job_key = ""
        self.segment = 0
        self.ckpt_dir = CKPT_DIR
        self.n_emitted = 0

    # F9 checkpoints
    def _ckpt(self) -> pathlib.Path:
        return pathlib.Path(self.ckpt_dir) / self.lane / f"{self.job_key}.pkl"

    def should_pause(self) -> bool:
        return bool(self.r.exists(STOP.format(self.lane)))

    def load_checkpoint(self):
        p = self._ckpt()
        if not p.exists():
            return None
        with open(p, "rb") as fh:
            return pickle.load(fh)

    def checkpoint(self, state) -> None:
        p = self._ckpt()
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".ck-", dir=p.parent)
        with os.fdopen(fd, "wb") as fh:
            pickle.dump(state, fh)
        os.replace(tmp, p)

    def pause(self, state) -> None:
        self.checkpoint(state)
        raise JobPaused()

    def emit(self, row: dict) -> None:
        self.r.xadd(ROWS.format(self.lane), {"job_id": self.job_id, "json": json.dumps(row, sort_keys=True)})
        self.n_emitted += 1


def _child_main(pipe, url: str, lane: str) -> None:
    ctx = Ctx(_redis(url), lane)
    while True:
        job = pipe.recv()
        if job is None:
            return
        ctx.job_id, ctx.n_emitted = job["job_id"], 0
        ctx.job_key, ctx.segment = job.get("job_key") or job["job_id"], int(job.get("segment", 0))
        ctx.ckpt_dir = job.get("ckpt_dir") or CKPT_DIR
        t0 = time.perf_counter()
        try:
            mod, _, name = job["fn"].partition(":")
            getattr(importlib.import_module(mod), name)(ctx, **json.loads(job["kwargs"]))
            ctx._ckpt().unlink(missing_ok=True)
            pipe.send({"ok": True, "wall_s": time.perf_counter() - t0, "emitted": ctx.n_emitted})
        except JobPaused:
            pipe.send({"ok": True, "paused": True, "wall_s": time.perf_counter() - t0, "emitted": ctx.n_emitted})
        except Exception:
            pipe.send({"ok": False, "wall_s": time.perf_counter() - t0, "emitted": ctx.n_emitted,
                       "error": traceback.format_exc()[-2000:]})


# ------------------------------------------------------------------ supervisor

class Worker:
    def __init__(self, lane: str, url: str | None = None, repo=None, poll_s: float = 0.05, log=print,
                 ckpt_dir=None):
        from primordial.bus import bus
        self.lane, self.url = lane, url or bus.URL
        self.r = _redis(self.url)
        self.repo = pathlib.Path(repo) if repo else pathlib.Path(__file__).resolve().parents[2]
        self.poll_s, self.log = poll_s, log
        self.child = self.pipe = None
        self.children_spawned = 0
        self.ckpt_dir = str(ckpt_dir or CKPT_DIR)
        self.exit_requested = False             # set from another thread: serve() returns after the current job
        self.rows_cursor = "$"
        self.group = f"worker-{lane}"
        try:
            self.r.xgroup_create(JOBS.format(lane), self.group, id="0", mkstream=True)
        except Exception as e:
            if "BUSYGROUP" not in str(e):
                raise

    def _spawn(self) -> None:
        c = mp.get_context("spawn")
        self.pipe, child_end = c.Pipe()
        self.child = c.Process(target=_child_main, args=(child_end, self.url, self.lane), daemon=True)
        self.child.start()
        self.children_spawned += 1

    def _kill_child(self) -> None:
        import psutil
        try:
            p = psutil.Process(self.child.pid)
            for q in reversed([p] + p.children(recursive=True)):
                try:
                    q.kill()
                except psutil.Error:
                    pass
        except psutil.Error:
            pass
        self.child.join(timeout=10)
        self.child = self.pipe = None

    def _child_cpu(self) -> float:
        import psutil
        t = psutil.Process(self.child.pid).cpu_times()
        return t.user + t.system

    def _drain(self, job_id: str, w: RowWriter) -> int:
        n = 0
        while True:
            got = self.r.xread({ROWS.format(self.lane): self.rows_cursor}, count=500)
            msgs = [m for _, ms in (got or []) for m in ms]
            if not msgs:
                return n
            for mid, f in msgs:
                self.rows_cursor = mid
                if f.get("job_id") != job_id:
                    continue
                row = json.loads(f["json"])
                row.setdefault("job_id", job_id)
                try:
                    w.write(row)
                except ValueError as e:
                    w.write({"status": "aborted", "reason": f"bad row: {e}", "job_id": job_id, "row": row})
                n += 1

    def run_job(self, job: dict) -> dict:
        if self.child is None or not self.child.is_alive():
            self._spawn()
        ttl = float(job["ttl_cpu_s"])
        cpu_prior = float(job.get("cpu_prior", 0) or 0)
        job = dict(job, ckpt_dir=self.ckpt_dir)
        rows_path = pathlib.Path(job["rows"])
        if not rows_path.is_absolute():
            rows_path = self.repo / rows_path
        # the rows cursor starts at the stream's current end, so only this job's rows are read
        last = self.r.xrevrange(ROWS.format(self.lane), count=1)
        self.rows_cursor = last[0][0] if last else "0"
        w = RowWriter(rows_path, job["exp_id"], commit_every_s=60, repo=self.repo)
        cpu0 = self._child_cpu()
        t0, started = time.perf_counter(), time.time()
        self.pipe.send(job)
        result, status = None, "ok"
        n = 0
        beat = time.monotonic()
        while result is None:
            if time.monotonic() - beat >= WSTATE_TTL / 3:  # a long job must not look dead (pm:worker TTL)
                self._state("busy", job["job_id"])
                beat = time.monotonic()
            n += self._drain(job["job_id"], w)
            if self.pipe.poll(self.poll_s):
                result = self.pipe.recv()
                status = ("paused" if result.get("paused") else "ok") if result["ok"] else "error"
                break
            if not self.child.is_alive():
                status, result = "died", {"ok": False, "error": f"child exit {self.child.exitcode}"}
                break
            cpu = self._child_cpu() - cpu0
            if cpu + cpu_prior > ttl:
                self._kill_child()
                status, result = "timeout", {"ok": False, "cpu_s": cpu}
                break
        n += self._drain(job["job_id"], w)
        if status == "timeout":
            cpu_s = result["cpu_s"]
        elif status == "died":
            cpu_s, self.child, self.pipe = None, None, None
        else:
            cpu_s = self._child_cpu() - cpu0
        wall_s = time.perf_counter() - t0
        if status in ("timeout", "died", "error"):
            w.write({"status": "timeout" if status == "timeout" else "aborted", "job_id": job["job_id"],
                     "kind": "job_end", "reason": status, "ttl_cpu_s": ttl, "cpu_s": cpu_s, "wall_s": wall_s,
                     "rows_before": n, "error": (result.get("error") or "")[-500:],
                     "job_key": job.get("job_key"), "segment": int(job.get("segment", 0)), "cpu_prior": cpu_prior})
        commit_error = None
        try:
            w.close(note=f"(job {job['job_id']} {status})")
        except Exception as e:                 # a failed rows commit must not kill serve(); rows stay in the file
            commit_error = f"{type(e).__name__}: {e}"[:500]
            self.log(f"job {job['job_id']} rows commit FAILED: {commit_error}")
        sha = self._head()
        out = {"job_id": job["job_id"], "status": status, "rows": n, "cpu_s": cpu_s, "wall_s": round(wall_s, 3),
               "child_wall_s": result.get("wall_s"), "sha": sha, "rows_path": str(rows_path),
               "started": round(started, 3), "ended": round(time.time(), 3),
               "job_key": job.get("job_key") or job["job_id"], "segment": int(job.get("segment", 0)),
               "cpu_prior": cpu_prior, "commit_error": commit_error}
        if status == "paused":
            out["next_job_id"] = submit(self.lane, job["fn"], job["exp_id"], job["rows"], ttl,
                                        json.loads(job["kwargs"]), r=self.r, job_key=out["job_key"],
                                        segment=out["segment"] + 1, cpu_prior=cpu_prior + (cpu_s or 0))
        self.r.xadd(DONE.format(self.lane), {"json": json.dumps(out, sort_keys=True)})
        self.log(f"job {job['job_id']} {job['fn']} -> {status} rows={n} cpu={cpu_s} wall={wall_s:.2f}s")
        return out

    def _head(self) -> str:
        import subprocess
        q = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "--short", "HEAD"], capture_output=True,
                           text=True)
        return q.stdout.strip()

    def _state(self, state: str, job_id: str = "") -> None:
        k = WSTATE.format(self.lane)
        self.r.hset(k, mapping={"state": state, "job_id": job_id, "ts": f"{time.time():.3f}"})
        self.r.expire(k, WSTATE_TTL)

    def serve(self, max_jobs: int | None = None, block_ms: int = 5000, idle_exit_s: float | None = None,
              deadline_s: float | None = None) -> list:
        consumer = os.environ.get("PM_TAG", "worker")
        done, idle0 = [], time.monotonic()
        end = None if deadline_s is None else time.monotonic() + deadline_s
        try:
            while ((max_jobs is None or len(done) < max_jobs) and (end is None or time.monotonic() < end)
                   and not self.exit_requested):
                if self.r.exists(STOP.format(self.lane)):
                    self._state("stopped")
                    time.sleep(min(block_ms / 1000, 0.1))
                    idle0 = time.monotonic()
                    continue
                self._state("idle")
                got = self.r.xreadgroup(self.group, consumer, {JOBS.format(self.lane): ">"}, count=1,
                                        block=block_ms)
                msgs = [m for _, ms in (got or []) for m in ms]
                if not msgs:
                    if idle_exit_s is not None and time.monotonic() - idle0 > idle_exit_s:
                        break
                    continue
                mid, job = msgs[0]
                self._state("busy", job["job_id"])
                done.append(self.run_job(job))
                self.r.xack(JOBS.format(self.lane), self.group, mid)
                idle0 = time.monotonic()
        finally:
            self.stop()
        return done

    def stop(self) -> None:
        self.r.delete(WSTATE.format(self.lane))
        if self.child is not None and self.child.is_alive():
            try:
                self.pipe.send(None)
                self.child.join(timeout=5)
            except (OSError, EOFError):
                pass
            if self.child.is_alive():
                self._kill_child()
        self.child = self.pipe = None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--lane", default=os.environ.get("PM_LANE", ""))
    s.add_argument("--max-jobs", type=int)
    s.add_argument("--idle-exit-s", type=float)
    q = sub.add_parser("submit")
    q.add_argument("lane")
    q.add_argument("fn")
    q.add_argument("--exp", required=True)
    q.add_argument("--rows", required=True)
    q.add_argument("--ttl-cpu-s", type=float, required=True)
    q.add_argument("--kwargs", default="{}")
    a = ap.parse_args(argv)
    if a.cmd == "submit":
        print(submit(a.lane, a.fn, a.exp, a.rows, a.ttl_cpu_s, json.loads(a.kwargs)))
        return 0
    if not a.lane:
        raise SystemExit("--lane or PM_LANE required")
    for d in Worker(a.lane).serve(max_jobs=a.max_jobs, idle_exit_s=a.idle_exit_s):
        print(json.dumps(d, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
