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

from primordial.fabric import broker
from primordial.fabric.rows import RowWriter

JOBS, ROWS, DONE = "pm:jobs:{}", "pm:rows:{}", "pm:jobs:{}:done"
STOP = "pm:jobs:{}:stop"            # F14: set by the epoch controller; the worker takes no job while it exists
PUSH_LOCK = "pm:push:lock:{}"       # ops.push holds it during a rebase; the worker takes no job while it exists.
                                    # Separate from STOP: the epoch controller clears STOP at resume (E, 09-15).
WSTATE = "pm:worker:{}"             # hash {state: idle|busy|stopped, job_id, ts}, TTL WSTATE_TTL
WSTATE_TTL = 30
RESUMABLE = "pm:resumable"         # F-R5-3: hash job_key -> resumable job object (JSON)
PROGRESS = "pm:progress:{}:{}"      # F-R5-3: ctx.progress() units, readable after a kill
DONE_ENV_FIELDS =("cohort", "campaign_stage", "experiment_class", "predicate_id")   # F-R5-1: copied into done
CKPT_DIR = pathlib.Path(os.environ.get("PM_CKPT_DIR", "C:/Users/jcrai/lab/pm-data/ckpt"))


class JobPaused(Exception):
    pass


SOCKET_TIMEOUT_S = 30.0             # > serve's block_ms: redis-py 8 defaults socket_timeout to 5 s, which
                                    # raced XREADGROUP block=5000 and killed an idle worker (G, 2026-09-14)


def _redis(url):
    import redis
    return redis.Redis.from_url(url, decode_responses=True, socket_timeout=SOCKET_TIMEOUT_S)


def submit(lane: str, fn: str, exp_id: str, rows_path, ttl_cpu_s: float, kwargs: dict | None = None,
           url: str | None = None, r=None, job_key: str = "", segment: int = 0, cpu_prior: float = 0.0,
           envelope: dict | None = None, wall_prior: float = 0.0) -> str:
    """Queue a job (or the next segment of a checkpointed one). -> job_id.
    envelope (F-R5-1): the job envelope; the worker admits or refuses it (fabric/envelope.py)."""
    from primordial.bus import bus
    r = r or _redis(url or bus.URL)
    job_id = uuid.uuid4().hex[:12]
    spec = {"job_id": job_id, "fn": fn, "exp_id": exp_id, "rows": str(rows_path),
            "ttl_cpu_s": str(float(ttl_cpu_s)), "kwargs": json.dumps(kwargs or {}),
            "job_key": job_key or job_id, "segment": str(int(segment)),
            "cpu_prior": f"{float(cpu_prior):.6f}", "wall_prior": f"{float(wall_prior):.6f}",
            "ts": f"{time.time():.3f}"}
    if envelope is not None:
        spec["envelope"] = json.dumps(envelope, sort_keys=True)
    r.xadd(JOBS.format(lane), spec)
    return job_id


def code_sha(repo) -> str:
    import subprocess
    q = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    return q.stdout.strip()


def code_file_sha256(fn: str) -> str | None:
    """sha256 of the job function's module source: rows commits move HEAD, so resume compares this."""
    import hashlib
    import importlib.util
    try:
        spec = importlib.util.find_spec(fn.partition(":")[0])
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.origin or not os.path.exists(spec.origin):
        return None
    return hashlib.sha256(pathlib.Path(spec.origin).read_bytes()).hexdigest()


def resumables(r) -> dict:
    return {k: json.loads(v) for k, v in r.hgetall(RESUMABLE).items()}


