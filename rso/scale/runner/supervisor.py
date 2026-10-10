"""The host supervisor (C-013-T022): drives the run to completion, one worker process at a time, and owns nothing
the next supervisor cannot rebuild from the run directory.

    single supervisor per run (SUPERVISOR.json; a dead holder is replaced at once on its host)
    loop: every chain COMPLETE -> FINAL_ACCOUNT.json, exit COMPLETE
          any chain HALTED     -> exit HALTED (a disagreement waits for a resolver; never retried into agreement)
          a live lease on the next chain (an orphan worker of a killed supervisor) -> wait for it, spawn nothing
          otherwise spawn `python -m rso.scale.runner work <run_dir> <chain>`; on its exit, record and repeat
At most two processes on the host (supervisor + one worker; harry1 thermal limit, escalation response).

launch_detached() starts a supervisor that does not belong to the caller: through an intermediary process that
exits at once (the supervisor is orphaned, outside the caller's process tree), detached from its console, in a new
process group, and on Windows broken away from the caller's job object when the job allows it. The launching
session can then end, or be killed, without touching the job.
"""
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

from rso.scale.runner import account as A
from rso.scale.runner import engine as E
from rso.scale.runner import lease as L
from rso.scale.runner import run as RUN
from rso.scale.runner import store as S
from rso.scale.runner import worker as W

NT = os.name == "nt"
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
CREATE_NO_WINDOW = 0x08000000
HEARTBEAT_STALE_S = 120


def sdir(run_dir):
    return os.path.join(run_dir, "supervisor")


def sup_event(run_dir, row):
    S.append_jsonl(os.path.join(sdir(run_dir), "events.jsonl"),
                   dict(row, host=S.HOST, pid=os.getpid(), at_utc=RUN.utc_now()))


def _lock(run_dir):
    return S.FileLock(os.path.join(sdir(run_dir), ".supervisor.lock"))


def _path(run_dir):
    return os.path.join(sdir(run_dir), "SUPERVISOR.json")


def _live(cur):
    if not cur:
        return False
    if cur["host"] == S.HOST:
        return S.pid_alive(cur["pid"], cur.get("create_time"))
    return time.time() - cur["heartbeat_at"] < HEARTBEAT_STALE_S


def acquire_supervisor(run_dir):
    with _lock(run_dir):
        p = _path(run_dir)
        cur = S.read_json(p) if os.path.exists(p) else None
        if _live(cur):
            return None
        tok = uuid.uuid4().hex
        S.atomic_write_json(p, dict(S.my_identity(), token=tok, started_at=time.time(), heartbeat_at=time.time(),
                                    previous=cur and {k: cur.get(k) for k in ("token", "pid", "host")}))
        return tok


def _heartbeat(run_dir, tok):
    with _lock(run_dir):
        cur = S.read_json(_path(run_dir))
        if cur["token"] != tok:
            return False
        cur["heartbeat_at"] = time.time()
        S.atomic_write_json(_path(run_dir), cur)
        return True


def release_supervisor(run_dir, tok):
    with _lock(run_dir):
        p = _path(run_dir)
        if os.path.exists(p) and S.read_json(p)["token"] == tok:
            os.remove(p)


def guard_code_root(code_root):
    """WORKING_CONTRACT s1/s6: never run from the canonical checkout; "cannot tell" fails closed (ARCH-52)."""
    from archaeon import workspace as WS
    root = Path(code_root)
    if not WS.workspace_known(root) or WS.is_main_worktree(root):
        raise SystemExit("refusing: {} is the canonical checkout or not a known git worktree".format(code_root))


def _spawn_worker(run_dir, chain_id, n, code_root):
    os.makedirs(os.path.join(sdir(run_dir), "logs"), exist_ok=True)
    log = open(os.path.join(sdir(run_dir), "logs", "worker-{}-{:03d}.log".format(chain_id, n)), "ab")
    kw = {"creationflags": CREATE_NO_WINDOW} if NT else {}
    p = subprocess.Popen([sys.executable, "-m", "rso.scale.runner", "work", run_dir, chain_id], cwd=code_root,
                         stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, **kw)
    log.close()
    return p


def _starts(run_dir, chain_id):
    rows, _ = S.read_jsonl(os.path.join(sdir(run_dir), "events.jsonl"))
    return sum(1 for r in rows if r.get("kind") == "WORKER_SPAWN" and r.get("chain_id") == chain_id)


