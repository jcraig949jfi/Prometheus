"""
wsw_F010_bigsample.py — F010 coupling significance firm-up at larger n.

Task: wsw_F010_bigsample, claimed by Harmonia_M2_sessionC.
Motivation: prior wsw_F010_P052 gave rho_decon=0.269 with z=1.80 at n_shared=62 (borderline).
sessionA seeded this task targeting n_shared >= 500 via per_degree=5000, per_combo=1000.
If z jumps > 3.5 at the larger sample, F010 is the strongest non-prime-mediated specimen.

Method: identical to wsw_F010_P052 but with larger per-stratum caps.
Projections reported: P010 baseline (raw log-values) and P052 decontaminated.
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

PER_DEGREE = 5000
PER_COMBO = 1000
N_PERMS = 300
MIN_MEMBERS_PER_LABEL = 3


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
    arr = np.array([int(v) for v in ints], dtype=object)
    mask = np.array([(v is not None and int(v) > 1) for v in arr])
    valid_vals = np.array([int(v) for v in arr[mask]], dtype=np.int64)
    if valid_vals.size < 50:
        return None, None, int(valid_vals.size)
    log_vals = np.log(valid_vals.astype(float))
    feats = np.array([prime_features(int(v)) for v in valid_vals], dtype=float)
    good = [i for i in range(feats.shape[1]) if np.std(feats[:, i]) > 1e-10]
    X = np.column_stack([feats[:, good], np.ones(feats.shape[0])])
    try:
        coef, *_ = np.linalg.lstsq(X, log_vals, rcond=None)
        pred = X @ coef
        resid = log_vals - pred
        r2 = 1.0 - float(np.var(resid) / max(np.var(log_vals), 1e-15))
    except Exception:
        return None, None, int(valid_vals.size)
    return resid, r2, int(valid_vals.size)


def paired_coupling(nf_lbls, nf_vals, art_lbls, art_vals):
    nf_by = defaultdict(list)
    for l, v in zip(nf_lbls, nf_vals):
        if l is not None and np.isfinite(v):
            nf_by[l].append(float(v))
    art_by = defaultdict(list)
    for l, v in zip(art_lbls, art_vals):
        if np.isfinite(v):
            art_by[l].append(float(v))
    shared = [l for l in set(nf_by) & set(art_by)
              if len(nf_by[l]) >= MIN_MEMBERS_PER_LABEL
              and len(art_by[l]) >= MIN_MEMBERS_PER_LABEL]
    if len(shared) < 10:
        return None, shared
    x = np.array([np.mean(nf_by[l]) for l in shared])
    y = np.array([np.mean(art_by[l]) for l in shared])
    if x.std() < 1e-12 or y.std() < 1e-12:
        return {"rho": None, "n": len(shared)}, shared
    rho, _ = stats.pearsonr(x, y)
    return {"rho": float(rho), "n": len(shared)}, shared


def permutation_null(nf_lbls, nf_vals, art_lbls, art_vals, n_perms, seed=42):
    rng = np.random.default_rng(seed)
    nf_lbls = list(nf_lbls)
    nulls = []
    for _ in range(n_perms):
        perm = rng.permutation(nf_lbls)
        res, _ = paired_coupling(perm, nf_vals, art_lbls, art_vals)
        if res and res.get("rho") is not None:
            nulls.append(res["rho"])
    return np.array(nulls, dtype=float)


def z_and_verdict(rho, nulls, label):
    if rho is None or nulls.size == 0:
        return None, None, "0"
    null_mean = float(nulls.mean())
    null_std = float(nulls.std())
    z = float((rho - null_mean) / null_std) if null_std > 1e-10 else None
    if z is None:
        verdict = "0"
    elif z >= 3.5:
        verdict = "+1_strong"
    elif z >= 3.0:
        verdict = "+1"
    elif z <= -3.0:
        verdict = "0"  # wrong sign
    elif abs(rho) < 0.10:
        verdict = "-1"
    else:
        verdict = "0"
    return z, {"mean": null_mean, "std": null_std}, verdict


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F010_bigsample] start {started}")

    with psycopg2.connect(**PG) as conn:
        nfs = load_nfs(conn)
        artins = load_artins(conn)
    print(f"[wsw_F010_bigsample] loaded NFs={len(nfs)} Artin={len(artins)}")

    def _safe_int(v, cap=10**18):
        try:
            f = float(v)
            if not math.isfinite(f) or f < 2 or f > cap:
                return None
            return int(f)
        except Exception:
            return None

    nf_pairs = [(r[1], _safe_int(r[2])) for r in nfs]
    nf_pairs = [(l, v) for l, v in nf_pairs if l is not None and v is not None]
    nf_lbls = [l for l, _ in nf_pairs]
    nf_vals = [v for _, v in nf_pairs]

    art_pairs = [(f"{r[1]}T{r[2]}", _safe_int(r[3])) for r in artins]
    art_pairs = [(l, v) for l, v in art_pairs if v is not None]
    art_lbls = [l for l, _ in art_pairs]
    art_vals = [v for _, v in art_pairs]

    print(f"[wsw_F010_bigsample] NF post-filter={len(nf_vals)} Artin post-filter={len(art_vals)}")

    nf_log = [math.log(v) for v in nf_vals]
    art_log = [math.log(v) for v in art_vals]

    # P010 baseline (raw log-values)
    base_res, base_shared = paired_coupling(nf_lbls, nf_log, art_lbls, art_log)
    base_nulls = permutation_null(nf_lbls, nf_log, art_lbls, art_log, N_PERMS)
    z_base, null_base, verdict_base = z_and_verdict(base_res["rho"] if base_res else None,
                                                     base_nulls, "P010")
    print(f"[wsw_F010_bigsample] P010 rho={base_res['rho']:.4f} z={z_base:.2f} n={len(base_shared)}")

    # P052 decontaminated
    nf_resid, nf_r2, _ = prime_detrend_values(nf_vals)
    art_resid, art_r2, _ = prime_detrend_values(art_vals)
    print(f"[wsw_F010_bigsample] prime-detrend NF r2={nf_r2:.4f} Artin r2={art_r2:.4f}")

    decon_res, decon_shared = paired_coupling(nf_lbls, nf_resid, art_lbls, art_resid)
    decon_nulls = permutation_null(nf_lbls, nf_resid, art_lbls, art_resid, N_PERMS)
    z_decon, null_decon, verdict_decon = z_and_verdict(
        decon_res["rho"] if decon_res else None, decon_nulls, "P052")
    print(f"[wsw_F010_bigsample] P052 rho={decon_res['rho']:.4f} z={z_decon:.2f} n={len(decon_shared)}")

    retention = (decon_res["rho"] / base_res["rho"]
                 if base_res and base_res.get("rho") and decon_res and decon_res.get("rho")
                 else None)

    results = {
        "task_id": "wsw_F010_bigsample",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "sample_config": {
            "per_degree": PER_DEGREE,
            "per_combo": PER_COMBO,
            "n_perms": N_PERMS,
            "min_members_per_label": MIN_MEMBERS_PER_LABEL,
        },
        "n_loaded": {"nfs": len(nfs), "artins": len(artins),
                     "nfs_post_filter": len(nf_vals), "artins_post_filter": len(art_vals)},
        "P010": {
            "description": "baseline: mean log(disc_abs) ↔ mean log(Conductor) across Galois labels",
            "rho": base_res["rho"] if base_res else None,
            "n_shared": len(base_shared),
            "null_mean": null_base["mean"] if null_base else None,
            "null_std": null_base["std"] if null_base else None,
            "z_score": z_base,
            "verdict": verdict_base,
        },
        "P052": {
            "description": "prime-detrend residuals on both sides, same coupling",
            "rho": decon_res["rho"] if decon_res else None,
            "n_shared": len(decon_shared),
            "null_mean": null_decon["mean"] if null_decon else None,
            "null_std": null_decon["std"] if null_decon else None,
            "z_score": z_decon,
            "verdict": verdict_decon,
            "prime_detrend_r2_nf": nf_r2,
            "prime_detrend_r2_artin": art_r2,
        },
        "retention_ratio_decon_vs_raw": retention,
        "threshold_crossed": {
            "z_decon_ge_3_0": (z_decon is not None and z_decon >= 3.0),
            "z_decon_ge_3_5": (z_decon is not None and z_decon >= 3.5),
        },
        "shape_summary": None,  # filled below
        "verdict_final": (
            "F010_STRONG_NONPRIME" if (z_decon is not None and z_decon >= 3.5) else
            "F010_SIGNIFICANT_NONPRIME" if (z_decon is not None and z_decon >= 3.0) else
            "F010_BORDERLINE_STILL"
        ),
        "notes": [
            f"Per-degree cap raised to {PER_DEGREE}, per-combo cap {PER_COMBO}",
            "NF 10^18 cap still applied (rare extreme-large disc from high degrees filtered)",
            "If threshold_crossed.z_decon_ge_3_5 is True, F010 becomes strongest non-prime-mediated specimen per sessionA criterion",
        ],
    }

    # Fix the shape_summary f-string conditional (same bug as before)
    retention_str = "n/a" if retention is None else f"{retention:.2f}"
    results["shape_summary"] = (
        f"F010 bigsample (per_degree={PER_DEGREE}): "
        f"P010 rho={base_res['rho']:.3f} z={z_base:.2f} n={len(base_shared)}; "
        f"P052 rho={decon_res['rho']:.3f} z={z_decon:.2f} n={len(decon_shared)}. "
        f"retention={retention_str}"
    )

    out_path = os.path.join("cartography", "docs", "wsw_F010_bigsample_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[wsw_F010_bigsample] wrote {out_path}")
    print(f"[wsw_F010_bigsample] verdict={results['verdict_final']}")


if __name__ == "__main__":
    main()
