#!/usr/bin/env python3
"""
NF9: Hecke Eigenvalue Lyapunov Exponent.

Treat normalized Hecke eigenvalues a_p / (2*sqrt(p)) as a discrete dynamical
system indexed by sequential primes.  Compute the maximal Lyapunov exponent
    lambda = (1/N) SUM_{n=1}^{N-1} log|x_{n+1} - x_n|
for each weight-2 dim-1 modular form (up to 2000).

Also compute via the standard Rosenstein nearest-neighbor divergence method
as a cross-check.

Analyse dependence on CM status, conductor, and Sato-Tate group.
"""

import json
import sys
import pathlib
import numpy as np
from sympy import primerange

DB_PATH = pathlib.Path(__file__).resolve().parents[2] / "charon" / "data" / "charon.duckdb"

# First 168 primes (up to 997)
PRIMES = list(primerange(2, 998))
assert len(PRIMES) == 168, f"Expected 168 primes, got {len(PRIMES)}"


def lyapunov_difference(x):
    """
    Compute lambda = (1/(N-1)) SUM log|x_{n+1} - x_n|.
    Returns NaN if any consecutive pair is identical.
    """
    diffs = np.abs(np.diff(x))
    # Replace zeros with tiny epsilon to avoid log(0)
    diffs = np.where(diffs == 0, 1e-15, diffs)
    return np.mean(np.log(diffs))


def lyapunov_rosenstein(x, tau=1, m=3, max_iter=50):
    """
    Rosenstein's method: embed in m-dimensional delay space,
    find nearest neighbor for each point, track divergence.
    Returns estimated lambda.
    """
    N = len(x)
    # Time-delay embedding
    n_embed = N - (m - 1) * tau
    if n_embed < max_iter + 10:
        return np.nan

    embedded = np.array([x[i:i + m * tau:tau] for i in range(n_embed)])

    # For each point, find nearest neighbor (exclude temporal neighbors)
    min_sep = m * tau  # minimum temporal separation
    divergences = np.zeros(max_iter)
    counts = np.zeros(max_iter)

    for i in range(n_embed - max_iter):
        # Distances to all other points
        dists = np.linalg.norm(embedded[i] - embedded, axis=1)
        dists[max(0, i - min_sep):min(n_embed, i + min_sep + 1)] = np.inf

        j = np.argmin(dists)
        if dists[j] == np.inf or dists[j] < 1e-15:
            continue

        # Track divergence
        for k in range(max_iter):
            if i + k >= n_embed or j + k >= n_embed:
                break
            d = np.linalg.norm(embedded[i + k] - embedded[j + k])
            if d > 0:
                divergences[k] += np.log(d)
                counts[k] += 1

    valid = counts > 0
    if valid.sum() < 5:
        return np.nan
    avg_div = np.zeros_like(divergences)
    avg_div[valid] = divergences[valid] / counts[valid]

    # Fit slope to initial linear region
    valid_idx = np.where(valid)[0]
    if len(valid_idx) < 5:
        return np.nan
    # Use first 20 valid points for slope
    use = valid_idx[:min(20, len(valid_idx))]
    if len(use) < 3:
        return np.nan
    coeffs = np.polyfit(use, avg_div[use], 1)
    return coeffs[0]  # slope = Lyapunov exponent


def compute_null_distribution(n_samples=1000, n_primes=168):
    """
    Null model: random sequences drawn from Sato-Tate distribution
    (semicircle on [-1, 1]) to compare against.
    """
    lambdas = []
    for _ in range(n_samples):
        # Sato-Tate: density proportional to sqrt(1 - x^2) on [-1,1]
        # Use rejection sampling or beta distribution
        # Beta(3/2, 3/2) on [0,1] mapped to [-1,1] gives Sato-Tate
        u = np.random.beta(1.5, 1.5, size=n_primes)
        x = 2 * u - 1  # map to [-1, 1]
        lambdas.append(lyapunov_difference(x))
    return np.array(lambdas)


