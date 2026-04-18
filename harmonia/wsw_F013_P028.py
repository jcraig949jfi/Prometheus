"""wsw_F013_P028.py — F013 zero-spacing rigidity vs rank, stratified by Katz-Sarnak symmetry type.

Task: wsw_F013_P028, claimed by Harmonia_M2_sessionB, tick 18.
Target projection: P028 (Katz-Sarnak via rank parity for EC).

Context:
  - F013: "Spacing variance decreases linearly with rank" (slope=-0.0019, R²=0.399, weak).
  - sessionD refined: the effect is density-mediated (P051 unfolding reduces slope ~74%).
  - Prior runs: F011_P028 z=5.4 (RESOLVES), F010_P028 Is_Even strong (RESOLVES).

Method:
  - Reuse F011 data pipeline: unfolded first-gap variance per (rank, symmetry class) cell.
  - For each Katz-Sarnak class (SO_even = even rank, SO_odd = odd rank), fit a linear slope
    of variance vs rank.
  - Compare slopes. If |slope_SO_even - slope_SO_odd| / se_slope >= 3.0 → P028 RESOLVES F013.
  - If slopes are similar, F013 is axis-uniform under P028.

For EC, root_number = (-1)^rank by BSD parity, so rank parity IS the Katz-Sarnak class.
  SO_even = ranks {0, 2, 4, ...}
  SO_odd  = ranks {1, 3, 5, ...}

Output: cartography/docs/wsw_F013_P028_results.json
"""
import json
import os
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import stats

GUE_VAR = 0.178
PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
MIN_STRATUM_N = 100


def connect(dbname):
    return psycopg2.connect(
        host=PG["host"], port=PG["port"], dbname=dbname,
        user=PG["user"], password=PG["password"], connect_timeout=10,
    )


def fetch_zeros():
    with connect("prometheus_fire") as c:
        return pd.read_sql("""
            SELECT lmfdb_label, conductor::bigint AS conductor,
                   zeros[1]::float8 AS z1, zeros[2]::float8 AS z2
              FROM zeros.object_zeros
             WHERE object_type = 'elliptic_curve'
               AND n_zeros >= 2 AND zeros[1] > 0.0 AND zeros[2] > zeros[1]
        """, c)


