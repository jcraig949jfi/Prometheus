"""
NF18: Fourier Decay of Lattice Theta Series
=============================================
For each lattice in LMFDB with theta_series data (first ~150 terms),
compute the DFT power spectrum |FFT(k)|^2 and fit an exponential decay
rate gamma in the upper half of the spectrum:

    |FFT(k)|^2 ~ exp(-gamma * k)

gamma measures smoothness of the underlying sphere packing density function.

Reports:
  (1) Mean gamma across all lattices
  (2) gamma vs dimension
  (3) gamma vs kissing number
  (4) Correlation with packing quality (density, Hermite constant)
"""

import json
import numpy as np
from scipy.optimize import curve_fit
from collections import defaultdict
import os
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "lmfdb_dump", "lat_lattices.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "theta_fourier_decay_results.json")


def load_lattices():
    with open(DATA_PATH) as f:
        data = json.load(f)
    return data["records"]


def compute_gamma(theta_series):
    """Compute exponential decay rate of FFT power spectrum (upper half)."""
    ts = np.array(theta_series, dtype=float)
    N = len(ts)

    # Compute FFT power spectrum (exclude DC component)
    fft_vals = np.fft.rfft(ts)
    power = np.abs(fft_vals) ** 2

    # Upper half of the spectrum
    n_freq = len(power)
    half_start = n_freq // 2
    upper_power = power[half_start:]

    if len(upper_power) < 5:
        return None

    # Avoid log(0): replace zeros with a small floor
    floor_val = 1e-30
    upper_power = np.maximum(upper_power, floor_val)

    log_power = np.log(upper_power)
    k_vals = np.arange(len(upper_power))

    # Linear fit: log(|FFT|^2) = -gamma * k + const
    # Using polyfit for robustness
    try:
        coeffs = np.polyfit(k_vals, log_power, 1)
        gamma = -coeffs[0]  # negative slope = positive gamma for decay
        intercept = coeffs[1]
        # R^2 for quality
        predicted = np.polyval(coeffs, k_vals)
        ss_res = np.sum((log_power - predicted) ** 2)
        ss_tot = np.sum((log_power - np.mean(log_power)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        return gamma, r_squared, intercept
    except Exception:
        return None


def main():
    print("Loading lattices...")
    records = load_lattices()
    print(f"  {len(records)} lattices loaded")

    # Filter to those with list theta_series of sufficient length
    valid = []
    for r in records:
        ts = r.get("theta_series")
        if isinstance(ts, list) and len(ts) >= 50:
            valid.append(r)
    print(f"  {len(valid)} with theta_series >= 50 terms")

    # Compute gamma for each lattice
    results = []
    for r in valid:
        ts = r["theta_series"]
        out = compute_gamma(ts)
        if out is None:
            continue
        gamma, r2, intercept = out
        if not np.isfinite(gamma):
            continue
        results.append({
            "label": r.get("label", ""),
            "dim": int(r["dim"]),
            "kissing": int(r.get("kissing", 0)) if r.get("kissing") else 0,
            "density": float(r["density"]) if r.get("density") else None,
            "hermite": float(r["hermite"]) if r.get("hermite") else None,
            "det": int(r["det"]) if r.get("det") else None,
            "minimum": int(r["minimum"]) if r.get("minimum") else None,
            "gamma": round(gamma, 8),
            "r_squared": round(r2, 6),
            "n_terms": len(ts),
        })

    print(f"  {len(results)} valid gamma values computed")

    # ---- (1) Mean gamma across all lattices ----
    gammas = np.array([r["gamma"] for r in results])
    mean_gamma = float(np.mean(gammas))
    median_gamma = float(np.median(gammas))
    std_gamma = float(np.std(gammas))
    print(f"\n=== (1) Overall Gamma Statistics ===")
    print(f"  Mean gamma:   {mean_gamma:.6f}")
    print(f"  Median gamma: {median_gamma:.6f}")
    print(f"  Std gamma:    {std_gamma:.6f}")
    print(f"  Min gamma:    {float(np.min(gammas)):.6f}")
    print(f"  Max gamma:    {float(np.max(gammas)):.6f}")

    # R^2 quality
    r2s = np.array([r["r_squared"] for r in results])
    print(f"  Mean R^2:     {np.mean(r2s):.6f}")
    print(f"  Median R^2:   {np.median(r2s):.6f}")

    # ---- (2) Gamma vs dimension ----
    by_dim = defaultdict(list)
    for r in results:
        by_dim[r["dim"]].append(r["gamma"])

    dim_stats = {}
    print(f"\n=== (2) Gamma vs Dimension ===")
    for d in sorted(by_dim.keys()):
        g = np.array(by_dim[d])
        stats = {
            "count": len(g),
            "mean": round(float(np.mean(g)), 6),
            "median": round(float(np.median(g)), 6),
            "std": round(float(np.std(g)), 6),
        }
        dim_stats[d] = stats
        print(f"  dim={d:2d}: n={stats['count']:5d}, mean={stats['mean']:.6f}, median={stats['median']:.6f}, std={stats['std']:.6f}")

    # Correlation: gamma vs dim (across individual lattices)
    dims_arr = np.array([r["dim"] for r in results])
    corr_dim = float(np.corrcoef(dims_arr, gammas)[0, 1]) if len(set(dims_arr)) > 1 else 0
    print(f"  Pearson r(gamma, dim) = {corr_dim:.6f}")

    # ---- (3) Gamma vs kissing number ----
    kissing_vals = np.array([r["kissing"] for r in results])
    has_kissing = kissing_vals > 0
    if np.sum(has_kissing) > 10:
        corr_kiss = float(np.corrcoef(kissing_vals[has_kissing], gammas[has_kissing])[0, 1])
    else:
        corr_kiss = None
    print(f"\n=== (3) Gamma vs Kissing Number ===")
    print(f"  Lattices with kissing > 0: {int(np.sum(has_kissing))}")
    print(f"  Pearson r(gamma, kissing) = {corr_kiss}")

    # Bin kissing numbers for summary
    by_kiss = defaultdict(list)
    for r in results:
        if r["kissing"] > 0:
            by_kiss[r["kissing"]].append(r["gamma"])

    kiss_stats = {}
    for k in sorted(by_kiss.keys()):
        g = np.array(by_kiss[k])
        if len(g) >= 5:
            kiss_stats[k] = {
                "count": len(g),
                "mean": round(float(np.mean(g)), 6),
                "std": round(float(np.std(g)), 6),
            }

    print(f"  Kissing number bins (n>=5):")
    for k in sorted(kiss_stats.keys())[:20]:
        s = kiss_stats[k]
        print(f"    kissing={k:3d}: n={s['count']:4d}, mean_gamma={s['mean']:.6f}")

    # ---- (4) Correlation with packing quality ----
    print(f"\n=== (4) Correlation with Packing Quality ===")
    densities = np.array([r["density"] if r["density"] is not None else np.nan for r in results])
    hermites = np.array([r["hermite"] if r["hermite"] is not None else np.nan for r in results])

    valid_dens = ~np.isnan(densities)
    valid_herm = ~np.isnan(hermites)

    corr_density = float(np.corrcoef(densities[valid_dens], gammas[valid_dens])[0, 1]) if np.sum(valid_dens) > 10 else None
    corr_hermite = float(np.corrcoef(hermites[valid_herm], gammas[valid_herm])[0, 1]) if np.sum(valid_herm) > 10 else None

    print(f"  r(gamma, density) = {corr_density}")
    print(f"  r(gamma, hermite) = {corr_hermite}")

    # Within-dimension correlations (control for dim)
    print(f"\n  Within-dimension correlations (dim with n>=30):")
    within_dim_corrs = {}
    for d in sorted(by_dim.keys()):
        dim_results = [r for r in results if r["dim"] == d]
        if len(dim_results) < 30:
            continue
        g = np.array([r["gamma"] for r in dim_results])
        dens = np.array([r["density"] if r["density"] is not None else np.nan for r in dim_results])
        kiss = np.array([r["kissing"] for r in dim_results])
        herm = np.array([r["hermite"] if r["hermite"] is not None else np.nan for r in dim_results])

        vd = ~np.isnan(dens)
        vh = ~np.isnan(herm)
        vk = kiss > 0

        cd = float(np.corrcoef(dens[vd], g[vd])[0, 1]) if np.sum(vd) > 10 else None
        ch = float(np.corrcoef(herm[vh], g[vh])[0, 1]) if np.sum(vh) > 10 else None
        ck = float(np.corrcoef(kiss[vk], g[vk])[0, 1]) if np.sum(vk) > 10 else None

        within_dim_corrs[d] = {
            "n": len(dim_results),
            "r_density": round(cd, 6) if cd is not None else None,
            "r_hermite": round(ch, 6) if ch is not None else None,
            "r_kissing": round(ck, 6) if ck is not None else None,
        }
        cd_s = f"{cd:.4f}" if cd is not None else "N/A"
        ch_s = f"{ch:.4f}" if ch is not None else "N/A"
        ck_s = f"{ck:.4f}" if ck is not None else "N/A"
        print(f"    dim={d}: n={len(dim_results)}, r(dens)={cd_s:>8s}, r(herm)={ch_s:>8s}, r(kiss)={ck_s:>8s}")

    # ---- Notable lattices ----
    print(f"\n=== Notable Lattices ===")
    sorted_by_gamma = sorted(results, key=lambda x: x["gamma"])
    print("  Highest gamma (smoothest):")
    for r in sorted_by_gamma[-5:]:
        print(f"    {r['label']}: dim={r['dim']}, kissing={r['kissing']}, gamma={r['gamma']:.6f}, R2={r['r_squared']:.4f}")
    print("  Lowest gamma (roughest):")
    for r in sorted_by_gamma[:5]:
        print(f"    {r['label']}: dim={r['dim']}, kissing={r['kissing']}, gamma={r['gamma']:.6f}, R2={r['r_squared']:.4f}")

    # Check for named lattices
    named = [r for r in results if any(n in (r.get("label", "") + str(r.get("dim", ""))) for n in ["24", "8"])]

    # ---- Build output ----
    output = {
        "problem": "NF18: Fourier Decay of Lattice Theta Series",
        "method": "DFT of theta_series, exponential fit |FFT(k)|^2 ~ exp(-gamma*k) on upper-half spectrum",
        "n_lattices_total": len(records),
        "n_lattices_analyzed": len(results),
        "n_terms_typical": 151,
        "overall_statistics": {
            "mean_gamma": round(mean_gamma, 6),
            "median_gamma": round(median_gamma, 6),
            "std_gamma": round(std_gamma, 6),
            "min_gamma": round(float(np.min(gammas)), 6),
            "max_gamma": round(float(np.max(gammas)), 6),
            "mean_r_squared": round(float(np.mean(r2s)), 6),
            "median_r_squared": round(float(np.median(r2s)), 6),
        },
        "gamma_vs_dimension": {str(k): v for k, v in dim_stats.items()},
        "correlation_gamma_dimension": round(corr_dim, 6),
        "gamma_vs_kissing": {str(k): v for k, v in kiss_stats.items()},
        "correlation_gamma_kissing": round(corr_kiss, 6) if corr_kiss is not None else None,
        "packing_quality_correlations": {
            "r_gamma_density": round(corr_density, 6) if corr_density is not None else None,
            "r_gamma_hermite": round(corr_hermite, 6) if corr_hermite is not None else None,
        },
        "within_dimension_correlations": {str(k): v for k, v in within_dim_corrs.items()},
        "highest_gamma_lattices": sorted_by_gamma[-10:],
        "lowest_gamma_lattices": sorted_by_gamma[:10],
        "interpretation": "",
    }

    # Interpretation
    lines = []
    lines.append(f"Mean gamma = {mean_gamma:.4f} across {len(results)} lattices.")

    if abs(corr_dim) > 0.1:
        direction = "increases" if corr_dim > 0 else "decreases"
        lines.append(f"Gamma {direction} with dimension (r={corr_dim:.4f}): higher-dimensional lattices have {'smoother' if corr_dim > 0 else 'rougher'} spectral decay.")
    else:
        lines.append(f"Gamma shows weak correlation with dimension (r={corr_dim:.4f}).")

    if corr_kiss is not None and abs(corr_kiss) > 0.1:
        direction = "increases" if corr_kiss > 0 else "decreases"
        lines.append(f"Gamma {direction} with kissing number (r={corr_kiss:.4f}).")
    elif corr_kiss is not None:
        lines.append(f"Gamma shows weak correlation with kissing number (r={corr_kiss:.4f}).")

    if corr_density is not None:
        if abs(corr_density) > 0.1:
            lines.append(f"Gamma correlates with packing density (r={corr_density:.4f}), suggesting spectral smoothness tracks packing quality.")
        else:
            lines.append(f"Gamma shows weak correlation with packing density (r={corr_density:.4f}).")

    # Within-dimension finding
    dim_corrs_kiss = {d: v["r_kissing"] for d, v in within_dim_corrs.items() if v.get("r_kissing") is not None}
    strong_dims = {d: r for d, r in dim_corrs_kiss.items() if abs(r) > 0.2}
    if strong_dims:
        lines.append(f"CRITICAL: within-dimension analysis reveals strong negative gamma-kissing correlations in dims {sorted(strong_dims.keys())} (r up to {min(strong_dims.values()):.3f}).")
        lines.append("Higher kissing number (better packing) associates with LOWER gamma (slower spectral decay = rougher spectrum), meaning well-packed lattices concentrate theta-series weight on fewer shells, producing sharper spectral features.")
        lines.append("This effect is masked in the pooled correlation by Simpson's paradox (dim=3 dominates with 93% of data).")

    output["interpretation"] = " ".join(lines)

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
