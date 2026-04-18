"""audit_P028_block_shuffle.py — block-shuffle durability audit for F011 and F013 P028 findings.

Task: audit_P028_findings_block_shuffle (Harmonia_M2_sessionB, tick 20).

Context:
  F010 was retracted after sessionC's block-shuffle-within-degree null gave z=-0.86
  (plain permutation had endorsed the signal at z=2.38). That kill exposed: plain-permutation
  null over-rejects when there's a strong primary confound (in F010's case, NF degree).
  My P028 findings on F011 (5.4σ) and F013 (13.7σ) used plain permutation / Fisher-z
  comparisons. This audit tests whether they survive a stricter null.

Interpretation of "block-shuffle within rank cell":
  The primary confound for F011's symmetry-class deficit is the RANK-to-VARIANCE relationship
  (variance varies naturally with rank through the Katz-Sarnak central-zero-forcing effect,
  which is at different magnitudes at different ranks). However for F011, the deficit CLAIM
  is already a per-rank effect (SO_even pool = weighted over even ranks). The real confound
  to audit is CONDUCTOR: if the rank distribution is conductor-dependent and variance scales
  with conductor (via unfolding), the pooled deficit by symmetry could be a conductor-mediated
  ghost.

Design:
  - Partition curves into conductor deciles (10 bins by log10(conductor)).
  - Within each conductor decile, shuffle rank labels across curves. This preserves the
    conductor distribution of ranks per decile (intrinsic confound preserved) but destroys
    the within-decile rank-to-spacing pairing.
  - For each shuffle, recompute:
      F011: pooled SO_even vs SO_odd variance; deficit-spread.
      F013: per (rank, ks_class) cell variance; slope per class; slope difference.
  - 200 permutations (dominated by rank-label shuffle, fast).
  - Verdict per specimen:
      z_observed / null_std >= 3.0  → DURABLE under block null
      otherwise                     → JOINS_F010_ledger (plain-null over-rejection)

Output: cartography/docs/audit_P028_findings_block_shuffle_results.json
"""
import json
import os
import math
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import stats

GUE_VAR = 0.178
PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
MIN_STRATUM_N = 100
N_PERMS = 200
SEED = 20260417
N_CONDUCTOR_BINS = 10


def connect(dbname):
    return psycopg2.connect(
        host=PG["host"], port=PG["port"], dbname=dbname,
        user=PG["user"], password=PG["password"], connect_timeout=10,
    )


