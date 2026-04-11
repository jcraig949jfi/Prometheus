#!/usr/bin/env python3
"""
OEIS Cross-Reference Graph Structure Analysis

Builds the OEIS cross-reference graph and measures:
- Degree distribution + power law fit
- Clustering coefficient
- Connected components
- Hub sequences
- Community detection (Louvain)
- Comparison to FLINT (alpha=1.26) and Lean (alpha=2.17) call graphs
"""

import json
import time
import warnings
from collections import Counter
from pathlib import Path

import numpy as np

# Paths
CROSSREFS = Path(r"F:\Prometheus\cartography\oeis\data\oeis_crossrefs.jsonl")
NAMES = Path(r"F:\Prometheus\cartography\oeis\data\oeis_names.json")
OUT = Path(r"F:\Prometheus\cartography\v2\oeis_graph_structure_results.json")

warnings.filterwarnings("ignore")


def load_edges():
    """Load directed edges from JSONL."""
    edges = []
    t0 = time.time()
    with open(CROSSREFS, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            edges.append((d['source'], d['target']))
    print(f"Loaded {len(edges):,} directed edges in {time.time()-t0:.1f}s")
    return edges


def load_names():
    """Load sequence names."""
    with open(NAMES, 'r', encoding='utf-8') as f:
        return json.load(f)


def fit_power_law(degrees, d_min=5):
    """
    MLE power law fit: alpha = 1 + n / sum(ln(d/d_min))
    for d >= d_min. Returns (alpha, d_min, n_tail).
    """
    tail = degrees[degrees >= d_min]
    if len(tail) < 10:
        return None, d_min, len(tail)
    n = len(tail)
    alpha = 1.0 + n / np.sum(np.log(tail / (d_min - 0.5)))
    return alpha, d_min, n


def compute_clustering_sample(adj, nodes, sample_size=10000):
    """
    Estimate clustering coefficient on a random sample of nodes.
    Uses undirected adjacency.
    """
    rng = np.random.default_rng(42)
    sample_nodes = rng.choice(nodes, size=min(sample_size, len(nodes)), replace=False)

    coefficients = []
    for node in sample_nodes:
        neighbors = adj.get(node, set())
        k = len(neighbors)
        if k < 2:
            continue
        # Count triangles
        triangles = 0
        nbr_list = list(neighbors)
        # For large neighborhoods, subsample
        if k > 200:
            sub = rng.choice(nbr_list, size=200, replace=False)
        else:
            sub = nbr_list
        for i in range(len(sub)):
            for j in range(i+1, len(sub)):
                if sub[j] in adj.get(sub[i], set()):
                    triangles += 1
        possible = k * (k - 1) / 2
        # Scale triangles if we subsampled
        if k > 200:
            scale = possible / (200 * 199 / 2)
            triangles *= scale
        coefficients.append(triangles / possible)

    return float(np.mean(coefficients)) if coefficients else 0.0


def connected_components_uf(edges, all_nodes):
    """Union-Find for connected components on undirected graph."""
    parent = {n: n for n in all_nodes}
    rank = {n: 0 for n in all_nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    for s, t in edges:
        if s in parent and t in parent:
            union(s, t)

    comp_sizes = Counter()
    for n in all_nodes:
        comp_sizes[find(n)] += 1

    sizes = sorted(comp_sizes.values(), reverse=True)
    return sizes


def louvain_communities(adj, nodes, max_iter=10):
    """
    Simple Louvain-style modularity optimization.
    For large graphs, use approximate approach.
    """
    # If graph too large for full Louvain, use label propagation instead
    if len(nodes) > 50000:
        return label_propagation(adj, nodes)

    node_to_comm = {n: i for i, n in enumerate(nodes)}
    m2 = sum(len(v) for v in adj.values())  # 2*edges for undirected

    if m2 == 0:
        return {0: list(nodes)}

    deg = {n: len(adj.get(n, set())) for n in nodes}

    for iteration in range(max_iter):
        moved = 0
        for node in nodes:
            if node not in adj or not adj[node]:
                continue
            current_comm = node_to_comm[node]

            # Count edges to each neighboring community
            comm_edges = Counter()
            for nbr in adj[node]:
                comm_edges[node_to_comm[nbr]] += 1

            # Find best community
            best_comm = current_comm
            best_gain = 0
            ki = deg[node]

            for comm, edges_to_comm in comm_edges.items():
                if comm == current_comm:
                    continue
                # Simplified modularity gain
                gain = edges_to_comm - ki * sum(deg[n] for n in adj.get(node, set()) if node_to_comm[n] == comm) / m2
                if gain > best_gain:
                    best_gain = gain
                    best_comm = comm

            if best_comm != current_comm:
                node_to_comm[node] = best_comm
                moved += 1

        if moved == 0:
            break

    # Collect communities
    communities = {}
    for n, c in node_to_comm.items():
        communities.setdefault(c, []).append(n)

    return communities


def label_propagation(adj, nodes, max_iter=20):
    """Label propagation for community detection on large graphs."""
    rng = np.random.default_rng(42)
    labels = {n: i for i, n in enumerate(nodes)}

    node_list = list(nodes)
    for iteration in range(max_iter):
        rng.shuffle(node_list)
        changed = 0
        for node in node_list:
            neighbors = adj.get(node, set())
            if not neighbors:
                continue
            # Most common label among neighbors
            label_counts = Counter(labels[nbr] for nbr in neighbors)
            most_common = label_counts.most_common(1)[0][0]
            if labels[node] != most_common:
                labels[node] = most_common
                changed += 1
        if changed == 0:
            break
        print(f"  Label propagation iter {iteration+1}: {changed:,} nodes changed")

    communities = {}
    for n, c in labels.items():
        communities.setdefault(c, []).append(n)
    return communities


def spectral_dimension_estimate(adj, nodes, n_walks=5000, max_steps=200):
    """
    Estimate spectral dimension from random walk return probability.
    P(return at step t) ~ t^(-d_s/2)
    """
    rng = np.random.default_rng(42)
    node_list = [n for n in nodes if n in adj and len(adj[n]) > 0]
    if not node_list:
        return None

    sample_starts = rng.choice(node_list, size=min(n_walks, len(node_list)), replace=True)

    # Track mean squared displacement or return counts
    return_counts = np.zeros(max_steps + 1)

    for start in sample_starts:
        current = start
        for step in range(1, max_steps + 1):
            nbrs = adj.get(current, set())
            if not nbrs:
                break
            current = rng.choice(list(nbrs))
            if current == start:
                return_counts[step] += 1

    # Fit power law to return probability for t >= 10
    steps = np.arange(10, max_steps + 1)
    probs = return_counts[10:] / n_walks
    # Smooth with running average
    window = 10
    if len(probs) > window:
        probs_smooth = np.convolve(probs, np.ones(window)/window, mode='valid')
        steps_smooth = steps[:len(probs_smooth)]
        mask = probs_smooth > 0
        if np.sum(mask) > 10:
            log_t = np.log(steps_smooth[mask])
            log_p = np.log(probs_smooth[mask])
            slope, _ = np.polyfit(log_t, log_p, 1)
            d_s = -2 * slope
            return float(d_s)
    return None


def main():
    t0 = time.time()

    # Load data
    edges = load_edges()
    names = load_names()

    # Build adjacency (undirected for most metrics)
    adj = {}
    all_nodes = set()
    for s, t in edges:
        all_nodes.add(s)
        all_nodes.add(t)
        adj.setdefault(s, set()).add(t)
        adj.setdefault(t, set()).add(s)

    # Also build directed out-degree
    out_deg = Counter()
    in_deg = Counter()
    for s, t in edges:
        out_deg[s] += 1
        in_deg[t] += 1

    n_nodes = len(all_nodes)
    n_edges = len(edges)
    node_list = sorted(all_nodes)

    print(f"\nGraph: {n_nodes:,} nodes, {n_edges:,} directed edges")

    # Degree distribution (undirected)
    degrees = np.array([len(adj.get(n, set())) for n in all_nodes])
    total_degree = degrees.astype(np.int64)

    print(f"Degree stats: min={degrees.min()}, median={np.median(degrees):.0f}, "
          f"mean={degrees.mean():.1f}, max={degrees.max()}")

    # Power law fit
    for d_min in [1, 2, 5, 10, 20]:
        alpha, _, n_tail = fit_power_law(degrees, d_min=d_min)
        if alpha:
            print(f"  Power law (d_min={d_min}): alpha={alpha:.3f}, n_tail={n_tail:,}")

    # Best fit with d_min=5 (standard)
    alpha_5, _, n_tail_5 = fit_power_law(degrees, d_min=5)
    # Also try d_min=10
    alpha_10, _, n_tail_10 = fit_power_law(degrees, d_min=10)

    # Degree histogram (binned)
    max_deg = int(degrees.max())
    bins = np.logspace(0, np.log10(max_deg + 1), 50)
    hist, bin_edges = np.histogram(degrees, bins=bins)
    degree_histogram = {f"{bin_edges[i]:.0f}-{bin_edges[i+1]:.0f}": int(hist[i])
                        for i in range(len(hist)) if hist[i] > 0}

    # Hub sequences (top 30 by total degree)
    total_deg_dict = {n: len(adj.get(n, set())) for n in all_nodes}
    top_hubs = sorted(total_deg_dict.items(), key=lambda x: -x[1])[:30]

    print(f"\nTop 15 hub sequences:")
    hubs_list = []
    for seq_id, deg in top_hubs:
        name = names.get(seq_id, "(unknown)")
        if len(name) > 80:
            name = name[:77] + "..."
        hubs_list.append({
            "sequence": seq_id,
            "degree": deg,
            "out_degree": out_deg.get(seq_id, 0),
            "in_degree": in_deg.get(seq_id, 0),
            "name": names.get(seq_id, "(unknown)")
        })
        if len(hubs_list) <= 15:
            print(f"  {seq_id} deg={deg:>5}  out={out_deg.get(seq_id,0):>5}  "
                  f"in={in_deg.get(seq_id,0):>5}  {name[:60]}")

    # Connected components
    print(f"\nComputing connected components...")
    comp_sizes = connected_components_uf(edges, all_nodes)
    n_components = len(comp_sizes)
    giant = comp_sizes[0] if comp_sizes else 0
    print(f"  Components: {n_components:,}, giant component: {giant:,} "
          f"({100*giant/n_nodes:.1f}%)")

    # Clustering coefficient (sampled)
    print(f"\nEstimating clustering coefficient (sample of 10,000 nodes)...")
    cc = compute_clustering_sample(adj, node_list, sample_size=10000)
    print(f"  Average clustering coefficient: {cc:.4f}")

    # Spectral dimension
    print(f"\nEstimating spectral dimension from random walks...")
    d_s = spectral_dimension_estimate(adj, node_list)
    if d_s:
        print(f"  Spectral dimension estimate: {d_s:.2f}")

    # Community detection
    print(f"\nRunning label propagation community detection...")
    communities = label_propagation(adj, node_list, max_iter=15)
    comm_sizes = sorted([len(v) for v in communities.values()], reverse=True)
    n_communities = len(comm_sizes)
    print(f"  Communities found: {n_communities:,}")
    print(f"  Largest 10: {comm_sizes[:10]}")

    # Modularity estimate
    m = n_edges  # directed edges count
    # For undirected interpretation, each directed edge is counted once
    total_undirected = sum(len(v) for v in adj.values()) // 2

    # Comparison to reference graphs
    comparisons = {
        "FLINT_call_graph": {"alpha": 1.26, "description": "C number theory library function calls"},
        "Lean_import_graph": {"alpha": 2.17, "description": "Lean4 mathlib module imports"},
        "OEIS_crossref_graph": {
            "alpha_dmin5": alpha_5,
            "alpha_dmin10": alpha_10,
            "description": "OEIS sequence cross-references"
        }
    }

    if alpha_5:
        if alpha_5 < 1.5:
            topology_class = "ultra-dense hub-and-spoke (like FLINT)"
        elif alpha_5 < 2.0:
            topology_class = "moderately heavy-tailed (between FLINT and Lean)"
        elif alpha_5 < 2.5:
            topology_class = "near-Lean hierarchical"
        else:
            topology_class = "steep decay, weak hubs"
    else:
        topology_class = "unknown"

    # Assemble results
    elapsed = time.time() - t0

    results = {
        "metadata": {
            "dataset": "OEIS cross-reference graph",
            "source": str(CROSSREFS),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "computation_time_s": round(elapsed, 1)
        },
        "graph_summary": {
            "n_nodes": n_nodes,
            "n_directed_edges": n_edges,
            "n_undirected_edges": total_undirected,
            "density": round(2 * total_undirected / (n_nodes * (n_nodes - 1)), 8) if n_nodes > 1 else 0
        },
        "degree_distribution": {
            "min": int(degrees.min()),
            "median": float(np.median(degrees)),
            "mean": round(float(degrees.mean()), 2),
            "max": int(degrees.max()),
            "std": round(float(degrees.std()), 2),
            "p95": int(np.percentile(degrees, 95)),
            "p99": int(np.percentile(degrees, 99))
        },
        "power_law_fit": {
            "alpha_dmin5": round(alpha_5, 4) if alpha_5 else None,
            "n_tail_dmin5": n_tail_5,
            "alpha_dmin10": round(alpha_10, 4) if alpha_10 else None,
            "n_tail_dmin10": n_tail_10,
            "interpretation": topology_class
        },
        "clustering_coefficient": {
            "mean_sampled": round(cc, 5),
            "sample_size": 10000,
            "note": "Estimated from 10K random node sample"
        },
        "connected_components": {
            "n_components": n_components,
            "giant_component_size": giant,
            "giant_component_fraction": round(giant / n_nodes, 4),
            "top_10_sizes": comp_sizes[:10]
        },
        "spectral_dimension": {
            "estimate": round(d_s, 3) if d_s else None,
            "method": "random walk return probability scaling"
        },
        "communities": {
            "n_communities": n_communities,
            "method": "label propagation",
            "top_10_sizes": comm_sizes[:10],
            "modularity_note": "Label propagation used for scalability on 380K+ nodes"
        },
        "hub_sequences": hubs_list,
        "reference_comparison": {
            "FLINT_call_graph_alpha": 1.26,
            "Lean_import_graph_alpha": 2.17,
            "OEIS_crossref_alpha_dmin5": round(alpha_5, 4) if alpha_5 else None,
            "OEIS_crossref_alpha_dmin10": round(alpha_10, 4) if alpha_10 else None,
            "position": topology_class,
            "analysis": (
                f"OEIS alpha={alpha_5:.2f} (d_min=5). "
                f"FLINT=1.26 (flat, dense hubs), Lean=2.17 (hierarchical). "
                f"OEIS {'is flatter than FLINT — extreme hub dominance' if alpha_5 and alpha_5 < 1.26 else 'sits between FLINT and Lean' if alpha_5 and alpha_5 < 2.17 else 'is steeper than Lean' if alpha_5 else 'unknown'}."
            ) if alpha_5 else "Power law fit unavailable"
        },
        "degree_histogram_logbinned": degree_histogram
    }

    # Save
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Results saved to {OUT}")
    print(f"Total time: {elapsed:.1f}s")
    print(f"{'='*60}")

    # Print summary comparison
    print(f"\n--- COMPARISON ---")
    print(f"  FLINT call graph:    alpha = 1.26")
    print(f"  OEIS crossref graph: alpha = {alpha_5:.4f} (d_min=5)" if alpha_5 else "  OEIS: no fit")
    print(f"  Lean import graph:   alpha = 2.17")
    print(f"  Position: {topology_class}")


if __name__ == '__main__':
    main()
