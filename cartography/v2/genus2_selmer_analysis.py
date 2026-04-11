"""
Genus-2 2-Selmer Rank Distribution Analysis
============================================
Measures the distribution of 2-Selmer ranks across genus-2 curves,
correlates with MW rank, and computes gap statistics.

Data: genus2_curves_full.json (two_selmer_rank) + genus2_curves_lmfdb.json (MW rank)
Output: genus2_selmer_results.json
"""

import json
import os
from collections import Counter, defaultdict
import statistics

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "genus2", "data")
OUT_PATH = os.path.join(BASE, "genus2_selmer_results.json")


def load_and_merge():
    """Merge full file (two_selmer_rank) with lmfdb file (MW rank) by conductor grouping."""
    full = json.load(open(os.path.join(DATA_DIR, "genus2_curves_full.json")))
    lmfdb_data = json.load(open(os.path.join(DATA_DIR, "genus2_curves_lmfdb.json")))
    lmfdb = lmfdb_data["records"]

    # Group by conductor for matching
    full_by_cond = defaultdict(list)
    for f in full:
        full_by_cond[f["conductor"]].append(f)

    lmfdb_by_cond = defaultdict(list)
    for l in lmfdb:
        lmfdb_by_cond[l["conductor"]].append(l)

    merged = []
    for cond in full_by_cond:
        fg = full_by_cond[cond]
        lg = lmfdb_by_cond.get(cond, [])
        if len(fg) != len(lg):
            continue
        fg_s = sorted(fg, key=lambda x: str(sorted(x["torsion"])))
        lg_s = sorted(lg, key=lambda x: x["torsion"])
        for f, l in zip(fg_s, lg_s):
            merged.append({
                "label": l["label"],
                "conductor": cond,
                "two_selmer_rank": f["two_selmer_rank"],
                "mw_rank": int(l["rank"]),
                "torsion": f["torsion"],
                "root_number": f.get("root_number"),
                "has_square_sha": f.get("has_square_sha"),
                "st_group": f.get("st_group"),
            })
    return merged


