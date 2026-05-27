"""Synthetic smooth-control calibration for G10's smoothness_ratio.

Per pivot/erebos_substrate_finding_iter10_g10_salem_cluster_
detection_2026-05-26.md follow-up #1: validate that G10's
SMOOTH_THRESHOLD = 3.0 returns ratio < 3.0 on a deliberately-
smooth synthetic distribution, AND >= 3.0 on a deliberately-
cliff'd one. Without this control, the threshold could be
arbitrary; with it, we have a falsifiable calibration point on
both sides of the boundary.
"""
from __future__ import annotations

import math

import pytest

from charon.agents.stygian.loaders.composition_g10_lehmer_threshold_sweep import (
    SMOOTH_THRESHOLD,
    _first_differences,
    _smoothness_ratio,
)


def _synthetic_uniform_distribution(n: int = 1000) -> list[float]:
    """Uniform on [1.0, 2.0]. Survival fraction at threshold t is
    (2.0 - t) / 1.0 = 2 - t for t in [1.0, 2.0]. The first-difference
    sequence across uniformly-spaced thresholds is constant, so
    smoothness_ratio should be exactly 1.0 (perfectly smooth)."""
    return [1.0 + (i / (n - 1)) for i in range(n)]


def _synthetic_cliff_distribution(n: int = 1000, cliff_at: float = 1.3) -> list[float]:
    """All values cluster just below cliff_at, with a thin tail above.
    Survival fraction at threshold = cliff_at - epsilon stays near 1;
    just above cliff_at, plummets to near 0. Cliff dominates the
    first-difference sequence; smoothness_ratio should be >> 3.0."""
    n_below = int(0.95 * n)
    n_above = n - n_below
    below = [cliff_at - 0.001 - (i / (10 * n_below)) for i in range(n_below)]
    above = [cliff_at + 0.01 + (i / (10 * n_above)) for i in range(n_above)]
    return sorted(below + above)


def _survival_at(values: list[float], t: float) -> float:
    return sum(1 for v in values if v >= t) / len(values)


def test_synthetic_uniform_yields_smooth_ratio():
    """Uniform [1.0, 2.0] swept on uniform thresholds → ratio ~ 1.0,
    far below SMOOTH_THRESHOLD."""
    values = _synthetic_uniform_distribution()
    thresholds = [1.0 + 0.1 * i for i in range(11)]  # 1.0, 1.1, ..., 2.0
    survivals = [_survival_at(values, t) for t in thresholds]
    diffs = _first_differences(survivals)
    ratio = _smoothness_ratio(diffs)
    assert ratio < SMOOTH_THRESHOLD, (
        f"Uniform distribution should yield smooth ratio < "
        f"{SMOOTH_THRESHOLD}, got {ratio:.4f}"
    )
    # Tighter check: uniform should yield ratio very close to 1.0
    assert ratio < 1.5, (
        f"Uniform distribution should yield ratio close to 1.0, "
        f"got {ratio:.4f}"
    )


def test_synthetic_cliff_yields_high_ratio():
    """Cliff distribution → ratio >> SMOOTH_THRESHOLD."""
    values = _synthetic_cliff_distribution(cliff_at=1.3)
    thresholds = [1.0 + 0.1 * i for i in range(11)]  # 1.0, 1.1, ..., 2.0
    survivals = [_survival_at(values, t) for t in thresholds]
    diffs = _first_differences(survivals)
    ratio = _smoothness_ratio(diffs)
    assert ratio > SMOOTH_THRESHOLD, (
        f"Cliff distribution should yield ratio > {SMOOTH_THRESHOLD}, "
        f"got {ratio:.4f}"
    )


def test_smoothness_ratio_handles_empty_diffs():
    assert _smoothness_ratio([]) == 0.0


def test_smoothness_ratio_handles_zero_mean():
    """All-zero diffs (no change anywhere) → ratio = 0 by convention."""
    assert _smoothness_ratio([0.0, 0.0, 0.0]) == 0.0


def test_smoothness_ratio_computes_max_over_mean():
    """ratio = max(|d|) / mean(|d|). Manual check: [1, 1, 4] → 4 / 2 = 2.0"""
    assert _smoothness_ratio([1.0, 1.0, 4.0]) == 2.0


def test_smooth_threshold_is_sane():
    """SMOOTH_THRESHOLD should be > 1.0 (uniform yields 1.0) and < 6.7
    (the observed Salem-cluster ratio). 3.0 sits cleanly in between."""
    assert SMOOTH_THRESHOLD > 1.0
    assert SMOOTH_THRESHOLD < 6.7  # observed Salem cluster value
