"""Tests for Sprint-1 A6 cross-generator transfer harness."""
from __future__ import annotations

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a6_cross_generator_transfer import (
    A6_TRANSFER_KEY_AXES,
    PASS_MARGIN,
    _shuffle_kps,
    run_a6,
)


def test_a6_key_axes_includes_invariant_and_kp():
    from charon.agents.erebos._kill_tensor import AXIS_INVARIANT, AXIS_KP
    assert AXIS_INVARIANT in A6_TRANSFER_KEY_AXES
    assert AXIS_KP in A6_TRANSFER_KEY_AXES


def test_shuffle_preserves_kp_multiset():
    """Shuffling should preserve the multiset of kps (just rearrange
    them)."""
    rows = [{"plugin_id": "p", "kill_pattern": kp}
            for kp in ["a", "a", "b", None, "c"]]
    shuffled = _shuffle_kps(rows, seed=1)
    from collections import Counter
    assert (
        Counter(r["kill_pattern"] for r in rows)
        == Counter(r["kill_pattern"] for r in shuffled)
    )


def test_run_a6_returns_sprint_result():
    r = run_a6()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A6"
    assert r.metric_name == "avg_transfer_lift_over_shuffle"
    assert r.pass_threshold == PASS_MARGIN
    assert r.comparator == ">"
    assert -1.0 <= r.metric_value <= 1.0


def test_run_a6_is_deterministic():
    r1 = run_a6()
    r2 = run_a6()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed
