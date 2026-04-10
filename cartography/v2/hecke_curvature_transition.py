#!/usr/bin/env python3
"""
Ollivier-Ricci Curvature Phase Transition on Mod-ell Hecke Graphs.

For each ell in {3, 5, 7, 11}:
  1. Load 17,314 dim-1 weight-2 modular forms from DuckDB
  2. Compute mod-ell fingerprint: (a_p mod ell) for first 25 primes
  3. Build k-NN graph (k=10) on fingerprint Hamming distance
  4. Compute mean Ollivier-Ricci curvature (ORC) on the k-NN graph
  5. Track curvature statistics

Outputs:
  - cartography/v2/hecke_curvature_transition_results.json
  - cartography/v2/hecke_curvature_transition.png

Compare to F4's curvature flow result (kappa*=0.73 at ell=5).
"""

import json
import os
import sys
import time
import math
import numpy as np
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────────────
ELLS = [3, 5, 7, 11]
K_NN = 10
NUM_PRIMES = 25
ORC_ALPHA = 0.5  # Laziness parameter for ORC
MAX_ORC_EDGES = 5000  # Cap for ORC computation (sampling if graph too large)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "charon", "data", "charon.duckdb")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(OUT_DIR, "hecke_curvature_transition_results.json")
PLOT_FILE = os.path.join(OUT_DIR, "hecke_curvature_transition.png")

# First 25 primes
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]


def load_forms():
    """Load all dim-1 weight-2 modular forms from DuckDB."""
    import duckdb
    con = duckdb.connect(DB_PATH, read_only=True)
    rows = con.execute("""
        SELECT level, ap_coeffs, is_cm, sato_tate_group
        FROM modular_forms
        WHERE dim = 1 AND weight = 2 AND ap_coeffs IS NOT NULL
        ORDER BY level
    """).fetchall()
    con.close()
    print(f"Loaded {len(rows)} forms from DuckDB")
    return rows


def compute_mod_ell_fingerprint(ap_coeffs_json, ell, num_primes=NUM_PRIMES):
    """Compute mod-ell fingerprint: tuple of (a_p mod ell) for first num_primes primes."""
    ap_list = json.loads(ap_coeffs_json)
    fp = []
    for i in range(min(num_primes, len(ap_list))):
        # ap_list[i] is [val] for dim-1 forms
        val = ap_list[i][0] if isinstance(ap_list[i], list) else ap_list[i]
        fp.append(int(val) % ell)
    return tuple(fp)


def hamming_distance(fp1, fp2):
    """Hamming distance between two fingerprint tuples."""
    return sum(a != b for a, b in zip(fp1, fp2))


