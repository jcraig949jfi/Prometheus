"""Shared fixtures for tests added in the Wave-2 harvest (W2-A2): the worktree root and the C1 rows."""
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
import gzip
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def repo():
    return REPO


@pytest.fixture(scope="session")
def c1_rows():
    p = REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
