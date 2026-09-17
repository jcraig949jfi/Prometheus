"""G-R4-3: screen verdicts under the four Q1/Q2 variants, bound exactness, and the 8-survivor stop."""
from __future__ import annotations

import itertools

import pytest

from primordial.metric import screen as S


def test_round3_w1_shape_is_culled_baseline_or_held():
    # gate 170.47 > abstain 88.28 > baseline (CI low below the floor): SWARM_R4 s7 Q2
    v = S.verdicts(88.28, 170.47, 50.0)
    assert v["four_policy|CULL"] == {"verdict": "CULLED", "cull_reason": "BASELINE", "floor": 88.28}
    assert v["four_policy|HOLD"]["verdict"] == "HELD"
    assert v["gate_in|CULL"] == {"verdict": "CULLED", "cull_reason": "BASELINE", "floor": 170.47}
    # operator ruling (gate_in|HOLD): HELD compares the gate with the FOUR-POLICY floor, not the gate-in floor
    assert v["gate_in|HOLD"] == {"verdict": "HELD", "cull_reason": None, "floor": 170.47}
    assert S.ACTIVE == ("gate_in", "HOLD")
    # a baseline between the four-policy floor and the gate: survives four_policy, HELD under gate_in|HOLD
    mid = S.verdicts(88.28, 170.47, 120.0)
    assert mid["four_policy|HOLD"]["verdict"] == "SURVIVED" and mid["gate_in|HOLD"]["verdict"] == "HELD"
    assert mid["gate_in|CULL"]["cull_reason"] == "BASELINE"


def test_survival_is_strict_and_gate_in_can_cull_a_four_policy_survivor():
    assert S.variant_verdict(100.0, 90.0, 100.0, "four_policy", "CULL")["verdict"] == "CULLED"   # equal: not >
    v = S.verdicts(100.0, 120.0, 110.0)
    assert v["four_policy|CULL"]["verdict"] == "SURVIVED" and v["gate_in|CULL"]["verdict"] == "CULLED"
    with pytest.raises(ValueError):
        S.variant_verdict(1, 1, 1, "gate", "CULL")


def test_bound_verdicts_are_exact_exactly_when_needs_learner_is_false():
    # brute force: for a bound b and every true floor F >= b, the verdicts from b equal those from F
    def labels(floor, gate, lo):
        return {k: (v["verdict"], v["cull_reason"]) for k, v in S.verdicts(floor, gate, lo).items()}

    grid = [0.0, 1.0, 2.0, 3.0, 4.0]
    flips = 0
    for b, gate, lo in itertools.product(grid, repeat=3):
        same = all(labels(b, gate, lo) == labels(F, gate, lo) for F in grid if F >= b)
        if not S.needs_learner(b, gate, lo):
            assert same, (b, gate, lo)
        flips += not same
    assert flips > 0                                                    # the rule is not vacuous
    with pytest.raises(ValueError):
        S.verdicts(1.0, 0.0, 2.0, floor_is_bound=True)
    assert S.verdicts(2.0, 1.0, 1.5, floor_is_bound=True)["four_policy|CULL"]["verdict"] == "CULLED"


def test_needs_learner_is_not_overcautious_on_a_cull_with_no_gate_headroom():
    assert not S.needs_learner(107.75, 107.75, 97.0)                   # round 3 w4: exact CULL from the bound
    assert S.needs_learner(88.28, 170.47, 50.0)                         # w1: HOLD could flip with the learner


def _cell(gs, p, floor, gate, lo):
    return {"gen_seed": gs, "pressure": p, "floor": floor, "gate_held64": gate, "verdicts": S.verdicts(floor, gate, lo)}


def test_stop_at_max_survivors_is_per_variant_in_gate_headroom_order():
    cells = [_cell(gs, "train8_held64", 10.0, 10.0 + gs, 30.0) for gs in range(1, 6)]   # all survive four_policy
    cells.append(_cell(9, "train128_held64", 10.0, 10.0, 5.0))                           # culled, headroom 0
    out = S.apply_stop(cells, max_survivors=3)
    assert [c["gen_seed"] for c in out] == [5, 4, 3, 2, 1, 9]
    fp = [c["verdicts"]["four_policy|CULL"] for c in out]
    assert [v["verdict"] for v in fp[:3]] == ["SURVIVED"] * 3
    assert [v["cull_reason"] for v in fp[3:]] == ["NOT_REACHED"] * 3
    assert fp[3]["computed"]["verdict"] == "SURVIVED" and fp[5]["computed"]["cull_reason"] == "WEAK_WORLD"
    # gate_in: floor = gate (11..15) < CI low 30, so the same three survive and the stop applies there too
    gi = [c["verdicts"]["gate_in|HOLD"] for c in out]
    assert [v["verdict"] for v in gi[:3]] == ["SURVIVED"] * 3 and gi[3]["cull_reason"] == "NOT_REACHED"
    # a variant with fewer survivors is never stopped: floor above every CI low culls all, no NOT_REACHED
    low = [_cell(gs, "train8_held64", 40.0, 40.0 + gs, 30.0) for gs in range(1, 6)]
    lo_out = S.apply_stop(low, max_survivors=3)
    assert all(c["verdicts"]["gate_in|HOLD"]["verdict"] == "HELD" for c in lo_out)
    assert all(c["verdicts"]["four_policy|CULL"]["cull_reason"] == "BASELINE" for c in lo_out)
