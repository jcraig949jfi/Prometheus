#!/usr/bin/env python3
"""
Hub Connectivity Analysis for Noesis v2.

Builds a NetworkX graph of hub-to-hub connections from cross_domain_links
and cross_domain_edges tables, then computes graph metrics.
"""

import json
import duckdb
import networkx as nx
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
OUTPUT_PATH = Path(__file__).parent / "hub_graph_metrics.json"


def extract_hub_from_resolution(resolution_id: str, known_hubs: set) -> str | None:
    """Try to extract hub comp_id from a resolution_id.

    Resolution IDs follow patterns like:
      HUB__RESOLUTION  (e.g., IMPOSSIBILITY_ARROW__SINGLE_PEAKED_PREFERENCES)
      STANDALONE_ID    (e.g., SPATIAL_MULTIPLEXING_MIMO)

    We match against known hubs by checking if the resolution_id starts with a hub name.
    """
    # Direct match
    if resolution_id in known_hubs:
        return resolution_id

    # Check for HUB__RESOLUTION pattern (double underscore)
    if "__" in resolution_id:
        hub_part = resolution_id.split("__")[0]
        if hub_part in known_hubs:
            return hub_part

    # Check if starts with any known hub (longest match first)
    sorted_hubs = sorted(known_hubs, key=len, reverse=True)
    for hub in sorted_hubs:
        if resolution_id.startswith(hub + "_"):
            return hub

    return None


