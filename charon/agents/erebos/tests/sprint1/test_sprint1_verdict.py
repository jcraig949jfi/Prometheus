"""Tests for the consolidated Sprint-1 verdict harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1.verdict import (
    KILL_RULE_MAX_FAILS,
    SprintVerdict,
    compute_verdict,
)


def test_compute_verdict_returns_well_formed_result():
    v = compute_verdict()
    assert isinstance(v, SprintVerdict)
    assert len(v.results) == 10
    assert v.n_pass + v.n_fail == 10


def test_kill_rule_threshold_is_four():
    assert KILL_RULE_MAX_FAILS == 4


def test_verdict_is_deterministic():
    v1 = compute_verdict()
    v2 = compute_verdict()
    assert v1.n_pass == v2.n_pass
    assert v1.n_fail == v2.n_fail
    assert v1.go_no_go == v2.go_no_go


def test_verdict_string_includes_all_experiments():
    v = compute_verdict()
    for i in range(1, 11):
        assert f"A{i}" in v.summary


def test_go_no_go_is_proceed_or_paused():
    v = compute_verdict()
    assert v.go_no_go in ("PROCEED", "PAUSED")


def test_kill_rule_triggered_matches_fail_count():
    v = compute_verdict()
    if v.n_fail >= KILL_RULE_MAX_FAILS:
        assert v.kill_rule_triggered is True
        assert v.go_no_go == "PAUSED"
    else:
        assert v.kill_rule_triggered is False
        assert v.go_no_go == "PROCEED"
