#!/usr/bin/env python3
"""
Lattice Theta Coefficient Growth Rate

Theory: for a d-dimensional lattice, the number of representations r(n) grows as
    r(n) ~ C * n^{d/2 - 1}
i.e. the growth exponent alpha = d/2 - 1.

This script:
1. Loads lattices with theta_series and dim from lat_lattices.json
2. For each lattice, fits log(r(n)) vs log(n) for nonzero coefficients
3. Extracts growth exponent alpha
4. Groups by dimension, compares empirical alpha to theoretical d/2-1
5. Reports distribution of alpha within each dimension
6. Identifies outliers that deviate most from theoretical growth
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).resolve().parent / "lattice_theta_growth_results.json"

print("Loading lattice data...")
with open(DATA_PATH) as f:
    data = json.load(f)

records = data["records"]
print(f"Total records: {len(records)}")

# ── Fit growth exponents ──────────────────────────────────────────────────────
MIN_NONZERO = 5  # need at least 5 nonzero coefficients for a meaningful fit
SKIP_FIRST = 1   # skip n=0 (constant term, always 1 for integral lattices)

results_by_dim = defaultdict(list)
all_fits = []

for rec in records:
    theta = rec.get("theta_series")
    dim = rec.get("dim")
    if not theta or dim is None:
        continue

    # Extract (n, r(n)) pairs for nonzero r(n), skipping n=0
    ns = []
    rs = []
    for n in range(SKIP_FIRST, len(theta)):
        if theta[n] > 0:
            ns.append(n)
            rs.append(theta[n])

    if len(ns) < MIN_NONZERO:
        continue

    log_n = np.log(np.array(ns, dtype=float))
    log_r = np.log(np.array(rs, dtype=float))

    # Linear regression: log(r) = alpha * log(n) + log(C)
    coeffs = np.polyfit(log_n, log_r, 1)
    alpha = coeffs[0]
    log_C = coeffs[1]

    # Residual quality
    predicted = alpha * log_n + log_C
    residuals = log_r - predicted
    r_squared = 1.0 - np.var(residuals) / np.var(log_r) if np.var(log_r) > 0 else 0.0

    theoretical_alpha = dim / 2.0 - 1.0
    deviation = alpha - theoretical_alpha

    entry = {
        "label": rec.get("label", rec.get("name", "unknown")),
        "name": rec.get("name", ""),
        "dim": dim,
        "alpha_empirical": round(float(alpha), 6),
        "alpha_theoretical": round(float(theoretical_alpha), 6),
        "deviation": round(float(deviation), 6),
        "abs_deviation": round(float(abs(deviation)), 6),
        "r_squared": round(float(r_squared), 6),
        "log_C": round(float(log_C), 6),
        "n_nonzero_coeffs": len(ns),
        "max_n_used": max(ns),
    }
    all_fits.append(entry)
    results_by_dim[dim].append(entry)

print(f"Fitted {len(all_fits)} lattices across {len(results_by_dim)} dimensions")

# ── Dimension-level summary ───────────────────────────────────────────────────
dim_summaries = []
for dim in sorted(results_by_dim.keys()):
    entries = results_by_dim[dim]
    alphas = [e["alpha_empirical"] for e in entries]
    deviations = [e["deviation"] for e in entries]
    r2s = [e["r_squared"] for e in entries]

    theoretical = dim / 2.0 - 1.0
    summary = {
        "dim": dim,
        "n_lattices": len(entries),
        "alpha_theoretical": round(theoretical, 4),
        "alpha_mean": round(float(np.mean(alphas)), 6),
        "alpha_median": round(float(np.median(alphas)), 6),
        "alpha_std": round(float(np.std(alphas)), 6),
        "alpha_min": round(float(np.min(alphas)), 6),
        "alpha_max": round(float(np.max(alphas)), 6),
        "mean_deviation": round(float(np.mean(deviations)), 6),
        "mean_abs_deviation": round(float(np.mean(np.abs(deviations))), 6),
        "r_squared_mean": round(float(np.mean(r2s)), 6),
        "r_squared_min": round(float(np.min(r2s)), 6),
    }
    dim_summaries.append(summary)

    print(f"\ndim={dim} ({len(entries)} lattices):")
    print(f"  Theoretical alpha = {theoretical:.4f}")
    print(f"  Empirical alpha   = {summary['alpha_mean']:.4f} +/- {summary['alpha_std']:.4f}")
    print(f"  Range: [{summary['alpha_min']:.4f}, {summary['alpha_max']:.4f}]")
    print(f"  Mean deviation    = {summary['mean_deviation']:.4f}")
    print(f"  Mean |deviation|  = {summary['mean_abs_deviation']:.4f}")
    print(f"  R^2 mean          = {summary['r_squared_mean']:.4f}")

# ── Top outliers ──────────────────────────────────────────────────────────────
# Sort all fits by absolute deviation from theory
all_fits_sorted = sorted(all_fits, key=lambda x: x["abs_deviation"], reverse=True)
top_outliers = all_fits_sorted[:20]

print("\n\n=== Top 20 Outliers (largest |deviation| from theory) ===")
for i, o in enumerate(top_outliers):
    print(f"  {i+1}. {o['label']} (dim={o['dim']}): "
          f"alpha={o['alpha_empirical']:.4f} vs theory={o['alpha_theoretical']:.4f} "
          f"(dev={o['deviation']:+.4f}, R^2={o['r_squared']:.4f})")

# ── Overall verdict ───────────────────────────────────────────────────────────
all_devs = [e["deviation"] for e in all_fits]
all_abs_devs = [e["abs_deviation"] for e in all_fits]
overall = {
    "total_lattices_fitted": len(all_fits),
    "mean_deviation": round(float(np.mean(all_devs)), 6),
    "mean_abs_deviation": round(float(np.mean(all_abs_devs)), 6),
    "median_abs_deviation": round(float(np.median(all_abs_devs)), 6),
    "fraction_within_0.5": round(float(np.mean([d < 0.5 for d in all_abs_devs])), 6),
    "fraction_within_0.25": round(float(np.mean([d < 0.25 for d in all_abs_devs])), 6),
    "fraction_within_0.1": round(float(np.mean([d < 0.1 for d in all_abs_devs])), 6),
}

print(f"\n=== Overall ===")
print(f"  Mean deviation:       {overall['mean_deviation']:.4f}")
print(f"  Mean |deviation|:     {overall['mean_abs_deviation']:.4f}")
print(f"  Median |deviation|:   {overall['median_abs_deviation']:.4f}")
print(f"  Within 0.1 of theory: {overall['fraction_within_0.1']*100:.1f}%")
print(f"  Within 0.25:          {overall['fraction_within_0.25']*100:.1f}%")
print(f"  Within 0.5:           {overall['fraction_within_0.5']*100:.1f}%")

# ── Save results ──────────────────────────────────────────────────────────────
output = {
    "description": "Lattice theta series coefficient growth rate analysis",
    "theory": "r(n) ~ C * n^{d/2 - 1} for d-dimensional lattice",
    "method": "OLS fit of log(r(n)) vs log(n) for nonzero coefficients, n >= 1",
    "overall": overall,
    "dimension_summaries": dim_summaries,
    "top_20_outliers": top_outliers,
}

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
