"""
Bilbao Space Group Structural Analysis
=======================================
Loads all 230 space group files, extracts structural features,
computes distributions, correlations, builds point-group graph,
and cross-references with Materials Project prevalence.

Saves results to bilbao_sg_analysis_results.json
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import math

# ── Paths ──────────────────────────────────────────────────────────────
BILBAO_DIR = Path(__file__).resolve().parent.parent / "physics" / "data" / "bilbao"
MP_FILE = Path(__file__).resolve().parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_FILE = Path(__file__).resolve().parent / "bilbao_sg_analysis_results.json"


def load_space_groups():
    """Load all 230 sg_*.json files."""
    sgs = {}
    for i in range(1, 231):
        fp = BILBAO_DIR / f"sg_{i}.json"
        if not fp.exists():
            print(f"WARNING: missing sg_{i}.json")
            continue
        with open(fp) as f:
            sgs[i] = json.load(f)
    print(f"Loaded {len(sgs)} space groups")
    return sgs


def extract_features(sgs):
    """Extract core features per SG."""
    records = []
    for sg_num in sorted(sgs):
        sg = sgs[sg_num]
        rec = {
            "sg_number": sg_num,
            "num_generators": sg["num_generators"],
            "num_wyckoff": sg["num_wyckoff_positions"],
            "pg_order": sg["point_group_order"],
            "num_pg_generators": len(sg.get("point_group_generators", [])),
            "max_stabilizer_order": max(
                (w["stabilizer_order"] for w in sg["wyckoff_positions"]),
                default=0
            ),
            "translation_basis": sg.get("translation_basis", []),
        }
        records.append(rec)
    return records


def compute_distributions(records):
    """Histograms for generator count, Wyckoff count, PG order."""
    gen_counts = Counter(r["num_generators"] for r in records)
    wyckoff_counts = Counter(r["num_wyckoff"] for r in records)
    pg_orders = Counter(r["pg_order"] for r in records)

    return {
        "generator_distribution": dict(sorted(gen_counts.items())),
        "wyckoff_distribution": dict(sorted(wyckoff_counts.items())),
        "pg_order_distribution": dict(sorted(pg_orders.items())),
        "generator_stats": _stats([r["num_generators"] for r in records]),
        "wyckoff_stats": _stats([r["num_wyckoff"] for r in records]),
        "pg_order_stats": _stats([r["pg_order"] for r in records]),
    }


def _stats(vals):
    n = len(vals)
    mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / n
    return {
        "mean": round(mu, 3),
        "std": round(math.sqrt(var), 3),
        "min": min(vals),
        "max": max(vals),
        "median": sorted(vals)[n // 2],
    }


def compute_correlations(records):
    """Pearson correlations between pairs of features."""
    def pearson(xs, ys):
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
        sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
        if sx == 0 or sy == 0:
            return 0.0
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
        return round(cov / (sx * sy), 4)

    gens = [r["num_generators"] for r in records]
    wyck = [r["num_wyckoff"] for r in records]
    pgo = [r["pg_order"] for r in records]

    return {
        "generators_vs_wyckoff": pearson(gens, wyck),
        "generators_vs_pg_order": pearson(gens, pgo),
        "wyckoff_vs_pg_order": pearson(wyck, pgo),
    }


def build_point_group_graph(sgs, records):
    """
    Connect space groups sharing the same point group order.
    Since we don't have explicit PG labels, we use pg_order + num_pg_generators
    as a proxy fingerprint for the abstract point group.
    """
    # Group SGs by point group fingerprint
    pg_groups = defaultdict(list)
    for r in records:
        sg = sgs[r["sg_number"]]
        # fingerprint: (pg_order, num_pg_generators)
        fp = (r["pg_order"], r["num_pg_generators"])
        pg_groups[fp].append(r["sg_number"])

    # Build edges (within each PG class)
    edges = []
    for fp, members in pg_groups.items():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                edges.append((members[i], members[j]))

    # Graph stats
    num_nodes = 230
    num_edges = len(edges)
    max_possible = num_nodes * (num_nodes - 1) // 2
    density = round(num_edges / max_possible, 6) if max_possible > 0 else 0

    # Component sizes = PG class sizes
    class_sizes = sorted([len(m) for m in pg_groups.values()], reverse=True)

    # Degree per node
    degree = Counter()
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    degrees = [degree.get(i, 0) for i in range(1, 231)]
    avg_degree = round(sum(degrees) / len(degrees), 2)
    max_degree = max(degrees) if degrees else 0

    return {
        "num_pg_classes": len(pg_groups),
        "class_sizes": class_sizes,
        "largest_class_size": class_sizes[0] if class_sizes else 0,
        "num_edges": num_edges,
        "graph_density": density,
        "avg_degree": avg_degree,
        "max_degree": max_degree,
        "pg_class_members": {
            f"pg_order={k[0]}_pggens={k[1]}": v
            for k, v in sorted(pg_groups.items())
        },
    }


def load_mp_prevalence():
    """Count structures per space group from MP 10K dataset."""
    if not MP_FILE.exists():
        print("WARNING: MP file not found, skipping cross-reference")
        return {}
    with open(MP_FILE) as f:
        mp = json.load(f)
    sg_counts = Counter()
    for entry in mp:
        sg_num = entry.get("spacegroup_number")
        if sg_num:
            sg_counts[sg_num] += 1
    return dict(sg_counts)


def cross_reference(records, mp_counts):
    """Cross-reference Wyckoff complexity with MP prevalence."""
    if not mp_counts:
        return {"status": "no MP data available"}

    # Top 20 SGs by MP prevalence
    top_mp = sorted(mp_counts.items(), key=lambda x: -x[1])[:20]

    # Build lookup
    rec_by_sg = {r["sg_number"]: r for r in records}

    top_mp_with_wyckoff = []
    for sg_num, count in top_mp:
        r = rec_by_sg.get(sg_num, {})
        top_mp_with_wyckoff.append({
            "sg_number": sg_num,
            "mp_count": count,
            "num_wyckoff": r.get("num_wyckoff", None),
            "num_generators": r.get("num_generators", None),
            "pg_order": r.get("pg_order", None),
        })

    # Top 20 SGs by Wyckoff count
    top_wyckoff = sorted(records, key=lambda r: -r["num_wyckoff"])[:20]
    top_wyckoff_with_mp = []
    for r in top_wyckoff:
        top_wyckoff_with_mp.append({
            "sg_number": r["sg_number"],
            "num_wyckoff": r["num_wyckoff"],
            "mp_count": mp_counts.get(r["sg_number"], 0),
            "pg_order": r["pg_order"],
        })

    # Correlation: Wyckoff count vs MP count (for SGs present in MP)
    xs, ys = [], []
    for r in records:
        sg = r["sg_number"]
        if sg in mp_counts:
            xs.append(r["num_wyckoff"])
            ys.append(mp_counts[sg])

    def pearson(xs, ys):
        n = len(xs)
        if n < 3:
            return None
        mx, my = sum(xs) / n, sum(ys) / n
        sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
        sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
        if sx == 0 or sy == 0:
            return 0.0
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
        return round(cov / (sx * sy), 4)

    wyckoff_vs_prevalence = pearson(xs, ys)

    # Also: pg_order vs prevalence
    xs2, ys2 = [], []
    for r in records:
        sg = r["sg_number"]
        if sg in mp_counts:
            xs2.append(r["pg_order"])
            ys2.append(mp_counts[sg])

    pg_order_vs_prevalence = pearson(xs2, ys2)

    # SGs with zero MP entries
    sgs_in_mp = set(mp_counts.keys())
    sgs_absent = sorted(set(range(1, 231)) - sgs_in_mp)

    return {
        "mp_dataset_size": sum(mp_counts.values()),
        "sgs_represented_in_mp": len(sgs_in_mp),
        "sgs_absent_from_mp": len(sgs_absent),
        "top_20_mp_prevalence": top_mp_with_wyckoff,
        "top_20_wyckoff_complexity": top_wyckoff_with_mp,
        "correlation_wyckoff_vs_mp_count": wyckoff_vs_prevalence,
        "correlation_pg_order_vs_mp_count": pg_order_vs_prevalence,
        "does_complexity_predict_prevalence": (
            "positive" if wyckoff_vs_prevalence and wyckoff_vs_prevalence > 0.1
            else "negative" if wyckoff_vs_prevalence and wyckoff_vs_prevalence < -0.1
            else "weak/none"
        ),
    }


def main():
    print("=" * 60)
    print("Bilbao Space Group Structural Analysis")
    print("=" * 60)

    # 1. Load
    sgs = load_space_groups()

    # 2. Extract features
    records = extract_features(sgs)
    print(f"Extracted features for {len(records)} SGs")

    # 3. Distributions
    distributions = compute_distributions(records)
    print(f"Generator range: {distributions['generator_stats']['min']}-{distributions['generator_stats']['max']}, "
          f"mean={distributions['generator_stats']['mean']}")
    print(f"Wyckoff range: {distributions['wyckoff_stats']['min']}-{distributions['wyckoff_stats']['max']}, "
          f"mean={distributions['wyckoff_stats']['mean']}")
    print(f"PG order range: {distributions['pg_order_stats']['min']}-{distributions['pg_order_stats']['max']}, "
          f"mean={distributions['pg_order_stats']['mean']}")

    # 4. Correlations
    correlations = compute_correlations(records)
    print(f"\nCorrelations:")
    for k, v in correlations.items():
        print(f"  {k}: r={v}")

    # 5. Point group graph
    pg_graph = build_point_group_graph(sgs, records)
    print(f"\nPoint Group Graph:")
    print(f"  {pg_graph['num_pg_classes']} PG classes")
    print(f"  Largest class: {pg_graph['largest_class_size']} SGs")
    print(f"  {pg_graph['num_edges']} edges, density={pg_graph['graph_density']}")
    print(f"  Avg degree={pg_graph['avg_degree']}, max degree={pg_graph['max_degree']}")

    # 6. MP cross-reference
    mp_counts = load_mp_prevalence()
    xref = cross_reference(records, mp_counts)
    if "mp_dataset_size" in xref:
        print(f"\nMP Cross-Reference ({xref['mp_dataset_size']} structures):")
        print(f"  SGs in MP: {xref['sgs_represented_in_mp']}/230")
        print(f"  Wyckoff vs prevalence: r={xref['correlation_wyckoff_vs_mp_count']}")
        print(f"  PG order vs prevalence: r={xref['correlation_pg_order_vs_mp_count']}")
        print(f"  Complexity predicts prevalence? {xref['does_complexity_predict_prevalence']}")

    # 7. Assemble full results
    # Per-SG table (without translation_basis to keep JSON small)
    sg_table = []
    for r in records:
        entry = {k: v for k, v in r.items() if k != "translation_basis"}
        entry["mp_count"] = mp_counts.get(r["sg_number"], 0)
        sg_table.append(entry)

    results = {
        "meta": {
            "analysis": "Bilbao Space Group Structural Analysis",
            "num_space_groups": len(records),
            "mp_dataset": str(MP_FILE.name),
        },
        "distributions": distributions,
        "correlations": correlations,
        "point_group_graph": {
            k: v for k, v in pg_graph.items() if k != "pg_class_members"
        },
        "pg_classes": pg_graph["pg_class_members"],
        "mp_cross_reference": xref,
        "sg_table": sg_table,
    }

    # Save
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
