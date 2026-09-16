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

G3 (round 8, D30 + D22): a continuation (segment > 0: an epoch requeue, a segment-wall pause, resume()) is
queued on pm:jobs:<L>:cont, not at the END of pm:jobs:<L> behind later submissions. It carries priority_ts, the
ORIGINAL queue entry time of segment 0. The worker peeks the head of both streams and takes the one with the
lower priority_ts, so a requeued continuation runs before any job submitted after it, and never ahead of a job
that was queued before it (queue position cannot silently convert priority). A shadow copy of the spec
(shadow=cont) stays on pm:jobs:<L> so every job_id lookup there (drain sizing, budget, receipt guard) still
resolves; the worker acks shadows without running them. Brokered, the head's priority_ts is also the worker's
place in the cross-lane FIFO wait queue (broker.py). Every done record carries the five queue fields (G5).

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
from primordial.fabric import telemetry as TM
from primordial.fabric.rows import RowWriter

JOBS, ROWS, DONE = "pm:jobs:{}", "pm:rows:{}", "pm:jobs:{}:done"
CONT = "pm:jobs:{}:cont"            # G3 (D30): continuation class, taken by original queue entry time
STOP = "pm:jobs:{}:stop"            # F14: set by the epoch controller; the worker takes no job while it exists
PUSH_LOCK = "pm:push:lock:{}"       # ops.push holds it during a rebase; the worker takes no job while it exists.
                                    # Separate from STOP: the epoch controller clears STOP at resume (E, 09-15).
WSTATE = "pm:worker:{}"             # hash {state: idle|busy|stopped, job_id, ts}, TTL WSTATE_TTL
WSTATE_TTL = 30
REG = "pm:worker:reg:{}:{}"         # F-R7-1: hash {pid, lane, repo, round_id, cmdline, host, started_ts, tag}, TTL REG_TTL
REG_TTL = 90
SEGMENT_GRACE_S = 60.0              # F-R6-4: a checkpointable job past its segment wall gets this long to pause
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
           envelope: dict | None = None, wall_prior: float = 0.0, code_file_sha256: str | None = None,
           continuation: bool | None = None, priority_ts: float | None = None) -> str:
    """Queue a job (or the next segment of a checkpointed one). -> job_id.
    envelope (F-R5-1): the job envelope; the worker admits or refuses it (fabric/envelope.py).
    code_file_sha256 (F-R6-2): the fn module's source fingerprint; computed here when not given (a later
    segment passes the original, so a mid-job edit is caught).
    continuation (G3): None = segment > 0. A continuation goes to pm:jobs:<L>:cont with priority_ts = the original
    segment's queue entry time (pass it on; defaults to now), plus a shadow spec on pm:jobs:<L> for lookups."""
    from primordial.bus import bus
    r = r or _redis(url or bus.URL)
    job_id = uuid.uuid4().hex[:12]
    spec = {"job_id": job_id, "fn": fn, "exp_id": exp_id, "rows": str(rows_path),
            "ttl_cpu_s": str(float(ttl_cpu_s)), "kwargs": json.dumps(kwargs or {}),
            "job_key": job_key or job_id, "segment": str(int(segment)),
            "cpu_prior": f"{float(cpu_prior):.6f}", "wall_prior": f"{float(wall_prior):.6f}",
            "ts": f"{time.time():.3f}"}
    cont = int(segment) > 0 if continuation is None else bool(continuation)
    spec["queue_enter_ts"] = spec["ts"]
    spec["priority_ts"] = f"{float(priority_ts):.3f}" if (cont and priority_ts is not None) else spec["ts"]
    spec["continuation"] = "1" if cont else "0"
    if envelope is not None:
        spec["envelope"] = json.dumps(envelope, sort_keys=True)
    fp = code_file_sha256 or code_file_sha256_of(fn)
    if fp:
        spec["code_file_sha256"] = fp
    repo = code_repo_of(fn)                  # F-R7-3 (D14 guard): where the submitter's code lives
    if repo:
        spec["code_repo"] = repo
    if cont:
        r.xadd(CONT.format(lane), spec)
        r.xadd(JOBS.format(lane), dict(spec, shadow="cont"))     # lookups by job_id; never run from here
    else:
        r.xadd(JOBS.format(lane), spec)
    return job_id


def code_sha(repo) -> str:
    import subprocess
    q = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    return q.stdout.strip()