def fetch_ec():
    with connect("lmfdb") as c:
        return pd.read_sql("""
            SELECT lmfdb_label, NULLIF(rank, '')::int AS rank
              FROM public.ec_curvedata
        """, c)


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F013_P028] start {started}")

    df_z = fetch_zeros()
    df_e = fetch_ec()
    print(f"[fetch] zeros={len(df_z)}, ec={len(df_e)}")

    df = df_z.merge(df_e, on="lmfdb_label", how="inner")
    df = df.dropna(subset=["rank"])
    df["rank"] = df["rank"].astype(int)

    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap_unf"] = z2u - z1u
    ok = np.isfinite(df["gap_unf"]) & (df["gap_unf"] > 0)
    df = df.loc[ok].copy()
    df["ks_class"] = np.where(df["rank"] % 2 == 0, "SO_even", "SO_odd")
    print(f"[unfold] {len(df)} rows with positive unfolded gap")

    # Variance per (rank, ks_class) cell
    per_cell = []
    for (rk, ks), g in df.groupby(["rank", "ks_class"]):
        vals = g["gap_unf"].to_numpy(float)
        vals = vals[np.isfinite(vals)]
        n = vals.size
        if n < MIN_STRATUM_N:
            continue
        var = float(np.var(vals, ddof=1))
        # sampling SE of variance under normal approx: var * sqrt(2/(n-1))
        se_var = var * math.sqrt(2.0 / max(n - 1, 1))
        per_cell.append({
            "rank": int(rk),
            "ks_class": ks,
            "n": n,
            "var": var,
            "se_var": se_var,
            "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
        })
    print("[per_cell]")
    for c in sorted(per_cell, key=lambda r: (r["ks_class"], r["rank"])):
        print(f"  rank={c['rank']:>2}  {c['ks_class']}  n={c['n']:>7}  "
              f"var={c['var']:.4f}  deficit={c['deficit_pct']:.1f}%")

    # Slope per Katz-Sarnak class. Use a pair-difference SE for the 2-cell case
    # (DOF=0 makes residual-based SE ill-defined, but the propagation-of-error
    # SE from the two per-cell variance SEs is well-defined and honest).
    def weighted_slope(cells):
        if len(cells) < 2:
            return None
        cells = sorted(cells, key=lambda c: c["rank"])
        x = np.array([c["rank"] for c in cells], dtype=float)
        y = np.array([c["var"] for c in cells], dtype=float)
        se_y = np.array([c["se_var"] for c in cells], dtype=float)

        if len(cells) == 2:
            # Exact pair-difference slope + propagation-of-error SE
            dx = x[1] - x[0]
            if dx == 0:
                return None
            slope = (y[1] - y[0]) / dx
            se_slope = math.sqrt(se_y[0] ** 2 + se_y[1] ** 2) / abs(dx)
            intercept = y[0] - slope * x[0]
            return {"slope": float(slope), "se_slope": float(se_slope),
                    "intercept": float(intercept), "n_cells": 2,
                    "method": "pair_difference_with_propagation"}

        # 3+ cells: weighted LS with WLS residual SE
        w = 1.0 / (se_y ** 2)
        w_sum = w.sum()
        xw = (w * x).sum() / w_sum
        yw = (w * y).sum() / w_sum
        num = (w * (x - xw) * (y - yw)).sum()
        den = (w * (x - xw) ** 2).sum()
        slope = num / den if den > 0 else None
        if slope is None:
            return None
        resid = y - (slope * x + (yw - slope * xw))
        chi2 = (w * resid ** 2).sum()
        dof = max(len(cells) - 2, 1)
        se_slope = math.sqrt(chi2 / (dof * den)) if den > 0 else None
        return {"slope": float(slope), "se_slope": float(se_slope) if se_slope else None,
                "intercept": float(yw - slope * xw), "n_cells": len(cells),
                "method": "weighted_least_squares"}

    so_even_cells = [c for c in per_cell if c["ks_class"] == "SO_even"]
    so_odd_cells = [c for c in per_cell if c["ks_class"] == "SO_odd"]

    so_even_fit = weighted_slope(so_even_cells)
    so_odd_fit = weighted_slope(so_odd_cells)
    print(f"[slope SO_even] {so_even_fit}")
    print(f"[slope SO_odd]  {so_odd_fit}")

    # Slope difference z-test
    if so_even_fit and so_odd_fit and so_even_fit["se_slope"] and so_odd_fit["se_slope"]:
        diff = so_even_fit["slope"] - so_odd_fit["slope"]
        se_diff = math.sqrt(so_even_fit["se_slope"] ** 2 + so_odd_fit["se_slope"] ** 2)
        z_diff = diff / se_diff if se_diff > 0 else None
        p_diff = 2.0 * (1.0 - stats.norm.cdf(abs(z_diff))) if z_diff is not None else None
    else:
        diff = se_diff = z_diff = p_diff = None

    # Verdict
    THRESH = 3.0
    if z_diff is not None and abs(z_diff) >= THRESH:
        verdict = "P028_RESOLVES"
        reading = (f"Rank-vs-variance slope differs between SO_even and SO_odd at z={z_diff:.2f} "
                   f"(|z|>={THRESH}). F013 is NOT axis-uniform under Katz-Sarnak. The slope-signs "
                   f"may even flip (SO_even vs SO_odd can move in opposite directions with rank).")
    elif z_diff is not None:
        verdict = "P028_AXIS_UNIFORM"
        reading = (f"Slopes agree within z={z_diff:.2f} (<{THRESH}). F013 is axis-uniform under "
                   f"Katz-Sarnak — the weak rank-variance slope is the same in both symmetry classes. "
                   f"Extends the shared_axis_exhausted ledger with F013 joining F011 (uniform under "
                   f"object-property axes; only the direct parity split resolves F011 but not F013).")
    else:
        verdict = "INCONCLUSIVE"
        reading = "Insufficient adequate cells per class to fit a slope."

    # Position in F011/F010 ledger
    ledger = {
        "F011_P028_result": "RESOLVES at z=5.4 (deficit spread 7.6%)",
        "F010_P028_result": "PARTIALLY RESOLVES at Is_Even axis (sessionC bigsample)",
        "F013_P028_result_this_run": verdict,
    }

    out = {
        "specimen_id": "F013",
        "projections_used": ["P028"],
        "verdict": verdict,
        "reading": reading,
        "per_cell": sorted(per_cell, key=lambda r: (r["ks_class"], r["rank"])),
        "fit_SO_even": so_even_fit,
        "fit_SO_odd": so_odd_fit,
        "slope_difference": {
            "diff": float(diff) if diff is not None else None,
            "se_diff": float(se_diff) if se_diff is not None else None,
            "z_diff": float(z_diff) if z_diff is not None else None,
            "p_value": float(p_diff) if p_diff is not None else None,
            "threshold": THRESH,
        },
        "cross_specimen_ledger": ledger,
        "shape_summary": reading,
        "_meta": {
            "task_id": "wsw_F013_P028",
            "instance": "Harmonia_M2_sessionB",
            "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
            "gue_var_baseline": GUE_VAR,
            "min_stratum_n": MIN_STRATUM_N,
            "data_source": "zeros.object_zeros × ec_curvedata on lmfdb_label",
            "notes": [
                "Katz-Sarnak class via rank parity: SO_even iff rank even; SO_odd iff rank odd.",
                "Variance per (rank, ks_class) cell; slope fit via weighted LS with var SE = var*sqrt(2/(n-1)).",
                "Rank 4+ has sparse coverage; only cells with n>=100 enter the fit.",
                "Expect SO_even cells at ranks {0, 2} (rank 4 usually <100); SO_odd at {1, 3}.",
            ],
        },
    }

    out_path = os.path.join("cartography", "docs", "wsw_F013_P028_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[wsw_F013_P028] wrote {out_path}")
    print(f"[verdict] {verdict}")
    print(f"[reading] {reading}")


if __name__ == "__main__":
    main()
