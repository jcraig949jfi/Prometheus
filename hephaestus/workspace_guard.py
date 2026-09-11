"""Startup refusal for Hephaestus's entry points (D-23, operator 2026-09-11).

Inherits the reference guard, archaeon/workspace.py, rather than restating
it (base role rule 1: inheritance over duplication; ergon/workspace_guard.py
is the same shape). Called from the ``__main__`` block of every
hephaestus/src module that writes queue state or results, never from
``main()`` itself, so a harness that drives ``main()`` is unaffected and
only a real process launch from the canonical checkout is refused.

Returns the workspace receipt (base_sha, branch, worktree_path, dirty) so
the caller can stamp it on the artifact it writes.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from archaeon.workspace import assert_not_canonical, receipt  # noqa: E402


def refuse_canonical(purpose: str) -> dict:
    """Refuse to run ``purpose`` from the canonical checkout; return the receipt."""
    return assert_not_canonical("run Hephaestus {}".format(purpose), allow_override=False)


__all__ = ["refuse_canonical", "receipt"]
