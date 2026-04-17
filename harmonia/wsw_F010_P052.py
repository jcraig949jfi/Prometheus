"""
wsw_F010_P052.py — P052 microscope decontamination on F010 coupling.

Task: wsw_F010_P052, claimed by Harmonia_M2_sessionC.
Reference: cartography/docs/wsw_F010_results.json (sessionC, 2026-04-17)
  -> prior result: P010 rho=0.404, 71 shared Galois labels; P052 deferred.

Method:
  1. Load NF (disc_abs) and Artin (Conductor) samples as in wsw_F010.
  2. Apply microscope Layer 1 (prime detrend) to each side's integer values:
     regress log(value) on prime-factorization features
     (n_distinct, total_exp, log(largest_prime), log(smallest_prime),
     is_prime, smoothness), use residual as the "decontaminated log-value".
  3. Aggregate residuals per Galois label (mean).
  4. Compute Pearson rho across shared Galois labels on decontaminated side.
  5. Run label permutation null for significance.
  6. Compare to baseline rho=0.404 from prior task.

Verdict convention (tensor invariance):
  +1  F010 survives P052 (decontaminated rho still z >= 3)
   0  inconclusive boundary
  -1  F010 collapses under P052 (coupling was prime-mediated)
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
from microscope import prime_features  # Layer 1 feature extractor

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

PER_DEGREE = 2000
PER_COMBO = 300
N_PERMS = 200
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
    """Given a list of integers > 1, return (residuals, r2, n_used, model_info).

    Model: log(value) ~ prime_features(value) + intercept, OLS.
    Residuals have same length and ordering as the filtered input set.
    Returns also the mask so callers can re-index their parallel arrays.
    """
    arr = np.array([int(v) for v in ints], dtype=object)
    # Keep indices to re-pair with labels
    mask = np.array([(v is not None and int(v) > 1) for v in arr])
    valid_vals = np.array([int(v) for v in arr[mask]], dtype=np.int64)
    if valid_vals.size < 50:
        return None, None, int(valid_vals.size), None
    log_vals = np.log(valid_vals.astype(float))
    feats = np.array([prime_features(int(v)) for v in valid_vals], dtype=float)
    # drop constant columns
    good = [i for i in range(feats.shape[1]) if np.std(feats[:, i]) > 1e-10]
    X = np.column_stack([feats[:, good], np.ones(feats.shape[0])])
    try:
        coef, *_ = np.linalg.lstsq(X, log_vals, rcond=None)
        pred = X @ coef
        resid = log_vals - pred
        r2 = 1.0 - float(np.var(resid) / max(np.var(log_vals), 1e-15))
    except Exception:
        return None, None, int(valid_vals.size), None
    return resid, r2, int(valid_vals.size), {
        "good_cols": good,
        "coef": coef.tolist(),
    }


def aggregate_residuals_by_label(labels, resids):
    out = defaultdict(list)
    for lbl, r in zip(labels, resids):
        if lbl is not None and np.isfinite(r):
            out[lbl].append(float(r))
    return out


def paired_coupling(nf_lbls, nf_resids, art_lbls, art_resids):
    nf_by = aggregate_residuals_by_label(nf_lbls, nf_resids)
    art_by = aggregate_residuals_by_label(art_lbls, art_resids)
    shared = [l for l in set(nf_by) & set(art_by)
              if len(nf_by[l]) >= MIN_MEMBERS_PER_LABEL
              and len(art_by[l]) >= MIN_MEMBERS_PER_LABEL]
    if len(shared) < 10:
        return None, shared
    x = np.array([np.mean(nf_by[l]) for l in shared])
    y = np.array([np.mean(art_by[l]) for l in shared])
    if x.std() < 1e-12 or y.std() < 1e-12:
        return {"rho": None, "n": len(shared), "error": "zero variance"}, shared
    rho, _ = stats.pearsonr(x, y)
    return {"rho": float(rho), "n": len(shared)}, shared


def permutation_null(nf_lbls, nf_resids, art_lbls, art_resids, n_perms, seed=42):
    rng = np.random.default_rng(seed)
    # We permute NF galois labels among NFs, so the NF-side residuals lose their
    # label identity but keep their distributional shape.
    nf_lbls = list(nf_lbls)
    nulls = []
    for _ in range(n_perms):
        perm = rng.permutation(nf_lbls)
        res, _ = paired_coupling(perm, nf_resids, art_lbls, art_resids)
        if res and res.get("rho") is not None:
            nulls.append(res["rho"])
    return np.array(nulls, dtype=float)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F010_P052] start {started}")

    with psycopg2.connect(**PG) as conn:
        nfs = load_nfs(conn)
        artins = load_artins(conn)
    print(f"[wsw_F010_P052] loaded {len(nfs)} NFs, {len(artins)} Artin reps")

    def _safe_int(v, cap=10**18):
        try:
            f = float(v)
            if not math.isfinite(f) or f < 2 or f > cap:
                return None
            return int(f)
        except Exception:
            return None

    nf_pairs = [(r[1], _safe_int(r[2])) for r in nfs]
    nf_pairs = [(lbl, v) for lbl, v in nf_pairs if lbl is not None and v is not None]
    nf_lbls = [lbl for lbl, _ in nf_pairs]
    nf_vals = [v for _, v in nf_pairs]

    art_pairs = [(f"{r[1]}T{r[2]}", _safe_int(r[3])) for r in artins]
    art_pairs = [(lbl, v) for lbl, v in art_pairs if v is not None]
    art_lbls = [lbl for lbl, _ in art_pairs]
    art_vals = [v for _, v in art_pairs]

    print(f"[wsw_F010_P052] NF objects (post small-int filter disc>1): {len(nf_vals)}")
    print(f"[wsw_F010_P052] Artin objects (post small-int filter cond>1): {len(art_vals)}")

    # Baseline rho (raw log-values, no decontamination) — recompute for comparison.
    nf_log_raw = [math.log(v) for v in nf_vals]
    art_log_raw = [math.log(v) for v in art_vals]
    base_res, base_shared = paired_coupling(nf_lbls, nf_log_raw, art_lbls, art_log_raw)
    print(f"[wsw_F010_P052] raw baseline rho={base_res['rho'] if base_res else None} n_shared={len(base_shared)}")

    # Layer 1: prime detrend on each side.
    nf_resid, nf_r2, nf_n, nf_model = prime_detrend_values(nf_vals)
    art_resid, art_r2, art_n, art_model = prime_detrend_values(art_vals)
    print(f"[wsw_F010_P052] NF prime-detrend r2={nf_r2:.4f} n={nf_n}")
    print(f"[wsw_F010_P052] Artin prime-detrend r2={art_r2:.4f} n={art_n}")

    # Decontaminated coupling
    decon_res, decon_shared = paired_coupling(nf_lbls, nf_resid, art_lbls, art_resid)
    print(f"[wsw_F010_P052] decontaminated rho={decon_res['rho'] if decon_res else None} n_shared={len(decon_shared)}")

    # Permutation null on decontaminated data
    nulls = permutation_null(nf_lbls, nf_resid, art_lbls, art_resid, N_PERMS)
    if nulls.size:
        null_mean = float(nulls.mean())
        null_std = float(nulls.std())
        z = ((decon_res["rho"] - null_mean) / null_std) if null_std > 1e-10 else None
        p_perm = float(np.mean(np.abs(nulls) >= abs(decon_res["rho"]))) if decon_res["rho"] else None
    else:
        null_mean = null_std = z = p_perm = None

    decon_rho = decon_res["rho"] if decon_res else None

    # Verdict per task spec: rho > 0.20 post-decontamination = survives
    if decon_rho is None:
        verdict = "0"
    elif abs(decon_rho) >= 0.20 and z is not None and z >= 3.0:
        verdict = "+1"
    elif abs(decon_rho) < 0.10:
        verdict = "-1"
    else:
        verdict = "0"

    retention_abs = (abs(decon_rho) if decon_rho is not None else 0.0)
    retention_ratio = (retention_abs / abs(base_res["rho"])
                       if base_res and base_res["rho"] else None)

    results = {
        "task_id": "wsw_F010_P052",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "baseline_rho_raw": base_res["rho"] if base_res else None,
        "baseline_n_shared": len(base_shared),
        "prior_task_baseline": {
            "rho": 0.404, "z": 4.07, "n_shared": 71,
            "source": "cartography/docs/wsw_F010_results.json (sessionC)",
        },
        "layer_1_prime_detrend": {
            "nf_r2": nf_r2, "nf_n": nf_n,
            "artin_r2": art_r2, "artin_n": art_n,
            "note": ("r2 = fraction of log(value) variance explained by prime features "
                     "(n_distinct, total_exp, log_largest_prime, log_smallest_prime, "
                     "is_prime, smoothness). High r2 means the side is heavily "
                     "prime-structured; low r2 means log(value) has non-prime info."),
        },
        "decontaminated_coupling": {
            "rho": decon_rho,
            "n_shared_labels": len(decon_shared),
            "null_mean": null_mean,
            "null_std": null_std,
            "z_score": z,
            "p_perm": p_perm,
            "n_perms": N_PERMS,
        },
        "retention_ratio_vs_baseline": retention_ratio,
        "verdict": verdict,
        "verdict_rule": ("+1 if |rho_decon| >= 0.20 AND z >= 3; "
                         "-1 if |rho_decon| < 0.10; else 0"),
        "shape_summary": (
            "F010 P052 microscope decontamination: baseline raw rho="
            f"{base_res['rho']:.3f}"
            f" -> prime-detrended rho={'nan' if decon_rho is None else f'{decon_rho:.3f}'}"
            f" (z={'n/a' if z is None else f'{z:.2f}'}, n={len(decon_shared)})."
            f" retention={'n/a' if retention_ratio is None else f'{retention_ratio:.2f}'}."
            f" verdict={verdict}."
        ),
        "notes": [
            "microscope Layer 1 only (prime detrend). Layer 2 (small-int filter) applied pre-detrend via disc/cond > 1. Layer 3 (rank/fractional) deferred — Layer 1 alone is the conventional first-pass microscope.",
            "z uses label-permutation null on NF side, N_PERMS=200.",
            "This sharpens the F010 entry: if P052 verdict is +1, F010 graduates past the 96%-prime-mediated default and becomes stronger than most prior coupling findings.",
        ],
    }

    out_path = os.path.join("cartography", "docs", "wsw_F010_P052_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[wsw_F010_P052] wrote {out_path}")
    print(f"[wsw_F010_P052] verdict={verdict}  decon_rho={decon_rho}  z={z}")


if __name__ == "__main__":
    main()
