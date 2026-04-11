"""
lean_manifold_dim.py — List2 #5: Formal Logic Manifold Dimension

Treat the Lean mathlib import graph as a discrete metric space.
Estimate intrinsic manifold dimension using the Levina-Bickel MLE
on k-nearest-neighbor distances.

Graph: 8,411+ files, ~34K directed edges.
Method:
  1. Build undirected import graph
  2. Sample 500 random nodes, compute shortest paths to all others
  3. For each sampled node, find k-NN distances (k=5,10,20)
  4. Levina-Bickel MLE: d_hat(x) = [ 1/(k-1) sum_{j=1}^{k-1} log(d_k(x)/d_j(x)) ]^{-1}
  5. Global estimate = mean of d_hat across all sampled nodes
"""

import re
import json
import math
import numpy as np
from collections import defaultdict, deque, Counter
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MATHLIB_SRC = Path("F:/Prometheus/cartography/mathlib/mathlib4_source")
OUTPUT_JSON = Path("F:/Prometheus/cartography/v2/lean_manifold_dim_results.json")
SAMPLE_SIZE = 500
K_VALUES = [5, 10, 20]
SEED = 42

# ---------------------------------------------------------------------------
# Step 1: Parse imports and build graph (reused from lean_proof_depth.py)
# ---------------------------------------------------------------------------

def parse_lean_imports(filepath):
    """Extract import targets from a .lean file."""
    imports = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                m = re.match(r'^(?:public\s+)?import\s+(\S+)', line)
                if m:
                    imports.append(m.group(1))
    except Exception:
        pass
    return imports


def build_import_graph():
    """Build import dependency graph from all .lean files."""
    print("Scanning Lean mathlib source...")
    lean_files = sorted(MATHLIB_SRC.rglob("*.lean"))
    print(f"  Found {len(lean_files)} .lean files")

    edges = []
    all_sources = set()

    for fp in lean_files:
        rel = fp.relative_to(MATHLIB_SRC)
        module_name = str(rel).replace('\\', '/').replace('/', '.').replace('.lean', '')
        all_sources.add(module_name)
        imports = parse_lean_imports(fp)
        for imp in imports:
            edges.append((module_name, imp))

    all_nodes = set(all_sources)
    for src, tgt in edges:
        all_nodes.add(tgt)

    print(f"  {len(all_nodes)} nodes, {len(edges)} directed edges")
    return sorted(all_nodes), edges


# ---------------------------------------------------------------------------
# Step 2: Build undirected adjacency and compute BFS distances from samples
# ---------------------------------------------------------------------------

def build_undirected_adjacency(nodes, edges):
    """Convert directed import graph to undirected adjacency list."""
    node_set = set(nodes)
    adj = defaultdict(list)
    edge_count = 0
    for src, tgt in edges:
        if src in node_set and tgt in node_set:
            adj[src].append(tgt)
            adj[tgt].append(src)
            edge_count += 1
    print(f"  Undirected graph: {len(node_set)} nodes, {edge_count} undirected edges")
    return adj


def bfs_distances(adj, source, all_nodes):
    """BFS from source, return dict of distances to all reachable nodes."""
    dist = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        d = dist[node]
        for nb in adj[node]:
            if nb not in dist:
                dist[nb] = d + 1
                queue.append(nb)
    return dist


# ---------------------------------------------------------------------------
# Step 3: Levina-Bickel MLE dimension estimator
# ---------------------------------------------------------------------------

def levina_bickel_estimate(distances_sorted, k):
    """
    Levina-Bickel MLE for intrinsic dimension at a single point.

    distances_sorted: sorted list of distances to neighbors (ascending, excluding 0).
    k: number of nearest neighbors to use.

    d_hat = [ 1/(k-1) * sum_{j=1}^{k-1} log(d_k / d_j) ]^{-1}

    Returns d_hat or None if degenerate.
    """
    if len(distances_sorted) < k:
        return None

    d_k = distances_sorted[k - 1]  # k-th nearest neighbor distance
    if d_k == 0:
        return None

    log_sum = 0.0
    valid = 0
    for j in range(k - 1):  # j = 0..k-2 => distances[0]..distances[k-2]
        d_j = distances_sorted[j]
        if d_j <= 0:
            continue
        log_sum += math.log(d_k / d_j)
        valid += 1

    if valid == 0:
        return None

    avg_log = log_sum / valid
    if avg_log <= 0:
        return None

    return 1.0 / avg_log


