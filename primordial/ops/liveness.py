"""Round 2 gate F2: lane liveness from the harness side, plus an explicit reaper.

A lane is judged from three sources that need no cooperation from the LLM:
  pid        the launch log's latest start for the lane (launch_lane.ps1): alive?
  transcript ~/.claude/projects/*/<session_id>.jsonl last write (activity)
  heartbeat  pm:alive:<L> on the bus (refreshed by every bus call)

  activity   (X, round 3) CPU gained by the session's process tree between two
             samples (e.g. a background python run), or a live F7 worker
             state pm:worker:<L>

States (F-R5-4, operator 19 s4.3), first match wins:
  DEAD          exit logged or pid gone
  BUSY_COMPUTE  pm:worker:<L> state busy, or (quiet lane) CPU gained by the session tree over one shared
                sample window, or a live worker key of unknown state
  DRAINING      stop flag pm:jobs:<L>:stop set (or pm:epoch:state phase draining) and the worker is
                stopped or absent -- before STALE, so a draining lane is never paged
  ACTIVE        transcript written within active_s (120 s)
  IDLE          heartbeat live, or transcript age <= stale_s: idle never pages
  STALE         pid alive, transcript older than stale_s (or unknown), no heartbeat, no compute
  NOT_LAUNCHED  no launch recorded
The monitor posts `missing` to A only on a change into STALE or DEAD of a lane that HOLDS A JOB
(pm:worker:<L> job_id non-empty, or pending entries in pm:jobs:<L> group worker-<L>). Round 2: E was
flagged STALE at 16:53 during a background run -- transcript 618 s quiet, heartbeat lapsed while it
waited, and nothing looked at the run itself.

    python -m primordial.ops.liveness                     # one table
    python -m primordial.ops.liveness --watch 60 --post --export-every-min 10
    python -m primordial.ops.liveness reap B --yes        # kill lane B's recorded process tree

Reaping is never automatic: a STALE lane may be inside a long tool call.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import pathlib
import time

LOG = pathlib.Path(os.environ.get("PM_LAUNCH_LOG", "C:/Users/jcrai/lab/pm-data/launcher/launch_log.jsonl"))
PROJECTS = pathlib.Path(os.environ.get("CLAUDE_PROJECTS", str(pathlib.Path.home() / ".claude" / "projects")))
from primordial.core.contract import LANES  # noqa: E402  (cohorts + builders)


def _ts(s: str) -> float:
    return datetime.datetime.fromisoformat(s).timestamp()


def launches(log=LOG) -> dict:
    """lane -> latest launch {pid, start, session_id, exit_code, exit_ts}."""
    out: dict = {}
    if not pathlib.Path(log).exists():
        return out
    for line in pathlib.Path(log).read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        lane = e.get("lane")
        if e.get("event") == "start":
            out[lane] = {"pid": e["pid"], "start": e["ts"], "worktree": e.get("worktree")}
        elif lane in out and out[lane]["pid"] == e.get("pid"):
            if e.get("event") == "session":
                out[lane]["session_id"] = e.get("session_id")
            elif e.get("event") == "exit":
                out[lane].update(exit_code=e.get("exit_code"), exit_ts=e.get("ts"), session_id=e.get("session_id"))
            elif e.get("event") == "reaped":
                out[lane]["reaped_ts"] = e.get("ts")
    return out


def transcript_age(session_id: str | None) -> float | None:
    if not session_id:
        return None
    hits = glob.glob(str(PROJECTS / "*" / f"{session_id}.jsonl"))
    return time.time() - max(os.path.getmtime(h) for h in hits) if hits else None


def pid_alive(pid: int) -> bool:
    import psutil
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except psutil.Error:
        return False


def tree_cpu(pid: int) -> dict:
    """{descendant pid: cumulative CPU seconds} under pid (the session itself excluded)."""
    import psutil
    try:
        kids = psutil.Process(pid).children(recursive=True)
    except psutil.Error:
        return {}
    out = {}
    for q in kids:
        try:
            t = q.cpu_times()
            out[q.pid] = t.user + t.system
        except psutil.Error:
            pass
    return out


def _wstate(r, lane: str) -> dict | None:
    """pm:worker:<L> as a dict, {} for a live key whose fields cannot be read, None when absent."""
    try:
        if not r.exists(f"pm:worker:{lane}"):
            return None
    except Exception:
        return None
    try:
        return dict(r.hgetall(f"pm:worker:{lane}") or {})
    except Exception:
        return {}


def _draining(r, lane: str) -> bool:
    try:
        if r.exists(f"pm:jobs:{lane}:stop"):
            return True
    except Exception:
        pass
    try:
        return r.hget("pm:epoch:state", "phase") == "draining"
    except Exception:
        return False


def holds_job(r, lane: str) -> bool:
    """A job in the lane's hands: the worker names one, or the lane's job stream has pending entries."""
    try:
        if (r.hgetall(f"pm:worker:{lane}") or {}).get("job_id"):
            return True
    except Exception:
        pass
    try:
        return int((r.xpending(f"pm:jobs:{lane}", f"worker-{lane}") or {}).get("pending", 0)) > 0
    except Exception:
        return False


def status(stale_s: float = 600, r=None, sample_s: float = 1.0, min_cpu_s: float = 0.05,
           snap=tree_cpu, sleep=time.sleep, active_s: float = 120) -> dict:
    from primordial.bus import bus
    try:
        r = r or bus.conn()
        beats = bus.alive(r=r)
    except Exception:
        beats = {}
    now = time.time()
    table, quiet = {}, {}
    for lane, L in launches().items():
        age = transcript_age(L.get("session_id"))
        hb = beats.get(lane)
        live_pid = "exit_code" not in L and pid_alive(int(L["pid"]))
        ws = _wstate(r, lane) if live_pid else None
        wst = None if ws is None else ws.get("state")
        if not live_pid:
            state = "DEAD"
        elif wst == "busy":
            state = "BUSY_COMPUTE"
        elif _draining(r, lane) and wst in (None, "stopped"):
            state = "DRAINING"
        elif age is not None and age <= active_s:
            state = "ACTIVE"
        elif hb or (age is not None and age <= stale_s):
            state = "IDLE"
        else:
            state = "STALE"                              # provisional: activity is checked below
            quiet[lane] = int(L["pid"])
        table[lane] = dict(state=state, pid=L["pid"], session_id=L.get("session_id"),
                           up_s=round(now - _ts(L["start"])), transcript_age_s=None if age is None else round(age),
                           heartbeat_tag=(hb or {}).get("tag"), exit_code=L.get("exit_code"), worker_state=wst)
    if quiet:
        before = {lane: snap(pid) for lane, pid in quiet.items()}
        sleep(sample_s)
        for lane, pid in quiet.items():
            after = snap(pid)
            gained = sum(max(0.0, c - before[lane].get(k, 0.0)) for k, c in after.items())
            ws = _wstate(r, lane)
            worker = ws is not None and ws.get("state") not in ("idle", "stopped")
            if gained >= min_cpu_s or worker:
                table[lane]["state"] = "BUSY_COMPUTE"
            table[lane].update(tree_cpu_gained_s=round(gained, 3), worker_live=ws is not None)
    for lane in LANES:
        table.setdefault(lane, {"state": "NOT_LAUNCHED"})
    return table


def print_table(t: dict) -> None:
    for lane in LANES:
        s = t[lane]
        print(f"{lane} {s['state']:13s} pid={s.get('pid')} up={s.get('up_s')}s "
              f"transcript_age={s.get('transcript_age_s')}s heartbeat={s.get('heartbeat_tag')} "
              f"exit={s.get('exit_code')} session={s.get('session_id')}")


def post_changes(t: dict, r) -> list[str]:
    """Record each lane's state; page A only on a change into STALE or DEAD of a lane holding a job. -> paged."""
    from primordial.bus import bus
    os.environ.setdefault("PM_LANE", "A")
    paged = []
    for lane, s in t.items():
        key = f"pm:liveness:{lane}"
        prev = r.get(key)
        if s["state"] != prev:
            r.set(key, s["state"])
            if s["state"] in ("DEAD", "STALE") and prev is not None and holds_job(r, lane):
                bus.post("missing", f"{lane} {s['state']}", json.dumps(s), to="A", r=r)
                paged.append(lane)
    return paged


