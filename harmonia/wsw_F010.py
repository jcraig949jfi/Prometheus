"""
wsw_F010.py — Weak Signal Walk on F010 (NF backbone via Galois-label coupling).

Task: wsw_F010, claimed by Harmonia_M2_sessionC, 2026-04-17.
Projections requested: P010, P020, P021, P042, P052.

Baseline F010 result (prior work): rho=0.40, z=3.64 over 114 shared Galois labels,
via categorical object-keyed scorer on (NF.log(disc_abs), Artin.log(Conductor)).

Method per projection:
  P010 — baseline: re-measure rho with Galois-label permutation null (100 perms).
  P020 — conductor conditioning: bin shared labels by mean_log_disc, within-bin rho
         and pooled-within-bin rho.
  P021 — bad-prime count stratification: bin shared labels by mean NF num_ram,
         within-stratum rho.
  P042 — feature permutation (ad hoc): compare rho(log_disc, log_cond) to
         rho(log_class_number, log_cond). Drop = feature-identity matters;
         preserved = feature-encoding-dependent artifact. This is a minimum
         implementation of the proposed P042 null.
  P052 — DEFERRED. Microscope decontamination requires integration work beyond
         this tick; recorded as 'deferred' with note.

Output: cartography/docs/wsw_F010_results.json

Discipline notes:
  - Pattern 4: balanced per-degree / per-(Galn,Galt) sampling (no LIMIT-without-stratification).
  - Pattern 7: no calibration-anchor dependence touched here.
  - Output verdict convention matches tensor invariance:
      +1 = projection resolves F010 (rho significantly > null)
       0 = inconclusive / boundary z
      -1 = projection collapses F010 (rho indistinguishable from null or < threshold)
"""
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import psycopg2
from scipy import stats

PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

PER_DEGREE = 2000
PER_COMBO = 300
N_PERMS = 100
MIN_MEMBERS_PER_LABEL = 3
MIN_SHARED_FOR_RHO = 10


def load_nfs(conn):
    cur = conn.cursor()
    out = []
    for degree in range(2, 21):
        cur.execute("""
            SELECT label, degree::int, galois_label,
                   NULLIF(class_number,'')::numeric,
                   NULLIF(disc_abs,'')::numeric,
                   NULLIF(num_ram,'')::int
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
        SELECT "Galn"::int AS galn, "Galt"::int AS galt
        FROM artin_reps
        WHERE "Galn" IS NOT NULL AND "Galt" IS NOT NULL
        GROUP BY "Galn", "Galt"
    """)
    combos = cur.fetchall()
    out = []
    for galn, galt in combos:
        cur.execute("""
            SELECT "Baselabel", "Dim"::int, "Galn"::int, "Galt"::int,
                   NULLIF("Conductor",'')::numeric,
                   NULLIF("NumBadPrimes",'')::int
            FROM artin_reps
            WHERE "Galn" = %s AND "Galt" = %s AND "Conductor" IS NOT NULL
            ORDER BY "Conductor"::numeric ASC
            LIMIT %s
        """, (str(galn), str(galt), PER_COMBO))
        out.extend(cur.fetchall())
    cur.close()
    return out


