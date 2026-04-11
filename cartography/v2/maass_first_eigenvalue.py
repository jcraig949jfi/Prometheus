"""
Maass First Eigenvalue Statistics by Level
==========================================
How does the smallest spectral parameter R_1 depend on level?

Selberg's eigenvalue conjecture: lambda_1 >= 1/4 for congruence subgroups,
i.e., R_1 >= 0 (since lambda = 1/4 + R^2).

Unconditional bounds:
  - Selberg (1965): lambda_1 >= 3/16   => R >= sqrt(3/16 - 1/4) is N/A (3/16 < 1/4)
    Actually: forms with lambda < 1/4 are "exceptional"; R is purely imaginary.
    For R real: lambda = 1/4 + R^2 >= 1/4 automatically.
    Selberg's bound means no exceptional eigenvalues below 3/16.
  - Kim-Sarnak (2003): lambda_1 >= 975/4096 ~ 0.2380

Data: LMFDB PostgreSQL dump of maass_newforms (14,995 records)
"""

import json
import numpy as np
from scipy import stats
from collections import defaultdict
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "lmfdb_dump" / "maass_newforms.json"
OUT_PATH = Path(__file__).parent / "maass_first_eigenvalue_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

records = raw["records"]
print(f"Loaded {len(records)} Maass newform records")

# Parse spectral parameters (stored as strings in postgres envelope)
forms = []
for r in records:
    try:
        sp = float(r["spectral_parameter"])
    except (ValueError, TypeError):
        continue
    forms.append({
        "spectral_parameter": sp,
        "level": int(r["level"]),
        "symmetry": int(r["symmetry"]),  # 1=even, -1=odd
    })

print(f"Parsed {len(forms)} forms with valid spectral parameters")

# ── Group by level ────────────────────────────────────────────────────
by_level = defaultdict(list)
for f in forms:
    by_level[f["level"]].append(f)

levels_sorted = sorted(by_level.keys())
print(f"Distinct levels: {len(levels_sorted)}")
print(f"Level range: {min(levels_sorted)} to {max(levels_sorted)}")

# ── For each level: min spectral parameter R_1 ───────────────────────
level_stats = []
for N in levels_sorted:
    group = by_level[N]
    sps = [g["spectral_parameter"] for g in group]
    R1 = min(sps)
    lambda1 = 0.25 + R1**2
    # By symmetry
    even_sps = [g["spectral_parameter"] for g in group if g["symmetry"] == 1]
    odd_sps = [g["spectral_parameter"] for g in group if g["symmetry"] == -1]
    # Some may have symmetry=0 (unknown)
    other_sps = [g["spectral_parameter"] for g in group if g["symmetry"] not in (1, -1)]

    level_stats.append({
        "level": N,
        "count": len(group),
        "R1_min": R1,
        "lambda1": lambda1,
        "R1_even": min(even_sps) if even_sps else None,
        "R1_odd": min(odd_sps) if odd_sps else None,
        "count_even": len(even_sps),
        "count_odd": len(odd_sps),
        "count_other": len(other_sps),
    })

# ── Selberg conjecture verification ──────────────────────────────────
# lambda >= 1/4 means R >= 0 (R is real, positive for non-exceptional)
# In the LMFDB data, spectral_parameter R is always >= 0 for Maass forms
# with lambda >= 1/4. Any R listed is real => lambda = 1/4 + R^2 >= 1/4.
#
# The question is whether any EXCEPTIONAL eigenvalues (0 < lambda < 1/4)
# exist. These would have purely imaginary R, not real.
# LMFDB stores R as real positive => all forms satisfy Selberg's conjecture.

all_R = [f["spectral_parameter"] for f in forms]
all_R_arr = np.array(all_R)
min_R = float(np.min(all_R_arr))
min_lambda = 0.25 + min_R**2

print(f"\n=== Selberg Conjecture Verification ===")
print(f"Minimum spectral parameter R: {min_R:.10f}")
print(f"Minimum eigenvalue lambda = 1/4 + R^2: {min_lambda:.10f}")
print(f"Selberg conjecture (lambda >= 1/4): {'SATISFIED' if min_lambda >= 0.25 else 'VIOLATED'}")
print(f"  (All R >= 0 => lambda >= 1/4 automatically for real R)")

# Check for very small R (close to exceptional)
SELBERG_BOUND = 3.0 / 16.0       # 0.1875
KIM_SARNAK_BOUND = 975.0 / 4096.0  # ~0.23804
small_R_forms = [f for f in forms if f["spectral_parameter"] < 1.0]
very_small_R = [f for f in forms if f["spectral_parameter"] < 0.1]

print(f"\nForms with R < 1.0: {len(small_R_forms)}")
print(f"Forms with R < 0.1: {len(very_small_R)}")

