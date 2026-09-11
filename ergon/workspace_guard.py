"""Startup refusal for Ergon's process entry points (D-23, operator 2026-09-11).

Inherits the reference guard, archaeon/workspace.py, rather than restating
it (base role rule 1: inheritance over duplication). Called from the
``__main__`` block of every scheduled or long-running Ergon process, never
from ``main()`` itself, so tests that drive ``main()`` from a harness are
unaffected and only a real process launch is refused.

Returns the workspace receipt (base_sha, branch, worktree_path, dirty) so
the caller can stamp it on its first ledger row.
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
    return assert_not_canonical("run Ergon {}".format(purpose), allow_override=False)


__all__ = ["refuse_canonical", "receipt"]
