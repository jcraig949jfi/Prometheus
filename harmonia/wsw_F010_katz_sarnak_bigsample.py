"""
wsw_F010_katz_sarnak_bigsample.py — Is_Even-stratified F010 coupling at per_degree=5000.

Task: wsw_F010_katz_sarnak_bigsample, claimed by Harmonia_M2_sessionC.

Critical test:
  sessionB wsw_F010_katz_sarnak (per_degree=2000, n_shared=107):
    Is_Even=True  rho=0.77 (n=56)
    Is_Even=False rho=-0.05 (n=51)
    Fisher z=5.38, p~1e-7

  sessionC wsw_F010_bigsample (per_degree=5000, n_shared=75):
    pooled rho=0.109 (collapsed from 0.404 — Pattern 20 artifact)

If the Is_Even=True stratum rho stays near 0.77 at per_degree=5000, P028 is the
real F010 resolver. If it collapses, sessionB saw the same artifact sliced.
"""
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2
from scipy import stats

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

PER_DEGREE = 5000
PER_COMBO = 1000
MIN_MEMBERS_PER_LABEL = 3
N_PERMS = 300


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
                   NULLIF("Conductor",'')::numeric,
                   "Is_Even", "Dim"::int
            FROM artin_reps
            WHERE "Galn" = %s AND "Galt" = %s AND "Conductor" IS NOT NULL
            ORDER BY "Conductor"::numeric ASC
            LIMIT %s
        """, (str(galn), str(galt), PER_COMBO))
        out.extend(cur.fetchall())
    cur.close()
    return out


def safe_int(v, cap=10**18):
    try:
        f = float(v)
        if not math.isfinite(f) or f < 2 or f > cap:
            return None
        return int(f)
    except Exception:
        return None


def coupling_on_subset(nf_lbls, nf_log, art_lbls, art_log):
    """Pearson rho of (mean_log_disc, mean_log_cond) across shared Galois labels."""
    nf_by = defaultdict(list)
    for l, v in zip(nf_lbls, nf_log):
        nf_by[l].append(v)
    art_by = defaultdict(list)
    for l, v in zip(art_lbls, art_log):
        art_by[l].append(v)
    shared = [l for l in set(nf_by) & set(art_by)
              if len(nf_by[l]) >= MIN_MEMBERS_PER_LABEL
              and len(art_by[l]) >= MIN_MEMBERS_PER_LABEL]
    if len(shared) < 10:
        return {"rho": None, "n_shared": len(shared), "skipped": "n_shared<10"}
    x = np.array([np.mean(nf_by[l]) for l in shared])
    y = np.array([np.mean(art_by[l]) for l in shared])
    if x.std() < 1e-12 or y.std() < 1e-12:
        return {"rho": 0.0, "n_shared": len(shared), "skipped": "zero variance"}
    rho, _ = stats.pearsonr(x, y)
    return {"rho": float(rho), "n_shared": len(shared)}


def permutation_null(nf_lbls, nf_log, art_lbls, art_log, n_perms, seed=42):
    rng = np.random.default_rng(seed)
    nulls = []
    labels_cp = list(nf_lbls)
    for _ in range(n_perms):
        perm = rng.permutation(labels_cp)
        r = coupling_on_subset(perm, nf_log, art_lbls, art_log)
        if r.get("rho") is not None:
            nulls.append(r["rho"])
    return np.array(nulls, dtype=float)


def z_score(rho, nulls):
    if rho is None or nulls.size == 0:
        return None, None, None
    m = float(nulls.mean())
    s = float(nulls.std())
    z = float((rho - m) / s) if s > 1e-10 else None
    return z, m, s


def fisher_z_diff(rho1, n1, rho2, n2):
    """Fisher-z test for difference of two correlations (independent samples)."""
    if None in (rho1, rho2) or n1 < 4 or n2 < 4 or abs(rho1) >= 1 or abs(rho2) >= 1:
        return None
    z1 = 0.5 * math.log((1 + rho1) / (1 - rho1))
    z2 = 0.5 * math.log((1 + rho2) / (1 - rho2))
    se = math.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
    if se == 0:
        return None
    return (z1 - z2) / se


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F010_ks_bigsample] start {started}")

    with psycopg2.connect(**PG) as conn:
        nfs = load_nfs(conn)
        artins = load_artins(conn)
    print(f"[wsw_F010_ks_bigsample] NFs={len(nfs)} Artins={len(artins)}")

    # NF side: (label, galois_label, disc_abs) - no Is_Even on NF side.
    # But stratify the ARTIN side by Is_Even; NF side's galois_label carries
    # no parity info. The shared set of galois labels is defined by intersection.
    nf_vals = []
    nf_lbls = []
    for r in nfs:
        v = safe_int(r[2])
        if r[1] is None or v is None:
            continue
        nf_lbls.append(r[1])
        nf_vals.append(math.log(v))

    # Bucket Artin rows by (Is_Even, Dim) combinations.
    art_rows = []
    for bl, galn, galt, cond, is_even, dim in artins:
        v = safe_int(cond)
        if v is None or is_even is None or dim is None:
            continue
        art_rows.append({
            "label": f"{galn}T{galt}",
            "log_cond": math.log(v),
            "is_even": bool(is_even) if isinstance(is_even, bool) else (str(is_even).lower() == "true"),
            "dim": int(dim),
        })
    print(f"[wsw_F010_ks_bigsample] Artin post-filter={len(art_rows)}")

    def subset(rows, **filters):
        out_lbls, out_vals = [], []
        for r in rows:
            if all(r[k] == v for k, v in filters.items()):
                out_lbls.append(r["label"])
                out_vals.append(r["log_cond"])
        return out_lbls, out_vals

    # Primary: Is_Even=True vs Is_Even=False, at larger n
    splits = {}

    # Pooled baseline (all Artins)
    a_lbl, a_log = [r["label"] for r in art_rows], [r["log_cond"] for r in art_rows]
    r_pool = coupling_on_subset(nf_lbls, nf_vals, a_lbl, a_log)
    nulls_pool = permutation_null(nf_lbls, nf_vals, a_lbl, a_log, N_PERMS)
    z_pool, m_pool, s_pool = z_score(r_pool.get("rho"), nulls_pool)
    splits["pooled_all_artin"] = {**r_pool, "z": z_pool, "null_mean": m_pool, "null_std": s_pool}
    print(f"[wsw_F010_ks_bigsample] pooled rho={r_pool.get('rho')} n={r_pool.get('n_shared')} z={z_pool}")

    # Is_Even=True
    a_lbl, a_log = subset(art_rows, is_even=True)
    r_even = coupling_on_subset(nf_lbls, nf_vals, a_lbl, a_log)
    nulls_even = permutation_null(nf_lbls, nf_vals, a_lbl, a_log, N_PERMS)
    z_even, m_even, s_even = z_score(r_even.get("rho"), nulls_even)
    splits["is_even_true"] = {**r_even, "z": z_even, "null_mean": m_even, "null_std": s_even,
                               "n_artin_rows": len(a_lbl)}
    print(f"[wsw_F010_ks_bigsample] Is_Even=True  rho={r_even.get('rho')} n={r_even.get('n_shared')} z={z_even}")

    # Is_Even=False
    a_lbl, a_log = subset(art_rows, is_even=False)
    r_odd = coupling_on_subset(nf_lbls, nf_vals, a_lbl, a_log)
    nulls_odd = permutation_null(nf_lbls, nf_vals, a_lbl, a_log, N_PERMS)
    z_odd, m_odd, s_odd = z_score(r_odd.get("rho"), nulls_odd)
    splits["is_even_false"] = {**r_odd, "z": z_odd, "null_mean": m_odd, "null_std": s_odd,
                                "n_artin_rows": len(a_lbl)}
    print(f"[wsw_F010_ks_bigsample] Is_Even=False rho={r_odd.get('rho')} n={r_odd.get('n_shared')} z={z_odd}")

    # Is_Even × Dim splits
    for dim in [1, 2, 4]:
        for ie in [True, False]:
            a_lbl, a_log = subset(art_rows, is_even=ie, dim=dim)
            r = coupling_on_subset(nf_lbls, nf_vals, a_lbl, a_log)
            key = f"is_even_{ie}_dim_{dim}"
            splits[key] = {**r, "n_artin_rows": len(a_lbl)}

    # Between-split Fisher z for parity contrast
    fz = fisher_z_diff(r_even.get("rho"), r_even.get("n_shared", 0),
                       r_odd.get("rho"), r_odd.get("n_shared", 0))

    # Compare to sessionB small-n
    sessionB = {"is_even_true": {"rho": 0.77, "n": 56},
                "is_even_false": {"rho": -0.05, "n": 51},
                "fisher_z_diff": 5.38}
    # This run
    thisrun = {"is_even_true": {"rho": r_even.get("rho"), "n": r_even.get("n_shared")},
               "is_even_false": {"rho": r_odd.get("rho"), "n": r_odd.get("n_shared")},
               "fisher_z_diff": fz}

    # Verdict
    even_rho = r_even.get("rho")
    if even_rho is None:
        verdict = "INCONCLUSIVE"
    elif even_rho >= 0.50 and (r_even.get("n_shared", 0) >= 30):
        verdict = "P028_CONFIRMED_RESOLVER"
    elif even_rho >= 0.20 and fz is not None and fz >= 3.0:
        verdict = "P028_RESOLVER_WEAKENED_BUT_PERSISTS"
    elif even_rho < 0.20:
        verdict = "P028_PATTERN20_ARTIFACT"
    else:
        verdict = "P028_INCONCLUSIVE"

    results = {
        "task_id": "wsw_F010_katz_sarnak_bigsample",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "per_degree": PER_DEGREE,
        "per_combo": PER_COMBO,
        "min_members_per_label": MIN_MEMBERS_PER_LABEL,
        "n_perms": N_PERMS,
        "splits": splits,
        "comparison_to_sessionB_smalln": {
            "sessionB": sessionB,
            "this_run": thisrun,
            "rho_even_delta": (even_rho - sessionB["is_even_true"]["rho"]
                                if even_rho is not None else None),
        },
        "verdict": verdict,
        "shape_summary": (
            f"F010 K-S at per_degree={PER_DEGREE}: Is_Even=True rho="
            f"{r_even.get('rho')} n={r_even.get('n_shared')} z={z_even}; "
            f"Is_Even=False rho={r_odd.get('rho')} n={r_odd.get('n_shared')} z={z_odd}; "
            f"Fisher z_diff={fz}. Verdict: {verdict}"
        ),
        "notes": [
            "sessionB's small-n values were rho=0.77 at Is_Even=True (n=56) and rho=-0.05 at Is_Even=False (n=51), Fisher z_diff=5.38.",
            "If Is_Even=True rho stays >= 0.5 at per_degree=5000 with n >= 30, P028 is the real F010 resolver (Pattern 20 does NOT apply — stratification sharpens rather than collapses).",
            "If Is_Even=True rho collapses (<0.2), sessionB saw a sliced version of the same Pattern-20 pooling artifact.",
        ],
    }

    out = os.path.join("cartography", "docs", "wsw_F010_katz_sarnak_bigsample_results.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[wsw_F010_ks_bigsample] wrote {out}")
    print(f"[wsw_F010_ks_bigsample] verdict: {verdict}")


if __name__ == "__main__":
    main()
