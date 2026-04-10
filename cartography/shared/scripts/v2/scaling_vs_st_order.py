#!/usr/bin/env python3
"""
R4-4: Is the Scaling Law Exponent a Rational Function of Sato-Tate Group Order?

Tests whether CL1 scaling-law slopes correlate with Sato-Tate group invariants
(component group order, identity component dimension, etc.).

Uses the Fité-Kedlaya-Rotger-Sutherland classification of genus-2 ST groups.
"""

import json
import sys
import os
import numpy as np
from scipy import stats
from pathlib import Path
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

HERE = Path(__file__).parent

# ─── FKRS Sato-Tate group data for genus 2 ─────────────────────────────────
# Reference: Fité, Kedlaya, Rotger, Sutherland (2012)
# "Sato-Tate distributions and Galois images"
#
# For each ST group:
#   label      : LMFDB st_label prefix
#   pi0_order  : |π₀(ST)| = number of connected components
#   dim        : dimension of identity component ST_0 as Lie group
#   identity   : name of identity component
#   endo_type  : endomorphism algebra type (Q, RM, CM, QM)
#   rank       : rank of endomorphism algebra
#
# USp(4) is the generic group (identity component = full USp(4), dim=10)
# Subgroups have smaller identity components.

ST_GROUP_DATA = {
    "USp(4)": {
        "pi0_order": 1,
        "dim_ST0": 10,   # USp(4) has dimension 10
        "identity": "USp(4)",
        "endo_type": "Q",
        "endo_rank": 1,
        "weight": 1,      # weight parameter for models
    },
    "G_{3,3}": {
        "pi0_order": 3,
        "dim_ST0": 4,    # SU(2) x SU(2), dim=3+3=6? No: G_{3,3} identity component is U(1)xU(1), dim=2
        # Actually: G_{3,3} has identity component SU(2)×SU(2) ≅ USp(2)×USp(2), dim=6
        # But the FKRS paper: G_{3,3} ⊂ USp(4), ST_0 = SU(2)×SU(2), |π₀|=3
        # SU(2)×SU(2) has dimension 3+3=6
        "dim_ST0": 6,
        "identity": "SU(2)xSU(2)",
        "endo_type": "RM",
        "endo_rank": 2,
        "weight": 3,
    },
    "N(G_{1,3})": {
        "pi0_order": 6,
        "dim_ST0": 6,    # SU(2)×SU(2)
        "identity": "SU(2)xSU(2)",
        "endo_type": "RM",
        "endo_rank": 2,
        "weight": 6,
    },
    "N(G_{3,3})": {
        "pi0_order": 6,
        "dim_ST0": 6,    # SU(2)×SU(2)
        "identity": "SU(2)xSU(2)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 6,
    },
    "E_6": {
        "pi0_order": 6,
        "dim_ST0": 2,    # U(1)×U(1), dim=2
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 6,
    },
    "J(E_1)": {
        "pi0_order": 2,
        "dim_ST0": 4,    # SU(2)×U(1), dim=3+1=4
        "identity": "SU(2)xU(1)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 2,
    },
    # Additional groups from FKRS for completeness (not in CL1 slopes)
    "J(E_6)": {
        "pi0_order": 12,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 12,
    },
    "J(E_4)": {
        "pi0_order": 8,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 8,
    },
    "E_4": {
        "pi0_order": 4,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 4,
    },
    "E_1": {
        "pi0_order": 1,
        "dim_ST0": 4,
        "identity": "SU(2)xU(1)",
        "endo_type": "RM",
        "endo_rank": 2,
        "weight": 1,
    },
    "E_3": {
        "pi0_order": 3,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 3,
    },
    "J(E_2)": {
        "pi0_order": 4,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 4,
    },
    "F_{ac}": {
        "pi0_order": 2,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 2,
    },
    "J(E_3)": {
        "pi0_order": 6,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 6,
    },
    "E_2": {
        "pi0_order": 2,
        "dim_ST0": 2,
        "identity": "U(1)xU(1)",
        "endo_type": "CM",
        "endo_rank": 2,
        "weight": 2,
    },
    "D_{2,1}": {
        "pi0_order": 4,
        "dim_ST0": 4,
        "identity": "SU(2)xU(1)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 4,
    },
    "J(C_2)": {
        "pi0_order": 4,
        "dim_ST0": 4,
        "identity": "SU(2)xU(1)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 4,
    },
    "D_{6,2}": {
        "pi0_order": 12,
        "dim_ST0": 4,
        "identity": "SU(2)xU(1)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 12,
    },
    "D_{3,2}": {
        "pi0_order": 6,
        "dim_ST0": 4,
        "identity": "SU(2)xU(1)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 6,
    },
    "J(C_4)": {
        "pi0_order": 8,
        "dim_ST0": 4,
        "identity": "SU(2)xU(1)",
        "endo_type": "QM",
        "endo_rank": 4,
        "weight": 8,
    },
}


