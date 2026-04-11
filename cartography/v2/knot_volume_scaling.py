"""
NF17: Hyperbolic Volume Scaling Law
====================================
Log-log regression of knot determinant (proxy for hyperbolic volume) vs
minimum crossing number.  No explicit volume field exists in the dataset,
so |det| is used — justified because log|det| correlates with hyperbolic
volume for hyperbolic knots (see Dunfield–Garoufalidis, Champanerkar et al.).

Reports:
  1. Power-law exponent alpha_vol
  2. R² of the fit
  3. Whether alternating (a) and non-alternating (n) knots follow
     different scaling laws
"""

import json
import math
import os
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

# ── paths ────────────────────────────────────────────────────────────────
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO, "knots", "data", "knots.json")
OUT_PATH = os.path.join(REPO, "v2", "knot_volume_scaling_results.json")


def parse_crossing_number(name: str) -> int:
    """Extract crossing number from knot name.

    Formats:
      '3_1'       -> 3
      '10_123'    -> 10
      '11*a_1'    -> 11   (* marks knots >=11)
      '13*n_500'  -> 13
    """
    prefix = name.split("_")[0]          # e.g. '11*a', '10', '3'
    digits = ""
    for ch in prefix:
        if ch.isdigit():
            digits += ch
        else:
            break
    return int(digits) if digits else 0


def parse_knot_type(name: str) -> str:
    """Return 'alternating', 'non-alternating', or 'unknown'."""
    prefix = name.split("_")[0]
    if "*a" in prefix or (prefix.replace("*", "").isdigit()):
        # Names without a/n (crossing <=10) are alternating by convention
        # in KnotInfo's ordering for small crossing numbers, but some are
        # non-alternating.  For <=10 crossing knots, there is no flag in
        # the name.  We'll label them 'classic' and analyse separately.
        pass
    if "*n" in prefix:
        return "non-alternating"
    if "*a" in prefix:
        return "alternating"
    # Knots with crossing number <= 10 don't carry a/n flag
    return "classic"


def log_log_regression(x, y):
    """OLS on log(x) vs log(y).  Returns slope (alpha), intercept, R²."""
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


def main():
    with open(DATA_PATH) as f:
        raw = json.load(f)

    knots = raw["knots"]

    # ── build arrays ─────────────────────────────────────────────────
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
            continue  # trivial knot or missing data
        ktype = parse_knot_type(k["name"])
        rows.append((cn, det, ktype))

    crossing = np.array([r[0] for r in rows], dtype=float)
    det = np.array([r[1] for r in rows], dtype=float)
    types = [r[2] for r in rows]

    # ── global fit ───────────────────────────────────────────────────
    global_fit = log_log_regression(crossing, det)
    print(f"GLOBAL  alpha={global_fit['alpha']:.4f}  R²={global_fit['R2']:.4f}  n={global_fit['n']}")

    # ── per-type fits ────────────────────────────────────────────────
    type_fits = {}
    for label in ("alternating", "non-alternating", "classic"):
        mask = np.array([t == label for t in types])
        if mask.sum() < 10:
            continue
        fit = log_log_regression(crossing[mask], det[mask])
        type_fits[label] = fit
        print(f"  {label:20s}  alpha={fit['alpha']:.4f}  R²={fit['R2']:.4f}  n={fit['n']}")

    # ── per crossing-number median determinant (for cleaner scaling) ──
    cn_medians = defaultdict(list)
    cn_medians_alt = defaultdict(list)
    cn_medians_nonalt = defaultdict(list)
    for cn_val, det_val, ktype in rows:
        cn_medians[cn_val].append(det_val)
        if ktype in ("alternating", "classic"):
            cn_medians_alt[cn_val].append(det_val)
        elif ktype == "non-alternating":
            cn_medians_nonalt[cn_val].append(det_val)

    median_table = {}
    for cn_val in sorted(cn_medians):
        vals = cn_medians[cn_val]
        median_table[cn_val] = {
            "median_det": float(np.median(vals)),
            "mean_det": float(np.mean(vals)),
            "count": len(vals),
        }

    # Median-based fit
    cn_arr = np.array(sorted(cn_medians.keys()), dtype=float)
    med_arr = np.array([np.median(cn_medians[int(c)]) for c in cn_arr])
    median_fit = log_log_regression(cn_arr, med_arr)
    print(f"\nMEDIAN  alpha={median_fit['alpha']:.4f}  R²={median_fit['R2']:.4f}  n={median_fit['n']}")

    # Median fits per type
    median_type_fits = {}
    for label, bucket in [("alternating+classic", cn_medians_alt),
                           ("non-alternating", cn_medians_nonalt)]:
        if len(bucket) < 3:
            continue
        cn_a = np.array(sorted(bucket.keys()), dtype=float)
        med_a = np.array([np.median(bucket[int(c)]) for c in cn_a])
        fit = log_log_regression(cn_a, med_a)
        median_type_fits[label] = fit
        print(f"  median {label:25s}  alpha={fit['alpha']:.4f}  R²={fit['R2']:.4f}  n={fit['n']}")

    # ── Chow test: are alternating and non-alternating slopes different? ──
    # Simple approach: compare slopes via t-test on difference
    alt_labels = ("alternating", "classic")
    has_both = all(l in type_fits for l in ("alternating", "non-alternating"))
    slope_test = None
    if has_both:
        a1 = type_fits["alternating"]["alpha"]
        a2 = type_fits["non-alternating"]["alpha"]
        se1 = type_fits["alternating"]["std_err"]
        se2 = type_fits["non-alternating"]["std_err"]
        t_stat = (a1 - a2) / math.sqrt(se1**2 + se2**2)
        df_approx = type_fits["alternating"]["n"] + type_fits["non-alternating"]["n"] - 4
        p_two = 2 * (1 - stats.t.cdf(abs(t_stat), df_approx))
        slope_test = {
            "alpha_alternating": a1,
            "alpha_non_alternating": a2,
            "delta_alpha": a1 - a2,
            "t_stat": float(t_stat),
            "df": int(df_approx),
            "p_value": float(p_two),
            "different_at_0.05": bool(p_two < 0.05),
        }
        print(f"\nSLOPE TEST  delta={a1-a2:.4f}  t={t_stat:.2f}  p={p_two:.2e}  different={p_two < 0.05}")

    # ── assemble results ─────────────────────────────────────────────
    results = {
        "problem": "NF17",
        "title": "Hyperbolic Volume Scaling Law (determinant proxy)",
        "method": "log-log OLS regression: log|det| ~ alpha * log(crossing_number)",
        "note": "No explicit volume field; |det| used as proxy for hyperbolic volume",
        "global_fit": global_fit,
        "type_fits": type_fits,
        "median_fit_by_crossing_number": median_fit,
        "median_type_fits": median_type_fits,
        "median_table": {str(k): v for k, v in median_table.items()},
        "slope_comparison_test": slope_test,
        "summary": {
            "scaling_exponent_alpha": global_fit["alpha"],
            "R2": global_fit["R2"],
            "alternating_vs_nonalternating_different": (
                slope_test["different_at_0.05"] if slope_test else None
            ),
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
