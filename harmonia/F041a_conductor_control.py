"""F041a_conductor_control.py — Kill-test F041a against within-decade conductor-mean variation.

F041a claim (from keating_snaith_arithmetic_analysis + wsw_F041a_block_null):
  At rank 2, the conductor-slope of M_1(X) := mean(leading_term | conductor in decade)
  increases monotonically with num_bad_primes across nbp=1..6 (1.21 -> 2.52).

Kill hypothesis (this test):
  The apparent monotone ladder could be a regression artifact of within-decade
  conductor-mean drift. Strata with more bad primes have systematically larger
  mean conductor within the same decade bin. If the nbp axis merely selects
  different x-values on the log-conductor axis within a decade, the fitted
  slope is confounded with that selection effect, not an arithmetic interaction.

Method:
  1. Pull rank=2 rows joined from zeros.object_zeros <-> public.ec_curvedata.
  2. For each (decade, nbp) cell, compute n, mean(leading_term), and
     mean(log(conductor)) from the raw conductor values (not the midpoint).
     Report the spread of mean_log_conductor_cell ACROSS nbp at fixed decade.
  3. Re-fit slope(nbp) using log(mean_conductor_cell) as the x-axis rather
     than the decade midpoint. Compare against the original.
  4. Joint regression:
       M_1_cell ~ b0 + b_logN * logN_cell + b_nbp * nbp + b_int * logN_cell * nbp
     Report z-scores for each coefficient (OLS with homoskedastic SE).
     If b_nbp z >= 3 after covariate adjustment -> F041a_SURVIVES_CONDUCTOR_CONTROL.
     If b_nbp z < 2 -> F041a_KILLED_CONDUCTOR_ARTIFACT.
  5. Narrow-bin control: within each decade, stratify cells by 0.1-log10-unit
     sub-bins of conductor AND by nbp. Refit slope(nbp) vs log(conductor) on
     these finer cells. Does the monotone-in-nbp pattern survive?

Output: cartography/docs/F041a_conductor_control_kill_test_results.json
"""
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

RANK_TARGET = 2
# Decades 10^3..10^6 per task: (1e3, 1e4), (1e4, 1e5), (1e5, 1e6), plus 10^6..10^7
# to match the F041a ladder scope. The kill test focuses on 10^3..10^6.
DECADE_EDGES = [(1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]
NBP_BINS = [1, 2, 3, 4, 5, 6]
MIN_PER_CELL = 100
NARROW_LOG10_WIDTH = 0.1

OUT_PATH = "cartography/docs/F041a_conductor_control_kill_test_results.json"


def load_rank2():
    print("[load] querying prometheus_fire.zeros.object_zeros (rank=2)...")
    with psycopg2.connect(**PF) as pf_conn:
        cur = pf_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 2
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor IS NOT NULL AND conductor > 0
        """)
        zeros_rows = {r[0]: (int(r[1]), float(r[2])) for r in cur.fetchall()}
    print(f"[load] rank-2 zeros rows: {len(zeros_rows)}")
    print("[load] querying lmfdb.public.ec_curvedata for num_bad_primes...")
    with psycopg2.connect(**LM) as lm_conn:
        cur = lm_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, NULLIF(num_bad_primes, '')::int
            FROM public.ec_curvedata
            WHERE num_bad_primes IS NOT NULL
        """)
        nbp = {r[0]: int(r[1]) for r in cur.fetchall() if r[1] is not None}
    print(f"[load] curvedata nbp rows: {len(nbp)}")
    out = []
    for lbl, (cond, lt) in zeros_rows.items():
        k = nbp.get(lbl)
        if k is None:
            continue
        out.append((cond, lt, k))
    print(f"[load] rank-2 joined rows: {len(out)}")
    return out


def decade_of(cond):
    for lo, hi in DECADE_EDGES:
        if lo <= cond < hi:
            return (lo, hi)
    return None


def decade_mid_log(lo, hi):
    # Geometric midpoint, natural log (matches keating_snaith script)
    return math.log(math.sqrt(lo * hi))


def build_cells(rows):
    """Returns {(lo, hi, nbp): (log_cond_array, leading_term_array)} for rank=2."""
    buckets_lc = defaultdict(list)
    buckets_lt = defaultdict(list)
    for cond, lt, nbp in rows:
        d = decade_of(cond)
        if d is None:
            continue
        if nbp not in NBP_BINS:
            continue
        buckets_lc[(d[0], d[1], nbp)].append(math.log(cond))
        buckets_lt[(d[0], d[1], nbp)].append(lt)
    return {
        k: (np.asarray(buckets_lc[k], dtype=float),
            np.asarray(buckets_lt[k], dtype=float))
        for k in buckets_lc
    }


