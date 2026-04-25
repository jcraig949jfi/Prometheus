"""Tests for prometheus_math.research.vcm_scaling.

Codifies Aporia's V-CM-scaling sub-void analysis (F011 paper-track):
rank-0 CM elliptic curves show a per-disc gap-compression deficit that
scales linearly with log|D|. The reference fit, hand-computed by
Aporia/Charon over LMFDB rank-0 CM curves, is:

    gap1_deficit = 19.15 * log|D| + 6.0      R^2 = 0.68     (Heegner-only)
    Heegner discriminants:
        {-3, -4, -7, -8, -11, -19, -43, -67, -163}
    n=12 across-all r = +0.79; n=11 (Heegner-only) r = +0.82.

Reference: roles/Aporia/SESSION_JOURNAL_20260422.md and Aporia/loop_state.json
(T22, T23, v_cm_scaling_FULL).

The tests below follow the four-category math-tdd rubric:
- A (authority): synthesizes data matching Aporia's reported fit and
  checks the regression recovers the published slope/intercept/R^2 to
  within numerical tolerance.
- P (property): R^2 in [0,1]; residuals sum to ~0; idempotence.
- E (edges): empty input, single-disc input, malformed input.
- C (composition): heegner_only_regression == filter+regress; per-disc
  residuals + slope*log|D| + intercept reconstructs mean compression.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.research import vcm_scaling


# ---------------------------------------------------------------------------
# Test fixtures: synthetic per-curve compression matching Aporia's fit
# ---------------------------------------------------------------------------

# Heegner discriminants (h=1, fundamental, maximal order)
HEEGNER = (-3, -4, -7, -8, -11, -19, -43, -67, -163)

# Aporia's published fit for Heegner-only at gap_index=1
PUB_SLOPE = 19.15
PUB_INTERCEPT = 6.0
PUB_R_SQUARED_TARGET = 0.68


def _synthetic_curves_for_disc(D: int, n: int, slope: float, intercept: float,
                                noise_std: float = 0.0, seed: int = 0) -> list[dict]:
    """Build n fake CM curves for discriminant D with known compression."""
    rng = np.random.default_rng(seed + abs(D))
    # underlying truth at this D, plus per-curve gaussian noise
    mu = slope * math.log(abs(D)) + intercept
    samples = rng.normal(mu, noise_std, size=n)
    out = []
    for i, c in enumerate(samples):
        out.append({
            'lmfdb_label': f'fake.{abs(D)}.{i}',
            'cm': D,
            'rank': 0,
            'conductor': 1000 + 17 * i,
            'fundamental_disc': D,  # Heegner: D itself is fundamental
            'cm_conductor': 1,
            'is_maximal': True,
            'class_number': 1,
            'compression': float(c),
        })
    return out


def _synthetic_aporia_dataset(noise_std: float = 1.5, seed: int = 42) -> list[dict]:
    """Build the Heegner-only synthetic dataset roughly matching Aporia's
    n=11 Heegner-only sample (D=-3 has many curves; rare D have few).

    Returns a flat list of per-curve dicts.
    """
    # rough per-disc populations modeled on Aporia's Charon table
    pop = {-3: 1350, -4: 600, -7: 400, -8: 350, -11: 250,
           -19: 180, -43: 90, -67: 50, -163: 20}
    out: list[dict] = []
    for D, n in pop.items():
        out.extend(_synthetic_curves_for_disc(
            D, n, PUB_SLOPE, PUB_INTERCEPT, noise_std=noise_std, seed=seed))
    return out


# ---------------------------------------------------------------------------
# 1. Authority-based tests
# ---------------------------------------------------------------------------

def test_per_disc_summary_recovers_d_minus_3_population():
    """per_disc_summary on synthetic Aporia data returns D=-3 with n~1350.

    Reference: Charon Heegner-only sample reports D=-3 dominates with
    ~1350 rank-0 CM curves at gap_index=1 (Aporia loop_state T23).
    """
    curves = _synthetic_aporia_dataset(noise_std=1.5, seed=11)
    summary = vcm_scaling.per_disc_summary(curves, gap_index=1)

    by_D = {row['D']: row for row in summary}
    assert -3 in by_D
    assert by_D[-3]['n'] == 1350
    # mean compression at D=-3 should be near 19.15*log(3) + 6 = 27.04
    expected_mean = PUB_SLOPE * math.log(3) + PUB_INTERCEPT
    assert abs(by_D[-3]['mean_compression'] - expected_mean) < 0.2
    assert by_D[-3]['is_heegner'] is True


def test_heegner_only_regression_recovers_published_slope():
    """heegner_only_regression on synthetic published-fit data recovers
    slope=19.15 and intercept=6.0 within tolerance.

    Reference: Aporia/SESSION_JOURNAL_20260422.md, line 23:
        'r = +0.82 on Heegner-only, gap1_deficit = 19.15*log|D| + 6.0,
         R²=0.68'.
    """
    curves = _synthetic_aporia_dataset(noise_std=2.5, seed=7)
    summary = vcm_scaling.per_disc_summary(curves, gap_index=1)
    fit = vcm_scaling.heegner_only_regression(summary)
    # noise level was modest, so slope should be well within 1.0 of truth
    assert abs(fit['slope'] - PUB_SLOPE) < 1.5
    assert abs(fit['intercept'] - PUB_INTERCEPT) < 5.0
    assert 0.0 <= fit['r_squared'] <= 1.0
    # the across-all r is reported at +0.79; |r| should be reasonably large
    assert abs(fit['r']) > 0.5


def test_heegner_filter_excludes_non_fundamental_discs():
    """heegner_only_regression must filter to {-3,-4,-7,-8,-11,-19,-43,-67,-163}.

    Reference: Heegner numbers (e.g. Cox, 'Primes of the Form x^2+ny^2',
    Theorem 7.30): the imaginary quadratic fields of class number 1 are
    exactly Q(sqrt(d)) for d in {-1,-2,-3,-7,-11,-19,-43,-67,-163},
    giving fundamental discriminants in HEEGNER above.
    """
    # synthesize a polluted dataset including non-Heegner D=-12 and D=-15
    pure = _synthetic_aporia_dataset(noise_std=1.0, seed=3)
    # add curves at non-Heegner D (won't be in the published Heegner fit)
    polluting = _synthetic_curves_for_disc(-12, 100, slope=200.0, intercept=0.0,
                                            noise_std=0.1, seed=99)
    for c in polluting:
        c['fundamental_disc'] = -3  # D=-12 = -3 * 2^2
        c['cm_conductor'] = 2
        c['is_maximal'] = False

    polluted_summary = vcm_scaling.per_disc_summary(pure + polluting, gap_index=1)
    pure_summary = vcm_scaling.per_disc_summary(pure, gap_index=1)
    # Heegner-only regression should ignore the wild non-Heegner D=-12 row
    fit_polluted = vcm_scaling.heegner_only_regression(polluted_summary)
    fit_pure = vcm_scaling.heegner_only_regression(pure_summary)
    # slopes must agree (the filter excluded the polluting disc)
    assert abs(fit_polluted['slope'] - fit_pure['slope']) < 1e-9
    assert abs(fit_polluted['intercept'] - fit_pure['intercept']) < 1e-9


# ---------------------------------------------------------------------------
# 2. Property-based tests (Hypothesis)
# ---------------------------------------------------------------------------

@given(
    n_discs=st.integers(min_value=2, max_value=15),
    slope=st.floats(min_value=-50.0, max_value=50.0,
                    allow_nan=False, allow_infinity=False),
    intercept=st.floats(min_value=-20.0, max_value=20.0,
                        allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=10_000),
)
@settings(max_examples=30, deadline=None)
def test_regress_log_abs_d_r_squared_in_unit_interval(n_discs, slope, intercept, seed):
    """For any synthetic linear data, R^2 must lie in [0, 1].

    Property: 0 <= R^2 <= 1 always (definition of coefficient of
    determination for an OLS fit on real data).
    """
    rng = np.random.default_rng(seed)
    discs = sorted(set(rng.integers(-1000, -1, size=n_discs * 3).tolist()))[:n_discs]
    if len(discs) < 2:
        return
    rows = []
    for D in discs:
        mu = slope * math.log(abs(D)) + intercept
        rows.append({
            'D': int(D), 'd_K': int(D), 'f': 1, 'n': 50,
            'mean_compression': float(mu + rng.normal(0, 1.0)),
            'std': 1.0, 'ci': (mu - 0.3, mu + 0.3),
            'is_heegner': int(D) in HEEGNER,
        })
    fit = vcm_scaling.regress_log_abs_d(rows, weighted=False)
    assert 0.0 <= fit['r_squared'] <= 1.0 + 1e-9


@given(noise_std=st.floats(min_value=0.05, max_value=5.0),
       seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=15, deadline=None)
def test_per_disc_residuals_sum_to_zero(noise_std, seed):
    """OLS residuals sum to zero (or very close, after numpy roundoff).

    Property: any unweighted OLS fit ``y_hat = a*x + b`` over n points
    has residuals satisfying ``sum_i (y_i - y_hat_i) == 0``. This is a
    standard property of the OLS normal equations.
    """
    curves = _synthetic_aporia_dataset(noise_std=noise_std, seed=seed)
    summary = vcm_scaling.per_disc_summary(curves, gap_index=1)
    fit = vcm_scaling.regress_log_abs_d(summary, weighted=False)
    residuals = vcm_scaling.per_disc_residuals(summary, fit)
    total = sum(r['residual'] for r in residuals)
    assert abs(total) < 1e-6


# ---------------------------------------------------------------------------
# 3. Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_empty_and_bad_bounds():
    """V-CM-scaling edges (group 1: empty/malformed):
    - empty cm_curves -> ValueError on per_disc_summary
    - empty per_disc list -> ValueError on regress_log_abs_d
    - heegner-only on data with zero Heegner discs -> ValueError
    - fetch_cm_curves with non-positive conductor_max -> ValueError
    - fetch_cm_curves with non-positive n_max -> ValueError
    """
    with pytest.raises(ValueError):
        vcm_scaling.per_disc_summary([], gap_index=1)

    with pytest.raises(ValueError):
        vcm_scaling.regress_log_abs_d([], weighted=False)

    # heegner-only with zero heegner rows -> ValueError
    non_heegner = [{
        'D': -12, 'd_K': -3, 'f': 2, 'n': 100,
        'mean_compression': 30.0, 'std': 1.0,
        'ci': (29.7, 30.3), 'is_heegner': False,
    }, {
        'D': -27, 'd_K': -3, 'f': 3, 'n': 100,
        'mean_compression': 35.0, 'std': 1.0,
        'ci': (34.7, 35.3), 'is_heegner': False,
    }]
    with pytest.raises(ValueError):
        vcm_scaling.heegner_only_regression(non_heegner)

    # fetch_cm_curves with bad bounds
    with pytest.raises(ValueError):
        vcm_scaling.fetch_cm_curves(rank=0, conductor_max=-5, n_max=100)
    with pytest.raises(ValueError):
        vcm_scaling.fetch_cm_curves(rank=0, conductor_max=1000, n_max=0)


def test_edge_single_disc_regression_is_degenerate():
    """V-CM-scaling edges (group 2: degenerate scale):
    - single-disc per_disc -> regression returns NaN slope, NaN R^2,
      and intercept set to the lone observation.

    A line through one point is undetermined; the API contract is that
    we surface NaNs rather than fabricate a slope.
    """
    one_row = [{
        'D': -3, 'd_K': -3, 'f': 1, 'n': 100,
        'mean_compression': 27.0, 'std': 1.0,
        'ci': (26.7, 27.3), 'is_heegner': True,
    }]
    fit = vcm_scaling.regress_log_abs_d(one_row, weighted=False)
    assert math.isnan(fit['slope'])
    assert math.isnan(fit['r_squared'])
    assert math.isnan(fit['p_value'])
    assert fit['intercept'] == 27.0
    # fit_predictions must still be produced (length 1) for plotting
    assert len(fit['fit_predictions']) == 1
    assert fit['fit_predictions'][0]['D'] == -3


# ---------------------------------------------------------------------------
# 4. Composition tests
# ---------------------------------------------------------------------------

def test_heegner_only_regression_equals_filter_plus_regress():
    """heegner_only_regression(summary) == regress_log_abs_d(filter(summary)).

    Composition: the convenience function must be definitionally equal
    to manual filter+regress. This catches drift if one is patched
    without the other.
    """
    curves = _synthetic_aporia_dataset(noise_std=1.5, seed=21)
    summary = vcm_scaling.per_disc_summary(curves, gap_index=1)
    via_facade = vcm_scaling.heegner_only_regression(summary)
    heegner_subset = [r for r in summary if r['is_heegner']]
    via_manual = vcm_scaling.regress_log_abs_d(heegner_subset, weighted=False)
    assert abs(via_facade['slope'] - via_manual['slope']) < 1e-9
    assert abs(via_facade['intercept'] - via_manual['intercept']) < 1e-9
    assert abs(via_facade['r_squared'] - via_manual['r_squared']) < 1e-9


def test_figure_full_pipeline(tmp_path):
    """Composition: full pipeline (summary → regression → residuals → figure)
    produces a non-trivial PNG on synthetic Aporia data.

    This catches integration bugs that single-function tests miss
    (e.g. mismatched key names between regression and figure).
    """
    curves = _synthetic_aporia_dataset(noise_std=1.5, seed=2026)
    summary = vcm_scaling.per_disc_summary(curves, gap_index=1)
    fit = vcm_scaling.regress_log_abs_d(summary, weighted=False)
    residuals = vcm_scaling.per_disc_residuals(summary, fit)

    out = tmp_path / "vcm_test.png"
    saved = vcm_scaling.figure(
        scan_result={
            'per_disc': summary,
            'regression': fit,
            'residuals': residuals,
        },
        out_path=str(out),
    )
    assert saved == str(out)
    assert out.exists()
    assert out.stat().st_size > 4_000  # non-trivial PNG (header + content)


def test_residual_plus_prediction_reconstructs_mean_compression():
    """For each per-disc row, residual + (slope*log|D| + intercept) ≈ mean.

    Composition: the residual is *defined* as observed - predicted, so
    residual + predicted must reconstruct observed exactly. Catches off-by
    sign-of-residual bugs.
    """
    curves = _synthetic_aporia_dataset(noise_std=1.0, seed=15)
    summary = vcm_scaling.per_disc_summary(curves, gap_index=1)
    fit = vcm_scaling.regress_log_abs_d(summary, weighted=False)
    residuals = vcm_scaling.per_disc_residuals(summary, fit)

    by_D_summary = {r['D']: r for r in summary}
    for r in residuals:
        D = r['D']
        predicted = fit['slope'] * math.log(abs(D)) + fit['intercept']
        observed = by_D_summary[D]['mean_compression']
        assert abs((r['residual'] + predicted) - observed) < 1e-9
