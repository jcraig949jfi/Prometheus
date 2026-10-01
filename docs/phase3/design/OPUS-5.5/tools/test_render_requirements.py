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
        for name in ("CATEGORIES", "PRIORITIES", "GATES_FIXED", "ENFORCE", "BUILD", "OP", "TAXONOMY", "COVERAGE", "R"):
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
    f.R[0]["text"] = f.R[0]["text"] + " —"
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
