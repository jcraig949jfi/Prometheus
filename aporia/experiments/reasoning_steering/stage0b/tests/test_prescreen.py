"""TDD tests for the signal pre-screen (Stage 0b) -- a FAST curl measure.

Centerpiece (the finding): anti-correlation does NOT imply curl. A set with a strongly
NEGATIVE pair that is still WEIGHTABLE (no 3-cycle) must FAIL the screen -- because a
scalar still orders the states. Only genuine CYCLIC (Condorcet) inconsistency passes.
"""
import pytest

from aporia.experiments.reasoning_steering.stage0b.prescreen import (
    signal_screen, ScreenResult,
)

# Condorcet 3-cycle: cyclic, non-weightable -> real curl.
CONDORCET = [
    {"margins": {"f1": 3, "f2": 1, "f3": 2}},
    {"margins": {"f1": 2, "f2": 3, "f3": 1}},
    {"margins": {"f1": 1, "f2": 2, "f3": 3}},
]
# Redundant: all agree -> gradient.
REDUNDANT = [{"margins": {"f1": float(v), "f2": float(v), "f3": float(v)}}
             for v in (6, 5, 4, 3, 2, 1)]
# Anti-correlated but WEIGHTABLE: f2 = -f1, f3 = f1 (a scalar = f1 orders all).
# Strong negative pair (f1,f2 ~ -1) yet NO cycle -> must FAIL despite anti-correlation.
ANTICORR_WEIGHTABLE = [{"margins": {"f1": float(i), "f2": float(-i), "f3": float(i)}}
                       for i in (1, 2, 3, 4, 5, 6)]


# 1. AUTHORITY
def test_authority_condorcet_passes():
    sc = signal_screen(CONDORCET, quick_null=80, seed=1)
    assert sc.verdict == "PASS"
    assert sc.observed_non_gradient_mass > sc.quick_null_mean


def test_authority_redundant_fails():
    sc = signal_screen(REDUNDANT, quick_null=80, seed=1)
    assert sc.verdict == "FAIL_NO_CURL"


# 2. THE FINDING — anti-correlation alone does NOT pass (it's still weightable).
def test_anticorrelation_without_cycle_fails():
    sc = signal_screen(ANTICORR_WEIGHTABLE, quick_null=80, seed=1)
    assert sc.min_corr < -0.5                 # a strongly anti-correlated pair EXISTS
    assert sc.n_negative_pairs >= 1           # ... and the correlation diagnostic sees it
    assert sc.verdict == "FAIL_NO_CURL"       # ... yet there is no curl (weightable)


# 3. PROPERTY / structure
def test_property_result_fields():
    sc = signal_screen(CONDORCET, quick_null=60, seed=0)
    assert isinstance(sc, ScreenResult)
    assert 0.0 <= sc.observed_non_gradient_mass <= 1.0
    assert sc.verdict in ("PASS", "FAIL_NO_CURL", "FAIL_TOO_FEW")
    assert sc.predicted_signal in ("worth_running", "unlikely")


# 4. EDGE CASES
def test_edge_cases():
    two = [{"margins": {"f1": float(i), "f2": float(2 * i)}} for i in range(5)]
    assert signal_screen(two).verdict == "FAIL_TOO_FEW"          # only 2 evaluators
    with pytest.raises(ValueError):
        signal_screen(CONDORCET[:2])                             # < 3 states
