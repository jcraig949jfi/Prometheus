"""F14 (round 3): the epoch controller. 30-minute generations with clean boundaries.

At T + n x epoch_s the controller:
  1. posts `EPOCH n` on the bus (to ALL);
  2. sets pm:jobs:<L>:stop for every lane: F7 workers stop taking jobs (a job
     already running finishes; its rows commit as usual);
  3. waits until every live worker reports `stopped` (pm:worker:<L>, refreshed
     by the worker; a lane with no live worker is not waited for), or
     drain_timeout_s, recording stragglers;
  4. exports the bus (ops/bus_export) into <out>/epoch_<n>/;
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
        rec = {"round_id": rid, "clock": clock, "closed_ts": round(time.time(), 3), "epochs": out,
               "budget": self._budget()}
        (self.out / f"ROUND_{rid}.json").write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n",
                                                   encoding="utf-8")
        self.r.hset(STATE, mapping={"phase": "closed", "ts": rec["closed_ts"]})
        self._event("round_closed", round_id=rid)
        self._publish_log()
        rec["sha"] = commit_path(self.out, f"ROUND-{rid}", "(round close record)", repo=self.repo)
        self._event("round_committed", sha=rec["sha"])
        self._push()
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
        counts = self.export(out=epoch_dir, stamp=f"e{n}", r=self.r)
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
    rd = sub.add_parser("round", help="F-R5-2: start (or join) the round clock and run it to close")
    rd.add_argument("--lanes", required=True)
    rd.add_argument("--round", default="r6")
    rd.add_argument("--stage", default=None, help="default: round_clock.ROUNDS row of --round")
    # F-R6-6: the clock shape; each default (None) is the ROUNDS row of --round, so --round r5 is exactly R5
    rd.add_argument("--epoch-s", type=float, default=None)
    rd.add_argument("--epochs", type=int, default=None)
    rd.add_argument("--drain-s", type=float, default=None)
    rd.add_argument("--close-s", type=float, default=None)
    for p in (ru, bo, rd):
        p.add_argument("--repo", default=os.environ.get("PM_EPOCH_REPO"),
                       help="the controller's own worktree (F-R5-6); never a lane or conductor worktree")
    return ap


def round_shape(a) -> dict:
    """F-R6-6: round_clock.start/plan kwargs from the `round` flags (None -> the round's ROUNDS row)."""
    return {"stage": a.stage, "epoch_s": a.epoch_s, "epochs": a.epochs, "drain_s": a.drain_s, "close_s": a.close_s}


def main(argv=None) -> int:
    a = parser().parse_args(argv)
    ok, why = controller_repo(a.repo)
    if not ok:
        print(f"refused: {why}", file=sys.stderr)
        return 2
    lanes = [x.strip() for x in a.lanes.split(",") if x.strip()]
    repo = pathlib.Path(a.repo).resolve()
    kw = {"out": repo / EPOCHS_REL, "repo": repo, "push": True}
    if a.cmd == "round":
        from primordial.ops import round_clock as RC
        ec = EpochController(lanes, **kw)
        rec = ec.run_round(RC.start(ec.r, a.round, **round_shape(a)))
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
