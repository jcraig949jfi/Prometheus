"""
ALL-055: Triangle Density vs Conductor — Phase Transition Detection
====================================================================
For the GSp(4) mod-2/3 congruence graphs, analyse triangle density
across conductor buckets already computed in gsp4_mod2_graph_results.json.
Also cross-reference with the GL(2) Hecke graph by ell.

Look for:
  1. Non-monotone behaviour in tri/node vs conductor bucket
  2. Triangle enrichment over Erdos-Renyi null
  3. Phase transition where clique size jumps
"""

import json, time
import numpy as np
from pathlib import Path

V2 = Path(__file__).resolve().parent
GSP4_RESULTS = V2 / "gsp4_mod2_graph_results.json"
HECKE_RESULTS = V2 / "hecke_graph_results.json"
OUT_PATH = V2 / "triangle_density_conductor_results.json"


def main():
    t0 = time.time()
    print("=== ALL-055: Triangle Density vs Conductor ===\n")

    with open(GSP4_RESULTS) as f:
        gsp4 = json.load(f)
    with open(HECKE_RESULTS) as f:
        hecke = json.load(f)

    # 1. GSp4 conductor-bucketed sections
    print("[1] GSp4 mod-p congruence graph statistics by bucket...")
    bucket_tags = [k for k in gsp4.keys() if k.startswith("mod")]
    bucket_data = []
    for tag in sorted(bucket_tags):
        d = gsp4[tag]
        n_nodes = d.get("n_nodes", 0)
        n_edges = d.get("n_edges", 0)
        n_tri = d.get("n_triangles", 0)
        max_clique = d.get("max_clique_size", 0)
        er = d.get("erdos_renyi_null", {})
        er_tri = er.get("expected_triangles", 0)

        tri_per_node = n_tri / n_nodes if n_nodes > 0 else 0
        tri_per_edge = n_tri / n_edges if n_edges > 0 else 0
        tri_enrichment = n_tri / er_tri if er_tri > 0 else float('inf')

        row = {
            "bucket": tag,
            "description": d.get("description", ""),
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "n_triangles": n_tri,
            "max_clique": max_clique,
            "tri_per_node": round(tri_per_node, 6),
            "tri_per_edge": round(tri_per_edge, 6),
            "er_expected_triangles": er_tri,
            "triangle_enrichment_vs_ER": round(tri_enrichment, 1),
            "edge_probability": er.get("edge_probability", 0),
        }
        bucket_data.append(row)
        print(f"    {tag}: {n_nodes} nodes, {n_edges} edges, {n_tri} tri, "
              f"clique={max_clique}, enrich={tri_enrichment:.0f}x")

    # 2. GL2 Hecke graph by ell
    print("\n[2] GL2 Hecke congruence graph by ell...")
    per_ell = hecke.get("per_ell", {})
    hecke_data = []
    for ell in sorted(int(e) for e in per_ell.keys()):
        d = per_ell[str(ell)]
        n_nodes = d.get("n_nodes", 0)
        n_edges = d.get("n_edges", 0)
        n_tri = d.get("n_triangles", 0)
        tri_per_node = n_tri / n_nodes if n_nodes > 0 else 0
        hecke_data.append({
            "ell": ell,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "n_triangles": n_tri,
            "tri_per_node": round(tri_per_node, 6),
            "n_components": d.get("n_components", 0),
        })
        print(f"    ell={ell}: {n_nodes} nodes, {n_edges} edges, {n_tri} tri, "
              f"tri/node={tri_per_node:.4f}")

    # 3. Phase transition detection in GSp4
    print("\n[3] Phase transition detection...")
    # Look at component size distribution for conductor-bucketed data
    transitions = []
    gsp4_cliques = [(b["bucket"], b["max_clique"], b["n_triangles"], b["n_nodes"])
                     for b in bucket_data]
    for i in range(1, len(gsp4_cliques)):
        prev_clique = gsp4_cliques[i-1][1]
        curr_clique = gsp4_cliques[i][1]
        if prev_clique > 0 and curr_clique > 0:
            ratio = curr_clique / prev_clique
            if ratio > 2.0 or ratio < 0.5:
                transitions.append({
                    "from": gsp4_cliques[i-1][0],
                    "to": gsp4_cliques[i][0],
                    "clique_ratio": round(ratio, 2),
                    "from_clique": prev_clique,
                    "to_clique": curr_clique,
                })

    # 4. GL2: triangle density scaling with ell
    print("\n[4] GL2 triangle density scaling...")
    ells = [h["ell"] for h in hecke_data if h["n_triangles"] > 0]
    tris = [h["n_triangles"] for h in hecke_data if h["n_triangles"] > 0]
    scaling = None
    if len(ells) >= 3:
        log_ell = np.log(ells)
        log_tri = np.log(tris)
        alpha, log_A = np.polyfit(log_ell, log_tri, 1)
        predicted = np.exp(log_A) * np.array(ells)**alpha
        r2 = 1 - np.sum((np.array(tris) - predicted)**2) / np.sum((np.array(tris) - np.mean(tris))**2)
        scaling = {"alpha": round(float(alpha), 3), "A": round(float(np.exp(log_A)), 2), "R2": round(float(r2), 4)}
        print(f"    Triangles ~ {np.exp(log_A):.1f} * ell^{alpha:.2f} (R²={r2:.4f})")

    # 5. GSp4 mod-2 enrichment: is the "all" graph denser than conductor buckets suggest?
    all_data = next((b for b in bucket_data if "all" in b["bucket"].lower()), None)
    enrichment_summary = None
    if all_data:
        enrichment_summary = {
            "total_enrichment_vs_ER": all_data["triangle_enrichment_vs_ER"],
            "total_triangles": all_data["n_triangles"],
            "total_nodes": all_data["n_nodes"],
            "max_clique": all_data["max_clique"],
        }
        print(f"\n    GSp4 mod-2 total: {all_data['n_triangles']} triangles, "
              f"{all_data['triangle_enrichment_vs_ER']}x over ER null")

    elapsed = time.time() - t0
    output = {
        "challenge": "ALL-055",
        "title": "Triangle Density vs Conductor",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "gsp4_buckets": bucket_data,
        "gl2_hecke_by_ell": hecke_data,
        "phase_transitions": transitions,
        "gl2_triangle_scaling": scaling,
        "gsp4_enrichment_summary": enrichment_summary,
        "assessment": None,
    }

    # Assessment
    max_enrich = max((b["triangle_enrichment_vs_ER"] for b in bucket_data
                      if b["triangle_enrichment_vs_ER"] != float('inf')), default=0)
    if transitions:
        output["assessment"] = f"PHASE TRANSITION: clique size jumps at {[t['from']+'→'+t['to'] for t in transitions]}. Max triangle enrichment {max_enrich:.0f}x over ER"
    elif max_enrich > 100:
        output["assessment"] = f"EXTREME ENRICHMENT: {max_enrich:.0f}x triangles vs random (no sharp transition, but massive structure)"
    elif max_enrich > 10:
        output["assessment"] = f"MODERATE ENRICHMENT: {max_enrich:.0f}x triangles vs random. Structure real but no phase transition"
    else:
        output["assessment"] = f"WEAK ENRICHMENT: only {max_enrich:.0f}x. Triangle density near random."

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"\nASSESSMENT: {output['assessment']}")

if __name__ == "__main__":
    main()
