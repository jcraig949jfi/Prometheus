"""F-R7-1 (round 7; R6 packet D12 + D14): cross-round residue in the live store.

Round 6 lost ~19 min of B-E to stale r5 stop flags (D12) and ~44 min of D to a live r5 worker that shared
the worker-D group and consumed an r6 job (D14). Here code finds residue before a clock opens, and the round
close stops exactly the registered worker processes.

Registration (fabric/worker.py): every serving worker writes pm:worker:reg:<L>:<pid>
{pid, lane, repo, round_id, cmdline, host, started_ts, tag}, refreshed with its heartbeat, deleted on stop.

scan(r, round_id, allowed_repos) is READ-ONLY. Residue kinds:
  STOP_FLAG             any pm:jobs:*:stop
  FOREIGN_REPO          a live, cmdline-verified registered worker whose repo is not an allowed round worktree
  MULTI_CONSUMER        > 1 live consumer of group worker-<L> (or > 1 live verified registration) for a lane; a
                        consumer is LIVE only if a live, cmdline-verified registration of lane L has tag == its name
  DEAD_CONSUMER         a consumer of worker-<L> with no live registered pid bound to its name (detail: pending)
  UNREGISTERED_ACTIVE_CONSUMER  the same, but it read from its group less than ACTIVE_IDLE_S ago: a LIVE worker
                        that never registered (e.g. started on pre-F-R7-1 code); stop or restart it, never clear it
  UNARCHIVED_PRIOR_KEY  a key in a round-namespaced family (pm:prior:) not namespaced by a round id (r<digits>)

clear(r, prior_round) removes only what a CLOSED prior round provably left (A, 16:40): its stop flags when
pm:epoch:state shows that round closed and the flag value == that round's epoch count; dead consumers with
pending == 0 and idle >= ACTIVE_IDLE_S. Everything else is refused (FLAG_ROUND_NOT_CLOSED, FLAG_VALUE_MISMATCH,
CONSUMER_RECENTLY_ACTIVE, CONSUMER_PENDING,
CONSUMER_LIVE, NOT_CLEARABLE). It never kills and never touches pm:prior:* (H-R7-2 migrates those).
    python -m primordial.ops.residue clear --prior-round r6 [--round r7 --allowed-repos a,b]   # rc 2 if refused
Notes (not residue): STALE_REGISTRATION (pid gone), PID_CMDLINE_MISMATCH (pid alive, not a worker: pid reuse).

allowed_repos, first that applies:
  1. explicit (CLI --allow-repos "G=F:/x;B=F:/y" per lane, or a flat comma list);
  1b. DECLARED round_clock.ROUNDS[<round>]["lane_repos"] (per lane; lane "gpu" = the GPU arbiter);
  2. Redis set pm:round:<round_id>:worktrees;
  3. env PM_ROUND_WORKTREES (comma separated);
  4. convention: a repo whose basename starts with "nestor-<round_id>-" or "nestor-bld-".
Paths compare normalized (forward slashes, case-insensitive, no trailing slash).

stop_registered(r, round_id, lanes) stops EXACTLY the registered pids whose LIVE argv tokens verify as
`-m primordial.fabric.worker serve --lane <L>` (plus that verified worker's own child processes). It never
matches a joined command string, never kills by name, skips its own pid, and never touches an unregistered
process (lesson: a substring kill once matched its own `python -c` source).

    python -m primordial.ops.residue scan --round r7 [--allowed-repos a,b]    # rc 1 on residue
    python -m primordial.ops.residue stop --round r7 [--lanes B,C]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time

REG_PATTERN = "pm:worker:reg:*"
PRIOR_FAMILIES = ("pm:prior:",)
WORKER_MODULE = "primordial.fabric.worker"
GPU_LANE, GPU_MODULE = "gpu", "primordial.nv.gpuq"
GPU_QUEUE, GPU_GROUP = "pm:gpu:jobs", "gpu-arbiter"          # primordial/nv/gpuq.py QUEUE / GROUP
REG = "pm:worker:reg:{}:{}"                                 # same key as fabric/worker.py REG
REG_TTL = 90


def register(r, lane: str, repo, round_id: str | None = None, pid: int | None = None, tag: str | None = None) -> str:
    """Register a serving process (F7 worker or GPU arbiter, lane "gpu") so scan/stop can see it. Call it from
    inside the serving process (os.getpid() is the real interpreter), refresh with refresh(), and unregister() on
    exit. -> the registration key."""
    import sys
    pid = os.getpid() if pid is None else pid
    try:
        import psutil
        cmdline = psutil.Process(pid).cmdline()
    except Exception:
        cmdline = list(sys.argv)
    key = REG.format(lane, pid)
    r.hset(key, mapping={"pid": pid, "lane": lane, "repo": str(pathlib.Path(repo).resolve()).replace("\\", "/"),
                         "round_id": (r.get("pm:round:current") or "") if round_id is None else round_id,
                         "cmdline": json.dumps(cmdline), "host": os.environ.get("COMPUTERNAME", ""),
                         "started_ts": f"{time.time():.3f}",
                         "tag": os.environ.get("PM_TAG", "") if tag is None else tag})
    r.expire(key, REG_TTL)
    _RECORDS[key] = r.hgetall(key)
    return key


# D28 (r8 C3): registrations made by THIS process, so refresh() can re-create one whose key expired while the
# process was blocked in a job longer than REG_TTL. r7: C-R7-01's GPU job ran 217.6 s > 90 s, the arbiter's key
# expired mid-job, and every later refresh was `EXPIRE missing-key` -- a silent no-op -- for ~23 min.
_RECORDS: dict[str, dict] = {}


def refresh(r, key: str) -> bool:
    """Extend the registration TTL; if the key is GONE, re-create it from this process's register() record.
    Re-creation happens only for a key this process registered (and has not unregistered) whose pid is still
    alive, so a refresh can never resurrect a dead or foreign registration. -> True iff the key exists after."""
    if r.expire(key, REG_TTL):
        return True
    rec = _RECORDS.get(key)
    if not rec or not _live(int(rec.get("pid") or 0))[0]:
        return False
    n = int(rec.get("reregistered_n") or 0) + 1
    rec.update(reregistered_n=str(n), reregistered_ts=f"{time.time():.3f}")   # disclosed on the record, never silent
    r.hset(key, mapping=rec)
    r.expire(key, REG_TTL)
    return True


def keepalive(r, key: str, interval_s: float = REG_TTL / 3):
    """Refresh `key` from a daemon thread every interval_s, so a caller that blocks for longer than REG_TTL (the
    GPU arbiter inside run_job) stays registered. -> a threading.Event; set() it (or unregister) to stop."""
    import threading
    stop = threading.Event()

    def loop():
        while not stop.wait(interval_s) and key in _RECORDS:
            try:
                refresh(r, key)
            except Exception:                     # noqa: BLE001 -- a bus hiccup must not kill the serving process
                pass

    threading.Thread(target=loop, name=f"reg-keepalive:{key}", daemon=True).start()
    return stop


def unregister(r, key: str) -> None:
    _RECORDS.pop(key, None)                        # first, so a concurrent keepalive cannot re-create it
    r.delete(key)


def verify_worker_cmdline(argv, lane: str) -> bool:
    """True only for argv TOKENS `<python> ... -m primordial.fabric.worker serve ... --lane <lane>`. The first
    interpreter mode token must be -m (a `-c` program carrying those words as arguments is not a worker)."""
    if not isinstance(argv, (list, tuple)) or len(argv) < 4:     # `python -m primordial.nv.gpuq serve` is 4 tokens
        return False
    toks = [str(t) for t in argv]
    i = None
    for j, t in enumerate(toks[1:], 1):
        if t == "-c" or (t.startswith("-c") and not t.startswith("--")):
            return False
        if t == "-m":
            i = j
            break
    if lane == GPU_LANE:                                  # the GPU arbiter: -m primordial.nv.gpuq serve (no --lane)
        return i is not None and toks[i + 1:i + 3] == [GPU_MODULE, "serve"]
    if i is None or toks[i + 1:i + 3] != [WORKER_MODULE, "serve"]:
        return False
    rest = toks[i + 3:]
    for k, t in enumerate(rest):
        if t == "--lane" and k + 1 < len(rest):
            return rest[k + 1] == lane
        if t.startswith("--lane="):
            return t.split("=", 1)[1] == lane
    return False


def _norm(p) -> str:
    return str(p).replace("\\", "/").rstrip("/").lower()


def registrations(r) -> list[dict]:
    out = []
    for k in r.scan_iter(REG_PATTERN):
        h = r.hgetall(k)
        if not h:
            continue
        d = dict(h, key=k)
        try:
            d["pid"] = int(d.get("pid", 0))
        except ValueError:
            d["pid"] = 0
        try:
            d["cmdline"] = json.loads(d.get("cmdline") or "[]")
        except ValueError:
            d["cmdline"] = []
        out.append(d)
    return out


def _live(pid: int):
    """-> (alive, live argv or None)."""
    import psutil
    try:
        p = psutil.Process(pid)
        if not p.is_running() or p.status() == psutil.STATUS_ZOMBIE:
            return False, None
        return True, p.cmdline()
    except psutil.Error:
        return False, None


def parse_allow(spec):
    """'G=F:/x;B=F:/y,F:/z' -> {lane: [paths]}; 'F:/a,F:/b' (or a list) -> flat list for every lane; dict passes."""
    if spec is None or isinstance(spec, dict):
        return spec
    if isinstance(spec, (list, tuple, set)):
        return [str(x) for x in spec if str(x).strip()]
    spec = str(spec)
    if "=" in spec:
        out = {}
        for part in spec.split(";"):
            if "=" in part:
                lane, paths = part.split("=", 1)
                out[lane.strip()] = [p for p in paths.split(",") if p.strip()]
        return out
    return [p for p in spec.split(",") if p.strip()]


def _per_lane(mapping: dict, source: str):
    norm = {L: {_norm(p) for p in ps} for L, ps in mapping.items()}
    return norm, (lambda lane, p: _norm(p) in norm.get(lane, set())), source


def _flat(paths, source: str):
    allowed = {_norm(x) for x in paths}
    return sorted(allowed), (lambda lane, p: _norm(p) in allowed), source


def allowed_repos(r, round_id: str, explicit=None):
    """DECLARED allowed repos (A, R7). -> (declaration, predicate(lane, path) -> bool, source). Order: explicit
    (per-lane map or flat list); round_clock.ROUNDS[round_id]["lane_repos"]; Redis set pm:round:<id>:worktrees;
    env PM_ROUND_WORKTREES; convention (basename nestor-<round>- or nestor-bld-). A lane missing from a per-lane
    map has no allowed repo. Paths compare with slashes normalized, case-insensitive."""
    explicit = parse_allow(explicit)
    if isinstance(explicit, dict) and explicit:
        return _per_lane(explicit, "explicit")
    if explicit:
        return _flat(explicit, "explicit")
    from primordial.ops import round_clock as RC
    declared = (RC.ROUNDS.get(round_id) or {}).get("lane_repos")
    if declared:
        return _per_lane(declared, f"round_clock.ROUNDS[{round_id}].lane_repos")
    members = r.smembers(f"pm:round:{round_id}:worktrees") if round_id else set()
    if members:
        return _flat(members, f"pm:round:{round_id}:worktrees")
    env = [x for x in os.environ.get("PM_ROUND_WORKTREES", "").split(",") if x.strip()]
    if env:
        return _flat(env, "PM_ROUND_WORKTREES")
    prefixes = (f"nestor-{round_id}-".lower(), "nestor-bld-")
    return None, (lambda lane, p: pathlib.PurePosixPath(_norm(p)).name.startswith(prefixes)), "convention"


def live_registrations(r) -> tuple[list[dict], list[dict]]:
    """-> (registrations whose pid is alive with a verified worker argv, notes for the rest)."""
    live, notes = [], []
    for reg in registrations(r):
        alive, argv = _live(reg["pid"])
        if not alive:
            notes.append({"kind": "STALE_REGISTRATION", "key": reg["key"], "pid": reg["pid"], "lane": reg.get("lane")})
        elif not verify_worker_cmdline(argv, reg.get("lane", "")):
            notes.append({"kind": "PID_CMDLINE_MISMATCH", "key": reg["key"], "pid": reg["pid"], "lane": reg.get("lane")})
        else:
            live.append(reg)
    return live, notes


def lane_groups(r):
    """Yield (lane, stream key, group, consumers): every pm:jobs:<L> with group worker-<L>, plus the GPU arbiter's
    pm:gpu:jobs group gpu-arbiter as lane "gpu"."""
    streams = []
    for k in sorted(r.scan_iter("pm:jobs:*")):
        parts = k.split(":")
        if len(parts) == 3:
            streams.append((parts[2], k, f"worker-{parts[2]}"))
    streams.append((GPU_LANE, GPU_QUEUE, GPU_GROUP))
    for lane, k, group in streams:
        try:
            if r.type(k) != "stream":
                continue
            consumers = r.xinfo_consumers(k, group)
        except Exception:
            continue
        yield lane, k, group, consumers


ACTIVE_IDLE_S = 120.0   # an unregistered consumer that read within this window is a live, unregistered worker


def _recently_active(c: dict) -> bool:
    idle = c.get("idle")
    return idle is not None and int(idle) < ACTIVE_IDLE_S * 1000


def _bound(live: list[dict], lane: str, name: str) -> list[dict]:
    """A consumer is live only if a live, verified registration of this lane carries its name as tag."""
    return [g for g in live if g.get("lane") == lane and g.get("tag") == name]


def scan(r, round_id: str, allowed=None, now: float | None = None) -> dict:
    """Read-only residue scan. -> {ok, residue: [...], notes: [...], allowed_source}."""
    residue = []
    for k in sorted(r.scan_iter("pm:jobs:*:stop")):
        residue.append({"kind": "STOP_FLAG", "key": k, "detail": r.get(k)})
    _, is_allowed, source = allowed_repos(r, round_id, allowed)
    live, notes = live_registrations(r)
    live_by_lane: dict = {}
    for reg in live:
        live_by_lane.setdefault(reg.get("lane"), []).append(reg)
        if not is_allowed(reg.get("lane"), reg.get("repo", "")):
            residue.append({"kind": "FOREIGN_REPO", "lane": reg.get("lane"), "pid": reg["pid"],
                            "detail": {"repo": reg.get("repo"), "round_id": reg.get("round_id"), "tag": reg.get("tag")}})
    multi = {L: {"pids": sorted(g["pid"] for g in regs), "consumers": []}
             for L, regs in live_by_lane.items() if len(regs) > 1}
    for lane, key, group, consumers in lane_groups(r):
        live_names = []
        for c in consumers:
            name = c.get("name")
            if _bound(live, lane, name):
                live_names.append(name)
            else:
                kind = "UNREGISTERED_ACTIVE_CONSUMER" if _recently_active(c) else "DEAD_CONSUMER"
                residue.append({"kind": kind, "lane": lane, "key": key,
                                "detail": {"group": group, "consumer": name,
                                           "pending": int(c.get("pending", 0)), "idle_ms": c.get("idle")}})
        if len(live_names) > 1:
            m = multi.setdefault(lane, {"pids": sorted(g["pid"] for g in live_by_lane.get(lane, [])), "consumers": []})
            m["consumers"] = sorted(live_names)
    for lane in sorted(multi, key=str):
        residue.append({"kind": "MULTI_CONSUMER", "lane": lane, "detail": multi[lane]})
    for fam in PRIOR_FAMILIES:
        for k in sorted(r.scan_iter(fam + "*")):
            seg = k[len(fam):].split(":", 1)[0]
            if not re.fullmatch(r"r\d+", seg):
                residue.append({"kind": "UNARCHIVED_PRIOR_KEY", "key": k})
    cur = current_closed(r, now)
    if cur is not None:
        residue.append({"kind": "CURRENT_POINTS_AT_CLOSED_ROUND", "key": "pm:round:current", "detail": cur})
    return {"ok": not residue, "round_id": round_id, "residue": residue, "notes": notes, "allowed_source": source,
            "ts": round(time.time() if now is None else now, 3)}


NOT_CLEARABLE_KINDS = ("FOREIGN_REPO", "MULTI_CONSUMER", "UNARCHIVED_PRIOR_KEY", "CURRENT_POINTS_AT_CLOSED_ROUND")


def current_closed(r, now: float | None = None) -> dict | None:
    """D18: the RAW pm:round:current pointer (round_clock.read(r) now hides it) when it names a closed round:
    that round's end_ts < now, or pm:epoch:state {phase closed, round_id == it}. -> {round_id, end_ts, why} or None."""
    from primordial.ops import round_clock as RC
    now = time.time() if now is None else now
    rid = r.get(RC.CURRENT)
    if not rid:
        return None
    clock = RC.read(r, rid)                                   # by id: history, never hidden
    st = r.hgetall("pm:epoch:state") or {}
    if clock is not None and clock["end_ts"] < now:
        return {"round_id": rid, "end_ts": clock["end_ts"], "why": "end_ts passed"}
    if st.get("phase") == "closed" and st.get("round_id") == rid:
        return {"round_id": rid, "end_ts": None if clock is None else clock["end_ts"], "why": "epoch state closed"}
    return None


