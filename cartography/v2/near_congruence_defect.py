#!/usr/bin/env python3
"""
Near-Congruence Defect Graph Analysis
======================================
M14 found 95.2% of near-congruences are norm_cartan pairs with disagreement
concentrated at specific primes {37,43,61,79,19,31,...}.

Treat disagreement primes as a topological defect:
  - Nodes = primes appearing in disagreement sets
  - Edges = primes that co-occur in the same disagreement set (weighted by count)
  - Compute: connected components, clustering coefficient, diameter
  - For each disagreement prime p: splitting type in Q(sqrt(-3)) and Q(sqrt(-7))
  - Check whether defect graph structure reflects CM splitting

Charon / Project Prometheus — 2026-04-10
"""

import json
import math
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]  # F:\Prometheus
INPUT_PATH = REPO_ROOT / "cartography" / "shared" / "scripts" / "v2" / "near_congruence_results.json"
OUT_PATH = SCRIPT_DIR / "near_congruence_defect_results.json"


def load_data():
    with open(INPUT_PATH) as f:
        return json.load(f)


def build_defect_graph(data):
    """
    Build graph from disagreement sets.
    Nodes = all primes appearing in any disagreement set.
    Edges connect primes that co-occur in the same disagreement set.
    Edge weight = number of times they co-occur.
    """
    # Collect ALL disagreement sets from the data
    # The top_repeated_sets in disagreement_pattern give us the main ones
    # We also have example pairs with explicit disagree_primes
    # The top_repeated_sets cover the structured data
    disagreement_sets = []
    for entry in data["disagreement_pattern"]["top_repeated_sets"]:
        primes = entry["primes"]
        count = entry["count"]
        for _ in range(count):
            disagreement_sets.append(tuple(sorted(primes)))

    # Also extract from example pairs (type_a, type_b, type_c)
    seen_pairs = set()
    for typ in ["type_a", "type_b", "type_c"]:
        if typ in data.get("example_near_congruences", {}):
            for ex in data["example_near_congruences"][typ]:
                key = (ex["label_i"], ex["label_j"])
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    disagreement_sets.append(tuple(sorted(ex["disagree_primes"])))

    # Build node set and edge weights
    nodes = set()
    edge_weights = Counter()
    edge_cooccurrence_sets = defaultdict(int)

    for dset in disagreement_sets:
        for p in dset:
            nodes.add(p)
        for p1, p2 in combinations(dset, 2):
            edge = (min(p1, p2), max(p1, p2))
            edge_weights[edge] += 1

    return nodes, edge_weights, disagreement_sets


def compute_graph_metrics(nodes, edge_weights):
    """Compute connected components, clustering coefficient, diameter."""
    nodes = sorted(nodes)
    n = len(nodes)
    node_idx = {p: i for i, p in enumerate(nodes)}

    # Adjacency list (unweighted for topology)
    adj = defaultdict(set)
    for (p1, p2), w in edge_weights.items():
        adj[p1].add(p2)
        adj[p2].add(p1)

    # Connected components via BFS
    visited = set()
    components = []
    for node in nodes:
        if node not in visited:
            component = []
            queue = [node]
            visited.add(node)
            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for nb in adj[curr]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            components.append(sorted(component))

    # Clustering coefficient (local, averaged)
    clustering_coeffs = {}
    for node in nodes:
        neighbors = adj[node]
        k = len(neighbors)
        if k < 2:
            clustering_coeffs[node] = 0.0
            continue
        # Count edges among neighbors
        triangles = 0
        for n1, n2 in combinations(neighbors, 2):
            if n2 in adj[n1]:
                triangles += 1
        clustering_coeffs[node] = 2.0 * triangles / (k * (k - 1))

    avg_clustering = sum(clustering_coeffs.values()) / len(clustering_coeffs) if clustering_coeffs else 0.0

    # Global clustering coefficient (transitivity)
    total_triangles = 0
    total_triples = 0
    for node in nodes:
        neighbors = list(adj[node])
        k = len(neighbors)
        if k < 2:
            continue
        total_triples += k * (k - 1) // 2
        for n1, n2 in combinations(neighbors, 2):
            if n2 in adj[n1]:
                total_triangles += 1
    # Each triangle counted 3 times
    global_clustering = total_triangles / total_triples if total_triples > 0 else 0.0

    # Diameter via BFS from each node (within largest component)
    def bfs_distances(start):
        dist = {start: 0}
        queue = [start]
        while queue:
            curr = queue.pop(0)
            for nb in adj[curr]:
                if nb not in dist:
                    dist[nb] = dist[curr] + 1
                    queue.append(nb)
        return dist

    diameter = 0
    eccentricities = {}
    for node in nodes:
        dists = bfs_distances(node)
        reachable = [d for d in dists.values()]
        ecc = max(reachable) if reachable else 0
        eccentricities[node] = ecc
        if ecc > diameter:
            diameter = ecc

    radius = min(eccentricities.values()) if eccentricities else 0

    # Degree distribution
    degrees = {node: len(adj[node]) for node in nodes}

    # Check if it's a clique
    max_edges = n * (n - 1) // 2
    actual_edges = len(edge_weights)
    is_clique = (actual_edges == max_edges) if n > 1 else True
    density = actual_edges / max_edges if max_edges > 0 else 0.0

    # Check if it's a tree
    is_tree = (actual_edges == n - 1) and (len(components) == 1)

    # Check if it's a path
    degree_counts = Counter(degrees.values())
    is_path = (len(components) == 1 and
               degree_counts.get(1, 0) == 2 and
               degree_counts.get(2, 0) == n - 2 and
               len(degree_counts) <= 2) if n > 2 else (n <= 2)

    return {
        "n_nodes": n,
        "n_edges": actual_edges,
        "nodes": nodes,
        "density": round(density, 4),
        "is_clique": is_clique,
        "is_tree": is_tree,
        "is_path": is_path,
        "n_components": len(components),
        "components": components,
        "diameter": diameter,
        "radius": radius,
        "avg_clustering_coefficient": round(avg_clustering, 4),
        "global_clustering_coefficient": round(global_clustering, 4),
        "degrees": {str(p): d for p, d in sorted(degrees.items())},
        "eccentricities": {str(p): e for p, e in sorted(eccentricities.items())},
        "clustering_per_node": {str(p): round(c, 4) for p, c in sorted(clustering_coeffs.items())},
    }