def load_cl1_data():
    """Load CL1 scaling law results."""
    with open(HERE / "scaling_law_reverse_results.json") as f:
        data = json.load(f)
    return data


def load_st_moments():
    """Load Sato-Tate moments results."""
    with open(HERE / "sato_tate_moments_results.json") as f:
        data = json.load(f)
    return data


def bootstrap_slope(enrichment_curve, n_boot=2000, seed=42):
    """
    Bootstrap confidence interval for log-log slope of enrichment vs prime.
    enrichment_curve: dict {str(prime): enrichment_value}
    """
    primes = sorted(int(p) for p in enrichment_curve.keys())
    log_p = np.log(primes)
    log_e = np.log([enrichment_curve[str(p)] for p in primes])

    # Original slope
    slope_orig, intercept_orig, _, _, _ = stats.linregress(log_p, log_e)

    # Bootstrap
    rng = np.random.RandomState(seed)
    n = len(primes)
    slopes = []
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        if len(set(idx)) < 2:
            continue  # skip degenerate samples
        try:
            s, _, _, _, _ = stats.linregress(log_p[idx], log_e[idx])
            slopes.append(s)
        except ValueError:
            continue

    slopes = np.array(slopes)
    ci_lo, ci_hi = np.percentile(slopes, [2.5, 97.5])
    return slope_orig, ci_lo, ci_hi, np.std(slopes)


def fit_model(x, y, model_name, weights=None):
    """Fit a linear model y = a*x + b and return R², slope, intercept."""
    if len(x) < 3:
        return {"R2": np.nan, "a": np.nan, "b": np.nan, "model": model_name, "n": len(x)}

    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    # Remove NaN/inf
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 3:
        return {"R2": np.nan, "a": np.nan, "b": np.nan, "model": model_name, "n": len(x)}

    if weights is not None:
        weights = np.array(weights, dtype=float)[mask]

    # Weighted least squares if weights provided
    if weights is not None and len(weights) == len(x):
        W = np.diag(weights)
        X = np.column_stack([x, np.ones_like(x)])
        try:
            beta = np.linalg.lstsq(W @ X, W @ y, rcond=None)[0]
            a, b = beta
            y_pred = X @ beta
            ss_res = np.sum(weights * (y - y_pred)**2)
            ss_tot = np.sum(weights * (y - np.average(y, weights=weights))**2)
            R2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
        except Exception:
            return {"R2": np.nan, "a": np.nan, "b": np.nan, "model": model_name, "n": len(x)}
    else:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        a, b, R2 = slope, intercept, r_value**2

    return {"R2": float(R2), "a": float(a), "b": float(b), "model": model_name, "n": int(len(x)),
            "p_value": float(p_value) if weights is None else None}


def compute_slopes_with_bootstrap(cl1_data):
    """Extract slopes with bootstrap CIs for each ST group."""
    results = {}
    st_slopes = cl1_data["slope_summary"]["sato_tate"]

    for group, info in st_slopes.items():
        ec = info["enrichment_curve"]
        slope, ci_lo, ci_hi, std = bootstrap_slope(ec)
        results[group] = {
            "slope": slope,
            "ci_lo": ci_lo,
            "ci_hi": ci_hi,
            "bootstrap_std": std,
            "n_curves": info["n_curves"],
            "enrichment_curve": ec,
        }

    # Also do endomorphism types
    endo_slopes = cl1_data["slope_summary"]["endomorphism"]
    endo_results = {}
    for etype, info in endo_slopes.items():
        ec = info["enrichment_curve"]
        slope, ci_lo, ci_hi, std = bootstrap_slope(ec)
        endo_results[etype] = {
            "slope": slope,
            "ci_lo": ci_lo,
            "ci_hi": ci_hi,
            "bootstrap_std": std,
            "n_curves": info["n_curves"],
        }

    return results, endo_results


def try_all_models(st_slopes):
    """
    Fit slope = f(group_parameter) for various group parameters.
    """
    # Collect data points: only groups where we have both slope and group data
    groups_with_data = []
    for g in st_slopes:
        if g in ST_GROUP_DATA:
            groups_with_data.append(g)

    if len(groups_with_data) < 3:
        return {}

    slopes = [st_slopes[g]["slope"] for g in groups_with_data]
    n_curves = [st_slopes[g]["n_curves"] for g in groups_with_data]
    # Weight by sqrt(n_curves) -- more data = more reliable slope
    weights = [np.sqrt(n) for n in n_curves]

    # Extract group parameters
    pi0_orders = [ST_GROUP_DATA[g]["pi0_order"] for g in groups_with_data]
    dim_ST0 = [ST_GROUP_DATA[g]["dim_ST0"] for g in groups_with_data]
    endo_ranks = [ST_GROUP_DATA[g]["endo_rank"] for g in groups_with_data]

    models = {}

    # Model 1: slope = a / |π₀(ST)| + b
    x1 = [1.0 / p for p in pi0_orders]
    models["slope_vs_1/pi0"] = fit_model(x1, slopes, "slope = a/|π₀| + b")
    models["slope_vs_1/pi0_weighted"] = fit_model(x1, slopes, "slope = a/|π₀| + b (weighted)", weights)

    # Model 2: slope = a / dim(ST_0) + b
    x2 = [1.0 / d for d in dim_ST0]
    models["slope_vs_1/dim"] = fit_model(x2, slopes, "slope = a/dim(ST₀) + b")
    models["slope_vs_1/dim_weighted"] = fit_model(x2, slopes, "slope = a/dim(ST₀) + b (weighted)", weights)

    # Model 3: slope = a * log(dim(ST_0)) + b
    x3 = [np.log(d) for d in dim_ST0]
    models["slope_vs_log_dim"] = fit_model(x3, slopes, "slope = a*log(dim(ST₀)) + b")

    # Model 4: slope = a * |π₀(ST)| + b
    x4 = [float(p) for p in pi0_orders]
    models["slope_vs_pi0"] = fit_model(x4, slopes, "slope = a*|π₀| + b")
    models["slope_vs_pi0_weighted"] = fit_model(x4, slopes, "slope = a*|π₀| + b (weighted)", weights)

    # Model 5: slope = a * log(|π₀|) + b
    x5 = [np.log(p) if p > 0 else 0 for p in pi0_orders]
    models["slope_vs_log_pi0"] = fit_model(x5, slopes, "slope = a*log(|π₀|) + b")

    # Model 6: slope = a * endo_rank + b
    x6 = [float(r) for r in endo_ranks]
    models["slope_vs_endo_rank"] = fit_model(x6, slopes, "slope = a*endo_rank + b")
    models["slope_vs_endo_rank_weighted"] = fit_model(x6, slopes, "slope = a*endo_rank + b (weighted)", weights)

    # Model 7: slope = a * (endo_rank / dim_ST0) + b  (ratio model)
    x7 = [float(r) / float(d) for r, d in zip(endo_ranks, dim_ST0)]
    models["slope_vs_rank/dim"] = fit_model(x7, slopes, "slope = a*(endo_rank/dim) + b")

    # Model 8: slope = a * |π₀| * endo_rank + b (product model)
    x8 = [float(p) * float(r) for p, r in zip(pi0_orders, endo_ranks)]
    models["slope_vs_pi0*rank"] = fit_model(x8, slopes, "slope = a*|π₀|*endo_rank + b")

    # Model 9: slope = a / (dim_ST0 / endo_rank) + b
    x9 = [float(r) / float(d) for r, d in zip(endo_ranks, dim_ST0)]
    models["slope_vs_rank/dim_v2"] = fit_model(x9, slopes, "slope = a*(rank/dim) + b")

    # Model 10: slope = a * (pi0 - 1) / dim + b   (excess components per dimension)
    x10 = [(float(p) - 1) / float(d) for p, d in zip(pi0_orders, dim_ST0)]
    models["slope_vs_(pi0-1)/dim"] = fit_model(x10, slopes, "slope = a*(|π₀|-1)/dim + b")

    # Model 11: quadratic in endo_rank
    # slope = a * rank^2 + b
    x11 = [float(r)**2 for r in endo_ranks]
    models["slope_vs_rank2"] = fit_model(x11, slopes, "slope = a*rank² + b")

    # Record data table
    data_table = []
    for g in groups_with_data:
        data_table.append({
            "group": g,
            "slope": st_slopes[g]["slope"],
            "ci_lo": st_slopes[g]["ci_lo"],
            "ci_hi": st_slopes[g]["ci_hi"],
            "n_curves": st_slopes[g]["n_curves"],
            "pi0_order": ST_GROUP_DATA[g]["pi0_order"],
            "dim_ST0": ST_GROUP_DATA[g]["dim_ST0"],
            "endo_type": ST_GROUP_DATA[g]["endo_type"],
            "endo_rank": ST_GROUP_DATA[g]["endo_rank"],
            "identity": ST_GROUP_DATA[g]["identity"],
        })

    return models, data_table, groups_with_data


