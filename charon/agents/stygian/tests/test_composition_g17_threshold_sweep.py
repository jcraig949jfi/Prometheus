"""Tests for the G17 multi-threshold sweep refinement (ITER-18).

Locks in the phase-transition finding: M = 1.26 is the threshold
where Salem moderation switches from severable to surviving.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders.composition_g17_lehmer_label_shuffle import (
    run_g17_lehmer_label_shuffle,
)


def test_sweep_includes_expected_threshold_grid():
    """Sweep should cover the Salem cluster upper edge densely."""
    result = run_g17_lehmer_label_shuffle()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {result.get('notes')}")
    sweep = result.get("threshold_sweep", [])
    assert len(sweep) >= 9
    thresholds = [s["threshold"] for s in sweep]
    # Must cover the transition region [1.24, 1.30]
    assert any(1.24 <= t <= 1.26 for t in thresholds)
    assert 1.30 in thresholds


def test_sweep_outcomes_monotone_severable_then_survives():
    """At low M (~1.20), intervention severs; at high M (>=1.30) it
    survives. There must NOT be alternation — outcomes are monotone."""
    result = run_g17_lehmer_label_shuffle()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {result.get('notes')}")
    sweep = result.get("threshold_sweep", [])
    outcomes = [s["outcome"] for s in sweep]
    # Find the first 'survives'; everything after should also be
    # 'survives' (monotone phase transition; no flipping back)
    if "survives" in outcomes:
        first_survives_idx = outcomes.index("survives")
        for o in outcomes[first_survives_idx:]:
            assert o == "survives", (
                f"Outcome alternated after first survives: {outcomes}"
            )


def test_phase_transition_at_documented_M():
    """ITER-18 documented phase-transition M = 1.26. Lock in."""
    result = run_g17_lehmer_label_shuffle()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {result.get('notes')}")
    pt = result.get("phase_transition_M")
    assert pt is not None
    # Allow drift of one sweep step (0.02) for catalog growth
    assert 1.24 <= pt <= 1.28, (
        f"Phase transition drifted from documented 1.26 to {pt}; "
        f"investigate catalog or sweep grid change"
    )


def test_sweep_peak_observed_at_1_30():
    """Observed divergence peaks at threshold 1.30 (per ITER-4)."""
    result = run_g17_lehmer_label_shuffle()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {result.get('notes')}")
    sweep = result.get("threshold_sweep", [])
    at_130 = next((s for s in sweep if abs(s["threshold"] - 1.30) < 1e-6), None)
    assert at_130 is not None
    assert at_130["observed_divergence"] >= 0.90, (
        f"Peak observed divergence at 1.30 dropped from documented "
        f"~0.997 to {at_130['observed_divergence']}"
    )


def test_sweep_low_threshold_severable():
    """At M=1.20, observed divergence should be < null_p95 (intervention
    succeeds)."""
    result = run_g17_lehmer_label_shuffle()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {result.get('notes')}")
    sweep = result.get("threshold_sweep", [])
    at_120 = next((s for s in sweep if abs(s["threshold"] - 1.20) < 1e-6), None)
    assert at_120 is not None
    assert at_120["outcome"] == "severable", (
        f"M=1.20 outcome should be severable (intervention succeeds); "
        f"got {at_120['outcome']}"
    )


def test_sweep_notes_mention_phase_transition():
    result = run_g17_lehmer_label_shuffle()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G17 loader UNVERIFIED: {result.get('notes')}")
    if result.get("phase_transition_M") is not None:
        assert "phase-transition" in result["notes"]
