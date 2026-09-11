"""Workspace invariant (operator 2026-09-11, D-23).

* No seat runs mutating work from the CANONICAL checkout. The canonical
  checkout is the repository's MAIN worktree, detectable without any path
  assumption: there, `git rev-parse --git-dir` equals `--git-common-dir`.
  In a linked worktree they differ.
* Every receipt records base_sha, branch, worktree_path and dirtiness.

`assert_not_canonical()` is called by Archaeon's entry points (the tick
loop, the campaign CLIs, the queue writer). The override
ARCHAEON_ALLOW_CANONICAL=1 exists for READ-ONLY inspection only and is
recorded in the receipt when used; it does not unlock queue writes.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

REPO = Path(__file__).resolve().parents[1]


class CanonicalCheckoutRefused(RuntimeError):
    pass


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd or REPO), capture_output=True, text=True, timeout=30).stdout.strip()


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` is inside the repository's MAIN worktree (the
    canonical checkout). A linked worktree's git-dir lives under
    <common>/worktrees/<name>, so the two answers differ there."""
    cwd = path or REPO
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty -- what every receipt carries."""
    cwd = path or REPO
    sha = _git("rev-parse", "HEAD", cwd=cwd)
    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no", cwd=cwd))
    return {"base_sha": sha, "branch": branch, "worktree_path": str(Path(cwd).resolve()),
            "dirty": dirty, "main_worktree": is_main_worktree(cwd),
            "allow_canonical_override": os.environ.get("ARCHAEON_ALLOW_CANONICAL") == "1"}


def assert_not_canonical(purpose: str = "work", *, allow_override: bool = True) -> Dict[str, Any]:
    """Refuse to do `purpose` from the canonical checkout. Returns the
    workspace receipt when allowed."""
    r = receipt()
    if r["main_worktree"] and not (allow_override and r["allow_canonical_override"]):
        raise CanonicalCheckoutRefused(
            "refusing to {} from the canonical checkout {} (the repository's main worktree). "
            "Work from a linked worktree: git -C <canonical> worktree add <path> -b <seat>/<task> origin/main "
            "(D-23, 2026-09-11).".format(purpose, r["worktree_path"]))
    return r