def legendre_symbol(a, p):
    """Compute Legendre symbol (a/p) via Euler's criterion."""
    if a % p == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return result if result == 1 else -1


def splitting_type(p, D):
    """
    Splitting type of prime p in Q(sqrt(D)):
      - "split" if (D/p) = 1  (p splits into two primes)
      - "inert" if (D/p) = -1 (p remains prime)
      - "ramified" if (D/p) = 0 (p divides discriminant)
    """
    ls = legendre_symbol(D % p, p)
    if ls == 0:
        return "ramified"
    elif ls == 1:
        return "split"
    else:
        return "inert"


def cm_splitting_analysis(nodes):
    """
    For each disagreement prime p, compute splitting type in:
      Q(sqrt(-3))  — discriminant -3 (CM field for j=0)
      Q(sqrt(-7))  — discriminant -7
    Also check Q(sqrt(-1)) and Q(sqrt(-2)) for completeness.
    """
    cm_fields = {
        "Q(sqrt(-3))": -3,
        "Q(sqrt(-7))": -7,
        "Q(sqrt(-1))": -1,
        "Q(sqrt(-2))": -2,
    }

    results = {}
    for p in sorted(nodes):
        results[str(p)] = {}
        for field_name, D in cm_fields.items():
            results[str(p)][field_name] = splitting_type(p, D)

    # Group by splitting pattern
    pattern_groups = defaultdict(list)
    for p in sorted(nodes):
        pattern = tuple(results[str(p)][f] for f in sorted(cm_fields.keys()))
        pattern_groups[pattern].append(p)

    return results, {str(k): v for k, v in pattern_groups.items()}


