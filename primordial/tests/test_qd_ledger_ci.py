"""M3: `qd_ledger check` uses the bootstrap CI of the candidate's median when run-seed values are given."""
from __future__ import annotations

import numpy as np

from primordial.metric import ci as CI
from primordial.metric.tests.test_ci import d3_arm
from primordial.ops import qd_ledger as Q
from primordial.tests.test_qd_ledger_draw import row
from primordial.tests.test_qd_ledger_floor import floor_row


def test_without_held_the_band_rule_is_unchanged_and_labelled():
    got = Q.check([row(90.0, 312)], "w4", "p", 88.0, 5, 200, 8)
    assert got["verdict"] == "PASS" and got["band_rule"] == "iqr"


def test_ci_replaces_a_wide_baseline_iqr_band():
    # baseline IQR 20 lets a tight candidate at 91 pass (91 >= 98 - 10); its CI (~[90.4, 91.6]) does not reach 98
    rows = [row(98.0, 312, iqr=20.0)]
    held = [90.2, 90.6, 90.8, 91.0, 91.0, 91.2, 91.4, 91.8]
    assert Q.check(rows, "w4", "p", 91.0, 0.6, 200, 8)["verdict"] == "PASS"
    got = Q.check(rows, "w4", "p", 91.0, 0.6, 200, 8, held=held)
    assert got["verdict"] == "FAIL" and got["band_rule"] == "bootstrap_ci95"
    assert got["band"] == list(CI.median_ci(held))


def test_ci_better_at_equal_bytes_needs_the_lower_bound_above():
    rows = [row(90.0, 312, iqr=0.0)]
    hi = [95.0, 95.5, 96.0, 96.0, 96.5, 97.0, 97.0, 98.0]
    assert Q.check(rows, "w4", "p", 96.25, 1.0, 312, 8, held=hi)["rule"] == "better at <= bytes"
    straddle = [80.0, 85.0, 88.0, 90.0, 92.0, 95.0, 99.0, 104.0]
    assert Q.check(rows, "w4", "p", 91.0, 9.0, 312, 8, held=straddle)["verdict"] == "FAIL"


def test_d3_w1_regression():
    # D3: float vs int4 on w1 are the same search in the same world; with the float arm as the baseline,
    # the int4 arm (fewer bytes) is at parity by its CI (47.77..65.63 covers 59.19), not a false FAIL
    f, q = d3_arm("float"), d3_arm("int4")
    rows = [row(float(np.median(f)), 344, iqr=float(np.percentile(f, 75) - np.percentile(f, 25)))]
    got = Q.check(rows, "w4", "p", float(np.median(q)), 8.98, 52, 8, held=q.tolist())
    assert got["verdict"] == "PASS" and got["rule"] == "parity at fewer bytes"
    assert got["band"] == [47.765625, 65.6318359375]


def test_floor_reads_the_ci_lower_bound():
    rows = [row(98.0, 312, iqr=2.0), floor_row(95.0)]
    wide = [90.0, 94.0, 96.0, 98.0, 99.0, 100.0, 101.0, 104.0]       # median 98.5, CI low < 95
    assert Q.check(rows, "w4", "p", 98.5, 1.0, 200, 8)["floor"]["verdict"] == "PASS"
    assert Q.check(rows, "w4", "p", 98.5, 1.0, 200, 8, held=wide)["floor"]["verdict"] == "BELOW_FLOOR"
