"""
Maass Ramanujan Bound Tightness Analysis

For each Maass form, compute max|c_p| across all prime indices p,
then analyze how close these get to the Ramanujan-Petersson bound of 2.

For Maass forms on GL(2), the RP conjecture states |c_p| <= 2 for all primes p.
Unlike elliptic curves (where RP is proved = Hasse bound), for Maass forms
this is conjectural. We filter out the ~12 forms that violate it (likely
numerical imprecision or non-tempered representations).

Compares to EC result: alpha = 0.456 (deficit 0.044 from RP bound at 0.5).
"""

import json
import numpy as np
from pathlib import Path
from sympy import primerange
from scipy import stats

# -- Load data ----------------------------------------------------------------
DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_PATH = Path(__file__).parent / "maass_ramanujan_tightness_results.json"

with open(DATA_PATH) as f:
    forms = json.load(f)

print(f"Loaded {len(forms)} Maass forms")

# -- For each form: extract prime-indexed coefficients, compute tightness ------
results_per_form = []
n_violators = 0

for form in forms:
    coeffs = form["coefficients"]
    N = len(coeffs)
    level = form.get("level", None)
    R = form.get("spectral_parameter", None)

    # Get all primes up to N (coefficients are c_1, c_2, ..., c_N)
    primes = list(primerange(2, N + 1))

    # Extract |c_p| at prime indices (c_p is at index p-1)
    abs_cp = [abs(coeffs[p - 1]) for p in primes]

    if not abs_cp:
        continue

    max_abs_cp = max(abs_cp)

    # Filter out RP violators (max|c_p| > 2.01 allows tiny numerical noise)
    if max_abs_cp > 2.01:
        n_violators += 1
        continue

    tightness = max_abs_cp / 2.0
    mean_abs_cp = np.mean(abs_cp)

    # Which prime achieves the max?
    argmax_idx = np.argmax(abs_cp)
    argmax_prime = primes[argmax_idx]

    results_per_form.append({
        "maass_id": form.get("maass_id", ""),
        "level": level,
        "spectral_parameter": R,
        "symmetry": form.get("symmetry", None),
        "n_primes": len(primes),
        "max_abs_cp": float(max_abs_cp),
        "tightness": float(tightness),
        "mean_abs_cp": float(mean_abs_cp),
        "argmax_prime": int(argmax_prime),
    })

print(f"Computed tightness for {len(results_per_form)} forms ({n_violators} RP violators filtered)")

# -- Aggregate statistics ------------------------------------------------------
tightness_arr = np.array([r["tightness"] for r in results_per_form])
max_abs_arr = np.array([r["max_abs_cp"] for r in results_per_form])

print("\n=== Ramanujan Tightness Distribution ===")
print(f"  N forms:           {len(tightness_arr)}")
print(f"  Mean tightness:    {np.mean(tightness_arr):.6f}")
print(f"  Median tightness:  {np.median(tightness_arr):.6f}")
print(f"  Std tightness:     {np.std(tightness_arr):.6f}")
print(f"  Min tightness:     {np.min(tightness_arr):.6f}")
print(f"  Max tightness:     {np.max(tightness_arr):.6f}")

print(f"\n  Mean max|c_p|:     {np.mean(max_abs_arr):.6f}")
print(f"  Median max|c_p|:   {np.median(max_abs_arr):.6f}")

frac_above_90 = np.mean(tightness_arr > 0.90)
frac_above_95 = np.mean(tightness_arr > 0.95)
frac_above_99 = np.mean(tightness_arr > 0.99)
frac_above_995 = np.mean(tightness_arr > 0.995)

print(f"\n  Fraction tightness > 0.90:  {frac_above_90:.4f}")
print(f"  Fraction tightness > 0.95:  {frac_above_95:.4f}")
print(f"  Fraction tightness > 0.99:  {frac_above_99:.4f}")
print(f"  Fraction tightness > 0.995: {frac_above_995:.4f}")

# -- Deficit: how far from the bound -------------------------------------------
deficit_arr = 2.0 - max_abs_arr
print(f"\n=== Deficit = 2 - max|c_p| ===")
print(f"  Mean deficit:      {np.mean(deficit_arr):.6f}")
print(f"  Median deficit:    {np.median(deficit_arr):.6f}")
print(f"  Std deficit:       {np.std(deficit_arr):.6f}")
print(f"  Min deficit:       {np.min(deficit_arr):.6f}  (closest to bound)")
print(f"  Max deficit:       {np.max(deficit_arr):.6f}  (farthest from bound)")