def fit_ols(X, y):
    """Plain OLS. Returns (beta, se, z, resid_std, r2, n, df)."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, k = X.shape
    XtX = X.T @ X
    try:
        XtX_inv = np.linalg.inv(XtX)
    except np.linalg.LinAlgError:
        return None
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    df = n - k
    if df <= 0:
        return {
            "beta": beta.tolist(), "se": [None] * k, "z": [None] * k,
            "resid_std": None, "r2": None, "n": int(n), "df": int(df),
            "note": "n <= k; SE undefined",
        }
    sigma2 = float((resid @ resid) / df)
    var = sigma2 * XtX_inv
    se = np.sqrt(np.diag(var))
    z = beta / np.where(se > 0, se, np.nan)
    ss_tot = float(((y - y.mean()) ** 2).sum())
    ss_res = float((resid ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return {
        "beta": beta.tolist(),
        "se": se.tolist(),
        "z": z.tolist(),
        "resid_std": math.sqrt(sigma2),
        "r2": r2,
        "n": int(n),
        "df": int(df),
    }


def simple_slope(xs, ys):
    """Slope of y ~ a + b*x with SE. Returns (b, se, z, n, df, r2)."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    n = x.size
    if n < 2:
        return None
    mx, my = x.mean(), y.mean()
    dx = x - mx
    dy = y - my
    sxx = float((dx * dx).sum())
    if sxx == 0:
        return None
    b = float((dx * dy).sum() / sxx)
    a = float(my - b * mx)
    yhat = a + b * x
    resid = y - yhat
    df = n - 2
    if df <= 0:
        return {"slope": b, "intercept": a, "se": None, "z": None,
                "n": int(n), "df": int(df), "r2": None}
    sigma2 = float((resid @ resid) / df)
    se_b = math.sqrt(sigma2 / sxx)
    z = b / se_b if se_b > 0 else None
    ss_tot = float((dy * dy).sum())
    ss_res = float((resid @ resid))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return {"slope": b, "intercept": a, "se": se_b, "z": z,
            "n": int(n), "df": int(df), "r2": r2}


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[F041a_conductor_control] start {started}")

    rows = load_rank2()

    cells = build_cells(rows)
    print(f"[cells] total (decade, nbp) cells: {len(cells)}")

    # -------- Step 1: per-cell summary --------
    per_cell = []
    for (lo, hi, nbp), (lc, lt) in sorted(cells.items()):
        n = int(lc.size)
        entry = {
            "decade_lo": lo, "decade_hi": hi, "nbp": nbp,
            "n": n,
            "mean_leading_term": float(lt.mean()) if n else None,
            "mean_log_conductor": float(lc.mean()) if n else None,
            "std_log_conductor": float(lc.std(ddof=1)) if n > 1 else None,
            "log10_decade_mid": math.log10(math.sqrt(lo * hi)),
            "log_decade_mid_natural": decade_mid_log(lo, hi),
            "used_in_fits": n >= MIN_PER_CELL,
        }
        per_cell.append(entry)

    # Coverage sanity check
    n_cells_used = sum(1 for c in per_cell if c["used_in_fits"])
    print(f"[cells] cells with n >= {MIN_PER_CELL}: {n_cells_used}/{len(per_cell)}")

    # -------- Step 2: within-decade mean-log-conductor spread across nbp --------
    print("[step2] within-decade conductor-mean spread across nbp...")
    within_decade_spread = []
    for (lo, hi) in DECADE_EDGES:
        cells_here = [c for c in per_cell
                      if c["decade_lo"] == lo and c["decade_hi"] == hi
                      and c["used_in_fits"]]
        if len(cells_here) < 2:
            within_decade_spread.append({
                "decade_lo": lo, "decade_hi": hi,
                "n_nbp_cells": len(cells_here),
                "note": "insufficient nbp strata with n>=MIN",
            })
            continue
        log10_conds = [c["mean_log_conductor"] / math.log(10) for c in cells_here]
        span = max(log10_conds) - min(log10_conds)
        decade_width_log10 = math.log10(hi) - math.log10(lo)
        within_decade_spread.append({
            "decade_lo": lo, "decade_hi": hi,
            "n_nbp_cells": len(cells_here),
            "nbps": [c["nbp"] for c in cells_here],
            "mean_log10_conductor_per_nbp":
                {str(c["nbp"]): c["mean_log_conductor"] / math.log(10)
                 for c in cells_here},
            "span_log10": span,
            "decade_width_log10": decade_width_log10,
            "span_fraction_of_decade": span / decade_width_log10,
            "material_drift": span > 0.1,  # task threshold
        })
    material_drift_any = any(w.get("material_drift", False)
                             for w in within_decade_spread)
    print(f"[step2] material within-decade drift observed: {material_drift_any}")

    # -------- Step 3: slope fits, midpoint vs cell-mean x-axis --------
    print("[step3] slope fits per nbp (midpoint vs cell-mean x-axis)...")
    # For the original fit, sort cells by decade for each nbp and fit M1 vs log(midpoint)
    nbp_to_cells = defaultdict(list)
    for c in per_cell:
        if c["used_in_fits"]:
            nbp_to_cells[c["nbp"]].append(c)

    slopes_midpoint = {}
    slopes_cellmean = {}
    for nbp in NBP_BINS:
        cs = sorted(nbp_to_cells.get(nbp, []), key=lambda c: c["decade_lo"])
        if len(cs) < 2:
            slopes_midpoint[nbp] = {"note": "insufficient decades with n>=MIN",
                                    "n_decades": len(cs)}
            slopes_cellmean[nbp] = {"note": "insufficient decades with n>=MIN",
                                    "n_decades": len(cs)}
            continue
        xs_mid = [c["log_decade_mid_natural"] for c in cs]
        xs_cell = [c["mean_log_conductor"] for c in cs]
        ys = [c["mean_leading_term"] for c in cs]
        slopes_midpoint[nbp] = simple_slope(xs_mid, ys) or {"note": "degenerate"}
        slopes_cellmean[nbp] = simple_slope(xs_cell, ys) or {"note": "degenerate"}
        slopes_midpoint[nbp]["n_decades"] = len(cs)
        slopes_cellmean[nbp]["n_decades"] = len(cs)
        slopes_midpoint[nbp]["decades_used"] = [(c["decade_lo"], c["decade_hi"])
                                                for c in cs]
        slopes_cellmean[nbp]["decades_used"] = [(c["decade_lo"], c["decade_hi"])
                                                for c in cs]

    # Pearson corr of slope with nbp under each x-axis
    def corr_nbp_slope(slopes_dict):
        xs, ys = [], []
        for nbp in NBP_BINS:
            s = slopes_dict.get(nbp, {})
            sl = s.get("slope") if isinstance(s, dict) else None
            if sl is None:
                continue
            xs.append(nbp)
            ys.append(sl)
        if len(xs) < 2:
            return None, xs, ys
        xs_a = np.array(xs, dtype=float)
        ys_a = np.array(ys, dtype=float)
        if xs_a.std() == 0 or ys_a.std() == 0:
            return None, xs, ys
        return float(np.corrcoef(xs_a, ys_a)[0, 1]), xs, ys

    corr_mid, _, ys_mid = corr_nbp_slope(slopes_midpoint)
    corr_cell, _, ys_cell = corr_nbp_slope(slopes_cellmean)
    print(f"[step3] slope range midpoint x-axis: {ys_mid}")
    print(f"[step3] slope range cell-mean x-axis: {ys_cell}")
    print(f"[step3] corr(nbp, slope): midpoint={corr_mid}, cellmean={corr_cell}")

    # -------- Step 4: joint regression on cell-level points --------
    print("[step4] joint OLS M1_cell ~ logN_cell + nbp + logN_cell*nbp ...")
    cells_for_joint = [c for c in per_cell if c["used_in_fits"]]
    y_vec = np.array([c["mean_leading_term"] for c in cells_for_joint])
    logN = np.array([c["mean_log_conductor"] for c in cells_for_joint])
    nbp_vec = np.array([c["nbp"] for c in cells_for_joint], dtype=float)
    # Center logN and nbp for interaction interpretability
    logN_c = logN - logN.mean()
    nbp_c = nbp_vec - nbp_vec.mean()
    inter = logN_c * nbp_c
    ones = np.ones_like(y_vec)
    X = np.column_stack([ones, logN_c, nbp_c, inter])
    joint_fit = fit_ols(X, y_vec)
    joint_fit["feature_names"] = ["intercept", "logN_centered",
                                  "nbp_centered", "logN_nbp_interaction"]
    joint_fit["logN_mean"] = float(logN.mean())
    joint_fit["nbp_mean"] = float(nbp_vec.mean())
    print(f"[step4] joint fit: beta={joint_fit['beta']}, z={joint_fit.get('z')}")

    # Also fit the univariate baseline M1 ~ logN + nbp (no interaction)
    X_noint = np.column_stack([ones, logN_c, nbp_c])
    baseline_fit = fit_ols(X_noint, y_vec)
    baseline_fit["feature_names"] = ["intercept", "logN_centered", "nbp_centered"]

    # And the pure-nbp fit (what a naive analyst would see)
    X_nbponly = np.column_stack([ones, nbp_c])
    nbp_only_fit = fit_ols(X_nbponly, y_vec)
    nbp_only_fit["feature_names"] = ["intercept", "nbp_centered"]

    # And the pure-logN fit
    X_lognonly = np.column_stack([ones, logN_c])
    logN_only_fit = fit_ols(X_lognonly, y_vec)
    logN_only_fit["feature_names"] = ["intercept", "logN_centered"]

    # -------- Step 5: narrow log-conductor sub-bins --------
    print(f"[step5] narrow sub-binning at {NARROW_LOG10_WIDTH} log10 units...")
    narrow_cells = defaultdict(list)  # (bin_center_log10, nbp) -> list of leading_term
    for cond, lt, nbp in rows:
        if nbp not in NBP_BINS:
            continue
        # Only consider conductors within the decade range
        if not (DECADE_EDGES[0][0] <= cond < DECADE_EDGES[-1][1]):
            continue
        log10c = math.log10(cond)
        # snap to bin center (floor to bin, then +width/2)
        bin_idx = math.floor(log10c / NARROW_LOG10_WIDTH)
        center = (bin_idx + 0.5) * NARROW_LOG10_WIDTH
        narrow_cells[(center, nbp)].append((log10c, lt))
    # Compute cell means
    narrow_summary = {}
    narrow_nbp_slopes = {}
    for nbp in NBP_BINS:
        pts = []  # (log10_cond_mean, mean_lt, n, center)
        for (center, k), items in narrow_cells.items():
            if k != nbp:
                continue
            if len(items) < MIN_PER_CELL:
                continue
            lcs = [p[0] for p in items]
            lts = [p[1] for p in items]
            pts.append({
                "bin_center_log10": center,
                "mean_log10_cond": float(np.mean(lcs)),
                "mean_leading_term": float(np.mean(lts)),
                "n": len(items),
            })
        pts.sort(key=lambda p: p["bin_center_log10"])
        narrow_summary[str(nbp)] = pts
        if len(pts) >= 2:
            xs = [p["mean_log10_cond"] * math.log(10) for p in pts]  # -> natural log
            ys = [p["mean_leading_term"] for p in pts]
            fit = simple_slope(xs, ys)
            if fit:
                fit["n_bins"] = len(pts)
            narrow_nbp_slopes[nbp] = fit
        else:
            narrow_nbp_slopes[nbp] = {"note": "insufficient narrow bins",
                                       "n_bins": len(pts)}

    def pack_slopes(d):
        out = {}
        for k, v in d.items():
            out[str(k)] = v
        return out

    narrow_corr, _, narrow_slopes_list = corr_nbp_slope(narrow_nbp_slopes)
    print(f"[step5] narrow-bin slopes by nbp: {narrow_slopes_list}")
    print(f"[step5] narrow-bin corr(nbp, slope): {narrow_corr}")

    # -------- Verdict --------
    # Primary criterion: z-score of b_nbp in the joint fit.
    b_nbp_z = None
    b_nbp = None
    b_int_z = None
    if joint_fit and "z" in joint_fit and joint_fit["z"] is not None:
        zs = joint_fit["z"]
        if zs[2] is not None and not (isinstance(zs[2], float) and math.isnan(zs[2])):
            b_nbp_z = float(zs[2])
            b_nbp = float(joint_fit["beta"][2])
        if zs[3] is not None and not (isinstance(zs[3], float) and math.isnan(zs[3])):
            b_int_z = float(zs[3])

    # Secondary criterion: narrow-bin ladder still monotone with similar corr
    # (compare with corr of original slopes_midpoint, which captures the F041a claim)
    survives = (b_nbp_z is not None and abs(b_nbp_z) >= 3.0)
    collapsed = (b_nbp_z is not None and abs(b_nbp_z) < 2.0)

    if survives:
        headline = "F041a_SURVIVES_CONDUCTOR_CONTROL"
        reading = (
            f"Joint regression b_nbp = {b_nbp:.4f} (z={b_nbp_z:.2f}) >= 3.0 after "
            f"controlling for mean log-conductor and interaction. "
            f"Interaction term z = {b_int_z}. Narrow-bin corr(nbp, slope) = {narrow_corr}. "
            f"The nbp effect on first-moment conductor-slope is not merely the "
            f"shadow of within-decade conductor drift; arithmetic structure survives."
        )
    elif collapsed:
        headline = "F041a_KILLED_CONDUCTOR_ARTIFACT"
        reading = (
            f"Joint regression b_nbp z = {b_nbp_z} < 2.0 after controlling for "
            f"mean log-conductor. Interaction z = {b_int_z}. The apparent "
            f"monotone nbp ladder is consistent with within-decade conductor-mean "
            f"drift; F041a is an artifact of the midpoint x-axis choice."
        )
    else:
        headline = "F041a_PARTIAL_WEAKENED"
        reading = (
            f"Joint b_nbp z = {b_nbp_z} (in [2, 3)); nbp retains a real but "
            f"attenuated signal after conductor adjustment. Interaction z = "
            f"{b_int_z}. Coverage should be extended before full adjudication."
        )

    result = {
        "specimen_id": "F041a_conductor_control_kill_test",
        "headline": headline,
        "reading": reading,
        "kill_hypothesis": (
            "F041a monotone-in-nbp slope ladder may be an artifact of "
            "within-decade conductor-mean drift: higher nbp strata may have "
            "systematically larger mean log-conductor within the same decade, "
            "making the midpoint-x regression misrepresent the true log-N "
            "dependence."
        ),
        "verdict_criteria": {
            "survives": "abs(b_nbp z) >= 3.0 in joint fit with logN + nbp + logN*nbp",
            "killed": "abs(b_nbp z) < 2.0 in joint fit",
            "partial": "2.0 <= abs(b_nbp z) < 3.0",
        },
        "step1_per_cell_summary": per_cell,
        "step2_within_decade_mean_log_conductor_spread": within_decade_spread,
        "step2_material_drift_any": material_drift_any,
        "step3_slopes_midpoint_xaxis": pack_slopes(slopes_midpoint),
        "step3_slopes_cellmean_xaxis": pack_slopes(slopes_cellmean),
        "step3_corr_nbp_slope_midpoint": corr_mid,
        "step3_corr_nbp_slope_cellmean": corr_cell,
        "step3_slope_change_summary": {
            str(nbp): {
                "midpoint": slopes_midpoint.get(nbp, {}).get("slope"),
                "cellmean": slopes_cellmean.get(nbp, {}).get("slope"),
                "delta": (
                    (slopes_cellmean.get(nbp, {}).get("slope") or 0)
                    - (slopes_midpoint.get(nbp, {}).get("slope") or 0)
                    if slopes_midpoint.get(nbp, {}).get("slope") is not None
                    and slopes_cellmean.get(nbp, {}).get("slope") is not None
                    else None
                ),
            } for nbp in NBP_BINS
        },
        "step4_joint_regression": joint_fit,
        "step4_baseline_fit_no_interaction": baseline_fit,
        "step4_nbp_only_fit": nbp_only_fit,
        "step4_logN_only_fit": logN_only_fit,
        "step4_key_numbers": {
            "b_nbp": b_nbp,
            "b_nbp_z": b_nbp_z,
            "b_interaction_z": b_int_z,
            "b_logN": (joint_fit["beta"][1] if joint_fit and joint_fit.get("beta") else None),
            "b_logN_z": (joint_fit["z"][1] if joint_fit and joint_fit.get("z") else None),
        },
        "step5_narrow_subbin_slopes_by_nbp": pack_slopes(narrow_nbp_slopes),
        "step5_narrow_subbin_summary_points": narrow_summary,
        "step5_narrow_corr_nbp_slope": narrow_corr,
        "_meta": {
            "task_id": "F041a_conductor_control_kill_test",
            "instance": "Harmonia_worker_U_A",
            "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
            "rank_target": RANK_TARGET,
            "decade_edges": DECADE_EDGES,
            "nbp_bins": NBP_BINS,
            "min_per_cell": MIN_PER_CELL,
            "narrow_log10_width": NARROW_LOG10_WIDTH,
            "notes": [
                "Pattern 20: per-cell n, M_1, and mean log-conductor all reported.",
                "OLS SE assumes homoskedastic residuals; with n_cells small, z is "
                "a heuristic — report alongside coefficient magnitude.",
                "df honestly reported; narrow-bin fits may be thin per stratum.",
            ],
        },
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"[F041a_conductor_control] wrote {OUT_PATH}")
    print(f"[HEADLINE] {headline}")
    print(f"[reading] {reading}")
    print(f"[b_nbp] = {b_nbp}, z = {b_nbp_z}, b_interaction_z = {b_int_z}")


if __name__ == "__main__":
    main()