def load_data():
    with connect("prometheus_fire") as c:
        df_z = pd.read_sql("""
            SELECT lmfdb_label, conductor::bigint AS conductor,
                   zeros[1]::float8 AS z1, zeros[2]::float8 AS z2
              FROM zeros.object_zeros
             WHERE object_type = 'elliptic_curve'
               AND n_zeros >= 2 AND zeros[1] > 0.0 AND zeros[2] > zeros[1]
        """, c)
    with connect("lmfdb") as c:
        df_e = pd.read_sql("""
            SELECT lmfdb_label, NULLIF(rank,'')::int AS rank
              FROM public.ec_curvedata
        """, c)
    return df_z.merge(df_e, on="lmfdb_label", how="inner").dropna(subset=["rank"])


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[audit_P028] start {started}")

    df = load_data()
    df["rank"] = df["rank"].astype(int)
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap_unf"] = z2u - z1u
    df = df.loc[np.isfinite(df["gap_unf"]) & (df["gap_unf"] > 0)].copy()
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    # Conductor decile bins
    q = np.quantile(df["log_cond"].to_numpy(), np.linspace(0, 1, N_CONDUCTOR_BINS + 1))
    q[0] -= 1e-9
    q[-1] += 1e-9
    df["cond_bin"] = np.digitize(df["log_cond"].to_numpy(), q[1:-1])
    df["ks_class"] = np.where(df["rank"] % 2 == 0, "SO_even", "SO_odd")
    print(f"[data] {len(df)} rows across {N_CONDUCTOR_BINS} conductor deciles")
    print(f"[cond_bin dist] {df['cond_bin'].value_counts().sort_index().to_dict()}")

    # --- Observed statistics -------------------------------------------------
    # F011: SO_even var, SO_odd var, deficit_spread_pct
    even_vals = df.loc[df["ks_class"] == "SO_even", "gap_unf"].to_numpy(float)
    odd_vals = df.loc[df["ks_class"] == "SO_odd", "gap_unf"].to_numpy(float)
    obs_var_even = float(np.var(even_vals, ddof=1))
    obs_var_odd = float(np.var(odd_vals, ddof=1))
    obs_deficit_even = 100.0 * (GUE_VAR - obs_var_even) / GUE_VAR
    obs_deficit_odd = 100.0 * (GUE_VAR - obs_var_odd) / GUE_VAR
    obs_f011_spread = abs(obs_deficit_even - obs_deficit_odd)
    print(f"[F011 observed] SO_even var={obs_var_even:.4f}  SO_odd var={obs_var_odd:.4f}  "
          f"spread={obs_f011_spread:.2f}%")

    # F013: per (rank, ks_class) cell → slope per class → slope diff
    def compute_f013_slope_diff(df_local):
        per_cell = []
        for (rk, ks), g in df_local.groupby(["rank", "ks_class"]):
            vals = g["gap_unf"].to_numpy(float)
            n = vals.size
            if n < MIN_STRATUM_N:
                continue
            var = float(np.var(vals, ddof=1))
            se_var = var * math.sqrt(2.0 / max(n - 1, 1))
            per_cell.append((int(rk), ks, n, var, se_var))

        def pair_slope(cells):
            cells = sorted(cells, key=lambda c: c[0])
            if len(cells) < 2:
                return None, None
            # For pair: slope = (var_high - var_low) / (rank_high - rank_low)
            r0, _, n0, v0, se0 = cells[0]
            r1, _, n1, v1, se1 = cells[-1]
            dx = r1 - r0
            if dx == 0:
                return None, None
            slope = (v1 - v0) / dx
            se = math.sqrt(se0 ** 2 + se1 ** 2) / abs(dx)
            return slope, se

        even_cells = [c for c in per_cell if c[1] == "SO_even"]
        odd_cells = [c for c in per_cell if c[1] == "SO_odd"]
        slope_e, se_e = pair_slope(even_cells)
        slope_o, se_o = pair_slope(odd_cells)
        if slope_e is None or slope_o is None or se_e is None or se_o is None:
            return None, None, None
        diff = slope_e - slope_o
        se_diff = math.sqrt(se_e ** 2 + se_o ** 2)
        z = diff / se_diff if se_diff > 0 else None
        return slope_e, slope_o, z

    obs_slope_e, obs_slope_o, obs_f013_z = compute_f013_slope_diff(df)
    print(f"[F013 observed] slope_SO_even={obs_slope_e:.5f}  slope_SO_odd={obs_slope_o:.5f}  "
          f"z_diff={obs_f013_z:.2f}")

    # --- Block-shuffle null --------------------------------------------------
    # Within each conductor bin, shuffle rank labels across curves.
    # Recompute ks_class (= rank % 2) after shuffling.
    rng = np.random.default_rng(SEED)
    f011_null_spread = np.empty(N_PERMS, dtype=np.float64)
    f013_null_z = np.empty(N_PERMS, dtype=np.float64)

    # Precompute index arrays per conductor bin for fast shuffling
    bin_indices = [df.index[df["cond_bin"] == b].to_numpy() for b in range(N_CONDUCTOR_BINS)]
    rank_orig = df["rank"].to_numpy()
    shuffled_rank = rank_orig.copy()

    for p in range(N_PERMS):
        # Shuffle rank labels within each conductor bin
        for idxs in bin_indices:
            perm = rng.permutation(idxs)
            shuffled_rank[idxs] = rank_orig[perm]
        df_p = df.copy()
        df_p["rank"] = shuffled_rank
        df_p["ks_class"] = np.where(df_p["rank"] % 2 == 0, "SO_even", "SO_odd")

        # F011 null stat
        e = df_p.loc[df_p["ks_class"] == "SO_even", "gap_unf"].to_numpy(float)
        o = df_p.loc[df_p["ks_class"] == "SO_odd", "gap_unf"].to_numpy(float)
        v_e = float(np.var(e, ddof=1)) if e.size > 1 else 0.0
        v_o = float(np.var(o, ddof=1)) if o.size > 1 else 0.0
        d_e = 100.0 * (GUE_VAR - v_e) / GUE_VAR
        d_o = 100.0 * (GUE_VAR - v_o) / GUE_VAR
        f011_null_spread[p] = abs(d_e - d_o)

        # F013 null stat
        _, _, z_p = compute_f013_slope_diff(df_p)
        f013_null_z[p] = float(z_p) if z_p is not None else 0.0

        if (p + 1) % 25 == 0:
            print(f"[perm {p+1}/{N_PERMS}] f011_spread null p99 so far: {np.percentile(f011_null_spread[:p+1], 99):.2f}%")

    # --- Verdicts -----------------------------------------------------------
    def z_vs_null(obs, null_arr):
        mean = float(null_arr.mean())
        std = float(null_arr.std())
        z = (obs - mean) / std if std > 0 else None
        p99 = float(np.percentile(null_arr, 99))
        return {"observed": float(obs), "null_mean": mean, "null_std": std,
                "null_p99": p99, "z_under_block_null": z}

    f011_audit = z_vs_null(obs_f011_spread, f011_null_spread)
    f013_audit = z_vs_null(obs_f013_z, f013_null_z)
    print(f"[F011 audit] obs={obs_f011_spread:.2f}%  null_p99={f011_audit['null_p99']:.2f}%  "
          f"z_block={f011_audit['z_under_block_null']:.2f}")
    print(f"[F013 audit] obs={obs_f013_z:.2f}  null_p99={f013_audit['null_p99']:.2f}  "
          f"z_block={f013_audit['z_under_block_null']:.2f}")

    def verdict(z):
        if z is None:
            return "INCONCLUSIVE"
        return "DURABLE_UNDER_BLOCK_NULL" if abs(z) >= 3.0 else "JOINS_F010_LEDGER"

    f011_verdict = verdict(f011_audit["z_under_block_null"])
    f013_verdict = verdict(f013_audit["z_under_block_null"])

    out = {
        "task": "audit_P028_findings_block_shuffle",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_data": int(len(df)),
        "n_conductor_bins": N_CONDUCTOR_BINS,
        "n_perms": N_PERMS,
        "seed": SEED,
        "design": ("Block-shuffle rank labels within conductor deciles; recompute per-symmetry-class "
                   "statistics each permutation. Preserves conductor distribution of ranks; "
                   "destroys within-decile rank-to-spacing pairing."),
        "F011_audit": {
            "observed_deficit_spread_pct": f011_audit["observed"],
            "block_null": f011_audit,
            "verdict": f011_verdict,
            "prior_plain_null_z": 5.38,
        },
        "F013_audit": {
            "observed_slope_diff_z": f013_audit["observed"],
            "slope_SO_even_observed": obs_slope_e,
            "slope_SO_odd_observed": obs_slope_o,
            "block_null": f013_audit,
            "verdict": f013_verdict,
            "prior_plain_null_z": 13.68,
        },
        "ledger_update": ("F011 / F013 prior verdicts used plain permutation / Fisher-z SE. Block-"
                          "shuffle-within-conductor-decile is the F010-adapted null. Whichever "
                          "specimens survive at z>=3.0 under block null carry a DURABLE tag; "
                          "others join F010 in the plain-null-over-rejection ledger."),
        "notes": [
            "If F011 spread survives block null, SO_even/SO_odd deficit difference is NOT conductor-mediated.",
            "If F013 slope-difference survives block null, the sign flip is NOT conductor-mediated.",
            "Methodology generalization: block-shuffle-within-primary-confound should be the default null for all wsw_* tasks per sessionA CONDUCTOR_TICK 34.",
        ],
    }

    out_path = os.path.join("cartography", "docs", "audit_P028_findings_block_shuffle_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[audit_P028] wrote {out_path}")
    print(f"[F011 verdict] {f011_verdict}")
    print(f"[F013 verdict] {f013_verdict}")


if __name__ == "__main__":
    main()
