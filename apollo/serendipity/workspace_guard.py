"""Startup refusal for Apollo's Foundry entry points (D-23, operator 2026-09-11).

Inherits the reference guard, archaeon/workspace.py, rather than restating it
(base role rule 1: inheritance over duplication). Called from the ``__main__``
block of every Apollo process that writes a ledger, a gate artifact or a fossil,
never from ``main()`` itself, so a harness that drives ``main()`` for a test is
unaffected and only a real process launch is refused.

Returns the workspace receipt (base_sha, branch, worktree_path, dirty) so the
caller can stamp it on its first artifact.
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
    return assert_not_canonical("run Apollo {}".format(purpose), allow_override=False)


__all__ = ["refuse_canonical", "receipt"]