def predict_unmeasured_groups(best_model_name, best_model, st_slopes):
    """Predict slopes for ST groups not in the CL1 measurement set."""
    measured = set(st_slopes.keys())
    predictions = {}

    a = best_model["a"]
    b = best_model["b"]

    for g, gdata in ST_GROUP_DATA.items():
        if g in measured:
            continue

        # Determine x based on which model won
        x = _compute_x(best_model_name, gdata)
        if x is None:
            continue

        predicted_slope = a * x + b
        predictions[g] = {
            "predicted_slope": float(predicted_slope),
            "pi0_order": gdata["pi0_order"],
            "dim_ST0": gdata["dim_ST0"],
            "endo_type": gdata["endo_type"],
            "endo_rank": gdata["endo_rank"],
        }

    return predictions


def _compute_x(model_name, gdata):
    """Compute the x-value for a given model and group data."""
    if "rank2" in model_name or "rank^2" in model_name:
        return float(gdata["endo_rank"])**2
    elif "rank/dim" in model_name:
        return float(gdata["endo_rank"]) / float(gdata["dim_ST0"])
    elif "pi0*rank" in model_name:
        return float(gdata["pi0_order"]) * float(gdata["endo_rank"])
    elif "endo_rank" in model_name:
        return float(gdata["endo_rank"])
    elif "1/pi0" in model_name:
        return 1.0 / float(gdata["pi0_order"])
    elif "log_pi0" in model_name:
        return np.log(float(gdata["pi0_order"]))
    elif "pi0" in model_name:
        return float(gdata["pi0_order"])
    elif "1/dim" in model_name:
        return 1.0 / float(gdata["dim_ST0"])
    elif "log_dim" in model_name:
        return np.log(float(gdata["dim_ST0"]))
    return None


