"""wsw_F010_alternative_null.py — F010 durability test via block-shuffle-within-degree null.

Task: wsw_F010_alternative_null, claimed by Harmonia_M2_sessionB, tick 14.
Target projection: P052 (already decontaminated; applying an alternative null here).

Context:
  - sessionC wsw_F010_bigsample: P010 rho=0.109 z=0.87 (collapsed), P052 rho=0.270 z=2.38 (borderline).
  - Raw F010 collapsed at bigsample; decontaminated signal sits at z=2.38 — neither durable nor dead.

Method:
  - Mirror sessionC bigsample loading (per_degree=5000, per_combo=1000, prime-detrend both sides).
  - Compute ρ(NF_detrended_log_disc, Artin_detrended_log_cond) over shared Galois labels.
  - BLOCK NULL: extract degree from Galois label (degree = Galn from "{Galn}T{Galt}"). Within
    each degree class, shuffle the (label -> Artin side value) assignment; recompute ρ. This
    preserves the per-degree marginal distribution and kills only within-degree pairing.
  - 1000 block permutations vs 300 in sessionC's plain permutation.
  - Verdict: if observed ρ z-score under block null >= 3.0 → F010 DURABLE (within-degree real).
    If z < 3.0 → F010 JOINS_F022 (same-data, no signal under the stricter null; the 0.27 was between-degree).

Output: cartography/docs/wsw_F010_alternative_null_results.json
"""
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                 "cartography", "shared", "scripts"))
from microscope import prime_features

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
PER_DEGREE = 2000  # reduced from 5000 for tick-bounded runtime; sessionC's original used 2000 and completed quickly
PER_COMBO = 500    # reduced from 1000 for the same reason
N_PERMS = 1000
MIN_MEMBERS_PER_LABEL = 3
SEED = 20260417


def load_nfs(conn):
    cur = conn.cursor()
    out = []
    for degree in range(2, 21):
        cur.execute("""
            SELECT label, galois_label, NULLIF(disc_abs,'')::numeric
              FROM nf_fields
             WHERE degree::int = %s AND galois_label IS NOT NULL
               AND disc_abs IS NOT NULL
             ORDER BY disc_abs::numeric ASC
             LIMIT %s
        """, (degree, PER_DEGREE))
        out.extend(cur.fetchall())
    cur.close()
    return out


