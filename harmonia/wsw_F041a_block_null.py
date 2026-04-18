"""wsw_F041a_block_null.py — F041a durability test via block-shuffle-within-cell null.

Task: Validate whether the rank-2+ x num_bad_primes slope interaction (per the
Keating-Snaith arithmetic analysis) survives a block-shuffle-within-cell null
in the spirit of wsw_F010_alternative_null.

Background (cartography/docs/keating_snaith_arithmetic_analysis_results.json):
  Rank 2 slope of M_1(X) = R_1 across conductor decades, by num_bad_primes:
    nbp=1: 1.21 (n_decades=2), nbp=2: 1.52, nbp=3: 1.70, nbp=4: 1.86,
    nbp=5: 1.95, nbp=6: 2.52
  Rank 0 / rank 1 slopes are roughly flat across nbp. Rank 3 limited coverage
  shows the same direction (nbp=2: 1.89, nbp=3: 2.25).

F041a candidate: "rank-dependent conductor-slope of first moment is further
modulated (monotone-increasing) by number of bad primes, at ranks >= 2".

Method (matches harmonia/wsw_F010_alternative_null.py style):
  1. Load joined (rank, conductor, leading_term, num_bad_primes) rows.
  2. Bin by conductor decade (10^3, 10^4, 10^5, 10^6, 10^7) — geometric mean
     used as log_X_mid.
  3. Real slopes: per (rank, decade, nbp) cell mean M_1 -> fit slope of
     M_1 vs log X over decades for each (rank, nbp) -> real_slope[rank][nbp].
  4. CELL-BLOCK NULL (within-cell shuffle): shuffle leading_term values
     WITHIN each (rank, decade, nbp) cell 300 times. Because cell-mean is
     invariant under within-cell permutation (mean is a symmetric function),
     this null is a SANITY CHECK on the pipeline — the slopes should be
     literally identical modulo float rounding.
  5. CROSS-NBP BLOCK NULL (the real discriminator): within each (rank, decade)
     cell, shuffle leading_term values ACROSS nbp strata. This destroys the
     nbp-specific mean at each decade while preserving the (rank, decade)
     marginal. If the real-data monotone-in-nbp pattern persists here, the
     signal is not an artifact of mean(L|nbp) varying: it lives in the slope
     structure. If it collapses, the "monotone slopes" were just reflections
     of mean(L) increasing with nbp (and a conductor-dependent weighting).

Verdict rubric:
  SURVIVES_BLOCK_NULL — cross-nbp null z >= 3.0 for all rank-2 nbp cells
    where real slope is monotone; F041a promoted.
  PARTIAL — some but not all nbp strata survive at z>=3; document details.
  COLLAPSES — cross-nbp z < 2.0 on the monotone ladder; the nbp "interaction"
    was a cell-mean artifact, not arithmetic structure.

Output: cartography/docs/wsw_F041a_block_null_results.json
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

RANKS = [0, 1, 2, 3]
# Decades as per keating_snaith_arithmetic_analysis.py
DECADE_EDGES = [(100, 1000), (1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]
NBP_BINS = [1, 2, 3, 4, 5, 6]
MIN_PER_TRIPLE = 100   # per the task: min n>=100 per (rank, decade, nbp)
N_PERMS = 300
SEED = 20260417


def load_joined():
    with psycopg2.connect(**PF) as pf_conn:
        cur = pf_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, analytic_rank, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND leading_term IS NOT NULL AND leading_term > 0
              AND conductor > 0 AND analytic_rank <= 3
        """)
        zeros_rows = {r[0]: (int(r[1]), int(r[2]), float(r[3]))
                      for r in cur.fetchall()}
    with psycopg2.connect(**LM) as lm_conn:
        cur = lm_conn.cursor()
        cur.execute("""
            SELECT lmfdb_label, NULLIF(num_bad_primes, '')::int
            FROM public.ec_curvedata
            WHERE num_bad_primes IS NOT NULL
        """)
        nbp = {r[0]: int(r[1]) for r in cur.fetchall() if r[1] is not None}
    out = []
    for lbl, (rank, cond, lt) in zeros_rows.items():
        k = nbp.get(lbl)
        if k is None:
            continue
        out.append((rank, cond, lt, k))
    return out


def decade_of(cond):
    for lo, hi in DECADE_EDGES:
        if lo <= cond < hi:
            return (lo, hi)
    return None


def decade_mid_log(lo, hi):
    return math.log(math.sqrt(lo * hi))


