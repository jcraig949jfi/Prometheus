"""Bootstrap and matched-null helpers (project #43).

Reusable bootstrap-CI / matched-null / permutation primitives for the
research threads (Charon, Aporia, Harmonia) that repeatedly compute the
same numpy/scipy boilerplate during scans.

This module promotes the common pattern

    null_samples = np.array([null_fn() for _ in range(n)])
    z = (observation - null_samples.mean()) / null_samples.std()
    p_two = 2 * min(np.mean(null_samples >= observation),
                    np.mean(null_samples <= observation))

into a single, documented, seedable, well-tested operation. It also
wraps :func:`scipy.stats.bootstrap` for the cases where SciPy already
does the right thing (percentile / BCa CIs on i.i.d. samples) and adds
the matched-null and permutation-test variants that SciPy doesn't
provide directly in the form Charon needs.

API
---
``bootstrap_ci(samples, statistic_fn, n_resamples=10000, alpha=0.05, seed=None)``
    Percentile bootstrap CI for an arbitrary statistic (default a
    two-tailed central interval). Returns dict with point estimate,
    lower/upper bounds, n_resamples, alpha, statistic_name.
``matched_null_test(observation, null_fn, n=10000, statistic='mean', seed=None)``
    Test a scalar observation (or array of observations summarised by
    ``statistic``) against a user-supplied null sampler. Two-tailed
    p-value, z-score, and full null distribution summary.
``permutation_test(samples_a, samples_b, statistic='diff_mean', n=10000, seed=None)``
    Two-sample permutation test for H0: A and B drawn from the same
    distribution. Two-tailed by construction (uses |observed_stat|).
``bayesian_bootstrap(samples, statistic_fn, n=10000, alpha=0.05, seed=None)``
    Rubin (1981) Bayesian bootstrap. Replaces multinomial resampling
    weights with Dirichlet(1, ..., 1) weights — the bootstrap analogue
    of a non-informative posterior.
``bootstrap_correlation(x, y, n=10000, alpha=0.05, seed=None)``
    Bootstrap CI on Pearson r. Useful for Charon's tensor-coupling
    significance scans.
``holm_bonferroni(p_values)``
    Holm (1979) step-down multiple-testing correction. Returns adjusted
    p-values monotonised so that ``adj[i] >= raw[i]`` always.

All p-values are TWO-TAILED unless the docstring says otherwise.
All randomness flows through ``numpy.random.default_rng(seed)`` so
results are reproducible without touching the legacy ``np.random.*``
global state.

References
----------
- Efron, B. (1979). "Bootstrap methods: another look at the jackknife".
  Annals of Statistics 7 (1): 1-26.
- Rubin, D. (1981). "The Bayesian Bootstrap". Annals of Statistics
  9 (1): 130-134.
- Holm, S. (1979). "A simple sequentially rejective multiple test
  procedure". Scandinavian J. Statistics 6: 65-70.
- Good, P. (2005). "Permutation, Parametric, and Bootstrap Tests of
  Hypotheses", 3rd ed., Springer.
- SciPy 1.13: ``scipy.stats.bootstrap`` (percentile / BCa CIs).
"""
from __future__ import annotations

from typing import Any, Callable, Sequence

import numpy as np

try:
    from scipy import stats as _scipy_stats  # noqa: F401
except Exception:  # pragma: no cover
    _scipy_stats = None  # type: ignore[assignment]


