"""TDD suite for prometheus_math.calibration — the four required categories."""
from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.calibration import (  # noqa: E402
    CalibrationError, brier_score, expected_calibration_error, murphy_decomposition,
)


# ---- 1. authority --------------------------------------------------------------------------

def test_brier_matches_hand_computed_values():
    """Hand computation, from the definition BS = (1/N) Σ (p_i − y_i)².

    Forecasts (0.9, 0.1, 0.8), outcomes (1, 0, 0):
        (0.9−1)² = 0.01, (0.1−0)² = 0.01, (0.8−0)² = 0.64  ⇒  0.66/3 = 0.22.
    A perfect forecaster scores 0; a maximally wrong one scores 1.
    """
    assert brier_score([0.9, 0.1, 0.8], [1, 0, 0]) == pytest.approx(0.22)
    assert brier_score([1.0, 0.0], [1, 0]) == 0.0
    assert brier_score([0.0, 1.0], [1, 0]) == 1.0


def test_murphy_partition_on_the_reference_shape():
    """Reference: Murphy (1973), *J. Appl. Meteorol.* 12, 595–600 — BS = REL − RES + UNC.

    Hand-checkable instance: forecast 0.5 on four claims, two of which are true.
        base rate ȳ = 0.5; one forecast group at p = 0.5 with ȳ_k = 0.5
        reliability = (0.5 − 0.5)² = 0        (perfectly reliable)
        resolution  = (0.5 − 0.5)² = 0        (carries no information)
        uncertainty = 0.5 × 0.5   = 0.25
        BS = 0 − 0 + 0.25 = 0.25 ✓
    """
    m = murphy_decomposition([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0])
    assert m.reliability == pytest.approx(0.0)
    assert m.resolution == pytest.approx(0.0)
    assert m.uncertainty == pytest.approx(0.25)
    assert m.brier == pytest.approx(0.25)
    assert m.skill == pytest.approx(0.0)          # exactly no better than the base rate


def test_perfect_forecaster_has_zero_reliability_and_full_resolution():
    """A forecaster that says 1.0 on every true claim and 0.0 on every false one attains
    reliability 0, resolution = uncertainty, and skill 1."""
    m = murphy_decomposition([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0])
    assert m.brier == pytest.approx(0.0)
    assert m.reliability == pytest.approx(0.0)
    assert m.resolution == pytest.approx(m.uncertainty)
    assert m.skill == pytest.approx(1.0)


# ---- 2. property (Hypothesis) ----------------------------------------------------------------

probs = st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False), min_size=1,
                 max_size=40)


@settings(max_examples=200, deadline=None)
@given(st.data())
def test_murphy_identity_holds_exactly(data):
    """THE invariant: BS = reliability − resolution + uncertainty, exact under binning by
    distinct forecast value."""
    n = data.draw(st.integers(min_value=1, max_value=40))
    ps = data.draw(st.lists(st.floats(0.0, 1.0, allow_nan=False), min_size=n, max_size=n))
    ys = data.draw(st.lists(st.integers(0, 1), min_size=n, max_size=n))
    m = murphy_decomposition(ps, ys)
    assert abs(m.identity_residual) < 1e-9


@settings(max_examples=150, deadline=None)
@given(st.data())
def test_all_scores_stay_in_their_ranges(data):
    n = data.draw(st.integers(min_value=1, max_value=30))
    ps = data.draw(st.lists(st.floats(0.0, 1.0, allow_nan=False), min_size=n, max_size=n))
    ys = data.draw(st.lists(st.integers(0, 1), min_size=n, max_size=n))
    m = murphy_decomposition(ps, ys)
    assert 0.0 <= m.brier <= 1.0
    assert m.reliability >= 0.0 and m.resolution >= 0.0
    assert 0.0 <= m.uncertainty <= 0.25
    assert 0.0 <= expected_calibration_error(ps, ys) <= 1.0


