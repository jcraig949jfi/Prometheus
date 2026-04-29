"""Tests for prometheus_math.statistics_distributions.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority (>=4): N(0,1) pdf at 0 = 1/sqrt(2*pi), cdf(0)=0.5,
  quantile(0.975) ~= 1.95996398, exponential mean = 1/rate, chi2(5) mean
  = 5, poisson pmf at k=3, mu=2 = 4/3 * exp(-2), KL(N||N)=0,
  KL(N(0,1)||N(0,2)) > 0.

- Property (>=3): cdf monotone non-decreasing, quantile(cdf(x))==x,
  quantile(0)=lower_bound, quantile(1)=upper_bound, sample mean within
  stderr (Hypothesis), KL(P||P)=0 across families, KL(P||Q) >= 0.

- Edge (>=3): invalid params raise ValueError; n_samples=0 returns
  empty array; sigma=0 raises; quantile(p<0) and quantile(p>1) raise;
  moment_estimator with n_moments > samples raises.

- Composition (>=2): MLE of N(3, 2) samples recovers params; empirical
  CDF converges to true CDF as n grows; rejection_sample with
  proposal=target accepts everything; sample -> empirical CDF -> true
  CDF (Glivenko-Cantelli).
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.statistics_distributions import (
    FAMILIES,
    beta,
    binomial,
    cauchy,
    chi2,
    empirical_cdf,
    exponential,
    f as f_dist,
    gamma,
    geometric,
    get_family,
    kde,
    kl_divergence,
    laplace,
    lognormal,
    mle_estimator,
    moment_estimator,
    multivariate_normal,
    negative_binomial,
    normal,
    pareto,
    poisson,
    rejection_sample,
    t as t_dist,
    uniform,
    weibull,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_normal_pdf_at_zero_against_analytical():
    """N(0,1) pdf(0) = 1/sqrt(2*pi) ~ 0.3989422804.

    Reference: any standard probability text (e.g., Casella & Berger
    'Statistical Inference', 2nd ed., eq. 3.3.13).
    """
    val = normal.pdf(0.0, mu=0.0, sigma=1.0)
    assert abs(val - 1.0 / math.sqrt(2.0 * math.pi)) < 1e-12


def test_normal_cdf_at_zero_is_half():
    """N(0,1) cdf(0) = 0.5 by symmetry."""
    assert abs(normal.cdf(0.0, mu=0.0, sigma=1.0) - 0.5) < 1e-12


def test_normal_quantile_975_matches_z_table():
    """N(0,1) quantile(0.975) ~ 1.959963984540054.

    Reference: standard z-table (every introductory stats textbook;
    e.g., Wackerly, Mendenhall, Scheaffer, 'Mathematical Statistics with
    Applications', Appendix Table 4).
    """
    z = normal.quantile(0.975, mu=0.0, sigma=1.0)
    assert abs(z - 1.959963984540054) < 1e-9


def test_exponential_mean_against_analytical():
    """Exp(rate=2) has mean 1/rate = 0.5. (Casella & Berger eq. 3.3.4.)"""
    assert abs(exponential.mean(rate=2.0) - 0.5) < 1e-12
    assert abs(exponential.var(rate=2.0) - 0.25) < 1e-12


def test_chi2_mean_equals_k():
    """chi2(k) has mean = k. (Casella & Berger eq. 5.3.5.)"""
    assert chi2.mean(k=5.0) == pytest.approx(5.0, abs=1e-12)
    assert chi2.var(k=5.0) == pytest.approx(10.0, abs=1e-12)


def test_poisson_pmf_three_mu_two_against_formula():
    """Poisson(mu=2) at k=3 = 2^3/3! * exp(-2) = 4/3 * exp(-2) ~ 0.18044.

    Reference: hand-computed from Poisson PMF mu^k * exp(-mu) / k!
    """
    expected = (2.0**3) / math.factorial(3) * math.exp(-2.0)
    val = poisson.pdf(3, mu=2.0)
    assert abs(val - expected) < 1e-12
    assert abs(expected - 0.18044704431548354) < 1e-12  # cross-check constant


def test_kl_normal_self_is_zero():
    """KL(N(0,1) || N(0,1)) = 0 (Cover & Thomas, Thm 2.6.3)."""
    val = kl_divergence(normal, {"mu": 0.0, "sigma": 1.0},
                        normal, {"mu": 0.0, "sigma": 1.0})
    assert abs(val) < 1e-12


def test_kl_normal_different_variance_against_closed_form():
    """KL(N(0,1) || N(0,2)) = log(2) + (1 - 1)/8 + 1/8 - 0.5
    = log(2) + 0.125 - 0.5 = log(2) - 0.375.

    Reference: closed-form KL(N(m1,s1)||N(m2,s2)) =
    log(s2/s1) + (s1^2 + (m1-m2)^2)/(2*s2^2) - 1/2.
    """
    val = kl_divergence(normal, {"mu": 0.0, "sigma": 1.0},
                        normal, {"mu": 0.0, "sigma": 2.0})
    expected = math.log(2.0) + (1.0 + 0.0) / (2.0 * 4.0) - 0.5
    assert abs(val - expected) < 1e-9
    assert val > 0.0


def test_kl_exponential_closed_form():
    """KL(Exp(2) || Exp(1)) = log(2) + 1/2 - 1 = log(2) - 0.5."""
    val = kl_divergence(exponential, {"rate": 2.0},
                        exponential, {"rate": 1.0})
    expected = math.log(2.0) - 0.5
    assert abs(val - expected) < 1e-9


def test_uniform_pdf_height_inverse_width():
    """U(0, 4) pdf height = 1/4 over its support."""
    assert abs(uniform.pdf(2.0, a=0.0, b=4.0) - 0.25) < 1e-12
    assert abs(uniform.cdf(1.0, a=0.0, b=4.0) - 0.25) < 1e-12


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


@given(
    st.floats(min_value=-3.0, max_value=3.0),
    st.floats(min_value=0.05, max_value=10.0),
)
def test_normal_cdf_is_monotone_non_decreasing(mu, sigma):
    """For any valid params, cdf is monotone non-decreasing."""
    xs = np.linspace(-10.0, 10.0, 50)
    cdf_vals = np.array([normal.cdf(x, mu=mu, sigma=sigma) for x in xs])
    assert np.all(np.diff(cdf_vals) >= -1e-12)


@given(
    st.floats(min_value=-2.0, max_value=2.0),
    st.floats(min_value=0.5, max_value=5.0),
    st.floats(min_value=0.01, max_value=0.99),
)
def test_normal_quantile_inverts_cdf(mu, sigma, p):
    """quantile(cdf(x))==x within numerical precision."""
    x = mu + sigma * 0.5
    p_back = normal.cdf(x, mu=mu, sigma=sigma)
    x_back = normal.quantile(p_back, mu=mu, sigma=sigma)
    assert abs(x_back - x) < 1e-7
    # And the other way: cdf(quantile(p)) == p.
    x_p = normal.quantile(p, mu=mu, sigma=sigma)
    p_recovered = normal.cdf(x_p, mu=mu, sigma=sigma)
    assert abs(p_recovered - p) < 1e-7


@pytest.mark.parametrize("family,params", [
    (normal, {"mu": 0.0, "sigma": 1.0}),
    (exponential, {"rate": 1.5}),
    (beta, {"alpha": 2.0, "beta": 3.0}),
    (uniform, {"a": -1.0, "b": 2.0}),
    (gamma, {"shape": 2.0, "rate": 3.0}),
    (chi2, {"k": 4.0}),
    (lognormal, {"mu": 0.0, "sigma": 0.5}),
])
def test_quantile_bounds_zero_one(family, params):
    """quantile(0) is the support lower bound; quantile(1) the upper."""
    lo, hi = family.support(**params)
    q0 = family.quantile(0.0, **params)
    q1 = family.quantile(1.0, **params)
    if math.isfinite(lo):
        assert abs(q0 - lo) < 1e-9
    else:
        assert q0 == -np.inf
    if math.isfinite(hi):
        assert abs(q1 - hi) < 1e-9
    else:
        assert q1 == np.inf


@settings(max_examples=20, deadline=None,
          suppress_health_check=[HealthCheck.too_slow])
@given(
    st.floats(min_value=-3.0, max_value=3.0),
    st.floats(min_value=0.5, max_value=2.5),
)
def test_sample_mean_within_stderr(mu, sigma):
    """Sample mean is within ~3 standard errors of the true mean."""
    n = 10_000
    xs = normal.sample(n, mu=mu, sigma=sigma, seed=42)
    stderr = sigma / math.sqrt(n)
    assert abs(xs.mean() - mu) < 5.0 * stderr  # 5-sigma slack


@pytest.mark.parametrize("family,params", [
    (normal, {"mu": 1.5, "sigma": 0.7}),
    (exponential, {"rate": 0.4}),
    (poisson, {"mu": 3.5}),
])
def test_kl_self_is_zero(family, params):
    """KL(P || P) == 0 for any P."""
    assert abs(kl_divergence(family, params, family, params)) < 1e-9


@pytest.mark.parametrize("family,pa,pb", [
    (normal, {"mu": 0.0, "sigma": 1.0}, {"mu": 1.0, "sigma": 1.5}),
    (exponential, {"rate": 0.5}, {"rate": 2.0}),
    (poisson, {"mu": 1.5}, {"mu": 4.0}),
])
def test_kl_is_nonnegative_gibbs(family, pa, pb):
    """Gibbs' inequality: KL(P || Q) >= 0."""
    assert kl_divergence(family, pa, family, pb) >= -1e-9


def test_pdf_integrates_to_one_continuous():
    """For continuous families, integrate pdf over support ~= 1."""
    from scipy import integrate
    cases = [
        (normal, {"mu": 0.0, "sigma": 1.0}, -10.0, 10.0),
        (exponential, {"rate": 1.5}, 0.0, 50.0),
        (beta, {"alpha": 2.0, "beta": 3.0}, 0.0, 1.0),
        (gamma, {"shape": 2.0, "rate": 1.0}, 0.0, 50.0),
    ]
    for fam, params, lo, hi in cases:
        val, _ = integrate.quad(lambda x: fam.pdf(x, **params), lo, hi)
        assert abs(val - 1.0) < 1e-4, f"{fam.name}: integral = {val}"


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_invalid_params_raise_value_error():
    """Various invalid parameters raise ValueError.

    Edges covered: sigma=0, sigma<0, beta with alpha=0, gamma with
    rate<0, binomial with p>1, poisson with mu=0, chi2 with k<0.
    """
    with pytest.raises(ValueError):
        normal.pdf(0.0, mu=0.0, sigma=0.0)
    with pytest.raises(ValueError):
        normal.pdf(0.0, mu=0.0, sigma=-1.0)
    with pytest.raises(ValueError):
        beta.pdf(0.5, alpha=0.0, beta=2.0)
    with pytest.raises(ValueError):
        gamma.pdf(1.0, shape=2.0, rate=-1.0)
    with pytest.raises(ValueError):
        binomial.pdf(2, n=10, p=1.5)
    with pytest.raises(ValueError):
        poisson.pdf(0, mu=0.0)
    with pytest.raises(ValueError):
        chi2.pdf(1.0, k=-1.0)


def test_n_samples_zero_is_empty_array():
    """sample(0) returns an empty 1-D float array."""
    out = normal.sample(0, mu=0.0, sigma=1.0)
    assert isinstance(out, np.ndarray)
    assert out.size == 0


def test_sample_negative_n_raises():
    """sample(-1) raises ValueError."""
    with pytest.raises(ValueError):
        normal.sample(-1, mu=0.0, sigma=1.0)


def test_quantile_out_of_range_raises():
    """quantile(p) for p outside [0,1] raises ValueError."""
    with pytest.raises(ValueError):
        normal.quantile(-0.01, mu=0.0, sigma=1.0)
    with pytest.raises(ValueError):
        normal.quantile(1.01, mu=0.0, sigma=1.0)


def test_moment_estimator_too_many_moments_raises():
    """n_moments greater than sample size raises ValueError."""
    with pytest.raises(ValueError):
        moment_estimator(np.array([1.0, 2.0, 3.0]), normal, n_moments=5)
    with pytest.raises(ValueError):
        moment_estimator(np.array([1.0, 2.0]), normal, n_moments=0)


def test_uniform_invalid_bounds_raise():
    """U(b, a) with b <= a raises ValueError."""
    with pytest.raises(ValueError):
        uniform.pdf(0.5, a=1.0, b=0.0)
    with pytest.raises(ValueError):
        uniform.pdf(0.5, a=2.0, b=2.0)


def test_kl_different_families_raise():
    """KL between different families is undefined here -> ValueError."""
    with pytest.raises(ValueError):
        kl_divergence(normal, {"mu": 0.0, "sigma": 1.0},
                      exponential, {"rate": 1.0})


def test_empty_samples_raise():
    """empirical_cdf, mle_estimator, kde all reject empty samples."""
    with pytest.raises(ValueError):
        empirical_cdf(np.array([]))
    with pytest.raises(ValueError):
        mle_estimator(np.array([]), normal)
    with pytest.raises(ValueError):
        kde(np.array([]))


def test_unknown_family_name_raises():
    """get_family with bogus name -> ValueError."""
    with pytest.raises(ValueError):
        get_family("not_a_distribution")


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_mle_recovers_normal_params():
    """MLE on N(mu=3, sigma=2) samples recovers (~3, ~2).

    Composition: sample -> mle_estimator chain. With n=20_000 the
    estimator should hit each parameter to ~1e-2.
    """
    rng = np.random.default_rng(0)
    n = 20_000
    samples = 3.0 + 2.0 * rng.standard_normal(size=n)
    fit = mle_estimator(samples, normal)
    assert fit["family"] == "normal"
    assert abs(fit["params"]["mu"] - 3.0) < 0.05
    assert abs(fit["params"]["sigma"] - 2.0) < 0.05


def test_moment_estimator_normal_recovers():
    """MoM on N(0, 1) recovers (~0, ~1)."""
    rng = np.random.default_rng(1)
    samples = rng.standard_normal(size=5_000)
    fit = moment_estimator(samples, normal, n_moments=2)
    assert abs(fit["params"]["mu"] - 0.0) < 0.05
    assert abs(fit["params"]["sigma"] - 1.0) < 0.05


def test_mle_exponential_recovers_rate():
    """MLE on Exp(rate=3) recovers ~3."""
    rng = np.random.default_rng(2)
    samples = rng.exponential(scale=1.0 / 3.0, size=5_000)
    fit = mle_estimator(samples, exponential)
    assert abs(fit["params"]["rate"] - 3.0) < 0.1


def test_empirical_cdf_converges_to_true_cdf():
    """Glivenko-Cantelli: sup |F_n - F| -> 0 as n grows.

    Composition: sample -> empirical_cdf -> compare with normal.cdf.
    """
    rng = np.random.default_rng(7)
    samples = rng.standard_normal(size=5_000)
    ec = empirical_cdf(samples)
    grid = np.linspace(-3.0, 3.0, 41)
    true_cdf = np.array([normal.cdf(x, mu=0.0, sigma=1.0) for x in grid])
    sup_err = np.max(np.abs(ec(grid) - true_cdf))
    assert sup_err < 0.05


def test_rejection_sample_proposal_equals_target_accepts_all():
    """When the proposal IS the target (M=1), every draw is accepted.

    Composition: sample (proposal) -> rejection -> empirical CDF.
    """
    rng = np.random.default_rng(11)

    def target_pdf(x):
        return float(normal.pdf(x, mu=0.0, sigma=1.0))

    out = rejection_sample(
        target_pdf=target_pdf,
        proposal_dist=normal,
        proposal_params={"mu": 0.0, "sigma": 1.0},
        M=1.0,
        n_samples=2_000,
        seed=11,
    )
    assert out.size == 2000
    # The accepted sample should have empirical mean ~ 0, std ~ 1.
    assert abs(np.mean(out)) < 0.1
    assert abs(np.std(out) - 1.0) < 0.1


def test_kde_close_to_true_pdf():
    """KDE on 5k N(0,1) draws is close to true density at 0."""
    rng = np.random.default_rng(13)
    samples = rng.standard_normal(size=5_000)
    f = kde(samples, bandwidth="silverman")
    true = normal.pdf(0.0, mu=0.0, sigma=1.0)
    assert abs(f(0.0) - true) < 0.05


def test_sample_quantile_inverse_round_trip():
    """For a large sample, quantile(F_n(x)) recovers ~x.

    Composition: sample -> empirical_cdf -> normal.quantile chain
    (Glivenko-Cantelli at intermediate point).
    """
    rng = np.random.default_rng(19)
    samples = normal.sample(20_000, mu=2.0, sigma=1.0, seed=19)
    ec = empirical_cdf(samples)
    # Pick a known x.
    x = 2.5
    p = ec(x)
    x_recovered = normal.quantile(p, mu=2.0, sigma=1.0)
    assert abs(x_recovered - x) < 0.05


def test_bootstrap_ci_re_export_works_on_normal_samples():
    """bootstrap_ci re-export covers a known population mean."""
    from prometheus_math.statistics_distributions import bootstrap_ci

    if bootstrap_ci is None:  # pragma: no cover
        pytest.skip("research.bootstrap not importable")
    rng = np.random.default_rng(23)
    samples = 5.0 + rng.standard_normal(size=2_000)
    res = bootstrap_ci(samples, np.mean, n_resamples=2_000, seed=23)
    assert res["ci_lower"] < 5.0 < res["ci_upper"]


def test_multivariate_normal_basic_round_trip():
    """MVN: 1-D special case agrees with N(mu, sigma^2)."""
    mean = [0.0, 1.0]
    cov = [[1.0, 0.0], [0.0, 4.0]]
    pdf_at_mean = multivariate_normal.pdf([0.0, 1.0], mean=mean, cov=cov)
    # 1/(2*pi * sqrt(det(cov))) at the mean.
    det = 1.0 * 4.0
    expected = 1.0 / (2.0 * math.pi * math.sqrt(det))
    assert abs(pdf_at_mean - expected) < 1e-9
    # Sampling shape.
    samples = multivariate_normal.sample(1000, mean=mean, cov=cov, seed=0)
    assert samples.shape == (1000, 2)
    # Marginal mean ~ given mean (large-n).
    assert np.allclose(samples.mean(axis=0), mean, atol=0.15)


def test_discrete_cdf_matches_pdf_cumulative_sum():
    """For a discrete family, cdf(k) == sum_{j<=k} pdf(j)."""
    ks = np.arange(0, 11)
    pmf = np.array([poisson.pdf(int(k), mu=2.5) for k in ks])
    cdf_direct = np.array([poisson.cdf(int(k), mu=2.5) for k in ks])
    cdf_from_pmf = np.cumsum(pmf)
    assert np.allclose(cdf_direct, cdf_from_pmf, atol=1e-12)


def test_all_listed_families_present():
    """Every family in the spec is in the FAMILIES registry."""
    expected = {
        "normal", "exponential", "beta", "gamma", "chi2", "t", "f",
        "binomial", "poisson", "geometric", "negative_binomial",
        "uniform", "lognormal", "log_normal", "weibull", "cauchy",
        "laplace", "pareto", "multivariate_normal",
    }
    assert expected.issubset(set(FAMILIES.keys()))


def test_log_normal_alias_is_lognormal():
    """log_normal is an alias of lognormal."""
    from prometheus_math.statistics_distributions import log_normal
    assert log_normal is lognormal