def analyze(merged):
    n = len(merged)

    # --- 1. 2-Selmer rank distribution ---
    selmer_dist = Counter(m["two_selmer_rank"] for m in merged)
    selmer_dist_sorted = dict(sorted(selmer_dist.items()))

    # --- 2. MW rank distribution ---
    mw_dist = Counter(m["mw_rank"] for m in merged)
    mw_dist_sorted = dict(sorted(mw_dist.items()))

    # --- 3. Joint distribution: (selmer, mw) ---
    joint = Counter((m["two_selmer_rank"], m["mw_rank"]) for m in merged)
    joint_table = {f"selmer={s},mw={w}": c for (s, w), c in sorted(joint.items())}

    # --- 4. Correlation ---
    selmer_vals = [m["two_selmer_rank"] for m in merged]
    mw_vals = [m["mw_rank"] for m in merged]
    mean_s = statistics.mean(selmer_vals)
    mean_m = statistics.mean(mw_vals)
    cov = sum((s - mean_s) * (w - mean_m) for s, w in zip(selmer_vals, mw_vals)) / n
    std_s = statistics.pstdev(selmer_vals)
    std_m = statistics.pstdev(mw_vals)
    correlation = cov / (std_s * std_m) if std_s > 0 and std_m > 0 else 0.0

    # --- 5. Gap = Selmer - MW ---
    gaps = [m["two_selmer_rank"] - m["mw_rank"] for m in merged]
    gap_dist = Counter(gaps)
    gap_dist_sorted = dict(sorted(gap_dist.items()))

    # --- 6. Mean Selmer-MW gap by MW rank ---
    gap_by_mw = defaultdict(list)
    for m in merged:
        gap_by_mw[m["mw_rank"]].append(m["two_selmer_rank"] - m["mw_rank"])

    mean_gap_by_mw = {}
    for rank in sorted(gap_by_mw):
        vals = gap_by_mw[rank]
        mean_gap_by_mw[str(rank)] = {
            "mean_gap": round(statistics.mean(vals), 4),
            "median_gap": statistics.median(vals),
            "count": len(vals),
            "frac_exact": round(sum(1 for v in vals if v == 0) / len(vals), 4),
        }

    # --- 7. Fraction with Selmer = MW (no Sha contribution) ---
    exact_match = sum(1 for g in gaps if g == 0)
    frac_exact = exact_match / n

    # Violations (Selmer < MW, should not happen theoretically)
    violations = sum(1 for g in gaps if g < 0)

    # --- 8. Mean gap by Selmer rank ---
    gap_by_selmer = defaultdict(list)
    for m in merged:
        gap_by_selmer[m["two_selmer_rank"]].append(m["two_selmer_rank"] - m["mw_rank"])

    mean_gap_by_selmer = {}
    for sr in sorted(gap_by_selmer):
        vals = gap_by_selmer[sr]
        mean_gap_by_selmer[str(sr)] = {
            "mean_gap": round(statistics.mean(vals), 4),
            "count": len(vals),
        }

    # --- 9. Selmer rank vs root number ---
    selmer_by_root = defaultdict(list)
    for m in merged:
        if m["root_number"] is not None:
            selmer_by_root[m["root_number"]].append(m["two_selmer_rank"])
    root_number_stats = {}
    for rn in sorted(selmer_by_root):
        vals = selmer_by_root[rn]
        root_number_stats[str(rn)] = {
            "mean_selmer": round(statistics.mean(vals), 4),
            "count": len(vals),
        }

    results = {
        "metadata": {
            "total_curves": n,
            "source_full": "genus2_curves_full.json",
            "source_lmfdb": "genus2_curves_lmfdb.json",
            "description": "2-Selmer rank distribution and gap analysis for genus-2 curves",
        },
        "selmer_rank_distribution": {
            str(k): v for k, v in selmer_dist_sorted.items()
        },
        "selmer_rank_fractions": {
            str(k): round(v / n, 6) for k, v in selmer_dist_sorted.items()
        },
        "mw_rank_distribution": {
            str(k): v for k, v in mw_dist_sorted.items()
        },
        "joint_distribution": joint_table,
        "correlation_selmer_mw": round(correlation, 6),
        "gap_distribution": {
            str(k): v for k, v in gap_dist_sorted.items()
        },
        "gap_fractions": {
            str(k): round(v / n, 6) for k, v in gap_dist_sorted.items()
        },
        "mean_selmer_mw_gap": round(statistics.mean(gaps), 4),
        "median_selmer_mw_gap": statistics.median(gaps),
        "mean_gap_by_mw_rank": mean_gap_by_mw,
        "mean_gap_by_selmer_rank": mean_gap_by_selmer,
        "exact_match_count": exact_match,
        "exact_match_fraction": round(frac_exact, 6),
        "violations_selmer_lt_mw": violations,
        "selmer_by_root_number": root_number_stats,
        "summary": {
            "mean_selmer_rank": round(mean_s, 4),
            "mean_mw_rank": round(mean_m, 4),
            "correlation": round(correlation, 6),
            "frac_selmer_equals_mw": round(frac_exact, 6),
            "frac_gap_ge_2": round(sum(1 for g in gaps if g >= 2) / n, 6),
            "interpretation": (
                f"Of {n} genus-2 curves, {round(frac_exact*100, 1)}% have 2-Selmer rank = MW rank "
                f"(no Sha[2] contribution). Mean gap = {round(statistics.mean(gaps), 3)}. "
                f"Correlation(Selmer, MW) = {round(correlation, 4)}."
            ),
        },
    }
    return results


def main():
    print("Loading and merging genus-2 data...")
    merged = load_and_merge()
    print(f"  Merged {len(merged)} curves")

    print("Analyzing 2-Selmer rank distribution...")
    results = analyze(merged)

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUT_PATH}")

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Total curves: {results['metadata']['total_curves']}")
    print(f"\n2-Selmer rank distribution:")
    for k, v in results["selmer_rank_distribution"].items():
        frac = results["selmer_rank_fractions"][k]
        print(f"  rank {k}: {v} ({frac*100:.1f}%)")
    print(f"\nMW rank distribution:")
    for k, v in results["mw_rank_distribution"].items():
        print(f"  rank {k}: {v}")
    print(f"\nCorrelation(Selmer, MW): {results['correlation_selmer_mw']}")
    print(f"Mean Selmer-MW gap: {results['mean_selmer_mw_gap']}")
    print(f"Fraction Selmer = MW: {results['exact_match_fraction']} ({results['exact_match_count']}/{results['metadata']['total_curves']})")
    print(f"Violations (Selmer < MW): {results['violations_selmer_lt_mw']}")
    print(f"\nMean gap by MW rank:")
    for k, v in results["mean_gap_by_mw_rank"].items():
        print(f"  MW rank {k}: mean_gap={v['mean_gap']}, exact_frac={v['frac_exact']}, n={v['count']}")
    print(f"\nGap distribution:")
    for k, v in results["gap_distribution"].items():
        frac = results["gap_fractions"][k]
        print(f"  gap={k}: {v} ({frac*100:.1f}%)")
    print(f"\nSelmer by root number:")
    for k, v in results["selmer_by_root_number"].items():
        print(f"  w={k}: mean_selmer={v['mean_selmer']}, n={v['count']}")


if __name__ == "__main__":
    main()