def slope_fit(xs, ys):
    if len(xs) < 2:
        return None
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    mx, my = x.mean(), y.mean()
    num = ((x - mx) * (y - my)).sum()
    den = ((x - mx) ** 2).sum()
    if den == 0:
        return None
    return float(num / den)


def build_cells(rows):
    """Returns {(rank, lo, hi, nbp): np.ndarray of leading_term values}."""
    cells = defaultdict(list)
    for rank, cond, lt, nbp in rows:
        if rank not in RANKS:
            continue
        d = decade_of(cond)
        if d is None:
            continue
        if nbp not in NBP_BINS:
            continue
        cells[(rank, d[0], d[1], nbp)].append(lt)
    return {k: np.asarray(v, dtype=float) for k, v in cells.items()}


def real_slopes(cells):
    """For each (rank, nbp), fit slope of cell-mean M_1 vs log_X_mid over
    decades where n >= MIN_PER_TRIPLE. Returns dict and a cell_detail dict."""
    out = {}
    detail = {}
    skipped = []
    # Organize by (rank, nbp)
    by_rn = defaultdict(list)  # (rank, nbp) -> list of (log_x_mid, M_1, n, lo, hi)
    for (rank, lo, hi, nbp), vals in cells.items():
        if vals.size < MIN_PER_TRIPLE:
            skipped.append({"rank": rank, "lo": lo, "hi": hi, "nbp": nbp,
                            "n": int(vals.size), "reason": "n<MIN_PER_TRIPLE"})
            continue
        m1 = float(vals.mean())
        by_rn[(rank, nbp)].append((decade_mid_log(lo, hi), m1,
                                    int(vals.size), lo, hi))
    for (rank, nbp), pts in by_rn.items():
        pts.sort(key=lambda t: t[0])
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        s = slope_fit(xs, ys)
        out.setdefault(rank, {})[nbp] = {
            "slope": s,
            "n_decades": len(pts),
            "cells": [{"log_X_mid": p[0], "M_1": p[1], "n": p[2],
                       "lo": p[3], "hi": p[4]} for p in pts],
        }
        detail[f"r={rank}_nbp={nbp}"] = out[rank][nbp]
    return out, detail, skipped


def cell_block_null(cells, n_perms, seed):
    """Within-cell shuffle — symmetric-function sanity check.

    Since M_1 is a symmetric function of the values in a cell, any within-cell
    permutation leaves all cell-means numerically identical (up to float
    roundoff). The resulting slope distribution should therefore be a spike.
    This is a pipeline-integrity check."""
    rng = np.random.default_rng(seed)
    # Pre-index cells that pass MIN
    usable = {k: v for k, v in cells.items() if v.size >= MIN_PER_TRIPLE}
    # Group by (rank, nbp) -> list of (log_x_mid, n, vals)
    group = defaultdict(list)
    for (rank, lo, hi, nbp), vals in usable.items():
        group[(rank, nbp)].append((decade_mid_log(lo, hi), vals))
    null_slopes = defaultdict(list)
    for _ in range(n_perms):
        for (rank, nbp), cell_list in group.items():
            xs = []
            ys = []
            for log_x_mid, vals in cell_list:
                # Within-cell shuffle is a no-op on the mean; do it anyway.
                shuf = rng.permutation(vals)
                xs.append(log_x_mid)
                ys.append(float(shuf.mean()))
            xs_sorted_idx = np.argsort(xs)
            xs = [xs[i] for i in xs_sorted_idx]
            ys = [ys[i] for i in xs_sorted_idx]
            s = slope_fit(xs, ys)
            if s is not None:
                null_slopes[(rank, nbp)].append(s)
    return null_slopes


