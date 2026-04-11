"""
C10: Phase Transition in Knot Polynomial Coefficient Growth
============================================================
For ~13K knots, compute the growth rate of Jones polynomial coefficients
as a function of crossing number. Test whether there is a critical crossing
number where growth transitions from polynomial to exponential.

Also measures:
  - Coefficient entropy as a function of crossing number
  - Comparison to Alexander polynomial coefficient growth
"""

import json
import math
import os
from collections import defaultdict

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar

# ── paths ────────────────────────────────────────────────────────────────
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO, "knots", "data", "knots.json")
OUT_PATH = os.path.join(REPO, "v2", "knot_jones_growth_results.json")


def parse_crossing_number(name: str) -> int:
    """Extract crossing number from knot name like '11*a_1' -> 11."""
    prefix = name.split("_")[0]
    digits = ""
    for ch in prefix:
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else 0


def coeff_entropy(coeffs):
    """Shannon entropy of |coefficient| distribution (normalized)."""
    abs_c = np.array([abs(c) for c in coeffs], dtype=float)
    total = abs_c.sum()
    if total == 0:
        return 0.0
    p = abs_c / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def log_log_regression(x, y):
    """OLS on log(x) vs log(y)."""
    lx = np.log(x)
    ly = np.log(y)
    slope, intercept, r, p, se = stats.linregress(lx, ly)
    return {
        "alpha": float(slope),
        "intercept": float(intercept),
        "R2": float(r ** 2),
        "p_value": float(p),
        "std_err": float(se),
        "n": int(len(x)),
    }


def semilog_regression(x, y):
    """OLS on x vs log(y) — tests exponential growth."""
    ly = np.log(y)
    slope, intercept, r, p, se = stats.linregress(x, ly)
    return {
        "exp_rate": float(slope),
        "intercept": float(intercept),
        "R2": float(r ** 2),
        "p_value": float(p),
        "std_err": float(se),
        "n": int(len(x)),
    }


def find_breakpoint(cn_arr, val_arr):
    """
    Find optimal breakpoint in crossing number where growth regime changes.
    Uses piecewise linear fit on log-log data, minimizing total RSS.
    Returns breakpoint, left slope, right slope, improvement over single fit.
    """
    lx = np.log(cn_arr)
    ly = np.log(val_arr)
    n = len(lx)

    if n < 6:
        return None

    # Single fit RSS
    slope_all, intercept_all, r_all, _, _ = stats.linregress(lx, ly)
    rss_single = np.sum((ly - (slope_all * lx + intercept_all)) ** 2)

    best_rss = rss_single
    best_bp = None
    best_left = None
    best_right = None

    # Try each interior point as breakpoint
    for i in range(2, n - 2):
        # Left segment
        s1, i1, r1, _, _ = stats.linregress(lx[:i+1], ly[:i+1])
        rss1 = np.sum((ly[:i+1] - (s1 * lx[:i+1] + i1)) ** 2)
        # Right segment
        s2, i2, r2, _, _ = stats.linregress(lx[i:], ly[i:])
        rss2 = np.sum((ly[i:] - (s2 * lx[i:] + i2)) ** 2)
        rss_total = rss1 + rss2

        if rss_total < best_rss:
            best_rss = rss_total
            best_bp = float(cn_arr[i])
            best_left = float(s1)
            best_right = float(s2)

    if best_bp is None:
        return None

    # F-test for breakpoint significance
    # Piecewise model has 4 params (2 slopes + 2 intercepts), single has 2
    df1 = 2  # extra params
    df2 = n - 4  # residual df for piecewise
    if df2 <= 0:
        return None
    f_stat = ((rss_single - best_rss) / df1) / (best_rss / df2)
    p_value = 1 - stats.f.cdf(f_stat, df1, df2)

    # Also test if right segment is better fit by exponential
    bp_idx = list(cn_arr).index(best_bp)
    right_x = cn_arr[bp_idx:]
    right_y = val_arr[bp_idx:]
    if len(right_x) >= 3:
        semilog_fit = semilog_regression(right_x, right_y)
        loglog_fit = log_log_regression(right_x, right_y)
    else:
        semilog_fit = None
        loglog_fit = None

    return {
        "breakpoint_crossing_number": best_bp,
        "left_slope_loglog": best_left,
        "right_slope_loglog": best_right,
        "slope_ratio": best_right / best_left if best_left != 0 else None,
        "rss_single": float(rss_single),
        "rss_piecewise": float(best_rss),
        "rss_improvement_frac": float((rss_single - best_rss) / rss_single),
        "f_stat": float(f_stat),
        "p_value": float(p_value),
        "significant_at_0.05": bool(p_value < 0.05),
        "right_segment_semilog_R2": semilog_fit["R2"] if semilog_fit else None,
        "right_segment_loglog_R2": loglog_fit["R2"] if loglog_fit else None,
        "right_segment_exponential_rate": semilog_fit["exp_rate"] if semilog_fit else None,
    }