# ---------------------------------------------------------------------------
# Step 4: Main computation
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("List2 #5: Formal Logic Manifold Dimension")
    print("  Levina-Bickel MLE on Lean mathlib import graph")
    print("=" * 70)

    # Build graph
    nodes, edges = build_import_graph()
    adj = build_undirected_adjacency(nodes, edges)

    # Sample nodes
    rng = np.random.RandomState(SEED)
    n_nodes = len(nodes)
    sample_idx = rng.choice(n_nodes, size=min(SAMPLE_SIZE, n_nodes), replace=False)
    sample_nodes = [nodes[i] for i in sample_idx]
    print(f"\n  Sampled {len(sample_nodes)} nodes for distance computation")

    # Compute BFS distances from each sample node
    print("  Computing BFS shortest paths from each sample node...")
    all_distance_lists = {}  # node -> sorted list of distances to all other nodes

    for i, src in enumerate(sample_nodes):
        if (i + 1) % 50 == 0:
            print(f"    BFS {i+1}/{len(sample_nodes)}...")
        dist_dict = bfs_distances(adj, src, nodes)
        # Collect distances to all reachable nodes (excluding self)
        dists = sorted([d for node, d in dist_dict.items() if d > 0])
        all_distance_lists[src] = dists

    # Check connectivity
    reachable_counts = [len(d) for d in all_distance_lists.values()]
    mean_reachable = np.mean(reachable_counts)
    print(f"  Mean reachable nodes per sample: {mean_reachable:.0f} / {n_nodes}")

    # Compute Levina-Bickel MLE for each k
    print("\n  Computing Levina-Bickel dimension estimates...")
    results_by_k = {}

    for k in K_VALUES:
        estimates = []
        for src in sample_nodes:
            dists = all_distance_lists[src]
            d_hat = levina_bickel_estimate(dists, k)
            if d_hat is not None and np.isfinite(d_hat):
                estimates.append(d_hat)

        arr = np.array(estimates)
        mean_dim = float(np.mean(arr))
        median_dim = float(np.median(arr))
        std_dim = float(np.std(arr))

        # Percentiles
        p5 = float(np.percentile(arr, 5))
        p25 = float(np.percentile(arr, 25))
        p75 = float(np.percentile(arr, 75))
        p95 = float(np.percentile(arr, 95))

        print(f"\n  k={k}:")
        print(f"    Valid estimates:  {len(estimates)} / {len(sample_nodes)}")
        print(f"    Mean dimension:  {mean_dim:.4f}")
        print(f"    Median dimension:{median_dim:.4f}")
        print(f"    Std:             {std_dim:.4f}")
        print(f"    [5%, 25%, 75%, 95%]: [{p5:.2f}, {p25:.2f}, {p75:.2f}, {p95:.2f}]")

        # Histogram of dimension estimates (binned to 0.5 width)
        bins = np.arange(0, max(arr) + 1, 0.5)
        hist, bin_edges = np.histogram(arr, bins=bins)
        hist_dict = {}
        for j in range(len(hist)):
            if hist[j] > 0:
                label = f"{bin_edges[j]:.1f}-{bin_edges[j+1]:.1f}"
                hist_dict[label] = int(hist[j])

        results_by_k[str(k)] = {
            "k": k,
            "num_valid": len(estimates),
            "num_samples": len(sample_nodes),
            "mean_dimension": round(mean_dim, 4),
            "median_dimension": round(median_dim, 4),
            "std_dimension": round(std_dim, 4),
            "percentiles": {
                "p5": round(p5, 4),
                "p25": round(p25, 4),
                "p75": round(p75, 4),
                "p95": round(p95, 4),
            },
            "histogram": hist_dict,
        }

    # Global estimate: mean across k values (use k=10 as primary)
    primary_k = 10
    global_dim = results_by_k[str(primary_k)]["mean_dimension"]

    # Also compute harmonic mean across k values
    k_means = [results_by_k[str(k)]["mean_dimension"] for k in K_VALUES]
    harmonic_mean = float(len(k_means) / sum(1.0/m for m in k_means))

    print(f"\n  === GLOBAL DIMENSION ESTIMATE ===")
    print(f"  Primary (k=10 mean):  {global_dim:.4f}")
    print(f"  Harmonic mean (all k): {harmonic_mean:.4f}")
    print(f"  All k means: {[round(m, 4) for m in k_means]}")

    # Distance distribution stats
    all_dists_flat = []
    for src in sample_nodes:
        dists = all_distance_lists[src]
        if len(dists) >= 20:
            all_dists_flat.extend(dists[:20])
    dist_arr = np.array(all_dists_flat)
    dist_hist = Counter(all_dists_flat)

    results = {
        "metadata": {
            "experiment": "List2 #5: Formal Logic Manifold Dimension",
            "method": "Levina-Bickel MLE on k-NN distances in undirected Lean mathlib import graph",
            "source": str(MATHLIB_SRC),
            "timestamp": datetime.now().isoformat(),
            "sample_size": len(sample_nodes),
            "k_values": K_VALUES,
            "seed": SEED,
        },
        "graph": {
            "num_nodes": n_nodes,
            "num_directed_edges": len(edges),
            "mean_reachable_per_sample": round(float(mean_reachable), 1),
        },
        "dimension_estimates": results_by_k,
        "global_estimate": {
            "primary_k": primary_k,
            "dimension_mle": round(global_dim, 4),
            "harmonic_mean_all_k": round(harmonic_mean, 4),
            "all_k_means": {str(k): round(m, 4) for k, m in zip(K_VALUES, k_means)},
        },
        "distance_distribution": {
            "mean_knn_distance_k20": round(float(np.mean(dist_arr)), 4) if len(dist_arr) > 0 else None,
            "distance_histogram_k20_neighborhood": {str(k): int(v) for k, v in sorted(dist_hist.items())},
        },
        "interpretation": {
            "note": "Intrinsic dimension of formal logic dependency structure",
            "expected": "~3.14 (low-dimensional manifold)",
        },
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
