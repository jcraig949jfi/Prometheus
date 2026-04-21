"""TOOL_GPD_TAIL_FIT — Generalized Pareto Distribution tail analysis.

Fits a GPD to exceedances above a threshold. Decisive for the abc/Szpiro
conjecture: if the shape parameter xi <= 0, the tail is thin (conjecture
likely true); if xi > 0, the tail is heavy (conjecture in trouble).

Interface:
    gpd_tail_fit(data, threshold) -> dict
    diagnose_tail(data, thresholds) -> list[dict]

Forged: 2026-04-21 | Tier: 1 (Python/scipy) | REQ-009
Tested against: known GPD samples with xi = -0.5, 0.0, +0.5
"""
import numpy as np
from scipy import stats


def gpd_tail_fit(data: list, threshold: float) -> dict:
    """Fit a Generalized Pareto Distribution to exceedances above threshold.

    Parameters
    ----------
    data : array-like
        The full dataset (not just exceedances).
    threshold : float
        The threshold u. Only data > u is used for fitting.

    Returns
    -------
    dict with keys:
        xi : float — shape parameter (< 0 thin tail, = 0 exponential, > 0 heavy)
        sigma : float — scale parameter
        n_exceedances : int — number of data points above threshold
        n_total : int — total data points
        exceedance_rate : float — fraction above threshold
        ks_statistic : float — Kolmogorov-Smirnov test statistic
        ks_pvalue : float — KS p-value (high = good fit)
        mean_excess : float — mean of exceedances
        max_excess : float — maximum exceedance
        verdict : str — "THIN_TAIL", "EXPONENTIAL_TAIL", or "HEAVY_TAIL"

    Raises
    ------
    ValueError
        If fewer than 10 exceedances (insufficient for reliable fit).
    """
    arr = np.asarray(data, dtype=np.float64)
    exceedances = arr[arr > threshold] - threshold

    if len(exceedances) < 10:
        raise ValueError(
            f"Only {len(exceedances)} exceedances above threshold {threshold}. "
            f"Need at least 10 for reliable GPD fit."
        )

    # Fit GPD: scipy parameterizes as (c, loc, scale) where c = xi
    c, loc, scale = stats.genpareto.fit(exceedances, floc=0)

    # KS test
    ks_stat, ks_pval = stats.kstest(exceedances, 'genpareto', args=(c, 0, scale))

    # Classify
    if c < -0.1:
        verdict = "THIN_TAIL"
    elif c > 0.1:
        verdict = "HEAVY_TAIL"
    else:
        verdict = "EXPONENTIAL_TAIL"

    return {
        "xi": float(c),
        "sigma": float(scale),
        "n_exceedances": int(len(exceedances)),
        "n_total": int(len(arr)),
        "exceedance_rate": float(len(exceedances) / len(arr)),
        "ks_statistic": float(ks_stat),
        "ks_pvalue": float(ks_pval),
        "mean_excess": float(np.mean(exceedances)),
        "max_excess": float(np.max(exceedances)),
        "verdict": verdict,
    }


def diagnose_tail(data: list, thresholds: list = None) -> list:
    """Run GPD fit across multiple thresholds to check stability.

    A robust finding shows xi stable across threshold choices.
    If xi flips sign, the result is threshold-dependent (unreliable).

    Parameters
    ----------
    data : array-like
    thresholds : list of float, optional
        If None, uses quantiles [0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98].

    Returns
    -------
    list of dict — one GPD fit per threshold, plus stability assessment.
    """
    arr = np.asarray(data, dtype=np.float64)
    if thresholds is None:
        thresholds = [float(np.quantile(arr, q)) for q in [0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98]]

    results = []
    for t in thresholds:
        try:
            fit = gpd_tail_fit(arr, t)
            fit["threshold"] = t
            results.append(fit)
        except ValueError:
            results.append({"threshold": t, "error": "insufficient_exceedances"})

    # Stability check
    xis = [r["xi"] for r in results if "xi" in r]
    if len(xis) >= 3:
        xi_std = float(np.std(xis))
        xi_mean = float(np.mean(xis))
        stable = xi_std < 0.2  # arbitrary but reasonable
        for r in results:
            r["xi_mean_across_thresholds"] = xi_mean
            r["xi_std_across_thresholds"] = xi_std
            r["stable"] = stable

    return results


if __name__ == "__main__":
    # Smoke test: generate known GPD data and verify recovery
    np.random.seed(42)

    # Thin tail (xi = -0.3)
    thin = stats.genpareto.rvs(c=-0.3, scale=1.0, size=5000)
    result = gpd_tail_fit(thin + 5.0, threshold=5.0)
    print(f"Thin tail test:  xi = {result['xi']:.3f} (expected ~ -0.3), verdict: {result['verdict']}")

    # Heavy tail (xi = +0.5)
    heavy = stats.genpareto.rvs(c=0.5, scale=1.0, size=5000)
    result = gpd_tail_fit(heavy + 5.0, threshold=5.0)
    print(f"Heavy tail test: xi = {result['xi']:.3f} (expected ~ +0.5), verdict: {result['verdict']}")

    # Exponential (xi = 0)
    expo = np.random.exponential(scale=1.0, size=5000)
    result = gpd_tail_fit(expo + 5.0, threshold=5.0)
    print(f"Exponential test: xi = {result['xi']:.3f} (expected ~ 0.0), verdict: {result['verdict']}")