@settings(max_examples=100, deadline=None)
@given(st.data())
def test_brier_is_proper_reporting_the_true_rate_beats_any_other_constant(data):
    """Propriety, the property that makes Brier resistant to hedging: against a battery whose
    base rate is r, the constant forecast r scores at least as well as any other constant.
    Checked against a grid of alternatives."""
    n = data.draw(st.integers(min_value=4, max_value=30))
    ys = data.draw(st.lists(st.integers(0, 1), min_size=n, max_size=n))
    r = sum(ys) / n
    honest = brier_score([r] * n, ys)
    for alt in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0):
        assert honest <= brier_score([alt] * n, ys) + 1e-12


# ---- 3. edge cases ---------------------------------------------------------------------------

def test_calibration_edges():
    """Edges covered:
    - empty input: CalibrationError (a score over nothing is undefined, NOT 0)
    - length mismatch: CalibrationError
    - forecast outside [0, 1]: CalibrationError
    - non-binary outcome: CalibrationError
    - bins < 1: CalibrationError
    - singleton input: defined, and uncertainty collapses to 0
    - degenerate battery (all outcomes identical): uncertainty 0, skill defined as 0
    - p exactly 1.0: must land in the last bin, not overflow it
    """
    with pytest.raises(CalibrationError):
        brier_score([], [])
    with pytest.raises(CalibrationError):
        brier_score([0.5], [1, 0])
    with pytest.raises(CalibrationError):
        brier_score([1.5], [1])
    with pytest.raises(CalibrationError):
        brier_score([0.5], [2])
    with pytest.raises(CalibrationError):
        expected_calibration_error([0.5], [1], bins=0)

    # CYCLE 039: these two assertions USED TO READ `skill == 0.0`, and that was the bug being
    # encoded by its own test — 0.0 meant "no skill" and "skill undefined" at once. On a
    # degenerate battery the base-rate forecaster is already perfect, so there is nothing to be
    # better than and skill has no value. It now refuses; a caller wanting a number opts in.
    single = murphy_decomposition([0.7], [1])
    assert single.uncertainty == 0.0
    with pytest.raises(CalibrationError):
        _ = single.skill
    assert single.skill_or(0.0) == 0.0
    assert single.brier == pytest.approx(0.09)

    degenerate = murphy_decomposition([0.2, 0.8], [1, 1])
    assert degenerate.uncertainty == 0.0
    with pytest.raises(CalibrationError):
        _ = degenerate.skill

    assert expected_calibration_error([1.0, 1.0], [1, 1]) == pytest.approx(0.0)


def test_pathological_scale():
    """Pathological scale: 20,000 forecasts, and the identity still holds exactly."""
    ps = [(i % 101) / 100.0 for i in range(20000)]
    ys = [1 if (i % 7) else 0 for i in range(20000)]
    m = murphy_decomposition(ps, ys)
    assert abs(m.identity_residual) < 1e-9


# ---- 4. composition ---------------------------------------------------------------------------

def test_composes_with_the_canon_R11_circuits():
    """Chain: the R11 hedger is defined to emit the base rate, so the decomposition computed
    from its forecasts must show reliability ≈ 0 AND resolution ≈ 0 — two code paths (the
    circuit's construction and this partition) agreeing on one fact."""
    from techne.ladder_circuits.canon_r11_calibration import (
        BATTERY, HedgingForecaster, forecasts_and_outcomes,
    )
    ps, ys = forecasts_and_outcomes(HedgingForecaster().assess_all(BATTERY))
    m = murphy_decomposition(ps, ys)
    assert m.reliability == pytest.approx(0.0, abs=1e-9)
    assert m.resolution == pytest.approx(0.0, abs=1e-9)
    assert m.skill == pytest.approx(0.0, abs=1e-9)


def test_ece_and_reliability_agree_when_forecasts_are_already_binned():
    """Chain across the two metrics: with forecasts drawn from a small grid, ECE at matching
    bin count and the square root of reliability must both vanish together on a battery where
    the stated confidences match the observed frequencies exactly."""
    ps = [0.5, 0.5, 1.0, 1.0]
    ys = [1, 0, 1, 1]
    m = murphy_decomposition(ps, ys)
    assert m.reliability == pytest.approx(0.0)
    assert expected_calibration_error(ps, ys, bins=10) == pytest.approx(0.0)
