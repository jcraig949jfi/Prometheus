"""
Maass forms: Does spectral parameter R predict coefficient statistics?

The spectral parameter R determines eigenvalue lambda = 1/4 + R^2.
Question: does R predict anything about coefficient distributions
beyond what Sato-Tate predicts?

Approach:
  1. Per-form statistics: mean|c_p|, var(c_p), frac(|c_p|>1), kurtosis
  2. Global correlations with R
  3. Quantile-binned analysis (20 bins)
  4. Critical R detection via changepoint analysis
  5. Level-controlled partial correlations
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path
from collections import defaultdict

# ── Load data ──────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
OUT_PATH = Path(__file__).parent / "maass_R_vs_coefficients_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

print(f"Loaded {len(raw)} Maass forms")

# ── Identify prime indices (0-based: index p-1 gives c_p) ─────────
def sieve_primes(n):
    is_p = [False, False] + [True] * (n - 1)
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n + 1, i):
                is_p[j] = False
    return [i for i in range(2, n + 1) if is_p[i]]

max_coeff_idx = min(x["n_coefficients"] for x in raw)
primes = sieve_primes(max_coeff_idx)
print(f"Using {len(primes)} primes (2..{primes[-1]}), max coeff index = {max_coeff_idx}")

# ── Per-form statistics ────────────────────────────────────────────
records = []
for form in raw:
    R = float(form["spectral_parameter"])
    level = form["level"]
    sym = form["symmetry"]
    coeffs = form["coefficients"]

    # Extract c_p at prime indices (coeffs[0] = c_1, coeffs[p-1] = c_p)
    c_p = np.array([coeffs[p - 1] for p in primes])

    abs_c_p = np.abs(c_p)
    mean_abs = float(np.mean(abs_c_p))
    var_c = float(np.var(c_p))
    frac_gt1 = float(np.mean(abs_c_p > 1.0))
    m2 = float(np.mean(c_p**2))
    m4 = float(np.mean(c_p**4))
    kurtosis_ratio = m4 / m2**2 if m2 > 1e-12 else np.nan

    records.append({
        "R": R,
        "level": level,
        "symmetry": sym,
        "mean_abs_cp": mean_abs,
        "var_cp": var_c,
        "frac_gt1": frac_gt1,
        "kurtosis_ratio": kurtosis_ratio,
    })

R_arr = np.array([r["R"] for r in records])
level_arr = np.array([r["level"] for r in records])
sym_arr = np.array([r["symmetry"] for r in records])

stat_names = ["mean_abs_cp", "var_cp", "frac_gt1", "kurtosis_ratio"]
stat_arrays = {s: np.array([r[s] for r in records]) for s in stat_names}

# ── 1. Global correlations ─────────────────────────────────────────
print("\n=== Global Correlations (R vs statistic) ===")
global_corrs = {}
for s in stat_names:
    mask = np.isfinite(stat_arrays[s])
    r_val, p_val = stats.pearsonr(R_arr[mask], stat_arrays[s][mask])
    rho, rho_p = stats.spearmanr(R_arr[mask], stat_arrays[s][mask])
    global_corrs[s] = {
        "pearson_r": round(float(r_val), 6),
        "pearson_p": float(p_val),
        "spearman_rho": round(float(rho), 6),
        "spearman_p": float(rho_p),
        "n": int(mask.sum()),
    }
    print(f"  {s:20s}: Pearson r={r_val:+.4f} (p={p_val:.2e}), "
          f"Spearman rho={rho:+.4f} (p={rho_p:.2e})")

# ── 2. Quantile-binned analysis (20 bins) ──────────────────────────
print("\n=== Quantile-Binned Analysis (20 bins) ===")
n_bins = 20
quantile_edges = np.quantile(R_arr, np.linspace(0, 1, n_bins + 1))
bin_indices = np.digitize(R_arr, quantile_edges[1:-1])  # 0..n_bins-1

binned_stats = []
for b in range(n_bins):
    mask = bin_indices == b
    if mask.sum() == 0:
        continue
    R_lo = float(R_arr[mask].min())
    R_hi = float(R_arr[mask].max())
    R_med = float(np.median(R_arr[mask]))
    entry = {
        "bin": b,
        "R_range": [round(R_lo, 4), round(R_hi, 4)],
        "R_median": round(R_med, 4),
        "n_forms": int(mask.sum()),
    }
    for s in stat_names:
        vals = stat_arrays[s][mask]
        vals = vals[np.isfinite(vals)]
        entry[f"{s}_mean"] = round(float(np.mean(vals)), 6)
        entry[f"{s}_std"] = round(float(np.std(vals)), 6)
    binned_stats.append(entry)
    print(f"  Bin {b:2d} R=[{R_lo:6.2f},{R_hi:6.2f}] n={mask.sum():5d} "
          f"mean|cp|={entry['mean_abs_cp_mean']:.4f} var={entry['var_cp_mean']:.4f} "
          f"frac>1={entry['frac_gt1_mean']:.4f} kurt={entry['kurtosis_ratio_mean']:.4f}")

# ── 3. Critical R detection ────────────────────────────────────────
print("\n=== Critical R Detection ===")
# For each statistic, find the bin boundary that maximizes the
# difference in means between the two groups (changepoint scan)
critical_R_results = {}
for s in stat_names:
    vals = stat_arrays[s]
    finite_mask = np.isfinite(vals)
    R_f = R_arr[finite_mask]
    v_f = vals[finite_mask]

    sort_idx = np.argsort(R_f)
    R_sorted = R_f[sort_idx]
    v_sorted = v_f[sort_idx]

    n = len(R_sorted)
    min_group = max(50, n // 40)  # at least ~2.5% per side

    best_t = -1
    best_split = None
    best_means = None

    cumsum = np.cumsum(v_sorted)
    total = cumsum[-1]

    for i in range(min_group, n - min_group):
        left_mean = cumsum[i] / (i + 1)
        right_mean = (total - cumsum[i]) / (n - i - 1)
        # Welch's t-statistic approximation
        left_var = np.var(v_sorted[:i+1])
        right_var = np.var(v_sorted[i+1:])
        se = np.sqrt(left_var / (i + 1) + right_var / (n - i - 1))
        if se > 1e-12:
            t = abs(left_mean - right_mean) / se
            if t > best_t:
                best_t = t
                best_split = float(R_sorted[i])
                best_means = (float(left_mean), float(right_mean))

    critical_R_results[s] = {
        "critical_R": round(best_split, 4) if best_split else None,
        "t_statistic": round(float(best_t), 4),
        "left_mean": round(best_means[0], 6) if best_means else None,
        "right_mean": round(best_means[1], 6) if best_means else None,
    }
    print(f"  {s:20s}: critical R = {best_split:.4f}, "
          f"t = {best_t:.2f}, means = {best_means[0]:.4f} vs {best_means[1]:.4f}")

# ── 4. Level-controlled partial correlations ───────────────────────
print("\n=== Level-Controlled Partial Correlations ===")
# Residualize R and each statistic against level, then correlate
partial_corrs = {}
for s in stat_names:
    mask = np.isfinite(stat_arrays[s])
    R_m = R_arr[mask]
    lev_m = level_arr[mask].astype(float)
    val_m = stat_arrays[s][mask]

    # Residualize R against level
    slope_R, intercept_R, _, _, _ = stats.linregress(lev_m, R_m)
    R_resid = R_m - (slope_R * lev_m + intercept_R)

    # Residualize stat against level
    slope_s, intercept_s, _, _, _ = stats.linregress(lev_m, val_m)
    s_resid = val_m - (slope_s * lev_m + intercept_s)

    r_partial, p_partial = stats.pearsonr(R_resid, s_resid)
    rho_partial, rho_p_partial = stats.spearmanr(R_resid, s_resid)

    partial_corrs[s] = {
        "partial_pearson_r": round(float(r_partial), 6),
        "partial_pearson_p": float(p_partial),
        "partial_spearman_rho": round(float(rho_partial), 6),
        "partial_spearman_p": float(rho_p_partial),
    }
    print(f"  {s:20s}: partial Pearson r={r_partial:+.4f} (p={p_partial:.2e}), "
          f"partial Spearman rho={rho_partial:+.4f} (p={rho_p_partial:.2e})")

# ── 5. Symmetry-split analysis ─────────────────────────────────────
print("\n=== Symmetry-Split Correlations ===")
symmetry_corrs = {}
for sym_val in [1, -1]:
    sym_mask = sym_arr == sym_val
    sym_label = "even" if sym_val == 1 else "odd"
    symmetry_corrs[sym_label] = {}
    for s in stat_names:
        mask = sym_mask & np.isfinite(stat_arrays[s])
        r_val, p_val = stats.spearmanr(R_arr[mask], stat_arrays[s][mask])
        symmetry_corrs[sym_label][s] = {
            "spearman_rho": round(float(r_val), 6),
            "spearman_p": float(p_val),
            "n": int(mask.sum()),
        }
    print(f"  {sym_label}: " + ", ".join(
        f"{s}={symmetry_corrs[sym_label][s]['spearman_rho']:+.4f}"
        for s in stat_names))

# ── 6. Per-level within-level correlations ─────────────────────────
print("\n=== Within-Level Correlations (levels with n>=30) ===")
level_groups = defaultdict(list)
for rec in records:
    level_groups[rec["level"]].append(rec)

within_level = {}
for s in stat_names:
    rhos = []
    for lev, recs in sorted(level_groups.items()):
        if len(recs) < 30:
            continue
        Rs = np.array([r["R"] for r in recs])
        vals = np.array([r[s] for r in recs])
        mask = np.isfinite(vals)
        if mask.sum() < 20:
            continue
        rho, _ = stats.spearmanr(Rs[mask], vals[mask])
        if np.isfinite(rho):
            rhos.append(rho)
    within_level[s] = {
        "n_levels": len(rhos),
        "median_rho": round(float(np.median(rhos)), 6) if rhos else None,
        "mean_rho": round(float(np.mean(rhos)), 6) if rhos else None,
        "std_rho": round(float(np.std(rhos)), 6) if rhos else None,
        "frac_positive": round(float(np.mean(np.array(rhos) > 0)), 4) if rhos else None,
    }
    print(f"  {s:20s}: median rho={within_level[s]['median_rho']}, "
          f"mean={within_level[s]['mean_rho']}, "
          f"frac>0={within_level[s]['frac_positive']} ({len(rhos)} levels)")

# ── 7. Sato-Tate baseline comparison ──────────────────────────────
# Under Sato-Tate: c_p ~ 2cos(theta) with theta ~ sin^2 measure
# Expected: E[|c_p|] = 8/(3*pi) ≈ 0.8488, Var(c_p) = 1, kurtosis = 2.0
print("\n=== Sato-Tate Expected Values ===")
st_expected = {
    "mean_abs_cp": 8 / (3 * np.pi),
    "var_cp": 1.0,
    "kurtosis_ratio": 2.0,
    "frac_gt1": 1 - (2/np.pi) * (np.arcsin(0.5) + 0.5 * np.sqrt(3)),
    # P(|2cos(theta)|>1) under sin^2 measure
}
print(f"  ST expected mean|cp| = {st_expected['mean_abs_cp']:.4f}")
print(f"  ST expected var(cp) = {st_expected['var_cp']:.4f}")
print(f"  ST expected kurtosis = {st_expected['kurtosis_ratio']:.4f}")

# Compare observed vs ST per bin
print("\n=== Deviation from Sato-Tate by R-bin ===")
st_deviations = []
for entry in binned_stats:
    dev = {}
    for s in ["mean_abs_cp", "var_cp", "kurtosis_ratio"]:
        if s in st_expected:
            observed = entry[f"{s}_mean"]
            expected = st_expected[s]
            dev[s] = round((observed - expected) / expected, 6)
    st_deviations.append({
        "bin": entry["bin"],
        "R_median": entry["R_median"],
        "rel_deviation": dev,
    })
    print(f"  R={entry['R_median']:6.2f}: "
          f"mean|cp| dev={dev.get('mean_abs_cp',0):+.4f}, "
          f"var dev={dev.get('var_cp',0):+.4f}, "
          f"kurt dev={dev.get('kurtosis_ratio',0):+.4f}")

# ── Verdict ────────────────────────────────────────────────────────
print("\n=== Verdict ===")
# Check if any partial correlation survives significance
sig_threshold = 0.01
surviving = []
for s in stat_names:
    if partial_corrs[s]["partial_pearson_p"] < sig_threshold:
        surviving.append(s)
    if partial_corrs[s]["partial_spearman_p"] < sig_threshold:
        if s not in surviving:
            surviving.append(s)

# Check if within-level correlations are consistently directional
consistent = []
for s in stat_names:
    if within_level[s]["frac_positive"] is not None:
        if within_level[s]["frac_positive"] > 0.7 or within_level[s]["frac_positive"] < 0.3:
            consistent.append(s)

if surviving:
    print(f"  Statistics with significant partial correlations: {surviving}")
else:
    print("  No statistic has significant partial correlation after controlling for level")

if consistent:
    print(f"  Statistics with consistent within-level direction: {consistent}")
else:
    print("  No statistic shows consistent within-level directional correlation")

# Determine if changepoints are meaningful
meaningful_cp = []
for s in stat_names:
    if critical_R_results[s]["t_statistic"] > 10:
        meaningful_cp.append(s)

verdict = (
    "R predicts coefficient statistics" if (surviving and consistent)
    else "R shows statistical signal but confounded with level" if surviving
    else "R shows no meaningful prediction of coefficient statistics after controlling for level"
)
print(f"\n  VERDICT: {verdict}")

# ── Save results ───────────────────────────────────────────────────
results = {
    "question": "Does Maass spectral parameter R predict coefficient statistics beyond Sato-Tate?",
    "data": {
        "n_forms": len(raw),
        "n_primes_used": len(primes),
        "prime_range": [primes[0], primes[-1]],
        "R_range": [round(float(R_arr.min()), 4), round(float(R_arr.max()), 4)],
        "R_median": round(float(np.median(R_arr)), 4),
    },
    "global_correlations": global_corrs,
    "partial_correlations_controlling_level": partial_corrs,
    "within_level_correlations": within_level,
    "symmetry_split_correlations": symmetry_corrs,
    "quantile_binned_stats": binned_stats,
    "sato_tate_deviations_by_bin": st_deviations,
    "critical_R_analysis": critical_R_results,
    "sato_tate_expected": {k: round(v, 6) for k, v in st_expected.items()},
    "verdict": verdict,
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
