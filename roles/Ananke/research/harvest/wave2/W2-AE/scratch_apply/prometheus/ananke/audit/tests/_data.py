"""Read-only data access for the audit tests (C1 rows, harvest outputs)."""
from __future__ import annotations

import functools
import gzip
import json
import pathlib

import pytest


def repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for q in here.parents:
        if (q / "roles" / "Ananke").is_dir():
            return q
    return here.parents[4]


REPO = repo_root()
HARVEST = REPO / "roles/Ananke/research/harvest"
ROWS = REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


def need(*paths):
    """skipif marker: every path must exist."""
    missing = [str(p) for p in paths if not pathlib.Path(p).exists()]
    return pytest.mark.skipif(bool(missing), reason=f"data not present: {missing}")


@functools.lru_cache(maxsize=1)
def rows() -> tuple:
    return tuple(json.loads(l) for l in gzip.open(ROWS, "rt") if l.strip())


@functools.lru_cache(maxsize=1)
def by_id() -> dict:
    return {r["cell_id"]: r for r in rows()}


def row(prefix: str, **match) -> dict:
    hits = [r for r in rows() if r["cell_id"].startswith(prefix)
            and all((r["env"]["family"] if k == "family" else r[k]) == v for k, v in match.items())]
    if len(hits) != 1:
        raise KeyError(f"{prefix} {match}: {len(hits)} rows")
    return hits[0]


def load_json(rel: str):
    return json.loads((REPO / rel).read_text())
