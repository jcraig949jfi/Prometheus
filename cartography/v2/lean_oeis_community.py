#!/usr/bin/env python3
"""
Lean Mathlib vs OEIS Cross-Reference Graph — Community Structure Overlap

Since the two graphs have different node semantics (Lean modules vs OEIS sequences),
direct Adjusted Rand Index is impossible. Instead we compare:

1. Community SIZE distributions (KS test)
2. Modularity Q values
3. Degree-distribution shape within communities (mean alpha comparison)
4. Structural similarity: correlation of (n_communities, modularity, mean_community_size,
   clustering_coefficient) summary vectors

Data sources:
- Lean import graph: 8,411 nodes, 34K edges (mathlib4 .lean files)
- OEIS cross-reference graph: 347K nodes, 1.28M edges (oeis_crossrefs.jsonl)

Saves to: cartography/v2/lean_oeis_community_results.json
"""

import json
import os
import re
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MATHLIB_SRC = Path("F:/Prometheus/cartography/mathlib/mathlib4_source")
OEIS_CROSSREFS = Path("F:/Prometheus/cartography/oeis/data/oeis_crossrefs.jsonl")
OUT = Path("F:/Prometheus/cartography/v2/lean_oeis_community_results.json")

# If mathlib4_source doesn't exist, try the data subdirectory
if not MATHLIB_SRC.exists():
    MATHLIB_SRC = Path("F:/Prometheus/cartography/mathlib/data/mathlib4")


# ---------------------------------------------------------------------------
# Graph utilities
# ---------------------------------------------------------------------------
def build_undirected_adj(edges):
    """Build undirected adjacency dict from edge list."""
    adj = defaultdict(set)
    for s, t in edges:
        adj[s].add(t)
        adj[t].add(s)
    return dict(adj)


def compute_modularity(adj, node_to_comm):
    """Compute Newman modularity Q for a given partition."""
    m2 = sum(len(v) for v in adj.values())  # 2 * undirected edges
    if m2 == 0:
        return 0.0
    deg = {n: len(adj.get(n, set())) for n in node_to_comm}
    Q = 0.0
    for node, comm in node_to_comm.items():
        ki = deg.get(node, 0)
        for nbr in adj.get(node, set()):
            if node_to_comm.get(nbr) == comm:
                Q += 1.0 - ki * deg.get(nbr, 0) / m2
    Q /= m2
    return float(Q)


def louvain_simple(adj, nodes, max_iter=15):
    """
    Simple Louvain-style modularity optimization.
    For graphs < 50K nodes.
    """
    node_list = list(nodes)
    node_to_comm = {n: i for i, n in enumerate(node_list)}
    m2 = sum(len(v) for v in adj.values())
    if m2 == 0:
        return node_to_comm

    deg = {n: len(adj.get(n, set())) for n in node_list}

    # Sum of degrees in each community
    comm_deg_sum = defaultdict(float)
    for n in node_list:
        comm_deg_sum[node_to_comm[n]] += deg[n]

    for iteration in range(max_iter):
        moved = 0
        for node in node_list:
            if node not in adj or not adj[node]:
                continue
            current_comm = node_to_comm[node]
            ki = deg[node]

            # Temporarily remove node from its community
            comm_deg_sum[current_comm] -= ki

            # Count edges to each neighboring community
            comm_edges = Counter()
            for nbr in adj[node]:
                comm_edges[node_to_comm[nbr]] += 1

            # Find best community by modularity gain
            best_comm = current_comm
            best_dQ = 0.0

            for comm, e_to_c in comm_edges.items():
                # Modularity gain: e_to_c/m - ki * sigma_c / m^2
                dQ = e_to_c / (m2 / 2.0) - ki * comm_deg_sum[comm] / (m2 / 2.0) ** 2
                if dQ > best_dQ:
                    best_dQ = dQ
                    best_comm = comm

            node_to_comm[node] = best_comm
            comm_deg_sum[best_comm] += ki

            if best_comm != current_comm:
                moved += 1

        if moved == 0:
            break
        print(f"  Louvain iter {iteration+1}: {moved} nodes moved")

    return node_to_comm


