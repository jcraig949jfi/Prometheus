#!/usr/bin/env python3
"""
Curvature Flow Fixed Point in Knot Polynomial Spectra (List3 #17).

1. Load knots with Jones polynomial coefficients
2. Build k-NN graph (k=10) using Hamming distance on mod-3 fingerprints of Jones coefficients
3. Apply Ollivier-Ricci curvature flow (iteratively adjust edge weights, recompute curvature)
4. Run for 50 iterations or until convergence
5. Measure: fixed-point curvature kappa*, edges destroyed, phase transition iteration
6. Compare to genus-2 Hecke kappa*=0.7295 and EC Hecke kappa_inf=-0.67

Outputs:
  - cartography/v2/knot_curvature_flow_results.json
"""

import json
import os
import sys
import time
import numpy as np

# ── Configuration ──────────────────────────────────────────────────────────
K_NN = 10
MOD_P = 3               # mod-3 fingerprints
ORC_ALPHA = 0.5          # Laziness parameter
MAX_ITERATIONS = 50
CONVERGENCE_TOL = 3e-3   # stop when sliding window spread < tol (accounts for sampling noise)
FLOW_STEP = 0.2          # curvature flow step size
EDGE_DESTROY_THRESHOLD = 1e-6  # edges below this weight are destroyed
MAX_ORC_EDGES = 5000     # sample if too many edges

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "knots", "data", "knots.json")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(OUT_DIR, "knot_curvature_flow_results.json")


def load_knots():
    """Load knots with Jones polynomial coefficients."""
    with open(DATA_PATH) as f:
        data = json.load(f)
    knots = data["knots"]
    print(f"Loaded {len(knots)} knots from {DATA_PATH}")
    return knots


def jones_mod_fingerprint(knot, mod_p=MOD_P):
    """Compute mod-p fingerprint from Jones polynomial coefficients.

    Returns tuple of (coeff mod p) for each Jones coefficient.
    """
    coeffs = knot.get("jones_coeffs")
    if not coeffs:
        jones = knot.get("jones")
        if jones and isinstance(jones, dict):
            coeffs = jones.get("coefficients", [])
    if not coeffs:
        return None
    return tuple(int(c) % mod_p for c in coeffs)


def pad_fingerprints(fps):
    """Pad all fingerprints to the same length (max length) with zeros."""
    max_len = max(len(fp) for fp in fps)
    return [fp + (0,) * (max_len - len(fp)) for fp in fps]


