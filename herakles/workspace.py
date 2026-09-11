"""Workspace invariant for the Herakles seat (operator 2026-09-11, D-23).

The check is COPIED from `archaeon/workspace.py`, as the missive instructs,
rather than reinvented: the canonical checkout is the repository's MAIN
worktree, and it is detectable with no path assumption because there
`git rev-parse --git-dir` and `--git-common-dir` resolve to the same
directory. In a linked worktree they differ.

WHY A SEPARATE MODULE RATHER THAN IMPORTING ARCHAEON'S. `herakles/evca` is a
pure library that another seat's executor wraps, and it must not acquire a
dependency on a third seat's package to do so. The check is eleven lines; the
coupling would be permanent. If the detection rule ever changes, both copies
change and a test in each seat catches the drift.

WHAT IS GUARDED. Only entry points that WRITE. Four of them:

    herakles/evca/tools/make_golden.py      regenerates the golden fixture
    herakles/evca/c1e/run_c1e.py            the historical reproduction run
    herakles/evca/c1e/compare_c3_2.py       writes the comparison result
    herakles/ca_stream/run_alpha.py         writes the alpha results

WHAT IS DELIBERATELY NOT GUARDED, and why. `herakles/evca/c3_null_check.py`
writes nothing and is run by ANOTHER SEAT against live rows. Adding a refusal
there would block Archaeon from a read-only diagnostic for a reason that has
nothing to do with them. A pure reader cannot corrupt a working tree, which is
the thing the invariant protects.

The libraries themselves -- `core.py`, `genomes.py`, `reset_v2.py` -- are not
guarded either. They are imported, not run, they perform no I/O at all, and a
guard on an import would fire inside a wrapper executing in a legitimate
worktree.

    HERAKLES_ALLOW_CANONICAL=1   read-only override, recorded in the receipt.
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
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or REPO),
                              capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` is inside the repository's MAIN worktree.

    A linked worktree's git-dir lives under <common>/worktrees/<name>, so the
    two answers differ there. No path is assumed and no directory name is
    matched, because a rule that keys on "F:/Prometheus" breaks the moment the
    clone moves.
    """
    cwd = path or REPO
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path and dirtiness. What a receipt carries."""
    cwd = path or REPO
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no",
                           cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "allow_canonical_override":
            os.environ.get("HERAKLES_ALLOW_CANONICAL") == "1",
    }


def assert_not_canonical(purpose: str = "work", *,
                         allow_override: bool = True) -> Dict[str, Any]:
    """Refuse to do `purpose` from the canonical checkout.

    Returns the workspace receipt when allowed, so a caller can record it
    without a second call.
    """
    r = receipt()
    if r["main_worktree"] and not (allow_override
                                   and r["allow_canonical_override"]):
        raise CanonicalCheckoutRefused(
            "refusing to %s from the canonical checkout %s (the repository's "
            "main worktree). Work from a linked worktree:\n"
            "    git -C <canonical> worktree add "
            "F:/Prometheus-worktrees/herakles-<task> -b herakles/<task> "
            "origin/main\n"
            "(D-23, 2026-09-11)." % (purpose, r["worktree_path"]))
    return r
