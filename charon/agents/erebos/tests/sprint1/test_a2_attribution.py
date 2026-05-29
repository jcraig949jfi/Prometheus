"""Tests for Sprint-1 A2 attribution harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a2_attribution import (
    PASS_THRESHOLD_ATTRIBUTION,
    run_a2,
)


def test_run_a2_returns_sprint_result():
    r = run_a2()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A2"
    assert r.metric_name == "attribution_rate"
    assert r.pass_threshold == PASS_THRESHOLD_ATTRIBUTION
    assert r.comparator == ">="
    assert 0.0 <= r.metric_value <= 1.0


def test_run_a2_is_deterministic():
    r1 = run_a2()
    r2 = run_a2()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed


def test_a2_notes_include_breakdown_counts():
    r = run_a2()
    assert "n_resolved_to_specific" in r.notes
    assert "n_unresolved" in r.notes
    assert "round-robin default" in r.notes


def test_verdict_string_marks_pass_or_fail():
    r = run_a2()
    s = r.verdict_string()
    assert ("PASS" in s) or ("FAIL" in s)
