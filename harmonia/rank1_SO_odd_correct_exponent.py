"""
rank1_SO_odd_correct_exponent.py — Harmonia worker T1.

Recompute empirical Keating-Snaith / CFKRS moment ratios for rank-1 elliptic
curves using the CORRECT SO_odd leading exponent k(k+1)/2 (not the SO_even
k(k-1)/2 used in the prior W1 pass).

Context (from cartography/docs/cfkrs_theoretical_comparison_results.json):

  W1 loaded empirical R_k from keating_snaith_moments_results.json, which
  was built with exponent k(k-1)/2 for BOTH ranks. For rank-1 (SO_odd) the
  correct CFKRS exponent for the derivative-moment asymptotic is k(k+1)/2,
  so the prior R_k carried a residual (log X)^k growth and all four k's
  landed FRONTIER.

  This script recomputes M_k per decade for rank=1 curves, applies the
  correct normalization, proxies a(k) from the largest decade, and runs
  exactly the comparison W1 did for rank 0.

Source-of-truth formulas:
  - SO_odd leading growth: M_k(X) ~ a(k) * g_SO_odd(k) * (log X)^{k(k+1)/2}
  - g_SO_odd(k) = g_SO_even(k) * 2^k * (k!)^2 / (2k)!  (Conrey-Snaith 2007,
    leading rank-1 ratio used by W1)
  - g_SO_even(k) = prod_{j=1}^{k-1} Gamma(j+1) * j! / Gamma(j+k+1)
    (Keating-Snaith 2000 Comm. Math. Phys. 214 Thm 2).

Method:
  1. Bin rank=1 EC zeros.object_zeros rows by conductor decade.
  2. Per decade compute raw moments M_k = mean(leading_term^k), SE via
     Var(X^k)/n.
  3. R_k_odd(X) = M_k(X) / (log X)^{k(k+1)/2}.
  4. Proxy a(k) = R_k at largest decade / g_SO_odd(k).
  5. Test SHAPE of convergence across smaller decades; report verdict per k.
  6. Fit R_k_odd(X) = A + B * (1/log X); check improvement vs constant and
     sign consistent with SO_odd asymptote direction.
  7. Also stratify slope by num_bad_primes (join against lmfdb.ec_curvedata),
     for consistency with W2/W3/W5.

Pattern 20: per-cell reporting, never pooled.

Output: cartography/docs/rank1_SO_odd_correct_exponent_results.json
"""
import json
import math
import os
from datetime import datetime, timezone

import mpmath as mp
import numpy as np
import psycopg2

mp.mp.dps = 30

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO_ROOT, "cartography", "docs",
                        "rank1_SO_odd_correct_exponent_results.json")

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

K_VALUES = [1, 2, 3, 4]
DECADE_EDGES = [(100, 1000), (1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]
MIN_PER_CELL = 100


# ---------- theoretical constants ----------

def g_SO_even_KS2000(k: int) -> float:
    prod = mp.mpf(1)
    for j in range(1, k):
        prod *= mp.gamma(j + 1) * mp.factorial(j) / mp.gamma(j + k + 1)
    return float(prod)


def g_SO_odd_CS2007(k: int) -> float:
    base = g_SO_even_KS2000(k)
    ratio = (mp.mpf(2) ** k * mp.factorial(k) ** 2) / mp.factorial(2 * k)
    return float(base * float(ratio))


# ---------- empirical ----------

def load_rank1_by_decade():
    """Return dict (lo, hi) -> np.ndarray of leading_term values."""
    out = {}
    with psycopg2.connect(**PF) as conn:
        cur = conn.cursor()
        for lo, hi in DECADE_EDGES:
            cur.execute("""
                SELECT leading_term
                FROM zeros.object_zeros
                WHERE object_type = 'elliptic_curve'
                  AND analytic_rank = 1
                  AND conductor >= %s AND conductor < %s
                  AND leading_term IS NOT NULL
                  AND leading_term > 0
            """, (lo, hi))
            vals = np.asarray([float(r[0]) for r in cur.fetchall()],
                              dtype=float)
            out[(lo, hi)] = vals
    return out


def load_rank1_joined_nbp():
    """Join rank-1 EC zeros (prometheus_fire) with lmfdb ec_curvedata
    num_bad_primes. Returns list of (conductor, leading_term, nbp)."""
    with psycopg2.connect(**PF) as pf_conn:
        cur = pf_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 1
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor > 0
        """)
        zeros = {r[0]: (int(r[1]), float(r[2])) for r in cur.fetchall()}
    with psycopg2.connect(**LM) as lm_conn:
        cur = lm_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, NULLIF(num_bad_primes, '')::int
            FROM public.ec_curvedata
            WHERE num_bad_primes IS NOT NULL
        """)
        nbp = {r[0]: r[1] for r in cur.fetchall()}
    rows = []
    for lbl, (cond, lt) in zeros.items():
        k = nbp.get(lbl)
        if k is None:
            continue
        rows.append((cond, lt, int(k)))
    return rows


