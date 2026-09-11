"""Startup refusal for Lexis's file-writing instruments (D-23, operator 2026-09-11).

Inherits the reference guard, archaeon/workspace.py, rather than restating it
(base role rule 1: inheritance over duplication; ergon/workspace_guard.py is
the sibling pattern). Called from the ``__main__`` block of every Lexis script
that writes a result file into the tree, never from ``main()`` itself, so
``verify_handoff.py`` and any harness that drives ``main()`` are unaffected
and only a real launch from the canonical checkout is refused.

Returns the workspace receipt (base_sha, branch, worktree_path, dirty) so the
caller can stamp it on what it writes.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from archaeon.workspace import assert_not_canonical, receipt  # noqa: E402


def refuse_canonical(purpose: str) -> dict:
    """Refuse to run ``purpose`` from the canonical checkout; return the receipt."""
    return assert_not_canonical("run Lexis {}".format(purpose), allow_override=False)


__all__ = ["refuse_canonical", "receipt"]
