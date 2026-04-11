"""
Lattice Theta Series Sparsity vs Dimension, Determinant, and Kissing Number
============================================================================
Challenge: measure the exact relationship between theta series sparsity
and lattice invariants (dim, det, kissing). Is there a universal sparsity law?
"""

import json
import numpy as np
from collections import defaultdict
from scipy import stats
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

# ---------- 1. Load data ----------
DATA_PATH = "F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json"
OUT_PATH  = "F:/Prometheus/cartography/v2/lattice_sparsity_results.json"

print("Loading lattices...")
with open(DATA_PATH) as f:
    raw = json.load(f)

records = raw["records"]
print(f"Loaded {len(records)} lattices")

# ---------- 2. Compute sparsity for each lattice ----------
rows = []
for rec in records:
    ts = rec.get("theta_series")
    if not ts or len(ts) < 2:
        continue
    # sparsity = fraction of zero coefficients (excluding q^0 = 1 always)
    coeffs = ts[1:]  # skip constant term
    if len(coeffs) == 0:
        continue
    n_zero = sum(1 for c in coeffs if c == 0)
    sparsity = n_zero / len(coeffs)

    dim = rec.get("dim")
    det = rec.get("det")
    kissing = rec.get("kissing")
    minimum = rec.get("minimum")
    level = rec.get("level")

    if dim is None or det is None:
        continue

    rows.append({
        "label": rec.get("label", ""),
        "dim": int(dim),
        "det": int(det) if det is not None else None,
        "kissing": int(kissing) if kissing is not None else None,
        "minimum": int(minimum) if minimum is not None else None,
        "level": int(level) if level is not None else None,
        "sparsity": sparsity,
        "theta_len": len(ts),
        "n_zero": n_zero,
    })

print(f"Computed sparsity for {len(rows)} lattices")

# ---------- 3. Basic statistics ----------
dims = sorted(set(r["dim"] for r in rows))
print(f"Dimensions present: {dims}")

by_dim = defaultdict(list)
for r in rows:
    by_dim[r["dim"]].append(r)

print("\n=== Sparsity by dimension ===")
dim_stats = {}
for d in dims:
    sp = [r["sparsity"] for r in by_dim[d]]
    dim_stats[d] = {
        "count": len(sp),
        "mean": float(np.mean(sp)),
        "std": float(np.std(sp)),
        "median": float(np.median(sp)),
        "min": float(np.min(sp)),
        "max": float(np.max(sp)),
    }
    print(f"  dim={d}: n={len(sp):>6}, mean={np.mean(sp):.4f}, std={np.std(sp):.4f}, "
          f"median={np.median(sp):.4f}, range=[{np.min(sp):.4f}, {np.max(sp):.4f}]")

# ---------- 4. Regression: sparsity vs dim ----------
print("\n=== Regression: sparsity vs dim ===")
all_dims = np.array([r["dim"] for r in rows], dtype=float)
all_sp   = np.array([r["sparsity"] for r in rows], dtype=float)
all_det  = np.array([r["det"] for r in rows], dtype=float)
all_kiss = np.array([r["kissing"] for r in rows if r["kissing"] is not None], dtype=float)
all_sp_kiss = np.array([r["sparsity"] for r in rows if r["kissing"] is not None], dtype=float)

# Linear
slope_dim, intercept_dim, r_dim, p_dim, se_dim = stats.linregress(all_dims, all_sp)
print(f"  Linear: sparsity = {slope_dim:.6f}*dim + {intercept_dim:.6f}")
print(f"  R² = {r_dim**2:.6f}, p = {p_dim:.2e}")

# ---------- 5. Regression: sparsity vs log(det) ----------
print("\n=== Regression: sparsity vs log(det) ===")
log_det = np.log(all_det + 1)
slope_det, intercept_det, r_det, p_det, se_det = stats.linregress(log_det, all_sp)
print(f"  Linear: sparsity = {slope_det:.6f}*log(det) + {intercept_det:.6f}")
print(f"  R² = {r_det**2:.6f}, p = {p_det:.2e}")

# ---------- 6. Regression: sparsity vs kissing ----------
print("\n=== Regression: sparsity vs kissing ===")
if len(all_kiss) > 10:
    slope_kiss, intercept_kiss, r_kiss, p_kiss, se_kiss = stats.linregress(all_kiss, all_sp_kiss)
    print(f"  Linear: sparsity = {slope_kiss:.6f}*kissing + {intercept_kiss:.6f}")
    print(f"  R² = {r_kiss**2:.6f}, p = {p_kiss:.2e}")

    # Also log(kissing)
    mask_k = all_kiss > 0
    if mask_k.sum() > 10:
        slope_lk, intercept_lk, r_lk, p_lk, se_lk = stats.linregress(
            np.log(all_kiss[mask_k]), all_sp_kiss[mask_k])
        print(f"  Log: sparsity = {slope_lk:.6f}*log(kissing) + {intercept_lk:.6f}")
        print(f"  R² = {r_lk**2:.6f}, p = {p_lk:.2e}")
else:
    slope_kiss = intercept_kiss = r_kiss = p_kiss = 0
    slope_lk = intercept_lk = r_lk = p_lk = 0

# ---------- 7. Within fixed dimension: which invariant best predicts sparsity? ----------
print("\n=== Within-dimension regressions ===")
within_dim_results = {}
for d in dims:
    sub = by_dim[d]
    if len(sub) < 20:
        continue
    sp = np.array([r["sparsity"] for r in sub])
    det_arr = np.array([r["det"] for r in sub], dtype=float)
    kiss_arr = np.array([r["kissing"] for r in sub if r["kissing"] is not None], dtype=float)
    sp_kiss = np.array([r["sparsity"] for r in sub if r["kissing"] is not None])

    res = {"n": len(sub)}

    # log(det) within this dim
    ld = np.log(det_arr + 1)
    if np.std(ld) > 1e-10 and np.std(sp) > 1e-10:
        sl, ic, rv, pv, _ = stats.linregress(ld, sp)
        res["log_det_R2"] = float(rv**2)
        res["log_det_slope"] = float(sl)
        res["log_det_p"] = float(pv)

    # kissing within this dim
    if len(kiss_arr) > 10 and np.std(kiss_arr) > 1e-10 and np.std(sp_kiss) > 1e-10:
        sl, ic, rv, pv, _ = stats.linregress(kiss_arr, sp_kiss)
        res["kissing_R2"] = float(rv**2)
        res["kissing_slope"] = float(sl)
        res["kissing_p"] = float(pv)

    # minimum within this dim
    min_arr = np.array([r["minimum"] for r in sub if r["minimum"] is not None], dtype=float)
    sp_min  = np.array([r["sparsity"] for r in sub if r["minimum"] is not None])
    if len(min_arr) > 10 and np.std(min_arr) > 1e-10 and np.std(sp_min) > 1e-10:
        sl, ic, rv, pv, _ = stats.linregress(min_arr, sp_min)
        res["minimum_R2"] = float(rv**2)
        res["minimum_slope"] = float(sl)
        res["minimum_p"] = float(pv)

    within_dim_results[d] = res

    best = max(
        [(res.get("log_det_R2", 0), "log_det"),
         (res.get("kissing_R2", 0), "kissing"),
         (res.get("minimum_R2", 0), "minimum")],
        key=lambda x: x[0]
    )
    print(f"  dim={d}: n={len(sub):>5}, best predictor = {best[1]} (R²={best[0]:.4f}), "
          f"log_det R²={res.get('log_det_R2', 0):.4f}")

# ---------- 8. Universal formula: sparsity ≈ f(dim, det) ----------
print("\n=== Universal formula search ===")

# Model 1: sparsity = a*dim + b*log(det) + c
X = np.column_stack([all_dims, log_det, np.ones(len(all_dims))])
coeffs_ols, residuals, rank, sv = np.linalg.lstsq(X, all_sp, rcond=None)
pred_m1 = X @ coeffs_ols
ss_res_m1 = np.sum((all_sp - pred_m1)**2)
ss_tot = np.sum((all_sp - np.mean(all_sp))**2)
r2_m1 = 1 - ss_res_m1 / ss_tot
print(f"  Model 1: sparsity = {coeffs_ols[0]:.6f}*dim + {coeffs_ols[1]:.6f}*log(det) + {coeffs_ols[2]:.6f}")
print(f"  R² = {r2_m1:.6f}")

# Model 2: sparsity = a*dim + b*log(det) + c*dim*log(det) + d
X2 = np.column_stack([all_dims, log_det, all_dims * log_det, np.ones(len(all_dims))])
coeffs_m2, _, _, _ = np.linalg.lstsq(X2, all_sp, rcond=None)
pred_m2 = X2 @ coeffs_m2
r2_m2 = 1 - np.sum((all_sp - pred_m2)**2) / ss_tot
print(f"  Model 2: sparsity = {coeffs_m2[0]:.6f}*dim + {coeffs_m2[1]:.6f}*log(det) + {coeffs_m2[2]:.6f}*dim*log(det) + {coeffs_m2[3]:.6f}")
print(f"  R² = {r2_m2:.6f}")

# Model 3: sparsity = a*log(det/dim^k) + b  (scale-invariant)
# Try: sparsity = a * log(det) / dim + b
ratio = log_det / all_dims
slope_r, intercept_r, r_r, p_r, _ = stats.linregress(ratio, all_sp)
print(f"  Model 3: sparsity = {slope_r:.6f}*log(det)/dim + {intercept_r:.6f}")
print(f"  R² = {r_r**2:.6f}")

# Model 4: sparsity = 1 - a * dim^b / det^c  (power law)
# Use log transform: log(1 - sparsity) = log(a) + b*log(dim) + c*log(det)
# Filter to 0 < sparsity < 1
mask4 = (all_sp > 0.01) & (all_sp < 0.99) & (all_det > 0)
log_1ms = np.log(1 - all_sp[mask4])
X4 = np.column_stack([np.log(all_dims[mask4]), np.log(all_det[mask4]), np.ones(mask4.sum())])
c4, _, _, _ = np.linalg.lstsq(X4, log_1ms, rcond=None)
pred_log = X4 @ c4
r2_m4_log = 1 - np.sum((log_1ms - pred_log)**2) / np.sum((log_1ms - np.mean(log_1ms))**2)
# Back-transform
a4 = np.exp(c4[2])
b4 = c4[0]
c4_det = c4[1]
print(f"  Model 4: 1-sparsity = {a4:.6f} * dim^{b4:.4f} * det^{c4_det:.6f}")
print(f"  R² (log space) = {r2_m4_log:.6f}")
# Actual R² in original space
pred_sp_m4 = 1 - a4 * (all_dims[mask4]**b4) * (all_det[mask4]**c4_det)
r2_m4_orig = 1 - np.sum((all_sp[mask4] - pred_sp_m4)**2) / np.sum((all_sp[mask4] - np.mean(all_sp[mask4]))**2)
print(f"  R² (original space) = {r2_m4_orig:.6f}")

# Model 5: Include kissing number
rows_full = [r for r in rows if r["kissing"] is not None and r["kissing"] > 0 and r["det"] > 0]
if len(rows_full) > 100:
    d5 = np.array([r["dim"] for r in rows_full], dtype=float)
    det5 = np.array([r["det"] for r in rows_full], dtype=float)
    k5 = np.array([r["kissing"] for r in rows_full], dtype=float)
    sp5 = np.array([r["sparsity"] for r in rows_full])

    X5 = np.column_stack([d5, np.log(det5+1), np.log(k5), np.ones(len(d5))])
    c5, _, _, _ = np.linalg.lstsq(X5, sp5, rcond=None)
    pred5 = X5 @ c5
    ss_tot5 = np.sum((sp5 - np.mean(sp5))**2)
    r2_m5 = 1 - np.sum((sp5 - pred5)**2) / ss_tot5
    print(f"\n  Model 5 (with kissing): sparsity = {c5[0]:.6f}*dim + {c5[1]:.6f}*log(det) + {c5[2]:.6f}*log(kissing) + {c5[3]:.6f}")
    print(f"  R² = {r2_m5:.6f}")

# ---------- 9. Jacobi theta zero pattern comparison ----------
print("\n=== Jacobi theta zero pattern analysis ===")
# For the classical Jacobi theta_3(q) = 1 + 2*sum(q^(n^2)), zeros are at non-square indices
# For lattice thetas, zeros occur at values not represented by the quadratic form
# Check: does sparsity track with "representation density" = kissing/det ?

# For dim=2 lattices, check zero positions
print("  Checking zero positions in dim=2 lattices (sample)...")
dim2 = by_dim.get(2, [])[:100]
zero_positions = defaultdict(int)
total_checked = 0
for rec_info in dim2:
    # Get original record
    label = rec_info["label"]
    for orig in records:
        if orig.get("label") == label:
            ts = orig["theta_series"][1:]  # skip q^0
            for i, c in enumerate(ts):
                if c == 0:
                    zero_positions[i+1] += 1
            total_checked += 1
            break

if total_checked > 0:
    # Most common zero positions
    common_zeros = sorted(zero_positions.items(), key=lambda x: -x[1])[:20]
    print(f"  Checked {total_checked} dim=2 lattices")
    print(f"  Most universal zeros (position: count/{total_checked}):")
    for pos, cnt in common_zeros[:10]:
        print(f"    q^{pos}: zero in {cnt}/{total_checked} lattices ({cnt/total_checked*100:.1f}%)")

# ---------- 10. Theta series length distribution ----------
print("\n=== Theta series length distribution ===")
lengths = defaultdict(list)
for r in rows:
    lengths[r["dim"]].append(r["theta_len"])
for d in dims:
    lens = lengths[d]
    print(f"  dim={d}: theta_len = {min(lens)}-{max(lens)}, mean={np.mean(lens):.0f}")

# ---------- 11. Assemble results ----------
print("\n=== Assembling results ===")