def main():
    import duckdb

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Fetch up to 2000 weight-2 dim-1 forms
    rows = con.execute("""
        SELECT lmfdb_label, level, is_cm, sato_tate_group, ap_coeffs
        FROM modular_forms
        WHERE weight = 2 AND dim = 1 AND ap_coeffs IS NOT NULL
        ORDER BY level
        LIMIT 2000
    """).fetchall()

    print(f"Loaded {len(rows)} forms")

    sqrt_primes = np.sqrt(PRIMES).astype(np.float64)

    results = []
    lambdas_all = []
    lambdas_cm = []
    lambdas_nocm = []
    conductors = []
    lambda_by_conductor_bin = {}

    for label, level, is_cm, st_group, ap_json in rows:
        ap_raw = json.loads(ap_json) if isinstance(ap_json, str) else ap_json
        # Each entry is [a_p] for dim-1
        ap = np.array([a[0] for a in ap_raw], dtype=np.float64)

        if len(ap) < 168:
            continue

        ap = ap[:168]
        # Normalize: x_n = a_{p_n} / (2 * sqrt(p_n))
        x = ap / (2.0 * sqrt_primes)

        # Method 1: difference-based Lyapunov
        lam_diff = lyapunov_difference(x)

        # Method 2: Rosenstein
        lam_ros = lyapunov_rosenstein(x)

        rec = {
            "label": label,
            "level": int(level),
            "is_cm": bool(is_cm),
            "sato_tate": st_group,
            "lambda_diff": float(lam_diff),
            "lambda_rosenstein": float(lam_ros) if not np.isnan(lam_ros) else None,
        }
        results.append(rec)
        lambdas_all.append(lam_diff)
        conductors.append(level)

        if is_cm:
            lambdas_cm.append(lam_diff)
        else:
            lambdas_nocm.append(lam_diff)

        # Bin by conductor
        if level <= 100:
            bkey = "1-100"
        elif level <= 500:
            bkey = "101-500"
        elif level <= 1000:
            bkey = "1001-1000"
        elif level <= 5000:
            bkey = "1001-5000"
        else:
            bkey = "5001+"
        lambda_by_conductor_bin.setdefault(bkey, []).append(lam_diff)

    lambdas_all = np.array(lambdas_all)
    lambdas_cm = np.array(lambdas_cm)
    lambdas_nocm = np.array(lambdas_nocm)

    # Null model
    print("Computing null distribution (Sato-Tate iid)...")
    null_lambdas = compute_null_distribution(n_samples=2000)

    # Statistics
    def stats(arr, name):
        if len(arr) == 0:
            return {"name": name, "count": 0}
        return {
            "name": name,
            "count": len(arr),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "median": float(np.median(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "pct_positive": float(np.mean(arr > 0) * 100),
            "pct_negative": float(np.mean(arr < 0) * 100),
            "q25": float(np.percentile(arr, 25)),
            "q75": float(np.percentile(arr, 75)),
        }

    overall = stats(lambdas_all, "all_forms")
    cm_stats = stats(lambdas_cm, "CM_forms")
    nocm_stats = stats(lambdas_nocm, "non_CM_forms")
    null_stats = stats(null_lambdas, "null_sato_tate_iid")

    # Conductor dependence
    conductor_summary = {}
    for bkey, vals in sorted(lambda_by_conductor_bin.items()):
        conductor_summary[bkey] = stats(np.array(vals), bkey)

    # Rosenstein stats
    ros_vals = [r["lambda_rosenstein"] for r in results if r["lambda_rosenstein"] is not None]
    ros_stats = stats(np.array(ros_vals), "rosenstein_method") if ros_vals else {"name": "rosenstein_method", "count": 0}

    # Histogram bins for distribution
    hist_counts, hist_edges = np.histogram(lambdas_all, bins=50)

    # Correlation: lambda vs log(conductor)
    log_cond = np.log(np.array(conductors, dtype=float))
    corr = float(np.corrcoef(lambdas_all, log_cond)[0, 1])

    # KS test: CM vs non-CM
    from scipy.stats import ks_2samp, mannwhitneyu
    if len(lambdas_cm) > 5 and len(lambdas_nocm) > 5:
        ks_stat, ks_p = ks_2samp(lambdas_cm, lambdas_nocm)
        mw_stat, mw_p = mannwhitneyu(lambdas_cm, lambdas_nocm, alternative='two-sided')
        cm_test = {
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_p),
            "mannwhitney_statistic": float(mw_stat),
            "mannwhitney_pvalue": float(mw_p),
        }
    else:
        cm_test = {"note": "insufficient CM forms for test"}

    # KS test: data vs null
    ks_null_stat, ks_null_p = ks_2samp(lambdas_all, null_lambdas)

    summary = {
        "problem": "NF9: Hecke Eigenvalue Lyapunov Exponent",
        "description": (
            "Treat normalized Hecke eigenvalues x_n = a_{p_n}/(2*sqrt(p_n)) as a "
            "discrete dynamical system. Compute maximal Lyapunov exponent via "
            "difference method and Rosenstein nearest-neighbor divergence."
        ),
        "n_forms": len(results),
        "n_primes": 168,
        "normalization": "x_n = a_{p_n} / (2 * sqrt(p_n)), so x_n in [-1, 1]",
        "overall_statistics": overall,
        "cm_statistics": cm_stats,
        "non_cm_statistics": nocm_stats,
        "null_model_statistics": null_stats,
        "rosenstein_statistics": ros_stats,
        "conductor_dependence": conductor_summary,
        "lambda_vs_log_conductor_correlation": corr,
        "cm_vs_nocm_test": cm_test,
        "data_vs_null_ks": {
            "ks_statistic": float(ks_null_stat),
            "ks_pvalue": float(ks_null_p),
        },
        "histogram": {
            "counts": hist_counts.tolist(),
            "bin_edges": [float(e) for e in hist_edges],
        },
        "interpretation": {},
        "per_form_results": results[:50],  # save first 50 for inspection
    }

    # Interpretation
    interp = []
    if overall["mean"] < -0.5:
        interp.append(
            f"Mean lambda = {overall['mean']:.4f} < 0: the system is CONTRACTING on average. "
            "Consecutive normalized eigenvalues tend to be close, not chaotic."
        )
    elif overall["mean"] > 0:
        interp.append(
            f"Mean lambda = {overall['mean']:.4f} > 0: the system shows CHAOTIC sensitivity."
        )
    else:
        interp.append(
            f"Mean lambda = {overall['mean']:.4f} near zero: borderline/neutral dynamics."
        )

    if abs(corr) < 0.1:
        interp.append(
            f"Correlation with log(conductor) = {corr:.4f}: NO conductor dependence."
        )
    else:
        interp.append(
            f"Correlation with log(conductor) = {corr:.4f}: "
            f"{'positive' if corr > 0 else 'negative'} conductor dependence."
        )

    if "ks_pvalue" in cm_test:
        if cm_test["ks_pvalue"] < 0.01:
            interp.append(
                f"CM vs non-CM: KS p = {cm_test['ks_pvalue']:.2e} — SIGNIFICANT difference. "
                f"CM mean = {cm_stats['mean']:.4f}, non-CM mean = {nocm_stats['mean']:.4f}."
            )
        else:
            interp.append(
                f"CM vs non-CM: KS p = {cm_test['ks_pvalue']:.4f} — no significant difference."
            )

    if ks_null_p < 0.01:
        interp.append(
            f"Data vs Sato-Tate iid null: KS p = {ks_null_p:.2e} — "
            "Hecke eigenvalues are NOT behaving like iid Sato-Tate draws "
            "(serial dependence detected)."
        )
    else:
        interp.append(
            f"Data vs null: KS p = {ks_null_p:.4f} — consistent with iid Sato-Tate model."
        )

    summary["interpretation"] = interp

    # Print summary
    print(f"\n{'='*60}")
    print("NF9: Hecke Eigenvalue Lyapunov Exponent")
    print(f"{'='*60}")
    print(f"Forms analysed: {len(results)}")
    print(f"Overall lambda: mean={overall['mean']:.4f}, std={overall['std']:.4f}")
    print(f"  median={overall['median']:.4f}, range=[{overall['min']:.4f}, {overall['max']:.4f}]")
    print(f"  %positive: {overall['pct_positive']:.1f}%, %negative: {overall['pct_negative']:.1f}%")
    print(f"\nCM forms ({cm_stats['count']}): mean={cm_stats.get('mean','N/A')}")
    print(f"Non-CM forms ({nocm_stats['count']}): mean={nocm_stats.get('mean','N/A')}")
    print(f"Null (iid ST): mean={null_stats['mean']:.4f}, std={null_stats['std']:.4f}")
    print(f"\nCorr(lambda, log N): {corr:.4f}")
    if "ks_pvalue" in cm_test:
        print(f"CM vs non-CM KS p-value: {cm_test['ks_pvalue']:.2e}")
    print(f"Data vs null KS p-value: {ks_null_p:.2e}")
    print(f"\nRosenstein method: mean={ros_stats.get('mean','N/A')}")
    print(f"\nInterpretation:")
    for line in interp:
        print(f"  - {line}")

    out_path = pathlib.Path(__file__).with_name("hecke_lyapunov_results.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
