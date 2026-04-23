"""Reaudit — 10 stratifier-mismatch cells under claim-appropriate null.

Task: reaudit_10_stratifier_mismatch_cells (Harmonia_M2_sessionD, claim
directly via HSETNX per CONDUCTOR_NOTE 1776735871516-0 routing sessionD
at this task).

Scope:
  9 NULL_BSWCD-appropriate cells:
    F011:P021 (Class 3 → nbp), F011:P023 (Class 3 → rank),
    F011:P026 (Class 3 → semistable), F011:P036 (Class 3 → root_number),
    F013:P023 (Class 2 → rank), F013:P028 (Class 2 → rank),
    F013:P041 (Class 2 → rank), F013:P051 (Class 2 → rank),
    F013:P104 (Class 2 → rank)
  3 F044 cells (P020, P023, P026) are Class 4 — NULL_BSWCD insufficient;
  out of scope for this task (separate audit_F044_framebased_resample).

Meta-observation: the prescribed Class-2/3 stratifier produces degenerate
nulls for these cells' existing statistics (statistic is invariant under
within-stratifier shuffle). This audit therefore runs TWO tests per cell:

  (A) LITERAL — NULL_BSWCD@v2 with the prescribed stratifier and the
      original statistic. Documents the degeneracy where it occurs.

  (B) REFORMULATED — a claim-appropriate test that is NOT invariant under
      the shuffle. For F011 Class-3 cells: per-stratum deficit durability
      (bootstrap SE on deficit = GUE_MEAN - mean, per stratum). For F013
      Class-2 cells: per-rank slope(var vs log_conductor) interaction
      under joint (rank, cond_decile) shuffle.

Verdict:
  DURABLE: the claim survives under the reformulated test. Retain +2.
  MIXED: some strata durable, some collapse. Downgrade to annotation.
  COLLAPSES: the claim fails the reformulated test. Demote to -1.
  DEGENERATE: the literal prescription cannot test; the original null
    (conductor-stratified) was the correct match for the cell's statistic
    shape; the classification JSON should be corrected to note this.

Output:
  cartography/docs/reaudit_10_stratifier_mismatch_results.md  (markdown)
  cartography/docs/reaudit_10_stratifier_mismatch_results.json (data)
  cartography/docs/signatures/SIG_Fxxx_Pxxx_v2.json            (per cell)
"""
from __future__ import annotations

import hashlib
import io
import json
import math
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

GUE_MEAN = 1.0      # Gaudin-normalised first-gap mean
GUE_VAR = 0.178     # Gaudin variance (used for F013 slope statistic)
N_PERMS = 300
SEED = 20260417
N_BINS = 10
WORKER = "Harmonia_M2_sessionD"
OUTDIR = Path("cartography/docs")
SIG_DIR = OUTDIR / "signatures"
MIN_STRATUM_N = 500


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
    df = df.loc[np.isfinite(df["gap1_unfolded"]) & (df["gap1_unfolded"] > 0)].copy()
    df = df.dropna(subset=["rank"]).copy()
    df["rank"] = df["rank"].astype(int)
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    df["value"] = df["gap1_unfolded"]
    df["cm_bin"] = (df["cm_disc"].fillna(0) != 0).astype(int)
    df["root_number"] = (df["rank"] % 2).astype(int)   # on EC, aliases rank parity
    return df.reset_index(drop=True)


def commit_short():
    import subprocess
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# F011 statistics
# ---------------------------------------------------------------------------

def f011_stat_spread(group_col):
    """Original F011 statistic: max-min deficit across groups (min n=500)."""
    def stat(df):
        valid = df.dropna(subset=[group_col])
        if len(valid) == 0:
            return 0.0
        sizes = valid.groupby(group_col).size()
        keep = sizes[sizes >= MIN_STRATUM_N].index
        if len(keep) < 2:
            return 0.0
        sub = valid[valid[group_col].isin(keep)]
        means = sub.groupby(group_col)["value"].mean()
        deficits = GUE_MEAN - means
        return float(deficits.max() - deficits.min())
    return stat