# Lambda values for small-R forms
for f in sorted(small_R_forms, key=lambda x: x["spectral_parameter"])[:10]:
    lam = 0.25 + f["spectral_parameter"]**2
    print(f"  Level={f['level']}, R={f['spectral_parameter']:.10f}, lambda={lam:.10f}, sym={f['symmetry']}")

# ── R1 vs level scaling ──────────────────────────────────────────────
print(f"\n=== R1 vs Level ===")
levels_arr = np.array([s["level"] for s in level_stats], dtype=float)
R1_arr = np.array([s["R1_min"] for s in level_stats])

# Log-log fit: R1 ~ N^alpha
mask = (levels_arr > 0) & (R1_arr > 0)
if np.sum(mask) > 10:
    log_N = np.log(levels_arr[mask])
    log_R1 = np.log(R1_arr[mask])
    slope, intercept, r_value, p_value, std_err = stats.linregress(log_N, log_R1)
    print(f"Log-log fit: R1 ~ N^{slope:.4f}")
    print(f"  R^2 = {r_value**2:.4f}, p = {p_value:.2e}")
    print(f"  Interpretation: {'R1 decreases' if slope < 0 else 'R1 increases'} with level")
else:
    slope, intercept, r_value, p_value, std_err = None, None, None, None, None
    print("Not enough data for log-log fit")

# Linear fit
lin_slope, lin_int, lin_r, lin_p, lin_se = stats.linregress(levels_arr, R1_arr)
print(f"Linear fit: R1 = {lin_slope:.6f} * N + {lin_int:.4f}")
print(f"  R^2 = {lin_r**2:.4f}")

# ── R1 distribution ──────────────────────────────────────────────────
print(f"\n=== R1 Distribution ===")
R1_all = R1_arr[R1_arr > 0]
print(f"  N levels with R1 > 0: {len(R1_all)}")
print(f"  Mean R1: {np.mean(R1_all):.6f}")
print(f"  Median R1: {np.median(R1_all):.6f}")
print(f"  Std R1: {np.std(R1_all):.6f}")
print(f"  Min R1: {np.min(R1_all):.6f}")
print(f"  Max R1: {np.max(R1_all):.6f}")

# Percentiles
for p in [5, 10, 25, 50, 75, 90, 95]:
    print(f"  {p}th percentile: {np.percentile(R1_all, p):.6f}")

# ── Symmetry dependence ──────────────────────────────────────────────
print(f"\n=== Symmetry Dependence ===")
R1_even = [s["R1_even"] for s in level_stats if s["R1_even"] is not None]
R1_odd = [s["R1_odd"] for s in level_stats if s["R1_odd"] is not None]

print(f"Levels with even forms: {len(R1_even)}")
print(f"Levels with odd forms: {len(R1_odd)}")

if R1_even:
    R1_even_arr = np.array(R1_even)
    print(f"Even: mean R1 = {np.mean(R1_even_arr):.6f}, median = {np.median(R1_even_arr):.6f}")
if R1_odd:
    R1_odd_arr = np.array(R1_odd)
    print(f"Odd:  mean R1 = {np.mean(R1_odd_arr):.6f}, median = {np.median(R1_odd_arr):.6f}")

# Compare even vs odd where both exist
both_levels = [s for s in level_stats if s["R1_even"] is not None and s["R1_odd"] is not None]
if len(both_levels) > 5:
    even_vals = np.array([s["R1_even"] for s in both_levels])
    odd_vals = np.array([s["R1_odd"] for s in both_levels])
    diff = even_vals - odd_vals
    print(f"\nPaired comparison (levels with both symmetries): {len(both_levels)} levels")
    print(f"  Mean(R1_even - R1_odd) = {np.mean(diff):.6f}")
    print(f"  Even < Odd in {np.sum(diff < 0)}/{len(diff)} levels")
    # Wilcoxon signed-rank test
    if len(diff) > 10:
        w_stat, w_p = stats.wilcoxon(even_vals, odd_vals)
        print(f"  Wilcoxon test: W={w_stat:.1f}, p={w_p:.4e}")

# ── Kim-Sarnak / Selberg gap analysis ────────────────────────────────
print(f"\n=== Exceptional Eigenvalue Gap ===")
print(f"Selberg bound: lambda >= 3/16 = {SELBERG_BOUND:.6f}")
print(f"Kim-Sarnak bound: lambda >= 975/4096 = {KIM_SARNAK_BOUND:.6f}")
print(f"Selberg conjecture: lambda >= 1/4 = 0.250000")

# For real R, lambda = 1/4 + R^2 >= 1/4 always.
# The gap between 3/16 and 1/4 is where exceptional eigenvalues would live.
# These would NOT appear as real R in the database.
# So we check: are there any forms with anomalously small R?
print(f"\nSmallest lambda values in dataset:")
lambda_vals = [0.25 + f["spectral_parameter"]**2 for f in forms]
lambda_arr = np.array(lambda_vals)
sorted_idx = np.argsort(lambda_arr)
for i in sorted_idx[:15]:
    f = forms[i]
    print(f"  Level={f['level']}, R={f['spectral_parameter']:.10f}, "
          f"lambda={0.25+f['spectral_parameter']**2:.10f}, sym={f['symmetry']}")

