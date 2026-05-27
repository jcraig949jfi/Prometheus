"""Synthetic-control tests for G18 minimal-counterexample loader.

Locks in the ITER-10 substrate self-correction (M_COMPARISON_EPSILON
fix for Lehmer-x-cyclotomic ULP false-positives) as a unit test that
will fire if anyone removes or weakens the epsilon tolerance.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders.composition_g18_lehmer_degree_band import (
    DEGREE_BAND_CEILING,
    DEGREE_BAND_FLOOR,
    M_COMPARISON_EPSILON,
    _find_counterexamples_in_band,
)
from charon.agents.stygian.loaders._mahler_composition_helpers import M_LEHMER


# ---------------------------------------------------------------------
# Epsilon-tolerance ULP fix (ITER-10 substrate self-correction)
# ---------------------------------------------------------------------

def test_lehmer_itself_is_not_a_counterexample(monkeypatch):
    """Lehmer's polynomial (M = M_LEHMER exactly) must NOT be flagged
    as a counterexample to its own bound."""
    import charon.agents.stygian.loaders.composition_g18_lehmer_degree_band as g18_mod

    def fake_loader(upper_M=2.0):
        return [{
            "degree": 10,
            "mahler_measure": M_LEHMER,
            "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
            "name": "Lehmer",
        }]

    monkeypatch.setattr(
        g18_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    cex = _find_counterexamples_in_band(
        degree_floor=10, degree_ceiling=20, M_threshold=M_LEHMER,
    )
    assert cex == [], (
        f"Lehmer's polynomial flagged as counterexample to its own bound; "
        f"epsilon tolerance is broken. cex={cex}"
    )


def test_lehmer_cyclotomic_extension_not_counterexample(monkeypatch):
    """Lehmer x Phi_k has M numerically within ULPs of M_LEHMER due to
    floating-point rounding. The original bug at ITER-10. This test
    locks in the epsilon fix."""
    import charon.agents.stygian.loaders.composition_g18_lehmer_degree_band as g18_mod

    # Real value from ITER-10 substrate self-correction
    M_LEHMER_X_PHI_16 = 1.1762808182599174  # 2 ULPs below M_LEHMER

    def fake_loader(upper_M=2.0):
        return [{
            "degree": 18,
            "mahler_measure": M_LEHMER_X_PHI_16,
            "coeffs": [1, 1, 0, -1, -1, -1, -1, -1, 1, 2, 1, -1, -1, -1, -1, -1, 0, 1, 1],
            "name": "Lehmer x Phi_16",
        }]

    monkeypatch.setattr(
        g18_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    cex = _find_counterexamples_in_band(
        degree_floor=10, degree_ceiling=20, M_threshold=M_LEHMER,
    )
    assert cex == [], (
        f"Lehmer x Phi_16 flagged as counterexample due to ULP noise; "
        f"M_COMPARISON_EPSILON fix is broken. cex={cex}"
    )


def test_genuinely_below_lehmer_IS_counterexample(monkeypatch):
    """A polynomial with M genuinely below M_LEHMER by more than
    epsilon SHOULD be flagged. If this test fails, the epsilon
    tolerance is too loose."""
    import charon.agents.stygian.loaders.composition_g18_lehmer_degree_band as g18_mod

    GENUINE_BREAK_M = M_LEHMER - 0.001  # 1 millionth of a unit below
    assert GENUINE_BREAK_M < M_LEHMER - M_COMPARISON_EPSILON

    def fake_loader(upper_M=2.0):
        return [{
            "degree": 15,
            "mahler_measure": GENUINE_BREAK_M,
            "coeffs": [],
            "name": "synthetic_counterexample",
        }]

    monkeypatch.setattr(
        g18_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    cex = _find_counterexamples_in_band(
        degree_floor=10, degree_ceiling=20, M_threshold=M_LEHMER,
    )
    assert len(cex) == 1, (
        f"Genuine M < M_LEHMER counterexample missed; epsilon too "
        f"loose. cex={cex}"
    )


def test_outside_degree_band_skipped(monkeypatch):
    """Entries with degree outside [floor, ceiling] are skipped even
    if they would otherwise be counterexamples."""
    import charon.agents.stygian.loaders.composition_g18_lehmer_degree_band as g18_mod

    def fake_loader(upper_M=2.0):
        return [{
            "degree": 4,  # below floor
            "mahler_measure": M_LEHMER - 0.01,
            "coeffs": [],
            "name": "low-degree",
        }]

    monkeypatch.setattr(
        g18_mod, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    cex = _find_counterexamples_in_band(
        degree_floor=10, degree_ceiling=20, M_threshold=M_LEHMER,
    )
    assert cex == []


def test_epsilon_value_is_sane():
    """The epsilon should be much smaller than any plausible distinct-M
    gap in the catalog (~1e-3) and much larger than double-precision
    ULP noise (~1e-15)."""
    assert 1e-13 < M_COMPARISON_EPSILON < 1e-3


def test_default_degree_band_bounds_are_sane():
    """Default band [10, 36] covers Lehmer's degree (10) through the
    Mossinghoff catalog ceiling (36)."""
    assert DEGREE_BAND_FLOOR == 10
    assert DEGREE_BAND_CEILING == 36
