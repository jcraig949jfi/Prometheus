"""D-23 startup refusal for Harmonia's entry points.  2026-09-11.

Copied from `archaeon/workspace.py` per the missive, deliberately rather than
imported: a guard that fails because another seat's module moved is a guard
that fails open on the day it matters.

WHY THESE TOOLS IN PARTICULAR. Harmonia's contract tools are run BY OTHER SEATS
-- Archaeon and Vivarium call `conformance_check.py` before a batch, and
`generate_sfe_contract.py` WRITES four files. If another seat runs them from
the canonical checkout, the write lands in the shared mutable working directory
that D-23 exists to protect. The refusal therefore belongs on my tools even
though the caller is not me.

THE DETECTION. A linked worktree's git-dir lives under
<common>/worktrees/<name>, so `git rev-parse --git-dir` and `--git-common-dir`
resolve to the same path ONLY in the main worktree.

NOT A PATH-STRING TEST. An earlier version of my own audit tested the string
from `pwd`, which under Git Bash is the MSYS-mapped path and not the real one,
so it answered "no" for a directory that plainly was one. Resolve the paths and
compare them; never match on a prefix.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class CanonicalCheckoutRefused(RuntimeError):
    """Raised when an entry point is invoked from the canonical checkout."""


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or Path.cwd()),
                              capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:                                              # noqa: BLE001
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` is inside the repository's MAIN worktree."""
    cwd = path or Path.cwd()
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False           # not a repo at all: not the canonical checkout
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty -- what every receipt carries."""
    cwd = path or Path.cwd()
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no", cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "session_temp": any(s in str(Path(cwd).resolve()).replace("\\", "/").lower()
                            for s in ("appdata/local/temp", "/temp/claude")),
    }


def assert_not_canonical(purpose: str = "work") -> Dict[str, Any]:
    """Refuse `purpose` from the canonical checkout. Returns the receipt."""
    r = receipt()
    if r["main_worktree"] and os.environ.get("HARMONIA_ALLOW_CANONICAL") != "1":
        raise CanonicalCheckoutRefused(
            "refusing to {} from the canonical checkout {} (the repository's "
            "main worktree). D-23: work from a linked worktree --\n"
            "  git -C F:/Prometheus worktree add "
            "F:/Prometheus-worktrees/<seat>-<task> -b <seat>/<task> origin/main"
            .format(purpose, r["worktree_path"]))
    return r
