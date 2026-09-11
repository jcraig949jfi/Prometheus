"""Workspace invariant for Proteus (operator 2026-09-11, D-23).

The canonical checkout `F:\\Prometheus` is read-mostly. No Proteus entry point may run mutating
work from it, and every receipt records where it ran.

DETECTION USES NO PATH ASSUMPTION. The canonical checkout is the repository's MAIN worktree, and
there `git rev-parse --git-dir` equals `--git-common-dir`; in a linked worktree they differ. A
path test would break the moment the clone moved, so this asks git.

WHY PROTEUS CARES PARTICULARLY. This seat has now twice observed the failure the invariant exists
to prevent: a working tree reporting thousands of tracked files missing with HEAD and index intact
and nothing staged. On 2026-09-11 that was 11,134 files. Both times nothing was lost, because
nothing was staged and every Proteus commit names explicit paths -- but the second occurrence is
what turned a nuisance into an ecosystem rule. `git restore .` repaired it; under D-23 rule 7
that counts as a DIAGNOSTIC, and the workflow is to destroy the worktree and recreate it from a
recorded base SHA.

THE OVERRIDE IS FOR READ-ONLY INSPECTION ONLY. `PROTEUS_ALLOW_CANONICAL=1` lets a human look at
something from the canonical checkout; it is recorded in the receipt whenever it is used, so a
run that took it is never mistaken for a run that did not.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OVERRIDE_ENV = "PROTEUS_ALLOW_CANONICAL"
INVARIANT = "D-23 (operator 2026-09-11)"


class CanonicalCheckoutRefused(RuntimeError):
    """Raised when a Proteus entry point is started from the canonical checkout."""


def _git(*args, cwd=None):
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or REPO), capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):       # pragma: no cover - no git, no claim
        return ""


def is_main_worktree(path=None) -> bool:
    """True iff `path` sits in the repository's MAIN worktree (the canonical checkout).

    Returns False when git cannot answer. A guard that cannot tell must not block work; the
    failure mode to avoid is refusing every run on a machine without git, not a missed refusal.
    """
    cwd = path or REPO
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def receipt(path=None) -> dict:
    """base_sha, branch, worktree_path, dirty -- what D-23 rule 4 requires on every receipt."""
    cwd = path or REPO
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no", cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "allow_canonical_override": os.environ.get(OVERRIDE_ENV) == "1",
        "invariant": INVARIANT,
    }


def assert_not_canonical(purpose="work", *, allow_override=True) -> dict:
    """Refuse to do `purpose` from the canonical checkout. Returns the workspace receipt."""
    r = receipt()
    if r["main_worktree"] and not (allow_override and r["allow_canonical_override"]):
        raise CanonicalCheckoutRefused(
            f"Proteus refuses to {purpose} from the canonical checkout "
            f"{r['worktree_path']} (the repository's main worktree). Work from a linked "
            f"worktree:\n"
            f"    git -C <canonical> fetch origin\n"
            f"    git -C <canonical> worktree add "
            f"<path>/proteus-<task> -b proteus/<task> origin/main\n"
            f"{INVARIANT}. Set {OVERRIDE_ENV}=1 only for read-only inspection.")
    return r
