"""Workspace invariant for Techne (operator 2026-09-11, D-23).

The check is ARCHAEON'S and is copied on their instruction ("copy the check"),
not re-derived: the canonical checkout is the repository's MAIN worktree, and it
is detectable without any path assumption because there `git rev-parse --git-dir`
equals `--git-common-dir`, while in a linked worktree they differ. A path-based
test would have to know a drive letter, which is exactly the portability defect
this seat is supposed to catch in other people's code.

WHAT THIS SEAT ADDS, BECAUSE ITS FAILURE MODE IS DIFFERENT. Archaeon's risk is
writing to the canonical checkout. Techne's entry points mostly INSTALL, BUILD
and RUN THIRD-PARTY BINARIES, so there is a second thing worth refusing and a
third worth recording:

  * a SESSION-TEMPORARY worktree. Rule 2 forbids a worktree under a session
    scratchpad for anything that outlives the session, and every receipt this
    seat writes outlives the session by construction -- that is what a receipt
    is for. I was in violation of this myself on 2026-09-11: my worktree lived
    under the agent scratchpad. `is_session_temporary()` names it so the next
    occurrence is caught by a check rather than by reading a missive.
  * the TOOL CACHE is not in the repository at all. It is host-local and
    gitignored, so a workspace receipt that recorded only base_sha would imply a
    reproducibility this seat does not have. The receipt carries the cache root
    and says it is unversioned.

THE OVERRIDE IS READ-ONLY, and it is recorded whenever it is used. It does not
unlock an install, a build, or anything that writes to the tool cache.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

REPO = Path(__file__).resolve().parents[1]

#: Markers of a path the agent harness hands out per session. A worktree under
#: one of these is destroyed when the session ends; work committed from it is
#: safe only because it was pushed, which is not a property to rely on.
_SESSION_TEMP_MARKERS = ("/appdata/local/temp/", "\\appdata\\local\\temp\\",
                         "/scratchpad/", "\\scratchpad\\")


class CanonicalCheckoutRefused(RuntimeError):
    pass


def _git(*args: str, cwd: Optional[Path] = None) -> str:
    """Empty string on any failure, INCLUDING a cwd that does not exist. Every
    caller below documents None or False as its answer when git cannot speak, and
    a helper that raises instead would make those docstrings false -- which is the
    defect class this seat spent the day on."""
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or REPO),
                              capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` is inside the repository's MAIN worktree (the canonical
    checkout). Archaeon's test, verbatim in behaviour: a linked worktree's
    git-dir lives under <common>/worktrees/<name>, so the two answers differ."""
    cwd = path or REPO
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def canonical_root(path: Optional[Path] = None) -> Optional[Path]:
    """The canonical checkout's directory, DERIVED and never hardcoded.

    VIVARIUM'S, adopted on 2026-09-11 in place of my own weaker test.
    `--git-common-dir` resolves to <canonical>/.git from any worktree, so its
    parent is the canonical checkout wherever the repository lives -- which makes
    the check survive a clone, another machine, and the day somebody moves it.
    """
    cd = _git("rev-parse", "--path-format=absolute", "--git-common-dir",
              cwd=path or REPO)
    if not cd:
        return None
    try:
        return Path(cd).resolve().parent
    except OSError:                                              # pragma: no cover
        return None


def inside_canonical_checkout(path: Optional[Path] = None) -> bool:
    """A LINKED worktree placed UNDERNEATH the canonical checkout.

    THE HOLE IN MY OWN GUARD, found by Vivarium within an hour of my finding the
    hole in theirs. Such a worktree is genuinely linked, so `is_main_worktree` is
    FALSE and the canonical check clears it -- while the files sit inside the
    directory that has twice lost ~11,000 tracked files to a concurrent rewrite.
    My first version matched temp-path MARKERS, which catches a scratchpad and
    misses this entirely. A derived root catches both without knowing a path.
    """
    root = canonical_root(path)
    here = Path(path or REPO).resolve()
    if root is None or here == root:
        return False                    # None: unknown. Equal: the canonical checkout itself.
    try:
        here.relative_to(root)
        return True
    except ValueError:
        return False


def is_session_temporary(path: Optional[Path] = None) -> bool:
    """True iff the worktree sits under a session-scoped temp path. Rule 2."""
    p = str(Path(path or REPO).resolve()).replace("\\", "/").lower()
    return any(m.replace("\\", "/") in p for m in _SESSION_TEMP_MARKERS)


def is_durable(path: Optional[Path] = None) -> bool:
    """Rule 2's conjunction: not the canonical checkout, not underneath it, not
    session-temporary. All three report differently and only the first is what
    `is_main_worktree` sees."""
    return not (is_main_worktree(path) or inside_canonical_checkout(path)
                or is_session_temporary(path))


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty -- what D-23 requires every
    receipt to carry, plus the two facts specific to this seat."""
    cwd = path or REPO
    try:
        from .acquisition import paths as _paths
        cache = str(_paths.tool_cache())
    except Exception:                                            # noqa: BLE001
        cache = None
    return {
        "base_sha": _git("rev-parse", "HEAD", cwd=cwd),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd),
        "worktree_path": str(Path(cwd).resolve()),
        "dirty": bool(_git("status", "--porcelain", "--untracked-files=no", cwd=cwd)),
        "main_worktree": is_main_worktree(cwd),
        "inside_canonical_checkout": inside_canonical_checkout(cwd),
        "session_temporary_worktree": is_session_temporary(cwd),
        "durable_worktree": is_durable(cwd),
        "allow_canonical_override": os.environ.get("TECHNE_ALLOW_CANONICAL") == "1",
        "tool_cache": cache,
        "tool_cache_versioned": False,
        "tool_cache_note": ("host-local and gitignored. base_sha pins this seat's CODE; it does "
                            "not pin the installed tools, whose identity is the hash-pinned "
                            "lock and the recorded artifact digests."),
    }


def assert_not_canonical(purpose: str = "work", *, allow_override: bool = True) -> Dict[str, Any]:
    """Refuse to do `purpose` from the canonical checkout. Returns the workspace
    receipt when allowed. A session-temporary worktree is RECORDED, not refused:
    it is a real violation of rule 2, but refusing outright would strand a
    running session with no path to commit its work -- and unpushed work is the
    exact loss D-23 exists to prevent."""
    r = receipt()
    if r["inside_canonical_checkout"]:
        # No override. A linked worktree under F:\Prometheus\ is rule 2's other
        # half, it is invisible to main_worktree, and nothing legitimate needs it.
        raise CanonicalCheckoutRefused(
            "refusing to %s from %s: a linked worktree UNDERNEATH the canonical checkout %s. "
            "It reports main_worktree false and is still inside the directory that has twice "
            "lost tracked files to a concurrent rewrite (D-23 rule 2)."
            % (purpose, r["worktree_path"], canonical_root()))
    if r["main_worktree"] and not (allow_override and r["allow_canonical_override"]):
        raise CanonicalCheckoutRefused(
            "refusing to %s from the canonical checkout %s (the repository's main worktree). "
            "Work from a linked worktree: git -C <canonical> worktree add "
            "F:/Prometheus-worktrees/techne-<task> -b techne/<task> origin/main (D-23, "
            "2026-09-11)." % (purpose, r["worktree_path"]))
    return r