def _prior_closed(r, prior_round: str, now: float) -> tuple[bool, dict | None]:
    from primordial.ops import round_clock as RC
    clock = RC.read(r, prior_round)
    state = r.hgetall("pm:epoch:state") or {}
    if state.get("phase") != "closed" or clock is None:
        return False, clock
    if "round_id" in state:
        return state["round_id"] == prior_round, clock
    return now >= clock["end_ts"] and r.get(RC.CURRENT) == prior_round, clock


def clear(r, prior_round: str, own_pid: int | None = None, round_id: str | None = None, allowed=None,
          now: float | None = None) -> dict:
    """Clear ONLY residue a closed prior round provably left: its stop flags (value == its epoch count) and
    dead consumers with nothing pending. Never kills a process, never touches pm:prior:*. Everything else that
    scan reports is refused NOT_CLEARABLE. One RESIDUE_CLEARED event per key/consumer on pm:events."""
    from primordial.fabric import envelope as EV
    now = time.time() if now is None else now
    cleared, refused = [], []

    def event(rec):
        r.xadd(EV.EVENTS, {"event": "RESIDUE_CLEARED",
                           "json": json.dumps(dict(rec, event="RESIDUE_CLEARED", prior_round=prior_round,
                                                   ts=round(time.time(), 3)), sort_keys=True)})

    closed, clock = _prior_closed(r, prior_round, now)
    expected = None if clock is None else str(int(clock["epochs"]))
    for k in sorted(r.scan_iter("pm:jobs:*:stop")):
        val = r.get(k)
        if not closed:
            refused.append({"kind": "STOP_FLAG", "key": k, "value": val, "reason": "FLAG_ROUND_NOT_CLOSED"})
        elif val != expected:
            refused.append({"kind": "STOP_FLAG", "key": k, "value": val, "expected": expected,
                            "reason": "FLAG_VALUE_MISMATCH"})
        else:
            r.delete(k)
            rec = {"kind": "STOP_FLAG", "key": k, "value": val}
            cleared.append(rec)
            event(rec)
    live, _ = live_registrations(r)
    for lane, key, group, consumers in lane_groups(r):
        for c in consumers:
            name, pending = c.get("name"), int(c.get("pending", 0))
            rec = {"kind": "DEAD_CONSUMER", "key": key, "group": group, "consumer": name, "pending": pending}
            if _bound(live, lane, name):
                refused.append(dict(rec, reason="CONSUMER_LIVE"))
            elif _recently_active(c):
                refused.append(dict(rec, kind="UNREGISTERED_ACTIVE_CONSUMER", idle_ms=c.get("idle"),
                                    reason="CONSUMER_RECENTLY_ACTIVE"))
            elif pending > 0:
                refused.append(dict(rec, reason="CONSUMER_PENDING"))
            else:
                r.xgroup_delconsumer(key, group, name)
                cleared.append(rec)
                event(rec)
    from primordial.ops import round_clock as RC
    cur = current_closed(r, now)
    if cur is not None and cur["round_id"] == prior_round:     # only the prior round's own pointer; the hash stays
        r.delete(RC.CURRENT)
        rec = {"kind": "CURRENT_POINTS_AT_CLOSED_ROUND", "key": RC.CURRENT, "value": prior_round, "why": cur["why"]}
        cleared.append(rec)
        event(rec)
    for item in scan(r, round_id or prior_round, allowed, now)["residue"]:
        if item["kind"] in NOT_CLEARABLE_KINDS:
            refused.append(dict(item, reason="NOT_CLEARABLE"))
    return {"prior_round": prior_round, "cleared": cleared, "refused": refused, "ok": not refused}