def resume(r, job_key: str, force: bool = False) -> dict:
    """F-R5-3: requeue a job from its resumable object. -> {ok, job_id} or {ok: False, reason}.
    Refused (not raised): NO_OBJECT, ALREADY_QUEUED (a segment is still queued), CODE_CHANGED (the job
    module's source differs from the checkpointing run; force=True overrides), NO_CHECKPOINT."""
    raw = r.hget(RESUMABLE, job_key)
    if not raw:
        return {"ok": False, "reason": "NO_OBJECT"}
    o = json.loads(raw)
    if o.get("queued_job_id") and not force:
        return {"ok": False, "reason": "ALREADY_QUEUED", "queued_job_id": o["queued_job_id"]}
    if code_file_sha256(o["function"]) != o.get("code_file_sha256") and not force:
        return {"ok": False, "reason": "CODE_CHANGED"}
    if not pathlib.Path(o["checkpoint"]).exists():
        return {"ok": False, "reason": "NO_CHECKPOINT"}
    job_id = submit(o["lane"], o["function"], o["exp_id"], o["rows"], o["ttl_cpu_s"], o["kwargs"], r=r,
                    job_key=o["job_key"], segment=o["segment"], cpu_prior=o["budget_consumed"]["cpu_s"],
                    envelope=o.get("envelope"), wall_prior=o["budget_consumed"]["wall_s"])
    r.hset(RESUMABLE, job_key, json.dumps(dict(o, queued_job_id=job_id), sort_keys=True))
    return {"ok": True, "job_id": job_id}


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

    def progress(self, completed_units, remaining_units) -> None:
        """F-R5-3: report work units; the resumable object carries the last report (survives a kill)."""
        self.r.set(PROGRESS.format(self.lane, self.job_key),
                   json.dumps({"completed_units": completed_units, "remaining_units": remaining_units}), ex=86400)

    def pause(self, state, completed_units=None, remaining_units=None) -> None:
        if completed_units is not None or remaining_units is not None:
            self.progress(completed_units, remaining_units)
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
        ctx.threads = int(job["threads"]) if job.get("threads") else None
        if ctx.threads and "numba" in sys.modules:           # F-R5-5: the CPU token's thread grant
            try:
                import numba
                numba.set_num_threads(max(1, min(ctx.threads, numba.config.NUMBA_NUM_THREADS)))
            except Exception:
                pass
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
                 ckpt_dir=None, auto_requeue: bool = True, broker: bool | None = None):
        from primordial.bus import bus
        self.lane, self.url = lane, url or bus.URL
        self.broker = broker                      # F-R5-5: None = broker iff pm:capacity:profile exists
        self.auto_requeue = auto_requeue          # F9: requeue a paused job's next segment (F-R5-3 can resume instead)
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

    @staticmethod
    def _envelope(job: dict):
        raw = job.get("envelope")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return "unparseable"

    def _brokered(self) -> bool:
        return self.broker if self.broker is not None else broker.profile(self.r) is not None

    def _admit(self, job: dict) -> dict | None:
        """F-R5-1/2: None = legacy job outside a round (no envelope, no clock); else admit()'s verdict."""
        from primordial.fabric import envelope as EV
        from primordial.ops import round_clock as RC
        clock = RC.read(self.r)
        env = self._envelope(job)
        if env is None and clock is None:
            return None
        return EV.admit(env, kind="cpu", clock=clock, continuation=int(job.get("segment", 0) or 0) > 0)

    def _refuse(self, job: dict, verdict: dict) -> dict:
        from primordial.fabric import envelope as EV
        env = self._envelope(job)
        ev = EV.refuse(self.r, self.lane, job, verdict, env)
        env = env if isinstance(env, dict) else {}
        key = job.get("job_key") or job["job_id"]
        raw = self.r.hget(RESUMABLE, key)
        if raw and json.loads(raw).get("queued_job_id") == job["job_id"]:   # its queued segment was refused:
            self.r.hset(RESUMABLE, key, json.dumps(dict(json.loads(raw), queued_job_id=None,   # resumable again
                                                        refused=verdict["reasons"]), sort_keys=True))
        out = {"job_id": job["job_id"], "status": "refused", "event": ev["event"], "reasons": verdict["reasons"],
               "rows": 0, "cpu_s": 0.0, "wall_s": 0.0, "job_key": job.get("job_key") or job["job_id"],
               "segment": int(job.get("segment", 0) or 0), "ended": round(time.time(), 3),
               **{k: env.get(k) for k in DONE_ENV_FIELDS}}
        self.r.xadd(DONE.format(self.lane), {"json": json.dumps(out, sort_keys=True)})
        self.log(f"job {job['job_id']} {job.get('fn')} -> refused {ev['event']} {verdict['reasons']}")
        return out

    def _event(self, name: str, rec: dict) -> None:
        from primordial.fabric import envelope as EV
        self.r.xadd(EV.EVENTS, {"event": name, "json": json.dumps(dict(rec, event=name, lane=self.lane),
                                                                  sort_keys=True)})

    def run_job(self, job: dict) -> dict:
        if self.child is None or not self.child.is_alive():
            self._spawn()
        env = self._envelope(job)
        env = env if isinstance(env, dict) else {}
        ttl = float(job["ttl_cpu_s"])
        if env.get("cpu_budget_s") is not None:              # F-R5-1: the envelope caps the task TTL
            ttl = min(ttl, float(env["cpu_budget_s"]))
        wall_limit = float(env["wall_budget_s"]) if env.get("wall_budget_s") is not None else None
        wall_prior = float(job.get("wall_prior", 0) or 0)
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
                status, result = "timeout", {"ok": False, "cpu_s": cpu, "limit": "cpu"}
                break
            if wall_limit is not None and time.perf_counter() - t0 + wall_prior > wall_limit:
                cpu = self._child_cpu() - cpu0
                self._kill_child()
                status, result = "timeout", {"ok": False, "cpu_s": cpu, "limit": "wall"}
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
                     "kind": "job_end", "reason": status, "limit": result.get("limit"), "ttl_cpu_s": ttl,
                     "wall_budget_s": wall_limit, "cpu_s": cpu_s, "wall_s": wall_s,
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
               "cpu_prior": cpu_prior, "wall_prior": wall_prior, "commit_error": commit_error,
               "limit": result.get("limit"), **{k: env.get(k) for k in DONE_ENV_FIELDS},
               "cpu_token": json.loads(job["cpu_token"]) if job.get("cpu_token") else None}
        if status == "paused" and self.auto_requeue:
            out["next_job_id"] = submit(self.lane, job["fn"], job["exp_id"], job["rows"], float(job["ttl_cpu_s"]),
                                        json.loads(job["kwargs"]), r=self.r, job_key=out["job_key"],
                                        segment=out["segment"] + 1, cpu_prior=cpu_prior + (cpu_s or 0),
                                        envelope=env or None, wall_prior=wall_prior + wall_s)
        ckpt = pathlib.Path(self.ckpt_dir) / self.lane / f"{out['job_key']}.pkl"
        if status == "ok":
            self.r.hdel(RESUMABLE, out["job_key"])
            self.r.delete(PROGRESS.format(self.lane, out["job_key"]))
        elif status == "paused" or (status == "timeout" and ckpt.exists()):
            obj = self._resumable(job, env, out, ckpt, ttl, wall_limit)
            out["resumable"] = True
            self._event("CHECKPOINTED", {k: obj[k] for k in ("job_key", "segment", "checkpoint", "completed_units",
                                                              "remaining_units", "reason", "queued_job_id")})
        if status == "timeout":
            self._event("TIMEOUT", {k: out[k] for k in ("job_id", "job_key", "segment", "rows", "cpu_s", "wall_s",
                                                         "limit", "sha", "rows_path")})
        self.r.xadd(DONE.format(self.lane), {"json": json.dumps(out, sort_keys=True)})
        self.log(f"job {job['job_id']} {job['fn']} -> {status} rows={n} cpu={cpu_s} wall={wall_s:.2f}s")
        return out

    def _resumable(self, job: dict, env: dict, out: dict, ckpt: pathlib.Path, ttl: float, wall_limit) -> dict:
        """F-R5-3: the resumable job object (operator 19 s4.5), written to pm:resumable[job_key]."""
        units = json.loads(self.r.get(PROGRESS.format(self.lane, out["job_key"])) or "{}")
        cpu_used = out["cpu_prior"] + (out["cpu_s"] or 0.0)
        wall_used = out["wall_prior"] + out["wall_s"]
        obj = {"job_key": out["job_key"], "function": job["fn"], "kwargs": json.loads(job["kwargs"]),
               "checkpoint": str(ckpt), "rows": job["rows"],
               "completed_units": units.get("completed_units"), "remaining_units": units.get("remaining_units"),
               "budget_consumed": {"cpu_s": round(cpu_used, 3), "wall_s": round(wall_used, 3)},
               "budget_remaining": {"cpu_s": round(ttl - cpu_used, 3),
                                    "wall_s": None if wall_limit is None else round(wall_limit - wall_used, 3)},
               "code_sha": code_sha(self.repo), "code_file_sha256": code_file_sha256(job["fn"]),
               "lane": self.lane, "exp_id": job["exp_id"], "envelope": env or None,
               "ttl_cpu_s": float(job["ttl_cpu_s"]), "segment": out["segment"] + 1, "reason": out["status"],
               "queued_job_id": out.get("next_job_id"), "ts": round(time.time(), 3)}
        self.r.hset(RESUMABLE, out["job_key"], json.dumps(obj, sort_keys=True))
        return obj

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
                if self.r.exists(STOP.format(self.lane)) or self.r.exists(PUSH_LOCK.format(self.lane)):
                    self._state("stopped")
                    time.sleep(min(block_ms / 1000, 0.1))
                    idle0 = time.monotonic()
                    continue
                tok = None
                if self._brokered():                           # F-R5-5: no free CPU token -> take no job
                    tok = broker.acquire(self.r, self.lane, ttl_s=60)
                    if tok is None:
                        self._state("waiting_cpu")
                        time.sleep(min(block_ms / 1000, 0.1))
                        continue
                self._state("idle")
                got = self.r.xreadgroup(self.group, consumer, {JOBS.format(self.lane): ">"}, count=1,
                                        block=min(block_ms, 200) if tok else block_ms)
                msgs = [m for _, ms in (got or []) for m in ms]
                if not msgs:
                    broker.release(self.r, tok)
                    if idle_exit_s is not None and time.monotonic() - idle0 > idle_exit_s:
                        break
                    continue
                mid, job = msgs[0]
                verdict = self._admit(job)
                if verdict is not None and not verdict["ok"]:
                    broker.release(self.r, tok)
                    done.append(self._refuse(job, verdict))
                    self.r.xack(JOBS.format(self.lane), self.group, mid)
                    continue
                if tok is not None:
                    env = self._envelope(job)
                    env = env if isinstance(env, dict) else {}
                    tok = broker.assign(self.r, tok, job, env.get("cohort"),
                                        ttl_s=float(env.get("wall_budget_s") or 3600) + 120)
                    job = dict(job, threads=str(tok["threads"]),
                               cpu_token=json.dumps({"slot": tok["slot"], "threads": tok["threads"]}))
                self._state("busy", job["job_id"])
                try:
                    done.append(self.run_job(job))
                finally:
                    broker.release(self.r, tok)
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
