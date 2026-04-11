"""
EC Szpiro Ratio Analysis
========================
Szpiro's conjecture: |disc| <= C(eps) * N^{6+eps}
=> sigma = log|disc| / log(N) should be <= 6.

Measures the distribution of sigma across all elliptic curves in the database.
"""

import json
import math
import duckdb
import numpy as np
from collections import defaultdict

DB_PATH = "charon/data/charon.duckdb"
OUT_PATH = "cartography/v2/ec_szpiro_results.json"

def compute_discriminant(ainvs):
    """Compute the minimal discriminant from Weierstrass coefficients [a1,a2,a3,a4,a6]."""
    a1, a2, a3, a4, a6 = ainvs
    b2 = a1**2 + 4*a2
    b4 = a1*a3 + 2*a4
    b6 = a3**2 + 4*a6
    b8 = a1**2*a6 - a1*a3*a4 + a2*a3**2 + 4*a2*a6 - a4**2
    disc = -b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6
    return disc


def analyze_subset(records, label="all"):
    """Compute full stats for a list of records."""
    sigmas = np.array([r["sigma"] for r in records])

    overall = {
        "n_curves": len(records),
        "mean": float(np.mean(sigmas)),
        "median": float(np.median(sigmas)),
        "std": float(np.std(sigmas)),
        "min": float(np.min(sigmas)),
        "max": float(np.max(sigmas)),
        "pct_25": float(np.percentile(sigmas, 25)),
        "pct_75": float(np.percentile(sigmas, 75)),
        "pct_95": float(np.percentile(sigmas, 95)),
        "pct_99": float(np.percentile(sigmas, 99)),
    }

    violations = [r for r in records if r["sigma"] > 6]
    violation_summary = {
        "count": len(violations),
        "fraction": len(violations) / len(records),
        "max_sigma": max(v["sigma"] for v in violations) if violations else None,
        "examples": sorted(violations, key=lambda x: -x["sigma"])[:10],
    }

    near_summary = {
        "count_above_5": int(np.sum(sigmas > 5)),
        "fraction_above_5": float(np.sum(sigmas > 5) / len(sigmas)),
    }

    bin_edges = np.arange(0, math.ceil(np.max(sigmas)) + 0.5, 0.5)
    counts, edges = np.histogram(sigmas, bins=bin_edges)
    histogram = [
        {"bin_low": float(edges[i]), "bin_high": float(edges[i+1]), "count": int(counts[i])}
        for i in range(len(counts))
    ]

    rank_groups = defaultdict(list)
    for r in records:
        rank_groups[r["rank"]].append(r["sigma"])

    by_rank = {}
    for rk in sorted(rank_groups.keys()):
        arr = np.array(rank_groups[rk])
        by_rank[str(rk)] = {
            "n": len(arr),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "max": float(np.max(arr)),
            "pct_above_5": float(np.sum(arr > 5) / len(arr)),
            "pct_above_6": float(np.sum(arr > 6) / len(arr)),
        }

    cm_groups = defaultdict(list)
    for r in records:
        cm_label = f"cm_{r['cm']}" if r["cm"] != 0 else "non_cm"
        cm_groups[cm_label].append(r["sigma"])

    by_cm = {}
    for cm_label in sorted(cm_groups.keys()):
        arr = np.array(cm_groups[cm_label])
        by_cm[cm_label] = {
            "n": len(arr),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "max": float(np.max(arr)),
        }

    return {
        "overall": overall,
        "violations_above_6": violation_summary,
        "near_violations": near_summary,
        "histogram": histogram,
        "by_rank": by_rank,
        "by_cm": by_cm,
    }


def main():
    con = duckdb.connect(DB_PATH, read_only=True)
    rows = con.execute(
        "SELECT ainvs, conductor, rank, cm, optimality FROM elliptic_curves WHERE conductor > 1"
    ).fetchall()
    con.close()

    all_records = []
    optimal_records = []
    skipped = 0
    for ainvs, conductor, rank, cm, optimality in rows:
        disc = compute_discriminant(ainvs)
        abs_disc = abs(disc)
        if abs_disc == 0 or conductor <= 1:
            skipped += 1
            continue
        sigma = math.log(abs_disc) / math.log(conductor)
        rec = {
            "sigma": sigma,
            "abs_disc": abs_disc,
            "conductor": conductor,
            "rank": int(rank),
            "cm": int(cm),
        }
        all_records.append(rec)
        if optimality == 1:
            optimal_records.append(rec)

    # Analyze all curves and optimal-only
    all_stats = analyze_subset(all_records, "all")
    all_stats["overall"]["skipped"] = skipped
    optimal_stats = analyze_subset(optimal_records, "optimal")

    # --- Assemble results ---
    results = {
        "title": "EC Szpiro Ratio Distribution",
        "conjecture": "sigma = log|disc| / log(N) <= 6+eps for all EC/Q (Szpiro); finitely many exceptions for each eps",
        "note": "LMFDB ainvs are global minimal Weierstrass models, so disc is the minimal discriminant. "
                "Different curves in same isogeny class have different minimal disc but same conductor. "
                "optimal_only restricts to one curve per isogeny class.",
        "all_curves": all_stats,
        "optimal_only": optimal_stats,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    for tag, stats in [("ALL CURVES", all_stats), ("OPTIMAL ONLY", optimal_stats)]:
        o = stats["overall"]
        v = stats["violations_above_6"]
        n = stats["near_violations"]
        print(f"\n=== {tag} ===")
        print(f"Curves: {o['n_curves']}")
        print(f"Szpiro ratio: mean={o['mean']:.4f}, median={o['median']:.4f}, max={o['max']:.4f}")
        print(f"Violations (sigma > 6): {v['count']} ({v['fraction']*100:.2f}%)")
        print(f"Near-violations (sigma > 5): {n['count_above_5']} ({n['fraction_above_5']*100:.2f}%)")
        print(f"By rank:")
        for rk, rs in stats["by_rank"].items():
            print(f"  rank {rk}: n={rs['n']}, mean={rs['mean']:.4f}, median={rs['median']:.4f}, max={rs['max']:.4f}")
        print(f"By CM:")
        for label, cs in stats["by_cm"].items():
            print(f"  {label}: n={cs['n']}, mean={cs['mean']:.4f}, max={cs['max']:.4f}")


if __name__ == "__main__":
    main()
