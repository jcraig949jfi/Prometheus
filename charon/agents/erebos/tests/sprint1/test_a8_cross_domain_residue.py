"""Tests for Sprint-1 A8 cross-domain residue harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a8_cross_domain_residue import (
    K_PATTERN_MILESTONE,
    PASS_SPEEDUP,
    SOURCE_DOMAIN,
    TARGET_DOMAIN,
    _generate_two_domain_ledger,
    run_a8,
)


def test_two_domain_ledger_has_both_domains():
    rows = _generate_two_domain_ledger()
    domains = {r["domain"] for r in rows}
    assert SOURCE_DOMAIN in domains
    assert TARGET_DOMAIN in domains


def test_run_a8_returns_sprint_result():
    r = run_a8()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A8"
    assert r.metric_name == "speedup_to_K_patterns_synthetic"
    assert r.pass_threshold == PASS_SPEEDUP
    assert r.comparator == ">"


def test_run_a8_is_deterministic():
    r1 = run_a8()
    r2 = run_a8()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed


def test_run_a8_notes_flag_synthetic_substitute():
    """The findings must make clear this is not the real-data
    test."""
    r = run_a8()
    assert "SYNTHETIC SUBSTITUTE" in r.notes
    assert "BSD" in r.notes