def main():
    start_time = datetime.now(timezone.utc)
    print(f"Hub Connectivity Analysis — started {start_time.isoformat()}")
    print(f"Database: {DB_PATH}")
    print()

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # 1. Get all hubs
    hubs = con.execute("SELECT comp_id FROM abstract_compositions ORDER BY 1").fetchall()
    hub_ids = {h[0] for h in hubs}
    print(f"Hubs (abstract_compositions): {len(hub_ids)}")

    # 2. Build edge list from cross_domain_links (explicit source_hub, target_hub)
    link_edges = con.execute("""
        SELECT source_hub, target_hub, COUNT(*) as cnt
        FROM cross_domain_links
        WHERE source_hub IS NOT NULL AND target_hub IS NOT NULL
        GROUP BY source_hub, target_hub
    """).fetchall()
    print(f"cross_domain_links: {len(link_edges)} unique hub-pairs")

    # 3. Build edge list from cross_domain_edges (need to resolve hub from resolution_id)
    raw_edges = con.execute("""
        SELECT source_resolution_id, target_resolution_id
        FROM cross_domain_edges
    """).fetchall()

    edge_counter = Counter()
    unmapped_resolutions = set()
    for src_res, tgt_res in raw_edges:
        src_hub = extract_hub_from_resolution(src_res, hub_ids)
        tgt_hub = extract_hub_from_resolution(tgt_res, hub_ids)
        if src_hub and tgt_hub and src_hub != tgt_hub:
            pair = tuple(sorted([src_hub, tgt_hub]))
            edge_counter[pair] += 1
        else:
            if not src_hub:
                unmapped_resolutions.add(src_res)
            if not tgt_hub:
                unmapped_resolutions.add(tgt_res)

    print(f"cross_domain_edges: {len(edge_counter)} unique hub-pairs (from {len(raw_edges)} edges)")
    if unmapped_resolutions:
        print(f"  Unmapped resolution IDs: {len(unmapped_resolutions)}")
        for u in sorted(unmapped_resolutions)[:10]:
            print(f"    - {u}")

    con.close()

    # 4. Build NetworkX graph
    G = nx.Graph()

    # Add all hubs as nodes (including potential isolates)
    for hub in hub_ids:
        G.add_node(hub)

    # Add edges from cross_domain_links
    link_weight_counter = Counter()
    for src_hub, tgt_hub, cnt in link_edges:
        # Add both hubs (target might be a new hub not in abstract_compositions)
        pair = tuple(sorted([src_hub, tgt_hub]))
        link_weight_counter[pair] += cnt
        if src_hub not in G:
            G.add_node(src_hub)
        if tgt_hub not in G:
            G.add_node(tgt_hub)

    # Merge link weights into graph
    for (a, b), w in link_weight_counter.items():
        if G.has_edge(a, b):
            G[a][b]["weight"] += w
        else:
            G.add_edge(a, b, weight=w)

    # Add edges from cross_domain_edges
    for (a, b), w in edge_counter.items():
        if G.has_edge(a, b):
            G[a][b]["weight"] += w
        else:
            G.add_edge(a, b, weight=w)

    print(f"\nGraph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # 5. Compute metrics
    degrees = dict(G.degree())
    weighted_degrees = dict(G.degree(weight="weight"))
    betweenness = nx.betweenness_centrality(G)

    components = list(nx.connected_components(G))
    components_sorted = sorted(components, key=len, reverse=True)

    largest_cc = G.subgraph(components_sorted[0]).copy() if components_sorted else G

    if largest_cc.number_of_nodes() > 1:
        diameter = nx.diameter(largest_cc)
        avg_path_length = nx.average_shortest_path_length(largest_cc)
    else:
        diameter = 0
        avg_path_length = 0.0

    # 6. Identify key hubs
    most_connected = max(degrees, key=degrees.get)
    most_bridge = max(betweenness, key=betweenness.get)
    isolated = [n for n, d in degrees.items() if d == 0]

    # Densest hub-pair
    densest_pair = None
    densest_weight = 0
    for u, v, data in G.edges(data=True):
        if data["weight"] > densest_weight:
            densest_weight = data["weight"]
            densest_pair = (u, v)

    # Degree distribution
    degree_values = sorted(degrees.values(), reverse=True)

    # 7. Print summary
    print("\n" + "=" * 70)
    print("HUB CONNECTIVITY ANALYSIS — RESULTS")
    print("=" * 70)

    print(f"\nGraph Overview:")
    print(f"  Nodes (hubs):          {G.number_of_nodes()}")
    print(f"  Edges (connections):   {G.number_of_edges()}")
    print(f"  Connected components:  {len(components)}")
    print(f"  Largest component:     {len(largest_cc)} nodes")
    print(f"  Diameter:              {diameter}")
    print(f"  Avg path length:       {avg_path_length:.3f}")
    print(f"  Graph density:         {nx.density(G):.4f}")

    print(f"\nMost Connected Hub (highest degree):")
    print(f"  {most_connected} — degree {degrees[most_connected]}, "
          f"weighted degree {weighted_degrees[most_connected]}")

    print(f"\nMost Bridge-like Hub (highest betweenness):")
    print(f"  {most_bridge} — betweenness {betweenness[most_bridge]:.4f}")

    if isolated:
        print(f"\nIsolated Hubs (degree 0): {len(isolated)}")
        for h in sorted(isolated):
            print(f"  - {h}")
    else:
        print(f"\nIsolated Hubs: None")

    if densest_pair:
        print(f"\nDensest Hub-Pair:")
        print(f"  {densest_pair[0]} <-> {densest_pair[1]} — {densest_weight} connections")

    print(f"\nTop 10 Hubs by Degree:")
    top_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    for hub, deg in top_degree:
        print(f"  {hub}: degree={deg}, betweenness={betweenness[hub]:.4f}")

    print(f"\nComponent Sizes: {[len(c) for c in components_sorted]}")

    # 8. Build metrics dict
    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "graph_overview": {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "connected_components": len(components),
            "largest_component_size": len(largest_cc),
            "diameter": diameter,
            "avg_path_length": round(avg_path_length, 4),
            "density": round(nx.density(G), 6),
        },
        "most_connected_hub": {
            "hub": most_connected,
            "degree": degrees[most_connected],
            "weighted_degree": weighted_degrees[most_connected],
        },
        "most_bridge_hub": {
            "hub": most_bridge,
            "betweenness_centrality": round(betweenness[most_bridge], 6),
        },
        "isolated_hubs": sorted(isolated),
        "densest_pair": {
            "hubs": list(densest_pair) if densest_pair else [],
            "connection_count": densest_weight,
        },
        "component_sizes": [len(c) for c in components_sorted],
        "hub_metrics": {
            hub: {
                "degree": degrees[hub],
                "weighted_degree": weighted_degrees[hub],
                "betweenness_centrality": round(betweenness[hub], 6),
            }
            for hub in sorted(degrees.keys())
        },
        "unmapped_resolution_ids": sorted(unmapped_resolutions),
    }

    # 9. Save
    with open(OUTPUT_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nMetrics saved to {OUTPUT_PATH}")

    end_time = datetime.now(timezone.utc)
    print(f"Completed in {(end_time - start_time).total_seconds():.1f}s")

    return metrics


if __name__ == "__main__":
    main()
