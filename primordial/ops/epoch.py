"""F14 (round 3): the epoch controller. 30-minute generations with clean boundaries.

At T + n x epoch_s the controller:
  1. posts `EPOCH n` on the bus (to ALL);
  2. sets pm:jobs:<L>:stop for every lane: F7 workers stop taking jobs (a job
     already running finishes; its rows commit as usual);
  3. waits until every live worker reports `stopped` (pm:worker:<L>, refreshed
     by the worker; a lane with no live worker is not waited for), or
     drain_timeout_s, recording stragglers;
  4. exports the bus (ops/bus_export) into <out>/epoch_<n>/; G7 (round 8): only rows after each stream's cursor,
     every pm:jobs:<L>:done and telemetry stream included, cursor + partition in <out>/export_cursor.json
     (committed with the epoch); at close a last delta (<out>/close/), one full dump per stream
     (<out>/close_full/) and a byte-identity check of full vs concatenated deltas, recorded in ROUND_<id>.json;
  4b. (bootpack=True, F15) writes one boot pack per lane into
     <out>/epoch_<n>/bootpack/<L>.md;
  5. writes the conductor record <out>/EPOCH_<n>.json and commits the
     directory (commit_path: that path only, PM_TAG required);
  6. clears the stop flags and marks epoch n+1 running (pm:epoch:state).
Every step is an event in self.events and in an event log OUTSIDE the repo (F-R6-1, defect D3: the log was
appended after each commit, so ops.push refused on a dirty tree 5/5 in round 5). Default
$PM_EPOCH_LOGDIR (or pm-data/epoch-logs)/epochs-<hash of out>/epoch_log.jsonl; log_dir overrides. Just
before every commit the log is copied verbatim to <out>/epoch_log.jsonl, so a commit carries every event
up to it and the next commit carries the tail. Nothing is written in the repo after a commit.

F-R5-6 (defect F8): drain_timeout_s=None sizes the drain to the jobs actually running: for every live
worker reporting `busy` with a job_id, that job's remaining wall bound (envelope wall_budget_s -
wall_prior; no envelope -> the PILOT cpu wall ceiling), max over workers, + DRAIN_MARGIN_S. No busy
worker -> DRAIN_MARGIN_S. The value is recorded in the `drained` event and the EPOCH record.

F-R5-6 (defect F7): the controller runs from its OWN worktree (e.g. F:/Prometheus-worktrees/nestor-epoch
on the integration branch), created by the conductor, never by a lane. The CLI requires --repo (or
PM_EPOCH_REPO) and refuses (exit 2, no Redis writes) a missing repo, the worktree holding this code
(a lane or conductor worktree) or a non-git directory. Records go to <repo>/roles/Nestor/sidequests/
graphworld/epochs and are committed there; with push=True (the CLI) each commit is pushed by
`python -m primordial.ops.push` run with cwd=repo. A failed push is an event `push_failed`; the clock
never waits on it.

    python -m primordial.ops.epoch run --lanes B,C,D,E [--epoch-min 30] [--epochs N]
    python -m primordial.ops.epoch boundary N --lanes B,C,D,E      # one boundary now
    python -m primordial.ops.epoch lint --sequence FILE [--beacons] # G4 close/watch protocol lint (rc 1 = FAIL)

G4 (round 8, D31) CLOSE/WATCH PROTOCOL. D31 was the conductor's: A's close note told lanes to stop their watchers, a
lane complied, its gpuq arbiter exited ~1 min after a ruling said to keep it -- 683 s deaf. The protocol:
  * a lane's ASK WATCH stays alive until DRAIN and stops only AFTER that lane's workers and after every SHARED
    service stop (a lane must be able to hear a "keep it" ruling until the last thing it could affect is down);
  * a SHARED service (SHARED_SERVICES, e.g. the gpuq arbiter) is stopped only with a current conductor
    confirmation record pm:close:confirm:<service> (hash: by, ts, ref) written before the stop;
  * watchers emit start/stop BEACONS (emitted by P in fabric/worker.py; field names agreed on the bus) to
    BEACONS; this module owns only the LINT over them.
protocol_lint() checks a written close SEQUENCE (json steps or a numbered prose note, parse_close_text) before it
is sent; beacon_lint() checks what actually happened; close_sweep() flags unconfirmed shared stops at close.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

from primordial.fabric.rows import commit_path
from primordial.fabric.worker import DONE, JOBS, STOP, WSTATE

ROOT = pathlib.Path(__file__).resolve().parents[2]
EPOCHS_REL = pathlib.Path("roles") / "Nestor" / "sidequests" / "graphworld" / "epochs"
DEFAULT_OUT = ROOT / EPOCHS_REL
STATE = "pm:epoch:state"
DRAIN_MARGIN_S = 30.0
DEFAULT_LOGDIR = "C:/Users/jcrai/lab/pm-data/epoch-logs"


def controller_repo(repo) -> tuple[bool, str]:
    """F-R5-6 (F7): -> (ok, reason). The controller's repo must be its own git worktree, not this code's."""
    if not repo:
        return False, "no controller repo: pass --repo or set PM_EPOCH_REPO (its own worktree, not a lane's)"
    p = pathlib.Path(repo)
    if not p.is_dir():
        return False, f"controller repo {p} is not a directory"
    if p.resolve() == ROOT.resolve():
        return False, f"controller repo {p} is the worktree holding this code ({ROOT}); use a dedicated worktree"
    q = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if q.returncode != 0:
        return False, f"controller repo {p} is not a git work tree"
    if pathlib.Path(q.stdout.strip()).resolve() == ROOT.resolve():
        return False, f"controller repo {p} is inside the worktree holding this code ({ROOT})"
    return True, ""
NO_NEW_WORK = "pm:round:{}:no_new_work"     # informational flag; workers refuse from the clock timestamps


class EpochController:
    def __init__(self, lanes, epoch_s: float = 1800, r=None, out=DEFAULT_OUT, repo=None, export=None,
                 drain_timeout_s: float | None = None, post: bool = True, log=print, bootpack: bool = False,
                 bootpack_kw: dict | None = None, push: bool = False, log_dir=None, push_branch: str | None = None):
        from primordial.bus import bus
        from primordial.ops import bus_export
        self.lanes = list(lanes)
        self.epoch_s = float(epoch_s)
        self.r = r or bus.conn()
        self.out = pathlib.Path(out)
        # F-R6-1 (D3): events live OUTSIDE the publish repo; each commit carries a verbatim copy up to it
        key = hashlib.sha1(str(self.out.resolve()).encode()).hexdigest()[:12]
        base = pathlib.Path(log_dir) if log_dir else pathlib.Path(os.environ.get("PM_EPOCH_LOGDIR", DEFAULT_LOGDIR)) / f"epochs-{key}"
        self.log_path = base / "epoch_log.jsonl"
        self.push_branch = push_branch
        self.repo = repo
        self.export = export or bus_export.export
        self.cursor_path = self.out / bus_export.CURSOR_NAME     # G7: committed with every epoch
        self.drain_timeout_s = drain_timeout_s
        self.post, self.log = post, log
        self.events: list[dict] = []
        self.bootpack, self.bootpack_kw = bootpack, dict(bootpack_kw or {})
        self.push = push

    def _job_wall_bound(self, lane: str, job_id: str) -> float:
        from primordial.fabric import envelope as EV
        fallback = float(EV.CEILINGS["PILOT"]["cpu_wall_s"])
        for _, f in self.r.xrange(JOBS.format(lane)):
            if f.get("job_id") != job_id:
                continue
            try:
                env = json.loads(f.get("envelope") or "null")
            except ValueError:
                env = None
            if isinstance(env, dict) and isinstance(env.get("wall_budget_s"), (int, float)):
                return max(0.0, float(env["wall_budget_s"]) - float(f.get("wall_prior") or 0))
            return fallback
        return fallback

    def drain_timeout(self) -> float:
        """F-R5-6 (F8): the drain window for this boundary (explicit value, else sized to running jobs)."""
        if self.drain_timeout_s is not None:
            return float(self.drain_timeout_s)
        bounds = [self._job_wall_bound(L, s["job_id"]) for L, s in self._live_workers().items()
                  if s.get("state") == "busy" and s.get("job_id")]
        return (max(bounds) if bounds else 0.0) + DRAIN_MARGIN_S

    def _publish_log(self) -> None:
        """F-R6-1: copy the outside event log into <out>/epoch_log.jsonl just before a commit (never after)."""
        self.out.mkdir(parents=True, exist_ok=True)
        data = self.log_path.read_bytes() if self.log_path.exists() else b""
        (self.out / "epoch_log.jsonl").write_bytes(data)

    def _push(self) -> None:
        if not self.push:
            return
        # this code's push (ROOT), targeting the controller repo; PM_LANE cleared: the controller is no lane's
        # worker, so push never takes a lane push lock on the live bus
        cmd = [sys.executable, "-m", "primordial.ops.push", "--repo", str(self.repo or ROOT)]
        env = dict(os.environ, PYTHONPATH=str(ROOT), PM_LANE="")
        if self.push_branch:
            cmd += ["--branch", self.push_branch]
            env["PM_INTEGRATION_BRANCH"] = self.push_branch
        try:
            q = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=600)
            if q.returncode != 0:
                self._event("push_failed", rc=q.returncode, tail=(q.stdout + q.stderr)[-500:])
            else:
                self._event("pushed")
        except Exception as e:                              # never block the clock on a push
            self._event("push_failed", error=f"{type(e).__name__}: {e}"[:500])

    def _event(self, name: str, **kw) -> dict:
        e = {"ts": round(time.time(), 3), "event": name, **kw}
        self.events.append(e)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(e, sort_keys=True) + "\n")
        self.log(f"[epoch] {name} {json.dumps(kw, sort_keys=True)}")
        return e

    def _cursored(self) -> bool:
        from primordial.ops import bus_export
        return self.export is bus_export.export

    def _export(self, out, stamp: str) -> dict:
        """G7: the real exporter runs with the committed cursor (deltas only); an injected one keeps its signature."""
        if self._cursored():
            return self.export(out=out, stamp=stamp, r=self.r, cursor_path=self.cursor_path, lanes=self.lanes)
        return self.export(out=out, stamp=stamp, r=self.r)

    def close_export(self) -> dict | None:
        """G7 close: last delta, one full dump per stream, and full == concatenated deltas byte for byte."""
        if not self._cursored():
            return None
        from primordial.ops import bus_export
        last = self._export(self.out / "close", "close")
        keys = sorted({s for part in bus_export.load_cursor(self.cursor_path)["partitions"] for s in part["streams"]})
        bus_export.full_dump(self.out / "close_full", r=self.r, stream_keys=keys)
        v = bus_export.verify_full(self.out, self.out / "close_full", self.cursor_path)
        self._event("export_full", ok=v["ok"], mismatched=v["mismatched"], close_rows={k: c[1] for k, c in last.items()})
        return v

    def _live_workers(self) -> dict:
        return {L: self.r.hgetall(WSTATE.format(L)) for L in self.lanes if self.r.exists(WSTATE.format(L))}

    def _budget(self) -> dict:
        """Budget use so far, by cohort (envelope) and by lane, from the done records (F13 identity)."""
        by_cohort, by_lane = {}, {}
        for L in self.lanes:
            for _, f in self.r.xrange(DONE.format(L)):
                d = json.loads(f["json"])
                c = d.get("cpu_s") or 0.0
                key = d.get("cohort") or f"lane:{L}"
                agg = by_cohort.setdefault(key, {"cpu_s": 0.0, "jobs": 0, "status": {}})
                agg["cpu_s"] = round(agg["cpu_s"] + float(c), 3)
                agg["jobs"] += 1
                agg["status"][d.get("status")] = agg["status"].get(d.get("status"), 0) + 1
                by_lane[L] = round(by_lane.get(L, 0.0) + float(c), 3)
        return {"by_cohort": by_cohort, "by_lane": by_lane}

    def _wait_until(self, ts: float) -> None:
        while (wait := ts - time.time()) > 0:
            time.sleep(min(wait, 1.0))

    def run_round(self, clock: dict) -> dict:
        """F-R5-2: run a round from its clock alone (ops.round_clock). No session announces a boundary.
        epochs 1..E-1: boundary + resume. no_new_work_ts: flag + event (workers refuse by the clock; a job
        already running finishes). drain_ts: boundary E without resume (stop flags stay: checkpointable jobs
        pause). end_ts: closed record committed."""
        rid = clock["round_id"]
        self._event("round_start", round_id=rid, clock=clock)
        self.r.hset(STATE, mapping={"n": 1, "phase": "running", "ts": round(time.time(), 3), "round_id": rid})
        out = []
        for n in range(1, int(clock["epochs"])):
            self._wait_until(clock["start_ts"] + n * clock["epoch_s"])
            out.append(self.boundary(n))
        self._wait_until(clock["no_new_work_ts"])
        self.r.set(NO_NEW_WORK.format(rid), f"{time.time():.3f}")
        self.r.hset(STATE, mapping={"phase": "no_new_work", "ts": round(time.time(), 3)})
        self._event("no_new_work", round_id=rid)
        if self.post:
            from primordial.bus import bus
            bus.post("note", f"ROUND {rid} NO_NEW_WORK", "controller: workers refuse new jobs by the clock",
                     to="ALL", r=self.r)
        self._wait_until(clock["drain_ts"])
        out.append(self.boundary(int(clock["epochs"]), resume=False, max_drain_s=clock["end_ts"] - time.time()))
        self._wait_until(clock["end_ts"])
        full = self.close_export()
        # G4: unconfirmed shared stops / deaf watchers up to end_ts, committed in the close record (the event tail
        # round_closed .. current_unset is a pinned contract, so the sweep runs before it)
        sweep = close_sweep(self.r)
        self._event("close_sweep", ok=sweep["ok"], checks_run=sweep["checks_run"], violations=sweep["violations"])
        rec = {"round_id": rid, "clock": clock, "closed_ts": round(time.time(), 3), "epochs": out,
               "budget": self._budget(), "export_full": full, "close_sweep": sweep}
        (self.out / f"ROUND_{rid}.json").write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n",
                                                   encoding="utf-8")
        self.r.hset(STATE, mapping={"phase": "closed", "ts": rec["closed_ts"]})
        self._event("round_closed", round_id=rid)
        self._publish_log()
        rec["sha"] = commit_path(self.out, f"ROUND-{rid}", "(round close record)", repo=self.repo)
        self._event("round_committed", sha=rec["sha"])
        self._push()
        # F-R7-1 (D12 + D14): stop exactly the registered worker processes, THEN clear the stop flags, so no
        # worker of this round can wake into the next one. Events go to the outside log only (F-R6-1).
        from primordial.ops import residue
        actions = residue.stop_registered(self.r, round_id=rid, lanes=self.lanes)
        self._event("workers_stopped", actions=actions)
        for L in self.lanes:
            self.r.delete(STOP.format(L))
        self._event("flags_cleared", lanes=self.lanes)
        # D18: a closed round must not stay current (admission refused every build-phase job NO_NEW_WORK). Only
        # if the pointer still names THIS round; the pm:round:<rid> hash stays as history. Outside-log event only.
        from primordial.ops import round_clock as RC
        if self.r.get(RC.CURRENT) == rid:
            self.r.delete(RC.CURRENT)
            self._event("current_unset", round_id=rid)
        rec["workers_stopped"] = actions
        return rec

    def boundary(self, n: int, resume: bool = True, max_drain_s: float | None = None) -> dict:
        """max_drain_s caps the sized drain (run_round passes the time left to end_ts: the close never slips)."""
        from primordial.bus import bus
        begin = self._event("epoch_post", n=n)
        if self.post:
            bus.post("note", f"EPOCH {n} boundary", f"controller: stop taking jobs; export + commit; lanes {self.lanes}",
                     to="ALL", r=self.r)
        self.r.hset(STATE, mapping={"n": n, "phase": "draining", "ts": begin["ts"]})
        for L in self.lanes:
            self.r.set(STOP.format(L), n)
        self._event("stop_set", lanes=self.lanes)
        drain_s = self.drain_timeout()
        if max_drain_s is not None:
            drain_s = max(0.0, min(drain_s, float(max_drain_s)))
        deadline = time.monotonic() + drain_s
        while True:
            live = self._live_workers()
            waiting = sorted(L for L, s in live.items() if s.get("state") != "stopped")
            if not waiting or time.monotonic() >= deadline:
                break
            time.sleep(0.05)
        drained = self._event("drained", workers=sorted(live), stragglers=waiting, drain_timeout_s=drain_s)
        epoch_dir = self.out / f"epoch_{n}"
        counts = self._export(epoch_dir, f"e{n}")
        self._event("exported", counts={k: v[1] for k, v in counts.items()})
        if self.bootpack:
            from primordial.ops import bootpack
            packs = bootpack.write_all(n, self.lanes, epoch_dir / "bootpack", r=self.r, **self.bootpack_kw)
            self._event("bootpacks", files=[p.name for p in packs])
        record = {"epoch": n, "lanes": self.lanes, "begin_ts": begin["ts"], "drained_ts": drained["ts"],
                  "workers": {L: s for L, s in live.items()}, "stragglers": waiting, "drain_timeout_s": drain_s,
                  "export": {k: v[1] for k, v in counts.items()}, "budget": self._budget(),
                  "controller": f"{os.environ.get('PM_LANE', '?')}[{os.environ.get('PM_TAG', '?')}]"}
        (self.out / f"EPOCH_{n}.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        self._publish_log()
        sha = commit_path(self.out, f"EPOCH-{n}", "(epoch record + bus export)", repo=self.repo)
        self._event("committed", sha=sha)
        self._push()
        if not resume:
            self.r.hset(STATE, mapping={"n": n, "phase": "draining", "ts": round(time.time(), 3)})
            self._event("drain_hold", n=n)
            return dict(record, sha=sha)
        for L in self.lanes:
            self.r.delete(STOP.format(L))
        self.r.hset(STATE, mapping={"n": n + 1, "phase": "running", "ts": round(time.time(), 3)})
        self._event("resumed", next_epoch=n + 1)
        return dict(record, sha=sha)

    def run(self, epochs: int | None = None, start: float | None = None) -> list[dict]:
        start = time.time() if start is None else start
        self.r.hset(STATE, mapping={"n": 1, "phase": "running", "ts": round(start, 3)})
        self._event("start", epoch_s=self.epoch_s, lanes=self.lanes)
        out, n = [], 1
        while epochs is None or n <= epochs:
            wait = start + n * self.epoch_s - time.time()
            if wait > 0:
                time.sleep(wait)
            out.append(self.boundary(n))
            n += 1
        return out


# ---------------------------------------------------------------- G4: close/watch protocol lint (D31)

BEACONS = "pm:telemetry:watch"               # XADD by P (worker.py), field json = WATCH_BEACON record (P 1789564787642-0)
WATCH_START, WATCH_STOP = "WATCH_START", "WATCH_STOP"
ASK_WATCH, WORKER = "ask_watch", "worker"
SHARED_SERVICES = ("gpuq",)                  # stopping one needs a conductor confirmation record
CONFIRM = "pm:close:confirm:{}"             # hash {by, ts, ref}; written by the conductor BEFORE the stop
CONFIRM_MAX_AGE_S = 3600.0                   # "current": no older than this at the stop
# The controller's own close order (run_round): drain boundary -> close record -> stop registered workers -> clear
# flags. It stops no watcher and no shared service; the suite lints it so a reorder cannot slip in unseen.
CONTROLLER_CLOSE_SEQUENCE = [{"action": "drain"}, {"action": "stop", "target": "worker", "lane": "*"}]


def _norm_step(st) -> dict:
    st = dict(st)
    st["action"] = str(st.get("action", "")).lower()
    st["target"] = str(st.get("target", "")).lower()
    st["lane"] = st.get("lane") or "*"
    return st


def _same_lane(a, b) -> bool:
    return a == "*" or b == "*" or a == b


def protocol_lint(sequence, shared=SHARED_SERVICES) -> dict:
    """-> {ok, checks_run, violations}. Steps, in execution order: {"action": "drain"} | {"action": "confirm",
    "target": <service>} | {"action": "stop", "target": ask_watch | worker | <service>, "lane": L or "*"}.
    FAIL on an ask-watch stop before DRAIN, before (or without) its lane's worker stop, or before any shared-service
    stop; and on a shared-service stop with no preceding confirm step."""
    steps = [_norm_step(x) for x in sequence]
    shared = {x.lower() for x in shared}
    violations, checks = [], 0
    drain_at = next((i for i, x in enumerate(steps) if x["action"] == "drain"), None)
    for i, st in enumerate(steps):
        if st["action"] != "stop":
            continue
        if st["target"] in shared:
            checks += 1
            if not any(x["action"] == "confirm" and x["target"] == st["target"] for x in steps[:i]):
                violations.append({"step": i, "kind": "SHARED_STOP_UNCONFIRMED", "service": st["target"]})
        if st["target"] != ASK_WATCH:
            continue
        L = st["lane"]
        checks += 1
        if drain_at is None or drain_at > i:
            violations.append({"step": i, "kind": "ASK_WATCH_STOP_BEFORE_DRAIN", "lane": L})
        checks += 1
        workers = [j for j, x in enumerate(steps) if x["action"] == "stop" and x["target"] == WORKER
                   and _same_lane(x["lane"], L)]
        if not workers or max(workers) > i:
            violations.append({"step": i, "kind": "ASK_WATCH_STOP_BEFORE_WORKERS", "lane": L,
                               "worker_stop_steps": workers})
        checks += 1
        later_shared = [j for j, x in enumerate(steps) if j > i and x["action"] == "stop" and x["target"] in shared]
        if later_shared:
            violations.append({"step": i, "kind": "ASK_WATCH_STOP_BEFORE_SHARED_SERVICE", "lane": L,
                               "shared_stop_steps": later_shared})
    return {"ok": not violations, "checks_run": checks, "violations": violations}


def parse_close_text(text: str, shared=SHARED_SERVICES) -> list[dict]:
    """A close NOTE in prose -> steps, one line at a time in order (the D31 note was prose). Per line: 'drain'
    (without a stop verb); 'confirm ... <service>'; 'stop|kill|exit ... watch/watcher/ask-watch'; '... worker(s)';
    '... <service>' (gpuq also matches 'arbiter'). 'lane X' scopes a line to X. Unrecognised lines yield nothing."""
    import re
    stop_verb = r"\b(stop|stopping|kill|exit|end|shut)"
    steps = []
    for line in text.splitlines():
        low = line.lower()
        m = re.search(r"\blane\s+([A-Z])\b", line)
        lane = m.group(1) if m else "*"
        has_stop = re.search(stop_verb, low)
        if re.search(r"\bdrain", low) and not has_stop:
            steps.append({"action": "drain"})
        for svc in shared:
            names = (svc, "arbiter") if svc == "gpuq" else (svc,)
            if any(n in low for n in names):
                if re.search(r"\bconfirm", low):
                    steps.append({"action": "confirm", "target": svc})
                elif has_stop:
                    steps.append({"action": "stop", "target": svc})
        if has_stop:
            if re.search(r"\bworkers?\b", low):
                steps.append({"action": "stop", "target": WORKER, "lane": lane})
            if re.search(r"\bwatch(er|ers|es)?\b|\bask[- ]?watch", low):
                steps.append({"action": "stop", "target": ASK_WATCH, "lane": lane})
    return steps


def _kind(b) -> str:
    return str(b.get("kind", "")).lower()


def _ts(b) -> float:
    return float(b.get("ts") or 0)


def normalize_beacons(entries) -> list[dict]:
    """Beacon rows -> the lint's shape {event, lane, kind, ts, pid, shared, tag, started_ts}. Accepts P's agreed record
    (a stream entry {"json": "..."} or its decoded dict, G7-exported rows included: {record: WATCH_BEACON, beacon:
    START|BEAT|STOP, lane, watcher, tag, pid, ts, started_ts, ...}; BEAT dropped) and the lint's own shape as is."""
    out = []
    for e in entries:
        e = dict(e)
        if "json" in e:
            j = e["json"]
            e = json.loads(j) if isinstance(j, str) else dict(j)
        if e.get("record") == "WATCH_BEACON" or "beacon" in e:
            b = str(e.get("beacon", "")).upper()
            if b not in ("START", "STOP"):
                continue
            e = {**e, "event": WATCH_START if b == "START" else WATCH_STOP, "kind": e.get("watcher", "")}
        if e.get("event") in (WATCH_START, WATCH_STOP):
            out.append(e)
    return out