def _file_sha(path) -> str | None:
    import hashlib
    if not path or not os.path.exists(path):
        return None
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def code_file_sha256(fn: str) -> str | None:
    """sha256 of the job function's module source: rows commits move HEAD, so resume compares this."""
    import importlib.util
    try:
        spec = importlib.util.find_spec(fn.partition(":")[0])
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.origin:
        return None
    return _file_sha(spec.origin)


code_file_sha256_of = code_file_sha256      # submit() has a parameter of the same name


def _repo_root(path, modname: str) -> str | None:
    """The sys.path root a module was imported from (for primordial.x.y: the worktree), forward slashes."""
    if not path:
        return None
    p = pathlib.Path(path).resolve()
    depth = len(modname.split(".")) - (0 if p.name == "__init__.py" else 1)
    try:
        return p.parents[depth].as_posix()
    except IndexError:
        return None


def code_repo_of(fn: str) -> str | None:
    import importlib.util
    mod = fn.partition(":")[0]
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError):
        return None
    return _repo_root(spec.origin, mod) if spec is not None and spec.origin else None


THREAD_ENV = ("NUMBA_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")
_SPAWN_LOCK = __import__("threading").Lock()


def thread_env(threads: int) -> dict:
    """D19: the environment a child must be SPAWNED with to get `threads` (pools are sized at import)."""
    return {k: str(int(threads)) for k in THREAD_ENV}


def apply_child_threads(threads: int | None) -> int | None:
    """D19, inside a child: set numba to the grant (bounded by the pool it was spawned with); -> effective threads."""
    if threads:
        try:
            import numba
            numba.set_num_threads(max(1, min(int(threads), numba.config.NUMBA_NUM_THREADS)))
        except Exception:
            pass
    nb = sys.modules.get("numba")
    try:
        return int(nb.get_num_threads()) if nb is not None else None
    except Exception:
        return None


def _norm_path(p) -> str | None:
    return None if not p else os.path.normcase(os.path.abspath(str(p))).replace("\\", "/").rstrip("/")


def _closure_prefixes() -> tuple:
    """F-R7-3: module-name prefixes that count as in-repo code (the import closure fingerprinted per job)."""
    return tuple(x for x in os.environ.get("PM_CLOSURE_PREFIXES", "primordial.").split(",") if x)


def _f(x) -> float | None:
    return None if x in (None, "") else float(x)


def is_continuation(job: dict) -> bool:
    return job.get("continuation") == "1" or int(job.get("segment", 0) or 0) > 0


def queue_of(job: dict) -> dict:
    """G5: the five queue fields of a job, stamped at grant by serve(); a job run outside serve() is granted now."""
    if job.get("queue"):
        return json.loads(job["queue"])
    enter = _f(job.get("queue_enter_ts") or job.get("ts")) or time.time()
    return TM.queue_fields(enter, time.time(), None, is_continuation(job))


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
                    envelope=o.get("envelope"), wall_prior=o["budget_consumed"]["wall_s"],
                    code_file_sha256=o.get("code_file_sha256"), continuation=True,
                    priority_ts=o.get("priority_ts"))
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
        self.seg_wall_s, self.seg_t0 = None, 0.0
        self.threads = self.numba_threads = None
        self.envelope = None                  # R8 G1/G5 (F 1789564931110-0): the job's envelope, for EV.prepare_row

    # F9 checkpoints
    def _ckpt(self) -> pathlib.Path:
        return pathlib.Path(self.ckpt_dir) / self.lane / f"{self.job_key}.pkl"

    def should_pause(self) -> bool:
        """The epoch stop flag, or (F-R6-4) this checkpointable job's segment wall is used up."""
        if self.seg_wall_s is not None and time.perf_counter() - self.seg_t0 >= self.seg_wall_s:
            return True
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
        from primordial.fabric import envelope as EV
        # R8 G1 + G5 acc.3 (agreed with F): vocabulary refused LOUDLY at emit (RowRefused -> the job ends `error`),
        # and every row is stamped with predicate_id / predicate_event_id from its envelope
        row = EV.prepare_row(row, self.n_emitted, self.envelope)
        if self.threads is not None or self.numba_threads is not None:        # D19: every row says how it ran
            row = dict(row)
            row.setdefault("granted_threads", self.threads)
            row.setdefault("numba_threads", self.numba_threads)
        self.r.xadd(ROWS.format(self.lane), {"job_id": self.job_id, "json": json.dumps(row, sort_keys=True)})
        self.n_emitted += 1