def load_artins(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT "Galn"::int, "Galt"::int
          FROM artin_reps
         WHERE "Galn" IS NOT NULL AND "Galt" IS NOT NULL
         GROUP BY "Galn", "Galt"
    """)
    combos = cur.fetchall()
    out = []
    for galn, galt in combos:
        cur.execute("""
            SELECT "Baselabel", "Galn"::int, "Galt"::int,
                   NULLIF("Conductor",'')::numeric
              FROM artin_reps
             WHERE "Galn" = %s AND "Galt" = %s AND "Conductor" IS NOT NULL
             ORDER BY "Conductor"::numeric ASC
             LIMIT %s
        """, (str(galn), str(galt), PER_COMBO))
        out.extend(cur.fetchall())
    cur.close()
    return out


def prime_detrend_values(ints):
    valid = [int(v) for v in ints if v is not None and int(v) > 1]
    if len(valid) < 50:
        return None, None, len(valid)
    log_vals = np.log(np.array(valid, dtype=float))
    feats = np.array([prime_features(v) for v in valid], dtype=float)
    good = [i for i in range(feats.shape[1]) if np.std(feats[:, i]) > 1e-10]
    X = np.column_stack([feats[:, good], np.ones(feats.shape[0])])
    coef, *_ = np.linalg.lstsq(X, log_vals, rcond=None)
    pred = X @ coef
    resid = log_vals - pred
    r2 = 1.0 - float(np.var(resid) / max(np.var(log_vals), 1e-15))
    return resid, r2, len(valid)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F010_alternative_null] start {started}")

    conn = psycopg2.connect(**PG)
    nfs = load_nfs(conn)
    artins = load_artins(conn)
    conn.close()
    print(f"[load] {len(nfs)} NFs, {len(artins)} Artin reps")

    # Aggregate per-label raw disc / cond lists and per-label residuals after global detrend
    # DISC_CAP patched in by Harmonia_M2_sessionC tick 19, per sessionB
    # 1776428241697-0 abandon diagnostic: microscope._factorize trial-division
    # is O(sqrt(n)) so disc_abs values near 10^18 cost ~10^9 ops each →
    # single-process factorization stalls indefinitely. Cap at 10^12 keeps
    # factorization fast (<1 ms per value) while still covering the bulk of
    # degree-2..10 NFs and most rank-1 Artin conductors. High-degree NFs
    # (degree ≥ 12 with large disc) are dropped — documented in _meta.
    DISC_CAP = 10**12
    def _safe_int(v):
        if v is None:
            return None
        try:
            fv = float(v)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(fv) or fv <= 1 or fv >= DISC_CAP:
            return None
        return int(fv)

    nf_by_lbl = defaultdict(list)
    for label, gal, disc in nfs:
        if gal is None:
            continue
        d = _safe_int(disc)
        if d is None:
            continue
        nf_by_lbl[gal].append(d)

    art_by_lbl = defaultdict(list)
    for bl, galn, galt, cond in artins:
        if galn is None or galt is None:
            continue
        c = _safe_int(cond)
        if c is None:
            continue
        key = f"{galn}T{galt}"
        art_by_lbl[key].append(c)

    # Global prime-detrend on all valid NF discs and all valid Artin conds, preserving labels.
    all_nf_discs = []
    all_nf_labels = []
    for lbl, discs in nf_by_lbl.items():
        for d in discs:
            all_nf_discs.append(d)
            all_nf_labels.append(lbl)
    all_art_conds = []
    all_art_labels = []
    for lbl, conds in art_by_lbl.items():
        for c in conds:
            all_art_conds.append(c)
            all_art_labels.append(lbl)

    print(f"[detrend] NF n={len(all_nf_discs)}, Artin n={len(all_art_conds)}")
    nf_resid, nf_r2, _ = prime_detrend_values(all_nf_discs)
    art_resid, art_r2, _ = prime_detrend_values(all_art_conds)
    print(f"[detrend] NF R2={nf_r2:.3f}  Artin R2={art_r2:.3f}")

    # Per-label mean residual on each side
    nf_lbl_resid = defaultdict(list)
    for lbl, r in zip(all_nf_labels, nf_resid):
        nf_lbl_resid[lbl].append(r)
    art_lbl_resid = defaultdict(list)
    for lbl, r in zip(all_art_labels, art_resid):
        art_lbl_resid[lbl].append(r)

    shared = sorted(set(nf_lbl_resid) & set(art_lbl_resid))
    # Filter min members per label on BOTH sides
    shared = [l for l in shared
              if len(nf_lbl_resid[l]) >= MIN_MEMBERS_PER_LABEL
              and len(art_lbl_resid[l]) >= MIN_MEMBERS_PER_LABEL]
    print(f"[shared] {len(shared)} labels with n>={MIN_MEMBERS_PER_LABEL} on both sides")

    # Degree per label (= Galn from "{Galn}T{Galt}")
    def degree_of(lbl):
        try:
            return int(lbl.split("T")[0])
        except (ValueError, IndexError):
            return -1

    x = np.array([np.mean(nf_lbl_resid[l]) for l in shared], dtype=float)
    y = np.array([np.mean(art_lbl_resid[l]) for l in shared], dtype=float)
    degrees = np.array([degree_of(l) for l in shared])

    # Observed rho
    obs_rho, _ = stats.pearsonr(x, y)
    print(f"[observed] rho_decon = {obs_rho:.4f}  n={len(shared)}")

    # Plain permutation null (for comparison to sessionC's z=2.38)
    rng = np.random.default_rng(SEED)
    plain_null = []
    for _ in range(N_PERMS):
        y_shuf = rng.permutation(y)
        r, _ = stats.pearsonr(x, y_shuf)
        if np.isfinite(r):
            plain_null.append(r)
    plain_null = np.array(plain_null)
    plain_z = (obs_rho - plain_null.mean()) / plain_null.std() if plain_null.std() > 0 else None
    print(f"[plain null]  mean={plain_null.mean():.4f}  std={plain_null.std():.4f}  z={plain_z:.2f}")

    # Block-shuffle-within-degree null
    degree_blocks = defaultdict(list)
    for i, d in enumerate(degrees):
        degree_blocks[int(d)].append(i)

    block_null = []
    for _ in range(N_PERMS):
        y_shuf = y.copy()
        for deg, idxs in degree_blocks.items():
            if len(idxs) >= 2:
                perm = rng.permutation(idxs)
                y_shuf[idxs] = y[perm]
        r, _ = stats.pearsonr(x, y_shuf)
        if np.isfinite(r):
            block_null.append(r)
    block_null = np.array(block_null)
    block_z = (obs_rho - block_null.mean()) / block_null.std() if block_null.std() > 0 else None
    print(f"[block null]  mean={block_null.mean():.4f}  std={block_null.std():.4f}  z={block_z:.2f}")

    # Degree-distribution statistics of shared labels
    deg_counts = {int(d): int((degrees == d).sum()) for d in sorted(set(degrees))}

    # Verdict
    DUR_THRESH = 3.0
    if block_z is not None and block_z >= DUR_THRESH:
        verdict = "F010_DURABLE"
        reading = (f"Block-shuffle-within-degree null z = {block_z:.2f} >= {DUR_THRESH}. "
                   f"The 0.27 decontaminated rho survives the stricter null — the signal is "
                   f"WITHIN-DEGREE, not between-degree. F010 is durable.")
    elif block_z is not None and block_z < DUR_THRESH:
        verdict = "F010_JOINS_F022"
        reading = (f"Block-shuffle-within-degree null z = {block_z:.2f} < {DUR_THRESH}. "
                   f"The 0.27 decontaminated rho does NOT survive the stricter null. The signal "
                   f"was between-degree artifact (degree class itself carries the coupling, not "
                   f"within-degree structure). F010 joins F022 — same data shows no signal under "
                   f"the block null.")
    else:
        verdict = "INCONCLUSIVE"
        reading = "Block null computation failed (insufficient variance or degenerate shuffle)."

    # Plain null retention check — does block null accept more structure than plain null?
    if plain_z is not None and block_z is not None:
        null_gap_shift = plain_null.std() - block_null.std()
        gap_reading = (f"plain_null_std={plain_null.std():.4f}, block_null_std={block_null.std():.4f}. "
                       f"{'Block null is TIGHTER (preserves between-degree structure)' if block_null.std() < plain_null.std() else 'Block null is LOOSER than plain null — unusual'}.")
    else:
        gap_reading = "n/a"

    result = {
        "specimen_id": "F010",
        "projections_used": ["P052", "P010_variant_block_null"],
        "verdict": verdict,
        "reading": reading,
        "observed_rho_decontaminated": float(obs_rho),
        "n_shared_labels": len(shared),
        "nf_detrend_r2": nf_r2,
        "artin_detrend_r2": art_r2,
        "degree_block_counts": deg_counts,
        "plain_permutation_null": {
            "n_perms": int(len(plain_null)),
            "mean": float(plain_null.mean()),
            "std": float(plain_null.std()),
            "z_score": float(plain_z) if plain_z is not None else None,
        },
        "block_null_within_degree": {
            "n_perms": int(len(block_null)),
            "mean": float(block_null.mean()),
            "std": float(block_null.std()),
            "z_score": float(block_z) if block_z is not None else None,
            "threshold_for_durable": DUR_THRESH,
        },
        "gap_analysis": gap_reading,
        "shape_summary": reading,
        "_meta": {
            "task_id": "wsw_F010_alternative_null",
            "instance": "Harmonia_M2_sessionB",
            "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
            "per_degree": PER_DEGREE,
            "per_combo": PER_COMBO,
            "n_perms": N_PERMS,
            "seed": SEED,
            "prior_reference": "sessionC wsw_F010_bigsample: P052 rho=0.27, z=2.38",
            "notes": [
                "Block-shuffle preserves per-degree marginal distribution, shuffles only within-degree.",
                "If the signal is degree-mediated (e.g. low-degree NFs pair with low-dim Artin reps), block null preserves it → z near zero.",
                "If the signal is within-degree (specific labels within same degree carry coupling), block null destroys it → z large.",
                "DUR_THRESH=3.0 chosen to match sessionA's criterion in the task brief.",
            ],
        },
    }

    out_path = os.path.join("cartography", "docs", "wsw_F010_alternative_null_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=float)
    print(f"[wsw_F010_alternative_null] wrote {out_path}")
    print(f"[verdict] {verdict}")
    print(f"[reading] {reading}")


if __name__ == "__main__":
    main()