def beacon_lint(beacons, confirmations: dict | None = None, shared=SHARED_SERVICES) -> dict:
    """What ACTUALLY happened, from watcher beacons (live BEACONS rows or their G7 export). Fields: event
    (WATCH_START | WATCH_STOP), lane, kind (ask_watch | worker | <service>), ts, shared (0|1), pid, tag, round_id,
    reason. FAIL when a lane's ask_watch WATCH_STOP precedes a WATCH_STOP of that lane's worker or of any shared
    service (deaf_s = the gap), or when a started worker of that lane had not stopped; flag a shared WATCH_STOP with
    no current confirmation (confirmations: service -> {ts, by, ref}, ts within CONFIRM_MAX_AGE_S before the stop)."""
    rows = sorted(normalize_beacons(beacons), key=_ts)
    shared = {x.lower() for x in shared}
    confirmations = confirmations or {}
    stops = [b for b in rows if b.get("event") == WATCH_STOP]

    def is_shared(b):
        return _kind(b) in shared or str(b.get("shared", "0")).lower() in ("1", "true")

    violations, checks = [], 0
    for b in stops:
        ts = _ts(b)
        if is_shared(b):
            checks += 1
            c = confirmations.get(_kind(b)) or {}
            if not c or not (ts - CONFIRM_MAX_AGE_S <= float(c.get("ts") or -1e18) <= ts):
                violations.append({"kind": "SHARED_STOP_UNCONFIRMED", "service": _kind(b), "lane": b.get("lane"),
                                   "ts": ts, "confirmation": c or None})
        if _kind(b) != ASK_WATCH:
            continue
        L = b.get("lane")
        checks += 1
        late_w = [_ts(x) for x in stops if _kind(x) == WORKER and x.get("lane") == L and _ts(x) > ts]
        started = [x for x in rows if x.get("event") == WATCH_START and _kind(x) == WORKER and x.get("lane") == L
                   and _ts(x) <= ts]
        unstopped = [x.get("pid") for x in started
                     if not any(_kind(y) == WORKER and y.get("pid") == x.get("pid") and _ts(y) <= ts for y in stops)]
        if late_w or unstopped:
            violations.append({"kind": "ASK_WATCH_STOP_BEFORE_WORKERS", "lane": L, "ts": ts,
                               "deaf_s": round(max(late_w or [ts]) - ts, 3), "unstopped_worker_pids": unstopped})
        checks += 1
        late_s = [_ts(x) for x in stops if is_shared(x) and _ts(x) > ts]
        if late_s:
            violations.append({"kind": "ASK_WATCH_STOP_BEFORE_SHARED_SERVICE", "lane": L, "ts": ts,
                               "deaf_s": round(max(late_s) - ts, 3)})
    return {"ok": not violations, "checks_run": checks, "violations": violations}


