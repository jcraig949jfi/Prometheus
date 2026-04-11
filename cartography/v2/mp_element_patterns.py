"""
Materials Project Element Combination Patterns — "Periodic Table" of Crystal Compositions

Loads 10K MP sample, parses element sets from formulas, builds co-occurrence
matrix and element graph, computes degree distribution, clustering, communities,
hub analysis, and power-law fit.  Compares to OEIS cross-reference graph (α=2.31).

Output → mp_element_patterns_results.json
"""

import json
import re
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

# ── paths ────────────────────────────────────────────────────────────────────
DATA = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT  = Path(__file__).parent / "mp_element_patterns_results.json"

# ── helpers ──────────────────────────────────────────────────────────────────
def parse_elements(formula: str) -> set[str]:
    """Extract element symbols from a chemical formula string."""
    return set(re.findall(r'[A-Z][a-z]?', formula))


def power_law_mle(degrees: list[int], x_min: int = 1) -> tuple[float, float]:
    """
    Maximum-likelihood estimate of power-law exponent α for discrete data.
    Returns (alpha, x_min).  Uses Clauset et al. (2009) estimator.
    """
    vals = np.array([d for d in degrees if d >= x_min], dtype=float)
    if len(vals) < 10:
        return float('nan'), x_min
    alpha = 1.0 + len(vals) / np.sum(np.log(vals / (x_min - 0.5)))
    return float(alpha), x_min


def louvain_communities(adj: dict[str, dict[str, int]], seed: int = 42) -> dict[str, int]:
    """
    Simple greedy modularity-maximisation (one pass Louvain-like).
    adj: {node: {neighbor: weight}}
    Returns {node: community_id}.
    """
    rng = np.random.default_rng(seed)
    nodes = list(adj.keys())
    rng.shuffle(nodes)

    community = {n: i for i, n in enumerate(nodes)}
    total_weight = sum(w for n in adj for w in adj[n].values()) / 2.0
    if total_weight == 0:
        return community

    # node strength
    k = {n: sum(adj[n].values()) for n in nodes}

    def delta_q(node, target_comm):
        """Change in modularity for moving node into target_comm."""
        sum_in = 0.0   # sum of weights inside target_comm involving node
        sum_tot = 0.0   # sum of strengths of nodes in target_comm
        ki = k[node]
        for nbr, w in adj[node].items():
            if community[nbr] == target_comm:
                sum_in += w
            if community[nbr] == target_comm and nbr != node:
                sum_tot += k[nbr]
        # Also add strengths of non-neighbor community members
        # (approximation: only consider neighbor contributions for speed)
        return (sum_in / total_weight) - (ki * sum_tot) / (2 * total_weight ** 2)

    improved = True
    passes = 0
    while improved and passes < 20:
        improved = False
        passes += 1
        for node in nodes:
            current_comm = community[node]
            neighbor_comms = {community[nbr] for nbr in adj[node]}
            best_comm = current_comm
            best_gain = 0.0
            for nc in neighbor_comms:
                if nc == current_comm:
                    continue
                gain = delta_q(node, nc) - delta_q(node, current_comm)
                if gain > best_gain:
                    best_gain = gain
                    best_comm = nc
            if best_comm != current_comm:
                community[node] = best_comm
                improved = True

    # Relabel communities to 0..n
    labels = {}
    for n in sorted(community, key=lambda x: community[x]):
        c = community[n]
        if c not in labels:
            labels[c] = len(labels)
        community[n] = labels[c]
    return community