def cross_nbp_block_null(cells, n_perms, seed):
    """CROSS-NBP block null — shuffles leading_term values WITHIN each
    (rank, decade) cell ACROSS nbp strata.

    Implementation: for each (rank, lo, hi), pool all leading_term values
    from all nbp bins (tagging each by its original nbp), and on each
    permutation, permute the value-to-nbp assignment within the pool.
    Then recompute per-(rank, nbp, decade) means and refit slopes by (rank, nbp).

    Destroys: mean(L|nbp,decade) — nbp-specific means at each decade collapse
    to the (rank, decade) marginal mean (in expectation).
    Preserves: (rank, decade) marginal distribution of leading_term.

    If the real-data monotone-in-nbp slope survives here with large z, the
    slope pattern is arithmetic structure above-and-beyond varying cell means.
    If it collapses, the pattern was an expression of E[L|nbp] varying."""
    rng = np.random.default_rng(seed + 1)
    # Build per (rank, lo, hi) pools: values and nbp tags
    pools = defaultdict(lambda: {"vals": [], "nbps": []})
    for (rank, lo, hi, nbp), vals in cells.items():
        if nbp not in NBP_BINS:
            continue
        pools[(rank, lo, hi)]["vals"].append(vals)
        pools[(rank, lo, hi)]["nbps"].append(np.full(vals.size, nbp,
                                                      dtype=np.int32))
    # Concatenate
    for key in list(pools.keys()):
        pools[key]["vals"] = np.concatenate(pools[key]["vals"]) \
            if pools[key]["vals"] else np.array([])
        pools[key]["nbps"] = np.concatenate(pools[key]["nbps"]) \
            if pools[key]["nbps"] else np.array([], dtype=np.int32)

    # Precompute the "usable" status per (rank, lo, hi, nbp): determined by
    # the REAL n in that cell (not by the permutation — whether to report the
    # slope follows real-data coverage, so we match MIN_PER_TRIPLE on REAL n).
    real_n = {k: v.size for k, v in cells.items()}

    # Also precompute all (rank, nbp) sequences: which decades pass MIN on real
    seqs = defaultdict(list)  # (rank, nbp) -> list of (log_x_mid, lo, hi)
    for (rank, lo, hi, nbp), vals in cells.items():
        if vals.size < MIN_PER_TRIPLE:
            continue
        seqs[(rank, nbp)].append((decade_mid_log(lo, hi), lo, hi))
    for key in seqs:
        seqs[key].sort(key=lambda t: t[0])

    null_slopes = defaultdict(list)
    for perm_idx in range(n_perms):
        # For each (rank, lo, hi), permute the nbp assignment on the pool
        shuffled_means = {}  # (rank, lo, hi, nbp) -> mean
        for (rank, lo, hi), pool in pools.items():
            vals = pool["vals"]
            nbps = pool["nbps"]
            if vals.size == 0:
                continue
            perm = rng.permutation(vals.size)
            nbps_shuf = nbps[perm]
            # Compute per-nbp means under the shuffled assignment
            for nbp in NBP_BINS:
                mask = (nbps_shuf == nbp)
                n = int(mask.sum())
                # MATCH REAL COVERAGE: we only record means for cells that
                # had >= MIN_PER_TRIPLE real observations. The shuffled n is
                # by construction equal to the real n (counts per nbp are
                # invariant under permutation), so this is consistent.
                if n == 0:
                    continue
                shuffled_means[(rank, lo, hi, nbp)] = float(vals[mask].mean())
        # Fit slopes by (rank, nbp) using the same decade coverage as real
        for (rank, nbp), dec_list in seqs.items():
            xs = []
            ys = []
            for log_x_mid, lo, hi in dec_list:
                key = (rank, lo, hi, nbp)
                if key in shuffled_means:
                    xs.append(log_x_mid)
                    ys.append(shuffled_means[key])
            if len(xs) < 2:
                continue
            s = slope_fit(xs, ys)
            if s is not None:
                null_slopes[(rank, nbp)].append(s)
    return null_slopes


def summarize_null(null_dict):
    out = {}
    for (rank, nbp), slopes in null_dict.items():
        arr = np.asarray(slopes, dtype=float)
        out.setdefault(str(rank), {})[str(nbp)] = {
            "n_perms": int(arr.size),
            "mean": float(arr.mean()) if arr.size else None,
            "std": float(arr.std(ddof=1)) if arr.size > 1 else None,
            "min": float(arr.min()) if arr.size else None,
            "max": float(arr.max()) if arr.size else None,
            "q05": float(np.quantile(arr, 0.05)) if arr.size else None,
            "q95": float(np.quantile(arr, 0.95)) if arr.size else None,
        }
    return out