def aggregate_labels(nfs, artins):
    """Return dict label -> {nf: {...}, art: {...}}."""
    nf_agg = defaultdict(lambda: {"disc": [], "cn": [], "num_ram": []})
    for lbl, deg, gal, cn, da, nr in nfs:
        if gal is None or da is None or float(da) <= 0:
            continue
        nf_agg[gal]["disc"].append(float(da))
        if cn is not None and float(cn) > 0:
            nf_agg[gal]["cn"].append(float(cn))
        if nr is not None:
            nf_agg[gal]["num_ram"].append(int(nr))

    art_agg = defaultdict(lambda: {"cond": [], "nbp": []})
    for bl, dim, galn, galt, cond, nbp in artins:
        if galn is None or galt is None or cond is None or float(cond) <= 0:
            continue
        key = f"{galn}T{galt}"
        art_agg[key]["cond"].append(float(cond))
        if nbp is not None:
            art_agg[key]["nbp"].append(int(nbp))

    merged = {}
    for lbl in set(nf_agg) & set(art_agg):
        if (len(nf_agg[lbl]["disc"]) < MIN_MEMBERS_PER_LABEL or
                len(art_agg[lbl]["cond"]) < MIN_MEMBERS_PER_LABEL):
            continue
        merged[lbl] = {
            "n_nf": len(nf_agg[lbl]["disc"]),
            "n_art": len(art_agg[lbl]["cond"]),
            "mean_log_disc": float(np.mean(np.log(nf_agg[lbl]["disc"]))),
            "mean_log_cn": float(np.mean(np.log(nf_agg[lbl]["cn"])))
                           if nf_agg[lbl]["cn"] else None,
            "mean_log_cond": float(np.mean(np.log(art_agg[lbl]["cond"]))),
            "mean_num_ram": float(np.mean(nf_agg[lbl]["num_ram"]))
                           if nf_agg[lbl]["num_ram"] else None,
            "mean_nbp": float(np.mean(art_agg[lbl]["nbp"]))
                       if art_agg[lbl]["nbp"] else None,
        }
    return merged