def analyze_edge_weights(edge_weights, nodes):
    """Analyze edge weight distribution."""
    if not edge_weights:
        return {}

    weights = list(edge_weights.values())
    sorted_edges = sorted(edge_weights.items(), key=lambda x: -x[1])

    return {
        "total_edges": len(weights),
        "min_weight": min(weights),
        "max_weight": max(weights),
        "mean_weight": round(sum(weights) / len(weights), 2),
        "median_weight": sorted(weights)[len(weights) // 2],
        "top_10_edges": [
            {"edge": [e[0], e[1]], "weight": w}
            for (e, w) in sorted_edges[:10]
        ],
        "bottom_5_edges": [
            {"edge": [e[0], e[1]], "weight": w}
            for (e, w) in sorted_edges[-5:]
        ],
    }


def check_cm_graph_correlation(graph_metrics, cm_results):
    """
    Check if graph neighborhoods correlate with CM splitting patterns.
    E.g., do split primes in Q(sqrt(-3)) cluster together in the defect graph?
    """
    # Group nodes by their splitting type in Q(sqrt(-3))
    split_3 = [int(p) for p, info in cm_results.items() if info["Q(sqrt(-3))"] == "split"]
    inert_3 = [int(p) for p, info in cm_results.items() if info["Q(sqrt(-3))"] == "inert"]
    split_7 = [int(p) for p, info in cm_results.items() if info["Q(sqrt(-7))"] == "split"]
    inert_7 = [int(p) for p, info in cm_results.items() if info["Q(sqrt(-7))"] == "inert"]

    # For the top-6 disagreement primes {37,43,61,79,19,31}
    top6 = {19, 31, 37, 43, 61, 79}
    top6_splitting = {}
    for p in sorted(top6):
        sp = str(p)
        if sp in cm_results:
            top6_splitting[sp] = cm_results[sp]

    return {
        "split_in_Q_sqrt_neg3": sorted(split_3),
        "inert_in_Q_sqrt_neg3": sorted(inert_3),
        "split_in_Q_sqrt_neg7": sorted(split_7),
        "inert_in_Q_sqrt_neg7": sorted(inert_7),
        "top6_primes_splitting": top6_splitting,
        "interpretation": (
            "If defect graph neighborhoods partition by CM splitting type, "
            "the disagreement is controlled by how primes decompose in the "
            "CM endomorphism ring."
        ),
    }


def main():
    print("Loading near-congruence results...")
    data = load_data()

    print("Building defect graph...")
    nodes, edge_weights, disagreement_sets = build_defect_graph(data)
    print(f"  Nodes: {len(nodes)}, Edges: {len(edge_weights)}")
    print(f"  Disagreement sets used: {len(disagreement_sets)}")

    print("Computing graph metrics...")
    graph_metrics = compute_graph_metrics(nodes, edge_weights)
    print(f"  Components: {graph_metrics['n_components']}")
    print(f"  Density: {graph_metrics['density']}")
    print(f"  Diameter: {graph_metrics['diameter']}")
    print(f"  Avg clustering: {graph_metrics['avg_clustering_coefficient']}")
    print(f"  Is clique: {graph_metrics['is_clique']}")
    print(f"  Is tree: {graph_metrics['is_tree']}")
    print(f"  Is path: {graph_metrics['is_path']}")

    print("Analyzing edge weights...")
    edge_analysis = analyze_edge_weights(edge_weights, nodes)

    print("Computing CM splitting types...")
    cm_results, cm_pattern_groups = cm_splitting_analysis(nodes)
    print(f"  Distinct splitting patterns: {len(cm_pattern_groups)}")

    print("Checking CM-graph correlation...")
    cm_correlation = check_cm_graph_correlation(graph_metrics, cm_results)

    # Determine graph structure type
    if graph_metrics["is_clique"]:
        structure_type = "complete_graph (clique)"
    elif graph_metrics["is_path"]:
        structure_type = "path"
    elif graph_metrics["is_tree"]:
        structure_type = "tree"
    elif graph_metrics["density"] > 0.8:
        structure_type = "near-clique (density > 0.8)"
    elif graph_metrics["density"] > 0.5:
        structure_type = "dense_graph"
    elif graph_metrics["n_components"] > 1:
        structure_type = "disconnected"
    else:
        structure_type = "general_connected"

    # Build output
    output = {
        "metadata": {
            "description": "Defect graph of near-congruence disagreement primes",
            "source": str(INPUT_PATH.name),
            "n_disagreement_sets_used": len(disagreement_sets),
            "n_unique_sets_in_source": data["disagreement_pattern"]["unique_sets"],
        },
        "graph_structure": {
            "type": structure_type,
            **graph_metrics,
        },
        "edge_weights": edge_analysis,
        "cm_splitting": {
            "per_prime": cm_results,
            "pattern_groups": cm_pattern_groups,
        },
        "cm_graph_correlation": cm_correlation,
        "verdict": {
            "structure_type": structure_type,
            "n_nodes": graph_metrics["n_nodes"],
            "n_edges": graph_metrics["n_edges"],
            "density": graph_metrics["density"],
            "n_components": graph_metrics["n_components"],
            "diameter": graph_metrics["diameter"],
            "avg_clustering": graph_metrics["avg_clustering_coefficient"],
            "global_clustering": graph_metrics["global_clustering_coefficient"],
            "cm_correlation_summary": (
                "Check whether split/inert partition matches graph neighborhoods"
            ),
        },
    }

    print(f"\nWriting results to {OUT_PATH}...")
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print("DEFECT GRAPH SUMMARY")
    print("=" * 60)
    print(f"Structure type: {structure_type}")
    print(f"Nodes: {graph_metrics['n_nodes']}, Edges: {graph_metrics['n_edges']}")
    print(f"Density: {graph_metrics['density']}")
    print(f"Connected components: {graph_metrics['n_components']}")
    print(f"Diameter: {graph_metrics['diameter']}, Radius: {graph_metrics['radius']}")
    print(f"Avg local clustering: {graph_metrics['avg_clustering_coefficient']}")
    print(f"Global clustering: {graph_metrics['global_clustering_coefficient']}")
    print(f"\nDegrees: {graph_metrics['degrees']}")
    print(f"\nCM splitting (top 6 primes):")
    for p in ['19', '31', '37', '43', '61', '79']:
        if p in cm_results:
            print(f"  p={p}: Q(sqrt(-3))={cm_results[p]['Q(sqrt(-3))']}, "
                  f"Q(sqrt(-7))={cm_results[p]['Q(sqrt(-7))']}")

    print(f"\nSplit in Q(sqrt(-3)): {cm_correlation['split_in_Q_sqrt_neg3']}")
    print(f"Inert in Q(sqrt(-3)): {cm_correlation['inert_in_Q_sqrt_neg3']}")
    print(f"Split in Q(sqrt(-7)): {cm_correlation['split_in_Q_sqrt_neg7']}")
    print(f"Inert in Q(sqrt(-7)): {cm_correlation['inert_in_Q_sqrt_neg7']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
