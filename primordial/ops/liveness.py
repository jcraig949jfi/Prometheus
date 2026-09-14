"""Round 2 gate F2: lane liveness from the harness side, plus an explicit reaper.

A lane is judged from three sources that need no cooperation from the LLM:
  pid        the launch log's latest start for the lane (launch_lane.ps1): alive?
  transcript ~/.claude/projects/*/<session_id>.jsonl last write (activity)
  heartbeat  pm:alive:<L> on the bus (refreshed by every bus call)

States: DEAD (exit logged or pid gone), STALE (pid alive, transcript quiet for
more than --stale-min, and no live heartbeat), OK, NOT_LAUNCHED.
On a change into DEAD or STALE the monitor posts `missing` on the bus once.

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
LANES = ("A", "B", "C", "D", "E")


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


def status(stale_s: float = 600, r=None) -> dict:
    from primordial.bus import bus
    try:
        beats = bus.alive(r=r or bus.conn())
    except Exception:
        beats = {}
    now = time.time()
    table = {}
    for lane, L in launches().items():
        age = transcript_age(L.get("session_id"))
        hb = beats.get(lane)
        live_pid = "exit_code" not in L and pid_alive(int(L["pid"]))
        if not live_pid:
            state = "DEAD"
        elif (age is None or age > stale_s) and not hb:
            state = "STALE"
        else:
            state = "OK"
        table[lane] = dict(state=state, pid=L["pid"], session_id=L.get("session_id"),
                           up_s=round(now - _ts(L["start"])), transcript_age_s=None if age is None else round(age),
                           heartbeat_tag=(hb or {}).get("tag"), exit_code=L.get("exit_code"))
    for lane in LANES:
        table.setdefault(lane, {"state": "NOT_LAUNCHED"})
    return table


def print_table(t: dict) -> None:
    for lane in LANES:
        s = t[lane]
        print(f"{lane} {s['state']:13s} pid={s.get('pid')} up={s.get('up_s')}s "
              f"transcript_age={s.get('transcript_age_s')}s heartbeat={s.get('heartbeat_tag')} "
              f"exit={s.get('exit_code')} session={s.get('session_id')}")


def post_changes(t: dict, r) -> None:
    from primordial.bus import bus
    os.environ.setdefault("PM_LANE", "A")
    for lane, s in t.items():
        key = f"pm:liveness:{lane}"
        prev = r.get(key)
        if s["state"] != prev:
            r.set(key, s["state"])
            if s["state"] in ("DEAD", "STALE") and prev is not None:
                bus.post("missing", f"{lane} {s['state']}", json.dumps(s), to="A", r=r)


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
