"""c1b_run.battery_row looks up the A2.2 eligibility table by the battery's cell id. Fresh-seed
champions run as "<cell>:fresh<k>", which is never a key, so the specimen's NOT_ELIGIBLE clauses are
dropped: DELAY_LINE_SPECIMEN / IN_FLIGHT_UNDECODED were issued without _UNRESOLVED at a physics where
Z is NOT_ELIGIBLE (C1b rows: 4ab2ba01 fresh1/2/3; corrected post hoc in c1b/build_summary.py, so the
recorded C1b summary is right, the driver is not). FAILS on current code, PASSES with
patches/c1b_run_fresh_eligibility.diff. Specimen rows are unchanged."""
# Regression test from Wave-2 worker W2-A2 (harvest/wave2/W2-A2/REPORT.md F6/F8/F9).
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
import pathlib
import pytest

REPO = pathlib.Path(__file__).resolve().parents[3]


@pytest.fixture
def repo():
    return REPO


import types

from prometheus.ananke import c1b, c1b_run

ELIG = {"4ab2ba014aac967e": {"NOT_ELIGIBLE": ["Z"]}}
BOOLS = {"A": True, "Z": True, "B": True, "C": True, "I": False,
         "K_S": False, "K_Kp": False, "K_w": False, "K_En": False}


def _stub(monkeypatch):
    run = types.SimpleNamespace(pairs=None)
    monkeypatch.setattr(c1b, "m2_battery", lambda ph, env: {})
    monkeypatch.setattr(c1b, "run_battery", lambda *a, **k: {"normal": {"status": "RAN", "run": run}})
    monkeypatch.setattr(c1b_run, "read_m2", lambda res, env: dict(BOOLS))
    monkeypatch.setattr(c1b, "census_predicts", lambda *a, **k: {})
    monkeypatch.setattr(c1b, "ticks", lambda env: {"mid": []})
    monkeypatch.setattr(c1b, "carryover", lambda *a, **k: {})
    monkeypatch.setattr(c1b_run, "summarise", lambda res: {})


def test_fresh_row_inherits_specimen_eligibility(monkeypatch):
    _stub(monkeypatch)
    row = c1b_run.battery_row("M2", "4ab2ba014aac967e:fresh1", None, None, None, None, ELIG, "cpu")
    assert row["label"] == "DELAY_LINE_SPECIMEN_UNRESOLVED", row["label"]
    assert row["not_eligible"] == ["Z"]


def test_specimen_row_unchanged(monkeypatch):
    _stub(monkeypatch)
    row = c1b_run.battery_row("M2", "4ab2ba014aac967e", None, None, None, None, ELIG, "cpu")
    assert row["label"] == "DELAY_LINE_SPECIMEN_UNRESOLVED"
