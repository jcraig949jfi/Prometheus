"""wsw_F011_excised_ensemble.py — Aporia Report 1: is F011's 38% deficit the excised ensemble?

Task: Report 1 delegation from Aporia via sessionA (2026-04-18, tick 23).

Aporia's diagnosis: the F011 deficit matches the Duenez-Huynh-Keating-Miller-Snaith
excised ensemble — a finite-CONDUCTOR effect where zeros repel from the central point
in families with functional-equation sign constraints. Two decisive tests:

  1. CONDUCTOR-WINDOW SCALING: bin 2M EC by conductor decade. If deficit SHRINKS with
     conductor → excised ensemble (known); if FLAT → genuine anomaly.
  2. EDGE vs BULK: compare first gap (z2-z1) to second gap (z3-z2). If deficit is ONLY
     in first gap → excised ensemble confirmed.

If both tests are excised-consistent, F011 tier changes from live_specimen to
calibration_confirmed (Duenez-HKMS asymptotic at finite N).

Data: prometheus_fire.zeros.object_zeros × lmfdb.public.ec_curvedata, n_zeros≥3.
Unfolding: catalog degree-2 formula.

Output: cartography/docs/wsw_F011_excised_ensemble_results.json
"""
import json
import os
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import stats

GUE_VAR = 0.178  # Wigner GUE first-gap variance (unfolded, asymptotic)
PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
MIN_STRATUM_N = 100


def connect(dbname):
    return psycopg2.connect(
        host=PG["host"], port=PG["port"], dbname=dbname,
        user=PG["user"], password=PG["password"], connect_timeout=10,
    )


def fetch_zeros():
    # Need z1, z2, z3 for edge-vs-bulk
    with connect("prometheus_fire") as c:
        return pd.read_sql("""
            SELECT lmfdb_label, conductor::bigint AS conductor,
                   zeros[1]::float8 AS z1,
                   zeros[2]::float8 AS z2,
                   zeros[3]::float8 AS z3,
                   n_zeros
              FROM zeros.object_zeros
             WHERE object_type = 'elliptic_curve'
               AND n_zeros >= 3
               AND zeros[1] > 0.0
               AND zeros[2] > zeros[1]
               AND zeros[3] > zeros[2]
        """, c)