def measure_slopes_from_moments(st_moments_data):
    """
    Use the Sato-Tate moment centroids to compute an independent slope
    measurement for groups with enough curves, using the b-moment scaling.
    """
    dist = st_moments_data.get("st_group_distribution", {})
    b_centroids = st_moments_data.get("centroids_b_moments", {})

    moment_slopes = {}
    for group, n_curves in dist.items():
        if n_curves < 3:
            continue
        if group not in b_centroids:
            continue

        # b-moments are M1, M2, M3, M4, M5, M6
        moments = b_centroids[group]
        if len(moments) < 4:
            continue

        # Log-log slope of M_k vs k
        ks = np.arange(1, len(moments) + 1)
        log_k = np.log(ks)
        log_m = np.log(np.array(moments))

        # Only use finite values
        mask = np.isfinite(log_m)
        if mask.sum() < 3:
            continue

        slope, intercept, r, p, se = stats.linregress(log_k[mask], log_m[mask])
        moment_slopes[group] = {
            "moment_growth_slope": float(slope),
            "r_squared": float(r**2),
            "n_curves": int(n_curves),
        }

    return moment_slopes


def endomorphism_analysis(cl1_data):
    """Analyze slopes by endomorphism type with bootstrap CIs."""
    endo = cl1_data["slope_summary"]["endomorphism"]
    endo_params = {
        "Q":  {"endo_dim": 1, "endo_rank": 1, "n_simple_factors": 1},
        "RM": {"endo_dim": 2, "endo_rank": 2, "n_simple_factors": 1},
        "CM": {"endo_dim": 4, "endo_rank": 2, "n_simple_factors": 1},
        "QM": {"endo_dim": 8, "endo_rank": 4, "n_simple_factors": 1},
    }

    results = {}
    for etype, info in endo.items():
        ec = info["enrichment_curve"]
        slope, ci_lo, ci_hi, std = bootstrap_slope(ec)
        results[etype] = {
            "slope": slope,
            "ci_lo": ci_lo,
            "ci_hi": ci_hi,
            "n_curves": info["n_curves"],
            **endo_params.get(etype, {}),
        }

    # Fit models on endomorphism data
    etypes = list(results.keys())
    slopes = [results[e]["slope"] for e in etypes]
    endo_dims = [endo_params[e]["endo_dim"] for e in etypes]
    endo_ranks = [endo_params[e]["endo_rank"] for e in etypes]
    log_dims = [np.log(d) for d in endo_dims]

    endo_models = {}
    endo_models["slope_vs_endo_dim"] = fit_model(endo_dims, slopes, "slope = a*endo_dim + b")
    endo_models["slope_vs_log_endo_dim"] = fit_model(log_dims, slopes, "slope = a*log(endo_dim) + b")
    endo_models["slope_vs_endo_rank"] = fit_model(endo_ranks, slopes, "slope = a*endo_rank + b")
    endo_models["slope_vs_1/endo_dim"] = fit_model([1/d for d in endo_dims], slopes, "slope = a/endo_dim + b")

    return results, endo_models


