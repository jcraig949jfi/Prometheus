"""Every committed receipts file is a regression fixture (overnight C121; directive s2 "EXP-001 is a regression
fixture" generalised): replay_file() re-executes the IR embedded in each file's SUMMARY and compares every run's
trace hashes, series hashes and objective value with what was committed. A divergence is a SEMANTIC change to
the kernel or a reference component that must be versioned, never absorbed. 838 runs were checked by hand at
C99; this makes the check permanent and covers the search-generated files too (players as a sweep axis)."""
from __future__ import annotations

import pathlib

import pytest

from prometheus.toolbox.backends.local import replay_file
from prometheus.toolbox.receipt import read_all

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = sorted(p for d in ("examples/receipts", "playtests/receipts") for p in (ROOT / d).rglob("*.jsonl")
               if p.name not in ("replay.jsonl", "archive.jsonl") and "soak" not in p.parts)     # archive.jsonl files are search ROWS, not receipts


def _replayable(p: pathlib.Path) -> bool:
    return any(r["arm"] == "SUMMARY" and r.get("experiment") for r in read_all(p))


@pytest.mark.parametrize("path", [p for p in FILES if _replayable(p)], ids=lambda p: str(p.relative_to(ROOT)).replace("\\", "/"))
def test_committed_receipts_replay_without_divergence(path, tmp_path):
    out = replay_file(path, tmp_path / "replay.jsonl")
    assert out["status"] == "OK", out
    assert out["runs_compared"] > 0 and out["divergent"] == [], {"file": str(path), "divergent": out["divergent"][:3], "compared": out["runs_compared"]}


def test_the_fixture_set_is_not_empty_and_names_the_big_ones():
    names = {str(p.relative_to(ROOT)).replace("\\", "/") for p in FILES if _replayable(p)}
    assert len(names) >= 25, sorted(names)
    assert {"examples/receipts/exp_001.jsonl", "examples/receipts/exp_002.jsonl", "playtests/receipts/pt_e/receipts.jsonl", "playtests/receipts/pt_g/receipts.jsonl"} <= names