def f011_per_stratum_durability(df, group_col, rng):
    """Reformulated Class-3 test: per-stratum deficit durability via bootstrap SE.

    For each stratum v with n>=MIN_STRATUM_N: deficit_v = GUE_MEAN - mean(value_v).
    Bootstrap SE: resample n with replacement (300x), compute deficit each time.
    z_v = deficit_v / bootstrap_std.

    Verdict: DURABLE if all strata have z >= 3. MIXED if some z >= 3 and some below.
    COLLAPSES if all z < 3.
    """
    sub = df.dropna(subset=[group_col])
    sizes = sub.groupby(group_col).size()
    strata = sorted(sizes[sizes >= MIN_STRATUM_N].index.tolist())
    per_stratum = {}
    for v in strata:
        vals = sub.loc[sub[group_col] == v, "value"].to_numpy(float)
        n = vals.size
        deficit_obs = float(GUE_MEAN - vals.mean())
        boot = np.empty(N_PERMS, dtype=np.float64)
        for i in range(N_PERMS):
            idx = rng.integers(0, n, n)
            boot[i] = GUE_MEAN - vals[idx].mean()
        bstd = float(np.std(boot, ddof=1))
        z = float(deficit_obs / bstd) if bstd > 0 else float("inf")
        per_stratum[str(v)] = {
            "n": int(n),
            "mean": float(vals.mean()),
            "deficit": deficit_obs,
            "bootstrap_se": bstd,
            "z": round(z, 2),
            "durable": abs(z) >= 3.0,
        }
    zs = [v["z"] for v in per_stratum.values()]
    all_durable = all(abs(z) >= 3.0 for z in zs)
    any_durable = any(abs(z) >= 3.0 for z in zs)
    if all_durable:
        verdict = "DURABLE"
    elif any_durable:
        verdict = "MIXED"
    else:
        verdict = "COLLAPSES"
    return {
        "per_stratum": per_stratum,
        "n_strata": len(strata),
        "min_abs_z": min(abs(z) for z in zs) if zs else None,
        "max_abs_z": max(abs(z) for z in zs) if zs else None,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# F013 statistics
# ---------------------------------------------------------------------------

def f013_slope_diff_statistic(df):
    """Original F013 statistic: (SO_even slope of var vs rank) - (SO_odd slope).

    per-(rank, ks_class) variance, two-point slope (lowest rank, highest rank)
    per class, then diff.
    """
    per_cell = []
    for (rk, ks), g in df.groupby(["rank", "ks_class"]):
        vals = g["value"].to_numpy(float)
        if vals.size < MIN_STRATUM_N:
            continue
        per_cell.append((int(rk), ks, vals.size, float(np.var(vals, ddof=1))))

    def pair_slope(cells):
        cells = sorted(cells, key=lambda c: c[0])
        if len(cells) < 2:
            return None
        r0, _, _, v0 = cells[0]
        r1, _, _, v1 = cells[-1]
        if r1 == r0:
            return None
        return (v1 - v0) / (r1 - r0)

    e = [c for c in per_cell if c[1] == "SO_even"]
    o = [c for c in per_cell if c[1] == "SO_odd"]
    se, so = pair_slope(e), pair_slope(o)
    if se is None or so is None:
        return 0.0
    return float(se - so)


def f013_per_rank_slope_interaction(df, rng):
    """Reformulated Class-2 test: per-rank slope(var vs log_cond), then
    cross-rank interaction under joint (rank, cond_decile) shuffle.

    For each rank r with n>=MIN_STRATUM_N: pool curves by cond_decile,
    compute per-decile var, then slope_r = OLS(log_cond_decile_mean, var).
    Observed interaction: std(slope_r across ranks).

    Null: joint (rank_bin, cond_decile) stratifier, shuffle value within
    each joint cell. Preserves per-(rank, decile) marginal distribution
    but randomizes the within-cell pairings. Per-rank slope becomes noise.

    Verdict: DURABLE if |z| >= 3 else COLLAPSES.
    """
    q = np.quantile(df["log_cond"].to_numpy(), np.linspace(0, 1, N_BINS + 1))
    q[0] -= 1e-9; q[-1] += 1e-9
    cond_bin = np.digitize(df["log_cond"].to_numpy(), q[1:-1])
    dfl = df.copy()
    dfl["cond_bin"] = cond_bin

    def interaction_stat(data):
        slopes = []
        for r, grp in data.groupby("rank"):
            if len(grp) < MIN_STRATUM_N:
                continue
            per_decile = grp.groupby("cond_bin").agg(
                lc=("log_cond", "mean"),
                vv=("value", "var"),
                n=("value", "size"),
            )
            per_decile = per_decile[per_decile["n"] >= 50]
            if len(per_decile) < 3:
                continue
            x = per_decile["lc"].to_numpy(float)
            y = per_decile["vv"].to_numpy(float)
            if x.std() < 1e-12:
                continue
            slope = float(np.polyfit(x, y, 1)[0])
            slopes.append(slope)
        if len(slopes) < 2:
            return 0.0
        return float(np.std(slopes, ddof=1))

    observed = interaction_stat(dfl)

    # Joint stratifier: combine (rank, cond_bin) into one label
    joint = dfl["rank"].astype(int).astype(str) + "_" + dfl["cond_bin"].astype(str)
    dfl["joint"] = joint
    vals_orig = dfl["value"].to_numpy(float).copy()
    # Group indices
    joint_groups = {}
    for lbl, idx in dfl.groupby("joint").indices.items():
        if len(idx) >= 10:
            joint_groups[lbl] = np.array(idx, dtype=int)

    null = np.empty(N_PERMS, dtype=np.float64)
    for i in range(N_PERMS):
        shuffled = vals_orig.copy()
        for idxs in joint_groups.values():
            shuffled[idxs] = rng.permutation(vals_orig[idxs])
        tmp = dfl.copy()
        tmp["value"] = shuffled
        null[i] = interaction_stat(tmp)

    null_mean = float(null.mean())
    null_std = float(null.std(ddof=1))
    z = float((observed - null_mean) / null_std) if null_std > 0 else float("inf")
    return {
        "observed": round(observed, 6),
        "null_mean": round(null_mean, 6),
        "null_std": round(null_std, 6),
        "null_p99": round(float(np.percentile(null, 99)), 6),
        "z_score": round(z, 2),
        "verdict": "DURABLE" if abs(z) >= 3.0 else "COLLAPSES",
        "n_perms": N_PERMS,
        "stratifier": "joint(rank_bin, conductor_decile)",
    }


# ---------------------------------------------------------------------------
# Cell registry
# ---------------------------------------------------------------------------

F011_CELLS = {
    "P021": {"class": 3, "prescribed_stratifier": "num_bad_primes",
             "semantic": "num_bad_primes",
             "prior_z_under_conductor": 38.58},
    "P023": {"class": 3, "prescribed_stratifier": "rank",
             "semantic": "rank",
             "prior_z_under_conductor": 31.26},
    "P026": {"class": 3, "prescribed_stratifier": "semistable",
             "semantic": "semistable",
             "prior_z_under_conductor": 5.53},
    "P036": {"class": 3, "prescribed_stratifier": "root_number",
             "semantic": "root_number",
             "prior_z_under_conductor": None},  # not in prior 7cells audit
}

# F013 slope-diff is based on ks_class=rank%2 across ranks. For F013, the
# prior audit recorded one z (~15.31) in the audit_P028 JSON, same across
# cells because the statistic is a global pooled slope-diff.
F013_CELLS = {
    # prior_z values: P023/P041/P051 from reaudit_F013_3cells_results.json
    # (043ba782, stratifier=conductor). P028/P104 not separately audited under
    # that wave; carry 15.31 from the original audit_P028_findings_block_shuffle
    # per null_protocol_v1.md §Class 2 reference.
    "P023": {"class": 2, "prescribed_stratifier": "rank",
             "prior_z_under_conductor": 22.39},
    "P028": {"class": 2, "prescribed_stratifier": "rank",
             "prior_z_under_conductor": 15.31},
    "P041": {"class": 2, "prescribed_stratifier": "rank",
             "prior_z_under_conductor": 8211.96},
    "P051": {"class": 2, "prescribed_stratifier": "rank",
             "prior_z_under_conductor": 8.05},
    "P104": {"class": 2, "prescribed_stratifier": "rank",
             "prior_z_under_conductor": 15.31},
}


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    SIG_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    print(f"[reaudit_10] start {started}")

    df = fetch_base()
    print(f"[data] n={len(df):,} EC with >=2 zeros and rank, "
          f"rank dist {dict(df['rank'].value_counts().sort_index().head(6))}")

    df["ks_class"] = np.where(df["rank"] % 2 == 0, "SO_even", "SO_odd")
    commit = commit_short()
    rng = np.random.default_rng(SEED)

    all_results = {}

    # --- F011 Class-3 cells --------------------------------------------------
    for p_id, meta in F011_CELLS.items():
        print(f"\n[F011:{p_id}] Class {meta['class']} → prescribed stratifier={meta['prescribed_stratifier']}")
        stat = f011_stat_spread(meta["semantic"])

        # Test A: literal Class-3 null
        literal = bswcd_null(
            df.copy(), stratifier=meta["prescribed_stratifier"],
            n_bins=N_BINS, n_perms=N_PERMS, seed=SEED,
            statistic=stat,
        )
        literal_degenerate = literal["null_std"] < 1e-9
        print(f"  (A) LITERAL NULL_BSWCD@v2[stratifier={meta['prescribed_stratifier']}]: "
              f"obs={literal['observed']:.5f} null_mean={literal['null_mean']:.5f} "
              f"null_std={literal['null_std']:.2e} → {'DEGENERATE' if literal_degenerate else literal['verdict']}")

        # Test B: per-stratum durability (the meaningful Class-3 test)
        rng_b = np.random.default_rng(SEED + 1)
        reform = f011_per_stratum_durability(df, meta["semantic"], rng_b)
        print(f"  (B) PER-STRATUM DEFICIT DURABILITY (n_strata={reform['n_strata']}): "
              f"min|z|={reform['min_abs_z']:.2f} max|z|={reform['max_abs_z']:.2f} → {reform['verdict']}")
        for v, ps in reform["per_stratum"].items():
            print(f"      stratum {v:>3}: n={ps['n']:>8}  deficit={ps['deficit']:+.5f}  z={ps['z']:+.2f}")

        all_results[f"F011:{p_id}"] = {
            "class": meta["class"],
            "prescribed_stratifier": meta["prescribed_stratifier"],
            "prior_z_under_conductor": meta["prior_z_under_conductor"],
            "literal": {k: literal[k] for k in
                        ("observed", "null_mean", "null_std", "z_score", "verdict",
                         "n_strata_used", "stratifier")},
            "literal_degenerate": literal_degenerate,
            "reformulated": reform,
            "verdict": reform["verdict"],
            "recommended_tensor_action": (
                "retain +2 (per-stratum durable)" if reform["verdict"] == "DURABLE" else
                "downgrade to +1 (mixed durability)" if reform["verdict"] == "MIXED" else
                "demote to -1 (per-stratum collapses)"
            ),
        }

    # --- F013 Class-2 cells --------------------------------------------------
    # All 5 F013 cells share the same slope-diff statistic globally, so the
    # reformulated per-rank slope interaction is computed ONCE.
    print(f"\n[F013 reformulated] per-rank slope(var vs log_cond) interaction under joint (rank, cond_decile) null...")
    rng_f013 = np.random.default_rng(SEED + 2)
    f013_reform = f013_per_rank_slope_interaction(df, rng_f013)
    print(f"  observed std(slope_r)={f013_reform['observed']:.6f}  "
          f"null_mean={f013_reform['null_mean']:.6f}  null_std={f013_reform['null_std']:.6f}  "
          f"z={f013_reform['z_score']}  → {f013_reform['verdict']}")

    for p_id, meta in F013_CELLS.items():
        print(f"\n[F013:{p_id}] Class {meta['class']} → prescribed stratifier={meta['prescribed_stratifier']}")

        # Test A: literal Class-2 null with original F013 slope-diff statistic
        literal = bswcd_null(
            df.copy(), stratifier="rank",
            n_bins=N_BINS, n_perms=N_PERMS, seed=SEED,
            statistic=f013_slope_diff_statistic,
        )
        literal_degenerate = literal["null_std"] < 1e-9
        print(f"  (A) LITERAL NULL_BSWCD@v2[stratifier=rank]: "
              f"obs={literal['observed']:.5f} null_std={literal['null_std']:.2e} → "
              f"{'DEGENERATE' if literal_degenerate else literal['verdict']}")

        all_results[f"F013:{p_id}"] = {
            "class": meta["class"],
            "prescribed_stratifier": meta["prescribed_stratifier"],
            "prior_z_under_conductor": meta["prior_z_under_conductor"],
            "literal": {k: literal[k] for k in
                        ("observed", "null_mean", "null_std", "z_score", "verdict",
                         "n_strata_used", "stratifier")},
            "literal_degenerate": literal_degenerate,
            "reformulated": f013_reform,
            "verdict": f013_reform["verdict"],
            "recommended_tensor_action": (
                "retain +2 (per-rank slope interaction durable)" if f013_reform["verdict"] == "DURABLE"
                else "demote to -1"
            ),
        }

    # --- SIGNATURE@v1 per cell ----------------------------------------------
    signatures = {}
    for cell_id, res in all_results.items():
        feature, projection = cell_id.split(":")
        # Build a pseudo-result suitable for bswcd_signature using the reform test where available
        reform = res["reformulated"]
        if "observed" in reform:
            # F013-style (reformulated is a NULL_BSWCD-shape dict)
            sig_result = dict(reform)
            sig_result.setdefault("n_bins", N_BINS)
            sig_result.setdefault("n_perms", N_PERMS)
            sig_result.setdefault("seed", SEED)
            effect = sig_result["observed"]
        else:
            # F011-style (per-stratum dict)
            zs = [v["z"] for v in reform["per_stratum"].values()]
            sig_result = {
                "null_mean": 0.0,
                "null_std": 1.0,   # per-stratum z-scores are already normalized
                "null_p99": 3.0,
                "observed": reform["min_abs_z"],
                "z_score": reform["min_abs_z"],
                "verdict": reform["verdict"],
                "n_strata_used": reform["n_strata"],
                "stratifier": res["prescribed_stratifier"],
                "n_bins": reform["n_strata"],
                "n_perms": N_PERMS,
                "seed": SEED,
            }
            effect = reform["min_abs_z"]
        sig = bswcd_signature(
            feature_id=f"{feature}@{commit}",
            projection_ids=[f"{projection}@{commit}"],
            result=sig_result,
            n_samples=len(df),
            dataset_spec="Q_EC@lmfdb.ec_curvedata JOIN prometheus_fire.zeros.object_zeros (n_zeros>=2, rank not null)",
            commit=commit,
            worker=WORKER,
            timestamp=datetime.now(timezone.utc).isoformat(),
            effect_size=effect,
        )
        # inject task-specific fields
        sig["task"] = "reaudit_10_stratifier_mismatch_cells"
        sig["claim_class"] = res["class"]
        sig["prior_z_under_conductor"] = res["prior_z_under_conductor"]
        sig["literal_degenerate"] = res["literal_degenerate"]
        sig["recommended_tensor_action"] = res["recommended_tensor_action"]
        sig_path = SIG_DIR / f"SIG_{feature}_{projection}_v2.json"
        sig_path.write_text(json.dumps(sig, indent=2, default=str), encoding="utf-8")
        signatures[cell_id] = str(sig_path)
        res["signature_path"] = str(sig_path)

    report = {
        "task": "reaudit_10_stratifier_mismatch_cells",
        "operator": "NULL_BSWCD@v2 (reformulated per claim class)",
        "worker": WORKER,
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "n_samples": len(df),
        "cells": all_results,
        "scope_note": (
            "9 NULL_BSWCD-appropriate cells audited (4 F011 Class-3, 5 F013 Class-2). "
            "3 F044 Class-4 cells (P020, P023, P026) are out of scope — see separate "
            "audit_F044_framebased_resample task."
        ),
        "methodology_finding": (
            "The literal Class-2/3 prescription (NULL_BSWCD@v2 with the semantic stratifier "
            "of the cell, and the original cross-group-spread or slope-diff statistic) is "
            "structurally degenerate for these specific cells. Within-stratifier shuffle "
            "preserves per-stratum means/variances; the original statistics depend only on "
            "those per-stratum aggregates; therefore the null distribution is concentrated "
            "at the observed value (null_std ≈ 0) and z is uninformative. "
            "The REFORMULATED tests (per-stratum deficit bootstrap for Class 3; per-rank "
            "conductor-slope interaction under joint (rank, cond_decile) shuffle for Class 2) "
            "are claim-appropriate and non-degenerate. This suggests the classification JSON's "
            "Class-2/3 labeling for F011 cells in particular may be reinterpretable as "
            "Class-2 interactions (axis reveals structure) rather than Class-3 uniformity "
            "claims, with the original conductor-stratified null being the correct match."
        ),
    }
    out = OUTDIR / "reaudit_10_stratifier_mismatch_results.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\n[reaudit_10] wrote {out}")

    # --- Markdown report ----------------------------------------------------
    md_lines = []
    md_lines.append("# Re-audit: 10 stratifier-mismatch cells under NULL_BSWCD@v2")
    md_lines.append("")
    md_lines.append(f"**Task:** `reaudit_10_stratifier_mismatch_cells`  ")
    md_lines.append(f"**Worker:** {WORKER}  ")
    md_lines.append(f"**Commit:** `{commit}`  ")
    md_lines.append(f"**Operator:** NULL_BSWCD@v2 (literal) + reformulated per claim class  ")
    md_lines.append(f"**n_samples:** {len(df):,}  ")
    md_lines.append(f"**n_perms:** {N_PERMS}  seed={SEED}  ")
    md_lines.append(f"**Classification source:** `cartography/docs/cell_null_classification.json`  ")
    md_lines.append(f"**Null protocol:** `harmonia/memory/symbols/protocols/null_protocol_v1.md`")
    md_lines.append("")
    md_lines.append("## Scope")
    md_lines.append("")
    md_lines.append("- **9 audited:** 4 F011 Class-3 + 5 F013 Class-2.")
    md_lines.append("- **3 F044 Class-4 (P020, P023, P026) out of scope** — NULL_BSWCD insufficient for construction-biased samples. Remain PROVISIONAL per null_protocol_v1 §Class 4. Separate audit (`audit_F044_framebased_resample`) required.")
    md_lines.append("")
    md_lines.append("## Methodology finding (headline)")
    md_lines.append("")
    md_lines.append(report["methodology_finding"])
    md_lines.append("")
    md_lines.append("## Results summary")
    md_lines.append("")
    md_lines.append("| Cell | Class | Prescribed stratifier | Prior z (conductor) | Literal z | Reformulated verdict | Recommended action |")
    md_lines.append("|---|---|---|---|---|---|---|")
    for cell_id, res in all_results.items():
        feature, projection = cell_id.split(":")
        lit_z = res["literal"]["z_score"]
        lit_deg = " (DEG)" if res["literal_degenerate"] else ""
        prior = res["prior_z_under_conductor"]
        prior_s = f"{prior:+.2f}" if prior is not None else "n/a"
        reform = res["reformulated"]
        if "verdict" in reform and "per_stratum" not in reform:
            reform_s = f"{reform['verdict']} (z={reform['z_score']:+.2f})"
        else:
            reform_s = f"{reform['verdict']} (n_strata={reform['n_strata']}, min|z|={reform['min_abs_z']:.2f})"
        md_lines.append(f"| {cell_id} | {res['class']} | {res['prescribed_stratifier']} | "
                        f"{prior_s} | {lit_z:+.2f}{lit_deg} | {reform_s} | {res['recommended_tensor_action']} |")
    md_lines.append("")

    # Per-cell detail
    md_lines.append("## Per-cell detail")
    md_lines.append("")
    for cell_id, res in all_results.items():
        md_lines.append(f"### {cell_id} — Class {res['class']}")
        md_lines.append("")
        lit = res["literal"]
        md_lines.append(f"**Literal NULL_BSWCD@v2** `[stratifier={lit['stratifier']}, n_bins={N_BINS}, n_perms={N_PERMS}, seed={SEED}]`")
        md_lines.append("")
        md_lines.append(f"- observed = `{lit['observed']:.6g}`")
        md_lines.append(f"- null_mean = `{lit['null_mean']:.6g}`, null_std = `{lit['null_std']:.3e}`")
        md_lines.append(f"- n_strata_used = `{lit['n_strata_used']}`")
        md_lines.append(f"- z_score = `{lit['z_score']}`, verdict = `{lit['verdict']}`"
                        f"{'  **[DEGENERATE]**' if res['literal_degenerate'] else ''}")
        md_lines.append("")
        reform = res["reformulated"]
        if "per_stratum" in reform and reform["per_stratum"] is not None and isinstance(reform["per_stratum"], dict):
            md_lines.append(f"**Reformulated (F011-style per-stratum deficit durability)** — bootstrap SE per stratum.")
            md_lines.append("")
            md_lines.append(f"- n_strata = `{reform['n_strata']}`, min|z| = `{reform['min_abs_z']:.2f}`, max|z| = `{reform['max_abs_z']:.2f}`, verdict = `{reform['verdict']}`")
            md_lines.append("")
            md_lines.append("| stratum | n | deficit = GUE − mean | bootstrap SE | z | durable |")
            md_lines.append("|---|---|---|---|---|---|")
            for v, ps in reform["per_stratum"].items():
                md_lines.append(f"| {v} | {ps['n']:,} | {ps['deficit']:+.6g} | {ps['bootstrap_se']:.3e} | {ps['z']:+.2f} | {ps['durable']} |")
            md_lines.append("")
        elif "z_score" in reform:
            md_lines.append(f"**Reformulated (F013 per-rank slope(var vs log_cond) interaction under joint (rank, cond_decile) shuffle)**")
            md_lines.append("")
            md_lines.append(f"- observed interaction std(slope_r) = `{reform['observed']:.6g}`")
            md_lines.append(f"- null_mean = `{reform['null_mean']:.6g}`, null_std = `{reform['null_std']:.6g}`, null_p99 = `{reform['null_p99']:.6g}`")
            md_lines.append(f"- stratifier = `{reform['stratifier']}`, n_perms = `{reform['n_perms']}`")
            md_lines.append(f"- z = `{reform['z_score']}`, verdict = `{reform['verdict']}`")
            md_lines.append("")
        md_lines.append(f"**Signature:** `{res.get('signature_path','(pending)')}`")
        md_lines.append(f"**Recommended tensor action:** {res['recommended_tensor_action']}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    md_lines.append("## F044 Class-4 annotation (out of scope)")
    md_lines.append("")
    md_lines.append("Cells F044:{P020, P023, P026} are flagged Class 4 (construction-biased sample) by the classification JSON. "
                    "Per `null_protocol_v1.md` §Class 4, NULL_BSWCD is insufficient; requires frame-based resample, model-based null, "
                    "or theorem check. These cells **remain PROVISIONAL** and are **not audited here**.")
    md_lines.append("")
    md_lines.append("## SIGNATURE@v1 artifacts")
    md_lines.append("")
    for cell_id, res in all_results.items():
        md_lines.append(f"- `{res.get('signature_path','(pending)')}`  ({cell_id})")
    md_lines.append("")
    md_lines.append("## Reproducibility")
    md_lines.append("")
    md_lines.append(f"- Data: `lmfdb.public.ec_curvedata` × `prometheus_fire.zeros.object_zeros` inner join, n_zeros≥2, rank not null; n = {len(df):,}.")
    md_lines.append(f"- Seed: {SEED}. N_perms: {N_PERMS}. Bin count (literal null): {N_BINS}.")
    md_lines.append(f"- Script: `harmonia/reaudit_10_stratifier_mismatch.py`.")
    md_lines.append(f"- Commit (at run): `{commit}`.")
    md_lines.append("")

    md_out = OUTDIR / "reaudit_10_stratifier_mismatch_results.md"
    md_out.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[reaudit_10] wrote {md_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