# ── main analysis ────────────────────────────────────────────────────────────
def main():
    with open(DATA) as f:
        data = json.load(f)
    print(f"Loaded {len(data)} materials")

    # 1. Parse element sets ────────────────────────────────────────────────────
    records = []
    for d in data:
        elems = sorted(parse_elements(d["formula"]))
        records.append({"material_id": d["material_id"], "formula": d["formula"],
                        "elements": elems, "n_elements": len(elems)})

    # Composition sizes
    size_counts = Counter(r["n_elements"] for r in records)
    print(f"Composition sizes: {dict(sorted(size_counts.items()))}")

    # Element frequencies
    elem_freq = Counter()
    for r in records:
        for e in r["elements"]:
            elem_freq[e] += 1
    top_elements = elem_freq.most_common(30)
    print(f"Top 10 elements: {top_elements[:10]}")

    # 2. Co-occurrence matrix ──────────────────────────────────────────────────
    cooccur = defaultdict(int)
    for r in records:
        for a, b in combinations(r["elements"], 2):
            pair = tuple(sorted([a, b]))
            cooccur[pair] += 1

    top_pairs = sorted(cooccur.items(), key=lambda x: -x[1])[:50]
    print(f"\nTop 10 element pairs:")
    for (a, b), c in top_pairs[:10]:
        print(f"  {a}-{b}: {c}")

    # 3. Most common compositions by size ──────────────────────────────────────
    binary_counts = Counter()
    ternary_counts = Counter()
    quaternary_counts = Counter()
    for r in records:
        key = tuple(r["elements"])
        if r["n_elements"] == 2:
            binary_counts[key] += 1
        elif r["n_elements"] == 3:
            ternary_counts[key] += 1
        elif r["n_elements"] == 4:
            quaternary_counts[key] += 1

    top_binary = binary_counts.most_common(20)
    top_ternary = ternary_counts.most_common(20)
    top_quaternary = quaternary_counts.most_common(20)

    print(f"\nTop 5 binary:     {top_binary[:5]}")
    print(f"Top 5 ternary:    {top_ternary[:5]}")
    print(f"Top 5 quaternary: {top_quaternary[:5]}")

    # 4. Element-element graph ─────────────────────────────────────────────────
    adj = defaultdict(lambda: defaultdict(int))
    for (a, b), w in cooccur.items():
        adj[a][b] += w
        adj[b][a] += w

    all_elements = sorted(adj.keys())
    n_nodes = len(all_elements)
    n_edges = len(cooccur)
    print(f"\nGraph: {n_nodes} nodes, {n_edges} edges")

    # Degree distribution (unweighted)
    degree = {e: len(adj[e]) for e in all_elements}
    # Weighted degree (strength)
    strength = {e: sum(adj[e].values()) for e in all_elements}

    degree_dist = Counter(degree.values())
    sorted_degrees = sorted(degree.items(), key=lambda x: -x[1])

    print(f"\nTop 10 hub elements (by degree):")
    for e, d in sorted_degrees[:10]:
        print(f"  {e}: degree={d}, strength={strength[e]}, frequency={elem_freq[e]}")

    # 5. Clustering coefficient (unweighted) ────────────────────────────────────
    clustering = {}
    for node in all_elements:
        neighbors = list(adj[node].keys())
        k = len(neighbors)
        if k < 2:
            clustering[node] = 0.0
            continue
        triangles = 0
        for i in range(k):
            for j in range(i + 1, k):
                if neighbors[j] in adj[neighbors[i]]:
                    triangles += 1
        clustering[node] = 2.0 * triangles / (k * (k - 1))

    avg_clustering = np.mean(list(clustering.values()))
    print(f"\nUnweighted graph is complete (density=1.0), so clustering=1.0 everywhere.")
    print(f"Real structure is in the WEIGHTS. Analyzing thresholded graph...")

    # 5b. Thresholded graph — keep only edges above median weight ─────────────
    weights = list(cooccur.values())
    weight_median = np.median(weights)
    weight_p75 = np.percentile(weights, 75)
    thresholds = {
        "median": int(weight_median),
        "p75": int(weight_p75),
        "p90": int(np.percentile(weights, 90)),
    }
    print(f"  Weight thresholds: {thresholds}")

    # Use median threshold for main analysis
    thresh = int(weight_median)
    adj_thresh = defaultdict(lambda: defaultdict(int))
    n_edges_thresh = 0
    for (a, b), w in cooccur.items():
        if w >= thresh:
            adj_thresh[a][b] = w
            adj_thresh[b][a] = w
            n_edges_thresh += 1

    elems_thresh = sorted(adj_thresh.keys())
    degree_thresh = {e: len(adj_thresh[e]) for e in elems_thresh}
    strength_thresh = {e: sum(adj_thresh[e].values()) for e in elems_thresh}

    print(f"  Thresholded graph (w>={thresh}): {len(elems_thresh)} nodes, {n_edges_thresh} edges")
    density_thresh = 2 * n_edges_thresh / (len(elems_thresh) * (len(elems_thresh) - 1)) if len(elems_thresh) > 1 else 0
    print(f"  Density: {density_thresh:.4f}")

    # Clustering on thresholded graph
    clustering_thresh = {}
    for node in elems_thresh:
        neighbors = list(adj_thresh[node].keys())
        k = len(neighbors)
        if k < 2:
            clustering_thresh[node] = 0.0
            continue
        triangles = 0
        for i in range(k):
            for j in range(i + 1, k):
                if neighbors[j] in adj_thresh[neighbors[i]]:
                    triangles += 1
        clustering_thresh[node] = 2.0 * triangles / (k * (k - 1))

    avg_clustering_thresh = np.mean(list(clustering_thresh.values())) if clustering_thresh else 0
    print(f"  Avg clustering (thresholded): {avg_clustering_thresh:.4f}")

    # Degree distribution of thresholded graph
    degree_dist_thresh = Counter(degree_thresh.values())
    sorted_degrees_thresh = sorted(degree_thresh.items(), key=lambda x: -x[1])
    print(f"  Top 10 hubs (thresholded):")
    for e, d in sorted_degrees_thresh[:10]:
        print(f"    {e}: degree={d}, strength={strength_thresh[e]}")

    # High-clustering elements in thresholded graph
    high_cluster_thresh = [(e, clustering_thresh[e], degree_thresh[e])
                           for e in elems_thresh if degree_thresh[e] > 5]
    high_cluster_thresh.sort(key=lambda x: -x[1])

    # 6. Communities ───────────────────────────────────────────────────────────
    adj_dict = {e: dict(adj[e]) for e in all_elements}
    communities = louvain_communities(adj_dict)
    n_communities = len(set(communities.values()))
    comm_sizes = Counter(communities.values())

    print(f"\nCommunities: {n_communities}")
    for cid, size in comm_sizes.most_common(10):
        members = [e for e, c in communities.items() if c == cid]
        members.sort(key=lambda e: -strength[e])
        print(f"  Community {cid} ({size} elements): {members[:8]}...")

    # 7. Power law fit (use thresholded degree — unweighted is trivial) ──────
    degree_vals = list(degree_thresh.values())
    alpha, x_min = power_law_mle(degree_vals, x_min=1)
    print(f"\nPower law: alpha = {alpha:.3f} (x_min={x_min})")
    print(f"OEIS cross-reference graph: alpha = 2.31")
    print(f"Difference: {abs(alpha - 2.31):.3f}")

    # Also fit with higher x_min
    for xm in [2, 5, 10]:
        a, _ = power_law_mle(degree_vals, x_min=xm)
        print(f"  alpha(x_min={xm}) = {a:.3f}, n={sum(1 for d in degree_vals if d >= xm)}")

    # Degree distribution for output
    degree_dist_out = sorted([(k, v) for k, v in degree_dist.items()])

    # 8. Weighted co-occurrence statistics ─────────────────────────────────────
    weights = list(cooccur.values())
    print(f"\nCo-occurrence weights: min={min(weights)}, max={max(weights)}, "
          f"mean={np.mean(weights):.1f}, median={np.median(weights):.1f}")

    # Weight distribution -- is it heavy-tailed?
    weight_alpha, _ = power_law_mle(weights, x_min=1)
    print(f"Weight power law: alpha = {weight_alpha:.3f}")

    # ── assemble results ─────────────────────────────────────────────────────
    results = {
        "metadata": {
            "source": "materials_project_10k.json",
            "n_materials": len(data),
            "n_unique_elements": n_nodes,
            "n_edges": n_edges,
            "analysis": "Element co-occurrence patterns in Materials Project 10K sample"
        },
        "composition_sizes": dict(sorted(size_counts.items())),
        "top_elements": [{"element": e, "count": c} for e, c in top_elements],
        "top_pairs": [{"pair": list(p), "count": c} for p, c in top_pairs],
        "top_binary": [{"elements": list(k), "count": v} for k, v in top_binary],
        "top_ternary": [{"elements": list(k), "count": v} for k, v in top_ternary],
        "top_quaternary": [{"elements": list(k), "count": v} for k, v in top_quaternary],
        "graph_unweighted": {
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "density": 2 * n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0,
            "avg_clustering": float(avg_clustering),
            "note": "Complete graph — all element pairs co-occur at least once in 10K sample",
            "degree_distribution": [{"degree": d, "count": c} for d, c in degree_dist_out],
        },
        "graph_thresholded": {
            "threshold": thresh,
            "threshold_label": f"weight >= median ({thresh})",
            "n_nodes": len(elems_thresh),
            "n_edges": n_edges_thresh,
            "density": round(density_thresh, 4),
            "avg_clustering": round(avg_clustering_thresh, 4),
            "degree_distribution": [{"degree": d, "count": c}
                                    for d, c in sorted(degree_dist_thresh.items())],
            "top_hubs": [{"element": e, "degree": degree_thresh[e],
                          "strength": strength_thresh[e],
                          "clustering": round(clustering_thresh.get(e, 0), 4)}
                         for e, _ in sorted_degrees_thresh[:20]],
        },
        "hubs": [
            {"element": e, "degree": degree[e], "strength": strength[e],
             "frequency": elem_freq[e], "clustering": round(clustering[e], 4)}
            for e, _ in sorted_degrees[:20]
        ],
        "power_law": {
            "degree_alpha": round(alpha, 4),
            "degree_x_min": x_min,
            "weight_alpha": round(weight_alpha, 4),
            "oeis_alpha": 2.31,
            "comparison": (
                f"MP degree α={alpha:.3f} vs OEIS α=2.31; "
                f"{'similar' if abs(alpha - 2.31) < 0.3 else 'different'} regime"
            )
        },
        "communities": {
            "n_communities": n_communities,
            "sizes": {str(cid): size for cid, size in comm_sizes.most_common()},
            "top_communities": []
        },
        "weight_stats": {
            "min": int(min(weights)),
            "max": int(max(weights)),
            "mean": round(float(np.mean(weights)), 2),
            "median": round(float(np.median(weights)), 2),
            "std": round(float(np.std(weights)), 2),
        }
    }

    # Community details
    for cid, size in comm_sizes.most_common(10):
        members = [e for e, c in communities.items() if c == cid]
        members.sort(key=lambda e: -strength.get(e, 0))
        results["communities"]["top_communities"].append({
            "id": cid,
            "size": size,
            "top_members": members[:10],
            "all_members": members
        })

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