def build_knn_graph(fingerprints, k):
    """Build k-NN graph on Hamming distance, returning networkx graph."""
    import networkx as nx

    n = len(fingerprints)
    d = len(fingerprints[0])
    fp_array = np.array(fingerprints, dtype=np.int16)

    print(f"  Building k-NN graph: n={n}, d={d}, k={k}")

    G = nx.Graph()
    G.add_nodes_from(range(n))

    batch_size = 500
    edge_count = 0

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        batch = fp_array[start:end]
        dists = np.sum(batch[:, np.newaxis, :] != fp_array[np.newaxis, :, :], axis=2)

        for i_local in range(end - start):
            i_global = start + i_local
            dist_row = dists[i_local]
            dist_row[i_global] = d + 1  # exclude self
            knn_indices = np.argpartition(dist_row, k)[:k]
            for j in knn_indices:
                if not G.has_edge(i_global, int(j)):
                    G.add_edge(i_global, int(j), weight=1.0)
                    edge_count += 1

        if start % 2000 == 0:
            print(f"    Processed {start}/{n} nodes, {edge_count} edges")

    print(f"  k-NN graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def compute_orc_edge(G, u, v, alpha, hop_cache):
    """Compute Ollivier-Ricci curvature for edge (u, v) using optimal transport.

    Uses hop distance (unweighted) as cost matrix and edge weights for random walk measures.
    """
    import ot

    nbrs_u = list(G.neighbors(u))
    nbrs_v = list(G.neighbors(v))
    support = list(set([u] + nbrs_u + [v] + nbrs_v))
    node_to_idx = {n: i for i, n in enumerate(support)}
    n_s = len(support)

    # Lazy random walk measures (weighted by edge weights)
    mu_u = np.zeros(n_s)
    mu_v = np.zeros(n_s)

    w_u = sum(G[u][x].get("weight", 1.0) for x in nbrs_u)
    mu_u[node_to_idx[u]] = alpha
    for x in nbrs_u:
        mu_u[node_to_idx[x]] += (1 - alpha) * G[u][x].get("weight", 1.0) / max(w_u, 1e-12)

    w_v = sum(G[v][x].get("weight", 1.0) for x in nbrs_v)
    mu_v[node_to_idx[v]] = alpha
    for x in nbrs_v:
        mu_v[node_to_idx[x]] += (1 - alpha) * G[v][x].get("weight", 1.0) / max(w_v, 1e-12)

    # Cost matrix: HOP distance (unweighted), not weighted distance
    cost = np.zeros((n_s, n_s))
    for i, ni in enumerate(support):
        for j, nj in enumerate(support):
            if i < j:
                d = hop_cache.get(ni, {}).get(nj, hop_cache.get(nj, {}).get(ni, 1e6))
                cost[i][j] = d
                cost[j][i] = d

    w1 = ot.emd2(mu_u, mu_v, cost)
    # d(u,v) = 1 hop for direct edges
    kappa = 1.0 - w1
    return kappa


def compute_all_orc(G, alpha=ORC_ALPHA, max_edges=MAX_ORC_EDGES):
    """Compute ORC for all (or sampled) edges. Returns dict edge -> curvature."""
    import networkx as nx
    import random

    edges = list(G.edges())
    if len(edges) > max_edges:
        edges = random.sample(edges, max_edges)
        print(f"    Sampled {max_edges}/{G.number_of_edges()} edges for ORC")

    # BFS shortest paths (UNWEIGHTED hop distance) from edge endpoints
    source_nodes = set()
    for u, v in edges:
        source_nodes.add(u)
        source_nodes.add(v)

    hop_cache = {}
    for node in source_nodes:
        hop_cache[node] = dict(nx.single_source_shortest_path_length(G, node, cutoff=3))

    curvatures = {}
    for u, v in edges:
        kappa = compute_orc_edge(G, u, v, alpha, hop_cache)
        curvatures[(u, v)] = kappa

    return curvatures


def curvature_flow_step(G, curvatures, step_size=FLOW_STEP, destroy_threshold=EDGE_DESTROY_THRESHOLD):
    """One step of normalized Ricci flow: w_e -> w_e * (1 - step_size * kappa_e), then renormalize.

    Edges with weight below threshold are destroyed.
    Returns number of edges destroyed.
    """
    destroyed = 0
    edges_to_remove = []

    # Store total weight before update for normalization
    total_weight_before = sum(G[u][v].get("weight", 1.0) for u, v in G.edges())

    for (u, v), kappa in curvatures.items():
        if G.has_edge(u, v):
            w = G[u][v].get("weight", 1.0)
            # Ricci flow: positive curvature contracts, negative expands
            w_new = w * (1.0 - step_size * kappa)
            w_new = max(w_new, 0.0)

            if w_new < destroy_threshold:
                edges_to_remove.append((u, v))
                destroyed += 1
            else:
                G[u][v]["weight"] = w_new

    for u, v in edges_to_remove:
        G.remove_edge(u, v)

    # Normalize: preserve total edge weight to prevent divergence
    if G.number_of_edges() > 0:
        total_weight_after = sum(G[u][v].get("weight", 1.0) for u, v in G.edges())
        if total_weight_after > 1e-12:
            scale = total_weight_before / total_weight_after
            for u, v in G.edges():
                G[u][v]["weight"] *= scale

    return destroyed


def run_curvature_flow(G, max_iter=MAX_ITERATIONS, convergence_tol=CONVERGENCE_TOL):
    """Run iterative Ollivier-Ricci curvature flow until convergence or max_iter."""

    history = []
    total_destroyed = 0
    phase_transition_iter = None
    initial_edges = G.number_of_edges()
    WINDOW = 10  # sliding window for convergence (accounts for sampling noise)

    for iteration in range(1, max_iter + 1):
        t_iter = time.time()

        # Compute curvatures
        curvatures = compute_all_orc(G)

        if not curvatures:
            print(f"  Iter {iteration}: no edges remain, stopping")
            break

        kappas = np.array(list(curvatures.values()))
        mean_kappa = float(np.mean(kappas))
        std_kappa = float(np.std(kappas))
        frac_neg = float(np.mean(kappas < 0))
        frac_pos = float(np.mean(kappas > 0))

        # Apply flow step
        destroyed = curvature_flow_step(G, curvatures)
        total_destroyed += destroyed

        # Check for phase transition: first iteration where frac_neg drops below 0.1
        # or mean curvature becomes positive
        if phase_transition_iter is None and frac_neg < 0.1 and mean_kappa > 0:
            phase_transition_iter = iteration

        iter_record = {
            "iteration": iteration,
            "mean_kappa": round(mean_kappa, 6),
            "std_kappa": round(std_kappa, 6),
            "median_kappa": round(float(np.median(kappas)), 6),
            "min_kappa": round(float(np.min(kappas)), 6),
            "max_kappa": round(float(np.max(kappas)), 6),
            "frac_negative": round(frac_neg, 4),
            "frac_positive": round(frac_pos, 4),
            "edges_destroyed_this_iter": destroyed,
            "total_edges_remaining": G.number_of_edges(),
            "elapsed_s": round(time.time() - t_iter, 2),
        }
        history.append(iter_record)

        print(f"  Iter {iteration:3d}: kappa*={mean_kappa:+.6f} +/- {std_kappa:.4f}  "
              f"neg={frac_neg:.3f}  edges={G.number_of_edges()}  destroyed={destroyed}  "
              f"[{time.time()-t_iter:.1f}s]")

        # Sliding window convergence: check if last WINDOW means are within tol
        if len(history) >= WINDOW:
            recent = [h["mean_kappa"] for h in history[-WINDOW:]]
            spread = max(recent) - min(recent)
            if spread < convergence_tol:
                print(f"  Converged at iteration {iteration} "
                      f"(window spread={spread:.2e} < {convergence_tol})")
                break

    # Final kappa*: average of last WINDOW iterations for stability
    if len(history) >= WINDOW:
        final_kappa = round(float(np.mean([h["mean_kappa"] for h in history[-WINDOW:]])), 6)
    elif history:
        final_kappa = history[-1]["mean_kappa"]
    else:
        final_kappa = None

    return {
        "history": history,
        "converged_at": iteration if iteration < max_iter else None,
        "total_iterations": len(history),
        "fixed_point_kappa": final_kappa,
        "total_edges_destroyed": total_destroyed,
        "initial_edges": initial_edges,
        "final_edges": G.number_of_edges(),
        "edge_survival_fraction": G.number_of_edges() / max(initial_edges, 1),
        "phase_transition_iteration": phase_transition_iter,
    }


def main():
    t0 = time.time()

    # 1. Load knots
    knots = load_knots()

    # 2. Compute mod-3 fingerprints from Jones coefficients
    fingerprints = []
    valid_knots = []
    for knot in knots:
        fp = jones_mod_fingerprint(knot)
        if fp is not None and len(fp) >= 3:
            fingerprints.append(fp)
            valid_knots.append(knot)

    print(f"Valid knots with Jones fingerprints: {len(fingerprints)}")

    # Pad to uniform length
    fingerprints = pad_fingerprints(fingerprints)
    fp_dim = len(fingerprints[0])
    n_unique = len(set(fingerprints))
    print(f"Fingerprint dimension: {fp_dim}, unique: {n_unique}/{len(fingerprints)}")

    # 3. Build k-NN graph
    G = build_knn_graph(fingerprints, K_NN)

    import networkx as nx
    n_components = nx.number_connected_components(G)
    components = sorted(nx.connected_components(G), key=len, reverse=True)
    largest_cc = len(components[0]) if components else 0

    graph_stats = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_components": n_components,
        "largest_component": largest_cc,
    }
    print(f"Graph: {graph_stats['n_nodes']} nodes, {graph_stats['n_edges']} edges, "
          f"{n_components} components, largest={largest_cc}")

    # 4. Run curvature flow
    print(f"\nStarting Ollivier-Ricci curvature flow (max {MAX_ITERATIONS} iterations)...")
    flow_results = run_curvature_flow(G)

    # 5. Comparisons
    kappa_star = flow_results["fixed_point_kappa"]
    comparisons = {
        "genus2_hecke_kappa_star": 0.7295,
        "ec_hecke_kappa_inf": -0.67,
        "knot_jones_kappa_star": kappa_star,
        "expected_knot_kappa": 0.68,
        "delta_from_expected": round(kappa_star - 0.68, 6) if kappa_star else None,
        "delta_from_genus2": round(kappa_star - 0.7295, 6) if kappa_star else None,
        "same_sign_as_genus2": (kappa_star > 0) if kappa_star else None,
        "same_sign_as_ec": (kappa_star < 0) if kappa_star else None,
    }

    total_elapsed = time.time() - t0

    # Assemble full results
    results = {
        "problem": "List3 #17: Curvature Flow Fixed Point in Knot Polynomial Spectra",
        "parameters": {
            "k_nn": K_NN,
            "mod_p": MOD_P,
            "orc_alpha": ORC_ALPHA,
            "max_iterations": MAX_ITERATIONS,
            "convergence_tol": CONVERGENCE_TOL,
            "flow_step": FLOW_STEP,
            "edge_destroy_threshold": EDGE_DESTROY_THRESHOLD,
            "max_orc_edges_per_iter": MAX_ORC_EDGES,
        },
        "data": {
            "n_knots_loaded": len(knots),
            "n_valid_fingerprints": len(fingerprints),
            "fingerprint_dimension": fp_dim,
            "n_unique_fingerprints": n_unique,
            "diversity_ratio": round(n_unique / len(fingerprints), 4),
        },
        "initial_graph": graph_stats,
        "curvature_flow": flow_results,
        "comparisons": comparisons,
        "total_elapsed_s": round(total_elapsed, 2),
    }

    # Save
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}")

    # Final summary
    print(f"\n{'='*60}")
    print("SUMMARY: Knot Jones Polynomial Curvature Flow")
    print(f"{'='*60}")
    print(f"  Knots: {len(fingerprints)} (mod-{MOD_P} Jones fingerprints)")
    print(f"  Graph: {graph_stats['n_nodes']} nodes, {graph_stats['n_edges']} edges")
    print(f"  Flow iterations: {flow_results['total_iterations']}")
    print(f"  Converged at: {flow_results['converged_at']}")
    print(f"  Fixed-point kappa*: {kappa_star}")
    print(f"  Edges destroyed: {flow_results['total_edges_destroyed']}/{flow_results['initial_edges']}")
    print(f"  Edge survival: {flow_results['edge_survival_fraction']:.4f}")
    print(f"  Phase transition iter: {flow_results['phase_transition_iteration']}")
    print(f"\n  Comparisons:")
    print(f"    genus-2 Hecke kappa* = 0.7295")
    print(f"    EC Hecke kappa_inf   = -0.67")
    print(f"    knot Jones kappa*    = {kappa_star}")
    print(f"    expected             = 0.68")
    if kappa_star:
        print(f"    delta from expected  = {kappa_star - 0.68:+.6f}")
    print(f"\n  Total elapsed: {total_elapsed:.1f}s")


if __name__ == "__main__":
    main()
