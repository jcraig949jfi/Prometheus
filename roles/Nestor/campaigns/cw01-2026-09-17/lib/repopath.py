"""Locate the repo root by walking up for a marker, not by counting directories.

CW01-D046. Every e05 script derives its roots by hardcoded depth:

    HERE = pathlib.Path(__file__).resolve().parent
    BASE = HERE.parents[1]          # campaign root
    REPO = BASE.parents[3]          # worktree root

That works only while the layout is exactly
`roles/<Seat>/campaigns/<id>/experiments/<exp>/`. The independent replication lane
found the consequence: the experiment is reproducible IN PLACE but **not relocatable**.
`git archive`-ing the experiment subtree to a different depth breaks the import of
`primordial.fabric`, and the lane's self-check only worked because `git archive`
happens to reconstruct that same layout. That bears directly on the campaign's
M1/M2/Podman/cloud portability mandate.

The walk-up already existed in `lib/localrun.py:93-99`, inside `check_prerequisites`,
tangled up with PM_TAG enforcement. This module extracts it as a pure function rather
than adding a second implementation of something the codebase already had.

ADDITIVE BY DESIGN. `localrun.check_prerequisites` is imported by cw01-e05's frozen,
committed driver and is NOT modified here. e05 reproduces from its own commit, which
pins its own copy of every library. This is for e06 onward.
"""
from __future__ import annotations

import pathlib


class RepoRootNotFound(RuntimeError):
    """Raised when no marker directory is found walking up from a start path."""


def find_root(start, marker=".git"):
    """First ancestor of `start` (inclusive) containing `marker`.

    Depth-independent by construction: the answer depends on where the marker is,
    never on how deeply `start` happens to be nested.
    """
    p = pathlib.Path(start).resolve()
    for cand in [p] + list(p.parents):
        if (cand / marker).exists():
            return cand
    raise RepoRootNotFound(
        "no %r found walking up from %s. If this is a relocated copy, the marker was "
        "not carried with it." % (marker, p))


def find_campaign_root(start, marker="CAMPAIGN_STATE.json"):
    """The campaign directory, found by its own state file rather than by depth."""
    return find_root(start, marker)


if __name__ == "__main__":
    import tempfile
    import sys

    ok = True

    def ck(label, cond, detail=""):
        global ok
        ok &= bool(cond)
        print("   %-46s %s %s" % (label, "PASS" if cond else "FAIL", detail))

    here = pathlib.Path(__file__).resolve().parent
    root = find_root(here)
    ck("finds a repo root from lib/", (root / ".git").exists(), str(root))

    # THE D046 PROPERTY: same answer from different depths.
    deep = here.parent / "experiments" / "cw01-e05"
    if deep.exists():
        ck("same root from a deeper path", find_root(deep) == root, str(deep.name))
    ck("same root from the root itself", find_root(root) == root)

    camp = find_campaign_root(here)
    ck("finds campaign root by its state file", (camp / "CAMPAIGN_STATE.json").exists(), camp.name)
    if deep.exists():
        ck("campaign root is depth-independent too", find_campaign_root(deep) == camp)

    # Fails closed, and says why, rather than returning a wrong answer.
    tmp = pathlib.Path(tempfile.mkdtemp())
    raised = False
    try:
        find_root(tmp, marker=".no_such_marker_exists")
    except RepoRootNotFound:
        raised = True
    ck("fails closed when the marker is absent", raised)

    # Contrast with the defect it replaces: hardcoded depth gives a DIFFERENT answer
    # from a different depth, which is exactly the relocatability failure.
    if deep.exists():
        by_depth_from_lib = here.parents[3] if len(here.parents) > 3 else None
        by_depth_from_exp = deep.parents[3] if len(deep.parents) > 3 else None
        ck("hardcoded depth disagrees across depths (the defect)",
           by_depth_from_lib != by_depth_from_exp,
           "%s vs %s" % (getattr(by_depth_from_lib, "name", None),
                         getattr(by_depth_from_exp, "name", None)))

    print("\n   %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    sys.exit(0 if ok else 1)
