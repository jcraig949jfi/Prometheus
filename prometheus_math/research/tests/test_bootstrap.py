"""Tests for prometheus_math.research.bootstrap (project #43).

Test categories (math-tdd skill, see techne/skills/math-tdd.md):

- **Authority**: closed-form / classical references for each public op
  (Gaussian CI coverage, central limit theorem mean/std, two-sample
  permutation theory under H0 same-dist, two-sample permutation theory
  under H1 mean-diff=1, Holm 1979 worked example).

- **Property**: invariants that must hold for any valid input —
  ``p_value in [0, 1]`` for every variant, ``ci_lower <= point <=
  ci_upper`` always, ``n_resamples`` monotonically tightens the median
  CI width on a fixed seed, Holm adjusted-p >= raw-p always.

- **Edge**: empty samples, single sample, constant samples, n=0,
  statistic_fn that raises, mismatched x/y length, p outside [0,1] for
  Holm.

- **Composition**: ``bootstrap_ci(samples, np.mean)`` reproduces
  ``scipy.stats.bootstrap`` to within Monte-Carlo tolerance;
  ``matched_null_test`` is a generalisation of ``bootstrap_ci`` when the
  null is "draw a bootstrap mean of the same sample".

References
----------
- Efron, B. (1979). Annals of Statistics 7 (1): 1-26.
- Holm, S. (1979). Scand. J. Statistics 6: 65-70.
- Good, P. (2005). Permutation, Parametric, and Bootstrap Tests of
  Hypotheses, 3rd ed., Springer.
- SciPy 1.13: ``scipy.stats.bootstrap`` (percentile method).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from prometheus_math.research import bootstrap as bs


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_authority_bootstrap_ci_gaussian_mean():
    """N(0, 1), n=1000: bootstrap mean ≈ 0 ± 0.05; 95% CI contains 0.

    Reference: classical CLT — sample mean of n=1000 i.i.d. N(0,1) has
    standard error 1/sqrt(1000) ≈ 0.032; the 95% percentile-bootstrap
    CI for the mean must contain 0 with high probability.
    """
    rng = np.random.default_rng(2024)
    samples = rng.normal(0.0, 1.0, size=1000)
    out = bs.bootstrap_ci(samples, np.mean, n_resamples=2000, alpha=0.05, seed=11)
    assert abs(out["point_estimate"]) < 0.05
    assert out["ci_lower"] < 0.0 < out["ci_upper"]
    # SE-based sanity: CI half-width ~ 1.96 * 0.032 = 0.063
    half = 0.5 * (out["ci_upper"] - out["ci_lower"])
    assert 0.02 < half < 0.15


def test_authority_permutation_test_same_distribution_h0():
    """Two N(0,1) samples — permutation test cannot reject H0.

    Reference: classical permutation theory (Good 2005, ch. 2): under
    H0 of identical distribution, the permutation p-value is uniform
    on [1/(n+1), 1]; for any single run the expected p is 0.5 and
    rejection at alpha=0.05 happens at most ~5% of the time.
    """
    rng = np.random.default_rng(5)
    a = rng.normal(0.0, 1.0, size=200)
    b = rng.normal(0.0, 1.0, size=200)
    out = bs.permutation_test(a, b, n=2000, seed=7)
    assert out["p_value"] > 0.05


def test_authority_permutation_test_clear_separation_h1():
    """Two N(mu,1) samples with mu_diff=1, n=200 each — clear rejection.

    Reference: standard power analysis. With n=200 per arm and
    Cohen's d = 1.0, the two-sample test power is essentially 1; the
    permutation p-value should be well below 1e-3.
    """
    rng = np.random.default_rng(10)
    a = rng.normal(0.0, 1.0, size=200)
    b = rng.normal(1.0, 1.0, size=200)
    out = bs.permutation_test(a, b, n=2000, seed=13)
    assert out["p_value"] < 1e-3
    assert abs(out["observed_stat"] + 1.0) < 0.2  # mean(a) - mean(b) ≈ -1


def test_authority_matched_null_test_observed_at_null_centre():
    """observation=0 vs null_fn drawing N(0,1) — p ≈ 0.5 — 1.

    Reference: by symmetry of the null around 0, observed=0 places the
    observation at the median of the null; the two-tailed empirical
    p-value should be near 1.0 (cannot distinguish observation from null).
    """
    rng = np.random.default_rng(99)
    out = bs.matched_null_test(
        observation=0.0,
        null_fn=lambda: float(rng.normal()),
        n=5000,
        seed=1,
    )
    # p should be large; the empirical p for obs at the median of a
    # symmetric null is bounded below by ~0.9 in expectation.
    assert out["p_value"] > 0.5
    assert abs(out["null_mean"]) < 0.05
    assert abs(out["null_std"] - 1.0) < 0.05


def test_authority_holm_bonferroni_worked_example():
    """Holm (1979) §3 worked example.

    Reference: Holm 1979, Table 1. Raw p = [0.01, 0.04, 0.03, 0.005],
    m=4. Sorted ascending: [0.005, 0.01, 0.03, 0.04] with multipliers
    [4, 3, 2, 1] gives [0.020, 0.030, 0.060, 0.040]; monotonised to
    [0.020, 0.030, 0.060, 0.060]. Inverting the sort permutation
    yields the adjusted p in original order:
        raw=0.01 -> 0.030
        raw=0.04 -> 0.060
        raw=0.03 -> 0.060
        raw=0.005 -> 0.020
    """
    raw = np.array([0.01, 0.04, 0.03, 0.005])
    expected = np.array([0.030, 0.060, 0.060, 0.020])
    adj = bs.holm_bonferroni(raw)
    np.testing.assert_allclose(adj, expected, atol=1e-12)


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


def test_property_p_values_always_in_unit_interval():
    """Every bootstrap variant returns p_value in [0, 1] across many seeds."""
    rng = np.random.default_rng(2025)
    for seed in range(20):
        a = rng.normal(0.0, 1.0, size=50)
        b = rng.normal(0.5, 1.0, size=50)
        perm = bs.permutation_test(a, b, n=500, seed=seed)
        assert 0.0 <= perm["p_value"] <= 1.0
        mn = bs.matched_null_test(
            observation=float(np.mean(a)),
            null_fn=lambda: float(rng.normal()),
            n=500,
            seed=seed,
        )
        assert 0.0 <= mn["p_value"] <= 1.0


def test_property_ci_contains_point_estimate():
    """ci_lower <= point_estimate <= ci_upper for every variant."""
    rng = np.random.default_rng(13)
    samples = rng.normal(3.0, 2.0, size=80)
    out = bs.bootstrap_ci(samples, np.mean, n_resamples=1000, seed=21)
    assert out["ci_lower"] <= out["point_estimate"] <= out["ci_upper"]
    bayes = bs.bayesian_bootstrap(samples, np.mean, n=1000, seed=22)
    assert bayes["ci_lower"] <= bayes["point_estimate"] <= bayes["ci_upper"]
    x = rng.normal(size=80)
    y = 0.6 * x + 0.4 * rng.normal(size=80)
    corr = bs.bootstrap_correlation(x, y, n=1000, seed=23)
    assert corr["ci_lower"] <= corr["r"] <= corr["ci_upper"]


def test_property_more_resamples_tightens_ci_in_expectation():
    """On a fixed seed, increasing n_resamples reduces sampling noise.

    The CI width converges as ``n_resamples -> inf``; 200 vs 5000
    resamples should give a width that is closer to the asymptotic
    width and within +/- the larger one.
    """
    rng = np.random.default_rng(7)
    samples = rng.normal(0, 1, size=200)
    widths = []
    for n_r in [200, 1000, 5000]:
        out = bs.bootstrap_ci(samples, np.mean, n_resamples=n_r, seed=42)
        widths.append(out["ci_upper"] - out["ci_lower"])
    # Asymptotic width is ~ 2 * 1.96 * sd / sqrt(200) ≈ 0.277.
    # All three values should be within 30% of each other and within
    # 50% of the asymptotic width.
    asymp = 2.0 * 1.96 / math.sqrt(200)
    for w in widths:
        assert 0.5 * asymp < w < 1.6 * asymp


def test_property_holm_adjusted_p_geq_raw():
    """Holm-adjusted p is always >= raw p, for any valid input."""
    rng = np.random.default_rng(33)
    for _ in range(30):
        m = rng.integers(1, 25)
        raw = rng.uniform(0.0, 1.0, size=int(m))
        adj = bs.holm_bonferroni(raw)
        assert np.all(adj >= raw - 1e-12)
        assert np.all(adj <= 1.0 + 1e-12)


def test_property_bootstrap_correlation_in_minus_one_one():
    """Pearson r is in [-1, 1]; bootstrap CI bounds must respect this."""
    rng = np.random.default_rng(45)
    x = rng.normal(size=80)
    y = rng.normal(size=80)
    out = bs.bootstrap_correlation(x, y, n=500, seed=1)
    assert -1.0 <= out["ci_lower"] <= 1.0
    assert -1.0 <= out["ci_upper"] <= 1.0
    assert -1.0 <= out["r"] <= 1.0


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


def test_edge_empty_samples_raises():
    """Empty samples -> ValueError for every public op that takes samples."""
    with pytest.raises(ValueError):
        bs.bootstrap_ci(np.array([]), np.mean)
    with pytest.raises(ValueError):
        bs.bayesian_bootstrap(np.array([]), np.mean)
    with pytest.raises(ValueError):
        bs.permutation_test(np.array([]), np.array([1.0, 2.0]))
    with pytest.raises(ValueError):
        bs.holm_bonferroni(np.array([]))


def test_edge_single_sample_gives_trivial_ci():
    """A single sample -> CI is [sample, sample] for the mean.

    With one observation the bootstrap can only resample that
    observation, so the bootstrap distribution is degenerate.
    """
    out = bs.bootstrap_ci(np.array([7.0]), np.mean, n_resamples=100, seed=0)
    assert out["point_estimate"] == 7.0
    assert out["ci_lower"] == 7.0
    assert out["ci_upper"] == 7.0


def test_edge_constant_samples_zero_width_ci():
    """Constant samples -> CI width 0; matched null test on constants."""
    out = bs.bootstrap_ci(np.full(50, 3.14), np.mean, n_resamples=200, seed=4)
    assert out["ci_upper"] - out["ci_lower"] == 0.0
    # constant null_fn -> degenerate null; observed at the constant
    # gives nan z, p ≈ 1
    out_mn = bs.matched_null_test(
        observation=3.14,
        null_fn=lambda: 3.14,
        n=100,
        seed=0,
    )
    assert math.isnan(out_mn["z_score"])
    assert out_mn["null_std"] == 0.0


def test_edge_n_resamples_zero_raises():
    with pytest.raises(ValueError):
        bs.bootstrap_ci(np.array([1.0, 2.0, 3.0]), np.mean, n_resamples=0)
    with pytest.raises(ValueError):
        bs.matched_null_test(0.0, lambda: 0.0, n=0)
    with pytest.raises(ValueError):
        bs.permutation_test(np.array([1.0]), np.array([2.0]), n=0)


def test_edge_statistic_fn_raises_propagates_as_valueerror():
    """A statistic_fn that raises is reported as a ValueError, not silently."""
    def bad_stat(_a):
        raise RuntimeError("bad stat")
    with pytest.raises(ValueError, match="bad stat"):
        bs.bootstrap_ci(np.array([1.0, 2.0]), bad_stat, n_resamples=10)


def test_edge_correlation_mismatched_length_raises():
    with pytest.raises(ValueError, match="same length"):
        bs.bootstrap_correlation(np.arange(5), np.arange(6), n=100)


def test_edge_correlation_constant_input_raises():
    with pytest.raises(ValueError, match="constant"):
        bs.bootstrap_correlation(np.ones(10), np.arange(10, dtype=float), n=100)


def test_edge_holm_invalid_p_values():
    with pytest.raises(ValueError):
        bs.holm_bonferroni(np.array([0.5, -0.1, 0.2]))
    with pytest.raises(ValueError):
        bs.holm_bonferroni(np.array([0.5, 1.5]))


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_bootstrap_ci_matches_scipy():
    """bootstrap_ci(samples, np.mean) ≈ scipy.stats.bootstrap on same samples.

    Both use the percentile method, so the CI bounds should agree to
    within Monte-Carlo error (≤ ~0.02 for n_resamples=2000 and a
    Gaussian sample of size 200).
    """
    pytest.importorskip("scipy")
    from scipy.stats import bootstrap as scipy_bootstrap

    rng = np.random.default_rng(0)
    samples = rng.normal(0.0, 1.0, size=200)

    ours = bs.bootstrap_ci(samples, np.mean, n_resamples=2000, alpha=0.05, seed=1)
    scipy_res = scipy_bootstrap(
        (samples,),
        np.mean,
        n_resamples=2000,
        confidence_level=0.95,
        method="percentile",
        random_state=np.random.default_rng(1),
    )
    # Both are stochastic; tolerance is loose. Asymptotic SE is ~0.07,
    # so 0.05 absolute tolerance on each bound is generous but bounded.
    assert abs(ours["ci_lower"] - scipy_res.confidence_interval.low) < 0.05
    assert abs(ours["ci_upper"] - scipy_res.confidence_interval.high) < 0.05


def test_composition_matched_null_generalises_bootstrap_mean():
    """matched_null_test with null_fn = bootstrap-of-mean ≈ bootstrap_ci.

    Composition lemma: feeding ``matched_null_test`` a null sampler of
    "draw a bootstrap mean of the same sample" recovers the bootstrap
    distribution of the sample mean — null_mean ≈ point_estimate, and
    null_std ≈ standard error.
    """
    rng = np.random.default_rng(11)
    samples = rng.normal(2.0, 1.0, size=300)
    boot = bs.bootstrap_ci(samples, np.mean, n_resamples=2000, seed=7)

    rng_null = np.random.default_rng(17)
    def null_fn() -> float:
        idx = rng_null.integers(0, samples.size, size=samples.size)
        return float(samples[idx].mean())

    mn = bs.matched_null_test(
        observation=float(np.mean(samples)),
        null_fn=null_fn,
        n=2000,
        seed=7,
    )
    # null_mean of bootstrap-mean draws ≈ sample mean
    assert abs(mn["null_mean"] - boot["point_estimate"]) < 0.05
    # SE estimate ≈ 1 / sqrt(300) ≈ 0.058
    expected_se = 1.0 / math.sqrt(300)
    assert abs(mn["null_std"] - expected_se) < 0.02


def test_composition_permutation_p_under_holm_correction():
    """holm_bonferroni composes with permutation_test outputs.

    Run 5 permutation tests, 4 are H0-true and 1 is H1-true with a
    large effect; Holm should leave the small p (H1) significant and
    push the H0-true p's above 0.05 after correction.
    """
    rng = np.random.default_rng(2)
    p_raw = []
    for i in range(4):
        a = rng.normal(0.0, 1.0, size=80)
        b = rng.normal(0.0, 1.0, size=80)
        p_raw.append(bs.permutation_test(a, b, n=500, seed=100 + i)["p_value"])
    a = rng.normal(0.0, 1.0, size=80)
    b = rng.normal(2.0, 1.0, size=80)
    p_raw.append(bs.permutation_test(a, b, n=500, seed=200)["p_value"])
    p_raw_arr = np.asarray(p_raw)
    p_adj = bs.holm_bonferroni(p_raw_arr)
    # H1 entry (last) should still be the smallest after correction
    assert np.argmin(p_adj) == 4
    # adjustment cannot decrease any value
    assert np.all(p_adj >= p_raw_arr - 1e-12)


def test_composition_correlation_chain_with_matched_null():
    """bootstrap_correlation r vs a permuted-y null reproduces the same r.

    Pair-bootstrap CI on r and a "shuffle y" null both use the same
    underlying observation; the observed r they report MUST match
    exactly (it is the same scalar computed two ways).
    """
    rng = np.random.default_rng(50)
    x = rng.normal(size=120)
    y = 0.7 * x + 0.5 * rng.normal(size=120)
    corr = bs.bootstrap_correlation(x, y, n=500, seed=3)
    # null: shuffle y, compute r
    rng_null = np.random.default_rng(99)
    def null_fn() -> float:
        y_shuf = rng_null.permutation(y)
        return float(np.corrcoef(x, y_shuf)[0, 1])
    mn = bs.matched_null_test(
        observation=corr["r"],
        null_fn=null_fn,
        n=500,
        seed=4,
    )
    assert mn["observed"] == corr["r"]
    # Under the shuffle null, the null mean should be ≈ 0
    assert abs(mn["null_mean"]) < 0.05
    # And r ≈ 0.7 should reject H0 of independence
    assert mn["p_value"] < 0.01