def pearson(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if x.size < MIN_SHARED_FOR_RHO or x.std() < 1e-10 or y.std() < 1e-10:
        return None, int(x.size)
    rho, _ = stats.pearsonr(x, y)
    if not np.isfinite(rho):
        return None, int(x.size)
    return float(rho), int(x.size)


def permutation_null(labels, merged, n_perms, feature="mean_log_disc",
                     target="mean_log_cond", seed=42):
    rng = np.random.default_rng(seed)
    x = np.array([merged[l][feature] for l in labels], dtype=float)
    y = np.array([merged[l][target] for l in labels], dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if x.size < MIN_SHARED_FOR_RHO:
        return None
    real_rho, _ = stats.pearsonr(x, y)
    nulls = []
    for _ in range(n_perms):
        ry = rng.permutation(y)
        rho, _ = stats.pearsonr(x, ry)
        if np.isfinite(rho):
            nulls.append(rho)
    nulls = np.array(nulls)
    null_mean = float(nulls.mean()) if nulls.size else 0.0
    null_std = float(nulls.std()) if nulls.size else 0.0
    z = float((real_rho - null_mean) / null_std) if null_std > 1e-10 else None
    p_perm = float(np.mean(np.abs(nulls) >= abs(real_rho))) if nulls.size else None
    return {
        "real_rho": float(real_rho),
        "n": int(x.size),
        "null_mean": null_mean,
        "null_std": null_std,
        "z_score": z,
        "p_perm": p_perm,
    }


def verdict_from_z(z):
    if z is None:
        return "0"
    if z >= 3.0:
        return "+1"
    if z <= -3.0:
        return "0"
    return "-1"


def stratify_and_pool(labels, merged, strata_key, bins=None):
    """Return within-stratum rho per stratum and pooled fisher-z average."""
    vals = []
    for lbl in labels:
        s = merged[lbl].get(strata_key)
        if s is not None:
            vals.append((lbl, s))
    if not vals:
        return None
    if bins is None:
        arr = np.array([v for _, v in vals], dtype=float)
        q = np.quantile(arr, [0, 1/3, 2/3, 1.0])
        bins = [(float(q[i]), float(q[i+1])) for i in range(3)]
    per_stratum = []
    fisher_sum = 0.0
    fisher_w = 0.0
    for lo, hi in bins:
        subset = [lbl for lbl, v in vals if lo <= v <= hi + 1e-9]
        x = [merged[l]["mean_log_disc"] for l in subset]
        y = [merged[l]["mean_log_cond"] for l in subset]
        rho, n_used = pearson(x, y)
        per_stratum.append({
            "range": [lo, hi],
            "n": n_used,
            "rho": rho,
        })
        if rho is not None and n_used > 3 and abs(rho) < 0.999:
            z_f = 0.5 * np.log((1 + rho) / (1 - rho))
            fisher_sum += (n_used - 3) * z_f
            fisher_w += (n_used - 3)
    if fisher_w > 0:
        z_bar = fisher_sum / fisher_w
        rho_pooled = float((np.exp(2 * z_bar) - 1) / (np.exp(2 * z_bar) + 1))
    else:
        rho_pooled = None
    return {"per_stratum": per_stratum, "rho_pooled": rho_pooled}


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F010] start {started}")

    conn = psycopg2.connect(**PG)
    nfs = load_nfs(conn)
    artins = load_artins(conn)
    print(f"[wsw_F010] loaded {len(nfs)} NFs, {len(artins)} Artin reps")

    merged = aggregate_labels(nfs, artins)
    shared = sorted(merged.keys())
    print(f"[wsw_F010] shared Galois labels: {len(shared)}")

    conn.close()

    results = {"per_projection": {}, "verdict_by_projection": {}}

    # P010 baseline
    p010 = permutation_null(shared, merged, N_PERMS)
    if p010 is None:
        print("[wsw_F010] P010 baseline FAILED — insufficient data")
        return
    p010_verdict = verdict_from_z(p010["z_score"])
    results["per_projection"]["P010"] = {
        "description": "baseline categorical object-keyed rho, galois-label permutation null",
        **p010,
        "verdict": p010_verdict,
    }
    results["verdict_by_projection"]["P010"] = p010_verdict
    print(f"[wsw_F010] P010 rho={p010['real_rho']:.4f} z={p010['z_score']:.2f} n={p010['n']}")

    # P020 conductor conditioning — bin by mean_log_disc
    p020 = stratify_and_pool(shared, merged, "mean_log_disc")
    if p020 is not None:
        rho_p = p020["rho_pooled"]
        ratio = (rho_p / p010["real_rho"]) if (rho_p is not None and p010["real_rho"]) else None
        verdict = "+1" if (rho_p is not None and abs(rho_p) > 0.25) else (
                  "-1" if rho_p is not None and abs(rho_p) < 0.10 else "0")
        results["per_projection"]["P020"] = {
            "description": "within-bin rho (3 bins of mean_log_disc) — conductor conditioning proxy",
            "bins": p020["per_stratum"],
            "rho_pooled_fisher_z": rho_p,
            "retention_ratio_vs_P010": float(ratio) if ratio is not None else None,
            "verdict": verdict,
        }
        results["verdict_by_projection"]["P020"] = verdict
        print(f"[wsw_F010] P020 pooled_rho={rho_p}")

    # P021 bad-prime count (num_ram on NF side)
    labels_with_nr = [l for l in shared if merged[l].get("mean_num_ram") is not None]
    if labels_with_nr:
        arr = np.array([merged[l]["mean_num_ram"] for l in labels_with_nr])
        # integer-like bins
        lo, hi = int(np.floor(arr.min())), int(np.ceil(arr.max()))
        bins = [(b, b + 0.9999) for b in range(lo, hi + 1)]
        p021 = stratify_and_pool(labels_with_nr, merged, "mean_num_ram", bins=bins)
    else:
        p021 = None
    if p021 is not None:
        rho_p = p021["rho_pooled"]
        verdict = "+1" if (rho_p is not None and abs(rho_p) > 0.25) else (
                  "-1" if rho_p is not None and abs(rho_p) < 0.10 else "0")
        results["per_projection"]["P021"] = {
            "description": "within-stratum rho by mean NF num_ram (integer bins)",
            "per_stratum": p021["per_stratum"],
            "rho_pooled_fisher_z": rho_p,
            "verdict": verdict,
        }
        results["verdict_by_projection"]["P021"] = verdict
        print(f"[wsw_F010] P021 pooled_rho={rho_p}")

    # P042 feature permutation — compare log_class_number alternative
    cn_labels = [l for l in shared if merged[l].get("mean_log_cn") is not None]
    x = [merged[l]["mean_log_disc"] for l in cn_labels]
    y = [merged[l]["mean_log_cond"] for l in cn_labels]
    x_alt = [merged[l]["mean_log_cn"] for l in cn_labels]
    rho_disc, n_disc = pearson(x, y)
    rho_alt, n_alt = pearson(x_alt, y)
    # Retention of disc signal vs. swap to class_number
    if rho_disc is not None and rho_alt is not None:
        drop = float(abs(rho_disc) - abs(rho_alt))
        # If the disc-specific rho is substantially larger than the class_number-
        # substituted rho, the coupling is feature-specific (+1). If they match
        # closely, representation artifact (-1).
        verdict = ("+1" if drop > 0.10 else
                   "-1" if drop < -0.05 or abs(rho_disc) < 0.10 else
                   "0")
    else:
        verdict = "0"
    results["per_projection"]["P042"] = {
        "description": ("ad-hoc feature permutation: rho(log_disc, log_cond) "
                        "vs rho(log_class_number, log_cond) over same shared labels"),
        "n_labels": len(cn_labels),
        "rho_disc_vs_cond": rho_disc,
        "rho_class_number_vs_cond": rho_alt,
        "drop": (float(abs(rho_disc) - abs(rho_alt))
                 if rho_disc is not None and rho_alt is not None else None),
        "verdict": verdict,
        "caveat": ("This is a minimum P042 implementation — true F39 permutes ALL "
                   "feature columns on each side, not a single-feature swap."),
    }
    results["verdict_by_projection"]["P042"] = verdict
    print(f"[wsw_F010] P042 disc={rho_disc} class_number={rho_alt} verdict={verdict}")

    # P052 deferred
    results["per_projection"]["P052"] = {
        "description": "prime decontamination (microscope.py 3-layer)",
        "verdict": "deferred",
        "note": ("Not run in this tick. Requires integration with "
                 "cartography/shared/scripts/microscope.py and a prime-factorization "
                 "pipeline for disc_abs + Conductor. Flagged as follow-up task for "
                 "sessionA to seed if P052 on F010 is load-bearing for the Pattern-13 "
                 "redirect. Current data (P020+P021) already constrains the result."),
    }
    results["verdict_by_projection"]["P052"] = "deferred"

    # Shape summary
    line_parts = []
    for k in ["P010", "P020", "P021", "P042", "P052"]:
        pv = results["per_projection"][k]
        rho = pv.get("real_rho") or pv.get("rho_pooled_fisher_z") or pv.get("rho_disc_vs_cond")
        if rho is None:
            line_parts.append(f"{k}:{pv['verdict']}")
        else:
            line_parts.append(f"{k}:rho={rho:.3f}({pv['verdict']})")
    results["shape_summary"] = (
        f"F010 Galois-label coupling walk over {len(shared)} shared labels. "
        + "; ".join(line_parts)
    )

    results["_meta"] = {
        "task_id": "wsw_F010",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "per_degree": PER_DEGREE,
        "per_combo": PER_COMBO,
        "n_perms_P010_null": N_PERMS,
        "n_shared_labels": len(shared),
        "prior_reference": "Harmonia 2026-04-15: rho=0.40, z=3.64, 114 shared labels",
        "notes": [
            "verdict convention: +1 = projection resolves F010 (coupling persists/visible); 0 = inconclusive; -1 = coupling collapses",
            "P020 uses mean_log_disc as a conductor proxy (true conductor fields are heterogeneous across NF and Artin tables; direct conductor binning would require cross-side normalization)",
            "P042 is an ad-hoc single-feature swap — full F39 remains TO-DO",
            "P052 deferred — microscope integration out of scope for this tick",
        ],
    }

    out_path = os.path.join("cartography", "docs", "wsw_F010_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[wsw_F010] wrote {out_path}")
    print(f"[wsw_F010] shape_summary: {results['shape_summary']}")


if __name__ == "__main__":
    main()