def main():
    print("=" * 72)
    print("R4-4: Scaling Law Exponent vs Sato-Tate Group Order")
    print("=" * 72)

    cl1_data = load_cl1_data()
    st_moments = load_st_moments()

    # ── Step 1: Compute slopes with bootstrap CIs ───────────────────────
    print("\n[1] Computing bootstrap confidence intervals for slopes...")
    st_slopes, endo_slopes = compute_slopes_with_bootstrap(cl1_data)

    print("\n  ST Group Slopes (with 95% CI):")
    print(f"  {'Group':<15} {'Slope':>8} {'CI_lo':>8} {'CI_hi':>8} {'n_curves':>8}")
    print("  " + "-" * 55)
    for g in sorted(st_slopes.keys(), key=lambda x: st_slopes[x]["slope"]):
        s = st_slopes[g]
        print(f"  {g:<15} {s['slope']:>8.4f} {s['ci_lo']:>8.4f} {s['ci_hi']:>8.4f} {s['n_curves']:>8d}")

    print("\n  Endomorphism Type Slopes (with 95% CI):")
    print(f"  {'Type':<10} {'Slope':>8} {'CI_lo':>8} {'CI_hi':>8} {'n_curves':>8}")
    print("  " + "-" * 50)
    for e in sorted(endo_slopes.keys(), key=lambda x: endo_slopes[x]["slope"]):
        s = endo_slopes[e]
        print(f"  {e:<10} {s['slope']:>8.4f} {s['ci_lo']:>8.4f} {s['ci_hi']:>8.4f} {s['n_curves']:>8d}")

    # ── Step 2: Display group parameters ────────────────────────────────
    print("\n[2] Sato-Tate group parameters (FKRS classification):")
    print(f"  {'Group':<15} {'|π₀|':>6} {'dim(ST₀)':>9} {'EndoType':>9} {'EndoRank':>9} {'ST₀':>15}")
    print("  " + "-" * 70)
    for g in sorted(st_slopes.keys(), key=lambda x: ST_GROUP_DATA.get(x, {}).get("pi0_order", 99)):
        gd = ST_GROUP_DATA.get(g, {})
        print(f"  {g:<15} {gd.get('pi0_order','?'):>6} {gd.get('dim_ST0','?'):>9} "
              f"{gd.get('endo_type','?'):>9} {gd.get('endo_rank','?'):>9} {gd.get('identity','?'):>15}")

    # ── Step 3: Fit models ──────────────────────────────────────────────
    print("\n[3] Fitting models: slope = f(group parameter)...")
    models, data_table, groups_used = try_all_models(st_slopes)

    print(f"\n  Models fitted on {len(groups_used)} ST groups:")
    print(f"  {'Model':<40} {'R²':>8} {'a':>10} {'b':>10}")
    print("  " + "-" * 70)
    sorted_models = sorted(models.items(), key=lambda x: -x[1].get("R2", -1) if np.isfinite(x[1].get("R2", -1)) else -999)
    for name, m in sorted_models:
        r2 = m.get("R2", np.nan)
        a = m.get("a", np.nan)
        b = m.get("b", np.nan)
        pval = m.get("p_value")
        extra = f"  p={pval:.4f}" if pval is not None and np.isfinite(pval) else ""
        print(f"  {m['model']:<40} {r2:>8.4f} {a:>10.4f} {b:>10.4f}{extra}")

    # ── Step 4: Endomorphism analysis ───────────────────────────────────
    print("\n[4] Endomorphism algebra analysis:")
    endo_results, endo_models = endomorphism_analysis(cl1_data)

    print(f"\n  {'Model':<40} {'R²':>8} {'a':>10} {'b':>10}")
    print("  " + "-" * 70)
    for name, m in sorted(endo_models.items(), key=lambda x: -x[1].get("R2", -1)):
        print(f"  {m['model']:<40} {m['R2']:>8.4f} {m['a']:>10.4f} {m['b']:>10.4f}")

    # ── Step 5: Best model & predictions ────────────────────────────────
    best_name, best_model = sorted_models[0]
    print(f"\n[5] Best model: {best_model['model']}")
    print(f"    R² = {best_model['R2']:.4f}")
    print(f"    slope = {best_model['a']:.6f} * x + {best_model['b']:.6f}")

    predictions = predict_unmeasured_groups(best_name, best_model, st_slopes)
    if predictions:
        print(f"\n  Predictions for unmeasured groups:")
        print(f"  {'Group':<15} {'Predicted':>10} {'|π₀|':>6} {'dim(ST₀)':>9} {'EndoType':>9}")
        print("  " + "-" * 55)
        for g in sorted(predictions.keys(), key=lambda x: predictions[x]["predicted_slope"], reverse=True):
            p = predictions[g]
            print(f"  {g:<15} {p['predicted_slope']:>10.4f} {p['pi0_order']:>6} {p['dim_ST0']:>9} {p['endo_type']:>9}")

    # ── Step 6: Moment-based independent check ──────────────────────────
    print("\n[6] Independent check: moment growth slopes from DS2:")
    moment_slopes = measure_slopes_from_moments(st_moments)

    # Compare moment growth with enrichment slope where both exist
    print(f"\n  {'Group':<15} {'Enrich.Slope':>12} {'Moment.Slope':>12} {'n_curves':>8}")
    print("  " + "-" * 50)
    for g in sorted(st_slopes.keys()):
        es = st_slopes[g]["slope"]
        ms = moment_slopes.get(g, {}).get("moment_growth_slope", None)
        nc = moment_slopes.get(g, {}).get("n_curves", 0)
        ms_str = f"{ms:>12.4f}" if ms is not None else "      N/A   "
        print(f"  {g:<15} {es:>12.4f} {ms_str} {nc:>8}")

    # ── Step 7: Cross-validation with endomorphism grouping ─────────────
    print("\n[7] Cross-validation: do ST groups within same endo type cluster?")
    endo_groups = {}
    for g in st_slopes:
        if g in ST_GROUP_DATA:
            et = ST_GROUP_DATA[g]["endo_type"]
            endo_groups.setdefault(et, []).append(g)

    for et, gs in sorted(endo_groups.items()):
        slopes_in_group = [st_slopes[g]["slope"] for g in gs]
        if len(slopes_in_group) > 1:
            spread = max(slopes_in_group) - min(slopes_in_group)
            print(f"  {et}: groups={gs}, slopes={[round(s,4) for s in slopes_in_group]}, spread={spread:.4f}")
        else:
            print(f"  {et}: groups={gs}, slope={slopes_in_group[0]:.4f}")

    # ── Assemble results ────────────────────────────────────────────────
    results = {
        "challenge": "R4-4",
        "title": "Scaling Law Exponent vs Sato-Tate Group Order",
        "st_slopes_with_ci": {g: {
            "slope": v["slope"],
            "ci_lo": v["ci_lo"],
            "ci_hi": v["ci_hi"],
            "bootstrap_std": v["bootstrap_std"],
            "n_curves": v["n_curves"],
        } for g, v in st_slopes.items()},
        "endo_slopes_with_ci": {e: {
            "slope": v["slope"],
            "ci_lo": v["ci_lo"],
            "ci_hi": v["ci_hi"],
            "n_curves": v["n_curves"],
        } for e, v in endo_slopes.items()},
        "group_parameters": {g: {k: v for k, v in ST_GROUP_DATA[g].items()} for g in st_slopes if g in ST_GROUP_DATA},
        "models": {name: m for name, m in sorted_models},
        "endo_models": endo_models,
        "best_model": {
            "name": best_name,
            **best_model,
        },
        "predictions_unmeasured": predictions,
        "moment_growth_slopes": moment_slopes,
        "data_table": data_table,
    }

    # ── Verdict ─────────────────────────────────────────────────────────
    best_r2 = best_model["R2"]
    if best_r2 > 0.8:
        verdict_str = f"STRONG FIT: Best model R²={best_r2:.4f}. The scaling law exponent IS well-predicted by ST group parameters."
    elif best_r2 > 0.5:
        verdict_str = f"MODERATE FIT: Best model R²={best_r2:.4f}. Partial correlation exists but not a clean rational function."
    elif best_r2 > 0.2:
        verdict_str = f"WEAK FIT: Best model R²={best_r2:.4f}. Some structure but high noise / few data points."
    else:
        verdict_str = f"NO FIT: Best model R²={best_r2:.4f}. Scaling exponent does NOT appear to be a simple function of ST group order."

    # Check if slopes are even well-determined
    noisy_groups = [g for g in st_slopes if st_slopes[g]["n_curves"] < 20]
    if noisy_groups:
        verdict_str += f"\n  WARNING: {len(noisy_groups)} groups have <20 curves — slopes may be unreliable: {noisy_groups}"

    results["verdict"] = verdict_str
    print(f"\n{'='*72}")
    print(f"VERDICT: {verdict_str}")
    print(f"{'='*72}")

    # ── Save ────────────────────────────────────────────────────────────
    out_path = HERE / "scaling_vs_st_order_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
