"""Re-auditor — F013 three +1 cells under NULL_BSWCD@v1.

F013 = Zero spacing rigidity vs rank (H06). P028 prior audit gave
z_block=15.31 on the SO_even vs SO_odd slope-difference — the whole
question of 'does variance-vs-rank slope differ by Katz-Sarnak family'
is DURABLE on aggregate.

Cells at +1:
  F013 x P023  Rank stratification   → test slope-across-rank
  F013 x P041  F24 variance decomp    → test variance partition cleanliness
  F013 x P051  N(T) unfolding        → test slope using unfolded spacings

Method: per cell, compute statistic + run NULL_BSWCD@v1 with conductor.
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from harmonia.nulls import bswcd_null, bswcd_signature  # noqa: E402

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
PG_FIRE = dict(PG, dbname="prometheus_fire")

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


def fetch():
    with connect(PG_FIRE) as c:
        dfz = pd.read_sql(
            """SELECT lmfdb_label, conductor::float8 AS conductor,
                      zeros[1]::float8 AS z1, zeros[2]::float8 AS z2
                 FROM zeros.object_zeros
                WHERE object_type='elliptic_curve'
                  AND n_zeros >= 2 AND zeros[1] > 0.0 AND zeros[2] > zeros[1]""", c)
    with connect(PG) as c:
        dfe = pd.read_sql(
            """SELECT lmfdb_label,
                      NULLIF(rank,'')::int AS rank
                 FROM public.ec_curvedata""", c)
    df = dfz.merge(dfe, on="lmfdb_label", how="inner").dropna(subset=["rank"])
    df["rank"] = df["rank"].astype(int)
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1_unfolded"] = z2u - z1u
    df["gap1_raw"] = df["z2"] - df["z1"]
    df = df.loc[np.isfinite(df["gap1_unfolded"]) & (df["gap1_unfolded"] > 0)].copy()
    return df


def slope_var_vs_rank(df, value_col):
    """Statistic: slope of variance(gap) vs rank across ranks 0..3.

    Captures 'zero spacing rigidity increases/decreases with rank'. A
    real signal gives a nonzero slope; block-shuffle-within-conductor
    should randomise it if it's conductor-mediated."""
    sub = df.dropna(subset=["rank"])
    sub = sub[sub["rank"].isin([0, 1, 2, 3])]
    if len(sub) < 100:
        return 0.0
    var_by_rank = sub.groupby("rank")[value_col].var()
    if len(var_by_rank) < 3:
        return 0.0
    xs = np.array(var_by_rank.index, dtype=float)
    ys = np.array(var_by_rank.values, dtype=float)
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    return float(slope)


def slope_mean_vs_rank(df, value_col):
    """Slope of mean(gap) vs rank — complementary statistic for P023."""
    sub = df.dropna(subset=["rank"])
    sub = sub[sub["rank"].isin([0, 1, 2, 3])]
    if len(sub) < 100:
        return 0.0
    m_by_rank = sub.groupby("rank")[value_col].mean()
    if len(m_by_rank) < 3:
        return 0.0
    xs = np.array(m_by_rank.index, dtype=float)
    ys = np.array(m_by_rank.values, dtype=float)
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    return float(slope)


def variance_decomp_clarity(df, value_col):
    """F24 projection P041: how cleanly does variance decompose by rank?

    Ratio of between-rank SS to total SS (eta^2). If rank truly explains
    structure, eta^2 is substantial. Block-shuffle-within-conductor
    destroys any rank-specific differentiation; eta^2 should drop.
    """
    sub = df.dropna(subset=["rank"])
    sub = sub[sub["rank"].isin([0, 1, 2, 3])]
    if len(sub) < 100:
        return 0.0
    overall = sub[value_col].mean()
    group_means = sub.groupby("rank")[value_col].agg(["mean", "count"])
    ss_between = float(((group_means["mean"] - overall) ** 2 * group_means["count"]).sum())
    ss_total = float(((sub[value_col] - overall) ** 2).sum())
    return ss_between / ss_total if ss_total > 1e-12 else 0.0


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
    print(f"[reaudit_F013] start {started}")

    df = fetch()
    print(f"[data] n={len(df)}")

    commit = commit_short()
    cells = {
        "P023": ("slope_mean_vs_rank on gap1_unfolded",
                 lambda d: slope_mean_vs_rank(d, "value"),
                 "gap1_unfolded"),
        "P041": ("eta2_variance_decomp on gap1_unfolded",
                 lambda d: variance_decomp_clarity(d, "value"),
                 "gap1_unfolded"),
        "P051": ("slope_var_vs_rank on gap1_unfolded (N(T) unfolding)",
                 lambda d: slope_var_vs_rank(d, "value"),
                 "gap1_unfolded"),
    }

    results = {}
    for p_id, (desc, stat, value_col) in cells.items():
        print(f"\n[F013 x {p_id}] {desc}")
        d = df.copy()
        d["value"] = d[value_col]
        observed_stat = stat(d)
        print(f"  observed stat = {observed_stat:+.6f}")
        r = bswcd_null(d, stratifier="conductor",
                       n_bins=N_BINS, n_perms=N_PERMS, seed=SEED,
                       statistic=stat)
        print(f"  z={r['z_score']:.2f} verdict={r['verdict']} "
              f"null_mean={r['null_mean']:+.6f} null_std={r['null_std']:.6f}")
        sig = bswcd_signature(
            feature_id=f"F013@{commit}",
            projection_ids=[f"{p_id}@{commit}"],
            result=r,
            n_samples=len(d),
            dataset_spec="Q_EC@lmfdb.ec_curvedata join prometheus_fire.zeros.object_zeros",
            commit=commit,
            worker=WORKER,
            timestamp=datetime.now(timezone.utc).isoformat(),
            effect_size=observed_stat,
        )
        sig_path = SIG_DIR / f"SIG_F013_{p_id}.json"
        sig_path.write_text(json.dumps(sig, indent=2, default=str), encoding="utf-8")
        results[p_id] = {
            "bswcd": r,
            "description": desc,
            "recommended_verdict": "+2" if r["verdict"] == "DURABLE" else "-1",
            "signature_path": str(sig_path),
        }

    report = {
        "task": "reaudit_F013_3cells",
        "operator": "NULL_BSWCD@v1",
        "worker": WORKER,
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "n_samples": len(df),
        "cells": results,
        "tensor_diff": {
            f"F013:{p_id}": {
                "from": 1,
                "to": 2 if res["bswcd"]["verdict"] == "DURABLE" else -1,
                "z_block": res["bswcd"]["z_score"],
            }
            for p_id, res in results.items()
        },
    }
    out = OUTDIR / "reaudit_F013_3cells_results.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n[reaudit_F013] wrote {out}")

    print("\n=== SUMMARY ===")
    for p_id, res in results.items():
        print(f"  F013:{p_id}: z={res['bswcd']['z_score']:+.2f} "
              f"-> {res['bswcd']['verdict']} -> {res['recommended_verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