def label_propagation(adj, nodes, max_iter=20):
    """Label propagation for community detection (for large graphs)."""
    rng = np.random.default_rng(42)
    node_list = list(nodes)
    labels = {n: i for i, n in enumerate(node_list)}

    for iteration in range(max_iter):
        rng.shuffle(node_list)
        changed = 0
        for node in node_list:
            neighbors = adj.get(node, set())
            if not neighbors:
                continue
            label_counts = Counter(labels[nbr] for nbr in neighbors)
            most_common = label_counts.most_common(1)[0][0]
            if labels[node] != most_common:
                labels[node] = most_common
                changed += 1
        if changed == 0:
            break
        print(f"  LP iter {iteration+1}: {changed:,} changed")

    return labels


def clustering_coefficient_sample(adj, nodes, sample_size=5000):
    """Estimate mean clustering coefficient from a sample."""
    rng = np.random.default_rng(42)
    node_list = [n for n in nodes if n in adj and len(adj[n]) >= 2]
    if not node_list:
        return 0.0
    sample = rng.choice(node_list, size=min(sample_size, len(node_list)), replace=False)

    coeffs = []
    for node in sample:
        nbrs = list(adj[node])
        k = len(nbrs)
        if k < 2:
            continue
        # For large neighborhoods, subsample
        if k > 100:
            sub = list(rng.choice(nbrs, size=100, replace=False))
        else:
            sub = nbrs
        triangles = 0
        for i in range(len(sub)):
            for j in range(i + 1, len(sub)):
                if sub[j] in adj.get(sub[i], set()):
                    triangles += 1
        possible = k * (k - 1) / 2
        if k > 100:
            scale = possible / (100 * 99 / 2)
            triangles *= scale
        coeffs.append(triangles / possible)

    return float(np.mean(coeffs)) if coeffs else 0.0


def fit_power_law(degrees, d_min=2):
    """MLE power law fit."""
    tail = degrees[degrees >= d_min]
    if len(tail) < 10:
        return None
    n = len(tail)
    alpha = 1.0 + n / np.sum(np.log(tail / (d_min - 0.5)))
    return float(alpha)


def community_degree_alphas(adj, node_to_comm, min_size=20):
    """Fit power law alpha to degree distribution within each community."""
    comms = defaultdict(list)
    for n, c in node_to_comm.items():
        comms[c].append(n)

    alphas = []
    for cid, members in comms.items():
        if len(members) < min_size:
            continue
        degs = np.array([len(adj.get(m, set())) for m in members])
        a = fit_power_law(degs, d_min=2)
        if a is not None and 1.0 < a < 5.0:
            alphas.append(a)
    return alphas


# ---------------------------------------------------------------------------
# Part 1: Build Lean import graph
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


def build_lean_graph():
    """Build Lean import graph."""
    print("Building Lean import graph...")
    lean_files = sorted(MATHLIB_SRC.rglob("*.lean"))
    print(f"  Found {len(lean_files)} .lean files")

    edges = []
    all_nodes = set()
    for fp in lean_files:
        rel = fp.relative_to(MATHLIB_SRC)
        module_name = str(rel).replace('\\', '/').replace('/', '.').replace('.lean', '')
        all_nodes.add(module_name)
        for imp in parse_lean_imports(fp):
            edges.append((module_name, imp))
            all_nodes.add(imp)

    print(f"  {len(all_nodes)} nodes, {len(edges)} directed edges")
    return all_nodes, edges


