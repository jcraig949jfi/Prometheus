"""Workspace invariant guard for PEW (operator D-23, 2026-09-11).

The canonical checkout F:\\Prometheus is read-mostly. No PEW entry point may
run from it: not the service, not the backup/restore jobs, not the indexer.
The detection carries no path assumption -- in the repository's MAIN worktree
`git rev-parse --git-dir` and `--git-common-dir` resolve to the same
directory; in a linked worktree they do not. Same check as
archaeon/workspace.py, deliberately, so the two cannot drift into disagreeing
about what "canonical" means.

Why PEW cares more than most: the service is a LONG-RUNNING process. A
mutating git operation under a running service swaps files beneath it, and the
canonical checkout has already lost ~11,000 tracked files twice. PEW's own
durability work is worthless if its code can be rewritten mid-write.

Override: EW_ALLOW_CANONICAL=1 for READ-ONLY inspection only. It is recorded
in the receipt whenever used, so an override never becomes invisible.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent          # evidence_wiki/


class CanonicalCheckoutRefused(RuntimeError):
    """Raised when a PEW entry point is started from the canonical checkout."""


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or ROOT),
                              capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:                                   # noqa: BLE001
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    cwd = path or ROOT
    gd, cd = _git("rev-parse", "--git-dir", cwd=cwd), _git(
        "rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False                                    # not a repo: not canonical
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty -- what every receipt carries."""
    cwd = path or ROOT
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no",
                           cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "allow_canonical_override": os.environ.get("EW_ALLOW_CANONICAL") == "1",
    }


def assert_not_canonical(purpose: str = "work", *, path: Optional[Path] = None):
    """Refuse to run from the canonical checkout. Returns the receipt."""
    r = receipt(path)
    if r["main_worktree"] and not r["allow_canonical_override"]:
        raise CanonicalCheckoutRefused(
            f"PEW refuses to {purpose} from the CANONICAL checkout "
            f"({r['worktree_path']}). D-23: the canonical clone is read-mostly. "
            "Work from a worktree:\n"
            "  git -C F:\\Prometheus fetch origin\n"
            "  git -C F:\\Prometheus worktree add "
            "F:\\Prometheus-worktrees\\mnemosyne-<task> -b mnemosyne/<task> "
            "origin/main\n"
            "Long-running PEW processes run from the PINNED worktree "
            "F:\\Prometheus-worktrees\\mnemosyne-pew, detached at a recorded "
            "SHA. Set EW_ALLOW_CANONICAL=1 only for read-only inspection.")
    return r