def build_knn_graph_batched(fingerprints, k):
    """Build k-NN graph on Hamming distance using vectorized numpy operations.

    Returns a networkx graph.
    """
    import networkx as nx

    n = len(fingerprints)
    d = len(fingerprints[0])

    # Convert fingerprints to numpy array for vectorized Hamming distance
    fp_array = np.array(fingerprints, dtype=np.int16)

    print(f"  Building k-NN graph: n={n}, d={d}, k={k}")

    G = nx.Graph()
    G.add_nodes_from(range(n))

    # Process in batches to avoid memory explosion
    batch_size = 500
    edge_count = 0

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        # Compute Hamming distances from batch to all nodes
        # Shape: (batch_size, n, d) -> compare -> sum -> (batch_size, n)
        batch = fp_array[start:end]  # (batch_size, d)
        # Broadcasting: (batch_size, 1, d) != (1, n, d) -> (batch_size, n, d)
        dists = np.sum(batch[:, np.newaxis, :] != fp_array[np.newaxis, :, :], axis=2)

        for i_local in range(end - start):
            i_global = start + i_local
            dist_row = dists[i_local]
            # Exclude self
            dist_row[i_global] = d + 1
            # Get k nearest neighbors
            knn_indices = np.argpartition(dist_row, k)[:k]
            for j in knn_indices:
                if not G.has_edge(i_global, int(j)):
                    G.add_edge(i_global, int(j), weight=1.0 / max(dist_row[j], 1))
                    edge_count += 1

        if (start // batch_size) % 10 == 0:
            print(f"    Batch {start//batch_size}: {edge_count} edges so far")

    print(f"  k-NN graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def ollivier_ricci_curvature_edge(G, u, v, alpha, sp_lengths):
    """Compute Ollivier-Ricci curvature for a single edge (u, v).

    Uses the lazy random walk measure:
      mu_u(x) = alpha if x == u, else (1-alpha)/deg(u) for neighbors x of u.
    Then kappa(u,v) = 1 - W1(mu_u, mu_v) / d(u,v).
    """
    import ot

    # Neighbors
    nbrs_u = list(G.neighbors(u))
    nbrs_v = list(G.neighbors(v))

    # Support = union of {u} + nbrs_u + {v} + nbrs_v
    support = list(set([u] + nbrs_u + [v] + nbrs_v))
    node_to_idx = {n: i for i, n in enumerate(support)}
    n_support = len(support)

    # Build measures mu_u, mu_v on support
    mu_u = np.zeros(n_support)
    mu_v = np.zeros(n_support)

    # mu_u: alpha on u, (1-alpha)/deg(u) on neighbors
    deg_u = len(nbrs_u)
    mu_u[node_to_idx[u]] = alpha
    for x in nbrs_u:
        mu_u[node_to_idx[x]] += (1 - alpha) / deg_u

    deg_v = len(nbrs_v)
    mu_v[node_to_idx[v]] = alpha
    for x in nbrs_v:
        mu_v[node_to_idx[x]] += (1 - alpha) / deg_v

    # Cost matrix: shortest path distances between support nodes
    cost = np.zeros((n_support, n_support))
    for i, ni in enumerate(support):
        for j, nj in enumerate(support):
            if i < j:
                if ni in sp_lengths and nj in sp_lengths[ni]:
                    d = sp_lengths[ni][nj]
                elif nj in sp_lengths and ni in sp_lengths[nj]:
                    d = sp_lengths[nj][ni]
                else:
                    d = 1e6  # disconnected
                cost[i][j] = d
                cost[j][i] = d

    # Wasserstein-1 distance
    w1 = ot.emd2(mu_u, mu_v, cost)

    # Graph distance between u and v
    d_uv = sp_lengths[u][v] if u in sp_lengths and v in sp_lengths[u] else 1.0

    kappa = 1.0 - w1 / d_uv
    return kappa


def compute_orc_sampled(G, alpha=ORC_ALPHA, max_edges=MAX_ORC_EDGES):
    """Compute Ollivier-Ricci curvature, sampling edges if graph is too large."""
    import random
    import networkx as nx

    n_edges = G.number_of_edges()
    edges = list(G.edges())

    if n_edges > max_edges:
        edges = random.sample(edges, max_edges)
        print(f"  Sampled {max_edges} edges from {n_edges} total")
    else:
        print(f"  Computing ORC on all {n_edges} edges...")

    # Collect all source nodes for BFS: edge endpoints only
    source_nodes = set()
    for u, v in edges:
        source_nodes.add(u)
        source_nodes.add(v)

    print(f"  Computing shortest paths from {len(source_nodes)} source nodes (cutoff=3)...")

    # BFS from each source node with cutoff=3 (sufficient for ORC on neighbors)
    sp_lengths = {}
    done = 0
    for node in source_nodes:
        sp_lengths[node] = nx.single_source_shortest_path_length(G, node, cutoff=3)
        done += 1
        if done % 2000 == 0:
            print(f"    BFS done for {done}/{len(source_nodes)} nodes")

    # Compute ORC for each edge
    curvatures = []
    for idx, (u, v) in enumerate(edges):
        kappa = ollivier_ricci_curvature_edge(G, u, v, alpha, sp_lengths)
        curvatures.append(kappa)
        if (idx + 1) % 5000 == 0:
            print(f"    ORC computed for {idx+1}/{len(edges)} edges, "
                  f"running mean={np.mean(curvatures):.4f}")

    return np.array(curvatures)


def analyze_curvature(curvatures, ell):
    """Compute statistics on curvature distribution."""
    if len(curvatures) == 0:
        return {"ell": ell, "error": "no curvatures computed"}

    c = curvatures
    stats = {
        "ell": ell,
        "n_edges_measured": len(c),
        "mean_curvature": float(np.mean(c)),
        "median_curvature": float(np.median(c)),
        "std_curvature": float(np.std(c)),
        "min_curvature": float(np.min(c)),
        "max_curvature": float(np.max(c)),
        "frac_negative": float(np.mean(c < 0)),
        "frac_positive": float(np.mean(c > 0)),
        "frac_zero": float(np.mean(c == 0)),
        "q25": float(np.percentile(c, 25)),
        "q75": float(np.percentile(c, 75)),
    }
    return stats


def compute_fingerprint_diversity(fingerprints, ell):
    """How many distinct fingerprints exist for this ell?"""
    unique = set(fingerprints)
    n = len(fingerprints)
    max_possible = ell ** NUM_PRIMES  # theoretical max (huge)
    return {
        "n_forms": n,
        "n_unique_fingerprints": len(unique),
        "diversity_ratio": len(unique) / n,
        "ell": ell,
        "fingerprint_dim": NUM_PRIMES,
    }


def make_plot(results):
    """Plot mean ORC vs ell."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ells = [r["curvature_stats"]["ell"] for r in results]
    means = [r["curvature_stats"]["mean_curvature"] for r in results]
    stds = [r["curvature_stats"]["std_curvature"] for r in results]
    frac_neg = [r["curvature_stats"]["frac_negative"] for r in results]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Panel 1: Mean ORC vs ell
    ax = axes[0]
    ax.errorbar(ells, means, yerr=stds, fmt='o-', capsize=5, linewidth=2, markersize=8, color='steelblue')
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='kappa=0 (sign change)')
    ax.axhline(y=0.73, color='orange', linestyle=':', alpha=0.7, label='F4 kappa*=0.73')
    ax.set_xlabel('ell (prime)', fontsize=12)
    ax.set_ylabel('Mean Ollivier-Ricci Curvature', fontsize=12)
    ax.set_title('ORC Phase Transition vs ell', fontsize=13)
    ax.set_xticks(ells)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 2: Fraction negative curvature vs ell
    ax = axes[1]
    ax.bar(ells, frac_neg, color='crimson', alpha=0.7, width=0.8)
    ax.set_xlabel('ell (prime)', fontsize=12)
    ax.set_ylabel('Fraction of Edges with kappa < 0', fontsize=12)
    ax.set_title('Negative Curvature Fraction', fontsize=13)
    ax.set_xticks(ells)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    # Panel 3: Fingerprint diversity
    diversities = [r["fingerprint_diversity"]["diversity_ratio"] for r in results]
    ax = axes[2]
    ax.plot(ells, diversities, 's-', color='forestgreen', markersize=8, linewidth=2)
    ax.set_xlabel('ell (prime)', fontsize=12)
    ax.set_ylabel('Diversity Ratio (unique/total)', fontsize=12)
    ax.set_title('Fingerprint Diversity', fontsize=13)
    ax.set_xticks(ells)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=150)
    print(f"Plot saved to {PLOT_FILE}")
    plt.close()


def main():
    t0 = time.time()

    # Load forms
    rows = load_forms()

    all_results = []

    for ell in ELLS:
        print(f"\n{'='*60}")
        print(f"Processing ell = {ell}")
        print(f"{'='*60}")
        t_ell = time.time()

        # Compute fingerprints
        fingerprints = []
        valid_indices = []
        for idx, (level, ap_json, is_cm, st_group) in enumerate(rows):
            fp = compute_mod_ell_fingerprint(ap_json, ell)
            if len(fp) == NUM_PRIMES:
                fingerprints.append(fp)
                valid_indices.append(idx)

        print(f"  {len(fingerprints)} valid fingerprints")

        # Fingerprint diversity
        diversity = compute_fingerprint_diversity(fingerprints, ell)
        print(f"  Unique fingerprints: {diversity['n_unique_fingerprints']} "
              f"(diversity={diversity['diversity_ratio']:.4f})")

        # Build k-NN graph
        G = build_knn_graph_batched(fingerprints, K_NN)

        # Graph topology stats
        import networkx as nx
        n_components = nx.number_connected_components(G)
        components = sorted(nx.connected_components(G), key=len, reverse=True)
        largest_cc = len(components[0]) if components else 0
        n_triangles = sum(nx.triangles(G).values()) // 3

        graph_stats = {
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "n_components": n_components,
            "largest_component": largest_cc,
            "n_triangles": n_triangles,
        }
        print(f"  Graph: {graph_stats['n_nodes']} nodes, {graph_stats['n_edges']} edges, "
              f"{n_components} components, largest={largest_cc}, triangles={n_triangles}")

        # Compute ORC
        curvatures = compute_orc_sampled(G, alpha=ORC_ALPHA)
        curv_stats = analyze_curvature(curvatures, ell)

        print(f"  Mean ORC = {curv_stats['mean_curvature']:.6f}")
        print(f"  Frac negative = {curv_stats['frac_negative']:.4f}")
        print(f"  Frac positive = {curv_stats['frac_positive']:.4f}")

        elapsed = time.time() - t_ell
        print(f"  Elapsed: {elapsed:.1f}s")

        result = {
            "ell": ell,
            "curvature_stats": curv_stats,
            "graph_stats": graph_stats,
            "fingerprint_diversity": diversity,
            "elapsed_s": round(elapsed, 2),
        }
        all_results.append(result)

    # Phase transition analysis
    means = [r["curvature_stats"]["mean_curvature"] for r in all_results]
    ells_arr = np.array(ELLS, dtype=float)
    means_arr = np.array(means)

    # Check for sign change
    sign_changes = []
    for i in range(len(means) - 1):
        if means[i] * means[i+1] < 0:
            # Linear interpolation to find crossing
            ell_cross = ELLS[i] + (ELLS[i+1] - ELLS[i]) * abs(means[i]) / (abs(means[i]) + abs(means[i+1]))
            sign_changes.append({
                "between_ells": [ELLS[i], ELLS[i+1]],
                "interpolated_ell": round(ell_cross, 3),
            })

    # Maximum curvature gradient (steepest change)
    gradients = []
    for i in range(len(means) - 1):
        delta_kappa = means[i+1] - means[i]
        delta_ell = ELLS[i+1] - ELLS[i]
        gradients.append({
            "ell_interval": [ELLS[i], ELLS[i+1]],
            "d_kappa_d_ell": round(delta_kappa / delta_ell, 6),
        })

    # Comparison to F4
    f4_kappa = 0.73
    f4_ell = 5
    ell5_result = next((r for r in all_results if r["ell"] == 5), None)
    f4_comparison = {
        "f4_kappa_star": f4_kappa,
        "f4_ell": f4_ell,
        "our_kappa_at_ell5": ell5_result["curvature_stats"]["mean_curvature"] if ell5_result else None,
        "ratio": (ell5_result["curvature_stats"]["mean_curvature"] / f4_kappa) if ell5_result else None,
    }

    total_elapsed = time.time() - t0

    summary = {
        "problem": "Frontier2 #2: Ollivier-Ricci Curvature Phase Transition on Mod-ell Hecke Graphs",
        "parameters": {
            "ells": ELLS,
            "k_nn": K_NN,
            "num_primes": NUM_PRIMES,
            "orc_alpha": ORC_ALPHA,
            "max_orc_edges": MAX_ORC_EDGES,
        },
        "per_ell_results": all_results,
        "phase_transition_analysis": {
            "sign_changes": sign_changes,
            "curvature_gradients": gradients,
            "has_phase_transition": len(sign_changes) > 0,
            "critical_ell": sign_changes[0]["interpolated_ell"] if sign_changes else None,
        },
        "f4_comparison": f4_comparison,
        "total_elapsed_s": round(total_elapsed, 2),
    }

    # Save results
    with open(RESULTS_FILE, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")

    # Plot
    make_plot(all_results)

    # Final summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in all_results:
        cs = r["curvature_stats"]
        print(f"  ell={cs['ell']:2d}: mean_kappa={cs['mean_curvature']:+.6f}  "
              f"frac_neg={cs['frac_negative']:.3f}  frac_pos={cs['frac_positive']:.3f}")

    if sign_changes:
        print(f"\n  PHASE TRANSITION DETECTED!")
        for sc in sign_changes:
            print(f"    Sign change between ell={sc['between_ells'][0]} and ell={sc['between_ells'][1]}")
            print(f"    Interpolated critical ell ~ {sc['interpolated_ell']:.2f}")
    else:
        print(f"\n  No sign change detected in [{ELLS[0]}, {ELLS[-1]}]")
        if all(m > 0 for m in means):
            print(f"  All curvatures POSITIVE (clustered geometry)")
        elif all(m < 0 for m in means):
            print(f"  All curvatures NEGATIVE (tree-like geometry)")

    print(f"\n  F4 comparison: our kappa(ell=5)={f4_comparison['our_kappa_at_ell5']:.4f} "
          f"vs F4 kappa*={f4_kappa}")
    print(f"\n  Total elapsed: {total_elapsed:.1f}s")


if __name__ == "__main__":
    main()
