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
    try:
        return subprocess.run(["git", *args], cwd=str(cwd or REPO), capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:                                   # noqa: BLE001 -- no git on PATH, timeout: "" means UNKNOWN
        return ""


def is_main_worktree(path: Optional[Path] = None) -> bool:
    """True iff `path` is inside the repository's MAIN worktree (the
    canonical checkout). A linked worktree's git-dir lives under
    <common>/worktrees/<name>, so the two answers differ there."""
    cwd = path or REPO
    gd = _git("rev-parse", "--git-dir", cwd=cwd)
    cd = _git("rev-parse", "--git-common-dir", cwd=cwd)
    if not gd or not cd:
        return False                                    # undeterminable; see workspace_known()
    return Path(cwd, gd).resolve() == Path(cwd, cd).resolve()


def workspace_known(path: Optional[Path] = None) -> bool:
    """True iff git answered for this path. ARCH-52 (Mnemosyne #290,
    2026-09-16): a PEW service ran from the CANONICAL checkout for a morning
    with main_worktree=false in its own receipt because the scheduled-task
    context had no git on PATH, _git() returned "", and is_main_worktree()
    read "cannot tell" as "not canonical". This reference guard had the
    same hole and every seat that copied it inherited it. "Cannot tell" is
    not "not canonical": assert_not_canonical() now fails CLOSED on it."""
    cwd = path or REPO
    return bool(_git("rev-parse", "--git-dir", cwd=cwd)) and bool(_git("rev-parse", "HEAD", cwd=cwd))


_REPO_ID: Dict[str, str] = {}


def repo_id(path: Optional[Path] = None) -> str:
    """The repository's identity: its root-commit SHA(s), sorted and joined
    by '+' when the history has several roots. Hermes HERMES-32 (#118,
    283687393): this one field turns "same-named repository, different
    history" from an UNSIGNABLE failure into an EXACT one, and the worktree
    role does no work for that specimen. Cached per process per git-common-
    dir since it cannot change while a process keeps its checkout."""
    cwd = path or REPO
    key = _git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd)   # relative ".git" would collide across repos
    if key not in _REPO_ID:
        roots = _git("rev-list", "--max-parents=0", "HEAD", cwd=cwd).split()
        _REPO_ID[key] = "+".join(sorted(roots))
    return _REPO_ID[key]


def receipt(path: Optional[Path] = None) -> Dict[str, Any]:
    """base_sha, branch, worktree_path, dirty, repo_id -- what every receipt carries."""
    cwd = path or REPO
    sha = _git("rev-parse", "HEAD", cwd=cwd)
    branch = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no", cwd=cwd))
    return {"base_sha": sha, "branch": branch, "worktree_path": str(Path(cwd).resolve()),
            "dirty": dirty, "main_worktree": is_main_worktree(cwd), "workspace_known": workspace_known(cwd),
            "repo_id": repo_id(cwd),
            "allow_canonical_override": os.environ.get("ARCHAEON_ALLOW_CANONICAL") == "1"}


def assert_not_canonical(purpose: str = "work", *, allow_override: bool = True) -> Dict[str, Any]:
    """Refuse to do `purpose` from the canonical checkout. Returns the
    workspace receipt when allowed."""
    r = receipt()
    if not r["workspace_known"]:
        raise CanonicalCheckoutRefused(
            "refusing to {} from {}: git did not answer for this path (no git on PATH, or not a repository), so "
            "whether it is the canonical checkout is UNKNOWN; the guard fails closed (ARCH-52, 2026-09-16)."
            .format(purpose, r["worktree_path"]))
    if r["main_worktree"] and not (allow_override and r["allow_canonical_override"]):
        raise CanonicalCheckoutRefused(
            "refusing to {} from the canonical checkout {} (the repository's main worktree). "
            "Work from a linked worktree: git -C <canonical> worktree add <path> -b <seat>/<task> origin/main "
            "(D-23, 2026-09-11).".format(purpose, r["worktree_path"]))
    return r
