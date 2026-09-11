#!/usr/bin/env python
"""Controls for the D-23 workspace guard in corpus_audit.py.

Base rule 3: every critical instrument possesses a way to demonstrate
that it can fail and that it detects the real thing. A guard nobody has
watched refuse is not a guard -- it is a line of code that has never been
observed doing its job.

This seat learned that the hard way on 2026-09-11: the guard was first
"verified" by running the worktree's copy of the script from a canonical
working directory, which proves nothing, because corpus_audit.py anchors
to its own file location, not to the caller's cwd. The test below calls
the guard directly with each root instead.

    POSITIVE control: the guard must REFUSE the canonical checkout
                      (git-dir == git-common-dir)
    NEGATIVE control: the guard must ACCEPT a linked worktree

Usage:

    python roles/Nous/science/test_guard.py

Exit 0 if both controls pass, 1 otherwise. Makes no network call and
reads no credential. Roots are discovered from git, never hardcoded.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys


def load_audit():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "corpus_audit.py")
    spec = importlib.util.spec_from_file_location("corpus_audit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(args, cwd=None):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                       text=True, timeout=60)
    return r.stdout.strip()


def discover_roots():
    """Return (canonical_root, worktree_root), both from git.

    The canonical checkout is the main worktree: `git rev-parse
    --git-common-dir` names its .git directory, whose parent is it.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    worktree = git(["-C", here, "rev-parse", "--show-toplevel"])
    common = git(["-C", here, "rev-parse", "--path-format=absolute",
                  "--git-common-dir"])
    canonical = os.path.dirname(common) if common else ""
    return canonical, worktree


def main() -> int:
    mod = load_audit()
    canonical, worktree = discover_roots()
    failures = []

    print("canonical checkout : %s" % canonical)
    print("this worktree      : %s" % worktree)
    print()

    print("POSITIVE control -- the guard must REFUSE the canonical checkout")
    if not canonical or not os.path.isdir(canonical):
        print("  INDETERMINATE: canonical root not resolvable from git")
        failures.append("positive control indeterminate")
    else:
        try:
            mod.assert_not_canonical(canonical)
            print("  FAIL: the guard did not fire on the canonical checkout")
            failures.append("guard did not refuse the canonical checkout")
        except SystemExit as exc:
            print("  PASS: refused -- %s" % str(exc)[:72])

    print("NEGATIVE control -- the guard must ACCEPT a linked worktree")
    try:
        mod.assert_not_canonical(worktree)
        print("  PASS: accepted the linked worktree")
    except SystemExit as exc:
        print("  FAIL: the guard wrongly refused a valid worktree -- %s" % exc)
        failures.append("guard refused a valid worktree")

    print()
    if failures:
        print("GUARD CONTROLS FAILED:")
        for f in failures:
            print("  %s" % f)
        return 1
    print("GUARD CONTROLS PASSED (positive and negative).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