def close_sweep(r, since_id: str = "-", shared=SHARED_SERVICES) -> dict:
    """G4 acceptance 2, at close: beacon_lint over the live BEACONS stream with the pm:close:confirm:* records."""
    beacons = [f for _, f in r.xrange(BEACONS, min=since_id)] if r.exists(BEACONS) else []
    conf = {svc: r.hgetall(CONFIRM.format(svc)) for svc in shared}
    return beacon_lint(beacons, {k: v for k, v in conf.items() if v}, shared)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ru = sub.add_parser("run")
    ru.add_argument("--lanes", required=True)
    ru.add_argument("--epoch-min", type=float, default=30)
    ru.add_argument("--epochs", type=int)
    bo = sub.add_parser("boundary")
    bo.add_argument("n", type=int)
    bo.add_argument("--lanes", required=True)
    li = sub.add_parser("lint", help="G4: lint a close sequence (json steps or a prose note) and/or live beacons")
    li.add_argument("--sequence", help="file: a json list of steps, or a close note in prose")
    li.add_argument("--beacons", action="store_true", help="also lint the live pm:telemetry:watch beacons")
    li.add_argument("--self-test", action="store_true",
                    help="G4 gate argv: canonical close sequences must PASS and the planted D31 shapes must FAIL")
    rd = sub.add_parser("round", help="F-R5-2: start (or join) the round clock and run it to close")
    rd.add_argument("--lanes", required=True)
    from primordial.ops import round_clock as RC
    rd.add_argument("--round", default=RC.DEFAULT_ROUND, help="default: round_clock.DEFAULT_ROUND (one source)")
    rd.add_argument("--stage", default=None, help="default: round_clock.ROUNDS row of --round")
    # F-R6-6: the clock shape; each default (None) is the ROUNDS row of --round, so --round r5 is exactly R5
    rd.add_argument("--epoch-s", type=float, default=None)
    rd.add_argument("--epochs", type=int, default=None)
    rd.add_argument("--drain-s", type=float, default=None)
    rd.add_argument("--close-s", type=float, default=None)
    rd.add_argument("--t0-ts", type=float, default=None,
                    help="G8/R17: round T0; end_ts is capped at round_clock.cap_end_ts(T0, clock start)")
    rd.add_argument("--allow-repos", "--allowed-repos", dest="allowed_repos", default=None,
                    help="F-R7-1: G=F:/x;B=F:/y or a flat comma list (default: ROUNDS lane_repos)")
    for p in (ru, bo, rd):
        p.add_argument("--repo", default=os.environ.get("PM_EPOCH_REPO"),
                       help="the controller's own worktree (F-R5-6); never a lane or conductor worktree")
    return ap


def round_shape(a) -> dict:
    """F-R6-6: round_clock.start/plan kwargs from the `round` flags (None -> the round's ROUNDS row)."""
    return {"stage": a.stage, "epoch_s": a.epoch_s, "epochs": a.epochs, "drain_s": a.drain_s, "close_s": a.close_s}


def explicit_round(argv) -> bool:
    """G8/R18: the `round` command names its round. The parser default (DEFAULT_ROUND) is a development
    convenience only; a production clock never starts from it."""
    return any(x == "--round" or x.startswith("--round=") for x in (sys.argv[1:] if argv is None else argv))


# Canonical close order for a lane (G4 protocol): drain; workers down; shared service down only after a conductor
# confirmation; the ask watch LAST.
LANE_CLOSE_SEQUENCE = [{"action": "drain"}, {"action": "stop", "target": WORKER, "lane": "*"},
                       {"action": "confirm", "target": "gpuq"}, {"action": "stop", "target": "gpuq"},
                       {"action": "stop", "target": ASK_WATCH, "lane": "*"}]
# Planted: A's r7 close note shape (D31) -- watchers stopped before workers and the arbiter, no confirmation.
PLANTED_D31_NOTE = """1. Drain has begun; no new jobs.
2. Lanes: stop your ask watchers now.
3. Then stop workers.
4. Stop the gpuq arbiter when your last GPU job ends."""
PLANTED_D31_BEACONS = [
    {"record": "WATCH_BEACON", "beacon": "START", "lane": "E", "watcher": "worker", "pid": 11, "ts": 1.0},
    {"record": "WATCH_BEACON", "beacon": "STOP", "lane": "E", "watcher": "worker", "pid": 11, "ts": 100.0},
    {"record": "WATCH_BEACON", "beacon": "STOP", "lane": "E", "watcher": "ask_watch", "pid": 10, "ts": 200.0},
    {"record": "WATCH_BEACON", "beacon": "STOP", "lane": "E", "watcher": "gpuq", "pid": 12, "ts": 883.0}]