def fetch_ec():
    with connect("lmfdb") as c:
        return pd.read_sql("""
            SELECT lmfdb_label, NULLIF(rank,'')::int AS rank
              FROM public.ec_curvedata
        """, c)


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def variance_stats(vals, name):
    vals = vals[np.isfinite(vals)]
    n = int(vals.size)
    if n < MIN_STRATUM_N:
        return {"name": name, "n": n, "included": False, "reason": f"n<{MIN_STRATUM_N}"}
    var = float(np.var(vals, ddof=1))
    mean = float(vals.mean())
    deficit = 100.0 * (GUE_VAR - var) / GUE_VAR
    # SE of variance under normal approx
    se_var = var * math.sqrt(2.0 / max(n - 1, 1))
    # z of observed variance vs GUE under null
    se_null = math.sqrt(2.0 * GUE_VAR * GUE_VAR / max(n - 1, 1))
    z = (var - GUE_VAR) / se_null
    return {"name": name, "n": n, "included": True,
            "var": var, "mean_gap": mean,
            "deficit_pct": deficit, "se_var": se_var, "z_vs_gue": float(z)}


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[excised] start {started}")

    df_z = fetch_zeros()
    df_e = fetch_ec()
    df = df_z.merge(df_e, on="lmfdb_label", how="inner").dropna(subset=["rank"])
    df["rank"] = df["rank"].astype(int)
    print(f"[fetch] merged n={len(df)} (z1,z2,z3 available)")

    conductor = df["conductor"].to_numpy(float)
    z1u = unfold(df["z1"].to_numpy(float), conductor)
    z2u = unfold(df["z2"].to_numpy(float), conductor)
    z3u = unfold(df["z3"].to_numpy(float), conductor)
    df["gap1"] = z2u - z1u  # first gap (edge, adjacent to central zero)
    df["gap2"] = z3u - z2u  # second gap (bulk proxy, one step in)

    ok = (np.isfinite(df["gap1"]) & (df["gap1"] > 0) &
          np.isfinite(df["gap2"]) & (df["gap2"] > 0))
    df = df.loc[ok].copy()
    print(f"[unfold] {len(df)} rows with positive gap1 and gap2")

    # ---------------- Test 1: conductor-window scaling ----------------
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    # Decade bins over observed log_cond range
    q = np.quantile(df["log_cond"], np.linspace(0, 1, 11))
    q[0] -= 1e-9; q[-1] += 1e-9
    df["cond_bin"] = np.digitize(df["log_cond"], q[1:-1])
    bin_edges = [(float(q[i]), float(q[i+1])) for i in range(len(q)-1)]

    per_bin_gap1 = []
    per_bin_gap2 = []
    for b in sorted(df["cond_bin"].unique()):
        sub = df.loc[df["cond_bin"] == b]
        s1 = variance_stats(sub["gap1"].to_numpy(float), f"bin{b}_gap1")
        s2 = variance_stats(sub["gap2"].to_numpy(float), f"bin{b}_gap2")
        s1["bin"] = int(b); s1["log_cond_range"] = bin_edges[int(b)]
        s2["bin"] = int(b); s2["log_cond_range"] = bin_edges[int(b)]
        s1["mean_log_cond"] = float(sub["log_cond"].mean())
        s2["mean_log_cond"] = float(sub["log_cond"].mean())
        per_bin_gap1.append(s1)
        per_bin_gap2.append(s2)
        if s1["included"]:
            print(f"[bin{b}] log_cond={s1['mean_log_cond']:.2f}  n={s1['n']:>6}  "
                  f"gap1_def={s1['deficit_pct']:5.2f}%  gap2_def={s2['deficit_pct']:5.2f}%")

    # Slope of gap1 deficit vs mean_log_cond (weighted by per-bin SE)
    bins_ok = [b for b in per_bin_gap1 if b["included"]]
    if len(bins_ok) >= 3:
        x = np.array([b["mean_log_cond"] for b in bins_ok])
        y1 = np.array([b["deficit_pct"] for b in bins_ok])
        se1 = np.array([100.0 * b["se_var"] / GUE_VAR for b in bins_ok])
        w = 1.0 / (se1 ** 2)
        xw = (w * x).sum() / w.sum()
        yw = (w * y1).sum() / w.sum()
        num = (w * (x - xw) * (y1 - yw)).sum()
        den = (w * (x - xw) ** 2).sum()
        slope_gap1 = num / den if den > 0 else None
        # SE of slope via residuals
        if slope_gap1 is not None:
            resid = y1 - (slope_gap1 * x + (yw - slope_gap1 * xw))
            chi2 = (w * resid ** 2).sum()
            dof = max(len(bins_ok) - 2, 1)
            se_slope_gap1 = math.sqrt(chi2 / (dof * den)) if den > 0 else None
            z_slope_gap1 = slope_gap1 / se_slope_gap1 if se_slope_gap1 else None
        else:
            se_slope_gap1 = z_slope_gap1 = None
    else:
        slope_gap1 = se_slope_gap1 = z_slope_gap1 = None

    # ---------------- Test 2: edge vs bulk (pooled) ----------------
    pooled_gap1 = variance_stats(df["gap1"].to_numpy(float), "pooled_gap1")
    pooled_gap2 = variance_stats(df["gap2"].to_numpy(float), "pooled_gap2")

    edge_vs_bulk_ratio = None
    edge_vs_bulk_z = None
    if pooled_gap1["included"] and pooled_gap2["included"]:
        # Is gap2 closer to GUE than gap1? (Predicted by excised ensemble.)
        # Compare |deficit_gap1| vs |deficit_gap2|
        d1 = pooled_gap1["deficit_pct"]
        d2 = pooled_gap2["deficit_pct"]
        edge_vs_bulk_ratio = d1 / d2 if d2 != 0 else None
        # z of (d1 - d2): their SEs (in deficit_pct units)
        se_d1 = 100.0 * pooled_gap1["se_var"] / GUE_VAR
        se_d2 = 100.0 * pooled_gap2["se_var"] / GUE_VAR
        se_diff = math.sqrt(se_d1 ** 2 + se_d2 ** 2)
        edge_vs_bulk_z = (d1 - d2) / se_diff if se_diff > 0 else None
        print(f"[pooled]  gap1 n={pooled_gap1['n']}  def={d1:.2f}%  "
              f"gap2 n={pooled_gap2['n']}  def={d2:.2f}%  "
              f"ratio={edge_vs_bulk_ratio:.2f}  z(d1-d2)={edge_vs_bulk_z:.2f}")

    # ---------------- Verdict ----------------
    # Excised ensemble predicts:
    #   (A) slope_gap1 vs log_cond: POSITIVE (deficit shrinks = deficit_pct increases
    #       toward 0 from below... but deficit_pct as I define it is (GUE - var)/GUE,
    #       so if deficit SHRINKS, deficit_pct DECREASES. So slope should be NEGATIVE.
    #       More precisely: var → GUE_VAR as conductor → inf, so (GUE - var) → 0 from above,
    #       so deficit_pct → 0 from positive. Slope vs log_cond should be NEGATIVE.
    #   (B) d1 > d2: first-gap deficit is LARGER than second-gap deficit (z > 0).
    #
    # Anomaly predicts:
    #   (A) slope flat (z < 3σ).
    #   (B) d1 ≈ d2 (z < 3σ).

    verdict_conductor_scaling = None
    if z_slope_gap1 is not None:
        if slope_gap1 < 0 and abs(z_slope_gap1) >= 3.0:
            verdict_conductor_scaling = "EXCISED_CONSISTENT_shrinks_with_conductor"
        elif slope_gap1 > 0 and abs(z_slope_gap1) >= 3.0:
            verdict_conductor_scaling = "ANOMALY_grows_with_conductor"
        elif abs(z_slope_gap1) < 3.0:
            verdict_conductor_scaling = "FLAT_across_conductor"
        else:
            verdict_conductor_scaling = "AMBIGUOUS"

    verdict_edge_vs_bulk = None
    if edge_vs_bulk_z is not None:
        if edge_vs_bulk_z >= 3.0:
            verdict_edge_vs_bulk = "EXCISED_CONSISTENT_first_gap_heavier"
        elif edge_vs_bulk_z <= -3.0:
            verdict_edge_vs_bulk = "INVERTED_second_gap_heavier"
        else:
            verdict_edge_vs_bulk = "GAPS_SIMILAR"

    # Overall
    excised_confirmed = (
        verdict_conductor_scaling == "EXCISED_CONSISTENT_shrinks_with_conductor" and
        verdict_edge_vs_bulk == "EXCISED_CONSISTENT_first_gap_heavier"
    )
    if excised_confirmed:
        overall = "EXCISED_ENSEMBLE_CONFIRMED"
        reading = ("Both tests align with Duenez-Huynh-Keating-Miller-Snaith excised ensemble. "
                   "F011's ~38% first-gap deficit is a finite-conductor effect well-known in the "
                   "L-function RMT literature. TIER CHANGE CANDIDATE: live_specimen → calibration_confirmed. "
                   "Pattern 5 (Known Bridges Are Known) applies: this is a rediscovery of established theory, "
                   "not a novel anomaly.")
    elif verdict_conductor_scaling == "FLAT_across_conductor" and verdict_edge_vs_bulk == "GAPS_SIMILAR":
        overall = "GENUINE_ANOMALY"
        reading = ("Neither conductor-window scaling nor edge-vs-bulk supports the excised ensemble. "
                   "F011 is NOT just finite-N / finite-conductor; something else is at play. "
                   "Tier retained at live_specimen; frontier for mechanism hypotheses beyond "
                   "central-zero-forcing.")
    else:
        overall = "MIXED_OR_PARTIAL"
        reading = (f"conductor_scaling={verdict_conductor_scaling}, edge_vs_bulk={verdict_edge_vs_bulk}. "
                   f"Partial evidence for excised ensemble but not both tests point the same way. "
                   f"Needs deeper investigation.")

    out = {
        "task": "Aporia Report 1 — F011 excised ensemble audit",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_data": int(len(df)),
        "n_conductor_bins": len(per_bin_gap1),
        "pooled_gap1": pooled_gap1,
        "pooled_gap2": pooled_gap2,
        "per_conductor_bin_gap1": per_bin_gap1,
        "per_conductor_bin_gap2": per_bin_gap2,
        "test_1_conductor_scaling": {
            "slope_gap1_deficit_vs_log_cond_per_decade": slope_gap1,
            "se_slope": se_slope_gap1,
            "z_slope": z_slope_gap1,
            "verdict": verdict_conductor_scaling,
            "interpretation_guide": "Excised ensemble predicts slope NEGATIVE (deficit shrinks as conductor grows). Anomaly predicts flat.",
        },
        "test_2_edge_vs_bulk": {
            "pooled_gap1_deficit_pct": pooled_gap1["deficit_pct"] if pooled_gap1["included"] else None,
            "pooled_gap2_deficit_pct": pooled_gap2["deficit_pct"] if pooled_gap2["included"] else None,
            "deficit_ratio_gap1_over_gap2": edge_vs_bulk_ratio,
            "z_difference": edge_vs_bulk_z,
            "verdict": verdict_edge_vs_bulk,
            "interpretation_guide": "Excised ensemble predicts gap1 deficit MUCH larger than gap2 (central zero repels only adjacent). Anomaly predicts gaps similar.",
        },
        "overall_verdict": overall,
        "reading": reading,
        "tier_change_candidate": "F011: live_specimen -> calibration_confirmed" if excised_confirmed else "F011: no tier change",
        "_meta": {
            "aporia_source": "aporia/docs/deep_research_batch1.md (Report 1)",
            "excised_ensemble_ref": "Duenez-Huynh-Keating-Miller-Snaith 2011; Forrester-Mays 2015; Chandee-Lee 2021",
            "gue_var_baseline": GUE_VAR,
            "unfolding_formula": "catalog degree-2 (gamma/2pi)(log(N*gamma^2/4pi^2)-2)",
            "notes": [
                "n_zeros>=3 filter drops curves with only 2 zeros logged; expect reduction vs wsw_F011 baseline.",
                "gap2 = z3 - z2 is a 'bulk proxy' (second low-lying gap). True bulk needs zeros at index ~100+.",
                "Conductor bins are 10 deciles by log10(conductor); per-bin n is balanced.",
                "Pattern 5 gate: if excised confirmed, F011 becomes calibration_confirmed (known classical result).",
            ],
        },
    }

    out_path = os.path.join("cartography", "docs", "wsw_F011_excised_ensemble_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[excised] wrote {out_path}")
    print(f"[overall] {overall}")
    print(f"[reading] {reading}")


if __name__ == "__main__":
    main()
