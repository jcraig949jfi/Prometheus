"""Tests for Sprint-1 A9 revocation correctness harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a9_revocation_correctness import (
    PASS_THRESHOLD,
    _build_synthetic_ledger,
    run_a9,
)


def test_ledger_has_required_fields():
    rows = _build_synthetic_ledger()
    for r in rows:
        assert "row_id" in r
        assert "plugin_id" in r
        assert "input_signature" in r


def test_run_a9_returns_sprint_result():
    r = run_a9()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A9"
    assert r.metric_name == "revocation_propagation_rate"
    assert r.pass_threshold == PASS_THRESHOLD
    assert r.comparator == ">="
    assert 0.0 <= r.metric_value <= 1.0


def test_run_a9_is_deterministic():
    r1 = run_a9()
    r2 = run_a9()
    assert r1.metric_value == r2.metric_value


def test_run_a9_notes_flag_structural_test():
    r = run_a9()
    assert "STRUCTURAL" in r.notes
