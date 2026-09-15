"""O3 (round 3): the integration push, fast-forward only while a RowWriter is live.

A rebase under a live RowWriter wedges it (its periodic commits land on the
pre-rebase HEAD; journal 09-14). So:

  no live writer   fetch; rebase onto the integration tip if behind; push
  live writer      fetch; push only if HEAD already contains the tip; else
                   refuse (exit 3) and name the writers. Never rebases.

Never forces. A rebase conflict is aborted (exit 4) and left to the lane.

    python -m primordial.ops.push                 # HEAD -> origin/<integration>
    python -m primordial.ops.push --dry
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

from primordial.fabric.rows import live_writers

INTEGRATION = os.environ.get("PM_INTEGRATION_BRANCH", "nestor/sidequest-graphworld-2026-09-14")
PUSH_LOCK_TTL_S = 900


def acquire_push_lock(lane: str, wait_s: float, log=print, r=None, poll_s: float = 1.0):
    """Park lane's F7 worker for a rebase (09-15, E: a rebase ran while the epoch controller cleared the
    stop flag; the next checkpointed segment opened its rows file and the rebase pick failed).
    Sets pm:push:lock:<L> (the worker takes no job while it exists; the controller never clears it) and
    waits until the worker is not busy. -> the redis client holding the lock; None when the bus is
    unreachable (rebase proceeds as before); False when the worker stayed busy for wait_s (lock released)."""
    from primordial.fabric.worker import PUSH_LOCK, WSTATE
    try:
        if r is None:
            from primordial.bus import bus
            r = bus.conn()
        r.set(PUSH_LOCK.format(lane), str(os.getpid()), ex=PUSH_LOCK_TTL_S)
    except Exception as e:                                # no bus: keep the old behaviour, say so
        log(f"push lock unavailable ({type(e).__name__}); rebasing without it")
        return None
    end = time.monotonic() + wait_s
    while r.hget(WSTATE.format(lane), "state") == "busy":
        if time.monotonic() >= end:
            r.delete(PUSH_LOCK.format(lane))
            return False
        time.sleep(poll_s)
    return r
REFUSED, CONFLICT = 3, 4


def _git(repo, *a, timeout=300):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=timeout)


def push(repo=".", remote: str = "origin", branch: str = INTEGRATION, dry: bool = False, log=print,
         lock_wait_s: float = 300, lock_redis=None) -> int:
    f = _git(repo, "fetch", "-q", remote, branch)
    if f.returncode != 0:
        log(f"fetch failed: {f.stderr.strip()[:300]}")
        return f.returncode
    tip = f"{remote}/{branch}"
    behind = _git(repo, "merge-base", "--is-ancestor", tip, "HEAD").returncode != 0
    live = live_writers(repo)
    if behind and live:
        names = ", ".join(f"{w.get('exp_id')} (pid {w.get('pid')})" for w in live)
        log(f"REFUSED: HEAD is behind {tip} and {len(live)} RowWriter(s) are live: {names}. "
            f"Fast-forward only while a writer is live; push after it closes.")
        return REFUSED
    if dry:
        log(f"dry: would push HEAD -> {tip} (behind={behind}, live={len(live)})")
        return 0
    lane = os.environ.get("PM_LANE", "") if behind else ""
    lock = acquire_push_lock(lane, lock_wait_s, log, r=lock_redis) if lane else None
    if lock is False:
        log(f"REFUSED: worker {lane} stayed busy for {lock_wait_s:.0f} s; push after its job ends")
        return REFUSED
    try:
        if behind:
            live = live_writers(repo)                     # re-check with the worker parked
            if live:
                names = ", ".join(f"{w.get('exp_id')} (pid {w.get('pid')})" for w in live)
                log(f"REFUSED: {len(live)} RowWriter(s) went live before the rebase: {names}")
                return REFUSED
            log(f"behind {tip}, no live writer" + (f", worker {lane} parked" if lock else "") + ": rebasing")
            rb = _git(repo, "rebase", tip)
            if rb.returncode != 0:
                _git(repo, "rebase", "--abort")
                log(f"CONFLICT: rebase onto {tip} aborted: {(rb.stdout + rb.stderr).strip()[:400]}")
                return CONFLICT
        p = _git(repo, "push", remote, f"HEAD:refs/heads/{branch}")
        log((p.stdout + p.stderr).strip()[-400:] or "pushed")
        return p.returncode
    finally:
        if lock:
            from primordial.fabric.worker import PUSH_LOCK
            lock.delete(PUSH_LOCK.format(lane))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default=INTEGRATION)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--lock-wait-s", type=float, default=300)
    a = ap.parse_args(argv)
    return push(a.repo, a.remote, a.branch, a.dry, lock_wait_s=a.lock_wait_s)


if __name__ == "__main__":
    sys.exit(main())