def reap(lane: str, yes: bool) -> int:
    import psutil
    L = launches().get(lane)
    if not L:
        print(f"no launch recorded for {lane}")
        return 1
    try:
        p = psutil.Process(int(L["pid"]))
    except psutil.Error:
        print(f"{lane} pid {L['pid']} is not running")
        return 1
    if "claude" not in p.name().lower():
        print(f"refusing: pid {p.pid} is {p.name()}, not a claude process (pid reused?)")
        return 1
    procs = [p] + p.children(recursive=True)
    print(f"{lane}: {len(procs)} processes under pid {p.pid} ({p.name()})")
    if not yes:
        print("dry run; add --yes to kill")
        return 0
    for q in reversed(procs):
        try:
            q.kill()
        except psutil.Error:
            pass
    with open(LOG, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"event": "reaped", "lane": lane, "pid": p.pid,
                             "ts": datetime.datetime.now().astimezone().isoformat()}) + "\n")
    print("reaped")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="status", choices=["status", "reap"])
    ap.add_argument("lane", nargs="?")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--stale-min", type=float, default=10)
    ap.add_argument("--watch", type=float, default=0, help="repeat every N seconds")
    ap.add_argument("--post", action="store_true", help="post `missing` on state changes")
    ap.add_argument("--export-every-min", type=float, default=0)
    a = ap.parse_args(argv)
    if a.cmd == "reap":
        return reap(a.lane, a.yes)
    from primordial.bus import bus
    r = bus.conn()
    last_export = 0.0
    while True:
        t = status(a.stale_min * 60, r=r)
        print(time.strftime("%H:%M:%S"))
        print_table(t)
        if a.post:
            post_changes(t, r)
        if a.export_every_min and time.time() - last_export >= a.export_every_min * 60:
            from primordial.ops import bus_export
            bus_export.export(r=r)
            last_export = time.time()
        if not a.watch:
            return 0
        time.sleep(a.watch)


if __name__ == "__main__":
    raise SystemExit(main())