# ── Level-binned statistics ───────────────────────────────────────────
print(f"\n=== Level-Binned R1 ===")
bins = [(1, 10), (11, 50), (51, 100), (101, 500), (501, 1000), (1001, 5000), (5001, 100000)]
for lo, hi in bins:
    subset = [s for s in level_stats if lo <= s["level"] <= hi]
    if subset:
        r1s = np.array([s["R1_min"] for s in subset])
        print(f"  Level [{lo:>5d}, {hi:>5d}]: {len(subset):>4d} levels, "
              f"mean R1={np.mean(r1s):.4f}, median={np.median(r1s):.4f}, "
              f"min={np.min(r1s):.4f}, max={np.max(r1s):.4f}")

# ── Build results ─────────────────────────────────────────────────────
results = {
    "title": "Maass First Eigenvalue Statistics by Level",
    "data_source": str(DATA_PATH),
    "total_forms": len(forms),
    "total_levels": len(levels_sorted),
    "level_range": [int(min(levels_sorted)), int(max(levels_sorted))],

    "selberg_conjecture": {
        "statement": "lambda_1 >= 1/4 for congruence subgroups",
        "min_R_in_data": float(min_R),
        "min_lambda_in_data": float(min_lambda),
        "conjecture_satisfied": bool(min_lambda >= 0.25),
        "note": "All spectral parameters in LMFDB are real positive => lambda = 1/4 + R^2 >= 1/4. "
                "Exceptional eigenvalues (lambda < 1/4) would have imaginary R and are not stored this way.",
        "forms_below_quarter": 0,
        "selberg_unconditional_bound": float(SELBERG_BOUND),
        "kim_sarnak_bound": float(KIM_SARNAK_BOUND),
    },

    "R1_distribution": {
        "mean": float(np.mean(R1_all)),
        "median": float(np.median(R1_all)),
        "std": float(np.std(R1_all)),
        "min": float(np.min(R1_all)),
        "max": float(np.max(R1_all)),
        "percentiles": {str(p): float(np.percentile(R1_all, p)) for p in [5, 10, 25, 50, 75, 90, 95]},
    },

    "level_scaling": {
        "log_log_slope": float(slope) if slope is not None else None,
        "log_log_R2": float(r_value**2) if r_value is not None else None,
        "log_log_p": float(p_value) if p_value is not None else None,
        "linear_slope": float(lin_slope),
        "linear_R2": float(lin_r**2),
        "interpretation": (
            f"R1 scales as N^{slope:.3f} (log-log); "
            f"{'weak' if abs(r_value**2 if r_value else 0) < 0.3 else 'moderate' if abs(r_value**2 if r_value else 0) < 0.6 else 'strong'} correlation"
        ) if slope is not None else "insufficient data",
    },

    "symmetry_dependence": {
        "levels_with_even": len(R1_even),
        "levels_with_odd": len(R1_odd),
        "mean_R1_even": float(np.mean(R1_even_arr)) if R1_even else None,
        "mean_R1_odd": float(np.mean(R1_odd_arr)) if R1_odd else None,
        "median_R1_even": float(np.median(R1_even_arr)) if R1_even else None,
        "median_R1_odd": float(np.median(R1_odd_arr)) if R1_odd else None,
        "paired_comparison_levels": len(both_levels) if both_levels else 0,
        "wilcoxon_p": float(w_p) if (both_levels and len(both_levels) > 10) else None,
    },

    "smallest_eigenvalues": [
        {
            "level": int(forms[i]["level"]),
            "spectral_parameter": float(forms[i]["spectral_parameter"]),
            "lambda": float(0.25 + forms[i]["spectral_parameter"]**2),
            "symmetry": int(forms[i]["symmetry"]),
        }
        for i in sorted_idx[:20]
    ],

    "level_binned": [
        {
            "bin": f"[{lo}, {hi}]",
            "n_levels": len([s for s in level_stats if lo <= s["level"] <= hi]),
            "mean_R1": float(np.mean([s["R1_min"] for s in level_stats if lo <= s["level"] <= hi]))
                if [s for s in level_stats if lo <= s["level"] <= hi] else None,
            "median_R1": float(np.median([s["R1_min"] for s in level_stats if lo <= s["level"] <= hi]))
                if [s for s in level_stats if lo <= s["level"] <= hi] else None,
        }
        for lo, hi in bins
    ],

    "per_level": [
        {
            "level": s["level"],
            "count": s["count"],
            "R1_min": float(s["R1_min"]),
            "lambda1": float(s["lambda1"]),
            "R1_even": float(s["R1_even"]) if s["R1_even"] is not None else None,
            "R1_odd": float(s["R1_odd"]) if s["R1_odd"] is not None else None,
        }
        for s in level_stats
    ],
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