def z_score_vs_null(real, null_mean, null_std):
    if real is None or null_mean is None or null_std is None or null_std == 0:
        return None
    return float((real - null_mean) / null_std)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F041a_block_null] start {started}")

    rows = load_joined()
    print(f"[load] joined rows: {len(rows)}")

    cells = build_cells(rows)
    print(f"[cells] total (rank, decade, nbp) cells: {len(cells)}")

    real, detail, skipped = real_slopes(cells)
    print(f"[real slopes] computed for {sum(len(v) for v in real.values())} "
          f"(rank, nbp) pairs; skipped {len(skipped)} low-n cells")

    # Sanity: cell-block null (within-cell shuffle is a no-op on means)
    print("[cell-block null] running within-cell shuffle (sanity)...")
    cell_null = cell_block_null(cells, N_PERMS, SEED)
    cell_null_summary = summarize_null(cell_null)

    # Real test: cross-nbp null
    print(f"[cross-nbp null] running {N_PERMS} permutations...")
    cross_null = cross_nbp_block_null(cells, N_PERMS, SEED)
    cross_null_summary = summarize_null(cross_null)

    # Compute z-scores for the cross-nbp null per (rank, nbp) cell
    z_table = {}
    for rank_key, by_nbp in cross_null_summary.items():
        rank = int(rank_key)
        for nbp_key, stats in by_nbp.items():
            nbp = int(nbp_key)
            r = real.get(rank, {}).get(nbp)
            if r is None or r["slope"] is None:
                continue
            z = z_score_vs_null(r["slope"], stats["mean"], stats["std"])
            z_table.setdefault(rank_key, {})[nbp_key] = {
                "real_slope": r["slope"],
                "n_decades": r["n_decades"],
                "null_mean": stats["mean"],
                "null_std": stats["std"],
                "z_score": z,
                "null_q05": stats["q05"],
                "null_q95": stats["q95"],
            }

    # Also z-scores for cell-block null (should be ~infinite/NaN due to zero std)
    z_table_cell = {}
    for rank_key, by_nbp in cell_null_summary.items():
        rank = int(rank_key)
        for nbp_key, stats in by_nbp.items():
            nbp = int(nbp_key)
            r = real.get(rank, {}).get(nbp)
            if r is None or r["slope"] is None:
                continue
            z = z_score_vs_null(r["slope"], stats["mean"], stats["std"])
            z_table_cell.setdefault(rank_key, {})[nbp_key] = {
                "real_slope": r["slope"],
                "null_mean": stats["mean"],
                "null_std": stats["std"],
                "z_score": z,
                "note": ("within-cell permutation leaves cell mean invariant; "
                         "expect null_std ~= 0 and z undefined/huge"),
            }

    # Verdict — focus on rank >= 2 monotone ladder
    rank2_zs = []
    for nbp in NBP_BINS:
        entry = z_table.get("2", {}).get(str(nbp))
        if entry is not None and entry["z_score"] is not None:
            rank2_zs.append((nbp, entry["z_score"], entry["real_slope"],
                             entry["n_decades"]))
    rank3_zs = []
    for nbp in NBP_BINS:
        entry = z_table.get("3", {}).get(str(nbp))
        if entry is not None and entry["z_score"] is not None:
            rank3_zs.append((nbp, entry["z_score"], entry["real_slope"],
                             entry["n_decades"]))

    # Ladder-magnitude discriminator — the per-cell |z| blows up at any
    # systematic offset between real and null cell means, so a large |z|
    # alone does NOT prove a monotone-in-nbp interaction. The sharp test
    # is: (i) the RANGE of real slopes across nbp strata at each rank, and
    # (ii) Pearson correlation of real slope with nbp. Under the cross-nbp
    # null the nbp-stratified slopes converge to a common (rank, decade)
    # marginal slope, so null_range -> 0. A large ratio (real_range /
    # null_range) with strong positive corr(nbp, slope) is the fingerprint
    # of the F041a interaction.
    ladder_discriminator = {}
    for rank in RANKS:
        rkey = str(rank)
        entries = z_table.get(rkey, {})
        pairs = []  # (nbp, real_slope, null_mean, null_std)
        for nbp in NBP_BINS:
            e = entries.get(str(nbp))
            if e is None or e["z_score"] is None:
                continue
            pairs.append((nbp, e["real_slope"], e["null_mean"],
                          e["null_std"]))
        if len(pairs) < 2:
            continue
        nbps_arr = np.array([p[0] for p in pairs], dtype=float)
        real_arr = np.array([p[1] for p in pairs], dtype=float)
        nullm_arr = np.array([p[2] for p in pairs], dtype=float)
        nulls_arr = np.array([p[3] for p in pairs], dtype=float)
        real_range = float(real_arr.max() - real_arr.min())
        null_mean_range = float(nullm_arr.max() - nullm_arr.min())
        avg_null_std = float(nulls_arr.mean())
        if real_arr.std() > 0 and nbps_arr.std() > 0:
            corr_nbp_slope = float(np.corrcoef(nbps_arr, real_arr)[0, 1])
        else:
            corr_nbp_slope = None
        # Amplification factor: how many "null ladder widths" does the
        # real ladder span? Use max(null_mean_range, avg_null_std) as
        # denominator to avoid division by zero and to make the ratio
        # comparable across ranks.
        denom = max(null_mean_range, avg_null_std, 1e-6)
        amplification = real_range / denom
        ladder_discriminator[rkey] = {
            "real_slope_range_across_nbp": real_range,
            "null_slope_mean_range_across_nbp": null_mean_range,
            "avg_null_std": avg_null_std,
            "amplification_ratio": amplification,
            "corr_nbp_vs_real_slope": corr_nbp_slope,
            "n_nbp_points": len(pairs),
            "nbps_used": [int(x) for x in nbps_arr],
            "real_slopes_used": real_arr.tolist(),
        }

    # A cell must have n_decades >= 3 to produce a non-degenerate z distribution
    # under permutation (otherwise slope is deterministic given two points and
    # two fixed means, leading to zero null variance). We downweight 2-decade
    # cells in the verdict.
    rank2_solid = [(nbp, z, s, nd) for nbp, z, s, nd in rank2_zs if nd >= 3]

    thresh_survive = 3.0
    thresh_collapse = 2.0

    # The adjudication uses both per-cell |z| and the ladder-magnitude
    # discriminator. A large |z| at a single cell only says "real cell
    # mean differs from (rank, decade) marginal", which is true even at
    # rank 0/1 where no monotone pattern exists. The monotone pattern
    # is what F041a claims, so we require:
    #   (A) |z| >= thresh_survive for every rank-2 solid (n_decades>=3) cell
    #   (B) amplification_ratio (real_range / null_range) >> 1 at rank 2
    #   (C) corr(nbp, real_slope) at rank 2 >= 0.9 (monotone ladder)
    # Collapse: (A) fails and amplification_ratio < 2.
    AMP_SURVIVE = 5.0
    CORR_SURVIVE = 0.9
    AMP_COLLAPSE = 2.0

    rank2_amp = ladder_discriminator.get("2", {}).get("amplification_ratio")
    rank2_corr = ladder_discriminator.get("2", {}).get("corr_nbp_vs_real_slope")

    if not rank2_solid:
        verdict = "INSUFFICIENT_COVERAGE"
        reading = (f"Rank-2 ladder has no (rank, nbp) cell with n_decades >= 3; "
                   f"the monotone pattern rests on 2-point fits where z is "
                   f"degenerate. Coverage must be expanded before F041a can be "
                   f"adjudicated. rank2_zs (all n_decades): {rank2_zs}.")
    else:
        zs_solid = [abs(z) for _, z, _, _ in rank2_solid]
        all_survive_z = all(z >= thresh_survive for z in zs_solid)
        any_survive_z = any(z >= thresh_survive for z in zs_solid)
        ladder_survives = (
            rank2_amp is not None and rank2_amp >= AMP_SURVIVE
            and rank2_corr is not None and rank2_corr >= CORR_SURVIVE
        )
        ladder_collapses = (
            rank2_amp is not None and rank2_amp < AMP_COLLAPSE
        )
        all_collapse_z = all(z < thresh_collapse for z in zs_solid)

        if all_survive_z and ladder_survives:
            verdict = "SURVIVES_BLOCK_NULL"
            reading = (f"Rank-2 solid strata: all |z| >= {thresh_survive} AND "
                       f"amplification ratio {rank2_amp:.1f}x >= {AMP_SURVIVE} "
                       f"AND corr(nbp, slope) = {rank2_corr:.3f} >= "
                       f"{CORR_SURVIVE}. The monotone-in-nbp slope ladder is "
                       f"arithmetic structure that survives cross-nbp "
                       f"shuffling. F041a promoted.")
        elif all_collapse_z or ladder_collapses:
            verdict = "COLLAPSES"
            reading = (f"Rank-2 ladder fails durability: amp={rank2_amp}, "
                       f"corr={rank2_corr}. The monotone-in-nbp slope "
                       f"pattern is consistent with mean(L|nbp) varying; "
                       f"no residual arithmetic structure survives the "
                       f"cross-nbp null. F041a collapses.")
        elif any_survive_z and (ladder_survives or rank2_amp is None):
            verdict = "PARTIAL"
            reading = (f"Partial durability: some |z| >= {thresh_survive}, "
                       f"amp={rank2_amp}, corr={rank2_corr}. The nbp "
                       f"interaction has a signal component but at least one "
                       f"solid rank-2 cell sits below {thresh_survive}. "
                       f"Document the surviving strata and investigate.")
        else:
            verdict = "PARTIAL"
            reading = (f"Rank-2 strata mixed: amp={rank2_amp}, corr={rank2_corr}. "
                       f"F041a not fully promoted; coverage/permutations need "
                       f"expansion to discriminate.")

    # Pattern 20 — emit every per-cell number
    per_cell_dump = {}
    for (rank, lo, hi, nbp), vals in sorted(cells.items()):
        per_cell_dump[f"r={rank}_d=[{lo},{hi})_nbp={nbp}"] = {
            "rank": rank, "lo": lo, "hi": hi, "nbp": nbp,
            "n": int(vals.size),
            "M_1": float(vals.mean()) if vals.size else None,
            "M_2": float((vals ** 2).mean()) if vals.size else None,
            "used_in_slope_fit": vals.size >= MIN_PER_TRIPLE,
        }

    result = {
        "specimen_id": "F041a",
        "claim_under_test": (
            "At ranks >= 2, the conductor-slope of M_1 (first moment of "
            "leading_term across conductor decades) is monotone-increasing "
            "in num_bad_primes. The interaction is real arithmetic structure, "
            "not a reflection of E[leading_term | nbp] varying."
        ),
        "verdict": verdict,
        "reading": reading,
        "real_slopes_M1_vs_logX": {
            str(rank): {str(nbp): v for nbp, v in by_nbp.items()}
            for rank, by_nbp in real.items()
        },
        "z_scores_cross_nbp_null": z_table,
        "z_scores_cell_within_null_SANITY": z_table_cell,
        "null_summaries": {
            "cross_nbp_block_null": cross_null_summary,
            "cell_within_null_SANITY": cell_null_summary,
        },
        "skipped_cells_low_n": skipped,
        "per_cell_detail": per_cell_dump,
        "ladder_discriminator_by_rank": ladder_discriminator,
        "rank2_ladder_zs_all": [
            {"nbp": nbp, "z": z, "real_slope": s, "n_decades": nd}
            for nbp, z, s, nd in rank2_zs
        ],
        "rank2_ladder_zs_solid_ndecades_ge_3": [
            {"nbp": nbp, "z": z, "real_slope": s, "n_decades": nd}
            for nbp, z, s, nd in rank2_solid
        ],
        "rank3_ladder_zs_all": [
            {"nbp": nbp, "z": z, "real_slope": s, "n_decades": nd}
            for nbp, z, s, nd in rank3_zs
        ],
        "_meta": {
            "task_id": "wsw_F041a_block_null",
            "instance": "Harmonia_worker_W2",
            "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
            "n_perms": N_PERMS,
            "min_per_triple": MIN_PER_TRIPLE,
            "seed": SEED,
            "decade_edges": DECADE_EDGES,
            "nbp_bins": NBP_BINS,
            "ranks": RANKS,
            "threshold_survive": thresh_survive,
            "threshold_collapse": thresh_collapse,
            "null_types": {
                "cell_within_null": "Within-cell shuffle. Sanity only: "
                                    "leaves cell mean invariant (symmetric "
                                    "function), z should be degenerate.",
                "cross_nbp_block_null": "Within-(rank,decade) shuffle across "
                                        "nbp. Destroys mean(L|nbp,decade) "
                                        "while preserving (rank,decade) "
                                        "marginal. THIS is the real test.",
            },
            "reference": ("Slopes to audit are from "
                          "cartography/docs/keating_snaith_arithmetic_analysis"
                          "_results.json -> slopes_P021_per_rank_per_nbp."),
            "pattern_20_notes": [
                "Every (rank, decade, nbp) cell reported with n, M_1, M_2.",
                "Skipped cells (n < MIN_PER_TRIPLE) listed explicitly.",
                "n_decades per (rank, nbp) reported; 2-decade fits flagged "
                "separately since their permutation z is degenerate.",
            ],
        },
    }

    out_path = os.path.join("cartography", "docs",
                             "wsw_F041a_block_null_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"[wsw_F041a_block_null] wrote {out_path}")
    print(f"[verdict] {verdict}")
    print(f"[reading] {reading}")
    print(f"[rank2 solid ladder]")
    for nbp, z, s, nd in rank2_solid:
        print(f"    nbp={nbp}  slope={s:.3f}  n_decades={nd}  z={z:.2f}")


if __name__ == "__main__":
    main()
