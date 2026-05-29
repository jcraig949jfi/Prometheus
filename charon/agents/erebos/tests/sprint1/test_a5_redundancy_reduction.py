"""Tests for Sprint-1 A5 redundancy reduction harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a5_redundancy_reduction import (
    PASS_THRESHOLD_SLOPE,
    _linear_slope,
    run_a5,
)


def test_linear_slope_perfect_line():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [2.0, 4.0, 6.0, 8.0]
    assert abs(_linear_slope(xs, ys) - 2.0) < 1e-9


def test_linear_slope_flat_line():
    xs = [1.0, 2.0, 3.0]
    ys = [5.0, 5.0, 5.0]
    assert _linear_slope(xs, ys) == 0.0


def test_linear_slope_too_few_points():
    assert _linear_slope([], []) == 0.0
    assert _linear_slope([1.0], [1.0]) == 0.0


def test_linear_slope_negative():
    xs = [1.0, 2.0, 3.0, 4.0]
    ys = [4.0, 3.0, 2.0, 1.0]
    assert _linear_slope(xs, ys) == -1.0


def test_run_a5_returns_sprint_result():
    r = run_a5()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A5"
    assert r.metric_name == "eligibility_rate_slope_second_half"
    assert r.pass_threshold == PASS_THRESHOLD_SLOPE
    assert r.comparator == "<"


def test_run_a5_is_deterministic():
    r1 = run_a5()
    r2 = run_a5()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed
