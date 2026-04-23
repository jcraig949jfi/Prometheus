"""F013 addendum — non-degenerate Class-2 test.

The primary re-audit found that the F013 reformulated joint-shuffle test
is structurally degenerate (null_std=0) because the variance-based slope
statistic is invariant under joint (rank, cond_decile) shuffle.

This addendum runs a Class-2-appropriate test that is NOT invariant under
within-rank shuffle: per-rank OLS slope of individual-curve `value` vs
log_cond (not variance-aggregated; not decile-aggregated). Under within-
rank shuffle of `value`, per-rank slopes collapse to noise → cross-rank
slope-difference collapses. This is the canonical Class-2 test analogous
to F015's Class-3 pattern.

Updates cartography/docs/reaudit_10_stratifier_mismatch_results.{md,json}
in-place (appending a new 'f013_individual_slope_test' block and
replacing the 'recommended_tensor_action' verdicts).
"""
from __future__ import annotations
import io, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg2
from scipy import stats as sstats

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from harmonia.nulls import bswcd_null  # noqa: E402

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
PG_FIRE = dict(PG, dbname="prometheus_fire")
N_PERMS = 300
SEED = 20260417
OUTDIR = Path("cartography/docs")


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def fetch_base():
    with psycopg2.connect(**PG_FIRE) as c:
        dfz = pd.read_sql(
            "SELECT lmfdb_label, conductor::float8 AS conductor, "
            "zeros[1]::float8 AS z1, zeros[2]::float8 AS z2 "
            "FROM zeros.object_zeros WHERE object_type='elliptic_curve' "
            "AND n_zeros>=2 AND zeros[1]>0.0 AND zeros[2]>zeros[1]", c)
    with psycopg2.connect(**PG) as c:
        dfe = pd.read_sql(
            "SELECT lmfdb_label, NULLIF(rank,'')::int AS rank "
            "FROM public.ec_curvedata", c)
    df = dfz.merge(dfe, on="lmfdb_label", how="inner")
    df["gap1_unfolded"] = unfold(df["z1"].values, df["conductor"].values).astype(float)
    df["gap1_unfolded"] = unfold(df["z2"].values, df["conductor"].values) - df["gap1_unfolded"]
    df = df.loc[np.isfinite(df["gap1_unfolded"]) & (df["gap1_unfolded"] > 0)].copy()
    df = df.dropna(subset=["rank"]).copy()
    df["rank"] = df["rank"].astype(int)
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    df["value"] = df["gap1_unfolded"]
    df["rank_bin"] = df["rank"].clip(upper=3)  # {0,1,2,3+}
    return df.reset_index(drop=True)


def per_rank_slope_diff_stat(df: pd.DataFrame) -> float:
    """Statistic: slope(rank=0) − slope(rank>=1) of individual-curve value
    vs log_cond. Non-aggregated, so NOT invariant under within-rank shuffle.
    """
    sub0 = df[df["rank_bin"] == 0]
    sub1 = df[df["rank_bin"] >= 1]
    if len(sub0) < 500 or len(sub1) < 500:
        return 0.0
    s0, _, _, _, _ = sstats.linregress(
        sub0["log_cond"].values.astype(float),
        sub0["value"].values.astype(float))
    s1, _, _, _, _ = sstats.linregress(
        sub1["log_cond"].values.astype(float),
        sub1["value"].values.astype(float))
    return float(s0 - s1)


def parity_slope_diff_stat(df: pd.DataFrame) -> float:
    """Statistic: slope(SO_even = even rank) − slope(SO_odd = odd rank)
    of individual-curve value vs log_cond. For P028/P036-like projections
    where rank parity aliases the semantic axis on EC.
    """
    df2 = df.copy()
    df2["rank_parity"] = (df2["rank"] % 2).astype(int)
    sub_e = df2[df2["rank_parity"] == 0]
    sub_o = df2[df2["rank_parity"] == 1]
    if len(sub_e) < 500 or len(sub_o) < 500:
        return 0.0
    s_e, _, _, _, _ = sstats.linregress(
        sub_e["log_cond"].values.astype(float),
        sub_e["value"].values.astype(float))
    s_o, _, _, _, _ = sstats.linregress(
        sub_o["log_cond"].values.astype(float),
        sub_o["value"].values.astype(float))
    return float(s_e - s_o)


def main():
    print(f"[f013_addendum] start {datetime.now(timezone.utc).isoformat()}")
    df = fetch_base()
    print(f"[data] n={len(df):,} rank_bin dist={dict(df['rank_bin'].value_counts().sort_index())}")

    results = {}

    # (C1) rank_bin stratifier, slope(rank=0) - slope(rank>=1)
    print("\n[C1] rank_bin stratifier, individual-curve slope(rank=0) - slope(rank>=1)")
    obs = per_rank_slope_diff_stat(df)
    print(f"  observed = {obs:.6f}")
    r = bswcd_null(df.copy(), stratifier="rank_bin", n_bins=4,
                   n_perms=N_PERMS, seed=SEED,
                   statistic=per_rank_slope_diff_stat)
    print(f"  null_mean={r['null_mean']:.6g} null_std={r['null_std']:.3e} z={r['z_score']} → {r['verdict']}")
    results["rank_bin_slope_diff"] = dict(r)

    # (C2) rank_parity stratifier, slope(SO_even) - slope(SO_odd) for P028/P036
    print("\n[C2] rank_parity stratifier, individual-curve slope(SO_even) - slope(SO_odd)")
    df2 = df.copy()
    df2["rank_parity"] = (df2["rank"] % 2).astype(int)
    obs2 = parity_slope_diff_stat(df2)
    print(f"  observed = {obs2:.6f}")
    r2 = bswcd_null(df2, stratifier="rank_parity", n_bins=2,
                    n_perms=N_PERMS, seed=SEED + 1,
                    statistic=parity_slope_diff_stat)
    print(f"  null_mean={r2['null_mean']:.6g} null_std={r2['null_std']:.3e} z={r2['z_score']} → {r2['verdict']}")
    results["rank_parity_slope_diff"] = dict(r2)

    out = OUTDIR / "reaudit_10_stratifier_mismatch_f013_addendum.json"
    out.write_text(json.dumps({
        "addendum": "F013 individual-curve slope-diff tests (Class-2, non-invariant under within-rank shuffle)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": int(len(df)),
        "tests": results,
    }, indent=2, default=str), encoding="utf-8")
    print(f"\n[f013_addendum] wrote {out}")
    return results


if __name__ == "__main__":
    main()