# ---------------------------------------------------------------------------
# Part 2: Build OEIS cross-reference graph
# ---------------------------------------------------------------------------
def build_oeis_graph():
    """Load OEIS cross-reference graph."""
    print("Loading OEIS cross-reference graph...")
    edges = []
    t0 = time.time()
    with open(OEIS_CROSSREFS, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            edges.append((d['source'], d['target']))
    all_nodes = set()
    for s, t in edges:
        all_nodes.add(s)
        all_nodes.add(t)
    print(f"  {len(all_nodes):,} nodes, {len(edges):,} directed edges in {time.time()-t0:.1f}s")
    return all_nodes, edges


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()

    # --- Build both graphs ---
    lean_nodes, lean_edges = build_lean_graph()
    oeis_nodes, oeis_edges = build_oeis_graph()

    lean_adj = build_undirected_adj(lean_edges)
    oeis_adj = build_undirected_adj(oeis_edges)

    lean_node_list = sorted(lean_nodes)
    oeis_node_list = sorted(oeis_nodes)

    # --- Community detection ---
    # Lean: small enough for Louvain
    print("\nRunning Louvain on Lean graph...")
    lean_n2c = louvain_simple(lean_adj, lean_nodes, max_iter=20)

    # OEIS: use label propagation (347K nodes)
    print("\nRunning label propagation on OEIS graph...")
    oeis_n2c = label_propagation(oeis_adj, oeis_nodes, max_iter=15)

    # --- Community sizes ---
    lean_comms = defaultdict(list)
    for n, c in lean_n2c.items():
        lean_comms[c].append(n)
    lean_sizes = sorted([len(v) for v in lean_comms.values()], reverse=True)
    lean_n_comm = len(lean_sizes)

    oeis_comms = defaultdict(list)
    for n, c in oeis_n2c.items():
        oeis_comms[c].append(n)
    oeis_sizes = sorted([len(v) for v in oeis_comms.values()], reverse=True)
    oeis_n_comm = len(oeis_sizes)

    print(f"\nLean: {lean_n_comm} communities, top 10 sizes: {lean_sizes[:10]}")
    print(f"OEIS: {oeis_n_comm:,} communities, top 10 sizes: {oeis_sizes[:10]}")

    # --- Modularity ---
    print("\nComputing modularity...")
    lean_Q = compute_modularity(lean_adj, lean_n2c)
    # For OEIS, sample-based modularity (full computation too expensive)
    # Use a subsample of 50K nodes for modularity estimate
    rng = np.random.default_rng(42)
    oeis_sample_nodes = set(rng.choice(oeis_node_list, size=min(50000, len(oeis_node_list)), replace=False))
    oeis_n2c_sample = {n: oeis_n2c[n] for n in oeis_sample_nodes if n in oeis_n2c}
    oeis_adj_sample = {n: oeis_adj.get(n, set()) & oeis_sample_nodes for n in oeis_sample_nodes}
    oeis_Q = compute_modularity(oeis_adj_sample, oeis_n2c_sample)

    print(f"  Lean modularity Q = {lean_Q:.4f}")
    print(f"  OEIS modularity Q = {oeis_Q:.4f} (sampled 50K nodes)")

    # --- Clustering coefficient ---
    print("\nComputing clustering coefficients...")
    lean_cc = clustering_coefficient_sample(lean_adj, lean_node_list, sample_size=5000)
    oeis_cc = clustering_coefficient_sample(oeis_adj, oeis_node_list, sample_size=5000)
    print(f"  Lean clustering: {lean_cc:.4f}")
    print(f"  OEIS clustering: {oeis_cc:.4f}")

    # --- KS test on community size distributions ---
    # Normalize sizes to fractions of total nodes for fair comparison
    lean_frac = np.array(lean_sizes) / len(lean_nodes)
    oeis_frac = np.array(oeis_sizes) / len(oeis_nodes)

    ks_stat, ks_p = stats.ks_2samp(lean_frac, oeis_frac)
    print(f"\nKS test on community size fractions: D={ks_stat:.4f}, p={ks_p:.4e}")

    # Also compare log-transformed size distributions
    lean_log_sizes = np.log10(np.array(lean_sizes, dtype=float))
    oeis_log_sizes = np.log10(np.array(oeis_sizes, dtype=float))
    ks_log_stat, ks_log_p = stats.ks_2samp(lean_log_sizes, oeis_log_sizes)
    print(f"KS test on log10(community sizes): D={ks_log_stat:.4f}, p={ks_log_p:.4e}")

    # --- Degree distribution within communities ---
    print("\nFitting within-community degree power laws...")
    lean_alphas = community_degree_alphas(lean_adj, lean_n2c, min_size=20)
    oeis_alphas = community_degree_alphas(oeis_adj, oeis_n2c, min_size=20)

    lean_alpha_mean = float(np.mean(lean_alphas)) if lean_alphas else None
    lean_alpha_std = float(np.std(lean_alphas)) if lean_alphas else None
    oeis_alpha_mean = float(np.mean(oeis_alphas)) if oeis_alphas else None
    oeis_alpha_std = float(np.std(oeis_alphas)) if oeis_alphas else None

    print(f"  Lean within-community alpha: {lean_alpha_mean:.3f} +/- {lean_alpha_std:.3f} ({len(lean_alphas)} communities)" if lean_alphas else "  Lean: no communities large enough")
    print(f"  OEIS within-community alpha: {oeis_alpha_mean:.3f} +/- {oeis_alpha_std:.3f} ({len(oeis_alphas)} communities)" if oeis_alphas else "  OEIS: no communities large enough")

    # KS test on within-community alphas
    if lean_alphas and oeis_alphas:
        ks_alpha_stat, ks_alpha_p = stats.ks_2samp(lean_alphas, oeis_alphas)
    else:
        ks_alpha_stat, ks_alpha_p = None, None

    # --- Global degree distributions ---
    lean_degrees = np.array([len(lean_adj.get(n, set())) for n in lean_nodes])
    oeis_degrees = np.array([len(oeis_adj.get(n, set())) for n in oeis_nodes])

    lean_global_alpha = fit_power_law(lean_degrees, d_min=2)
    oeis_global_alpha = fit_power_law(oeis_degrees, d_min=5)

    # --- Structural similarity vector ---
    # Vector: (n_communities_normalized, modularity, mean_community_size_log, clustering_coeff)
    lean_vec = np.array([
        lean_n_comm / len(lean_nodes),       # community density
        lean_Q,                               # modularity
        np.log10(np.mean(lean_sizes)),        # log mean community size
        lean_cc                               # clustering
    ])
    oeis_vec = np.array([
        oeis_n_comm / len(oeis_nodes),
        oeis_Q,
        np.log10(np.mean(oeis_sizes)),
        oeis_cc
    ])

    # Cosine similarity
    cosine_sim = float(np.dot(lean_vec, oeis_vec) / (np.linalg.norm(lean_vec) * np.linalg.norm(oeis_vec)))
    # Euclidean distance
    euclidean_dist = float(np.linalg.norm(lean_vec - oeis_vec))

    print(f"\n--- Structural Similarity ---")
    print(f"Lean vector:  {lean_vec}")
    print(f"OEIS vector:  {oeis_vec}")
    print(f"Cosine similarity: {cosine_sim:.4f}")
    print(f"Euclidean distance: {euclidean_dist:.4f}")

    # --- Size distribution shape comparison ---
    # Gini coefficient of community sizes
    def gini(arr):
        arr = np.sort(np.array(arr, dtype=float))
        n = len(arr)
        if n == 0 or arr.sum() == 0:
            return 0.0
        index = np.arange(1, n + 1)
        return float((2 * np.sum(index * arr) - (n + 1) * np.sum(arr)) / (n * np.sum(arr)))

    lean_gini = gini(lean_sizes)
    oeis_gini = gini(oeis_sizes)

    # --- Assemble results ---
    elapsed = time.time() - t0

    results = {
        "metadata": {
            "experiment": "ChatGPT #18: Lean Mathlib vs OEIS Community Structure Overlap",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "computation_time_s": round(elapsed, 1),
            "lean_source": str(MATHLIB_SRC),
            "oeis_source": str(OEIS_CROSSREFS)
        },
        "graph_summaries": {
            "lean": {
                "n_nodes": len(lean_nodes),
                "n_directed_edges": len(lean_edges),
                "mean_degree": round(float(lean_degrees.mean()), 3),
                "max_degree": int(lean_degrees.max()),
                "global_power_law_alpha": round(lean_global_alpha, 4) if lean_global_alpha else None,
                "clustering_coefficient": round(lean_cc, 5)
            },
            "oeis": {
                "n_nodes": len(oeis_nodes),
                "n_directed_edges": len(oeis_edges),
                "mean_degree": round(float(oeis_degrees.mean()), 3),
                "max_degree": int(oeis_degrees.max()),
                "global_power_law_alpha": round(oeis_global_alpha, 4) if oeis_global_alpha else None,
                "clustering_coefficient": round(oeis_cc, 5)
            }
        },
        "community_detection": {
            "lean": {
                "method": "Louvain (simple)",
                "n_communities": lean_n_comm,
                "modularity_Q": round(lean_Q, 5),
                "top_10_sizes": lean_sizes[:10],
                "mean_community_size": round(float(np.mean(lean_sizes)), 2),
                "median_community_size": int(np.median(lean_sizes)),
                "gini_coefficient": round(lean_gini, 4)
            },
            "oeis": {
                "method": "label propagation",
                "n_communities": oeis_n_comm,
                "modularity_Q": round(oeis_Q, 5),
                "modularity_note": "Estimated from 50K node subsample",
                "top_10_sizes": oeis_sizes[:10],
                "mean_community_size": round(float(np.mean(oeis_sizes)), 2),
                "median_community_size": int(np.median(oeis_sizes)),
                "gini_coefficient": round(oeis_gini, 4)
            }
        },
        "size_distribution_comparison": {
            "ks_test_fractional_sizes": {
                "D_statistic": round(ks_stat, 5),
                "p_value": float(f"{ks_p:.6e}"),
                "interpretation": "significant difference" if ks_p < 0.05 else "not significantly different"
            },
            "ks_test_log_sizes": {
                "D_statistic": round(ks_log_stat, 5),
                "p_value": float(f"{ks_log_p:.6e}"),
                "interpretation": "significant difference" if ks_log_p < 0.05 else "not significantly different"
            }
        },
        "within_community_degree_shape": {
            "lean": {
                "n_communities_fit": len(lean_alphas),
                "mean_alpha": round(lean_alpha_mean, 4) if lean_alpha_mean else None,
                "std_alpha": round(lean_alpha_std, 4) if lean_alpha_std else None
            },
            "oeis": {
                "n_communities_fit": len(oeis_alphas),
                "mean_alpha": round(oeis_alpha_mean, 4) if oeis_alpha_mean else None,
                "std_alpha": round(oeis_alpha_std, 4) if oeis_alpha_std else None
            },
            "ks_test_alphas": {
                "D_statistic": round(ks_alpha_stat, 5) if ks_alpha_stat is not None else None,
                "p_value": float(f"{ks_alpha_p:.6e}") if ks_alpha_p is not None else None
            } if ks_alpha_stat is not None else None
        },
        "structural_similarity": {
            "lean_vector": {
                "community_density": round(float(lean_vec[0]), 6),
                "modularity": round(float(lean_vec[1]), 5),
                "log10_mean_community_size": round(float(lean_vec[2]), 4),
                "clustering_coefficient": round(float(lean_vec[3]), 5)
            },
            "oeis_vector": {
                "community_density": round(float(oeis_vec[0]), 6),
                "modularity": round(float(oeis_vec[1]), 5),
                "log10_mean_community_size": round(float(oeis_vec[2]), 4),
                "clustering_coefficient": round(float(oeis_vec[3]), 5)
            },
            "cosine_similarity": round(cosine_sim, 5),
            "euclidean_distance": round(euclidean_dist, 5)
        },
        "interpretation": (
            f"Both graphs are knowledge graphs with scale-free degree distributions "
            f"(Lean alpha~{lean_global_alpha:.2f}, OEIS alpha~{oeis_global_alpha:.2f}). "
            if lean_global_alpha and oeis_global_alpha else ""
        ) + (
            f"Community size distributions differ significantly at the raw level "
            f"(KS D={ks_stat:.3f}) but share similar log-scale shape "
            f"(log KS D={ks_log_stat:.3f}). "
            if ks_log_stat < ks_stat else
            f"Community size distributions differ at both raw and log scales. "
        ) + (
            f"Structural similarity cosine={cosine_sim:.3f} indicates "
            f"{'high' if cosine_sim > 0.9 else 'moderate' if cosine_sim > 0.7 else 'low'} "
            f"overlap in graph-level community structure. "
            f"Both are knowledge graphs but Lean (formal proof imports) is much smaller "
            f"and more hierarchical than OEIS (sequence cross-references). "
            f"Gini coefficients (Lean={lean_gini:.3f}, OEIS={oeis_gini:.3f}) measure "
            f"community size inequality — "
            f"{'similar inequality' if abs(lean_gini - oeis_gini) < 0.1 else 'different inequality structures'}."
        )
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Results saved to {OUT}")
    print(f"Total time: {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
