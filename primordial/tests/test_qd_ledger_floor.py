"""M1: `qd_ledger check` reads every verdict against the trivial-policy floor as well as raw."""
from __future__ import annotations

from primordial.ops import qd_ledger as Q
from primordial.tests.test_qd_ledger_draw import row


def floor_row(median, kind="abstain", world="w4", pressure="p"):
    r = row(median, 0, iqr=0.0, baseline=False, rep=f"floor_{kind}", status="control")
    r["cell"].update(world=world, pressure=pressure)
    r["floor"] = kind
    return r


def test_no_floor_rows_leaves_raw_verdict_and_says_so():
    rows = [row(90.0, 312)]
    got = Q.check(rows, "w4", "p", 88.0, 5, 200, 8)
    assert got["verdict"] == "PASS" and got["floor"] == {"verdict": "NO_FLOOR"}


def test_floor_above_baseline_makes_raw_pass_below_floor():
    # the round 2 shape: baseline 98.76, a 0-byte abstain policy at 107.75, candidate at parity
    rows = [row(98.76, 312), floor_row(107.75), floor_row(11.49, kind="random_action")]
    got = Q.check(rows, "w4", "p", 97.19, 0.47, 8, 8)
    assert got["verdict"] == "PASS"                                  # raw rule unchanged
    assert got["floor"]["verdict"] == "BELOW_FLOOR"
    assert got["floor"]["floor_held64"] == 107.75 and got["floor"]["floor_kind"] == "abstain"
    assert got["floor"]["normalized"] == {"linear": None}             # no headroom above the floor


def test_candidate_above_floor_but_baseline_below_it_has_no_headroom():
    rows = [row(98.76, 312), floor_row(100.0)]
    got = Q.check(rows, "w4", "p", 110.0, 2.0, 8, 8)
    assert got["verdict"] == "PASS" and got["floor"]["verdict"] == "NO_HEADROOM"


def test_floor_below_baseline_keeps_raw_verdict_and_normalizes():
    rows = [row(90.0, 312), floor_row(50.0)]
    got = Q.check(rows, "w4", "p", 88.0, 4.0, 200, 8)
    assert got["verdict"] == got["floor"]["verdict"] == "PASS"
    assert got["floor"]["normalized"] == {"linear": 0.95}
    low = Q.check(rows, "w4", "p", 51.0, 4.0, 200, 8)                # 51 - 2 <= 50
    assert low["verdict"] == "FAIL" and low["floor"]["verdict"] == "BELOW_FLOOR"


def test_floor_rows_never_enter_the_front_or_top():
    rows = [row(90.0, 312), floor_row(120.0)]
    assert [r["mechanism"] for r in Q.pareto(rows, "w4")] == ["linear"]
    assert all(not r.get("floor") for r in Q.top(rows, "w4"))


def test_ineligible_stays_ineligible_under_floor():
    rows = [row(90.0, 312), floor_row(10.0)]
    assert Q.check(rows, "w4", "p", 99.0, 5, 10, 4)["floor"]["verdict"] == "INELIGIBLE"
