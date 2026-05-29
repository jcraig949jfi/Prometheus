"""Tests for Sprint-1 A3 predictive power harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a3_predictive_power import (
    GENERATIVE_MODEL,
    N_EMISSIONS,
    PASS_MARGIN,
    TRAIN_FRACTION,
    _macro_f1,
    generate_synthetic_ledger,
    run_a3,
)


def test_ledger_size():
    rows = generate_synthetic_ledger(n=100)
    assert len(rows) == 100


def test_ledger_seed_reproducible():
    r1 = generate_synthetic_ledger(n=50, seed=99)
    r2 = generate_synthetic_ledger(n=50, seed=99)
    for a, b in zip(r1, r2):
        assert a.plugin_id == b.plugin_id
        assert a.domain == b.domain
        assert a.kill_pattern == b.kill_pattern


def test_macro_f1_perfect_prediction():
    """All correct -> F1 = 1.0."""
    y_true = ["a", "b", "a", "b"]
    y_pred = ["a", "b", "a", "b"]
    assert _macro_f1(y_true, y_pred) == 1.0


def test_macro_f1_completely_wrong():
    """All wrong on binary -> F1 = 0.0."""
    y_true = ["a", "a", "a", "a"]
    y_pred = ["b", "b", "b", "b"]
    assert _macro_f1(y_true, y_pred) == 0.0


def test_run_a3_returns_sprint_result():
    r = run_a3()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A3"
    assert r.metric_name == "macro_f1_lift_over_random"
    assert r.pass_threshold == PASS_MARGIN
    assert r.comparator == ">"
    # Lift can be negative if predictor is bad
    assert -1.0 <= r.metric_value <= 1.0


def test_run_a3_is_deterministic():
    r1 = run_a3()
    r2 = run_a3()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed
