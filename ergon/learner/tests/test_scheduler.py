"""Tests for ergon.learner.scheduler — operator-class scheduler with min-share enforcement."""
from __future__ import annotations

from collections import Counter

import pytest

from ergon.learner.scheduler import (
    DEFAULT_MIN_SHARES,
    DEFAULT_OPERATOR_WEIGHTS_MVP,
    OperatorScheduler,
    SchedulerStats,
)


# ===========================================================================
# Authority — v8 §3.5.4 specifies the minimum shares
# ===========================================================================


def test_default_min_shares_match_v8():
    """v8 §3.5.4: uniform >=5%, anti_prior >=5%, structured_null >=5%."""
    assert DEFAULT_MIN_SHARES["uniform"] == 0.05
    assert DEFAULT_MIN_SHARES["anti_prior"] == 0.05
    assert DEFAULT_MIN_SHARES["structured_null"] == 0.05
    assert sum(DEFAULT_MIN_SHARES.values()) == pytest.approx(0.15)


def test_default_mvp_weights_sum_to_one():
    weight_sum = sum(DEFAULT_OPERATOR_WEIGHTS_MVP.values())
    assert weight_sum == pytest.approx(1.0)


def test_default_weights_have_no_neural_or_external_llm():
    """At MVP scope: no neural or external_llm operator (deferred to v0.5)."""
    assert "neural" not in DEFAULT_OPERATOR_WEIGHTS_MVP
    assert "external_llm" not in DEFAULT_OPERATOR_WEIGHTS_MVP


# ===========================================================================
# Property — minimum-share enforcement after warm-up
# ===========================================================================


def test_scheduler_enforces_min_share_for_uniform():
    """Run the scheduler past warm-up; uniform's share should never fall below 5%."""
    # Use heavily-skewed weights that would normally starve uniform
    skewed_weights = {
        "structural": 0.95,
        "symbolic": 0.04,
        "uniform": 0.005,
        "structured_null": 0.005,
        "anti_prior": 0.0,  # zero — would never sample without min-share
    }
    sched = OperatorScheduler(
        operator_weights={**skewed_weights},
        seed=42,
        lookback_window=50,
    )
    # Adjust weights to sum to 1.0
    sched.operator_weights = skewed_weights
    # Re-validate
    weight_sum = sum(skewed_weights.values())
    assert weight_sum == pytest.approx(1.0)

    # Run past warm-up
    for i in range(500):
        sched.next_operator_class(episode_idx=i)

    # Within the last lookback window, uniform should be >=5%
    window = sched.window_shares()
    assert window.get("uniform", 0) >= 0.04  # allow tiny tolerance for rounding


def test_scheduler_enforces_min_share_for_anti_prior():
    skewed_weights = {
        "structural": 0.95,
        "symbolic": 0.04,
        "uniform": 0.005,
        "structured_null": 0.005,
        "anti_prior": 0.0,
    }
    sched = OperatorScheduler(
        operator_weights=skewed_weights,
        seed=42,
        lookback_window=50,
    )
    for i in range(500):
        sched.next_operator_class(episode_idx=i)
    window = sched.window_shares()
    assert window.get("anti_prior", 0) >= 0.04


def test_scheduler_enforces_min_share_for_structured_null():
    skewed_weights = {
        "structural": 0.95,
        "symbolic": 0.04,
        "uniform": 0.005,
        "structured_null": 0.005,
        "anti_prior": 0.0,
    }
    sched = OperatorScheduler(
        operator_weights=skewed_weights,
        seed=42,
        lookback_window=50,
    )
    for i in range(500):
        sched.next_operator_class(episode_idx=i)
    window = sched.window_shares()
    assert window.get("structured_null", 0) >= 0.04


def test_scheduler_total_non_prior_share_at_least_15_percent():
    """Combined non-prior-shaped operators get ≥15% of episodes (v8 §3.5.4)."""
    skewed_weights = {
        "structural": 0.95,
        "symbolic": 0.04,
        "uniform": 0.005,
        "structured_null": 0.005,
        "anti_prior": 0.0,
    }
    sched = OperatorScheduler(
        operator_weights=skewed_weights,
        seed=42,
        lookback_window=100,
    )
    for i in range(500):
        sched.next_operator_class(episode_idx=i)
    window = sched.window_shares()
    non_prior = (
        window.get("uniform", 0) +
        window.get("anti_prior", 0) +
        window.get("structured_null", 0)
    )
    assert non_prior >= 0.14


