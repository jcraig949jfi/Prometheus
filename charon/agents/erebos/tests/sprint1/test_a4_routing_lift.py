"""Tests for Sprint-1 A4 routing lift harness."""
from __future__ import annotations

from collections import Counter

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a4_routing_lift import (
    PASS_THRESHOLD_RATIO,
    _shannon_entropy_bits,
    run_a4,
)


def test_entropy_zero_for_empty_counter():
    assert _shannon_entropy_bits(Counter()) == 0.0


def test_entropy_zero_for_single_class():
    """Mass concentrated on one class -> H = 0."""
    c = Counter({"a": 10})
    assert _shannon_entropy_bits(c) == 0.0


def test_entropy_one_for_uniform_binary():
    """50/50 distribution over two classes -> H = 1 bit."""
    c = Counter({"a": 5, "b": 5})
    assert abs(_shannon_entropy_bits(c) - 1.0) < 1e-9


def test_entropy_log2_for_uniform_n_classes():
    """Uniform over N classes -> H = log2(N)."""
    import math
    c = Counter({f"c{i}": 1 for i in range(8)})
    assert abs(_shannon_entropy_bits(c) - 3.0) < 1e-9


def test_run_a4_returns_sprint_result():
    r = run_a4()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A4"
    assert r.metric_name == "eig_ratio_kp_over_rr"
    assert r.pass_threshold == PASS_THRESHOLD_RATIO
    assert r.comparator == ">"
    assert r.metric_value >= 0.0


def test_run_a4_is_deterministic():
    r1 = run_a4()
    r2 = run_a4()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed
