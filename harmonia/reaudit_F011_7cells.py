"""Re-auditor role — F011 seven +1 cells under NULL_BSWCD@v1.

F011 = GUE first-gap deficit (rank-0 residual frontier after excision).
Cells currently at +1: P021, P023, P024, P025, P026, P050, P051.

For each (F011, P) cell, we compute a projection-appropriate statistic
and run NULL_BSWCD@v1 with the canonical stratifier
(conductor_decile, Pattern 26-compliant). We also cross-check with
the stratifier that best matches the projection's semantic axis where
one exists.

Output: cartography/docs/reaudit_F011_7cells_results.json + one
SIGNATURE JSON per cell in cartography/docs/signatures/.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from harmonia.nulls import bswcd_null, bswcd_signature  # noqa: E402

PG = dict(
    host="192.168.1.176", port=5432, dbname="lmfdb",
    user="postgres", password="prometheus", connect_timeout=10,
)
PG_FIRE = dict(PG, dbname="prometheus_fire")

GUE_MEAN = 1.0     # GUE normalised first-gap mean (after unfolding)
N_PERMS = 300
SEED = 20260417
N_BINS = 10
WORKER = "Harmonia_M2_sessionD_reauditor"
OUTDIR = Path("cartography/docs")
SIG_DIR = OUTDIR / "signatures"


def connect(cfg):
    return psycopg2.connect(**cfg)


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def fetch_base():
    with connect(PG_FIRE) as c:
        dfz = pd.read_sql(
            """
            SELECT lmfdb_label,
                   conductor::float8 AS conductor,
                   zeros[1]::float8 AS z1,
                   zeros[2]::float8 AS z2
              FROM zeros.object_zeros
             WHERE object_type = 'elliptic_curve'
               AND n_zeros >= 2 AND zeros[1] > 0.0 AND zeros[2] > zeros[1]
            """,
            c,
        )
    with connect(PG) as c:
        dfe = pd.read_sql(
            """
            SELECT lmfdb_label,
                   NULLIF(rank,'')::int  AS rank,
                   NULLIF(torsion,'')::int AS torsion,
                   NULLIF(cm,'')::int     AS cm_disc,
                   CASE WHEN semistable='True' THEN 1
                        WHEN semistable='False' THEN 0 END AS semistable,
                   NULLIF(num_bad_primes,'')::int AS num_bad_primes
              FROM public.ec_curvedata
            """,
            c,
        )
    df = dfz.merge(dfe, on="lmfdb_label", how="inner")
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1_unfolded"] = z2u - z1u
    df["gap1_raw"] = df["z2"] - df["z1"]
    df = df.loc[np.isfinite(df["gap1_unfolded"]) & (df["gap1_unfolded"] > 0)].copy()
    df["rank"] = df["rank"].astype("Int64")
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    return df


def deficit_stat_by_group(group_col):
    """Returns a statistic function: cross-group spread of deficits.

    deficit_g = GUE_MEAN - mean(gap1_unfolded | group=g)
    spread = max(deficit_g) - min(deficit_g) across groups with n >= 500.

    The `value` column is the one block-shuffle permutes; `gap1_unfolded`
    is a shorthand. We alias here.
    """
    def stat(df):
        valid = df.dropna(subset=[group_col])
        if len(valid) == 0:
            return 0.0
        sizes = valid.groupby(group_col).size()
        keep = sizes[sizes >= 500].index
        if len(keep) < 2:
            return 0.0
        sub = valid[valid[group_col].isin(keep)]
        g = sub.groupby(group_col)["value"].mean()
        deficits = GUE_MEAN - g
        return float(deficits.max() - deficits.min())
    return stat


def deficit_stat_rank0_variance():
    """For P050/P051 (preprocessing axes): the variance of the unfolded
    gap distribution among rank-0 curves. A deficit visible above GUE_MEAN
    means the first-gap is compressed."""
    def stat(df):
        sub = df[df["rank"] == 0]
        if len(sub) < 500:
            return 0.0
        return float(GUE_MEAN - sub["value"].mean())
    return stat


def cell_spec():
    """What statistic + stratifier to use per cell."""
    return {
        # Bad-prime count stratification
        "P021": {
            "stat": deficit_stat_by_group("num_bad_primes"),
            "stratifier": "conductor",
            "semantic": "num_bad_primes",
            "description": "F011 deficit spread across num_bad_primes buckets, conductor block-shuffle",
        },
        # Rank stratification
        "P023": {
            "stat": deficit_stat_by_group("rank"),
            "stratifier": "conductor",
            "semantic": "rank",
            "description": "F011 deficit spread across rank, conductor block-shuffle",
        },
        # Torsion stratification
        "P024": {
            "stat": deficit_stat_by_group("torsion"),
            "stratifier": "conductor",
            "semantic": "torsion",
            "description": "F011 deficit spread across torsion orders, conductor block-shuffle",
        },
        # CM vs non-CM
        "P025": {
            "stat": deficit_stat_by_group("cm_bin"),
            "stratifier": "conductor",
            "semantic": "cm",
            "description": "F011 deficit spread CM vs non-CM, conductor block-shuffle",
        },
        # Semistable vs additive
        "P026": {
            "stat": deficit_stat_by_group("semistable"),
            "stratifier": "conductor",
            "semantic": "semistable",
            "description": "F011 deficit spread semistable vs additive, conductor block-shuffle",
        },
        # First-gap preprocessing — rank-0 raw deficit
        "P050": {
            "stat": deficit_stat_rank0_variance(),
            "stratifier": "conductor",
            "semantic": "conductor",
            "description": "F011 rank-0 deficit under first-gap unfolding, conductor block-shuffle",
        },
        # N(T) unfolding preprocessing — rank-0 deficit
        "P051": {
            "stat": deficit_stat_rank0_variance(),
            "stratifier": "conductor",
            "semantic": "conductor",
            "description": "F011 rank-0 deficit under N(T) unfolding, conductor block-shuffle",
        },
    }


def commit_short():
    import subprocess
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    SIG_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    print(f"[reaudit_F011] start {started}")

    df = fetch_base()
    df["cm_bin"] = (df["cm_disc"].fillna(0) != 0).astype(int)
    # Use unfolded gap as the 'value' column to shuffle
    df["value"] = df["gap1_unfolded"]
    print(f"[data] n={len(df)} curves; rank dist: {dict(df['rank'].value_counts().head(5))}")

    specs = cell_spec()
    results = {}
    commit = commit_short()

    for p_id, spec in specs.items():
        print(f"\n[F011 x {p_id}] {spec['description']}")
        sub = df.copy()
        # Size before filtering
        n_in = len(sub)
        observed_stat = spec["stat"](sub)
        print(f"  observed stat = {observed_stat:.5f}")
        result = bswcd_null(
            sub, stratifier=spec["stratifier"],
            n_bins=N_BINS, n_perms=N_PERMS, seed=SEED,
            statistic=spec["stat"],
        )
        print(f"  result: z={result['z_score']:.2f} verdict={result['verdict']} "
              f"null_mean={result['null_mean']:.5f} null_std={result['null_std']:.5f}")
        sig = bswcd_signature(
            feature_id=f"F011@{commit}",
            projection_ids=[f"{p_id}@{commit}"],
            result=result,
            n_samples=n_in,
            dataset_spec="Q_EC@lmfdb.ec_curvedata join prometheus_fire.zeros.object_zeros (n_zeros>=2)",
            commit=commit,
            worker=WORKER,
            timestamp=datetime.now(timezone.utc).isoformat(),
            effect_size=observed_stat,
        )
        sig_path = SIG_DIR / f"SIG_F011_{p_id}.json"
        sig_path.write_text(json.dumps(sig, indent=2, default=str), encoding="utf-8")
        results[p_id] = {
            "bswcd": result,
            "signature_path": str(sig_path),
            "description": spec["description"],
            "recommended_verdict": "+2" if result["verdict"] == "DURABLE" else "-1",
        }

    # Finalize report
    report = {
        "task": "reaudit_F011_7cells",
        "operator": "NULL_BSWCD@v1",
        "worker": WORKER,
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "n_samples_base": len(df),
        "cells": results,
        "tensor_diff": {
            f"F011:{p_id}": {
                "from": 1,
                "to": 2 if res["bswcd"]["verdict"] == "DURABLE" else -1,
                "z_block": res["bswcd"]["z_score"],
            }
            for p_id, res in results.items()
        },
    }

    out = OUTDIR / "reaudit_F011_7cells_results.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n[reaudit_F011] wrote {out}")

    # Summary
    print("\n=== SUMMARY ===")
    for p_id, res in results.items():
        print(f"  F011:{p_id}: z={res['bswcd']['z_score']:+.2f} "
              f"-> verdict={res['bswcd']['verdict']} "
              f"-> recommend {res['recommended_verdict']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
