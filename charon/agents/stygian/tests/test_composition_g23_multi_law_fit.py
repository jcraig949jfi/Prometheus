"""Tests for the G23 multi-law decay-fit refinement (ITER-17).

Validates:
- Linear regression primitive (slope, R^2)
- Multi-law candidate fitting (1/N, 1/log N, 1/sqrt N, exp(-N))
- Best-fit selection by R^2
- Live result: 1/log(N) beats 1/N on Mossinghoff per-degree minima
"""
from __future__ import annotations

import math

import pytest

from charon.agents.stygian.loaders.composition_g23_lehmer_degree_decay import (
    DECAY_SLOPE_TOLERANCE,
    _linear_regression,
    run_g23_lehmer_degree_decay,
)


# ---------------------------------------------------------------------
# Linear regression primitive
# ---------------------------------------------------------------------

def test_regression_recovers_perfect_line():
    """y = 2x + 3 exactly -> slope=2, intercept=3, R^2=1."""
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [5.0, 7.0, 9.0, 11.0, 13.0]
    fit = _linear_regression(xs, ys)
    assert fit is not None
    assert abs(fit["slope"] - 2.0) < 1e-9
    assert abs(fit["intercept"] - 3.0) < 1e-9
    assert abs(fit["r_squared"] - 1.0) < 1e-9


def test_regression_returns_none_for_constant_x():
    """Zero variance in x -> can't fit."""
    fit = _linear_regression([1.0, 1.0, 1.0], [5.0, 7.0, 9.0])
    assert fit is None


def test_regression_returns_none_for_too_few_points():
    """Need at least 2 points."""
    fit = _linear_regression([1.0], [5.0])
    assert fit is None


def test_regression_low_r_squared_for_noise():
    """Pure noise should have low R^2."""
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [3.0, 1.0, 4.0, 1.0, 5.0]  # noise
    fit = _linear_regression(xs, ys)
    assert fit is not None
    assert fit["r_squared"] < 0.5


# ---------------------------------------------------------------------
# Live Mossinghoff multi-law fit: 1/log(N) beats 1/N
# ---------------------------------------------------------------------

def test_live_decay_fit_returns_candidate_laws():
    result = run_g23_lehmer_degree_decay()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G23 loader UNVERIFIED: {result.get('notes')}")
    laws = result.get("candidate_laws", [])
    # Should have at least 4 candidate laws (constant filtered out)
    assert len(laws) >= 4
    law_names = {l["name"] for l in laws}
    assert "1/N" in law_names
    assert "1/log(N)" in law_names
    assert "1/sqrt(N)" in law_names


def test_live_best_fit_is_logarithmic():
    """Per ITER-17 finding: 1/log(N) beats 1/N on the live catalog."""
    result = run_g23_lehmer_degree_decay()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G23 loader UNVERIFIED: {result.get('notes')}")
    best = result.get("best_fit_law")
    assert best is not None
    # The Mossinghoff per-degree minimum-Mahler error decays best as
    # 1/log(N) per ITER-17 empirical result; document this so any
    # future data shift triggers the test.
    assert best["name"] == "1/log(N)", (
        f"Best-fit law was {best['name']}, expected 1/log(N) per "
        f"ITER-17 empirical result. Either Mossinghoff catalog data "
        f"has shifted or the multi-law fit logic changed."
    )
    assert best["r_squared"] >= 0.40


def test_live_verdict_still_rejects_naive_1_over_N():
    """The classification verdict is independent of multi-law fit;
    the naive 1/N test still rejects per ITER-11."""
    result = run_g23_lehmer_degree_decay()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G23 loader UNVERIFIED: {result.get('notes')}")
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "error_term_does_not_decay"


def test_live_log_log_slope_well_below_decay_tolerance():
    """log-log slope of M_min curve is shallow (~0.2) — far from the
    -1.0 that O(1/N) would predict."""
    result = run_g23_lehmer_degree_decay()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G23 loader UNVERIFIED: {result.get('notes')}")
    slope = result["slope"]
    # Documented ITER-11 result: slope ≈ -0.205
    assert -0.5 <= slope <= 0.0, (
        f"Slope drifted from documented ~-0.21 to {slope}; catalog "
        f"distribution may have shifted."
    )
    # And it's NOT within DECAY_SLOPE_TOLERANCE of -1.0
    assert abs(slope - (-1.0)) > DECAY_SLOPE_TOLERANCE


# ---------------------------------------------------------------------
# Best-fit notes addendum
# ---------------------------------------------------------------------

def test_notes_mention_best_fit_when_substantially_better():
    """If best-fit R^2 is much higher than log-log fit, the notes
    should mention it."""
    result = run_g23_lehmer_degree_decay()
    if result.get("verdict") == "UNVERIFIED":
        pytest.skip(f"G23 loader UNVERIFIED: {result.get('notes')}")
    best = result.get("best_fit_law")
    if best is None:
        pytest.skip("No best-fit law computed")
    log_log_r2 = result["r_squared"]
    if best["r_squared"] > log_log_r2 + 0.05:
        # Addendum should fire
        assert "Multi-law best fit" in result["notes"]
        assert best["name"] in result["notes"]