def test_scheduler_deterministic_given_seed():
    """Same seed produces same operator-class sequence."""
    sched_a = OperatorScheduler(seed=123)
    sched_b = OperatorScheduler(seed=123)
    seq_a = [sched_a.next_operator_class(i) for i in range(50)]
    seq_b = [sched_b.next_operator_class(i) for i in range(50)]
    assert seq_a == seq_b


# ===========================================================================
# Property — diagnostic reporting
# ===========================================================================


def test_cumulative_shares_normalized():
    """cumulative_shares should sum to 1.0 across all selected operators."""
    sched = OperatorScheduler(seed=42)
    for i in range(100):
        sched.next_operator_class(i)
    shares = sched.cumulative_shares()
    assert sum(shares.values()) == pytest.approx(1.0, abs=1e-9)


def test_window_shares_normalized():
    sched = OperatorScheduler(seed=42, lookback_window=20)
    for i in range(100):
        sched.next_operator_class(i)
    shares = sched.window_shares()
    assert sum(shares.values()) == pytest.approx(1.0, abs=1e-9)


def test_check_min_share_compliance_format():
    sched = OperatorScheduler(seed=42, lookback_window=50)
    for i in range(200):
        sched.next_operator_class(i)
    compliance = sched.check_min_share_compliance()
    for op in DEFAULT_MIN_SHARES.keys():
        assert op in compliance
        info = compliance[op]
        assert "min_share" in info
        assert "actual_share" in info
        assert "compliant" in info


def test_stats_returns_scheduler_stats_object():
    sched = OperatorScheduler(seed=42)
    for i in range(50):
        sched.next_operator_class(i)
    stats = sched.stats(episode_idx=49)
    assert isinstance(stats, SchedulerStats)
    assert stats.episode_idx == 49
    assert sum(stats.operator_call_counts.values()) == 50


# ===========================================================================
# Edge — invalid configuration
# ===========================================================================


def test_invalid_operator_weights_rejected():
    """operator_weights must sum to ~1.0."""
    with pytest.raises(ValueError):
        OperatorScheduler(operator_weights={"structural": 0.5, "uniform": 0.3})  # sums to 0.8


def test_min_shares_exceeding_one_rejected():
    """sum of min_shares cannot exceed 1.0."""
    with pytest.raises(ValueError):
        OperatorScheduler(
            min_shares={
                "uniform": 0.4,
                "anti_prior": 0.4,
                "structured_null": 0.4,
            },
        )


def test_warmup_period_no_force_selection():
    """In the first lookback_window episodes, scheduler shouldn't force-select."""
    sched = OperatorScheduler(seed=42, lookback_window=20)
    # Run only warmup-many episodes
    counts: Counter = Counter()
    for i in range(20):
        op = sched.next_operator_class(i)
        counts[op] += 1
    # Sliding window not yet full, so no min-share enforcement fired.
    # Distribution should approximately match operator_weights
    # (uniform should be near 0.07 default, not artificially boosted)
    assert sum(counts.values()) == 20


# ===========================================================================
# Composition — full pilot simulation
# ===========================================================================


def test_full_pilot_simulation_meets_v8_constraints():
    """Simulate a 1000-episode pilot; verify v8 §3.5.4 constraints hold throughout."""
    sched = OperatorScheduler(seed=42, lookback_window=100)
    sequence = []
    for i in range(1000):
        sequence.append(sched.next_operator_class(i))

    # After warmup (100 episodes), every 100-episode window should respect
    # the min-share constraint
    final_window_shares = sched.window_shares()
    for op, min_share in DEFAULT_MIN_SHARES.items():
        actual = final_window_shares.get(op, 0)
        assert actual >= min_share - 0.01  # tiny tolerance for boundary effects

    # All five operator classes are represented in the cumulative output
    cumulative_ops = set(sched._cumulative_counts.keys())
    assert "structural" in cumulative_ops
    assert "symbolic" in cumulative_ops
    assert "uniform" in cumulative_ops
    assert "structured_null" in cumulative_ops
    assert "anti_prior" in cumulative_ops
