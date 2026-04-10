"""
F24: Prime Interaction Nonlinearity Coefficient

Tests whether constraint interference between prime pairs is linear or
nonlinear in log(ell1 * ell2).

Linear model:   log(I) = a * log(ell1*ell2) + b
Quadratic model: log(I) = a * log(ell1*ell2)^2 + b * log(ell1*ell2) + c

If the quadratic term 'a' is significant, prime interactions have
higher-order coupling -- they are not simply multiplicative.

Uses exact interference data from constraint_interference_results.json
and augmented data from interference_function_results.json.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent

# ── Load data ──────────────────────────────────────────────────────────
with open(DATA_DIR / "constraint_interference_results.json") as f:
    ci_data = json.load(f)

with open(DATA_DIR / "interference_function_results.json") as f:
    if_data = json.load(f)

# ── Extract the 6 prime pairs from {3,5,7,11} ─────────────────────────
primes = [3, 5, 7, 11]
pairs = []
for i in range(len(primes)):
    for j in range(i + 1, len(primes)):
        pairs.append((primes[i], primes[j]))

# Primary data: exact interference from constraint_interference_results
exact = ci_data["exact_interference"]
pair_data = []
for p1, p2 in pairs:
    key = f"{p1}x{p2}"
    entry = exact[key]
    ratio = entry["ratio"]
    pair_data.append({
        "ell_1": p1,
        "ell_2": p2,
        "product": p1 * p2,
        "ratio": ratio,
        "p_value": entry.get("hypergeometric_p", None),
        "N_12": entry.get("N_12_observed", None),
    })

print("=" * 70)
print("F24: PRIME INTERACTION NONLINEARITY COEFFICIENT")
print("=" * 70)
print()

# ── Display raw data ──────────────────────────────────────────────────
print("Raw interference data (6 pairs from {3,5,7,11}):")
print(f"{'Pair':<8} {'Product':>8} {'log(prod)':>10} {'Ratio':>10} {'log(Ratio)':>10} {'N_12':>6} {'p-value':>12}")
print("-" * 70)
for d in pair_data:
    lp = np.log(d["product"])
    lr = np.log(d["ratio"]) if d["ratio"] > 0 else float("nan")
    pval = d["p_value"] if d["p_value"] else "N/A"
    if isinstance(pval, float):
        pval = f"{pval:.2e}"
    print(f"{d['ell_1']}x{d['ell_2']:<5} {d['product']:>8} {lp:>10.4f} {d['ratio']:>10.4f} {lr:>10.4f} {d['N_12']:>6} {pval:>12}")

# ── Filter: only use pairs with positive (constructive) interference ──
# 3x11 has ratio=0.68 (destructive), log is negative -- include it for
# completeness but flag it. For nonlinearity test, we use ALL 6 pairs
# since even destructive interference carries information about the
# functional form.

# For the primary analysis, use all 6 pairs (including destructive 3x11)
x_all = np.array([np.log(d["product"]) for d in pair_data])
y_all = np.array([np.log(d["ratio"]) if d["ratio"] > 0 else np.nan for d in pair_data])

# Identify valid points (non-nan)
valid = ~np.isnan(y_all)
x = x_all[valid]
y = y_all[valid]
labels_all = [f"{d['ell_1']}x{d['ell_2']}" for d in pair_data]
labels = [labels_all[i] for i in range(len(labels_all)) if valid[i]]
n_pts = len(x)

print(f"\nUsing {n_pts} pairs for regression (all with ratio > 0)")

# ── Model 1: Linear ──────────────────────────────────────────────────
# log(I) = a * log(ell1*ell2) + b
A_lin = np.column_stack([x, np.ones(n_pts)])
coeffs_lin, res_lin, rank_lin, sv_lin = np.linalg.lstsq(A_lin, y, rcond=None)
a_lin, b_lin = coeffs_lin
y_pred_lin = A_lin @ coeffs_lin
ss_res_lin = np.sum((y - y_pred_lin) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r2_lin = 1 - ss_res_lin / ss_tot if ss_tot > 0 else 0

# AIC for linear (k=2 params)
k_lin = 2
aic_lin = n_pts * np.log(ss_res_lin / n_pts) + 2 * k_lin if n_pts > 0 else float("inf")

print(f"\n{'-' * 70}")
print(f"MODEL 1: LINEAR    log(I) = a * log(ell1*ell2) + b")
print(f"{'-' * 70}")
print(f"  a (slope)     = {a_lin:.6f}")
print(f"  b (intercept) = {b_lin:.6f}")
print(f"  R^2           = {r2_lin:.6f}")
print(f"  SS_residual   = {ss_res_lin:.6f}")
print(f"  AIC           = {aic_lin:.4f}")
print(f"  Residuals:")
for i, lab in enumerate(labels):
    print(f"    {lab}: observed={y[i]:.4f}  predicted={y_pred_lin[i]:.4f}  residual={y[i]-y_pred_lin[i]:.4f}")

# ── Model 2: Quadratic ──────────────────────────────────────────────
# log(I) = a * log(ell1*ell2)^2 + b * log(ell1*ell2) + c
A_quad = np.column_stack([x**2, x, np.ones(n_pts)])
coeffs_quad, res_quad, rank_quad, sv_quad = np.linalg.lstsq(A_quad, y, rcond=None)
a_quad, b_quad, c_quad = coeffs_quad
y_pred_quad = A_quad @ coeffs_quad
ss_res_quad = np.sum((y - y_pred_quad) ** 2)
r2_quad = 1 - ss_res_quad / ss_tot if ss_tot > 0 else 0

# AIC for quadratic (k=3 params)
k_quad = 3
aic_quad = n_pts * np.log(ss_res_quad / n_pts) + 2 * k_quad if n_pts > 0 else float("inf")

print(f"\n{'-' * 70}")
print(f"MODEL 2: QUADRATIC    log(I) = a * log(ell1*ell2)^2 + b * log(ell1*ell2) + c")
print(f"{'-' * 70}")
print(f"  a (quadratic / nonlinearity coeff) = {a_quad:.6f}")
print(f"  b (linear)                         = {b_quad:.6f}")
print(f"  c (intercept)                      = {c_quad:.6f}")
print(f"  R^2           = {r2_quad:.6f}")
print(f"  SS_residual   = {ss_res_quad:.6f}")
print(f"  AIC           = {aic_quad:.4f}")
print(f"  Residuals:")
for i, lab in enumerate(labels):
    print(f"    {lab}: observed={y[i]:.4f}  predicted={y_pred_quad[i]:.4f}  residual={y[i]-y_pred_quad[i]:.4f}")

# ── Model comparison ──────────────────────────────────────────────────
delta_aic = aic_lin - aic_quad  # positive means quadratic is better
delta_r2 = r2_quad - r2_lin
f_stat_num = (ss_res_lin - ss_res_quad) / 1  # 1 extra param
f_stat_den = ss_res_quad / (n_pts - k_quad) if n_pts > k_quad else float("inf")
f_stat = f_stat_num / f_stat_den if f_stat_den > 0 else 0

# Bootstrap significance of the quadratic term
np.random.seed(42)
n_boot = 10000
a_quad_boots = []
for _ in range(n_boot):
    idx = np.random.choice(n_pts, n_pts, replace=True)
    xb, yb = x[idx], y[idx]
    Ab = np.column_stack([xb**2, xb, np.ones(len(xb))])
    try:
        cb, _, _, _ = np.linalg.lstsq(Ab, yb, rcond=None)
        a_quad_boots.append(cb[0])
    except:
        pass

a_quad_boots = np.array(a_quad_boots)
a_quad_mean = np.mean(a_quad_boots)
a_quad_std = np.std(a_quad_boots)
a_quad_ci_lo = np.percentile(a_quad_boots, 2.5)
a_quad_ci_hi = np.percentile(a_quad_boots, 97.5)
# Fraction of bootstraps with same sign as point estimate
frac_same_sign = np.mean(np.sign(a_quad_boots) == np.sign(a_quad)) if a_quad != 0 else 0.5

print(f"\n{'=' * 70}")
print(f"MODEL COMPARISON")
print(f"{'=' * 70}")
print(f"  Delta AIC (linear - quadratic) = {delta_aic:.4f}")
print(f"    (positive => quadratic preferred)")
print(f"  Delta R^2 = {delta_r2:.6f}")
print(f"  F-statistic = {f_stat:.4f}")
print(f"  Nonlinearity coefficient a = {a_quad:.6f}")
print(f"  Bootstrap 95% CI for a: [{a_quad_ci_lo:.6f}, {a_quad_ci_hi:.6f}]")
print(f"  Bootstrap mean(a) = {a_quad_mean:.6f}, std(a) = {a_quad_std:.6f}")
print(f"  Fraction of bootstraps with same sign: {frac_same_sign:.4f}")

# ── Constructive-only analysis (excluding 3x11) ─────────────────────
constructive_mask = np.array([d["ratio"] > 1.0 for d in pair_data])
constructive_and_valid = constructive_mask & valid
xc = x_all[constructive_and_valid]
yc = y_all[constructive_and_valid]
labels_c = [labels_all[i] for i in range(len(labels_all)) if constructive_and_valid[i]]
nc = len(xc)

print(f"\n{'=' * 70}")
print(f"CONSTRUCTIVE-ONLY ANALYSIS ({nc} pairs with ratio > 1)")
print(f"{'=' * 70}")

if nc >= 3:
    # Linear
    Ac_lin = np.column_stack([xc, np.ones(nc)])
    cc_lin, _, _, _ = np.linalg.lstsq(Ac_lin, yc, rcond=None)
    yc_pred_lin = Ac_lin @ cc_lin
    ssc_res_lin = np.sum((yc - yc_pred_lin) ** 2)
    ssc_tot = np.sum((yc - np.mean(yc)) ** 2)
    r2c_lin = 1 - ssc_res_lin / ssc_tot if ssc_tot > 0 else 0

    print(f"\n  Linear: log(I) = {cc_lin[0]:.6f} * log(prod) + {cc_lin[1]:.6f}")
    print(f"  R^2 = {r2c_lin:.6f}")

    # Quadratic
    Ac_quad = np.column_stack([xc**2, xc, np.ones(nc)])
    cc_quad, _, _, _ = np.linalg.lstsq(Ac_quad, yc, rcond=None)
    yc_pred_quad = Ac_quad @ cc_quad
    ssc_res_quad = np.sum((yc - yc_pred_quad) ** 2)
    r2c_quad = 1 - ssc_res_quad / ssc_tot if ssc_tot > 0 else 0

    print(f"  Quadratic: log(I) = {cc_quad[0]:.6f} * log(prod)^2 + {cc_quad[1]:.6f} * log(prod) + {cc_quad[2]:.6f}")
    print(f"  R^2 = {r2c_quad:.6f}")
    print(f"  Nonlinearity coefficient (constructive) = {cc_quad[0]:.6f}")

    for i, lab in enumerate(labels_c):
        print(f"    {lab}: obs={yc[i]:.4f} lin_pred={yc_pred_lin[i]:.4f} quad_pred={yc_pred_quad[i]:.4f}")
else:
    cc_lin = [np.nan, np.nan]
    cc_quad = [np.nan, np.nan, np.nan]
    r2c_lin = np.nan
    r2c_quad = np.nan
    ssc_res_lin = np.nan
    ssc_res_quad = np.nan
    print(f"  Too few constructive pairs ({nc}) for regression")

# ── Conductor-conditioned nonlinearity ───────────────────────────────
# Check if the nonlinearity persists within conductor bins
print(f"\n{'=' * 70}")
print(f"CONDUCTOR-CONDITIONED NONLINEARITY")
print(f"{'=' * 70}")

cond_data = ci_data.get("conductor_conditioned", {})
bin_results = {}

for bin_name in ["N<500", "500<=N<2000", "2000<=N<5000"]:
    bin_pairs = []
    for p1, p2 in pairs:
        key = f"{bin_name}_{p1}x{p2}"
        if key in cond_data:
            entry = cond_data[key]
            ratio = entry.get("ratio", None)
            if ratio is not None and ratio > 0:
                bin_pairs.append({
                    "ell_1": p1, "ell_2": p2,
                    "product": p1 * p2,
                    "ratio": ratio,
                    "N_12": entry.get("N_12", 0),
                })

    if len(bin_pairs) >= 3:
        xb = np.array([np.log(bp["product"]) for bp in bin_pairs])
        yb = np.array([np.log(bp["ratio"]) for bp in bin_pairs])
        nb = len(xb)

        # Linear fit
        Ab_lin = np.column_stack([xb, np.ones(nb)])
        cb_lin, _, _, _ = np.linalg.lstsq(Ab_lin, yb, rcond=None)
        yb_pred_lin = Ab_lin @ cb_lin
        ssb_res_lin = np.sum((yb - yb_pred_lin) ** 2)
        ssb_tot = np.sum((yb - np.mean(yb)) ** 2)
        r2b_lin = 1 - ssb_res_lin / ssb_tot if ssb_tot > 0 else 0

        # Quadratic fit (if enough points)
        if nb >= 4:
            Ab_quad = np.column_stack([xb**2, xb, np.ones(nb)])
            cb_quad, _, _, _ = np.linalg.lstsq(Ab_quad, yb, rcond=None)
            yb_pred_quad = Ab_quad @ cb_quad
            ssb_res_quad = np.sum((yb - yb_pred_quad) ** 2)
            r2b_quad = 1 - ssb_res_quad / ssb_tot if ssb_tot > 0 else 0
            nonlin_coeff = cb_quad[0]
        else:
            r2b_quad = np.nan
            nonlin_coeff = np.nan
            cb_quad = [np.nan, np.nan, np.nan]

        print(f"\n  Bin: {bin_name} ({nb} pairs with ratio > 0)")
        print(f"    Linear R^2 = {r2b_lin:.4f}, slope = {cb_lin[0]:.4f}")
        if not np.isnan(r2b_quad):
            print(f"    Quadratic R^2 = {r2b_quad:.4f}, nonlinearity = {nonlin_coeff:.6f}")
        for bp in bin_pairs:
            print(f"      {bp['ell_1']}x{bp['ell_2']}: ratio={bp['ratio']:.4f}, N_12={bp['N_12']}")

        bin_results[bin_name] = {
            "n_pairs": nb,
            "linear_slope": float(cb_lin[0]),
            "linear_intercept": float(cb_lin[1]),
            "linear_r2": float(r2b_lin),
            "quadratic_a": float(cb_quad[0]) if not np.isnan(cb_quad[0]) else None,
            "quadratic_b": float(cb_quad[1]) if not np.isnan(cb_quad[1]) else None,
            "quadratic_c": float(cb_quad[2]) if not np.isnan(cb_quad[2]) else None,
            "quadratic_r2": float(r2b_quad) if not np.isnan(r2b_quad) else None,
        }
    else:
        print(f"\n  Bin: {bin_name} -- too few valid pairs ({len(bin_pairs)})")
        bin_results[bin_name] = {"n_pairs": len(bin_pairs), "note": "insufficient data"}

# ── Augmented data analysis ──────────────────────────────────────────
# Include conductor-conditioned points as additional measurements
print(f"\n{'=' * 70}")
print(f"AUGMENTED ANALYSIS (global + conductor-conditioned points)")
print(f"{'=' * 70}")

aug_x = list(x)
aug_y = list(y)
aug_labels = list(labels)
aug_weights = []

# Weight: global points get weight proportional to N_12
for d in pair_data:
    if d["ratio"] > 0:
        aug_weights.append(max(d["N_12"], 1))

# Add conductor-conditioned data
for bin_name in ["N<500", "500<=N<2000", "2000<=N<5000"]:
    for p1, p2 in pairs:
        key = f"{bin_name}_{p1}x{p2}"
        if key in cond_data:
            entry = cond_data[key]
            ratio = entry.get("ratio", None)
            n12 = entry.get("N_12", 0)
            if ratio is not None and ratio > 0 and n12 >= 2:
                aug_x.append(np.log(p1 * p2))
                aug_y.append(np.log(ratio))
                aug_labels.append(f"{bin_name}_{p1}x{p2}")
                aug_weights.append(n12)

aug_x = np.array(aug_x)
aug_y = np.array(aug_y)
aug_w = np.array(aug_weights, dtype=float)
aug_w = aug_w / aug_w.sum()  # normalize
na = len(aug_x)

print(f"  Total data points: {na}")

# Weighted linear
W = np.diag(aug_w)
Aa_lin = np.column_stack([aug_x, np.ones(na)])
ca_lin = np.linalg.lstsq(np.sqrt(W) @ Aa_lin, np.sqrt(W) @ aug_y, rcond=None)[0]
ya_pred_lin = Aa_lin @ ca_lin
ssa_res_lin = np.sum(aug_w * (aug_y - ya_pred_lin) ** 2)
ssa_tot = np.sum(aug_w * (aug_y - np.average(aug_y, weights=aug_w)) ** 2)
r2a_lin = 1 - ssa_res_lin / ssa_tot if ssa_tot > 0 else 0

# Weighted quadratic
Aa_quad = np.column_stack([aug_x**2, aug_x, np.ones(na)])
ca_quad = np.linalg.lstsq(np.sqrt(W) @ Aa_quad, np.sqrt(W) @ aug_y, rcond=None)[0]
ya_pred_quad = Aa_quad @ ca_quad
ssa_res_quad = np.sum(aug_w * (aug_y - ya_pred_quad) ** 2)
r2a_quad = 1 - ssa_res_quad / ssa_tot if ssa_tot > 0 else 0

print(f"  Weighted linear:    R^2 = {r2a_lin:.6f}, slope = {ca_lin[0]:.6f}")
print(f"  Weighted quadratic: R^2 = {r2a_quad:.6f}, nonlinearity = {ca_quad[0]:.6f}")
print(f"  Delta R^2 (quad - lin) = {r2a_quad - r2a_lin:.6f}")

# ── Physical interpretation ──────────────────────────────────────────
# If a_quad > 0: super-linear (interference accelerates with product)
# If a_quad < 0: sub-linear (interference decelerates)
# If a_quad ~ 0: linear in log-space (purely multiplicative)

sign_str = "super-linear (accelerating)" if a_quad > 0 else "sub-linear (decelerating)" if a_quad < 0 else "linear"
sig_str = "significant" if frac_same_sign > 0.95 else "marginal" if frac_same_sign > 0.80 else "not significant"

print(f"\n{'=' * 70}")
print(f"VERDICT")
print(f"{'=' * 70}")
print(f"  Nonlinearity coefficient (global, all 6 pairs):  a = {a_quad:.6f}")
print(f"  Nonlinearity coefficient (constructive, 5 pairs): a = {cc_quad[0]:.6f}" if not np.isnan(cc_quad[0]) else "  Constructive: N/A")
print(f"  Nonlinearity coefficient (augmented, weighted):   a = {ca_quad[0]:.6f}")
print(f"  Direction: {sign_str}")
print(f"  Significance (bootstrap): {sig_str} ({frac_same_sign:.1%} same sign)")
print(f"  CI: [{a_quad_ci_lo:.6f}, {a_quad_ci_hi:.6f}]")

# Key diagnostic: does 7x11 (the outlier) drive the nonlinearity?
# Refit without 7x11
mask_no711 = np.array([not (d["ell_1"] == 7 and d["ell_2"] == 11) for d in pair_data])
mask_no711_valid = mask_no711 & valid
x_no711 = x_all[mask_no711_valid]
y_no711 = y_all[mask_no711_valid]
n_no711 = len(x_no711)

if n_no711 >= 3:
    A_no711 = np.column_stack([x_no711**2, x_no711, np.ones(n_no711)])
    c_no711, _, _, _ = np.linalg.lstsq(A_no711, y_no711, rcond=None)
    print(f"\n  Without 7x11: nonlinearity = {c_no711[0]:.6f} (from {n_no711} pts)")
    print(f"  (Tests whether 7x11 N_12=3 outlier drives the result)")
else:
    c_no711 = [np.nan, np.nan, np.nan]
    print(f"\n  Without 7x11: too few points ({n_no711})")

# ── Cross-check: log(I) vs individual log(ell) contributions ────────
# Decompose: is the nonlinearity from ell_1, ell_2, or the interaction?
print(f"\n{'=' * 70}")
print(f"SEPARABILITY CHECK: log(I) = alpha*log(ell1) + beta*log(ell2) + gamma*log(ell1)*log(ell2) + const")
print(f"{'=' * 70}")

log_e1 = np.array([np.log(d["ell_1"]) for d in pair_data])[valid]
log_e2 = np.array([np.log(d["ell_2"]) for d in pair_data])[valid]
interaction = log_e1 * log_e2

A_sep = np.column_stack([log_e1, log_e2, interaction, np.ones(n_pts)])
c_sep, _, _, _ = np.linalg.lstsq(A_sep, y, rcond=None)
y_pred_sep = A_sep @ c_sep
ss_res_sep = np.sum((y - y_pred_sep) ** 2)
r2_sep = 1 - ss_res_sep / ss_tot if ss_tot > 0 else 0

print(f"  alpha (log ell_1)         = {c_sep[0]:.6f}")
print(f"  beta  (log ell_2)         = {c_sep[1]:.6f}")
print(f"  gamma (log(ell1)*log(ell2)) = {c_sep[2]:.6f}  <-- interaction term")
print(f"  const                     = {c_sep[3]:.6f}")
print(f"  R^2                       = {r2_sep:.6f}")

# Without interaction term
A_sep_no = np.column_stack([log_e1, log_e2, np.ones(n_pts)])
c_sep_no, _, _, _ = np.linalg.lstsq(A_sep_no, y, rcond=None)
y_pred_sep_no = A_sep_no @ c_sep_no
ss_res_sep_no = np.sum((y - y_pred_sep_no) ** 2)
r2_sep_no = 1 - ss_res_sep_no / ss_tot if ss_tot > 0 else 0

print(f"\n  Without interaction term: R^2 = {r2_sep_no:.6f}")
print(f"  R^2 improvement from interaction: {r2_sep - r2_sep_no:.6f}")

# ── Save results ─────────────────────────────────────────────────────
results = {
    "metadata": {
        "problem": "F24: Prime Interaction Nonlinearity Coefficient",
        "primes": primes,
        "n_pairs_total": len(pairs),
        "n_pairs_valid": int(n_pts),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    "raw_data": [
        {
            "pair": f"{d['ell_1']}x{d['ell_2']}",
            "ell_1": d["ell_1"],
            "ell_2": d["ell_2"],
            "product": d["product"],
            "log_product": float(np.log(d["product"])),
            "ratio": d["ratio"],
            "log_ratio": float(np.log(d["ratio"])) if d["ratio"] > 0 else None,
            "N_12": d["N_12"],
            "interference": "constructive" if d["ratio"] > 1 else "destructive" if d["ratio"] < 1 else "independent",
        }
        for d in pair_data
    ],
    "linear_model": {
        "formula": "log(I) = a * log(ell1*ell2) + b",
        "a_slope": float(a_lin),
        "b_intercept": float(b_lin),
        "r_squared": float(r2_lin),
        "ss_residual": float(ss_res_lin),
        "aic": float(aic_lin),
    },
    "quadratic_model": {
        "formula": "log(I) = a * log(ell1*ell2)^2 + b * log(ell1*ell2) + c",
        "a_nonlinearity": float(a_quad),
        "b_linear": float(b_quad),
        "c_intercept": float(c_quad),
        "r_squared": float(r2_quad),
        "ss_residual": float(ss_res_quad),
        "aic": float(aic_quad),
    },
    "comparison": {
        "delta_aic_lin_minus_quad": float(delta_aic),
        "delta_r2_quad_minus_lin": float(delta_r2),
        "f_statistic": float(f_stat),
        "quadratic_preferred": bool(delta_aic > 2),
        "bootstrap": {
            "n_bootstrap": n_boot,
            "a_mean": float(a_quad_mean),
            "a_std": float(a_quad_std),
            "a_ci_95": [float(a_quad_ci_lo), float(a_quad_ci_hi)],
            "frac_same_sign": float(frac_same_sign),
            "significant_at_95pct": bool(frac_same_sign > 0.975),
        },
    },
    "constructive_only": {
        "n_pairs": int(nc),
        "linear_slope": float(cc_lin[0]) if not np.isnan(cc_lin[0]) else None,
        "linear_r2": float(r2c_lin) if not np.isnan(r2c_lin) else None,
        "quadratic_nonlinearity": float(cc_quad[0]) if not np.isnan(cc_quad[0]) else None,
        "quadratic_r2": float(r2c_quad) if not np.isnan(r2c_quad) else None,
    },
    "augmented_weighted": {
        "n_points": int(na),
        "linear_slope": float(ca_lin[0]),
        "linear_r2": float(r2a_lin),
        "quadratic_nonlinearity": float(ca_quad[0]),
        "quadratic_r2": float(r2a_quad),
        "delta_r2": float(r2a_quad - r2a_lin),
    },
    "robustness": {
        "without_7x11": {
            "nonlinearity": float(c_no711[0]) if not np.isnan(c_no711[0]) else None,
            "n_points": int(n_no711),
            "note": "Tests if 7x11 (N_12=3, ratio=15.84) drives the nonlinearity",
        },
        "conductor_bins": bin_results,
    },
    "separability_test": {
        "formula": "log(I) = alpha*log(ell1) + beta*log(ell2) + gamma*log(ell1)*log(ell2) + const",
        "alpha": float(c_sep[0]),
        "beta": float(c_sep[1]),
        "gamma_interaction": float(c_sep[2]),
        "const": float(c_sep[3]),
        "r2_with_interaction": float(r2_sep),
        "r2_without_interaction": float(r2_sep_no),
        "r2_improvement": float(r2_sep - r2_sep_no),
    },
    "verdict": {
        "nonlinearity_coefficient": float(a_quad),
        "direction": sign_str,
        "significance": sig_str,
        "bootstrap_ci_95": [float(a_quad_ci_lo), float(a_quad_ci_hi)],
        "interaction_gamma": float(c_sep[2]),
        "interpretation": None,  # filled below
    },
}

# Build interpretation
interp_parts = []
if abs(a_quad) < 0.01:
    interp_parts.append("The nonlinearity coefficient is near zero -- prime interactions are approximately linear in log(product) space, consistent with multiplicative coupling.")
elif frac_same_sign < 0.80:
    interp_parts.append(f"The nonlinearity coefficient ({a_quad:.4f}) is unstable under bootstrap (only {frac_same_sign:.0%} same sign). Cannot distinguish linear from quadratic with {n_pts} points.")
else:
    interp_parts.append(f"The nonlinearity coefficient is {a_quad:.4f} ({sign_str}), with {frac_same_sign:.0%} bootstrap consistency.")

if abs(c_sep[2]) > 0.1 and r2_sep - r2_sep_no > 0.01:
    interp_parts.append(f"The interaction term gamma={c_sep[2]:.4f} adds R^2={r2_sep - r2_sep_no:.4f}, suggesting primes have genuine higher-order coupling beyond separable contributions.")
else:
    interp_parts.append(f"The interaction term gamma={c_sep[2]:.4f} adds negligible R^2={r2_sep - r2_sep_no:.4f}. Separable model (each prime contributes independently) is adequate.")

if c_no711 is not None and not np.isnan(c_no711[0]):
    if np.sign(c_no711[0]) != np.sign(a_quad):
        interp_parts.append(f"CAUTION: Removing 7x11 flips the nonlinearity sign ({c_no711[0]:.4f}). The result is driven by the 7x11 outlier (N_12=3 forms).")
    elif abs(c_no711[0]) < abs(a_quad) * 0.5:
        interp_parts.append(f"Removing 7x11 halves the coefficient ({c_no711[0]:.4f}). The 7x11 pair (N_12=3) substantially amplifies the apparent nonlinearity.")
    else:
        interp_parts.append(f"Removing 7x11 gives nonlinearity={c_no711[0]:.4f}, consistent with the full dataset. Result not driven by a single outlier.")

results["verdict"]["interpretation"] = " ".join(interp_parts)

# Honest limitations
results["honest_assessment"] = {
    "data_limitations": [
        f"Only {n_pts} data points (pairs from primes 3,5,7,11) -- fitting 2-3 parameter models to 5-6 points",
        "3x11 pair is destructive (ratio=0.68, N_12=4, p=0.93) -- statistically noise",
        "5x11 and 7x11 each have N_12=3 -- extreme ratios from tiny counts",
        "7x11 ratio 15.84x is 3-4x above model predictions -- outlier or genuine super-linear effect",
        "Primes >= 13 have zero non-trivial clusters in 17K forms -- no extrapolation possible",
    ],
    "what_is_solid": [
        "log(I) increases with log(product) for constructive pairs -- monotonic trend is real",
        "Linear model captures most variance (R^2 reported above)",
        "The question of linear vs quadratic is genuinely underdetermined with 5-6 points",
    ],
    "bottom_line": "With only 5-6 data points spanning a narrow range of log(product), we cannot robustly distinguish linear from quadratic. The nonlinearity coefficient is measured but its significance depends heavily on the 7x11 pair (3 forms). More data (larger prime sets, more modular forms) needed to resolve.",
}

print(f"\n  Interpretation: {results['verdict']['interpretation']}")
print(f"\n  Bottom line: {results['honest_assessment']['bottom_line']}")

# ── Save ─────────────────────────────────────────────────────────────
out_path = DATA_DIR / "prime_nonlinearity_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path}")
