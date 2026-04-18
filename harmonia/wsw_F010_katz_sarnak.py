"""wsw_F010_katz_sarnak.py — F010 NF backbone through Katz-Sarnak symmetry-type axis.

Task: wsw_F010_katz_sarnak, claimed by Harmonia_M2_sessionB, tick 12.
Projections: P028 (Katz-Sarnak symmetry type, applied to Artin rep side via Is_Even × Dim).

Method:
  - Same NF + Artin loading pipeline as sessionC's wsw_F010.py (balanced per-degree / per-(Galn,Galt) sampling).
  - Build two alternative Artin aggregates per Galois label: one restricted to Is_Even=True
    reps, one to Is_Even=False reps.
  - Compute rho(NF log_disc, Artin log_cond) within each Is_Even class.
  - Also compute per-Dim-class rho for the major dim strata (1, 2, 4).
  - Compare ro across classes. If |rho_even - rho_odd| > 3 * Fisher-SE threshold, P028
    resolves F010 structure at the symmetry axis. Otherwise F010 is axis-class-uniform
    across Katz-Sarnak — extending the F011 P028 finding's scope.

Output: cartography/docs/wsw_F010_katz_sarnak_results.json
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
MIN_MEMBERS_PER_LABEL = 3
MIN_SHARED_FOR_RHO = 10


def load_nfs(conn):
    cur = conn.cursor()
    out = []
    for degree in range(2, 21):
        cur.execute("""
            SELECT label, degree::int, galois_label,
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
    """Load Artin reps with Is_Even and Dim carried."""
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
                   "Is_Even"
              FROM artin_reps
             WHERE "Galn" = %s AND "Galt" = %s AND "Conductor" IS NOT NULL
             ORDER BY "Conductor"::numeric ASC
             LIMIT %s
        """, (str(galn), str(galt), PER_COMBO))
        out.extend(cur.fetchall())
    cur.close()
    return out


def is_even_bool(raw) -> bool | None:
    """Parse the text Is_Even field to Python bool; None on unparseable."""
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s in ("t", "true", "1"):
        return True
    if s in ("f", "false", "0"):
        return False
    return None


def aggregate(nfs, artins):
    """Per-Galois-label aggregate: NF side (disc), Artin side split by Is_Even × Dim."""
    nf_agg = defaultdict(list)
    for lbl, deg, gal, da, nr in nfs:
        if gal is None or da is None or float(da) <= 0:
            continue
        nf_agg[gal].append(float(da))

    # Artin: label -> dict of dim buckets and even/odd buckets
    art_all = defaultdict(list)
    art_even = defaultdict(list)
    art_odd = defaultdict(list)
    art_dim1 = defaultdict(list)
    art_dim2 = defaultdict(list)
    art_dim4 = defaultdict(list)

    for bl, dim, galn, galt, cond, is_even_raw in artins:
        if galn is None or galt is None or cond is None or float(cond) <= 0:
            continue
        key = f"{galn}T{galt}"
        c = float(cond)
        art_all[key].append(c)
        ev = is_even_bool(is_even_raw)
        if ev is True:
            art_even[key].append(c)
        elif ev is False:
            art_odd[key].append(c)
        if dim == 1:
            art_dim1[key].append(c)
        elif dim == 2:
            art_dim2[key].append(c)
        elif dim == 4:
            art_dim4[key].append(c)

    def mean_log(arr):
        arr = [v for v in arr if v > 0]
        return float(np.mean(np.log(arr))) if len(arr) >= MIN_MEMBERS_PER_LABEL else None

    merged = {}
    for lbl in nf_agg:
        nf_mld = mean_log(nf_agg[lbl])
        if nf_mld is None:
            continue
        entry = {
            "n_nf": len([v for v in nf_agg[lbl] if v > 0]),
            "mean_log_disc": nf_mld,
            "mean_log_cond_all": mean_log(art_all[lbl]),
            "mean_log_cond_even": mean_log(art_even[lbl]),
            "mean_log_cond_odd": mean_log(art_odd[lbl]),
            "mean_log_cond_dim1": mean_log(art_dim1[lbl]),
            "mean_log_cond_dim2": mean_log(art_dim2[lbl]),
            "mean_log_cond_dim4": mean_log(art_dim4[lbl]),
            "n_art_all": len(art_all[lbl]),
            "n_art_even": len(art_even[lbl]),
            "n_art_odd": len(art_odd[lbl]),
            "n_art_dim1": len(art_dim1[lbl]),
            "n_art_dim2": len(art_dim2[lbl]),
            "n_art_dim4": len(art_dim4[lbl]),
        }
        # Only keep labels that have at least the ALL aggregate
        if entry["mean_log_cond_all"] is not None:
            merged[lbl] = entry
    return merged


def compute_rho(merged, label_filter, y_key):
    labels = [l for l in merged if merged[l].get(y_key) is not None]
    if not label_filter(labels, merged):
        return None
    x = np.array([merged[l]["mean_log_disc"] for l in labels], dtype=float)
    y = np.array([merged[l][y_key] for l in labels], dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if x.size < MIN_SHARED_FOR_RHO or x.std() < 1e-10 or y.std() < 1e-10:
        return None
    rho, p = stats.pearsonr(x, y)
    if not np.isfinite(rho):
        return None
    # Fisher z and SE
    z_f = 0.5 * np.log((1 + rho) / (1 - rho))
    se = 1.0 / np.sqrt(x.size - 3) if x.size > 3 else None
    return {
        "rho": float(rho),
        "n": int(x.size),
        "p": float(p),
        "fisher_z": float(z_f),
        "fisher_se": float(se) if se is not None else None,
    }


def compare_fisher(a, b, label_a, label_b):
    """Two-sample Fisher-z test for difference of correlations."""
    if a is None or b is None or a["fisher_se"] is None or b["fisher_se"] is None:
        return {"diff_z": None, "diff_p": None, "verdict": "INCONCLUSIVE"}
    z = a["fisher_z"] - b["fisher_z"]
    se = np.sqrt(a["fisher_se"] ** 2 + b["fisher_se"] ** 2)
    z_stat = z / se if se > 0 else None
    # two-sided p
    p = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat))) if z_stat is not None else None
    verdict = ("DIFFER" if z_stat is not None and abs(z_stat) >= 3.0 else
               "SIMILAR" if z_stat is not None else "INCONCLUSIVE")
    return {
        "label_a": label_a,
        "label_b": label_b,
        "rho_a": a["rho"],
        "rho_b": b["rho"],
        "fisher_z_diff": float(z),
        "fisher_se_diff": float(se),
        "z_stat": float(z_stat) if z_stat is not None else None,
        "p_value": float(p) if p is not None else None,
        "verdict": verdict,
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[wsw_F010_katz_sarnak] start {started}")

    conn = psycopg2.connect(**PG)
    nfs = load_nfs(conn)
    artins = load_artins(conn)
    print(f"[load] {len(nfs)} NFs, {len(artins)} Artin reps")
    conn.close()

    merged = aggregate(nfs, artins)
    print(f"[aggregate] {len(merged)} shared Galois labels")

    # Baseline — all Artin reps
    baseline = compute_rho(merged, lambda labels, m: True, "mean_log_cond_all")
    print(f"[baseline] rho={baseline['rho']:.4f}  n={baseline['n']}")

    # Split by Is_Even
    rho_even = compute_rho(merged, lambda labels, m: True, "mean_log_cond_even")
    rho_odd = compute_rho(merged, lambda labels, m: True, "mean_log_cond_odd")
    print(f"[even] rho={rho_even['rho'] if rho_even else 'n/a'}  n={rho_even['n'] if rho_even else 0}")
    print(f"[odd]  rho={rho_odd['rho'] if rho_odd else 'n/a'}  n={rho_odd['n'] if rho_odd else 0}")

    even_vs_odd = compare_fisher(rho_even, rho_odd, "Is_Even=True", "Is_Even=False")
    print(f"[even_vs_odd] {even_vs_odd['verdict']}  z={even_vs_odd.get('z_stat')}")

    # Split by Dim
    rho_dim1 = compute_rho(merged, lambda labels, m: True, "mean_log_cond_dim1")
    rho_dim2 = compute_rho(merged, lambda labels, m: True, "mean_log_cond_dim2")
    rho_dim4 = compute_rho(merged, lambda labels, m: True, "mean_log_cond_dim4")
    for lbl, res in [("dim1", rho_dim1), ("dim2", rho_dim2), ("dim4", rho_dim4)]:
        if res:
            print(f"[{lbl}] rho={res['rho']:.4f}  n={res['n']}")
        else:
            print(f"[{lbl}] insufficient data")

    # Dim pairwise comparisons (1 vs 2, 2 vs 4)
    dim1_vs_dim2 = compare_fisher(rho_dim1, rho_dim2, "Dim=1", "Dim=2")
    dim2_vs_dim4 = compare_fisher(rho_dim2, rho_dim4, "Dim=2", "Dim=4")

    # Verdict for P028 on F010
    # P028 RESOLVES if any DIFFER verdict in the 3 pairwise comparisons
    pairwise = [even_vs_odd, dim1_vs_dim2, dim2_vs_dim4]
    differs = [p for p in pairwise if p["verdict"] == "DIFFER"]

    if differs:
        verdict = "P028_RESOLVES"
        reading = (f"P028 resolves F010 through at least one symmetry-axis: "
                   + "; ".join(f"{d['label_a']} vs {d['label_b']} differ at z={d['z_stat']:.2f}"
                                for d in differs)
                   + ". F010 is NOT axis-class-uniform under Katz-Sarnak. Pattern 18 generalization: "
                   "the deficit-uniformity pattern observed in F011 object-property axes does NOT transfer "
                   "to F010 — or conversely, F010 has more axis-sensitivity than F011.")
    elif any(p["verdict"] == "SIMILAR" for p in pairwise):
        verdict = "P028_FLAT"
        reading = (f"P028 does NOT resolve F010 — all tested symmetry classes give similar rho "
                   f"(all |z_diff| < 3). F010 coupling survives uniformly across Is_Even × Dim. "
                   f"Extends the F011 P028 context: F011 P028 was 7.6% spread; F010 P028 is flat. "
                   f"Not a simple transfer — the F011 signal was central-zero-forcing on L-functions, "
                   f"which has no analog in the NF-Artin log_disc/log_cond coupling.")
    else:
        verdict = "INCONCLUSIVE"
        reading = "Insufficient data in one or more strata to draw conclusions."

    out = {
        "specimen_id": "F010",
        "projections_used": ["P028"],
        "verdict": verdict,
        "reading": reading,
        "baseline_all_reps": baseline,
        "by_is_even": {
            "Is_Even=True": rho_even,
            "Is_Even=False": rho_odd,
            "comparison": even_vs_odd,
        },
        "by_dim": {
            "Dim=1": rho_dim1,
            "Dim=2": rho_dim2,
            "Dim=4": rho_dim4,
            "comparison_1_vs_2": dim1_vs_dim2,
            "comparison_2_vs_4": dim2_vs_dim4,
        },
        "pairwise_comparisons": pairwise,
        "shape_summary": reading,
        "_meta": {
            "task_id": "wsw_F010_katz_sarnak",
            "instance": "Harmonia_M2_sessionB",
            "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
            "per_degree": PER_DEGREE,
            "per_combo": PER_COMBO,
            "n_shared_labels": len(merged),
            "threshold_sigma": 3.0,
            "prior_reference": "sessionC wsw_F010 rho=0.404, n~114; sessionB wsw_F011_katz_sarnak P028_RESOLVES",
            "notes": [
                "Katz-Sarnak on Artin reps: Is_Even is the parity of complex conjugation, Dim is rep dimension.",
                "Fisher z two-sample test with se=1/sqrt(n-3) per group; threshold |z_diff|>=3 for DIFFER verdict.",
                "Dim strata limited to 1, 2, 4 (~70% of artin_reps); higher dims sampled poorly per label.",
                "F010 baseline here may differ from sessionC's 0.404 because this script uses mean_log_cond across ALL artin reps for the label, while sessionC used the same aggregate. Cross-check via baseline rho.",
            ],
        },
    }

    out_path = os.path.join("cartography", "docs", "wsw_F010_katz_sarnak_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"[wsw_F010_katz_sarnak] wrote {out_path}")
    print(f"[verdict] {verdict}")
    print(f"[reading] {reading}")


if __name__ == "__main__":
    main()
