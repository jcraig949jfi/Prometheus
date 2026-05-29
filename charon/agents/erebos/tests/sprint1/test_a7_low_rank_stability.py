"""Tests for Sprint-1 A7 low-rank stability harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a7_low_rank_stability import (
    PASS_THRESHOLD_RATIO,
    _generate_stream,
    run_a7,
)


def test_stream_size():
    rows = _generate_stream(100, seed=1)
    assert len(rows) == 100


def test_stream_seed_reproducible():
    r1 = _generate_stream(50, seed=99)
    r2 = _generate_stream(50, seed=99)
    for a, b in zip(r1, r2):
        assert a == b


def test_run_a7_returns_sprint_result():
    r = run_a7()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A7"
    assert r.metric_name == "late_rate_over_early_rate"
    assert r.pass_threshold == PASS_THRESHOLD_RATIO
    assert r.comparator == "<"
    assert r.metric_value >= 0.0


def test_run_a7_is_deterministic():
    r1 = run_a7()
    r2 = run_a7()
    assert r1.metric_value == r2.metric_value