_LOADED: dict = {}                  # F-R6-2 (child): module -> sha256 of its source when this child imported it


_CLOSURE: dict = {}                 # F-R7-3 (child): in-repo module -> (file, sha256 when this child first saw it)


def _snapshot_closure() -> None:
    pre = _closure_prefixes()
    for name, m in list(sys.modules.items()):
        if name in _CLOSURE or not name.startswith(pre):
            continue
        f = getattr(m, "__file__", None)
        if f and os.path.exists(f):
            _CLOSURE[name] = (f, _file_sha(f))


def _loaded_sha(mod: str) -> dict:
    """-> {sha: the fn module as loaded, stale: in-repo modules whose source changed since loaded, repo}."""
    if mod not in _LOADED:
        try:
            m = importlib.import_module(mod)
        except Exception:
            return {"sha": None, "stale": [], "repo": None, "error": traceback.format_exc()[-500:]}
        _LOADED[mod] = _file_sha(getattr(m, "__file__", None))
    _snapshot_closure()
    stale = sorted(n for n, (f, s) in _CLOSURE.items() if _file_sha(f) != s)
    return {"sha": _LOADED[mod], "stale": stale,
            "repo": _repo_root(getattr(sys.modules.get(mod), "__file__", None), mod)}


def _child_main(pipe, url: str, lane: str) -> None:
    ctx = Ctx(_redis(url), lane)
    while True:
        job = pipe.recv()
        if job is None:
            return
        _snapshot_closure()                                  # F-R7-3: modules a finished job imported lazily
        if "probe" in job:                                   # F-R6-2: which code would this child run?
            pipe.send(_loaded_sha(job["probe"]))
            continue
        ctx.job_id, ctx.n_emitted = job["job_id"], 0
        try:
            ctx.envelope = json.loads(job["envelope"]) if job.get("envelope") else None
        except ValueError:
            ctx.envelope = None
        ctx.seg_wall_s = float(job["segment_wall_s"]) if job.get("segment_wall_s") else None
        ctx.job_key, ctx.segment = job.get("job_key") or job["job_id"], int(job.get("segment", 0))
        ctx.ckpt_dir = job.get("ckpt_dir") or CKPT_DIR
        ctx.threads = int(job["threads"]) if job.get("threads") else None     # F-R5-5: the CPU token's grant
        ctx.numba_threads = apply_child_threads(ctx.threads)                  # D19: effective, stamped on rows
        t0 = ctx.seg_t0 = time.perf_counter()
        try:
            mod, _, name = job["fn"].partition(":")
            m = importlib.import_module(mod)
            _LOADED.setdefault(mod, _file_sha(getattr(m, "__file__", None)))
            getattr(m, name)(ctx, **json.loads(job["kwargs"]))
            ctx._ckpt().unlink(missing_ok=True)
            pipe.send({"ok": True, "wall_s": time.perf_counter() - t0, "emitted": ctx.n_emitted, "numba_threads": ctx.numba_threads})
        except JobPaused:
            pipe.send({"ok": True, "paused": True, "wall_s": time.perf_counter() - t0, "emitted": ctx.n_emitted, "numba_threads": ctx.numba_threads})
        except Exception:
            pipe.send({"ok": False, "wall_s": time.perf_counter() - t0, "emitted": ctx.n_emitted, "numba_threads": ctx.numba_threads,
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
        self.child_threads = None                 # D19: threads the current child was spawned with
        self.ckpt_dir = str(ckpt_dir or CKPT_DIR)
        self.exit_requested = False             # set from another thread: serve() returns after the current job
        self.rows_cursor = "$"
        self.group = f"worker-{lane}"
        for stream in (JOBS.format(lane), CONT.format(lane)):
            try:
                self.r.xgroup_create(stream, self.group, id="0", mkstream=True)
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    raise

    def _spawn(self, threads: int | None = None) -> None:
        """D19: the child's thread pools are sized at import from the environment it is spawned with, so a granted
        token's threads go into the CHILD environment (the session's NUMBA_NUM_THREADS=3 capped every job)."""
        c = mp.get_context("spawn")
        self.pipe, child_end = c.Pipe()
        self.child = c.Process(target=_child_main, args=(child_end, self.url, self.lane), daemon=True)
        with _SPAWN_LOCK:                          # os.environ is process-wide; restore it for the parent
            saved = {k: os.environ.get(k) for k in THREAD_ENV}
            if threads:
                os.environ.update(thread_env(threads))
            try:
                self.child.start()
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v
        self.child_threads = threads
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
        """Rows of job_id into its RowWriter. D29 (R8 G1): a row the writer refuses is kept as an `aborted` wrapper
        row (residue) AND recorded in self.row_refusals, which turns the job's status to `error` -- never `ok`."""
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
                    self.row_refusals.append(f"row {n}: {e}"[:300])
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

    def _probe(self, fn: str) -> dict:
        self.pipe.send({"probe": fn.partition(":")[0]})
        if not self.pipe.poll(120):
            return {"sha": None, "error": "probe timeout"}
        return self.pipe.recv()

    def _refuse(self, job: dict, verdict: dict, stub: bool = True) -> dict:
        from primordial.fabric import envelope as EV
        env = self._envelope(job)
        ev = EV.refuse(self.r, self.lane, job, verdict, env, stub=stub)
        env = env if isinstance(env, dict) else {}
        key = job.get("job_key") or job["job_id"]
        raw = self.r.hget(RESUMABLE, key)
        if raw and json.loads(raw).get("queued_job_id") == job["job_id"]:   # its queued segment was refused:
            self.r.hset(RESUMABLE, key, json.dumps(dict(json.loads(raw), queued_job_id=None,   # resumable again
                                                        refused=verdict["reasons"]), sort_keys=True))
        out = {"job_id": job["job_id"], "status": "refused", "event": ev["event"], "reasons": verdict["reasons"],
               "rows": 0, "cpu_s": 0.0, "wall_s": 0.0, "job_key": job.get("job_key") or job["job_id"],
               "segment": int(job.get("segment", 0) or 0), "ended": round(time.time(), 3),
               **{k: env.get(k) for k in DONE_ENV_FIELDS}, "predicate_event_id": env.get("predicate_event_id"),
               **queue_of(job)}
        self.r.xadd(DONE.format(self.lane), {"json": json.dumps(out, sort_keys=True)})
        self.log(f"job {job['job_id']} {job.get('fn')} -> refused {ev['event']} {verdict['reasons']}")
        return out

    def _event(self, name: str, rec: dict) -> None:
        from primordial.fabric import envelope as EV
        self.r.xadd(EV.EVENTS, {"event": name, "json": json.dumps(dict(rec, event=name, lane=self.lane),
                                                                  sort_keys=True)})

    def run_job(self, job: dict) -> dict:
        granted = int(job["threads"]) if job.get("threads") else None
        if self.child is not None and self.child.is_alive() and granted and self.child_threads != granted:
            self._kill_child()                               # D19: pools are fixed at spawn; respawn at the grant
        if self.child is None or not self.child.is_alive():
            self._spawn(granted)
        want, want_repo = job.get("code_file_sha256"), job.get("code_repo")
        if want or want_repo:                                # F-R6-2 (D4) + F-R7-3: never run stale resident code
            got = self._probe(job["fn"])
            if want_repo and not got.get("error") and _norm_path(got.get("repo")) != _norm_path(want_repo):
                # D14 guard: this child imports the code from another repo; a respawn cannot change sys.path
                return self._refuse(job, {"ok": False, "event": "CODE_REPO_MISMATCH", "reasons": ["CODE_REPO_MISMATCH"],
                                          "stage": None, "ceiling": None, "loaded": got.get("repo"),
                                          "want": want_repo}, stub=False)

            def stale(g):
                return (want and g.get("sha") != want) or bool(g.get("stale"))
            if stale(got):
                changed = list(got.get("stale") or [])
                mod = job["fn"].partition(":")[0]
                if want and got.get("sha") != want and mod not in changed:
                    changed.append(mod)
                self._kill_child()
                self._spawn(granted)
                self._event("CODE_RELOADED", {"job_id": job["job_id"], "job_key": job.get("job_key"),
                                              "fn": job["fn"], "loaded": got.get("sha"), "want": want,
                                              "changed": changed})
                got = self._probe(job["fn"])
                if stale(got):
                    return self._refuse(job, {"ok": False, "event": "CODE_FINGERPRINT_MISMATCH",
                                              "reasons": ["CODE_FINGERPRINT_MISMATCH"], "stage": None,
                                              "ceiling": None, "loaded": got.get("sha"), "want": want,
                                              "error": got.get("error")}, stub=False)
        env = self._envelope(job)
        env = env if isinstance(env, dict) else {}
        ttl = float(job["ttl_cpu_s"])
        if env.get("cpu_budget_s") is not None:              # F-R5-1: the envelope caps the task TTL
            ttl = min(ttl, float(env["cpu_budget_s"]))
        # F-R6-4: wall_budget_s is the SEGMENT wall. A checkpointable job is told to pause at it (and killed only
        # SEGMENT_GRACE_S later); any other job is killed at it. CPU stays cumulative (cpu_prior).
        wall_limit = float(env["wall_budget_s"]) if env.get("wall_budget_s") is not None else None
        checkpointable = env.get("checkpointable") is True
        kill_at = None if wall_limit is None else wall_limit + (SEGMENT_GRACE_S if checkpointable else 0.0)
        wall_prior = float(job.get("wall_prior", 0) or 0)
        cpu_prior = float(job.get("cpu_prior", 0) or 0)
        job = dict(job, ckpt_dir=self.ckpt_dir,
                   segment_wall_s=str(wall_limit) if (checkpointable and wall_limit is not None) else "")
        rows_path = pathlib.Path(job["rows"])
        if not rows_path.is_absolute():
            rows_path = self.repo / rows_path
        # the rows cursor starts at the stream's current end, so only this job's rows are read
        last = self.r.xrevrange(ROWS.format(self.lane), count=1)
        self.rows_cursor = last[0][0] if last else "0"
        w = RowWriter(rows_path, job["exp_id"], commit_every_s=60, repo=self.repo)
        self.row_refusals = []
        cpu0 = self._child_cpu()
        t0, started = time.perf_counter(), time.time()
        self.pipe.send(job)
        result, status = None, "ok"
        n = 0
        beat = time.monotonic()
        samples, sample_at = [], (time.monotonic() if TM.sampling_on() else None)
        while result is None:
            if sample_at is not None and time.monotonic() >= sample_at:   # G5: RSS/CPU%/threads every 30 s
                s = TM.sample_process(self.child.pid)
                if s is not None:
                    samples.append(s)
                sample_at = time.monotonic() + TM.SAMPLE_EVERY_S
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
            if kill_at is not None and time.perf_counter() - t0 > kill_at:
                cpu = self._child_cpu() - cpu0
                self._kill_child()
                status, result = "timeout", {"ok": False, "cpu_s": cpu, "limit": "wall"}
                break
        n += self._drain(job["job_id"], w)
        if self.row_refusals and status in ("ok", "paused"):     # D29: refused rows never report ok
            status = "error"
            result = dict(result, ok=False, error=f"ROWS_REFUSED ({len(self.row_refusals)}): "
                                                  + "; ".join(self.row_refusals[:5]))
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
               "cpu_token": json.loads(job["cpu_token"]) if job.get("cpu_token") else None,
               "granted_threads": granted, "numba_threads": result.get("numba_threads"),
               "predicate_event_id": env.get("predicate_event_id"), "resource_samples": samples,
               "row_refusals": len(self.row_refusals),
               "telemetry_sampling": sample_at is not None, **queue_of(job)}
        if status == "paused" and self.auto_requeue:
            out["next_job_id"] = submit(self.lane, job["fn"], job["exp_id"], job["rows"], float(job["ttl_cpu_s"]),
                                        json.loads(job["kwargs"]), r=self.r, job_key=out["job_key"],
                                        segment=out["segment"] + 1, cpu_prior=cpu_prior + (cpu_s or 0),
                                        envelope=env or None, wall_prior=wall_prior + wall_s,
                                        code_file_sha256=job.get("code_file_sha256"), continuation=True,
                                        priority_ts=_f(job.get("priority_ts") or job.get("ts")))
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
               "queued_job_id": out.get("next_job_id"), "ts": round(time.time(), 3),
               "priority_ts": _f(job.get("priority_ts") or job.get("ts"))}
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
        if getattr(self, "_reg_key", None):                  # F-R7-1: the registration lives as long as the heartbeat
            self.r.expire(self._reg_key, REG_TTL)

    def _register(self) -> None:
        """F-R7-1 (D14): register this process (os.getpid() is the real interpreter, not a venv launcher) so the
        round close can stop exactly it and the residue scan can see its repo and round."""
        import psutil
        pid = os.getpid()
        self._reg_key = REG.format(self.lane, pid)
        try:
            cmdline = psutil.Process(pid).cmdline()
        except Exception:
            cmdline = list(sys.argv)
        self.r.hset(self._reg_key, mapping={
            "pid": pid, "lane": self.lane, "repo": str(self.repo.resolve()).replace("\\", "/"),
            "round_id": self.r.get("pm:round:current") or "", "cmdline": json.dumps(cmdline),
            "host": os.environ.get("COMPUTERNAME", ""), "started_ts": f"{time.time():.3f}",
            "tag": os.environ.get("PM_TAG", "")})
        self.r.expire(self._reg_key, REG_TTL)

    def _stream_head(self, stream: str) -> tuple | None:
        """G3: the next undelivered entry of `stream` for this lane's group -> (entry_id, fields) or None."""
        last = "0-0"
        for g in self.r.xinfo_groups(stream):
            if g.get("name") == self.group:
                last = g.get("last-delivered-id") or "0-0"
        got = self.r.xrange(stream, min="(" + last, max="+", count=1)
        return got[0] if got else None

    def peek(self, consumer: str) -> dict | None:
        """G3: the job this worker should take next -> {stream, priority_ts, job_id} or None. Continuations and fresh
        jobs compete on priority_ts (original queue entry); a tie goes to the continuation. Shadow specs at the
        head of pm:jobs:<L> are consumed and acked here (they exist only for job_id lookups)."""
        main, cont = JOBS.format(self.lane), CONT.format(self.lane)
        heads = []
        for stream in (cont, main):
            for _ in range(1000):
                h = self._stream_head(stream)
                if h is None or not h[1].get("shadow"):
                    break
                got = self.r.xreadgroup(self.group, consumer, {stream: ">"}, count=1)
                for _, ms in got or []:
                    for mid, _f_ in ms:
                        self.r.xack(stream, self.group, mid)
            if h is not None and not h[1].get("shadow"):
                pts = _f(h[1].get("priority_ts") or h[1].get("ts")) or 0.0
                heads.append((pts, 0 if stream == cont else 1, stream, h[1].get("job_id")))
        if not heads:
            return None
        pts, _, stream, job_id = min(heads)
        return {"stream": stream, "priority_ts": pts, "job_id": job_id}

    def depth(self) -> dict:
        """G5: undelivered queue depth of this lane (fresh + continuation; shadows not counted)."""
        out = {}
        for name, stream in (("depth_main", JOBS.format(self.lane)), ("depth_cont", CONT.format(self.lane))):
            last = "0-0"
            for g in self.r.xinfo_groups(stream):
                if g.get("name") == self.group:
                    last = g.get("last-delivered-id") or "0-0"
            out[name] = sum(1 for _, f in self.r.xrange(stream, min="(" + last, max="+") if not f.get("shadow"))
        return out

    def _beacon(self, kind: str, **extra) -> None:
        self._beacon_seq = getattr(self, "_beacon_seq", -1) + 1
        info = dict(self._beacon_info, seq=self._beacon_seq, **extra)
        try:
            TM.beacon(self.r, self.lane, kind, info)
        except Exception as e:                                     # telemetry never kills the worker
            self.log(f"beacon {kind} failed: {e}")

    def serve(self, max_jobs: int | None = None, block_ms: int = 5000, idle_exit_s: float | None = None,
              deadline_s: float | None = None) -> list:
        consumer = os.environ.get("PM_TAG", "worker")
        self._register()
        waiter = f"{self.lane}:{consumer}:{os.getpid()}:{id(self)}"
        self._beacon_info = {"watcher": "worker", "tag": consumer, "pid": os.getpid(),
                             "repo": str(self.repo.resolve()).replace("\\", "/"),
                             "round_id": self.r.get("pm:round:current") or "", "started_ts": round(time.time(), 3)}
        self._beacon_seq = -1                                     # seq restarts per watcher instance (START = 0)
        self._beacon("START", beat_interval_s=TM.BEAT_EVERY_S)
        beat_at = time.monotonic() + TM.BEAT_EVERY_S
        depth_at = time.monotonic()
        stop_reason = "exception"
        done, idle0 = [], time.monotonic()
        end = None if deadline_s is None else time.monotonic() + deadline_s
        poll = min(block_ms / 1000, 0.1)
        try:
            while ((max_jobs is None or len(done) < max_jobs) and (end is None or time.monotonic() < end)
                   and not self.exit_requested):
                if time.monotonic() >= beat_at:
                    self._beacon("BEAT")
                    beat_at = time.monotonic() + TM.BEAT_EVERY_S
                if time.monotonic() >= depth_at:
                    try:
                        TM.depth_sample(self.r, self.lane, self.depth())
                    except Exception as e:
                        self.log(f"depth sample failed: {e}")
                    depth_at = time.monotonic() + TM.DEPTH_EVERY_S
                if self.r.exists(STOP.format(self.lane)) or self.r.exists(PUSH_LOCK.format(self.lane)):
                    broker.leave(self.r, waiter)
                    self._state("stopped")
                    time.sleep(poll)
                    idle0 = time.monotonic()
                    continue
                # non-consuming XREADGROUP at id 0: keeps this consumer visible (and its idle time fresh) in the group
                # while it peeks instead of blocking on ">" -- the residue scan finds live and foreign workers by it
                self.r.xreadgroup(self.group, consumer, {JOBS.format(self.lane): "0"}, count=1)
                head = self.peek(consumer)
                if head is None:
                    broker.leave(self.r, waiter)
                    self._state("idle")
                    if idle_exit_s is not None and time.monotonic() - idle0 > idle_exit_s:
                        stop_reason = "idle_exit"
                        break
                    time.sleep(poll)
                    continue
                tok = None
                if self._brokered():                           # F-R5-5 + G3: FIFO by the head job's priority_ts
                    tok = broker.acquire(self.r, self.lane, ttl_s=60, waiter=waiter, priority_ts=head["priority_ts"])
                    if tok is None:
                        self._state("waiting_cpu")
                        time.sleep(min(poll, 0.05))
                        continue
                self._state("idle")
                stream = head["stream"]
                got = self.r.xreadgroup(self.group, consumer, {stream: ">"}, count=1)
                msgs = [m for _, ms in (got or []) for m in ms]
                if not msgs:
                    broker.release(self.r, tok)
                    continue
                mid, job = msgs[0]
                if job.get("shadow"):                          # raced past peek: a lookup copy, never run
                    broker.release(self.r, tok)
                    self.r.xack(stream, self.group, mid)
                    continue
                qf = TM.queue_fields(_f(job.get("queue_enter_ts") or job.get("ts")) or time.time(), time.time(),
                                     tok.get("_queue_position") if tok else self._lane_position(job),
                                     is_continuation(job))
                job = dict(job, queue=json.dumps(qf, sort_keys=True))
                try:
                    TM.grant(self.r, self.lane, job, qf, self.depth())
                except Exception as e:
                    self.log(f"grant record failed: {e}")
                verdict = self._admit(job)
                if verdict is not None and not verdict["ok"]:
                    broker.release(self.r, tok)
                    done.append(self._refuse(job, verdict, stub=verdict.get("stub", True)))   # R7: no stub for sample refusals
                    self.r.xack(stream, self.group, mid)
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
                self.r.xack(stream, self.group, mid)
                idle0 = time.monotonic()
            else:
                stop_reason = ("exit_requested" if self.exit_requested else
                               "max_jobs" if (max_jobs is not None and len(done) >= max_jobs) else "deadline")
        finally:
            broker.leave(self.r, waiter)
            self._beacon("STOP", stop_reason=stop_reason, jobs=len(done))
            self.stop()
        return done

    def _lane_position(self, job: dict) -> int:
        """Unbrokered queue_position: undelivered jobs of this lane with an earlier priority_ts than this one."""
        pts = _f(job.get("priority_ts") or job.get("ts")) or 0.0
        n = 0
        for stream in (JOBS.format(self.lane), CONT.format(self.lane)):
            last = "0-0"
            for g in self.r.xinfo_groups(stream):
                if g.get("name") == self.group:
                    last = g.get("last-delivered-id") or "0-0"
            n += sum(1 for _, f in self.r.xrange(stream, min="(" + last, max="+")
                     if not f.get("shadow") and (_f(f.get("priority_ts") or f.get("ts")) or 0.0) < pts)
        return n

    def stop(self) -> None:
        self.r.delete(WSTATE.format(self.lane))
        if getattr(self, "_reg_key", None):
            self.r.delete(self._reg_key)
            self._reg_key = None
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