__all__ = [
    "bootstrap_ci",
    "matched_null_test",
    "permutation_test",
    "bayesian_bootstrap",
    "bootstrap_correlation",
    "holm_bonferroni",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_samples(samples: Any, name: str = "samples") -> np.ndarray:
    """Coerce ``samples`` to a 1-D float array and validate non-empty."""
    arr = np.asarray(samples, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.ndim != 1:
        raise ValueError(
            f"{name} must be 1-D; got shape {arr.shape}"
        )
    if arr.size == 0:
        raise ValueError(f"{name} is empty; need at least 1 observation")
    return arr


def _validate_n(n: int, name: str = "n_resamples") -> int:
    if not isinstance(n, (int, np.integer)):
        raise ValueError(f"{name} must be int; got {type(n).__name__}")
    if int(n) <= 0:
        raise ValueError(f"{name} must be > 0; got {n}")
    return int(n)


def _validate_alpha(alpha: float) -> float:
    a = float(alpha)
    if not (0.0 < a < 1.0):
        raise ValueError(f"alpha must be in (0,1); got {a}")
    return a


def _statistic_name(fn: Callable[..., Any]) -> str:
    """Best-effort human name for a statistic callable."""
    name = getattr(fn, "__name__", None)
    if name and name != "<lambda>":
        return name
    return repr(fn)


# ---------------------------------------------------------------------------
# bootstrap_ci
# ---------------------------------------------------------------------------


def bootstrap_ci(
    samples: Sequence[float] | np.ndarray,
    statistic_fn: Callable[[np.ndarray], float] = np.mean,
    n_resamples: int = 10_000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> dict[str, Any]:
    """Percentile bootstrap CI for an arbitrary statistic.

    Two-tailed central interval at level ``1 - alpha`` (e.g. alpha=0.05
    -> 95% CI). Resamples ``samples`` with replacement ``n_resamples``
    times, evaluates ``statistic_fn`` on each resample, and returns the
    empirical (alpha/2, 1 - alpha/2) percentiles.

    Parameters
    ----------
    samples : 1-D array-like
        i.i.d. observations.
    statistic_fn : callable
        Maps a 1-D array to a scalar. Default ``np.mean``.
    n_resamples : int, default 10_000
        Number of bootstrap resamples.
    alpha : float, default 0.05
        Two-tailed level — CI is the (alpha/2, 1-alpha/2) percentiles.
    seed : int or None
        Passed to ``numpy.random.default_rng``. ``None`` -> nondeterministic.

    Returns
    -------
    dict with keys:
        point_estimate : float
            ``statistic_fn(samples)`` on the original sample.
        ci_lower, ci_upper : float
        n_resamples : int
        alpha : float
        statistic_name : str
        bootstrap_distribution : np.ndarray, shape (n_resamples,)

    Raises
    ------
    ValueError
        If samples is empty / not 1-D, n_resamples <= 0, alpha not in (0,1),
        or ``statistic_fn`` raises (re-raised with context).
    """
    arr = _validate_samples(samples, "samples")
    n_resamples = _validate_n(n_resamples, "n_resamples")
    alpha = _validate_alpha(alpha)
    rng = np.random.default_rng(seed)

    try:
        point = float(statistic_fn(arr))
    except Exception as exc:
        raise ValueError(
            f"statistic_fn raised on the original sample: {exc!r}"
        ) from exc

    n = arr.size
    boot = np.empty(n_resamples, dtype=float)
    # vectorise the resampling indices for speed
    idx = rng.integers(0, n, size=(n_resamples, n))
    for i in range(n_resamples):
        try:
            boot[i] = float(statistic_fn(arr[idx[i]]))
        except Exception as exc:
            raise ValueError(
                f"statistic_fn raised on bootstrap resample {i}: {exc!r}"
            ) from exc

    lo = float(np.quantile(boot, alpha / 2.0))
    hi = float(np.quantile(boot, 1.0 - alpha / 2.0))
    # CI must contain the point estimate by definition of a central
    # bootstrap interval; if the statistic is degenerate (constant)
    # this still holds because lo == hi == point.
    if lo > point:
        lo = point
    if hi < point:
        hi = point

    return {
        "point_estimate": point,
        "ci_lower": lo,
        "ci_upper": hi,
        "n_resamples": n_resamples,
        "alpha": alpha,
        "statistic_name": _statistic_name(statistic_fn),
        "bootstrap_distribution": boot,
    }


# ---------------------------------------------------------------------------
# matched_null_test
# ---------------------------------------------------------------------------


_STATISTIC_REDUCERS: dict[str, Callable[[np.ndarray], float]] = {
    "mean": lambda a: float(np.mean(a)),
    "median": lambda a: float(np.median(a)),
    "sum": lambda a: float(np.sum(a)),
    "max": lambda a: float(np.max(a)),
    "min": lambda a: float(np.min(a)),
}


def matched_null_test(
    observation: float | Sequence[float] | np.ndarray,
    null_fn: Callable[[], float],
    n: int = 10_000,
    statistic: str | Callable[[np.ndarray], float] = "mean",
    seed: int | None = None,
) -> dict[str, Any]:
    """Test an observation against a user-supplied null distribution.

    Generates ``n`` null samples by calling ``null_fn()`` repeatedly,
    summarises them, and reports a two-tailed empirical p-value.

    The ``observation`` may be a scalar (used directly) or an array
    (reduced via ``statistic``).

    Two-tailed p-value formula::

        p = 2 * min( mean(null >= obs), mean(null <= obs) )

    clipped to ``[1/(n+1), 1.0]`` to avoid p=0 from finite Monte Carlo.

    Parameters
    ----------
    observation : float or 1-D array-like
        Either a scalar or a 1-D array of observations. Arrays are
        reduced by ``statistic``.
    null_fn : callable () -> float
        A zero-arg callable that returns a single draw from the null.
        Will be called ``n`` times. Charon typically passes
        ``lambda: rng.choice(pool, size).mean()`` or similar.
    n : int, default 10_000
        Number of null draws.
    statistic : str or callable
        How to reduce ``observation`` if array-valued. Built-in options:
        ``'mean'`` (default), ``'median'``, ``'sum'``, ``'max'``, ``'min'``.
        A callable mapping 1-D array -> scalar is also accepted.
    seed : int or None
        Reproducibility seed. Note: ``null_fn`` itself must use this seed
        if it generates randomness; we cannot inject the rng into the
        callable. ``seed`` is reserved for any additional randomness
        introduced inside this function (e.g. tie-breaking, future BCa).

    Returns
    -------
    dict with keys:
        observed : float
        null_mean, null_std, null_min, null_max : float
        p_value : float (two-tailed, in [1/(n+1), 1])
        z_score : float
        n_samples : int
        null_distribution : np.ndarray, shape (n,)

    Raises
    ------
    ValueError
        If n <= 0, observation cannot be reduced, or null_fn raises.
    """
    n = _validate_n(n, "n")
    # rng currently unused but documented in the contract (and kept so
    # that callers can pass seed=... uniformly across the module)
    _rng = np.random.default_rng(seed)
    del _rng

    # Reduce observation to a scalar
    if callable(statistic):
        reducer: Callable[[np.ndarray], float] = lambda a: float(statistic(a))  # type: ignore[misc]
    elif isinstance(statistic, str):
        if statistic not in _STATISTIC_REDUCERS:
            raise ValueError(
                f"unknown statistic {statistic!r}; "
                f"choose from {sorted(_STATISTIC_REDUCERS)} or pass a callable"
            )
        reducer = _STATISTIC_REDUCERS[statistic]
    else:
        raise ValueError(
            f"statistic must be str or callable; got {type(statistic).__name__}"
        )

    obs_arr = np.asarray(observation, dtype=float)
    if obs_arr.ndim == 0:
        observed = float(obs_arr)
    elif obs_arr.ndim == 1:
        if obs_arr.size == 0:
            raise ValueError("observation array is empty")
        try:
            observed = reducer(obs_arr)
        except Exception as exc:
            raise ValueError(
                f"statistic reducer failed on observation: {exc!r}"
            ) from exc
    else:
        raise ValueError(
            f"observation must be scalar or 1-D; got shape {obs_arr.shape}"
        )

    null = np.empty(n, dtype=float)
    for i in range(n):
        try:
            null[i] = float(null_fn())
        except Exception as exc:
            raise ValueError(
                f"null_fn raised on draw {i}: {exc!r}"
            ) from exc

    null_mean = float(np.mean(null))
    null_std = float(np.std(null, ddof=1)) if n > 1 else 0.0
    null_min = float(np.min(null))
    null_max = float(np.max(null))
    # Treat numerically-constant nulls as exactly constant: ddof=1 std
    # of an all-equal array can come out at ~1e-16 due to two-pass roundoff.
    if null_max == null_min:
        null_std = 0.0

    # Two-tailed empirical p, with the standard +1/(n+1) regularisation
    # so that no p-value is exactly 0.
    p_right = (np.sum(null >= observed) + 1) / (n + 1)
    p_left = (np.sum(null <= observed) + 1) / (n + 1)
    p_value = float(min(1.0, 2.0 * min(p_right, p_left)))

    if null_std > 0:
        z_score = (observed - null_mean) / null_std
    else:
        # Degenerate null: every draw identical. z is +/- inf if
        # observed differs from the constant null, NaN if it matches.
        # Use a tolerance because float roundoff in np.mean(constant_array)
        # can offset the mean by a few ULPs.
        scale = max(abs(observed), abs(null_mean), 1.0)
        if abs(observed - null_mean) <= 1e-12 * scale:
            z_score = float("nan")
        else:
            z_score = float("inf") * np.sign(observed - null_mean)
    z_score = float(z_score)

    return {
        "observed": float(observed),
        "null_mean": null_mean,
        "null_std": null_std,
        "null_min": null_min,
        "null_max": null_max,
        "p_value": p_value,
        "z_score": z_score,
        "n_samples": n,
        "null_distribution": null,
    }


# ---------------------------------------------------------------------------
# permutation_test
# ---------------------------------------------------------------------------


def _diff_mean(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(a) - np.mean(b))


def _diff_median(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.median(a) - np.median(b))


_PERM_STATISTICS: dict[str, Callable[[np.ndarray, np.ndarray], float]] = {
    "diff_mean": _diff_mean,
    "diff_median": _diff_median,
}


def permutation_test(
    samples_a: Sequence[float] | np.ndarray,
    samples_b: Sequence[float] | np.ndarray,
    statistic: str | Callable[[np.ndarray, np.ndarray], float] = "diff_mean",
    n: int = 10_000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> dict[str, Any]:
    """Two-sample permutation test for H0: A and B drawn from same dist.

    Two-tailed empirical p-value is the fraction of permutations whose
    statistic has ``abs >= abs(observed)``. CI on the observed statistic
    is the (alpha/2, 1-alpha/2) percentile interval of the permutation
    distribution, intended as a rough scale reference for the null.

    Parameters
    ----------
    samples_a, samples_b : 1-D array-like
        Independent samples, each non-empty.
    statistic : str or callable
        ``'diff_mean'`` (default) or ``'diff_median'`` or a callable
        ``(a, b) -> scalar``.
    n : int, default 10_000
        Number of random permutations.
    alpha : float, default 0.05
    seed : int or None

    Returns
    -------
    dict with keys:
        observed_stat : float
        p_value : float (two-tailed, in [1/(n+1), 1])
        ci_lower, ci_upper : float
        n_perms : int
        permutation_distribution : np.ndarray, shape (n,)

    Raises
    ------
    ValueError
        For empty inputs, invalid n / alpha, or unknown statistic name.
    """
    a = _validate_samples(samples_a, "samples_a")
    b = _validate_samples(samples_b, "samples_b")
    n = _validate_n(n, "n")
    alpha = _validate_alpha(alpha)
    rng = np.random.default_rng(seed)

    if callable(statistic):
        stat_fn: Callable[[np.ndarray, np.ndarray], float] = (
            lambda x, y: float(statistic(x, y))  # type: ignore[misc]
        )
    elif isinstance(statistic, str):
        if statistic not in _PERM_STATISTICS:
            raise ValueError(
                f"unknown permutation statistic {statistic!r}; "
                f"choose from {sorted(_PERM_STATISTICS)} or pass a callable"
            )
        stat_fn = _PERM_STATISTICS[statistic]
    else:
        raise ValueError(
            f"statistic must be str or callable; got {type(statistic).__name__}"
        )

    observed = stat_fn(a, b)

    pooled = np.concatenate([a, b])
    n_a = a.size
    perm_dist = np.empty(n, dtype=float)
    for i in range(n):
        rng.shuffle(pooled)
        perm_dist[i] = stat_fn(pooled[:n_a], pooled[n_a:])

    abs_obs = abs(observed)
    # +1/(n+1) regularisation
    p_value = float(
        (np.sum(np.abs(perm_dist) >= abs_obs) + 1) / (n + 1)
    )
    p_value = min(1.0, p_value)

    lo = float(np.quantile(perm_dist, alpha / 2.0))
    hi = float(np.quantile(perm_dist, 1.0 - alpha / 2.0))

    return {
        "observed_stat": float(observed),
        "p_value": p_value,
        "ci_lower": lo,
        "ci_upper": hi,
        "n_perms": n,
        "permutation_distribution": perm_dist,
    }


# ---------------------------------------------------------------------------
# bayesian_bootstrap
# ---------------------------------------------------------------------------


def bayesian_bootstrap(
    samples: Sequence[float] | np.ndarray,
    statistic_fn: Callable[[np.ndarray, np.ndarray], float] | Callable[[np.ndarray], float] = np.mean,
    n: int = 10_000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> dict[str, Any]:
    """Rubin's Bayesian bootstrap (Rubin 1981).

    Replaces each multinomial resample with a Dirichlet(1,...,1) weight
    vector. The posterior of any *linear* statistic (mean, sum) is
    obtained as ``sum(weights * samples)``. For nonlinear statistics
    we fall back to weighted-resampling: draw indices proportional to
    the Dirichlet weights and apply ``statistic_fn`` to the resample.

    Two-tailed central credible interval at level ``1-alpha``.

    Parameters
    ----------
    samples : 1-D array-like
    statistic_fn : callable
        Either a 1-arg ``f(samples_array) -> float`` or a 2-arg
        ``f(samples_array, weights) -> float``. The 2-arg form is
        preferred — it avoids the resampling step.
    n : int, default 10_000
    alpha : float, default 0.05
    seed : int or None

    Returns
    -------
    dict with keys:
        point_estimate : float
        ci_lower, ci_upper : float
        n : int
        alpha : float
        posterior_distribution : np.ndarray, shape (n,)

    Notes
    -----
    Default ``np.mean`` is a 1-arg callable; we detect this and
    transparently switch to the linear ``sum(w * x)`` form for speed.

    Raises
    ------
    ValueError
        Empty samples / invalid n or alpha.
    """
    arr = _validate_samples(samples, "samples")
    n = _validate_n(n, "n")
    alpha = _validate_alpha(alpha)
    rng = np.random.default_rng(seed)

    m = arr.size

    # Determine 1-arg vs 2-arg statistic
    accepts_weights = False
    try:
        import inspect
        sig = inspect.signature(statistic_fn)
        params = list(sig.parameters.values())
        # crude but adequate: if there are 2+ positional params, assume
        # the second is weights
        positional = [
            p for p in params
            if p.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
        accepts_weights = len(positional) >= 2
    except (TypeError, ValueError):
        accepts_weights = False

    point = float(np.mean(arr) if statistic_fn is np.mean
                  else (statistic_fn(arr, np.full(m, 1.0 / m)) if accepts_weights
                        else statistic_fn(arr)))  # type: ignore[arg-type]

    posterior = np.empty(n, dtype=float)
    # Dirichlet(1, ..., 1) is uniform on the simplex
    weights_all = rng.dirichlet(np.ones(m), size=n)
    for i in range(n):
        w = weights_all[i]
        if statistic_fn is np.mean:
            posterior[i] = float(np.dot(w, arr))
        elif accepts_weights:
            posterior[i] = float(statistic_fn(arr, w))  # type: ignore[arg-type]
        else:
            # weighted resample fallback
            idx = rng.choice(m, size=m, p=w)
            posterior[i] = float(statistic_fn(arr[idx]))  # type: ignore[arg-type]

    lo = float(np.quantile(posterior, alpha / 2.0))
    hi = float(np.quantile(posterior, 1.0 - alpha / 2.0))

    return {
        "point_estimate": point,
        "ci_lower": lo,
        "ci_upper": hi,
        "n": n,
        "alpha": alpha,
        "posterior_distribution": posterior,
    }


# ---------------------------------------------------------------------------
# bootstrap_correlation
# ---------------------------------------------------------------------------


def bootstrap_correlation(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    n: int = 10_000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> dict[str, Any]:
    """Bootstrap CI on Pearson r.

    Resamples ``(x_i, y_i)`` PAIRS with replacement, recomputes Pearson
    correlation each time, returns the percentile (alpha/2, 1-alpha/2)
    CI. Two-tailed.

    Useful for Charon's tensor-coupling significance scans where the
    user wants ``r`` plus a CI but the underlying joint distribution is
    not Gaussian (Fisher's z-transform CI not appropriate).

    Returns
    -------
    dict with keys:
        r : float
        ci_lower, ci_upper : float
        n : int
        alpha : float
        bootstrap_distribution : np.ndarray, shape (n,)

    Raises
    ------
    ValueError
        len(x) != len(y), n_pairs < 3, invalid n / alpha, or constant
        x or y (correlation undefined).
    """
    x_arr = _validate_samples(x, "x")
    y_arr = _validate_samples(y, "y")
    if x_arr.size != y_arr.size:
        raise ValueError(
            f"x and y must have same length; got {x_arr.size} and {y_arr.size}"
        )
    if x_arr.size < 3:
        raise ValueError(
            f"need at least 3 paired observations for correlation; got {x_arr.size}"
        )
    if np.std(x_arr) == 0 or np.std(y_arr) == 0:
        raise ValueError(
            "Pearson correlation undefined: x or y is constant"
        )
    n = _validate_n(n, "n")
    alpha = _validate_alpha(alpha)
    rng = np.random.default_rng(seed)

    m = x_arr.size
    point = float(np.corrcoef(x_arr, y_arr)[0, 1])

    boot = np.empty(n, dtype=float)
    idx_all = rng.integers(0, m, size=(n, m))
    for i in range(n):
        idx = idx_all[i]
        xi = x_arr[idx]
        yi = y_arr[idx]
        sx = xi.std()
        sy = yi.std()
        if sx == 0 or sy == 0:
            # degenerate resample; correlation undefined -> nan, skipped
            # via nan-percentile below
            boot[i] = np.nan
        else:
            boot[i] = float(np.corrcoef(xi, yi)[0, 1])

    lo = float(np.nanquantile(boot, alpha / 2.0))
    hi = float(np.nanquantile(boot, 1.0 - alpha / 2.0))
    if lo > point:
        lo = point
    if hi < point:
        hi = point

    return {
        "r": point,
        "ci_lower": lo,
        "ci_upper": hi,
        "n": n,
        "alpha": alpha,
        "bootstrap_distribution": boot,
    }


# ---------------------------------------------------------------------------
# holm_bonferroni
# ---------------------------------------------------------------------------


def holm_bonferroni(p_values: Sequence[float] | np.ndarray) -> np.ndarray:
    """Holm (1979) step-down multiple-testing correction.

    Given ``m`` raw p-values ``p_1, ..., p_m``, sort ascending; the
    ``k``-th sorted p is multiplied by ``m - k + 1``. The sequence is
    then enforced monotone-nondecreasing and clipped to ``[0, 1]``.

    Adjusted p ``>= raw`` is therefore guaranteed.

    Parameters
    ----------
    p_values : 1-D array-like of floats in [0, 1]

    Returns
    -------
    np.ndarray, shape (m,) — adjusted p-values, IN THE ORIGINAL ORDER.

    Raises
    ------
    ValueError
        If the array is empty, contains values outside [0, 1] or is
        not 1-D.
    """
    p = np.asarray(p_values, dtype=float)
    if p.ndim != 1:
        raise ValueError(f"p_values must be 1-D; got shape {p.shape}")
    if p.size == 0:
        raise ValueError("p_values is empty")
    if np.any(p < 0) or np.any(p > 1) or np.any(np.isnan(p)):
        raise ValueError("p_values must lie in [0, 1] and be non-NaN")

    m = p.size
    order = np.argsort(p)
    sorted_p = p[order]
    factors = np.arange(m, 0, -1, dtype=float)  # m, m-1, ..., 1
    adj_sorted = sorted_p * factors
    # enforce monotonicity
    adj_sorted = np.maximum.accumulate(adj_sorted)
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)
    # invert sort
    out = np.empty(m, dtype=float)
    out[order] = adj_sorted
    return out