# ---------- fit helpers ----------

def ols_linear(xs, ys, ses=None):
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    if ses is None:
        w = np.ones_like(xs)
    else:
        w = 1.0 / np.asarray(ses, float) ** 2
    W = np.diag(w)
    X = np.vstack([np.ones_like(xs), xs]).T
    XtWX = X.T @ W @ X
    XtWy = X.T @ W @ ys
    try:
        beta = np.linalg.solve(XtWX, XtWy)
    except np.linalg.LinAlgError:
        return None
    resid = ys - X @ beta
    dof = max(1, len(xs) - 2)
    sigma2 = float((resid ** 2 * w).sum() / dof)
    try:
        cov = sigma2 * np.linalg.inv(XtWX)
    except np.linalg.LinAlgError:
        return None
    return {
        "intercept": float(beta[0]),
        "slope": float(beta[1]),
        "intercept_se": float(np.sqrt(max(0.0, cov[0, 0]))),
        "slope_se": float(np.sqrt(max(0.0, cov[1, 1]))),
        "resid_rms": float(np.sqrt((resid ** 2).mean())),
        "n_points": int(len(xs)),
    }


# ---------- main ----------

def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[T1/rank1_SO_odd] start {started}")

    g_odd = {k: g_SO_odd_CS2007(k) for k in K_VALUES}
    g_even = {k: g_SO_even_KS2000(k) for k in K_VALUES}
    print(f"[T1] g_SO_odd = {g_odd}")

    # ------------------------------------------------------------------
    # Load empirical data per decade, compute moments and R_k_odd
    # ------------------------------------------------------------------
    print("[T1] loading rank=1 leading_term by decade...")
    per_decade_vals = load_rank1_by_decade()

    per_cell = {}  # decade_label -> {log_X_mid, n, by_k}
    for (lo, hi), vals in per_decade_vals.items():
        if vals.size < MIN_PER_CELL:
            print(f"  skip [{lo},{hi}) n={vals.size} (< MIN_PER_CELL)")
            continue
        # log_X_mid = ln of geometric-mean conductor = 0.5 * (ln lo + ln hi)
        log_X_mid = 0.5 * (math.log(lo) + math.log(hi))
        decade_label = f"{lo}-{hi}"
        by_k = {}
        n = int(vals.size)
        for k in K_VALUES:
            powers = vals ** k
            M_k = float(powers.mean())
            # SE of mean(X^k)
            if n > 1:
                se = float(powers.std(ddof=1) / math.sqrt(n))
            else:
                se = 0.0
            # SO_odd correct exponent: k(k+1)/2
            exponent = k * (k + 1) / 2
            denom = log_X_mid ** exponent
            R_k_odd = M_k / denom
            R_k_odd_se = se / denom
            # Also retain the SO_even-exponent (prior W1) for reference
            denom_even = log_X_mid ** (k * (k - 1) / 2)
            R_k_even_exp = M_k / denom_even
            by_k[str(k)] = {
                "M_k": M_k,
                "M_k_se": se,
                "exponent_SO_odd": k * (k + 1) / 2,
                "R_k_odd": R_k_odd,
                "R_k_odd_se": R_k_odd_se,
                "R_k_using_SO_even_exponent_for_reference": R_k_even_exp,
            }
        per_cell[decade_label] = {
            "lo": lo, "hi": hi,
            "log_X_mid": log_X_mid,
            "n": n,
            "by_k": by_k,
        }
        print(f"  decade [{lo},{hi}) n={n} log_X={log_X_mid:.3f} "
              f"R1_odd={by_k['1']['R_k_odd']:.4f} "
              f"R2_odd={by_k['2']['R_k_odd']:.4f}")

    # ------------------------------------------------------------------
    # Proxy a(k) from largest decade, compute shape-convergence ratios
    # ------------------------------------------------------------------
    decades_sorted = sorted(per_cell.keys(), key=lambda s: int(s.split("-")[0]))
    if not decades_sorted:
        raise RuntimeError("no rank-1 decades populated")
    largest_decade = decades_sorted[-1]
    proxy_a_k = {}
    for k in K_VALUES:
        R_ld = per_cell[largest_decade]["by_k"][str(k)]["R_k_odd"]
        proxy_a_k[str(k)] = R_ld / g_odd[k] if g_odd[k] != 0 else None

    # Per-cell comparison
    per_cell_comparison = {
        "symmetry_assignment": "SO_odd",
        "exponent_used": "k*(k+1)/2 (CORRECT for SO_odd derivative moments)",
        "exponent_matches_empirical_R_k": True,
        "largest_decade_used_for_proxy_a_k": largest_decade,
        "cells": {},
    }
    for decade, cell in per_cell.items():
        cell_out = {
            "log_X_mid": cell["log_X_mid"],
            "n": cell["n"],
            "by_k": {},
        }
        for k in K_VALUES:
            R_emp = cell["by_k"][str(k)]["R_k_odd"]
            R_emp_se = cell["by_k"][str(k)]["R_k_odd_se"]
            a_proxy = proxy_a_k[str(k)]
            R_theory = a_proxy * g_odd[k]
            cell_out["by_k"][str(k)] = {
                "R_k_empirical": R_emp,
                "R_k_empirical_se": R_emp_se,
                "g_theory_CFKRS_SO_odd": g_odd[k],
                "a_k_proxy": a_proxy,
                "R_k_theory_proxy": R_theory,
                "empirical_over_theory_ratio": (R_emp / R_theory
                                                if R_theory != 0 else None),
                "caveat": (
                    "a(k)_proxy calibrated to largest-decade R_k; this test is "
                    "SHAPE of convergence only. True a(k) needs per-curve "
                    "Euler product."
                ),
            }
        per_cell_comparison["cells"][decade] = cell_out

    # ------------------------------------------------------------------
    # Sub-leading correction fits: R_k_odd(X) = A + B / log X
    # ------------------------------------------------------------------
    subleading_fits = {}
    log_Xs = [per_cell[d]["log_X_mid"] for d in decades_sorted]
    for k in K_VALUES:
        R_vals = [per_cell[d]["by_k"][str(k)]["R_k_odd"] for d in decades_sorted]
        R_ses = [per_cell[d]["by_k"][str(k)]["R_k_odd_se"] for d in decades_sorted]
        if len(log_Xs) < 2:
            subleading_fits[str(k)] = {"skipped": "fewer than 2 decades"}
            continue
        inv_log = [1.0 / L for L in log_Xs]
        fit = ols_linear(inv_log, R_vals, R_ses)
        if fit is None:
            subleading_fits[str(k)] = {"fit_failed": True}
            continue
        resid_const = float(np.std(R_vals))
        # Direction-of-convergence check: sign of B. Because at the largest
        # decade ratio R_emp/R_theory = 1 by proxy construction, and smaller
        # decades have ratios < 1 or > 1, the sub-leading fit sign tells us
        # how R_k approaches its asymptote:
        #   B < 0 means R_k grows as log X grows (approach from below).
        #   B > 0 means R_k falls as log X grows (approach from above).
        # For SO_odd arithmetic families with a derivative moment, the
        # finite-N CFKRS corrections are empirically negative (increasing
        # R_k toward asymptote from below) — same direction as SO_even.
        # We report the sign and let the observed shape speak.
        subleading_fits[str(k)] = {
            "model": "R_k_odd(X) = A + B * (1/log X)",
            "A_fit": fit["intercept"],
            "A_se": fit["intercept_se"],
            "B_fit": fit["slope"],
            "B_se": fit["slope_se"],
            "resid_rms": fit["resid_rms"],
            "resid_rms_if_constant": resid_const,
            "improvement_factor_vs_constant": (
                float(resid_const / fit["resid_rms"])
                if fit["resid_rms"] > 0 else None
            ),
            "log_X_points": log_Xs,
            "R_k_points": R_vals,
            "n_points": fit["n_points"],
            "sign_consistent_with_approach_from_below":
                bool(fit["slope"] < 0),
            "CFKRS_sub_leading_sign_prediction": (
                "negative (R_k approaches asymptote from BELOW as log X "
                "grows; same direction empirically observed for SO_even rank 0)"
            ),
        }

    # ------------------------------------------------------------------
    # Headline verdict per k under correct exponent
    # ------------------------------------------------------------------
    MAX_PCT_GAP_FOR_CONFIRMED = 0.25   # max dev across decades
    MAX_PCT_GAP_AT_SECOND_LARGEST = 0.10  # 10% at second-largest (tight)

    headline_per_k = {}
    verdict_counts = {"confirmed": 0, "partial": 0, "frontier": 0, "na": 0}
    for k in K_VALUES:
        ratios = []
        for d in decades_sorted:
            r = (per_cell_comparison["cells"][d]["by_k"][str(k)]
                 .get("empirical_over_theory_ratio"))
            if r is not None:
                ratios.append((d, r))
        if len(ratios) < 2:
            headline_per_k[str(k)] = {"status": "NA",
                                      "reason": "fewer than 2 decades"}
            verdict_counts["na"] += 1
            continue
        dev_from_1 = [abs(r - 1.0) for _, r in ratios]
        max_dev = max(dev_from_1)
        monotone = all(
            abs(ratios[i][1] - 1) >= abs(ratios[i + 1][1] - 1)
            for i in range(len(ratios) - 1)
        )
        second_largest_dev = abs(ratios[-2][1] - 1)
        if (second_largest_dev <= MAX_PCT_GAP_AT_SECOND_LARGEST and monotone):
            status = "CALIBRATION_CONFIRMED"
            reason = (
                f"second-largest decade within {second_largest_dev:.2%} of 1 "
                f"(threshold {MAX_PCT_GAP_AT_SECOND_LARGEST:.0%}), "
                f"monotonically approaching; max dev across all decades "
                f"{max_dev:.2%}"
            )
            verdict_counts["confirmed"] += 1
        elif max_dev <= MAX_PCT_GAP_FOR_CONFIRMED and monotone:
            status = "PARTIAL"
            reason = (
                f"shape convergent and monotone (max dev {max_dev:.2%}) but "
                f"second-largest decade still off by {second_largest_dev:.2%} "
                f"— finite-N regime"
            )
            verdict_counts["partial"] += 1
        else:
            status = "FRONTIER"
            reason = (f"max deviation {max_dev:.2%} "
                      f"(threshold {MAX_PCT_GAP_FOR_CONFIRMED:.0%}); "
                      f"monotone={monotone}; second-largest-dev "
                      f"{second_largest_dev:.2%}")
            verdict_counts["frontier"] += 1
        headline_per_k[str(k)] = {
            "status": status,
            "reason": reason,
            "max_dev_from_1_across_decades": max_dev,
            "second_largest_decade_dev_from_1": second_largest_dev,
            "monotone_toward_1": monotone,
            "ratios_per_decade": [
                {"decade": d, "emp_over_theory": r} for d, r in ratios
            ],
        }

    # ------------------------------------------------------------------
    # num_bad_primes stratification — slope(R_k_odd vs 1/log X) per nbp
    # ------------------------------------------------------------------
    print("[T1] loading rank=1 with num_bad_primes join...")
    joined = load_rank1_joined_nbp()
    print(f"[T1] joined rows: {len(joined)}")

    # Build per (nbp, decade) cell, compute R_k_odd, then slope fit across
    # decades per nbp.
    MIN_PER_TRIPLE = 100  # conservative
    nbp_cells = {}  # nbp -> decade_label -> by_k dict
    for cond, lt, nbp in joined:
        for lo, hi in DECADE_EDGES:
            if lo <= cond < hi:
                decade_label = f"{lo}-{hi}"
                break
        else:
            continue
        nbp_cells.setdefault(nbp, {}).setdefault(decade_label, []).append(lt)

    nbp_summary = {}
    for nbp, decade_map in sorted(nbp_cells.items()):
        per_decade_R = {}
        for decade_label, vals in decade_map.items():
            vals_arr = np.asarray(vals, dtype=float)
            if vals_arr.size < MIN_PER_TRIPLE:
                continue
            lo, hi = (int(x) for x in decade_label.split("-"))
            log_X_mid = 0.5 * (math.log(lo) + math.log(hi))
            by_k = {}
            for k in K_VALUES:
                powers = vals_arr ** k
                M_k = float(powers.mean())
                se = (float(powers.std(ddof=1) / math.sqrt(vals_arr.size))
                      if vals_arr.size > 1 else 0.0)
                exponent = k * (k + 1) / 2
                denom = log_X_mid ** exponent
                R_k_odd = M_k / denom
                R_k_odd_se = se / denom
                by_k[str(k)] = {
                    "M_k": M_k, "M_k_se": se,
                    "R_k_odd": R_k_odd, "R_k_odd_se": R_k_odd_se,
                }
            per_decade_R[decade_label] = {
                "log_X_mid": log_X_mid, "n": int(vals_arr.size),
                "by_k": by_k,
            }
        if len(per_decade_R) < 2:
            nbp_summary[str(nbp)] = {
                "n_decades_with_data": len(per_decade_R),
                "cells": per_decade_R,
                "skipped_slope_fit": "fewer than 2 populated decades",
            }
            continue
        decades_here = sorted(per_decade_R.keys(),
                              key=lambda s: int(s.split("-")[0]))
        log_Xs_here = [per_decade_R[d]["log_X_mid"] for d in decades_here]
        inv_log_here = [1.0 / L for L in log_Xs_here]
        nbp_fits = {}
        for k in K_VALUES:
            R_here = [per_decade_R[d]["by_k"][str(k)]["R_k_odd"]
                      for d in decades_here]
            R_here_se = [per_decade_R[d]["by_k"][str(k)]["R_k_odd_se"]
                         for d in decades_here]
            fit = ols_linear(inv_log_here, R_here, R_here_se)
            if fit is None:
                nbp_fits[str(k)] = {"fit_failed": True}
                continue
            nbp_fits[str(k)] = {
                "A_fit": fit["intercept"],
                "A_se": fit["intercept_se"],
                "B_fit": fit["slope"],
                "B_se": fit["slope_se"],
                "n_points": fit["n_points"],
                "resid_rms": fit["resid_rms"],
            }
        nbp_summary[str(nbp)] = {
            "n_decades_with_data": len(per_decade_R),
            "cells": per_decade_R,
            "slope_fits_per_k": nbp_fits,
        }

    # Pool-level reference: slope(R_k_odd vs 1/log X) aggregate across all nbp
    # is just the overall fit, already in subleading_fits. Deltas per nbp
    # against that aggregate measure rank-1 nbp heterogeneity.
    nbp_heterogeneity = {}
    for k in K_VALUES:
        overall_A = subleading_fits[str(k)].get("A_fit")
        overall_B = subleading_fits[str(k)].get("B_fit")
        per_nbp = {}
        for nbp_key, summary in nbp_summary.items():
            f = summary.get("slope_fits_per_k", {}).get(str(k))
            if f is None:
                continue
            dA = f["A_fit"] - overall_A if overall_A is not None else None
            dB = f["B_fit"] - overall_B if overall_B is not None else None
            per_nbp[nbp_key] = {
                "A_fit": f["A_fit"], "A_se": f["A_se"],
                "B_fit": f["B_fit"], "B_se": f["B_se"],
                "n_decades": f["n_points"],
                "A_minus_overall": dA, "B_minus_overall": dB,
            }
        nbp_heterogeneity[str(k)] = {
            "overall_A": overall_A,
            "overall_B": overall_B,
            "per_nbp": per_nbp,
        }

    # ------------------------------------------------------------------
    # Overall verdict
    # ------------------------------------------------------------------
    rank1_confirmed = verdict_counts["confirmed"]
    rank1_partial = verdict_counts["partial"]
    rank1_frontier = verdict_counts["frontier"]

    if rank1_confirmed >= 2 and rank1_frontier == 0:
        overall = "CALIBRATION_CONFIRMED"
    elif rank1_confirmed + rank1_partial >= 2 and rank1_frontier <= 1:
        overall = "PARTIAL_CALIBRATION"
    else:
        overall = "FRONTIER"

    headline = {
        "overall_verdict": overall,
        "rank1_SO_odd_k_confirmed": rank1_confirmed,
        "rank1_SO_odd_k_partial": rank1_partial,
        "rank1_SO_odd_k_frontier": rank1_frontier,
        "verdict_counts": verdict_counts,
        "one_liner": (
            f"Rank-1 CFKRS shape test WITH CORRECT SO_odd exponent k(k+1)/2: "
            f"{rank1_confirmed}/4 k-values CALIBRATION_CONFIRMED, "
            f"{rank1_partial}/4 PARTIAL, {rank1_frontier}/4 FRONTIER (proxy "
            f"a(k) calibration). Compare W1 which had 0/4 CONFIRMED using "
            f"the wrong SO_even exponent. Overall verdict: {overall}."
        ),
    }

    finished = datetime.now(timezone.utc).isoformat()
    out = {
        "task": "rank1_SO_odd_correct_exponent_CFKRS_shape_test",
        "instance": "Harmonia_worker_T1",
        "started": started,
        "finished": finished,
        "data_source": "prometheus_fire.zeros.object_zeros "
                       "(elliptic_curve, analytic_rank=1, leading_term>0)",
        "nbp_data_source": "lmfdb.public.ec_curvedata.num_bad_primes",
        "formula_source_of_truth":
            "Keating-Snaith 2000 Thm 2 + Conrey-Snaith 2007 rank-1 ratio",
        "cfkrs_constants": {
            "g_SO_even_KS2000": g_even,
            "g_SO_odd_CS2007": g_odd,
            "formula_source": (
                "g_SO_even(k) = prod_{j=1}^{k-1} Gamma(j+1) * j! / "
                "Gamma(j+k+1). g_SO_odd(k) = g_SO_even(k) * 2^k * (k!)^2 / "
                "(2k)!. Correct SO_odd leading exponent is k(k+1)/2."
            ),
        },
        "per_cell_raw": per_cell,
        "proxy_a_k": proxy_a_k,
        "per_cell_comparison_SO_odd_correct": per_cell_comparison,
        "sub_leading_correction_fits": subleading_fits,
        "num_bad_primes_stratification": nbp_summary,
        "num_bad_primes_heterogeneity_vs_overall": nbp_heterogeneity,
        "headline_per_k": headline_per_k,
        "headline": headline,
        "caveats": [
            ("a(k) proxy = empirical R_k_odd at largest decade / "
             "g_SO_odd(k). CALIBRATES absolute scale; this is a SHAPE test."),
            ("Correct SO_odd exponent k(k+1)/2 used throughout. The prior "
             "W1 report used k(k-1)/2 for rank 1, which carried a residual "
             "(log X)^k growth and forced FRONTIER on all 4 k."),
            ("num_bad_primes stratification joins across databases "
             "(prometheus_fire + lmfdb). MIN_PER_TRIPLE=100. Small-nbp "
             "cells (nbp>=5) drop out at large decades."),
            ("Per Pattern 20: all comparisons are per-cell (decade, nbp) "
             "and never pooled."),
        ],
        "pattern_20_discipline": [
            "All CFKRS ratios per (decade) cell; never pooled across "
            "decades.",
            "Rank-1 SO_odd reported separately (no mixing with rank-0 "
            "SO_even or rank>=2 families).",
            "nbp stratification reports per-nbp slope fits without pooling "
            "across nbp classes.",
        ],
    }

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, default=str)

    print(f"[T1] wrote {OUT_PATH}")
    print("[T1] headline:")
    print(json.dumps(headline, indent=2))
    return out


if __name__ == "__main__":
    main()
