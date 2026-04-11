"""
List2 #18: Knot Volume-Crossing Non-linear Scaling
====================================================
Non-linear regression V = a*C^b between crossing number C and
hyperbolic volume V.

No explicit volume field in knots.json; |det| used as proxy
(justified: log|det| correlates with hyperbolic volume for
hyperbolic knots — Dunfield-Garoufalidis, Champanerkar et al.).

Extends NF17 (α=2.75 median, R2=0.958) with:
  1. Direct non-linear least squares: V = a*C^b
  2. Exponential model: V = a*exp(b*C)
  3. C*log(C) model: V = a*C*log(C) + c
  4. Model comparison via AIC/BIC
  5. Both per-knot and median-per-crossing fits
"""

import json
import math
import os
import re
import warnings
from collections import defaultdict

import numpy as np
from scipy import optimize, stats

warnings.filterwarnings("ignore")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO, "knots", "data", "knots.json")
OUT_PATH = os.path.join(REPO, "v2", "knot_volume_crossing_results.json")


def parse_crossing_number(name: str) -> int:
    prefix = name.split("_")[0]
    digits = ""
    for ch in prefix:
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else 0


def parse_knot_type(name: str) -> str:
    prefix = name.split("_")[0]
    if "*n" in prefix:
        return "non-alternating"
    if "*a" in prefix:
        return "alternating"
    return "classic"


# -- Model functions --------------------------------------------------

def power_law(C, a, b):
    """V = a * C^b"""
    return a * np.power(C, b)


def exponential(C, a, b):
    """V = a * exp(b * C)"""
    return a * np.exp(b * C)


def c_log_c(C, a, c):
    """V = a * C * log(C) + c"""
    return a * C * np.log(C) + c


