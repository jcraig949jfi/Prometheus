"""Where the Lean build lives, resolved for ANY worktree (Techne, 2026-09-11).

The lean-repl and mathlib4 builds are host-local and gitignored
(`external_deps/repl/`, `external_deps/mathlib4/`), and every test that uses them
computed `REPO_ROOT/external_deps` from `__file__`. Under the D-23 worktree
contract that path resolves to the WORKTREE, where the build does not exist, so
from any seat's worktree the whole Lean battery reported "16 skipped" -- and the
forensic inventory of 2026-09-11 nearly recorded the Lean donor as dead on that
evidence. Measured the same day through a directory junction: 32 of 32 pass.

Resolution order, first hit wins, each candidate checked for the REPL binary
(the property that matters) rather than for the directory name:

    1. $PROMETHEUS_EXTERNAL_DEPS            explicit, config-driven
    2. <this repo root>/external_deps       the pre-D-23 layout, or a junction
    3. <canonical checkout>/external_deps   parent of `git rev-parse --git-common-dir`,
                                            which is the main worktree wherever the
                                            repository lives (no drive letter assumed)

Returns the first directory that holds `repl/.lake/build/bin/repl.exe`; if none does,
returns candidate 2 so the callers' existing skip messages stay accurate.
"""
from __future__ import annotations

import os
import pathlib
import subprocess

_REPL_BIN = ("repl", ".lake", "build", "bin", "repl.exe")


def _has_repl(root: pathlib.Path) -> bool:
    return root.joinpath(*_REPL_BIN).is_file()


def _canonical_root(start: pathlib.Path) -> pathlib.Path | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             cwd=str(start), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0 or not out.stdout.strip():
        return None
    return pathlib.Path(out.stdout.strip()).parent


def external_deps_root() -> str:
    here = pathlib.Path(__file__).resolve()
    repo_root = here.parents[3]
    candidates = []
    env = os.environ.get("PROMETHEUS_EXTERNAL_DEPS")
    if env:
        candidates.append(pathlib.Path(env))
    candidates.append(repo_root / "external_deps")
    canon = _canonical_root(repo_root)
    if canon is not None:
        candidates.append(canon / "external_deps")
    for c in candidates:
        if _has_repl(c):
            return str(c)
    return str(repo_root / "external_deps")