# Percentiles
for pct in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    print(f"  {pct}th percentile:  {np.percentile(deficit_arr, pct):.6f}")

# -- Does tightness depend on level? -------------------------------------------
print("\n=== Tightness vs Level ===")
levels_all = np.array([r["level"] for r in results_per_form])
tightness_all = np.array([r["tightness"] for r in results_per_form])

# Spearman correlation
mask = ~np.isnan(levels_all.astype(float))
if mask.sum() > 10:
    rho, pval = stats.spearmanr(levels_all[mask], tightness_all[mask])
    print(f"  Spearman rho(level, tightness): {rho:.6f}, p={pval:.2e}")

# Bin by level ranges
level_bins = [(1, 10), (10, 50), (50, 100), (100, 500), (500, 1000)]
for lo, hi in level_bins:
    mask_bin = (levels_all >= lo) & (levels_all < hi)
    if mask_bin.sum() > 0:
        print(f"  Level [{lo:>4d}, {hi:>4d}): n={mask_bin.sum():>5d}, mean tightness={np.mean(tightness_all[mask_bin]):.6f}")

# -- Does tightness depend on spectral parameter R? ----------------------------
print("\n=== Tightness vs Spectral Parameter ===")
R_all = np.array([r["spectral_parameter"] for r in results_per_form], dtype=float)
mask_R = ~np.isnan(R_all)
if mask_R.sum() > 10:
    rho_R, pval_R = stats.spearmanr(R_all[mask_R], tightness_all[mask_R])
    print(f"  Spearman rho(R, tightness): {rho_R:.6f}, p={pval_R:.2e}")

# Bin by R ranges
R_bins = [(0, 5), (5, 10), (10, 20), (20, 40), (40, 100)]
for lo, hi in R_bins:
    mask_bin = (R_all >= lo) & (R_all < hi)
    if mask_bin.sum() > 0:
        print(f"  R [{lo:>3d}, {hi:>3d}): n={mask_bin.sum():>5d}, mean tightness={np.mean(tightness_all[mask_bin]):.6f}")

# -- Does tightness depend on number of coefficients? --------------------------
print("\n=== Tightness vs Number of Prime Coefficients ===")
n_primes_all = np.array([r["n_primes"] for r in results_per_form])
rho_np, pval_np = stats.spearmanr(n_primes_all, tightness_all)
print(f"  Spearman rho(n_primes, tightness): {rho_np:.6f}, p={pval_np:.2e}")
print(f"  (More primes sampled -> higher max|c_p| expected by extremal statistics)")

# -- Comparison with EC --------------------------------------------------------
print("\n=== Comparison with Elliptic Curves ===")
print(f"  EC: alpha = 0.456 -> tightness ~ 0.912 -> deficit ~ 0.088")
print(f"  Maass: mean tightness = {np.mean(tightness_arr):.4f} -> deficit = {np.mean(deficit_arr):.4f}")
print(f"  Maass median tightness = {np.median(tightness_arr):.4f}")

# -- Extremal statistics null model --------------------------------------------
# Under Sato-Tate (semicircle), the distribution of max|c_p| over k primes
# converges to 2 as k -> inf. The rate depends on the tail of the distribution.
# For ST: P(|c_p| > x) ~ (1 - x^2/4)^{3/2} near x=2
# Expected max over k iid draws from ST:
# E[max] ~ 2 - O(k^{-2/3}) for the Sato-Tate distribution

print("\n=== Extremal Statistics Null Model (Sato-Tate) ===")
# Simulate: draw k samples from Sato-Tate and compute max|x|
np.random.seed(42)
n_sim = 10000
for k in [100, 200, 500, 1000, 2000]:
    # Sato-Tate / Wigner semicircle: density (2/pi)*sqrt(1-(x/2)^2) on [-2,2]
    # Sample via: x = 2*cos(theta), theta uniform on [0,pi]
    maxvals = []
    for _ in range(n_sim):
        theta = np.random.uniform(0, np.pi, size=k)
        samples = 2 * np.cos(theta)
        maxvals.append(np.max(np.abs(samples)))
    maxvals = np.array(maxvals)
    print(f"  k={k:>5d}: E[max|x|] = {np.mean(maxvals):.6f}, tightness = {np.mean(maxvals)/2:.6f}")