def self_test() -> list[tuple[str, bool, dict]]:
    """G4 gate: (name, passed, report). A lint that cannot FAIL is not a lint, so the planted shapes must fail."""
    out = []
    for name, rep_, want_ok in (("controller_close_sequence", protocol_lint(CONTROLLER_CLOSE_SEQUENCE), True),
                                ("lane_close_sequence", protocol_lint(LANE_CLOSE_SEQUENCE), True),
                                ("planted_d31_note", protocol_lint(parse_close_text(PLANTED_D31_NOTE)), False),
                                ("planted_d31_beacons", beacon_lint(PLANTED_D31_BEACONS), False)):
        # the controller stops no watcher and no shared service, so 0 checks is its correct result; every other
        # case must actually exercise the lint
        vacuous_ok = name == "controller_close_sequence"
        out.append((name, rep_["ok"] is want_ok and (rep_["checks_run"] > 0 or vacuous_ok), rep_))
    return out


def lint_main(a) -> int:
    """G4 CLI: rc 0 only when at least one lint ran and every lint passed; prints `checks run: N`."""
    reps = []
    if a.self_test:
        for name, passed, x in self_test():
            reps.append((name, {"ok": passed, "checks_run": 1, "violations": [] if passed else [{"kind": "SELF_TEST_FAILED",
                                                                                            "report": x}]}))
    if a.sequence:
        text = pathlib.Path(a.sequence).read_text(encoding="utf-8")
        try:
            steps = json.loads(text)
        except ValueError:
            steps = parse_close_text(text)
        reps.append(("sequence", protocol_lint(steps)))
    if a.beacons:
        from primordial.bus import bus
        reps.append(("beacons", close_sweep(bus.conn())))
    for name, x in reps:
        print(json.dumps({"lint": name, **x}, sort_keys=True))
    ok = bool(reps) and all(x["ok"] for _, x in reps)
    print(f"checks run: {sum(x['checks_run'] for _, x in reps)}")
    print("PROTOCOL LINT " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None) -> int:
    a = parser().parse_args(argv)
    if a.cmd == "lint":
        return lint_main(a)
    if a.cmd == "round":
        from primordial.ops import round_clock as RC
        if not explicit_round(argv):
            print("refused: `round` needs an explicit --round (R18: a campaign clock never infers its identity)",
                  file=sys.stderr)
            return 2
        try:
            RC.row_for(a.round)
        except RC.UnknownRound as e:
            print(f"refused: {e}", file=sys.stderr)
            return 2
    ok, why = controller_repo(a.repo)
    if not ok:
        print(f"refused: {why}", file=sys.stderr)
        return 2
    lanes = [x.strip() for x in a.lanes.split(",") if x.strip()]
    repo = pathlib.Path(a.repo).resolve()
    kw = {"out": repo / EPOCHS_REL, "repo": repo, "push": True}
    if a.cmd == "round":
        from primordial.ops import residue
        from primordial.ops import round_clock as RC
        ec = EpochController(lanes, **kw)
        allowed = a.allowed_repos                       # residue.parse_allow: per-lane map or flat list
        rep = residue.scan(ec.r, a.round, allowed)       # F-R7-1: no clock opens over residue (read-only scan)
        if not rep["ok"]:
            print(json.dumps(rep, sort_keys=True, default=str))
            print(f"refused: residue in the live store ({len(rep['residue'])} items)", file=sys.stderr)
            return 3
        now = time.time()
        cap = None if a.t0_ts is None else RC.cap_end_ts(a.t0_ts, now)
        rec = ec.run_round(RC.start(ec.r, a.round, start_ts=now, science_end_ts=cap, **round_shape(a)))
        print(json.dumps({k: rec[k] for k in ("round_id", "closed_ts", "sha")}, sort_keys=True))
        return 0
    if a.cmd == "boundary":
        print(json.dumps(EpochController(lanes, **kw).boundary(a.n), sort_keys=True))
        return 0
    for rec in EpochController(lanes, epoch_s=a.epoch_min * 60, **kw).run(a.epochs):
        print(json.dumps(rec, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
