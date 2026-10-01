"""Repository root for read-only data fixtures (C1 rows, harvest outputs, git history).

Walks up from this file to the first directory that holds roles/Ananke, so the tests run unchanged from the
repository (prometheus/explib/tests) and from a staging copy nested anywhere inside a worktree. Tests that
need a data file skip when it is absent; nothing here is written."""
from __future__ import annotations

import pathlib


def repo_root(start: pathlib.Path | None = None) -> pathlib.Path:
    p = (start or pathlib.Path(__file__)).resolve()
    for q in [p, *p.parents]:
        if (q / "roles" / "Ananke").is_dir():
            return q
    return p.parents[3]


REPO = repo_root()
