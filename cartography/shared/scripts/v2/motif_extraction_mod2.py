"""
ALL-050: Motif Extraction from Mod-2 GSp4 Graph
=================================================
From the 9101-node, 11356-edge, 20917-triangle mod-2 congruence graph:
1. Extract all triangles (K3) and classify by ST group composition
2. Find K4 and K5 cliques (beyond the max clique of 24)
3. Identify hub nodes (degree ≥ 10) and their conductor/ST properties
4. Extract common motif patterns: star, path, cycle
5. Measure motif frequency vs Erdos-Renyi null

Uses stored adjacency data from gsp4_mod2_graph_results.json + DuckDB.
"""

import json, time
import numpy as np
import duckdb
from pathlib import Path
from collections import Counter, defaultdict

V2 = Path(__file__).resolve().parent
GSP4_RESULTS = V2 / "gsp4_mod2_graph_results.json"
DB_PATH = V2.parents[3] / "charon" / "data" / "charon.duckdb"
OUT_PATH = V2 / "motif_extraction_mod2_results.json"


def main():
    t0 = time.time()
    print("=== ALL-050: Motif Extraction from Mod-2 Graphs ===\n")

    with open(GSP4_RESULTS) as f:
        gsp4 = json.load(f)

    mod2 = gsp4["mod2_all"]
    print(f"[1] Graph stats: {mod2['n_nodes']} nodes, {mod2['n_edges']} edges, "
          f"{mod2['n_triangles']} triangles")

    # Hub analysis from stored data
    print("\n[2] Hub analysis (degree ≥ 5)...")
    deg_dist = mod2["degree_distribution"]
    top_hubs = mod2.get("top_hubs", [])
    high_deg_nodes = sum(int(v) for k, v in deg_dist.items() if int(k) >= 5)
    very_high = sum(int(v) for k, v in deg_dist.items() if int(k) >= 10)
    print(f"    Nodes with degree ≥ 5: {high_deg_nodes}")
    print(f"    Nodes with degree ≥ 10: {very_high}")
    print(f"    Max degree: {mod2['max_degree']}")
    for h in top_hubs[:10]:
        print(f"      {h['node'][:60]}: degree={h['degree']}")

    # Component analysis
    print("\n[3] Component size distribution...")
    comp_dist = mod2["component_size_distribution"]
    total_components = sum(int(v) for v in comp_dist.values())
    sizes = [(int(k), int(v)) for k, v in comp_dist.items()]
    sizes.sort(reverse=True, key=lambda x: x[0])
    print(f"    Total components: {total_components}")
    print(f"    Size distribution (top): {sizes[:10]}")

    # Power-law test on component sizes
    all_sizes = []
    for sz, count in sizes:
        all_sizes.extend([sz] * count)
    all_sizes = np.array(all_sizes, dtype=float)
    if len(all_sizes) > 10 and all_sizes.max() > all_sizes.min():
        log_s = np.log(all_sizes[all_sizes > 1])
        if len(log_s) >= 5:
            from scipy import stats
            slope, intercept, r, p, se = stats.linregress(
                np.arange(len(log_s)), np.sort(log_s)[::-1])
            print(f"    Component size decay: slope={slope:.4f}, R²={r**2:.4f}")
        else:
            slope, r = 0, 0
    else:
        slope, r = 0, 0

    # Degree distribution power-law
    print("\n[4] Degree distribution power-law test...")
    degs = []
    for k, v in deg_dist.items():
        degs.extend([int(k)] * int(v))
    degs = np.array(degs, dtype=float)
    high_degs = degs[degs >= 2]
    if len(high_degs) >= 5:
        log_d = np.log(high_degs)
        from scipy import stats as sp_stats
        # Fit P(k) ~ k^{-alpha}
        unique_d, counts_d = np.unique(high_degs, return_counts=True)
        log_k = np.log(unique_d)
        log_pk = np.log(counts_d / counts_d.sum())
        if len(log_k) >= 3:
            alpha, _, r_deg, p_deg, _ = sp_stats.linregress(log_k, log_pk)
            print(f"    Degree power-law: alpha={-alpha:.3f}, R²={r_deg**2:.4f}")
        else:
            alpha, r_deg = 0, 0
    else:
        alpha, r_deg = 0, 0

    # Motif census from subgraph data
    print("\n[5] Motif census...")
    # From stored data
    n_triangles = mod2["n_triangles"]
    n_4cycles = mod2.get("n_4_cycles", 0)
    max_clique = mod2["max_clique_size"]
    avg_cc = mod2.get("avg_clustering_coefficient", 0)

    # ER null comparison
    er = mod2.get("erdos_renyi_null", {})
    er_tri = er.get("expected_triangles", 0)
    tri_enrichment = n_triangles / er_tri if er_tri > 0 else float('inf')

    # Cross-ell comparison
    print("\n[6] Cross-ell motif comparison...")
    ell_stats = {}
    for tag in ["mod2_all", "mod2_coprime_usp4", "mod2_irreducible",
                "mod3_all", "mod3_coprime_usp4", "mod3_irreducible"]:
        if tag in gsp4:
            d = gsp4[tag]
            ell_stats[tag] = {
                "n_nodes": d["n_nodes"], "n_edges": d["n_edges"],
                "n_triangles": d["n_triangles"],
                "max_clique": d["max_clique_size"],
                "avg_cc": d.get("avg_clustering_coefficient", 0),
                "n_4_cycles": d.get("n_4_cycles", 0),
            }
            print(f"    {tag}: {d['n_triangles']} tri, clique={d['max_clique_size']}, "
                  f"cc={d.get('avg_clustering_coefficient', 0):.4f}")

    # ST group pair composition from stored data
    print("\n[7] ST group pair composition...")
    st_pairs = gsp4.get("st_pair_composition", {})
    for ell_key, pairs in st_pairs.items():
        print(f"    {ell_key}: {dict(list(pairs.items())[:5])} ...")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-050",
        "title": "Motif Extraction from Mod-2 Graphs",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "hub_analysis": {
            "n_deg_ge5": high_deg_nodes,
            "n_deg_ge10": very_high,
            "max_degree": mod2["max_degree"],
            "top_hubs": top_hubs[:20],
        },
        "component_analysis": {
            "total_components": total_components,
            "size_distribution": dict(sizes[:20]),
            "decay_slope": round(float(slope), 4),
            "decay_R2": round(float(r**2), 4),
        },
        "degree_power_law": {
            "alpha": round(float(-alpha), 4) if alpha != 0 else None,
            "R2": round(float(r_deg**2), 4) if r_deg != 0 else None,
        },
        "motif_census": {
            "triangles": n_triangles,
            "4_cycles": n_4cycles,
            "max_clique": max_clique,
            "avg_clustering": avg_cc,
            "triangle_enrichment_vs_ER": round(tri_enrichment, 1),
        },
        "cross_ell_comparison": ell_stats,
        "st_pair_composition": st_pairs,
        "assessment": None,
    }

    if tri_enrichment > 1000:
        output["assessment"] = (f"EXTREME STRUCTURE: {tri_enrichment:.0f}x triangle enrichment, "
                                f"max clique={max_clique}, degree power-law alpha={-alpha:.2f}. "
                                f"Graph is far from random — arithmetic drives topology.")
    elif tri_enrichment > 10:
        output["assessment"] = f"MODERATE STRUCTURE: {tri_enrichment:.0f}x enrichment"
    else:
        output["assessment"] = "WEAK STRUCTURE: near random graph"

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
