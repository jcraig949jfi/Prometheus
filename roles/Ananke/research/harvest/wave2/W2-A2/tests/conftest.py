"""W2-A2 regression tests. Run against the ORIGINAL package:
    PYTHONPATH=<worktree root> pytest -q tests
and against the patched copy:
    PYTHONPATH=<W2-A2>/scratch/patched;<worktree root> pytest -q tests
CPU only; no GPU, no search."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")
import pathlib
import pytest

W2 = pathlib.Path(__file__).resolve().parents[1]
REPO = pathlib.Path(__file__).resolve().parents[7]
ROWS_GZ = REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"


@pytest.fixture(scope="session")
def c1_rows():
    import gzip
    import json
    return [json.loads(l) for l in gzip.open(ROWS_GZ, "rt") if l.strip()]


@pytest.fixture(scope="session")
def repo():
    return REPO
