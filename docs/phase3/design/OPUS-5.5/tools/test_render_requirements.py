"""Controls for the requirements checker: it must accept the real data and fail on each planted violation.

Run:  python -m pytest docs/phase3/design/OPUS-5.5/tools/test_render_requirements.py -q
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import render_requirements as rr  # noqa: E402


class Fake:
    """A mutable copy of the requirements module's data."""

    def __init__(self, rd):
        for name in ("CATEGORIES", "PRIORITIES", "GATES_FIXED", "ENFORCE", "BUILD", "OP", "TAXONOMY", "COVERAGE", "R",
                     "S1_WORK_ITEMS", "S1_BUDGET_CAP_M"):
            setattr(self, name, copy.deepcopy(getattr(rd, name)))


def real():
    return Fake(rr.load())


def test_real_data_passes():
    assert rr.validate(real()) == []


def test_duplicate_id_fails():
    f = real()
    f.R.append(dict(f.R[0]))
    assert any("duplicate" in e for e in rr.validate(f))


def test_bad_priority_fails():
    f = real()
    f.R[0]["pri"] = "MUST"
    assert any("bad priority" in e for e in rr.validate(f))


def test_bad_gate_fails():
    f = real()
    f.R[0]["gate"] = "SOMETIME"
    assert any("bad gate" in e for e in rr.validate(f))


def test_non_ascii_fails():
    f = real()
    f.R[0]["text"] = f.R[0]["text"] + " " + chr(0x2014)
    assert any("non-ASCII" in e for e in rr.validate(f))


def test_uncovered_class_fails():
    f = real()
    f.COVERAGE.pop("T01")
    assert any("T01" in e and "not covered" in e for e in rr.validate(f))


def test_coverage_by_unenforced_requirement_fails():
    f = real()
    # point a class only at a HIGH VALUE / FLAG requirement
    flag = next(r["id"] for r in f.R if r["pri"] == "HIGH VALUE" and r["enforce"] == "FLAG")
    f.COVERAGE["T02"] = [flag]
    assert any("T02" in e and "no REQUIRED" in e for e in rr.validate(f))


def test_coverage_to_withdrawn_fails():
    f = real()
    wd = next(r["id"] for r in f.R if r["pri"] == "WITHDRAWN")
    f.COVERAGE["T03"] = [wd] + f.COVERAGE["T03"]
    assert any("withdrawn" in e for e in rr.validate(f))


def test_block_without_test_or_counterfeit_fails():
    f = real()
    r = next(r for r in f.R if r["pri"] == "REQUIRED" and r["enforce"] == "BLOCK")
    r["fake"] = ""
    r["test"] = ""
    assert any("neither counterfeit nor test" in e for e in rr.validate(f))


def test_slice_block_without_counterfeit_fails():
    f = real()
    r = next(r for r in f.R if r["gate"] == "SLICE" and r["enforce"] == "BLOCK")
    r["fake"] = ""
    assert any("SLICE BLOCK requirement without a counterfeit" in e for e in rr.validate(f))


def test_class_covered_only_without_counterfeit_fails():
    f = real()
    for ref in f.COVERAGE["SD2"]:
        next(r for r in f.R if r["id"] == ref)["fake"] = ""
    assert any("SD2" in e and "counterfeit" in e for e in rr.validate(f))


def test_live_requirement_without_test_fails():
    f = real()
    r = next(r for r in f.R if r["pri"] != "WITHDRAWN")
    r["test"] = ""
    assert any("without a discriminating test" in e for e in rr.validate(f))


def test_unassigned_slice_requirement_fails():
    f = real()
    wid, title, budget, refs = f.S1_WORK_ITEMS[0]
    dropped = refs[0]
    f.S1_WORK_ITEMS[0] = (wid, title, budget, refs[1:])
    assert any(dropped in e and "S1 work items" in e for e in rr.validate(f))


def test_s1_budget_over_cap_fails():
    f = real()
    wid, title, budget, refs = f.S1_WORK_ITEMS[0]
    f.S1_WORK_ITEMS[0] = (wid, title, budget + f.S1_BUDGET_CAP_M, refs)
    assert any("above the" in e and "cap" in e for e in rr.validate(f))
