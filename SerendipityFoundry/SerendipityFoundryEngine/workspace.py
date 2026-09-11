"""Workspace invariant D-23, engine side (operator 2026-09-11).

Refuses to run engine entry points from the CANONICAL checkout, and supplies
the workspace receipt every other receipt now has to carry.

WHY THIS FILE IS NOT IN `sfe/`. `engine_source_hash` is computed over sorted
`sfe/*.py` (sfe/release.py), so a module placed there would change the BUILD
IDENTITY of every engine that imports it -- a hygiene guard would have forced a
redeploy and invalidated a contract pinned to the running hash. It lives beside
serve.py instead, where it guards without being part of what it guards.

WHY THE ENGINE'S CASE IS NOT ARCHAEON'S CASE. Archaeon's guard stops mutating
WORK in the canonical checkout. The engine's problem is larger and quieter: the
SFE service has been running out of the canonical checkout with its LEDGER
inside it, and `var/` is gitignored -- so `git status` on that directory reports
clean while it holds the live database, every blob, the only rollback snapshot
and the only copy of the TLS private key. D-23 rule 7 says destroy a corrupt
worktree rather than nurse it. Applied there, "destroy" would take all of that
with it, and nothing in git would have hinted it was at risk.

So this module refuses two distinct things:
  * running an entry point from the canonical checkout at all, and
  * serving a DATABASE that lives inside the canonical checkout, even when the
    code is properly outside it -- because that is the half-move that looks
    compliant and keeps the whole hazard.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

HERE = Path(__file__).resolve().parent


class CanonicalCheckoutRefused(RuntimeError):
    pass


class DataInsideCanonicalCheckout(RuntimeError):
    pass


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or HERE),
                              capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` sits in the repository's MAIN worktree.

    Detected without any path assumption: a linked worktree's git-dir lives
    under <common>/worktrees/<name>, so the two answers differ there. Hard-
    coding "F:/Prometheus" would be a check that a second canonical clone
    somewhere else would silently pass.
    """
    cwd = path or HERE
    gd, cd = _git("rev-parse", "--git-dir", cwd=cwd), \
        _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False          # not a repo at all: not the canonical checkout
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def canonical_root() -> Optional[Path]:
    """The canonical checkout's top level, or None if this is not a repo."""
    cd = _git("rev-parse", "--git-common-dir")
    if not cd:
        return None
    return Path(HERE, cd).resolve().parent


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty -- what D-23 rule 4 requires."""
    cwd = path or HERE
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no",
                           cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "allow_canonical_override":
            os.environ.get("SFE_ALLOW_CANONICAL") == "1",
    }


def assert_not_canonical(purpose: str = "run") -> Dict[str, Any]:
    """Refuse `purpose` from the canonical checkout. Returns the receipt."""
    r = receipt()
    if r["main_worktree"] and not r["allow_canonical_override"]:
        raise CanonicalCheckoutRefused(
            "D-23: refusing to %s from the CANONICAL checkout (%s).\n"
            "  The canonical clone is read-mostly: fetch, inspection and "
            "worktree management only.\n"
            "  Work from a linked worktree instead:\n"
            "    git -C %s fetch origin\n"
            "    git -C %s worktree add F:\\Prometheus-worktrees\\daedalus-<task>"
            " -b daedalus/<task> origin/main\n"
            "  Read-only inspection override: SFE_ALLOW_CANONICAL=1 (recorded "
            "in the receipt; it does not make a write safe)."
            % (purpose, r["worktree_path"], r["worktree_path"],
               r["worktree_path"]))
    return r


def assert_data_outside_canonical(db_path: str) -> None:
    """Refuse to serve a ledger that lives inside the canonical checkout.

    THIS IS THE ONE THAT MATTERS. Moving only the CODE out satisfies a reading
    of D-23 and leaves the entire hazard: the database would still sit in a
    directory that has twice lost ~11,000 files and that the invariant tells
    people to destroy rather than nurse -- and because `var/` is gitignored, no
    git command would ever mention it was there.
    """
    root = canonical_root()
    if root is None:
        return
    db = Path(db_path).resolve()
    try:
        db.relative_to(root)
    except ValueError:
        return                                        # outside: fine
    raise DataInsideCanonicalCheckout(
        "D-23: refusing to serve a database inside the CANONICAL checkout.\n"
        "  db   : %s\n  canonical: %s\n"
        "  `var/` is gitignored, so `git status` there reports clean while it "
        "holds the live ledger, the blobs, the rollback snapshot and the TLS "
        "private key. Rule 7 (destroy, do not nurse) applied to that directory "
        "would take all of it, and nothing in git would have warned anyone.\n"
        "  Move the data OUT of the repository entirely -- it is not source, "
        "and it must outlive any worktree.\n"
        "  Override for a throwaway ledger only: SFE_ALLOW_CANONICAL=1."
        % (db, root))


def guard(purpose: str = "run", db_path: Optional[str] = None
          ) -> Dict[str, Any]:
    """Both refusals plus the receipt, for an entry point's first line."""
    r = assert_not_canonical(purpose)
    if db_path and not r["allow_canonical_override"]:
        assert_data_outside_canonical(db_path)
    return r