# Determine best universal model
models = {
    "linear_dim_logdet": {"formula": f"sparsity = {coeffs_ols[0]:.6f}*dim + {coeffs_ols[1]:.6f}*log(det) + {coeffs_ols[2]:.6f}", "R2": float(r2_m1)},
    "interaction_dim_logdet": {"formula": f"sparsity = {coeffs_m2[0]:.6f}*dim + {coeffs_m2[1]:.6f}*log(det) + {coeffs_m2[2]:.6f}*dim*log(det) + {coeffs_m2[3]:.6f}", "R2": float(r2_m2)},
    "ratio_logdet_dim": {"formula": f"sparsity = {slope_r:.6f}*log(det)/dim + {intercept_r:.6f}", "R2": float(r_r**2)},
    "power_law": {"formula": f"1-sparsity = {a4:.6f} * dim^{b4:.4f} * det^{c4_det:.6f}", "R2_log": float(r2_m4_log), "R2_orig": float(r2_m4_orig)},
}

best_model_name = max(models, key=lambda k: models[k].get("R2", models[k].get("R2_orig", 0)))
best_model = models[best_model_name]

results = {
    "challenge": "Lattice Theta Series Sparsity vs Dimension and Determinant",
    "data_source": "LMFDB lat_lattices (39,293 lattices)",
    "n_analyzed": len(rows),
    "dimensions_present": dims,

    "sparsity_by_dimension": {str(d): dim_stats[d] for d in dims},

    "global_regressions": {
        "sparsity_vs_dim": {
            "slope": float(slope_dim),
            "intercept": float(intercept_dim),
            "R2": float(r_dim**2),
            "p_value": float(p_dim),
        },
        "sparsity_vs_log_det": {
            "slope": float(slope_det),
            "intercept": float(intercept_det),
            "R2": float(r_det**2),
            "p_value": float(p_det),
        },
        "sparsity_vs_kissing": {
            "slope": float(slope_kiss),
            "intercept": float(intercept_kiss),
            "R2": float(r_kiss**2) if r_kiss else 0,
            "p_value": float(p_kiss) if p_kiss else 1,
        },
        "sparsity_vs_log_kissing": {
            "slope": float(slope_lk),
            "intercept": float(intercept_lk),
            "R2": float(r_lk**2) if r_lk else 0,
            "p_value": float(p_lk) if p_lk else 1,
        },
    },

    "within_dimension_regressions": {str(d): v for d, v in within_dim_results.items()},

    "universal_formula_search": models,
    "best_universal_model": {
        "name": best_model_name,
        **best_model,
    },

    "findings": [],
}

# Generate findings
findings = []

# Finding 1: sparsity vs dimension direction
if slope_dim < 0:
    findings.append(f"Sparsity DECREASES with dimension (slope={slope_dim:.6f}, R²={r_dim**2:.4f}): higher-dim lattices represent more integers.")
else:
    findings.append(f"Sparsity INCREASES with dimension (slope={slope_dim:.6f}, R²={r_dim**2:.4f}): higher-dim lattices are sparser.")

# Finding 2: best global predictor
global_r2 = {
    "dim": r_dim**2,
    "log_det": r_det**2,
    "kissing": r_kiss**2 if r_kiss else 0,
}
best_pred = max(global_r2, key=global_r2.get)
findings.append(f"Best single global predictor: {best_pred} (R²={global_r2[best_pred]:.4f})")

# Finding 3: within-dimension best predictor
within_bests = defaultdict(int)
for d, res in within_dim_results.items():
    best = max(
        [(res.get("log_det_R2", 0), "log_det"),
         (res.get("kissing_R2", 0), "kissing"),
         (res.get("minimum_R2", 0), "minimum")],
        key=lambda x: x[0]
    )
    within_bests[best[1]] += 1
findings.append(f"Within fixed dimension, best predictor frequencies: {dict(within_bests)}")

# Finding 4: universal formula
findings.append(f"Best universal model: {best_model_name} with R²={best_model.get('R2', best_model.get('R2_orig', 0)):.4f}")

# Finding 5: sparsity range
all_sp_sorted = sorted(all_sp)
findings.append(f"Overall sparsity range: [{all_sp_sorted[0]:.4f}, {all_sp_sorted[-1]:.4f}], median={np.median(all_sp):.4f}")

# Finding 6: is there a universal law?
best_r2 = best_model.get("R2", best_model.get("R2_orig", 0))
if best_r2 > 0.8:
    findings.append(f"YES: universal sparsity law found ({best_model_name}, R²={best_r2:.4f})")
elif best_r2 > 0.5:
    findings.append(f"PARTIAL: moderate universal trend ({best_model_name}, R²={best_r2:.4f}), but significant residual variance")
else:
    findings.append(f"NO universal sparsity law: best model R²={best_r2:.4f}. Sparsity depends on finer structure beyond dim/det")

results["findings"] = findings

for f in findings:
    print(f"  >> {f}")

# Save
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT_PATH}")