def stop_registered(r, round_id: str | None = None, lanes=None, timeout_s: float = 10.0,
                    own_pid: int | None = None) -> list[dict]:
    """Stop exactly the registered, cmdline-verified worker pids (and that worker's own children)."""
    import psutil
    own_pid = os.getpid() if own_pid is None else own_pid
    lanes = None if lanes is None else set(lanes)
    actions = []
    for reg in registrations(r):
        lane, pid = reg.get("lane"), reg["pid"]
        if lanes is not None and lane not in lanes:
            continue
        if round_id is not None and reg.get("round_id") not in (round_id, ""):
            continue
        rec = {"pid": pid, "lane": lane, "key": reg["key"]}
        if pid == own_pid:
            actions.append(dict(rec, action="skipped_own_pid"))
            continue
        alive, argv = _live(pid)
        if not alive:
            r.delete(reg["key"])
            actions.append(dict(rec, action="stale_registration_removed"))
            continue
        if not verify_worker_cmdline(argv, lane):
            actions.append(dict(rec, action="skipped_cmdline_mismatch", argv=argv))
            continue
        try:
            p = psutil.Process(pid)
            procs = [p] + [c for c in p.children(recursive=True) if c.pid != own_pid]
        except psutil.Error:
            r.delete(reg["key"])
            actions.append(dict(rec, action="stale_registration_removed"))
            continue
        for q in procs:
            try:
                q.terminate()
            except psutil.Error:
                pass
        _, still = psutil.wait_procs(procs, timeout=timeout_s)
        for q in still:
            try:
                q.kill()
            except psutil.Error:
                pass
        r.delete(reg["key"])
        actions.append(dict(rec, action="killed" if still else "stopped", children=[q.pid for q in procs[1:]]))
    return actions


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--round", required=True)
    s.add_argument("--allow-repos", "--allowed-repos", dest="allowed_repos", default=None,
                   help="'G=F:/x;B=F:/y' per lane, or a flat comma list for every lane")
    t = sub.add_parser("stop")
    t.add_argument("--round", default=None)
    t.add_argument("--lanes", default=None)
    c = sub.add_parser("clear")
    c.add_argument("--prior-round", required=True)
    c.add_argument("--round", default=None, help="the round about to open (for the NOT_CLEARABLE listing)")
    c.add_argument("--allow-repos", "--allowed-repos", dest="allowed_repos", default=None)
    a = ap.parse_args(argv)
    from primordial.bus import bus
    r = bus.conn()
    if a.cmd == "clear":
        allowed = a.allowed_repos
        rep = clear(r, a.prior_round, round_id=a.round, allowed=allowed)
        print(json.dumps(rep, sort_keys=True, default=str))
        print(f"residue clear {a.prior_round}: cleared {len(rep['cleared'])}, refused {len(rep['refused'])} "
              f"({sorted({x['reason'] for x in rep['refused']})})")
        return 0 if rep["ok"] else 2
    if a.cmd == "scan":
        allowed = a.allowed_repos
        rep = scan(r, a.round, allowed)
        print(json.dumps(rep, sort_keys=True, default=str))
        return 0 if rep["ok"] else 1
    lanes = [x.strip() for x in a.lanes.split(",") if x.strip()] if a.lanes else None
    print(json.dumps(stop_registered(r, a.round, lanes), sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
