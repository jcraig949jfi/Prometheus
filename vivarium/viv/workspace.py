"""D-23: no seat does mutating work from the canonical checkout.

WHY THIS EXISTS. `F:\\Prometheus` has twice lost ~11,000 tracked files from
disk with HEAD and index intact and nothing staged -- the signature of an
interrupted or concurrent working-tree rewrite, not of a deletion. Several
seats run long-lived processes from worktrees inside it. Sharing a repository
is safe; sharing a mutable working directory is not.

THE DETECTION IS PATH-FREE, and that is the point. `git rev-parse --git-dir`
and `--git-common-dir` return the same directory ONLY in a repository's main
worktree; a linked worktree's git-dir lives under `<common>/worktrees/<name>`,
so the two answers differ there. A check written against `F:\\Prometheus` as a
string would pass on a clone, on another machine, and on the day somebody moves
the canonical checkout -- which is exactly when it needs to hold.

This is Archaeon's `archaeon/workspace.py` check, copied as the missive
instructs rather than reimplemented, so the two seats cannot drift on what
"canonical" means. The override is READ-ONLY by intent, is recorded in the
receipt when used, and does NOT unlock the consumer: a seat that writes to the
production register from the canonical checkout is the case this exists to
prevent, and an override that could permit it would be a hole with a polite
name.

VIVARIUM'S SPECIFIC EXPOSURE. The consumer is a LONG-LIVED process holding a
single global execution slot. If it runs from a working directory another seat
can rewrite underneath it, then a file vanishing mid-run is not a tidy crash --
it is a claimed row with no worker, which this seat refuses to adopt on
principle. Rule 6 puts it in a pinned worktree checked out DETACHED at a
recorded SHA, and `viv.cli run` records that SHA on every start.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

REPO = Path(__file__).resolve().parents[2]

#: Read-only inspection only. Never unlocks `run`.
OVERRIDE_ENV = "VIV_ALLOW_CANONICAL"


class CanonicalCheckoutRefused(RuntimeError):
    """This entry point will not run from the repository's main worktree."""


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or REPO),
                              capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:                                    # noqa: BLE001
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` sits in the repository's MAIN worktree.

    False when git is unavailable or the answer cannot be obtained. That
    direction is deliberate: an unanswerable question must not become a
    refusal that stops a consumer from starting, and the receipt records the
    uncertainty instead.
    """
    cwd = path or REPO
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False
    try:
        return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()
    except OSError:                                      # pragma: no cover
        return False


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty -- what every receipt carries.

    `detached` is reported separately from `branch` because rule 6 requires a
    long-lived process to run DETACHED at a pinned SHA, and "HEAD" as a branch
    name is easy to read past.
    """
    cwd = path or REPO
    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": branch,
        "detached": branch == "HEAD",
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no",
                           cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "allow_canonical_override": os.environ.get(OVERRIDE_ENV) == "1",
    }


def assert_not_canonical(purpose: str = "work", *,
                         allow_override: bool = True) -> Dict[str, Any]:
    """Refuse `purpose` from the canonical checkout. Returns the receipt."""
    r = receipt()
    if r["main_worktree"] and not (allow_override
                                   and r["allow_canonical_override"]):
        raise CanonicalCheckoutRefused(
            "D-23: refusing to %s from the CANONICAL checkout (%s).\n"
            "That directory is read-mostly: fetch, inspection and worktree "
            "management only. It has twice lost ~11,000 tracked files from "
            "disk to a concurrent working-tree rewrite, and this seat's "
            "consumer holds a global execution slot -- a file vanishing "
            "mid-run leaves a claimed row with no worker.\n"
            "  git -C %s fetch origin\n"
            "  git -C %s worktree add F:\\\\Prometheus-worktrees/vivarium-<task> "
            "-b vivarium/<task> origin/main\n"
            "and work there. %s=1 permits READ-ONLY inspection and never `run`."
            % (purpose, r["worktree_path"], REPO, REPO, OVERRIDE_ENV))
    return r