def main():
    with open(DATA_PATH) as f:
        raw = json.load(f)

    knots = raw["knots"]

    # ── collect Jones and Alexander data ────────────────────────────────
    jones_by_cn = defaultdict(list)   # cn -> list of max|coeff|
    alex_by_cn = defaultdict(list)
    jones_entropy_by_cn = defaultdict(list)
    alex_entropy_by_cn = defaultdict(list)
    jones_span_by_cn = defaultdict(list)   # span = max_power - min_power
    jones_l2_by_cn = defaultdict(list)     # L2 norm of coefficients

    n_jones = 0
    n_alex = 0

    for k in knots:
        cn = k["crossing_number"]
        if cn == 0:
            cn = parse_crossing_number(k["name"])
        if cn < 3:
            continue

        # Jones polynomial
        jones = k.get("jones")
        if jones and jones.get("coefficients"):
            coeffs = jones["coefficients"]
            if len(coeffs) > 0 and any(c != 0 for c in coeffs):
                max_abs = max(abs(c) for c in coeffs)
                jones_by_cn[cn].append(max_abs)
                jones_entropy_by_cn[cn].append(coeff_entropy(coeffs))
                jones_span_by_cn[cn].append(
                    jones.get("max_power", 0) - jones.get("min_power", 0)
                )
                jones_l2_by_cn[cn].append(
                    float(np.sqrt(sum(c**2 for c in coeffs)))
                )
                n_jones += 1

        # Alexander polynomial
        alex = k.get("alexander")
        if alex and alex.get("coefficients"):
            coeffs = alex["coefficients"]
            if len(coeffs) > 0 and any(c != 0 for c in coeffs):
                max_abs = max(abs(c) for c in coeffs)
                alex_by_cn[cn].append(max_abs)
                alex_entropy_by_cn[cn].append(coeff_entropy(coeffs))
                n_alex += 1

    print(f"Knots with Jones data: {n_jones}")
    print(f"Knots with Alexander data: {n_alex}")
    print(f"Crossing numbers (Jones): {sorted(jones_by_cn.keys())}")

    # ── Jones: median max|coeff| per crossing number ───────────────────
    cn_sorted = sorted(jones_by_cn.keys())
    cn_arr = np.array(cn_sorted, dtype=float)
    jones_median_max = np.array(
        [np.median(jones_by_cn[c]) for c in cn_sorted], dtype=float
    )
    jones_mean_max = np.array(
        [np.mean(jones_by_cn[c]) for c in cn_sorted], dtype=float
    )
    jones_p90_max = np.array(
        [np.percentile(jones_by_cn[c], 90) for c in cn_sorted], dtype=float
    )
    jones_counts = [len(jones_by_cn[c]) for c in cn_sorted]

    print("\n-- Jones max|coeff| by crossing number --")
    for c, med, mean, p90, cnt in zip(cn_sorted, jones_median_max, jones_mean_max, jones_p90_max, jones_counts):
        print(f"  c={c:2d}  median={med:8.1f}  mean={mean:8.1f}  p90={p90:8.1f}  n={cnt}")

    # ── Regressions ────────────────────────────────────────────────────
    # Log-log (power law): max|coeff| ~ c^alpha
    jones_loglog = log_log_regression(cn_arr, jones_median_max)
    print(f"\nJones log-log: alpha={jones_loglog['alpha']:.4f}  R²={jones_loglog['R2']:.4f}")

    # Semi-log (exponential): max|coeff| ~ exp(beta * c)
    jones_semilog = semilog_regression(cn_arr, jones_median_max)
    print(f"Jones semi-log: rate={jones_semilog['exp_rate']:.4f}  R²={jones_semilog['R2']:.4f}")

    # Which fits better?
    growth_regime = "exponential" if jones_semilog["R2"] > jones_loglog["R2"] else "polynomial"
    print(f"Better fit: {growth_regime}")

    # ── Breakpoint analysis ────────────────────────────────────────────
    bp_result = find_breakpoint(cn_arr, jones_median_max)
    if bp_result:
        print(f"\nBreakpoint: c={bp_result['breakpoint_crossing_number']:.0f}")
        print(f"  Left slope (log-log): {bp_result['left_slope_loglog']:.4f}")
        print(f"  Right slope (log-log): {bp_result['right_slope_loglog']:.4f}")
        print(f"  F-test p={bp_result['p_value']:.4e}  significant={bp_result['significant_at_0.05']}")
        if bp_result['right_segment_semilog_R2'] is not None:
            print(f"  Right segment: semilog R²={bp_result['right_segment_semilog_R2']:.4f}"
                  f"  loglog R²={bp_result['right_segment_loglog_R2']:.4f}")

    # ── Also do on mean and p90 ────────────────────────────────────────
    jones_loglog_mean = log_log_regression(cn_arr, jones_mean_max)
    jones_semilog_mean = semilog_regression(cn_arr, jones_mean_max)
    jones_loglog_p90 = log_log_regression(cn_arr, jones_p90_max)
    jones_semilog_p90 = semilog_regression(cn_arr, jones_p90_max)

    # ── L2 norm and span growth ────────────────────────────────────────
    jones_median_l2 = np.array(
        [np.median(jones_l2_by_cn[c]) for c in cn_sorted], dtype=float
    )
    jones_median_span = np.array(
        [np.median(jones_span_by_cn[c]) for c in cn_sorted], dtype=float
    )
    l2_loglog = log_log_regression(cn_arr, jones_median_l2)
    span_loglog = log_log_regression(cn_arr, jones_median_span)
    print(f"\nJones L2 norm log-log: alpha={l2_loglog['alpha']:.4f}  R²={l2_loglog['R2']:.4f}")
    print(f"Jones span log-log: alpha={span_loglog['alpha']:.4f}  R²={span_loglog['R2']:.4f}")

    # ── Entropy analysis ───────────────────────────────────────────────
    jones_median_entropy = np.array(
        [np.median(jones_entropy_by_cn[c]) for c in cn_sorted], dtype=float
    )
    entropy_vs_cn = semilog_regression(cn_arr, jones_median_entropy)
    # Also linear fit for entropy
    ent_slope, ent_int, ent_r, ent_p, ent_se = stats.linregress(cn_arr, jones_median_entropy)
    entropy_linear = {
        "slope": float(ent_slope),
        "intercept": float(ent_int),
        "R2": float(ent_r ** 2),
        "p_value": float(ent_p),
    }
    print(f"\nJones entropy linear: slope={ent_slope:.4f}  R²={ent_r**2:.4f}")

    entropy_table = {}
    for c in cn_sorted:
        vals = jones_entropy_by_cn[c]
        entropy_table[str(c)] = {
            "median": float(np.median(vals)),
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "n": len(vals),
        }

    # ── Alexander comparison ───────────────────────────────────────────
    alex_cn_sorted = sorted(alex_by_cn.keys())
    alex_cn_arr = np.array(alex_cn_sorted, dtype=float)
    alex_median_max = np.array(
        [np.median(alex_by_cn[c]) for c in alex_cn_sorted], dtype=float
    )

    alex_loglog = log_log_regression(alex_cn_arr, alex_median_max)
    alex_semilog = semilog_regression(alex_cn_arr, alex_median_max)
    alex_growth_regime = "exponential" if alex_semilog["R2"] > alex_loglog["R2"] else "polynomial"

    alex_median_entropy = np.array(
        [np.median(alex_entropy_by_cn[c]) for c in alex_cn_sorted], dtype=float
    )
    alex_ent_slope, alex_ent_int, alex_ent_r, alex_ent_p, _ = stats.linregress(
        alex_cn_arr, alex_median_entropy
    )

    print(f"\nAlexander log-log: alpha={alex_loglog['alpha']:.4f}  R²={alex_loglog['R2']:.4f}")
    print(f"Alexander semi-log: rate={alex_semilog['exp_rate']:.4f}  R²={alex_semilog['R2']:.4f}")
    print(f"Alexander growth: {alex_growth_regime}")
    print(f"Alexander entropy slope: {alex_ent_slope:.4f}  R²={alex_ent_r**2:.4f}")

    # ── Alexander breakpoint ───────────────────────────────────────────
    alex_bp = find_breakpoint(alex_cn_arr, alex_median_max)

    # ── Summary table ──────────────────────────────────────────────────
    jones_table = {}
    for c, med, mean, p90, cnt in zip(cn_sorted, jones_median_max, jones_mean_max, jones_p90_max, jones_counts):
        jones_table[str(c)] = {
            "median_max_coeff": float(med),
            "mean_max_coeff": float(mean),
            "p90_max_coeff": float(p90),
            "count": cnt,
        }

    alex_table = {}
    for c in alex_cn_sorted:
        vals = alex_by_cn[c]
        alex_table[str(c)] = {
            "median_max_coeff": float(np.median(vals)),
            "mean_max_coeff": float(np.mean(vals)),
            "count": len(vals),
        }

    # ── Assemble results ───────────────────────────────────────────────
    results = {
        "problem": "C10",
        "title": "Phase Transition in Knot Polynomial Coefficient Growth",
        "n_knots_jones": n_jones,
        "n_knots_alexander": n_alex,
        "crossing_numbers_available": cn_sorted,
        "jones_analysis": {
            "growth_by_crossing_number": jones_table,
            "loglog_fit_median": jones_loglog,
            "semilog_fit_median": jones_semilog,
            "loglog_fit_mean": jones_loglog_mean,
            "semilog_fit_mean": jones_semilog_mean,
            "loglog_fit_p90": jones_loglog_p90,
            "semilog_fit_p90": jones_semilog_p90,
            "dominant_growth_regime": growth_regime,
            "l2_norm_loglog": l2_loglog,
            "span_loglog": span_loglog,
            "breakpoint_analysis": bp_result,
        },
        "jones_entropy": {
            "entropy_by_crossing_number": entropy_table,
            "linear_fit": entropy_linear,
        },
        "alexander_analysis": {
            "growth_by_crossing_number": alex_table,
            "loglog_fit_median": alex_loglog,
            "semilog_fit_median": alex_semilog,
            "dominant_growth_regime": alex_growth_regime,
            "entropy_linear_slope": float(alex_ent_slope),
            "entropy_linear_R2": float(alex_ent_r ** 2),
            "breakpoint_analysis": alex_bp,
        },
        "comparison": {
            "jones_alpha": jones_loglog["alpha"],
            "alexander_alpha": alex_loglog["alpha"],
            "jones_exp_rate": jones_semilog["exp_rate"],
            "alexander_exp_rate": alex_semilog["exp_rate"],
            "jones_loglog_R2": jones_loglog["R2"],
            "jones_semilog_R2": jones_semilog["R2"],
            "alexander_loglog_R2": alex_loglog["R2"],
            "alexander_semilog_R2": alex_semilog["R2"],
            "jones_grows_faster": jones_loglog["alpha"] > alex_loglog["alpha"],
            "note": "Compare Jones alpha to Alexander volume-proxy alpha=2.75 from NF17",
        },
        "summary": {
            "jones_power_law_exponent": jones_loglog["alpha"],
            "jones_exponential_rate": jones_semilog["exp_rate"],
            "jones_better_fit": growth_regime,
            "jones_loglog_R2": jones_loglog["R2"],
            "jones_semilog_R2": jones_semilog["R2"],
            "critical_crossing_number": (
                bp_result["breakpoint_crossing_number"] if bp_result else None
            ),
            "breakpoint_significant": (
                bp_result["significant_at_0.05"] if bp_result else None
            ),
            "jones_entropy_slope": entropy_linear["slope"],
            "alexander_power_law_exponent": alex_loglog["alpha"],
            "alexander_better_fit": alex_growth_regime,
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
