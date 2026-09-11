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

#: Path fragments that mark a SESSION-TEMPORARY directory. Rule 2 forbids a
#: worktree there for anything that outlives the session, and the danger is
#: that such a directory is REMOVED rather than corrupted -- so the failure is
#: a process whose code disappears under it, not a merge conflict.
_TEMP_MARKERS = ("\\temp\\", "/temp/", "\\tmp\\", "/tmp/",
                 "scratchpad", "appdata\\local\\temp")


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


def canonical_root(path: Optional[Path] = None) -> Optional[Path]:
    """The canonical checkout's directory, derived and never hardcoded.

    `--git-common-dir` resolves to <canonical>/.git from ANY worktree, so its
    parent is the canonical checkout wherever the repository lives. Deriving it
    is what makes the two checks below survive a clone, another machine, and
    the day somebody moves it.
    """
    cd = _git("rev-parse", "--path-format=absolute", "--git-common-dir",
              cwd=path or REPO)
    if not cd:
        return None
    try:
        return Path(cd).resolve().parent
    except OSError:                                      # pragma: no cover
        return None


def inside_canonical_checkout(path: Optional[Path] = None) -> bool:
    """A LINKED worktree placed underneath the canonical checkout.

    THE HOLE TECHNE FOUND, and it is the half a copied guard passes. Such a
    worktree reports `main_worktree` FALSE -- it genuinely is a linked worktree
    -- so the canonical check clears it every time, while the files sit inside
    the directory that has twice lost ~11,000 tracked files to a concurrent
    working-tree rewrite. Rule 2 forbids it; `main_worktree` cannot see it.
    """
    root = canonical_root(path)
    here = Path(path or REPO).resolve()
    if root is None:
        return False
    if here == root:
        return False                 # that is the canonical checkout itself
    try:
        here.relative_to(root)
        return True
    except ValueError:
        return False


def session_temporary(path: Optional[Path] = None) -> bool:
    """A worktree under a temp or agent-scratchpad directory.

    Also Techne's finding, from the other side: their worktree was under a
    session scratchpad, `main_worktree` was false throughout, and the guard
    cleared them while the work sat somewhere that gets DELETED. For a
    long-lived process that is worse than corruption -- the code vanishes
    underneath a running interpreter holding a claimed row.
    """
    here = str(Path(path or REPO).resolve()).lower()
    return any(m in here for m in _TEMP_MARKERS)


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
        # Rule 2, the two conditions `main_worktree` cannot see. Reported on
        # EVERY receipt, because a violation that is only checked at one entry
        # point is invisible in the record of everything else.
        "inside_canonical_checkout": inside_canonical_checkout(cwd),
        "session_temporary_worktree": session_temporary(cwd),
        "durable_worktree": not (is_main_worktree(cwd)
                                 or inside_canonical_checkout(cwd)
                                 or session_temporary(cwd)),
        "allow_canonical_override": os.environ.get(OVERRIDE_ENV) == "1",
    }


def assert_durable_worktree(purpose: str = "run") -> Dict[str, Any]:
    """Rule 2 + rule 6: a LONG-LIVED process needs a durable worktree.

    Refuses all three placements, not just the canonical checkout: the main
    worktree, a linked worktree underneath it, and a session-temporary path.
    The last two both report `main_worktree: false`, which is exactly why
    `assert_not_canonical` alone is not enough for a process that outlives the
    session that started it.

    There is no override. A consumer holding a global execution slot, writing
    to the durable register, running from a directory that can be rewritten or
    deleted underneath it is the failure this whole invariant exists to
    prevent, and an override would be a hole with a polite name.
    """
    r = receipt()
    if r["durable_worktree"]:
        return r
    if r["main_worktree"]:
        why = "this IS the canonical checkout"
    elif r["inside_canonical_checkout"]:
        why = ("this is a linked worktree UNDERNEATH the canonical checkout "
               "(%s). It reports main_worktree false and is still inside the "
               "directory that has twice lost ~11,000 tracked files"
               % canonical_root())
    else:
        why = ("this is a SESSION-TEMPORARY path. It is removed when the "
               "session ends, and a long-lived process whose code is deleted "
               "underneath it leaves a claimed row with no worker")
    raise CanonicalCheckoutRefused(
        "D-23 rule 2/6: refusing to %s from %s -- %s.\n"
        "A long-lived process runs from a PINNED, DETACHED worktree:\n"
        "  git -C %s worktree add --detach "
        "F:\\Prometheus-worktrees/vivarium-<process> <sha>\n"
        "There is no override for this one."
        % (purpose, r["worktree_path"], why, canonical_root() or REPO))


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
