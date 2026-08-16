"""Tests for the R3 control battery (Harmonia B, meter integrity).

The calibration suite in r3_controls itself is the deep test (both-directions, measured
operating characteristics); these unit tests pin the DECISION RULES and the plumbing so a
threshold edit or a pairing bug cannot land silently.
"""
import math

import pytest

from ergon.probe.assemble import assemble_retrieved, leaks_verdict
from ergon.probe.fixtures import synthetic_run
from ergon.probe.r3_controls import (
    B_MIN_N,
    control_a_payload_consumption,
    control_b_cheat,
    exact_binom_p_upper,
    headroom_check,
    leakage_decision,
    mcnemar_exact_p,
    packet_static_gate,
    pick_level,
    redact_content,
    wall_substrate_check,
    _guard_namespace,
    _synthetic_d0_records,
)


# ------------------------------------------------------------ exact stats


def test_binom_upper_exact_values():
    # P(X >= 61 | 100, .5) — the adjudicated boundary region of control C
    assert abs(exact_binom_p_upper(61, 100) - 0.0176) < 0.0005
    assert abs(exact_binom_p_upper(58, 100) - 0.0666) < 0.0005
    assert exact_binom_p_upper(0, 100) == pytest.approx(1.0)
    assert exact_binom_p_upper(100, 100) == pytest.approx(0.5 ** 100)


def test_mcnemar_symmetric_and_null():
    assert mcnemar_exact_p(0, 0) == 1.0
    assert mcnemar_exact_p(5, 5) == pytest.approx(1.0)
    assert mcnemar_exact_p(20, 5) == mcnemar_exact_p(5, 20)
    assert mcnemar_exact_p(20, 5) < 0.01


# ------------------------------------------------------------ control C decision rule


@pytest.mark.parametrize("k,expected", [
    (50, "PASS"),   # chance
    (58, "PASS"),   # p ~ .067 > .05, point .58 <= .60
    (60, "FAIL"),   # p ~ .028 < .05 (point boundary alone would allow it)
    (61, "FAIL"),   # both conditions violated
    (66, "FAIL"),   # decisive leak
    (40, "PASS"),   # below chance is not leakage (one-sided, preregistered direction)
])
def test_leakage_decision_vector(k, expected):
    assert leakage_decision(k, 100).verdict == expected


def test_leakage_two_failure_constant_is_two():
    from ergon.probe.r3_controls import C_MAX_FAILURES
    assert C_MAX_FAILURES == 2  # prereg §4.5: two failures exclude D0/D1


# ------------------------------------------------------------ packet path


def test_stripped_d0_packets_pass_static_gate_and_raw_leaks():
    recs = _synthetic_d0_records(20)
    tau = {"probe_prepass": 21}
    pkts = [assemble_retrieved(task_uid=r.uid or "", stratum="D0", records=[r], tau=tau)
            for r in recs]
    assert packet_static_gate(pkts).verdict == "PASS"
    # the same records UNREDACTED must be detectably leaky, else the gate proves nothing
    assert all(leaks_verdict(r.render()) for r in recs)


def test_redact_content_removes_content_keeps_frame():
    recs = _synthetic_d0_records(1)
    pkt = assemble_retrieved(task_uid="t", stratum="D2", records=recs,
                             tau={"probe_prepass": 2})
    red = redact_content(pkt.text)
    assert "=== RESIDUE ===" in red                      # frame intact
    assert "gcd" not in red.split("=== RESIDUE ===")[1]  # content gone from body
    assert len(red.splitlines()) == len(pkt.text.splitlines())  # structure intact


# ------------------------------------------------------------ controls A/B on planted worlds


def test_control_a_passes_on_planted_consumption():
    rows = synthetic_run(n_tasks=B_MIN_N, planted={"F0": 0.0, "F-answer": 0.50},
                         seed=20260816, solvers=("fixture:solver",))
    assert control_a_payload_consumption(rows).verdict == "PASS"


def test_control_a_fails_on_broken_pipeline():
    rows = synthetic_run(n_tasks=B_MIN_N, planted={"F0": 0.0, "F-answer": 0.0},
                         seed=20260816, solvers=("fixture:solver",))
    assert control_a_payload_consumption(rows).verdict == "FAIL"


def test_control_b_fails_on_planted_format_leak():
    rows = synthetic_run(n_tasks=B_MIN_N, planted={"F0": 0.0, "F-prom-retrieved": 0.15},
                         seed=20260817, solvers=("fixture:solver",))
    assert control_b_cheat(rows).verdict == "FAIL"


def test_control_b_empty_rows_is_fail_not_pass():
    # a control that measured nothing must not report clean
    assert control_b_cheat([]).verdict == "FAIL"


def test_control_a_empty_rows_is_fail_not_pass():
    assert control_a_payload_consumption([]).verdict == "FAIL"


# ------------------------------------------------------------ headroom / leveling


def test_pick_level_smallest_in_band_and_symmetric_failure():
    r = pick_level({"L0": {"s1": 0.82, "s2": 0.30}, "L1": {"s1": 0.55}})
    assert r.verdict == "PASS" and "L1" in r.detail
    assert pick_level({"L0": {"s": 0.9}, "L1": {"s": 0.2}}).verdict == "FAIL"


def test_headroom_uses_measured_ceiling():
    assert headroom_check(0.45, 0.95).verdict == "PASS"
    assert headroom_check(0.55, 0.70).verdict == "FAIL"   # 15pp < 25pp
    # a perfect F0 leaves no headroom even under a perfect ceiling
    assert headroom_check(0.90, 1.00).verdict == "FAIL"


# ------------------------------------------------------------ hygiene


def test_namespace_guard_rejects_arm_runs():
    rows = synthetic_run(n_tasks=4, seed=1, solvers=("s",))
    for r in rows:
        object.__setattr__(r, "run_id", "TIERB-2026")
    with pytest.raises(ValueError):
        _guard_namespace(rows)


def test_wall_substrate_check_real_corpus():
    r = wall_substrate_check()
    assert r.verdict == "PASS"
    assert r.numbers["n_ctrl"] == 2