# Typical n_primes in our data
median_nprimes = int(np.median(n_primes_all))
print(f"\n  Median n_primes in data: {median_nprimes}")
maxvals_data = []
for _ in range(n_sim):
    theta = np.random.uniform(0, np.pi, size=median_nprimes)
    samples = 2 * np.cos(theta)
    maxvals_data.append(np.max(np.abs(samples)))
maxvals_data = np.array(maxvals_data)
st_null_tightness = np.mean(maxvals_data) / 2
print(f"  ST null at k={median_nprimes}: E[max|x|] = {np.mean(maxvals_data):.6f}, tightness = {st_null_tightness:.6f}")
print(f"  Observed mean tightness:   {np.mean(tightness_arr):.6f}")
excess = np.mean(tightness_arr) - st_null_tightness
print(f"  Excess over ST null:       {excess:+.6f}")

# -- Histogram data ------------------------------------------------------------
hist_counts, hist_edges = np.histogram(tightness_arr, bins=50, range=(0.7, 1.0))
deficit_counts, deficit_edges = np.histogram(deficit_arr, bins=50, range=(0.0, 0.6))

# -- Save results --------------------------------------------------------------
output = {
    "description": "Maass form Ramanujan-Petersson bound tightness analysis",
    "n_forms_total": len(forms),
    "n_forms_analyzed": len(results_per_form),
    "n_rp_violators_filtered": n_violators,
    "summary": {
        "mean_tightness": float(np.mean(tightness_arr)),
        "median_tightness": float(np.median(tightness_arr)),
        "std_tightness": float(np.std(tightness_arr)),
        "min_tightness": float(np.min(tightness_arr)),
        "max_tightness": float(np.max(tightness_arr)),
        "mean_max_abs_cp": float(np.mean(max_abs_arr)),
        "median_max_abs_cp": float(np.median(max_abs_arr)),
        "mean_deficit": float(np.mean(deficit_arr)),
        "median_deficit": float(np.median(deficit_arr)),
        "frac_tightness_above_0.90": float(frac_above_90),
        "frac_tightness_above_0.95": float(frac_above_95),
        "frac_tightness_above_0.99": float(frac_above_99),
        "frac_tightness_above_0.995": float(frac_above_995),
    },
    "deficit_percentiles": {
        str(p): float(np.percentile(deficit_arr, p))
        for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
    },
    "level_dependence": {
        "spearman_rho": float(rho),
        "spearman_p": float(pval),
        "bins": [
            {"range": f"[{lo},{hi})", "n": int(((levels_all >= lo) & (levels_all < hi)).sum()),
             "mean_tightness": float(np.mean(tightness_all[(levels_all >= lo) & (levels_all < hi)]))
             if ((levels_all >= lo) & (levels_all < hi)).sum() > 0 else None}
            for lo, hi in level_bins
        ]
    },
    "spectral_dependence": {
        "spearman_rho": float(rho_R),
        "spearman_p": float(pval_R),
        "bins": [
            {"range": f"[{lo},{hi})", "n": int(((R_all >= lo) & (R_all < hi)).sum()),
             "mean_tightness": float(np.mean(tightness_all[(R_all >= lo) & (R_all < hi)]))
             if ((R_all >= lo) & (R_all < hi)).sum() > 0 else None}
            for lo, hi in R_bins
        ]
    },
    "n_primes_dependence": {
        "spearman_rho": float(rho_np),
        "spearman_p": float(pval_np),
        "median_n_primes": int(median_nprimes),
    },
    "extremal_statistics_null": {
        "description": "Expected max|c_p|/2 under Sato-Tate semicircle for k iid draws",
        "simulated_at_median_k": {
            "k": int(median_nprimes),
            "expected_tightness": float(st_null_tightness),
        },
        "observed_mean_tightness": float(np.mean(tightness_arr)),
        "excess_over_null": float(excess),
    },
    "ec_comparison": {
        "ec_alpha": 0.456,
        "ec_tightness": 0.912,
        "ec_deficit": 0.088,
        "maass_mean_tightness": float(np.mean(tightness_arr)),
        "maass_mean_deficit": float(np.mean(deficit_arr)),
        "maass_median_tightness": float(np.median(tightness_arr)),
        "maass_median_deficit": float(np.median(deficit_arr)),
    },
    "histogram_tightness": {
        "bin_edges": [float(x) for x in hist_edges],
        "counts": [int(x) for x in hist_counts],
    },
    "histogram_deficit": {
        "bin_edges": [float(x) for x in deficit_edges],
        "counts": [int(x) for x in deficit_counts],
    },
}

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