def fit_power_law(x, y):
    """Non-linear least squares for V = a*C^b."""
    try:
        popt, pcov = optimize.curve_fit(power_law, x, y, p0=[1.0, 2.0], maxfev=10000)
        y_pred = power_law(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1.0 - ss_res / ss_tot
        perr = np.sqrt(np.diag(pcov))
        return {
            "a": float(popt[0]),
            "b": float(popt[1]),
            "a_se": float(perr[0]),
            "b_se": float(perr[1]),
            "R2": float(r2),
            "SS_res": float(ss_res),
            "n": int(len(x)),
            "n_params": 2,
        }
    except Exception as e:
        return {"error": str(e)}


def fit_exponential(x, y):
    """Non-linear least squares for V = a*exp(b*C)."""
    try:
        popt, pcov = optimize.curve_fit(exponential, x, y, p0=[1.0, 0.3], maxfev=10000)
        y_pred = exponential(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1.0 - ss_res / ss_tot
        perr = np.sqrt(np.diag(pcov))
        return {
            "a": float(popt[0]),
            "b": float(popt[1]),
            "a_se": float(perr[0]),
            "b_se": float(perr[1]),
            "R2": float(r2),
            "SS_res": float(ss_res),
            "n": int(len(x)),
            "n_params": 2,
        }
    except Exception as e:
        return {"error": str(e)}


def fit_c_log_c(x, y):
    """Linear least squares for V = a*C*log(C) + c."""
    try:
        popt, pcov = optimize.curve_fit(c_log_c, x, y, p0=[10.0, 0.0], maxfev=10000)
        y_pred = c_log_c(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1.0 - ss_res / ss_tot
        perr = np.sqrt(np.diag(pcov))
        return {
            "a": float(popt[0]),
            "c": float(popt[1]),
            "a_se": float(perr[0]),
            "c_se": float(perr[1]),
            "R2": float(r2),
            "SS_res": float(ss_res),
            "n": int(len(x)),
            "n_params": 2,
        }
    except Exception as e:
        return {"error": str(e)}


def log_log_ols(x, y):
    """OLS on log-log for comparison with NF17."""
    lx = np.log(x)
    ly = np.log(y)
    slope, intercept, r, p, se = stats.linregress(lx, ly)
    return {
        "alpha": float(slope),
        "log_a": float(intercept),
        "a": float(np.exp(intercept)),
        "R2": float(r ** 2),
        "p_value": float(p),
        "std_err": float(se),
        "n": int(len(x)),
        "n_params": 2,
    }


def compute_aic_bic(ss_res, n, k):
    """AIC and BIC from residual sum of squares."""
    if n <= k + 1 or ss_res <= 0:
        return {"AIC": float("inf"), "BIC": float("inf")}
    log_lik = -n / 2 * (np.log(2 * np.pi * ss_res / n) + 1)
    aic = 2 * k - 2 * log_lik
    bic = k * np.log(n) - 2 * log_lik
    return {"AIC": float(aic), "BIC": float(bic)}


def main():
    with open(DATA_PATH) as f:
        raw = json.load(f)

    knots = raw["knots"]

    # -- build arrays -------------------------------------------------
    rows = []
    for k in knots:
        cn = k["crossing_number"]
        if cn == 0:
            cn = parse_crossing_number(k["name"])
        det_raw = k.get("determinant")
        if det_raw is None:
            continue
        det = abs(det_raw)
        if cn < 3 or det < 1:
            continue
        ktype = parse_knot_type(k["name"])
        rows.append((cn, det, ktype))

    crossing = np.array([r[0] for r in rows], dtype=float)
    det = np.array([r[1] for r in rows], dtype=float)

    # -- per-crossing medians -----------------------------------------
    cn_medians = defaultdict(list)
    for cn_val, det_val, _ in rows:
        cn_medians[cn_val].append(det_val)

    cn_arr = np.array(sorted(cn_medians.keys()), dtype=float)
    med_arr = np.array([np.median(cn_medians[int(c)]) for c in cn_arr])

    median_table = {}
    for c in sorted(cn_medians):
        vals = cn_medians[c]
        median_table[str(c)] = {
            "median_det": float(np.median(vals)),
            "mean_det": float(np.mean(vals)),
            "std_det": float(np.std(vals)),
            "count": len(vals),
        }

    print("=" * 65)
    print("List2 #18: Knot Volume-Crossing Non-linear Scaling")
    print("=" * 65)
    print(f"Total knots with C>=3 and |det|>=1: {len(rows)}")
    print(f"Crossing numbers: {sorted(cn_medians.keys())}")
    print()

    # ===================================================================
    # FIT 1: Median-based fits (cleaner signal, matches NF17 approach)
    # ===================================================================
    print("-- Median-based fits (n={}) --".format(len(cn_arr)))

    # Power law: V = a * C^b (non-linear LS)
    med_power = fit_power_law(cn_arr, med_arr)
    print(f"  Power law:   V = {med_power.get('a', '?'):.4f} * C^{med_power.get('b', '?'):.4f}  "
          f"R2={med_power.get('R2', '?'):.6f}")

    # Log-log OLS (for comparison with NF17)
    med_loglog = log_log_ols(cn_arr, med_arr)
    print(f"  Log-log OLS: alpha={med_loglog['alpha']:.4f}  R2={med_loglog['R2']:.6f}  "
          f"(NF17 got 2.746)")

    # Exponential: V = a * exp(b * C)
    med_exp = fit_exponential(cn_arr, med_arr)
    print(f"  Exponential: V = {med_exp.get('a', '?'):.4f} * exp({med_exp.get('b', '?'):.4f}*C)  "
          f"R2={med_exp.get('R2', '?'):.6f}")

    # C*log(C): V = a * C * log(C) + c
    med_clogc = fit_c_log_c(cn_arr, med_arr)
    print(f"  C*log(C):    V = {med_clogc.get('a', '?'):.4f} * C*log(C) + {med_clogc.get('c', '?'):.4f}  "
          f"R2={med_clogc.get('R2', '?'):.6f}")

    # AIC/BIC comparison for median fits
    print("\n  Model comparison (median):")
    med_models = {}
    for name, fit in [("power_law", med_power), ("exponential", med_exp), ("c_log_c", med_clogc)]:
        if "error" not in fit:
            ic = compute_aic_bic(fit["SS_res"], fit["n"], fit["n_params"])
            fit.update(ic)
            med_models[name] = fit
            print(f"    {name:15s}  AIC={ic['AIC']:.1f}  BIC={ic['BIC']:.1f}  R2={fit['R2']:.6f}")

    # Determine best model
    best_med = min(med_models.items(), key=lambda x: x[1].get("AIC", float("inf")))
    print(f"  Best (AIC): {best_med[0]}")

    # ===================================================================
    # FIT 2: Per-knot fits (all data, noisier)
    # ===================================================================
    print(f"\n-- Per-knot fits (n={len(crossing)}) --")

    all_power = fit_power_law(crossing, det)
    print(f"  Power law:   V = {all_power.get('a', '?'):.4f} * C^{all_power.get('b', '?'):.4f}  "
          f"R2={all_power.get('R2', '?'):.6f}")

    all_loglog = log_log_ols(crossing, det)
    print(f"  Log-log OLS: alpha={all_loglog['alpha']:.4f}  R2={all_loglog['R2']:.6f}")

    all_exp = fit_exponential(crossing, det)
    print(f"  Exponential: V = {all_exp.get('a', '?'):.4f} * exp({all_exp.get('b', '?'):.4f}*C)  "
          f"R2={all_exp.get('R2', '?'):.6f}")

    all_clogc = fit_c_log_c(crossing, det)
    print(f"  C*log(C):    V = {all_clogc.get('a', '?'):.4f} * C*log(C) + {all_clogc.get('c', '?'):.4f}  "
          f"R2={all_clogc.get('R2', '?'):.6f}")

    print("\n  Model comparison (all knots):")
    all_models = {}
    for name, fit in [("power_law", all_power), ("exponential", all_exp), ("c_log_c", all_clogc)]:
        if "error" not in fit:
            ic = compute_aic_bic(fit["SS_res"], fit["n"], fit["n_params"])
            fit.update(ic)
            all_models[name] = fit
            print(f"    {name:15s}  AIC={ic['AIC']:.1f}  BIC={ic['BIC']:.1f}  R2={fit['R2']:.6f}")

    best_all = min(all_models.items(), key=lambda x: x[1].get("AIC", float("inf")))
    print(f"  Best (AIC): {best_all[0]}")

    # ===================================================================
    # Expected: b ~ 1.33? Check against actual
    # ===================================================================
    b_median = med_power.get("b", None)
    b_all = all_power.get("b", None)
    print(f"\n-- Expected b ~ 1.33 check --")
    print(f"  Power law b (median): {b_median:.4f}" if b_median else "  Power law b (median): FAILED")
    print(f"  Power law b (all):    {b_all:.4f}" if b_all else "  Power law b (all):    FAILED")
    print(f"  Log-log alpha (median): {med_loglog['alpha']:.4f}")
    print(f"  NOTE: |det| is NOT hyperbolic volume; it's a proxy.")
    print(f"  The b~1.33 expectation applies to actual hyperbolic volume.")
    print(f"  |det| grows much faster than volume with crossing number.")

    # ===================================================================
    # Residual analysis
    # ===================================================================
    if "error" not in med_power:
        resid = med_arr - power_law(cn_arr, med_power["a"], med_power["b"])
        resid_norm = resid / med_arr
        print(f"\n-- Residuals (median power law) --")
        for i, c in enumerate(cn_arr):
            print(f"  C={int(c):2d}  obs={med_arr[i]:.0f}  pred={power_law(c, med_power['a'], med_power['b']):.1f}  "
                  f"resid%={100*resid_norm[i]:+.1f}%")

    # ===================================================================
    # Assemble results
    # ===================================================================
    results = {
        "problem": "List2_18",
        "title": "Knot Volume-Crossing Non-linear Scaling",
        "extends": "NF17",
        "note": "No volume_hyperbolic field in dataset; |det| used as proxy",
        "data_summary": {
            "n_knots": len(rows),
            "crossing_numbers": sorted(cn_medians.keys()),
            "n_crossing_groups": len(cn_arr),
        },
        "median_fits": {
            "power_law": med_power,
            "log_log_ols": med_loglog,
            "exponential": med_exp,
            "c_log_c": med_clogc,
            "best_model_AIC": best_med[0],
        },
        "all_knot_fits": {
            "power_law": all_power,
            "log_log_ols": all_loglog,
            "exponential": all_exp,
            "c_log_c": all_clogc,
            "best_model_AIC": best_all[0],
        },
        "median_table": median_table,
        "interpretation": {
            "b_power_law_median": med_power.get("b"),
            "b_power_law_all": all_power.get("b"),
            "alpha_loglog_median": med_loglog["alpha"],
            "expected_b_for_volume": 1.33,
            "proxy_note": (
                "|det| is not hyperbolic volume. For actual volume, Lackenby proved "
                "V <= 10*(C-1)*v_tet (linear upper bound in C). The expected b~1.33 "
                "for volume-vs-C is sub-quadratic. Our |det| proxy has b~2.7 because "
                "det grows exponentially faster than volume with crossing number."
            ),
            "power_law_is_best": best_med[0] == "power_law",
            "model_ranking_median": sorted(
                [(k, v.get("AIC", float("inf"))) for k, v in med_models.items()],
                key=lambda x: x[1],
            ),
        },
        "summary": {
            "b_nlls": med_power.get("b"),
            "b_loglog": med_loglog["alpha"],
            "best_model": best_med[0],
            "R2_power_median": med_power.get("R2"),
            "R2_exp_median": med_exp.get("R2"),
            "R2_clogc_median": med_clogc.get("R2"),
            "NF17_alpha": 2.746,
            "conclusion": (
                "Power law V=a*C^b fits |det| proxy with b~{:.2f} (median) and R^2~{:.4f}. "
                "This is the |det| scaling, not volume scaling. For true hyperbolic volume, "
                "theory predicts near-linear growth (Lackenby bound), so b~1.33 is plausible "
                "for volume but our data only has |det|."
            ).format(med_power.get("b", 0), med_power.get("R2", 0)),
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
