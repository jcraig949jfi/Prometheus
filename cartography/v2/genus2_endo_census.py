#!/usr/bin/env python3
"""
Genus-2 Complete Endomorphism Ring Census
==========================================
Cross-tabulates endomorphism ring × Sato-Tate group × rank across all 66,158
genus-2 curves in the LMFDB.

Data sources:
  - genus2_curves_full.json   : st_group, aut_grp, geom_aut_grp, discriminant, etc.
  - genus2_curves_lmfdb.json  : endomorphism_ring, rank, conductor, label

Join strategy: sort both by (conductor, normalized_torsion) and zip.
  66,157 / 66,158 match exactly; 1 torsion discrepancy tolerated.

Output: genus2_endo_census_results.json
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]  # cartography/
DATA = ROOT / "genus2" / "data"
OUT = Path(__file__).resolve().parent / "genus2_endo_census_results.json"


def norm_torsion(t):
    """Normalize torsion to a comparable tuple."""
    if isinstance(t, list):
        return tuple(t)
    if isinstance(t, str):
        parts = t.strip("[]").split(",")
        return tuple(int(x.strip()) for x in parts if x.strip())
    return (t,)


def load_and_merge():
    """Load both datasets and merge on (conductor, torsion)."""
    with open(DATA / "genus2_curves_full.json") as f:
        full = json.load(f)
    with open(DATA / "genus2_curves_lmfdb.json") as f:
        lmfdb = json.load(f)["records"]

    assert len(full) == len(lmfdb), f"Length mismatch: {len(full)} vs {len(lmfdb)}"
    n = len(full)

    # Sort both by (conductor, torsion_tuple, tiebreaker)
    full_sorted = sorted(full, key=lambda r: (
        r["conductor"], norm_torsion(r["torsion"]),
        r.get("discriminant", 0)
    ))
    lmfdb_sorted = sorted(lmfdb, key=lambda r: (
        r["conductor"], norm_torsion(r["torsion"]),
        r.get("label", "")
    ))

    merged = []
    matched = 0
    for fr, lr in zip(full_sorted, lmfdb_sorted):
        if (fr["conductor"] == lr["conductor"]
                and norm_torsion(fr["torsion"]) == norm_torsion(lr["torsion"])):
            matched += 1

        # Merge fields: full provides st_group, aut_grp, geom_aut_grp, etc.
        # LMFDB provides endomorphism_ring, rank, label, equation
        rec = {
            "label": lr["label"],
            "conductor": int(lr["conductor"]) if isinstance(lr["conductor"], str) else lr["conductor"],
            "rank": int(lr["rank"]) if isinstance(lr["rank"], str) else lr["rank"],
            "endomorphism_ring": lr["endomorphism_ring"],
            "st_group": fr["st_group"],
            "aut_grp": fr["aut_grp"],
            "geom_aut_grp": fr["geom_aut_grp"],
            "discriminant": fr["discriminant"],
            "disc_sign": fr.get("disc_sign"),
            "torsion": lr["torsion"] if isinstance(lr["torsion"], list) else fr["torsion"],
            "two_selmer_rank": fr.get("two_selmer_rank"),
            "has_square_sha": fr.get("has_square_sha"),
            "root_number": fr.get("root_number"),
        }
        merged.append(rec)

    print(f"Merged {len(merged)} curves ({matched}/{n} conductor+torsion matched)")
    return merged


def build_census(curves):
    """Build the full cross-tabulation and census."""
    results = {}

    # ---- 1. Basic counts ----
    endo_counts = Counter(c["endomorphism_ring"] for c in curves)
    st_counts = Counter(c["st_group"] for c in curves)
    rank_counts = Counter(c["rank"] for c in curves)

    results["total_curves"] = len(curves)
    results["endomorphism_ring_counts"] = dict(sorted(endo_counts.items(), key=lambda x: -x[1]))
    results["st_group_counts"] = dict(sorted(st_counts.items(), key=lambda x: -x[1]))
    results["rank_counts"] = dict(sorted(rank_counts.items(), key=lambda x: x[0]))

    # ---- 2. Cross-tabulation: endo_ring × st_group ----
    endo_st = defaultdict(lambda: defaultdict(int))
    for c in curves:
        endo_st[c["endomorphism_ring"]][c["st_group"]] += 1

    results["cross_tab_endo_st"] = {
        endo: dict(sorted(st_map.items(), key=lambda x: -x[1]))
        for endo, st_map in sorted(endo_st.items(), key=lambda x: -sum(x[1].values()))
    }

    # ---- 3. Cross-tabulation: endo_ring × rank ----
    endo_rank = defaultdict(lambda: defaultdict(int))
    for c in curves:
        endo_rank[c["endomorphism_ring"]][c["rank"]] += 1

    results["cross_tab_endo_rank"] = {
        endo: dict(sorted(rank_map.items(), key=lambda x: x[0]))
        for endo, rank_map in sorted(endo_rank.items(), key=lambda x: -sum(x[1].values()))
    }

    # ---- 4. Full triple cross-tab: endo × st × rank ----
    triple = defaultdict(lambda: {
        "count": 0,
        "conductors": [],
        "discriminants": [],
    })
    for c in curves:
        key = (c["endomorphism_ring"], c["st_group"], c["rank"])
        bucket = triple[key]
        bucket["count"] += 1
        bucket["conductors"].append(c["conductor"])
        if c["discriminant"] is not None:
            bucket["discriminants"].append(abs(c["discriminant"]))

    # Compute stats for each triple
    triple_stats = []
    for (endo, st, rank), bucket in sorted(triple.items(), key=lambda x: -x[1]["count"]):
        conds = bucket["conductors"]
        discs = bucket["discriminants"]
        entry = {
            "endomorphism_ring": endo,
            "st_group": st,
            "rank": rank,
            "count": bucket["count"],
            "fraction": round(bucket["count"] / len(curves), 6),
            "mean_conductor": round(statistics.mean(conds), 2) if conds else None,
            "median_conductor": round(statistics.median(conds), 2) if conds else None,
            "min_conductor": min(conds) if conds else None,
            "max_conductor": max(conds) if conds else None,
            "mean_abs_disc": round(statistics.mean(discs), 2) if discs else None,
            "median_abs_disc": round(statistics.median(discs), 2) if discs else None,
        }
        triple_stats.append(entry)

    results["triple_cross_tab"] = triple_stats

    # ---- 5. Empty and universal combinations ----
    all_endos = sorted(endo_counts.keys())
    all_sts = sorted(st_counts.keys())
    all_ranks = sorted(rank_counts.keys())

    occupied = set(triple.keys())
    total_possible = len(all_endos) * len(all_sts) * len(all_ranks)

    empty_combos = []
    for endo in all_endos:
        for st in all_sts:
            for rank in all_ranks:
                if (endo, st, rank) not in occupied:
                    empty_combos.append({
                        "endomorphism_ring": endo,
                        "st_group": st,
                        "rank": rank,
                    })

    results["combinatorial_space"] = {
        "total_possible_triples": total_possible,
        "occupied_triples": len(occupied),
        "empty_triples": len(empty_combos),
        "occupancy_rate": round(len(occupied) / total_possible, 4),
    }
    results["empty_combinations"] = empty_combos

    # Universal = combinations that contain > 1% of all curves
    universal = [t for t in triple_stats if t["fraction"] > 0.01]
    results["universal_combinations"] = universal

    # ---- 6. Endo ring → ST group determinism ----
    # In genus 2, the endomorphism algebra constrains the ST group.
    # Check if endo_ring determines st_group uniquely.
    endo_to_sts = defaultdict(set)
    for c in curves:
        endo_to_sts[c["endomorphism_ring"]].add(c["st_group"])

    determinism = {}
    for endo in sorted(endo_to_sts.keys()):
        sts = sorted(endo_to_sts[endo])
        determinism[endo] = {
            "st_groups": sts,
            "is_unique": len(sts) == 1,
            "count": endo_counts[endo],
        }
    results["endo_determines_st"] = determinism

    # ---- 7. ST group → endo ring reverse map ----
    st_to_endos = defaultdict(set)
    for c in curves:
        st_to_endos[c["st_group"]].add(c["endomorphism_ring"])

    reverse_map = {}
    for st in sorted(st_to_endos.keys()):
        endos = sorted(st_to_endos[st])
        reverse_map[st] = {
            "endomorphism_rings": endos,
            "is_unique": len(endos) == 1,
            "count": st_counts[st],
        }
    results["st_determines_endo"] = reverse_map

    # ---- 8. Automorphism group enrichment ----
    endo_aut = defaultdict(lambda: defaultdict(int))
    for c in curves:
        aut_key = str(c["aut_grp"])
        endo_aut[c["endomorphism_ring"]][aut_key] += 1

    results["endo_by_aut_group"] = {
        endo: dict(sorted(aut_map.items(), key=lambda x: -x[1]))
        for endo, aut_map in sorted(endo_aut.items(), key=lambda x: -sum(x[1].values()))
    }

    # ---- 9. Geometric automorphism group ----
    endo_geom_aut = defaultdict(lambda: defaultdict(int))
    for c in curves:
        gaut_key = str(c["geom_aut_grp"])
        endo_geom_aut[c["endomorphism_ring"]][gaut_key] += 1

    results["endo_by_geom_aut_group"] = {
        endo: dict(sorted(gaut_map.items(), key=lambda x: -x[1]))
        for endo, gaut_map in sorted(endo_geom_aut.items(), key=lambda x: -sum(x[1].values()))
    }

    # ---- 10. Torsion structure by endo ring ----
    endo_torsion = defaultdict(lambda: defaultdict(int))
    for c in curves:
        tors_key = str(c["torsion"]) if isinstance(c["torsion"], list) else str(c["torsion"])
        endo_torsion[c["endomorphism_ring"]][tors_key] += 1

    results["torsion_by_endo"] = {
        endo: {
            "unique_torsion_structures": len(tors_map),
            "top_5": dict(sorted(tors_map.items(), key=lambda x: -x[1])[:5]),
        }
        for endo, tors_map in sorted(endo_torsion.items(), key=lambda x: -sum(x[1].values()))
    }

    # ---- 11. Root number distribution by endo ring ----
    endo_rn = defaultdict(lambda: defaultdict(int))
    for c in curves:
        rn = c.get("root_number")
        if rn is not None:
            endo_rn[c["endomorphism_ring"]][rn] += 1

    results["root_number_by_endo"] = {
        endo: dict(sorted(rn_map.items(), key=lambda x: x[0]))
        for endo, rn_map in sorted(endo_rn.items(), key=lambda x: -sum(x[1].values()))
    }

    # ---- 12. Selmer rank by endo ring ----
    endo_selmer = defaultdict(list)
    for c in curves:
        sr = c.get("two_selmer_rank")
        if sr is not None:
            endo_selmer[c["endomorphism_ring"]].append(sr)

    results["selmer_rank_by_endo"] = {
        endo: {
            "mean": round(statistics.mean(vals), 4),
            "median": statistics.median(vals),
            "max": max(vals),
            "count": len(vals),
        }
        for endo, vals in sorted(endo_selmer.items(), key=lambda x: -len(x[1]))
    }

    # ---- 13. "Periodic table" summary ----
    # Rows = endomorphism rings (8), Columns = ST groups (20)
    # Cell = (count, mean_rank, mean_conductor)
    periodic_table = {}
    for endo in all_endos:
        row = {}
        for st in all_sts:
            subset = [c for c in curves
                      if c["endomorphism_ring"] == endo and c["st_group"] == st]
            if subset:
                ranks = [c["rank"] for c in subset]
                conds = [c["conductor"] for c in subset]
                row[st] = {
                    "count": len(subset),
                    "mean_rank": round(statistics.mean(ranks), 4),
                    "mean_conductor": round(statistics.mean(conds), 2),
                    "rank_distribution": dict(Counter(ranks)),
                }
        if row:
            periodic_table[endo] = row

    results["periodic_table"] = periodic_table

    # ---- 14. Sha square vs endo ring ----
    endo_sha = defaultdict(lambda: {"square": 0, "non_square": 0, "unknown": 0})
    for c in curves:
        sha_val = c.get("has_square_sha")
        endo = c["endomorphism_ring"]
        if sha_val == 1:
            endo_sha[endo]["square"] += 1
        elif sha_val == 0:
            endo_sha[endo]["non_square"] += 1
        else:
            endo_sha[endo]["unknown"] += 1

    results["sha_square_by_endo"] = dict(sorted(endo_sha.items(),
        key=lambda x: -(x[1]["square"] + x[1]["non_square"])))

    return results


def print_summary(results):
    """Print a human-readable summary."""
    print(f"\n{'='*70}")
    print(f"GENUS-2 ENDOMORPHISM RING CENSUS — {results['total_curves']} CURVES")
    print(f"{'='*70}\n")

    print("Endomorphism Ring Distribution:")
    for ring, count in results["endomorphism_ring_counts"].items():
        pct = 100 * count / results["total_curves"]
        print(f"  {ring:15s}  {count:6d}  ({pct:5.2f}%)")

    print(f"\nSato-Tate Group Distribution:")
    for st, count in results["st_group_counts"].items():
        pct = 100 * count / results["total_curves"]
        print(f"  {st:15s}  {count:6d}  ({pct:5.2f}%)")

    print(f"\nRank Distribution:")
    for rank, count in results["rank_counts"].items():
        pct = 100 * count / results["total_curves"]
        print(f"  rank {rank}:  {count:6d}  ({pct:5.2f}%)")

    print(f"\nEndo Ring -> ST Group Determinism:")
    for endo, info in results["endo_determines_st"].items():
        unique = "UNIQUE" if info["is_unique"] else "MULTIPLE"
        print(f"  {endo:15s} -> {unique}: {', '.join(info['st_groups'])}")

    cs = results["combinatorial_space"]
    print(f"\nCombinatorial Space:")
    print(f"  Possible triples (endo × ST × rank): {cs['total_possible_triples']}")
    print(f"  Occupied triples:                     {cs['occupied_triples']}")
    print(f"  Empty triples:                        {cs['empty_triples']}")
    print(f"  Occupancy rate:                       {cs['occupancy_rate']:.1%}")

    print(f"\nUniversal Combinations (>1% of all curves):")
    for t in results["universal_combinations"]:
        print(f"  {t['endomorphism_ring']:15s} × {t['st_group']:15s} × rank {t['rank']}"
              f"  ->  {t['count']:6d}  ({100*t['fraction']:.2f}%)")

    print(f"\nTop 10 Occupied Triples:")
    for t in results["triple_cross_tab"][:10]:
        print(f"  {t['endomorphism_ring']:15s} × {t['st_group']:15s} × rank {t['rank']}"
              f"  ->  {t['count']:6d}  mean_cond={t['mean_conductor']}")

    print(f"\nRarest Occupied Triples (count <= 3):")
    rare = [t for t in results["triple_cross_tab"] if t["count"] <= 3]
    for t in rare:
        print(f"  {t['endomorphism_ring']:15s} × {t['st_group']:15s} × rank {t['rank']}"
              f"  ->  {t['count']:6d}  mean_cond={t['mean_conductor']}")


def main():
    curves = load_and_merge()
    results = build_census(curves)
    print_summary(results)

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
