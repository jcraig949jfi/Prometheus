"""prometheus_math.statistics_distributions — clean, named distribution API.

Project #74 Phase 1.

Wraps scipy.stats with a uniform, named-keyword-argument API for the
common univariate (and one multivariate) distribution families. Every
family exposes the same seven primitives:

    pdf(x, **params)
    cdf(x, **params)
    quantile(p, **params)        (a.k.a. inverse CDF / ppf)
    sample(n, **params, seed=)
    mean(**params)
    var(**params)
    entropy(**params)            (differential entropy, nats)

Plus higher-level helpers:

    kl_divergence(dist_a, params_a, dist_b, params_b) -> float
    moment_estimator(samples, family, n_moments=4) -> dict
    mle_estimator(samples, family) -> dict
    bootstrap_ci(samples, statistic_fn, ...) -> dict (re-export)
    empirical_cdf(samples) -> callable
    rejection_sample(target_pdf, proposal, M, n_samples, seed=) -> ndarray
    kde(samples, bandwidth='silverman') -> callable

Goals:
- scipy.stats is the backbone. We wrap, we do NOT reimplement.
- Each family has an explicit, mathematician-friendly parameter
  vocabulary: normal uses ``mu, sigma``; exponential uses ``rate``;
  poisson uses ``mu`` (Poisson rate); etc.
- Discrete families return PMFs from ``pdf`` (consistent name with
  their continuous cousins) and use the cumulative-probability convention
  ``P[X <= k]`` for ``cdf``.

Phase 2 (multivariate continuous beyond MVN, copulas, mixture models)
is deferred.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Union

import numpy as np
import scipy.stats as _ss
from scipy import integrate as _integrate

# Re-export bootstrap_ci so users can hit pm.statistics_distributions
# for everything in one place.
try:
    from prometheus_math.research.bootstrap import bootstrap_ci  # noqa: F401
except Exception:  # pragma: no cover
    bootstrap_ci = None  # type: ignore[assignment]


__all__ = [
    # families (each exposes pdf/cdf/quantile/sample/mean/var/entropy)
    "normal",
    "exponential",
    "beta",
    "gamma",
    "chi2",
    "t",
    "f",
    "binomial",
    "poisson",
    "geometric",
    "negative_binomial",
    "uniform",
    "lognormal",
    "log_normal",  # alias
    "weibull",
    "cauchy",
    "laplace",
    "pareto",
    "multivariate_normal",
    # registry / dispatch
    "FAMILIES",
    "get_family",
    # helpers
    "kl_divergence",
    "moment_estimator",
    "mle_estimator",
    "bootstrap_ci",
    "empirical_cdf",
    "rejection_sample",
    "kde",
]


# ---------------------------------------------------------------------------
# Family dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Family:
    """A named distribution family.

    Each family carries:

    - ``name`` : canonical lowercase name (e.g. 'normal').
    - ``frozen`` : function ``(**params) -> scipy.stats frozen rv``.
    - ``support`` : function ``(**params) -> (lower, upper)``.
    - ``discrete`` : True for PMF families (binomial/poisson/...).
    """

    name: str
    frozen: Callable[..., Any]
    support: Callable[..., tuple]
    discrete: bool = False

    # ---- the seven primitives ----

    def pdf(self, x, **params):
        """Probability density (continuous) or mass (discrete)."""
        rv = self.frozen(**params)
        return rv.pmf(x) if self.discrete else rv.pdf(x)

    def cdf(self, x, **params):
        """Cumulative distribution function ``P[X <= x]``."""
        return self.frozen(**params).cdf(x)

    def quantile(self, p, **params):
        """Inverse CDF (a.k.a. percent-point function).

        ``quantile(0)`` returns the support lower bound, ``quantile(1)``
        the upper bound. ``p`` outside ``[0, 1]`` raises ValueError.
        """
        p_arr = np.asarray(p, dtype=float)
        if np.any(p_arr < 0.0) or np.any(p_arr > 1.0):
            raise ValueError("quantile p must be in [0, 1]")
        return self.frozen(**params).ppf(p)

    def sample(self, n, seed: Optional[int] = None, **params):
        """Draw ``n`` i.i.d. samples."""
        if int(n) < 0:
            raise ValueError("n must be >= 0")
        if int(n) == 0:
            return np.array([], dtype=float)
        rng = np.random.default_rng(seed)
        return self.frozen(**params).rvs(size=int(n), random_state=rng)

    def mean(self, **params):
        return float(self.frozen(**params).mean())

    def var(self, **params):
        return float(self.frozen(**params).var())

    def entropy(self, **params):
        return float(self.frozen(**params).entropy())


# ---------------------------------------------------------------------------
# Family definitions — each one wraps a scipy.stats distribution with
# our preferred parameter vocabulary.
# ---------------------------------------------------------------------------


def _check_positive(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v) or v <= 0.0:
        raise ValueError(f"{name} must be a positive finite float, got {value!r}")
    return v


def _check_nonneg(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v) or v < 0.0:
        raise ValueError(f"{name} must be a non-negative finite float, got {value!r}")
    return v


def _check_int_nonneg(name: str, value: int) -> int:
    v = int(value)
    if v < 0:
        raise ValueError(f"{name} must be a non-negative int, got {value!r}")
    return v


def _check_prob(name: str, value: float) -> float:
    v = float(value)
    if not (0.0 < v <= 1.0):
        raise ValueError(f"{name} must be in (0, 1], got {value!r}")
    return v


# Normal -- N(mu, sigma).
def _normal_frozen(*, mu: float = 0.0, sigma: float = 1.0):
    sigma = _check_positive("sigma", sigma)
    return _ss.norm(loc=float(mu), scale=sigma)


def _normal_support(**_):
    return (-np.inf, np.inf)


normal = Family("normal", _normal_frozen, _normal_support, discrete=False)


# Exponential -- Exp(rate). PDF = rate * exp(-rate * x), x >= 0.
def _exponential_frozen(*, rate: float = 1.0):
    rate = _check_positive("rate", rate)
    return _ss.expon(scale=1.0 / rate)


def _exponential_support(**_):
    return (0.0, np.inf)


exponential = Family("exponential", _exponential_frozen, _exponential_support)


# Beta -- Beta(alpha, beta) on [0, 1].
def _beta_frozen(*, alpha: float, beta: float):
    a = _check_positive("alpha", alpha)
    b = _check_positive("beta", beta)
    return _ss.beta(a, b)


def _beta_support(**_):
    return (0.0, 1.0)


beta = Family("beta", _beta_frozen, _beta_support)


# Gamma -- Gamma(shape, rate). Mean = shape / rate.
def _gamma_frozen(*, shape: float, rate: float = 1.0):
    s = _check_positive("shape", shape)
    r = _check_positive("rate", rate)
    return _ss.gamma(s, scale=1.0 / r)


def _gamma_support(**_):
    return (0.0, np.inf)


gamma = Family("gamma", _gamma_frozen, _gamma_support)


# Chi-squared -- chi2(k) with k degrees of freedom.
def _chi2_frozen(*, k: float):
    df = _check_positive("k", k)
    return _ss.chi2(df)


def _chi2_support(**_):
    return (0.0, np.inf)


chi2 = Family("chi2", _chi2_frozen, _chi2_support)


# Student's t -- t(df).
def _t_frozen(*, df: float):
    nu = _check_positive("df", df)
    return _ss.t(nu)


def _t_support(**_):
    return (-np.inf, np.inf)


t = Family("t", _t_frozen, _t_support)


# F-distribution -- F(d1, d2).
def _f_frozen(*, d1: float, d2: float):
    a = _check_positive("d1", d1)
    b = _check_positive("d2", d2)
    return _ss.f(a, b)


def _f_support(**_):
    return (0.0, np.inf)


f = Family("f", _f_frozen, _f_support)


# Binomial -- Binom(n, p).
def _binomial_frozen(*, n: int, p: float):
    n = _check_int_nonneg("n", n)
    p_ = float(p)
    if not (0.0 <= p_ <= 1.0):
        raise ValueError(f"p must be in [0, 1], got {p!r}")
    return _ss.binom(n, p_)


def _binomial_support(*, n: int, **_):
    return (0, int(n))


binomial = Family("binomial", _binomial_frozen, _binomial_support, discrete=True)


# Poisson -- Poisson(mu).
def _poisson_frozen(*, mu: float):
    m = _check_positive("mu", mu)
    return _ss.poisson(m)


def _poisson_support(**_):
    return (0, np.inf)


poisson = Family("poisson", _poisson_frozen, _poisson_support, discrete=True)


# Geometric -- number of trials until first success (k = 1, 2, ...).
def _geometric_frozen(*, p: float):
    p_ = _check_prob("p", p)
    return _ss.geom(p_)


def _geometric_support(**_):
    return (1, np.inf)


geometric = Family("geometric", _geometric_frozen, _geometric_support, discrete=True)


# Negative binomial -- NegBin(r, p): number of failures before the r-th success.
def _negative_binomial_frozen(*, r: int, p: float):
    r_ = int(r)
    if r_ <= 0:
        raise ValueError(f"r must be positive int, got {r!r}")
    p_ = _check_prob("p", p)
    return _ss.nbinom(r_, p_)


def _negative_binomial_support(**_):
    return (0, np.inf)


negative_binomial = Family(
    "negative_binomial",
    _negative_binomial_frozen,
    _negative_binomial_support,
    discrete=True,
)


# Uniform -- U(a, b).
def _uniform_frozen(*, a: float = 0.0, b: float = 1.0):
    a_ = float(a)
    b_ = float(b)
    if b_ <= a_:
        raise ValueError(f"need a < b for Uniform; got a={a!r}, b={b!r}")
    return _ss.uniform(loc=a_, scale=b_ - a_)


def _uniform_support(*, a: float = 0.0, b: float = 1.0, **_):
    return (float(a), float(b))


uniform = Family("uniform", _uniform_frozen, _uniform_support)


# LogNormal -- LogNorm(mu, sigma): X = exp(mu + sigma*Z), Z ~ N(0,1).
def _lognormal_frozen(*, mu: float = 0.0, sigma: float = 1.0):
    s = _check_positive("sigma", sigma)
    return _ss.lognorm(s=s, scale=math.exp(float(mu)))


def _lognormal_support(**_):
    return (0.0, np.inf)


lognormal = Family("lognormal", _lognormal_frozen, _lognormal_support)
log_normal = lognormal  # alias


# Weibull -- Weibull(k, lam): k = shape, lam = scale.
def _weibull_frozen(*, k: float, lam: float = 1.0):
    sh = _check_positive("k", k)
    sc = _check_positive("lam", lam)
    return _ss.weibull_min(sh, scale=sc)


def _weibull_support(**_):
    return (0.0, np.inf)


weibull = Family("weibull", _weibull_frozen, _weibull_support)


# Cauchy -- Cauchy(loc, scale).
def _cauchy_frozen(*, loc: float = 0.0, scale: float = 1.0):
    s = _check_positive("scale", scale)
    return _ss.cauchy(loc=float(loc), scale=s)


def _cauchy_support(**_):
    return (-np.inf, np.inf)


cauchy = Family("cauchy", _cauchy_frozen, _cauchy_support)


# Laplace -- Laplace(loc, scale).
def _laplace_frozen(*, loc: float = 0.0, scale: float = 1.0):
    s = _check_positive("scale", scale)
    return _ss.laplace(loc=float(loc), scale=s)


def _laplace_support(**_):
    return (-np.inf, np.inf)


laplace = Family("laplace", _laplace_frozen, _laplace_support)


# Pareto -- Pareto(alpha, xm).
def _pareto_frozen(*, alpha: float, xm: float = 1.0):
    a = _check_positive("alpha", alpha)
    s = _check_positive("xm", xm)
    return _ss.pareto(a, scale=s)


def _pareto_support(*, xm: float = 1.0, **_):
    return (float(xm), np.inf)


pareto = Family("pareto", _pareto_frozen, _pareto_support)


# Multivariate normal -- MVN(mean, cov). Distinct API: pdf/cdf take vectors;
# mean/var return arrays.
class _MultivariateNormal:
    name = "multivariate_normal"
    discrete = False

    @staticmethod
    def _frozen(*, mean, cov):
        m = np.asarray(mean, dtype=float).ravel()
        C = np.asarray(cov, dtype=float)
        if C.shape != (m.size, m.size):
            raise ValueError(
                f"cov must be ({m.size},{m.size}); got {C.shape}"
            )
        # Symmetric? scipy will raise if not PSD.
        try:
            return _ss.multivariate_normal(mean=m, cov=C, allow_singular=False)
        except (np.linalg.LinAlgError, ValueError) as exc:
            raise ValueError(f"invalid covariance matrix: {exc}") from exc

    def frozen(self, **params):
        return self._frozen(**params)

    def support(self, **params):
        m = np.asarray(params["mean"], dtype=float).ravel()
        return (np.full_like(m, -np.inf), np.full_like(m, np.inf))

    def pdf(self, x, **params):
        return self._frozen(**params).pdf(x)

    def cdf(self, x, **params):
        return self._frozen(**params).cdf(x)

    def quantile(self, p, **params):
        # No standard multivariate quantile; raise to be honest.
        raise NotImplementedError(
            "quantile is not defined for multivariate_normal "
            "(use marginal normal.quantile)"
        )

    def sample(self, n, seed: Optional[int] = None, **params):
        if int(n) < 0:
            raise ValueError("n must be >= 0")
        if int(n) == 0:
            d = np.asarray(params["mean"], dtype=float).ravel().size
            return np.empty((0, d), dtype=float)
        rng = np.random.default_rng(seed)
        return self._frozen(**params).rvs(size=int(n), random_state=rng)

    def mean(self, **params):
        return np.asarray(params["mean"], dtype=float).ravel().copy()

    def var(self, **params):
        return np.asarray(params["cov"], dtype=float).copy()

    def entropy(self, **params):
        return float(self._frozen(**params).entropy())


multivariate_normal = _MultivariateNormal()


# Registry
FAMILIES: Dict[str, Any] = {
    "normal": normal,
    "exponential": exponential,
    "beta": beta,
    "gamma": gamma,
    "chi2": chi2,
    "t": t,
    "f": f,
    "binomial": binomial,
    "poisson": poisson,
    "geometric": geometric,
    "negative_binomial": negative_binomial,
    "uniform": uniform,
    "lognormal": lognormal,
    "log_normal": lognormal,
    "weibull": weibull,
    "cauchy": cauchy,
    "laplace": laplace,
    "pareto": pareto,
    "multivariate_normal": multivariate_normal,
}


def get_family(name_or_family) -> Any:
    """Resolve a name or Family object to its Family instance."""
    if isinstance(name_or_family, str):
        try:
            return FAMILIES[name_or_family]
        except KeyError as exc:
            raise ValueError(f"unknown distribution family: {name_or_family!r}") from exc
    return name_or_family


# ---------------------------------------------------------------------------
# kl_divergence
# ---------------------------------------------------------------------------


def _normal_kl(p: dict, q: dict) -> float:
    """Closed-form KL(N(mu1,s1) || N(mu2,s2))."""
    m1, s1 = float(p["mu"]), _check_positive("sigma", p["sigma"])
    m2, s2 = float(q["mu"]), _check_positive("sigma", q["sigma"])
    return math.log(s2 / s1) + (s1**2 + (m1 - m2) ** 2) / (2 * s2**2) - 0.5


def _exponential_kl(p: dict, q: dict) -> float:
    """KL(Exp(r1) || Exp(r2)) = log(r1/r2) + r2/r1 - 1."""
    r1 = _check_positive("rate", p["rate"])
    r2 = _check_positive("rate", q["rate"])
    return math.log(r1 / r2) + r2 / r1 - 1.0


def _poisson_kl(p: dict, q: dict) -> float:
    """KL(Poisson(m1) || Poisson(m2)) = m1*log(m1/m2) + m2 - m1."""
    m1 = _check_positive("mu", p["mu"])
    m2 = _check_positive("mu", q["mu"])
    return m1 * math.log(m1 / m2) + m2 - m1


_CLOSED_FORM_KL = {
    "normal": _normal_kl,
    "exponential": _exponential_kl,
    "poisson": _poisson_kl,
}


def kl_divergence(
    dist_a, params_a: Mapping[str, Any], dist_b, params_b: Mapping[str, Any]
) -> float:
    """KL(P || Q) for two same-family named distributions.

    Closed-form for normal / exponential / poisson; numerical integration
    elsewhere. Continuous families integrate ``p(x) * log p(x)/q(x)`` over
    the support; discrete families sum over a truncation that captures
    >= 1-1e-12 of the mass.
    """
    fa = get_family(dist_a)
    fb = get_family(dist_b)
    if fa.name != fb.name:
        raise ValueError(
            f"kl_divergence requires both distributions be the same family; "
            f"got {fa.name!r} and {fb.name!r}"
        )
    name = fa.name
    if name in _CLOSED_FORM_KL:
        return _CLOSED_FORM_KL[name](dict(params_a), dict(params_b))

    if fa.discrete:
        return _kl_discrete(fa, params_a, params_b)
    return _kl_continuous(fa, params_a, params_b)


def _kl_continuous(family: Family, pa, pb) -> float:
    rva = family.frozen(**pa)
    rvb = family.frozen(**pb)
    lo_a, hi_a = family.support(**pa)

    def integrand(x):
        pdf_p = rva.pdf(x)
        pdf_q = rvb.pdf(x)
        if pdf_p <= 0.0:
            return 0.0
        if pdf_q <= 0.0:
            return np.inf
        return pdf_p * (math.log(pdf_p) - math.log(pdf_q))

    # Integrate over a finite truncation of the support.
    eps = 1e-12
    lo = rva.ppf(eps) if not math.isfinite(lo_a) else lo_a + 1e-12
    hi = rva.ppf(1.0 - eps) if not math.isfinite(hi_a) else hi_a - 1e-12
    val, _err = _integrate.quad(integrand, lo, hi, limit=200)
    return float(max(val, 0.0))


def _kl_discrete(family: Family, pa, pb) -> float:
    rva = family.frozen(**pa)
    rvb = family.frozen(**pb)
    # Truncate at p-mass 1 - 1e-12.
    eps = 1e-12
    k_max = int(rva.ppf(1.0 - eps))
    k_min = int(max(0, rva.ppf(eps)))
    ks = np.arange(k_min, k_max + 1)
    pk = rva.pmf(ks)
    qk = rvb.pmf(ks)
    out = 0.0
    for p_, q_ in zip(pk, qk):
        if p_ <= 0.0:
            continue
        if q_ <= 0.0:
            return np.inf
        out += p_ * (math.log(p_) - math.log(q_))
    return float(max(out, 0.0))


# ---------------------------------------------------------------------------
# Estimators
# ---------------------------------------------------------------------------


def _validate_samples(samples) -> np.ndarray:
    arr = np.asarray(samples, dtype=float)
    if arr.ndim != 1 or arr.size == 0:
        raise ValueError("samples must be a non-empty 1-D array")
    if not np.all(np.isfinite(arr)):
        raise ValueError("samples must be finite")
    return arr


def moment_estimator(
    samples, family, n_moments: int = 4
) -> Dict[str, Any]:
    """Method-of-moments parameter estimation.

    Currently supports normal/exponential/gamma/uniform/poisson. Returns
    a dict ``{ 'family': name, 'params': {...}, 'moments': [m1, ..., mk] }``.
    """
    arr = _validate_samples(samples)
    if int(n_moments) < 1:
        raise ValueError("n_moments must be >= 1")
    if int(n_moments) > arr.size:
        raise ValueError("n_moments must be <= len(samples)")
    fam = get_family(family)

    # Raw and central moments.
    m1 = float(np.mean(arr))
    var = float(np.var(arr, ddof=0))
    moments = [float(np.mean(arr**k)) for k in range(1, int(n_moments) + 1)]

    if fam.name == "normal":
        params = {"mu": m1, "sigma": math.sqrt(max(var, 0.0))}
    elif fam.name == "exponential":
        if m1 <= 0:
            raise ValueError("exponential MoM requires positive sample mean")
        params = {"rate": 1.0 / m1}
    elif fam.name == "gamma":
        if m1 <= 0 or var <= 0:
            raise ValueError("gamma MoM requires positive mean and variance")
        rate = m1 / var
        shape = m1 * rate
        params = {"shape": shape, "rate": rate}
    elif fam.name == "uniform":
        # X ~ U(a,b); E[X] = (a+b)/2; Var[X] = (b-a)^2/12.
        spread = math.sqrt(max(12.0 * var, 0.0))
        a_hat = m1 - spread / 2.0
        b_hat = m1 + spread / 2.0
        params = {"a": a_hat, "b": b_hat}
    elif fam.name == "poisson":
        if m1 <= 0:
            raise ValueError("poisson MoM requires positive sample mean")
        params = {"mu": m1}
    else:
        raise NotImplementedError(
            f"moment_estimator not implemented for family {fam.name!r}"
        )
    return {"family": fam.name, "params": params, "moments": moments}


def mle_estimator(samples, family) -> Dict[str, Any]:
    """Maximum-likelihood parameter estimation.

    Closed-form where available (normal/exponential/poisson/uniform);
    scipy.stats.fit otherwise.
    """
    arr = _validate_samples(samples)
    fam = get_family(family)
    name = fam.name

    if name == "normal":
        mu = float(np.mean(arr))
        sigma = float(np.std(arr, ddof=0))
        if sigma == 0.0:
            raise ValueError("normal MLE: sample variance is zero")
        return {"family": name, "params": {"mu": mu, "sigma": sigma}}
    if name == "exponential":
        m = float(np.mean(arr))
        if m <= 0:
            raise ValueError("exponential MLE requires positive sample mean")
        return {"family": name, "params": {"rate": 1.0 / m}}
    if name == "poisson":
        m = float(np.mean(arr))
        if m <= 0:
            raise ValueError("poisson MLE requires positive sample mean")
        return {"family": name, "params": {"mu": m}}
    if name == "uniform":
        a_hat = float(np.min(arr))
        b_hat = float(np.max(arr))
        if a_hat == b_hat:
            raise ValueError("uniform MLE: degenerate sample (min==max)")
        return {"family": name, "params": {"a": a_hat, "b": b_hat}}
    if name == "lognormal":
        if np.any(arr <= 0):
            raise ValueError("lognormal MLE requires strictly positive samples")
        log_arr = np.log(arr)
        mu = float(np.mean(log_arr))
        sigma = float(np.std(log_arr, ddof=0))
        if sigma == 0.0:
            raise ValueError("lognormal MLE: log-sample variance is zero")
        return {"family": name, "params": {"mu": mu, "sigma": sigma}}
    if name == "gamma":
        # scipy.stats.gamma.fit returns (shape, loc, scale); fix loc=0.
        try:
            shape, loc, scale = _ss.gamma.fit(arr, floc=0.0)
        except Exception as exc:  # pragma: no cover
            raise ValueError(f"gamma MLE failed: {exc}") from exc
        return {
            "family": name,
            "params": {"shape": float(shape), "rate": 1.0 / float(scale)},
        }
    if name == "beta":
        try:
            a_, b_, _loc, _scale = _ss.beta.fit(arr, floc=0.0, fscale=1.0)
        except Exception as exc:  # pragma: no cover
            raise ValueError(f"beta MLE failed: {exc}") from exc
        return {"family": name, "params": {"alpha": float(a_), "beta": float(b_)}}

    raise NotImplementedError(f"mle_estimator not implemented for {name!r}")


# ---------------------------------------------------------------------------
# Empirical CDF
# ---------------------------------------------------------------------------


def empirical_cdf(samples) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
    """Return a callable computing the empirical CDF of ``samples``.

    The empirical CDF is the right-continuous step function

        F_n(x) = (1/n) * #{ x_i <= x }.

    Returns a function ``ec(x) -> float | ndarray``.
    """
    arr = _validate_samples(samples)
    sorted_arr = np.sort(arr)
    n = sorted_arr.size

    def ec(x):
        x_arr = np.asarray(x, dtype=float)
        idx = np.searchsorted(sorted_arr, x_arr, side="right")
        out = idx / n
        if x_arr.ndim == 0:
            return float(out)
        return out

    ec.samples = sorted_arr  # exposed for inspection
    return ec


# ---------------------------------------------------------------------------
# Rejection sampling
# ---------------------------------------------------------------------------


def rejection_sample(
    target_pdf: Callable[[float], float],
    proposal_dist: Any,
    M: float,
    n_samples: int,
    proposal_params: Optional[Dict[str, Any]] = None,
    seed: Optional[int] = None,
    max_iter_per_sample: int = 10_000,
) -> np.ndarray:
    """Generic rejection sampler.

    Draws ``Y ~ proposal``, accepts with probability ``target(Y) / (M * q(Y))``
    where ``q`` is the proposal pdf and ``M`` is an upper bound on
    ``target / q`` over the proposal support.

    Parameters
    ----------
    target_pdf : callable
        Target density f(x). Need not be normalised; M must absorb the
        constant.
    proposal_dist : Family or str
        Family from FAMILIES, or its name.
    M : float
        Envelope constant. Must satisfy ``f(x) <= M * q(x)`` for all x in
        the proposal's support; otherwise the sampler is biased.
    n_samples : int
        Number of accepted samples to return.
    proposal_params : dict
        Parameters for the proposal family. Defaults to ``{}``.
    seed : int or None
    max_iter_per_sample : int
        Per-sample rejection budget; raises RuntimeError if exhausted.
    """
    fam = get_family(proposal_dist)
    if fam.discrete:
        raise ValueError("rejection_sample expects a continuous proposal")
    if M <= 0:
        raise ValueError("M must be positive")
    n_samples = int(n_samples)
    if n_samples < 0:
        raise ValueError("n_samples must be >= 0")
    if n_samples == 0:
        return np.array([], dtype=float)
    proposal_params = dict(proposal_params or {})
    rng = np.random.default_rng(seed)

    accepted = np.empty(n_samples, dtype=float)
    n_accepted = 0
    iters = 0
    max_total_iter = n_samples * max_iter_per_sample
    while n_accepted < n_samples:
        if iters > max_total_iter:
            raise RuntimeError(
                f"rejection_sample exceeded {max_total_iter} iterations "
                f"with only {n_accepted}/{n_samples} accepted; "
                "the envelope M may be too tight or too loose"
            )
        # Batch for speed.
        batch = max(2 * (n_samples - n_accepted), 32)
        ys = fam.frozen(**proposal_params).rvs(size=batch, random_state=rng)
        us = rng.uniform(size=batch)
        target_vals = np.array([float(target_pdf(yv)) for yv in ys])
        proposal_vals = fam.frozen(**proposal_params).pdf(ys)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(proposal_vals > 0, target_vals / (M * proposal_vals), 0.0)
        if np.any(ratio > 1.0 + 1e-9):
            raise ValueError(
                "rejection_sample: target/M*proposal > 1 detected; "
                "envelope M is too small (sampling would be biased)"
            )
        accept_mask = us < ratio
        new_accepts = ys[accept_mask]
        take = min(new_accepts.size, n_samples - n_accepted)
        accepted[n_accepted : n_accepted + take] = new_accepts[:take]
        n_accepted += take
        iters += batch
    return accepted


# ---------------------------------------------------------------------------
# Kernel Density Estimation
# ---------------------------------------------------------------------------


def kde(
    samples,
    bandwidth: Union[str, float] = "silverman",
) -> Callable[[Union[float, np.ndarray]], Union[float, np.ndarray]]:
    """Gaussian KDE backed by ``scipy.stats.gaussian_kde``.

    Returns a callable ``f(x) -> density``. ``bandwidth`` may be
    ``'silverman'``, ``'scott'``, or a positive float (the scalar
    bandwidth in input units; scipy applies it via the ``factor`` kwarg
    on the covariance).
    """
    arr = _validate_samples(samples)
    if isinstance(bandwidth, str):
        if bandwidth not in ("silverman", "scott"):
            raise ValueError("bandwidth string must be 'silverman' or 'scott'")
        kdefn = _ss.gaussian_kde(arr, bw_method=bandwidth)
    else:
        bw = float(bandwidth)
        if bw <= 0.0:
            raise ValueError("bandwidth must be positive")
        kdefn = _ss.gaussian_kde(arr, bw_method=bw)

    def f(x):
        x_arr = np.asarray(x, dtype=float)
        out = kdefn(x_arr.ravel())
        return float(out[0]) if x_arr.ndim == 0 else out.reshape(x_arr.shape)

    f.bandwidth = kdefn.factor
    f.samples = arr
    return f