def supervise(run_dir, poll_s=0.5, code_root=E.REPO):
    tok = acquire_supervisor(run_dir)
    if tok is None:
        return {"state": "SUPERVISOR_HELD"}
    m, mid = RUN.load_manifest(run_dir)
    max_starts = m["stop_rules"]["max_worker_starts_per_chain"]
    sup_event(run_dir, {"kind": "SUPERVISOR_START", "manifest_id": mid, "code_root": code_root})
    worker, last_beat = None, 0.0

    def stop(state, **extra):
        sup_event(run_dir, dict(extra, kind="SUPERVISOR_END", state=state))
        release_supervisor(run_dir, tok)
        return dict(extra, state=state)

    while True:
        if time.time() - last_beat > 2.0:
            if not _heartbeat(run_dir, tok):
                return {"state": "SUPERVISOR_REPLACED"}
            last_beat = time.time()
        if worker is not None:
            proc, chain_id = worker
            rc = proc.poll()
            if rc is None:
                time.sleep(poll_s)
                continue
            sup_event(run_dir, {"kind": "WORKER_EXIT" if rc in (0, 3) else "WORKER_LOST", "chain_id": chain_id,
                                "worker_pid": proc.pid, "returncode": rc})
            worker = None
            if rc == W.EXIT["INVALID"]:
                return stop("BLOCKED", chain_id=chain_id, reason="resume INVALID (s3.8 checks 1/2/4)")
            if rc == W.EXIT["CAP_REFUSED"]:
                return stop("CAP_REFUSED", chain_id=chain_id)
        heads = {c: RUN.head(run_dir, c) for c in RUN.chain_ids(m)}
        states = {h["state"] for h in heads.values()}
        if states == {RUN.COMPLETE}:
            acct = A.final_account(run_dir, write=True)
            return stop("COMPLETE", run_digest=acct["run_digest"])
        if RUN.HALTED in states:
            return stop("HALTED", chains=[c for c, h in heads.items() if h["state"] == RUN.HALTED])
        chain_id = next(c for c, h in heads.items() if h["state"] == RUN.OPEN)
        holder = L.live_holder(run_dir, chain_id)
        if holder is not None:                                  # an orphan worker is still running: let it finish
            time.sleep(poll_s)
            continue
        n = _starts(run_dir, chain_id)
        if n >= max_starts:
            return stop("BLOCKED", chain_id=chain_id, reason="max_worker_starts_per_chain reached")
        proc = _spawn_worker(run_dir, chain_id, n + 1, code_root)
        sup_event(run_dir, {"kind": "WORKER_SPAWN", "chain_id": chain_id, "worker_pid": proc.pid, "n": n + 1})
        worker = (proc, chain_id)


def _detach_kwargs(breakaway=True):
    if NT:
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | (CREATE_BREAKAWAY_FROM_JOB if breakaway else 0)
        return {"creationflags": flags}
    return {"start_new_session": True}


def _popen_detached(args, cwd, stdout):
    try:
        return subprocess.Popen(args, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=subprocess.STDOUT,
                                close_fds=True, **_detach_kwargs(True)), True
    except OSError:                                             # the job forbids breakaway: detach without it
        return subprocess.Popen(args, cwd=cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=subprocess.STDOUT,
                                close_fds=True, **_detach_kwargs(False)), False


def spawn_supervisor(run_dir, code_root=E.REPO):
    """Intermediary: start the supervisor detached, record it, exit (so the supervisor has no living parent)."""
    os.makedirs(os.path.join(sdir(run_dir), "logs"), exist_ok=True)
    log = open(os.path.join(sdir(run_dir), "logs", "supervisor-{}.log".format(int(time.time()))), "ab")
    p, breakaway = _popen_detached([sys.executable, "-m", "rso.scale.runner", "supervise", run_dir], code_root, log)
    rec = {"supervisor_pid": p.pid, "intermediary_pid": os.getpid(), "breakaway_from_job": breakaway,
           "code_root": code_root, "at_utc": RUN.utc_now()}
    S.atomic_write_json(os.path.join(sdir(run_dir), "LAUNCH.json"), rec)
    sup_event(run_dir, dict(rec, kind="LAUNCH"))
    return rec


def launch_detached(run_dir, code_root=E.REPO, timeout=60):
    guard_code_root(code_root)
    run_dir = os.path.abspath(run_dir)
    p, _ = _popen_detached([sys.executable, "-m", "rso.scale.runner", "_spawn", run_dir], code_root,
                           subprocess.DEVNULL)
    p.wait(timeout)
    return S.read_json(os.path.join(sdir(run_dir), "LAUNCH.json"))
