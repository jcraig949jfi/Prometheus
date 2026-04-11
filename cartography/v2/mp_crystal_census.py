"""
Materials Project Crystal System Census + Point Group Prediction
================================================================
Loads MP data (~210K structures), computes:
1. Crystal system distribution
2. Space group distribution (power law test)
3. Point group -> space group mapping + entropy
4. Point group -> crystal system verification
5. nsites distribution
6. Elements distribution
7. Density vs crystal system
"""

import json
import re
import math
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_full.json"
OUT_PATH = Path(__file__).parent / "mp_crystal_census_results.json"


def parse_elements(formula: str) -> list:
    """Extract element symbols from a chemical formula."""
    return re.findall(r'[A-Z][a-z]?', formula)


def entropy(counts: list) -> float:
    """Shannon entropy in bits from a list of counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    probs = [c / total for c in counts if c > 0]
    return -sum(p * math.log2(p) for p in probs)


def fit_power_law_ols(counts_sorted):
    """Simple OLS power law fit on log-log: log(count) = a - b*log(rank)."""
    ranks = np.arange(1, len(counts_sorted) + 1, dtype=float)
    log_r = np.log(ranks)
    log_c = np.log(np.array(counts_sorted, dtype=float))
    # OLS
    A = np.vstack([np.ones_like(log_r), log_r]).T
    result = np.linalg.lstsq(A, log_c, rcond=None)
    coeffs = result[0]
    a, b = coeffs[0], coeffs[1]
    # R^2
    predicted = a + b * log_r
    ss_res = np.sum((log_c - predicted) ** 2)
    ss_tot = np.sum((log_c - np.mean(log_c)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return {"intercept": float(a), "exponent": float(b), "R2": float(r2)}


def main():
    print("Loading data...")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    N = len(data)
    print(f"Loaded {N} structures")

    # ---- 1. Crystal system distribution ----
    crystal_counts = Counter()
    sg_counts = Counter()
    pg_to_sg = defaultdict(set)
    pg_to_cs = defaultdict(set)
    pg_counts = Counter()
    nsites_list = []
    element_counts = Counter()
    density_by_cs = defaultdict(list)

    for entry in data:
        cs = entry.get("crystal_system", "Unknown")
        sg_num = entry.get("spacegroup_number")
        pg = entry.get("point_group", "Unknown")
        nsites = entry.get("nsites")
        formula = entry.get("formula", "")
        density = entry.get("density")

        crystal_counts[cs] += 1
        if sg_num is not None:
            sg_counts[sg_num] += 1
        pg_counts[pg] += 1
        if pg and sg_num:
            pg_to_sg[pg].add(sg_num)
        if pg and cs:
            pg_to_cs[pg].add(cs)
        if nsites is not None:
            nsites_list.append(nsites)
        for el in parse_elements(formula):
            element_counts[el] += 1
        if density is not None and cs:
            density_by_cs[cs].append(density)

    # ---- 1. Crystal system ----
    cs_sorted = sorted(crystal_counts.items(), key=lambda x: -x[1])
    cs_total = sum(crystal_counts.values())
    crystal_system_dist = {
        name: {"count": cnt, "fraction": round(cnt / cs_total, 4)}
        for name, cnt in cs_sorted
    }
    print("\n=== Crystal System Distribution ===")
    for name, info in crystal_system_dist.items():
        print(f"  {name:15s}: {info['count']:7d}  ({info['fraction']:.2%})")

    # ---- 2. Space group distribution ----
    sg_sorted = sorted(sg_counts.items(), key=lambda x: -x[1])
    top20_sg = [
        {"sg_number": sg, "count": cnt, "fraction": round(cnt / N, 4)}
        for sg, cnt in sg_sorted[:20]
    ]
    # power law fit
    sg_count_values = [cnt for _, cnt in sg_sorted]
    power_law = fit_power_law_ols(sg_count_values)

    print(f"\n=== Space Group Distribution (top 20 of {len(sg_counts)} occupied) ===")
    for item in top20_sg[:10]:
        print(f"  SG {item['sg_number']:>3d}: {item['count']:7d}  ({item['fraction']:.2%})")
    print(f"  Power law fit: exponent={power_law['exponent']:.3f}, R2={power_law['R2']:.4f}")

    # ---- 3. Point group -> space group entropy ----
    pg_sg_entropy = {}
    for pg, sgs in sorted(pg_to_sg.items()):
        # count how many structures in each SG for this PG
        sg_struct_counts = []
        for sg in sgs:
            # count structures with this pg AND this sg
            cnt = sum(1 for e in data if e.get("point_group") == pg and e.get("spacegroup_number") == sg)
            sg_struct_counts.append(cnt)
        H = entropy(sg_struct_counts)
        pg_sg_entropy[pg] = {
            "n_spacegroups": len(sgs),
            "spacegroups": sorted(sgs),
            "entropy_bits": round(H, 4),
            "max_entropy_bits": round(math.log2(len(sgs)), 4) if len(sgs) > 1 else 0.0,
            "total_structures": pg_counts[pg]
        }

    print(f"\n=== Point Group -> Space Group Entropy ===")
    for pg, info in sorted(pg_sg_entropy.items(), key=lambda x: -x[1]["n_spacegroups"])[:10]:
        print(f"  PG {pg:>6s}: {info['n_spacegroups']:3d} SGs, H={info['entropy_bits']:.2f} / {info['max_entropy_bits']:.2f} bits")

    # ---- 4. Point group -> crystal system (should be 1:1) ----
    pg_cs_violations = {}
    pg_cs_map = {}
    for pg, css in pg_to_cs.items():
        if len(css) > 1:
            pg_cs_violations[pg] = sorted(css)
        pg_cs_map[pg] = sorted(css)

    pg_predicts_cs = len(pg_cs_violations) == 0
    print(f"\n=== Point Group -> Crystal System ===")
    print(f"  Perfect 1:1 mapping: {pg_predicts_cs}")
    if pg_cs_violations:
        print(f"  Violations ({len(pg_cs_violations)}):")
        for pg, css in sorted(pg_cs_violations.items()):
            print(f"    PG {pg}: {css}")

    # ---- 5. nsites distribution ----
    nsites_arr = np.array(nsites_list)
    nsites_stats = {
        "count": len(nsites_list),
        "mean": round(float(np.mean(nsites_arr)), 2),
        "median": round(float(np.median(nsites_arr)), 2),
        "std": round(float(np.std(nsites_arr)), 2),
        "min": int(np.min(nsites_arr)),
        "max": int(np.max(nsites_arr)),
        "p25": round(float(np.percentile(nsites_arr, 25)), 2),
        "p75": round(float(np.percentile(nsites_arr, 75)), 2),
        "p95": round(float(np.percentile(nsites_arr, 95)), 2),
        "p99": round(float(np.percentile(nsites_arr, 99)), 2),
    }
    # histogram bins
    bins = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    hist, _ = np.histogram(nsites_arr, bins=bins)
    nsites_stats["histogram"] = {
        f"{bins[i]}-{bins[i+1]-1}": int(hist[i]) for i in range(len(hist))
    }

    print(f"\n=== nsites Distribution ===")
    print(f"  Mean={nsites_stats['mean']}, Median={nsites_stats['median']}, Max={nsites_stats['max']}")
    print(f"  P25={nsites_stats['p25']}, P75={nsites_stats['p75']}, P95={nsites_stats['p95']}")

    # ---- 6. Elements distribution ----
    top30_elements = element_counts.most_common(30)
    elements_dist = [
        {"element": el, "count": cnt, "fraction": round(cnt / N, 4)}
        for el, cnt in top30_elements
    ]

    print(f"\n=== Top 15 Elements ===")
    for item in elements_dist[:15]:
        print(f"  {item['element']:>2s}: {item['count']:7d}  ({item['fraction']:.2%})")

    # ---- 7. Density vs crystal system ----
    density_stats = {}
    for cs, densities in sorted(density_by_cs.items()):
        d = np.array(densities)
        density_stats[cs] = {
            "count": len(densities),
            "mean": round(float(np.mean(d)), 3),
            "median": round(float(np.median(d)), 3),
            "std": round(float(np.std(d)), 3),
            "p10": round(float(np.percentile(d, 10)), 3),
            "p90": round(float(np.percentile(d, 90)), 3),
        }

    print(f"\n=== Density by Crystal System ===")
    for cs, stats in sorted(density_stats.items(), key=lambda x: -x[1]["mean"]):
        print(f"  {cs:15s}: mean={stats['mean']:.2f}, median={stats['median']:.2f}, std={stats['std']:.2f}")

    # ---- Assemble results ----
    results = {
        "metadata": {
            "source": "materials_project_full.json",
            "n_structures": N,
            "n_occupied_spacegroups": len(sg_counts),
            "n_point_groups": len(pg_counts),
            "n_unique_elements": len(element_counts),
        },
        "crystal_system_distribution": crystal_system_dist,
        "spacegroup_distribution": {
            "top_20": top20_sg,
            "power_law_fit": power_law,
            "n_occupied": len(sg_counts),
            "n_total": 230,
        },
        "point_group_spacegroup_entropy": pg_sg_entropy,
        "point_group_crystal_system": {
            "perfect_mapping": pg_predicts_cs,
            "violations": pg_cs_violations,
            "full_map": pg_cs_map,
        },
        "nsites_distribution": nsites_stats,
        "elements_distribution": {
            "top_30": elements_dist,
            "n_unique": len(element_counts),
        },
        "density_by_crystal_system": density_stats,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
