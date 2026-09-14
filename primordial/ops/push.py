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

from primordial.fabric.rows import live_writers

INTEGRATION = os.environ.get("PM_INTEGRATION_BRANCH", "nestor/sidequest-graphworld-2026-09-14")
REFUSED, CONFLICT = 3, 4


def _git(repo, *a, timeout=300):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=timeout)


def push(repo=".", remote: str = "origin", branch: str = INTEGRATION, dry: bool = False, log=print) -> int:
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
    if behind:
        log(f"behind {tip}, no live writer: rebasing")
        if not dry:
            rb = _git(repo, "rebase", tip)
            if rb.returncode != 0:
                _git(repo, "rebase", "--abort")
                log(f"CONFLICT: rebase onto {tip} aborted: {(rb.stdout + rb.stderr).strip()[:400]}")
                return CONFLICT
    if dry:
        log(f"dry: would push HEAD -> {tip} (behind={behind}, live={len(live)})")
        return 0
    p = _git(repo, "push", remote, f"HEAD:refs/heads/{branch}")
    log((p.stdout + p.stderr).strip()[-400:] or "pushed")
    return p.returncode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default=INTEGRATION)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    return push(a.repo, a.remote, a.branch, a.dry)


if __name__ == "__main__":
    sys.exit(main())
