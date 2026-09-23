"""H-R5-3: F12 progress axes by rule from receipt type + lineage; error_metabolism credited to the refuter (O8)."""
from __future__ import annotations

import pytest

from primordial.score import axes_r5 as AX

TEST = "primordial/tests/test_demo_regression.py"
ROWS = "primordial/ledger/rows/C/C-R5-demo.jsonl"


@pytest.fixture
def root(tmp_path):
    for p in (TEST, ROWS):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x\n", encoding="utf-8")
    return tmp_path


def _rec(lane, exp, status="PASS", ts=1.0, **kw):
    return {"lane": lane, "exp_id": exp, "status": status, "ts": ts, "rows": ROWS,
            "controls": {"cheat": "failed as expected"}, **kw}


def test_error_metabolism_is_credited_to_the_refuter_never_the_originator(root):
    recs = [_rec("B", "B-R5-claim", ts=1.0), _rec("B", "B-R5-other", ts=1.5),
            _rec("D", "D-R5-refute", ts=2.0, refutes="B-R5-claim is wrong"),
            _rec("C", "C-R5-late", ts=3.0, refutes=["B-R5-claim"]),                  # already metabolized
            _rec("B", "B-R5-self", ts=4.0, refutes="B-R5-other"),                     # own lane: 0
            _rec("E", "E-R5-nocheat", ts=5.0, refutes="B-R5-other", controls={}),     # not board-eligible
            _rec("C", "C-R5-fail", status="FAIL", ts=6.0, refutes="B-R5-other")]      # a FAIL refutes nothing
    out = AX.axes(recs, root=root)
    assert out["D"]["error_metabolism"] == 1 and out["D"]["detail"]["error_metabolism"][0]["originators"] == ["B"]
    assert out["B"]["error_metabolism"] == 0 and out["C"]["error_metabolism"] == 0 and out["E"]["error_metabolism"] == 0
    assert out["B"]["detail"]["own_refutations_unscored"] == [{"exp_id": "B-R5-self", "refutes": ["B-R5-other"]}]


def test_instrument_gain_needs_a_tooling_pass_with_an_existing_regression_test(root):
    recs = [_rec("E", "E-R5-fix", envelope={"experiment_class": "tooling"}, regression_test=TEST),
            _rec("E", "E-R5-top", experiment_class="instrument", regression_test=f"see {TEST}"),
            _rec("E", "E-R5-notest", envelope={"experiment_class": "tooling"}, regression_test="primordial/tests/test_gone.py"),
            _rec("E", "E-R5-science", envelope={"experiment_class": "science"}, regression_test=TEST),
            _rec("E", "E-R5-failed", status="FAIL", envelope={"experiment_class": "tooling"}, regression_test=TEST)]
    out = AX.axes(recs, root=root)
    assert out["E"]["instrument_gain"] == 2
    assert [x["exp_id"] for x in out["E"]["detail"]["instrument_gain"]] == ["E-R5-fix", "E-R5-top"]


BOUNDARY = {"parameter": "runs_per_family", "below": {"value": 4, "verdict": "INELIGIBLE"},
            "above": {"value": 8, "verdict": "FAIL"}}


@pytest.mark.parametrize("status,boundary,rows,credit", [
    ("FAIL", BOUNDARY, ROWS, 1),
    ("KILL", BOUNDARY, ROWS, 1),
    ("PASS", BOUNDARY, ROWS, 0),                                                          # not a scientific FAIL
    ("FAIL", {**BOUNDARY, "above": {"value": 8, "verdict": "INELIGIBLE"}}, ROWS, 0),     # same verdict both sides
    ("FAIL", {**BOUNDARY, "below": {"value": 9, "verdict": "INELIGIBLE"}}, ROWS, 0),     # sides out of order
    ("FAIL", {**BOUNDARY, "parameter": ""}, ROWS, 0),
    ("FAIL", BOUNDARY, "primordial/ledger/rows/C/absent.jsonl", 0),                     # rows not committed
    ("FAIL", None, ROWS, 0),
])
def test_boundary_resolution_rule(root, status, boundary, rows, credit):
    rec = _rec("C", "C-R5-b", status=status, rows=rows, science={"boundary": boundary} if boundary else {})
    assert AX.axes([rec], root=root)["C"]["boundary_resolution"] == credit


def test_self_reported_points_are_ignored(root):
    rec = _rec("B", "B-R5-brag", science={"error_metabolism": 5, "instrument_gain": 3, "boundary_resolution": 9})
    out = AX.axes([rec], root=root)["B"]
    assert {a: out[a] for a in AX.AXES} == {"boundary_resolution": 0, "instrument_gain": 0, "error_metabolism": 0}
