#!/usr/bin/env python3
"""
L-function Ollivier-Ricci Curvature on Isogeny Class Similarity Graph
======================================================================

Build a graph where nodes = EC isogeny classes, edges connect classes with
high mod-5 fingerprint similarity (top 1% by Hamming distance).

Compute discrete Ollivier-Ricci curvature (ORC) on each edge:
    ORC(u,v) = 1 - W_1(mu_u, mu_v) / d(u,v)
where mu_u = uniform on neighbors of u, W_1 = Wasserstein-1, d = shortest path.

Stratify by analytic rank to detect phase transitions at rank boundaries.
"""

import json
import time
import random
import numpy as np
import duckdb
import networkx as nx
from scipy.optimize import linprog
from scipy.spatial.distance import hamming
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = SCRIPT_DIR / "lfunction_ricci_results.json"

N_SAMPLE = 2000
MOD_P = 5
TOP_PERCENTILE = 0.01  # top 1% edges by similarity


def load_isogeny_classes(n_sample=N_SAMPLE):
    """Load one representative per isogeny class, sample n_sample."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    # Pick one curve per isogeny class (the first by object_id)
    query = """
        WITH ranked AS (
            SELECT lmfdb_iso, aplist, analytic_rank, conductor, rank,
                   ROW_NUMBER() OVER (PARTITION BY lmfdb_iso ORDER BY object_id) as rn
            FROM elliptic_curves
            WHERE aplist IS NOT NULL AND analytic_rank IS NOT NULL
        )
        SELECT lmfdb_iso, aplist, analytic_rank, conductor, rank
        FROM ranked WHERE rn = 1
    """
    rows = con.execute(query).fetchall()
    con.close()

    random.seed(42)
    if len(rows) > n_sample:
        # Stratified sampling to preserve rank distribution
        by_rank = defaultdict(list)
        for r in rows:
            by_rank[r[2]].append(r)

        total = len(rows)
        sampled = []
        for rank, items in sorted(by_rank.items()):
            k = max(1, int(n_sample * len(items) / total))
            k = min(k, len(items))
            sampled.extend(random.sample(items, k))

        # Fill remaining slots
        remaining = n_sample - len(sampled)
        sampled_set = set(r[0] for r in sampled)
        leftover = [r for r in rows if r[0] not in sampled_set]
        if remaining > 0 and leftover:
            sampled.extend(random.sample(leftover, min(remaining, len(leftover))))

        rows = sampled[:n_sample]

    print(f"Loaded {len(rows)} isogeny classes")
    rank_counts = defaultdict(int)
    for r in rows:
        rank_counts[r[2]] += 1
    print(f"Rank distribution: {dict(sorted(rank_counts.items()))}")

    return rows


def compute_mod_fingerprints(rows, p=MOD_P):
    """Compute mod-p fingerprint for each isogeny class's aplist."""
    fingerprints = {}
    for iso, aplist, arank, cond, rank in rows:
        fp = tuple(a % p for a in aplist)
        fingerprints[iso] = {
            "fingerprint": fp,
            "analytic_rank": arank,
            "conductor": cond,
            "rank": rank,
        }
    return fingerprints


def build_similarity_graph(fingerprints, top_pct=TOP_PERCENTILE):
    """Build graph with edges for top_pct most similar pairs by Hamming distance."""
    isos = list(fingerprints.keys())
    n = len(isos)
    fp_len = len(next(iter(fingerprints.values()))["fingerprint"])

    # Compute all pairwise Hamming distances
    print(f"Computing pairwise Hamming distances for {n} nodes...")
    fps = np.array([fingerprints[iso]["fingerprint"] for iso in isos])

    # Hamming distance: fraction of positions that differ
    # For mod-5 fingerprints of length 25, hamming distance is count_differ/25
    t0 = time.time()
    distances = []
    for i in range(n):
        for j in range(i + 1, n):
            d = np.sum(fps[i] != fps[j]) / fp_len
            distances.append((i, j, d))

    distances.sort(key=lambda x: x[2])
    print(f"Computed {len(distances)} pairwise distances in {time.time()-t0:.1f}s")

    # Take top 1% (lowest Hamming distance = most similar)
    n_edges = max(1, int(len(distances) * top_pct))
    top_edges = distances[:n_edges]

    print(f"Top {top_pct*100}% = {n_edges} edges")
    if top_edges:
        print(f"Hamming distance range: [{top_edges[0][2]:.4f}, {top_edges[-1][2]:.4f}]")

    G = nx.Graph()
    for iso in isos:
        G.add_node(iso, **fingerprints[iso])

    for i, j, d in top_edges:
        # Edge weight = Hamming distance (lower = more similar)
        G.add_edge(isos[i], isos[j], hamming_dist=d)

    # Remove isolated nodes for curvature computation
    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges "
          f"({len(isolates)} isolated nodes removed)")

    return G


def wasserstein_1(mu_u, mu_v, dist_matrix, nodes_u, nodes_v, all_nodes):
    """
    Compute Wasserstein-1 distance between two discrete distributions.
    mu_u: dict node->weight for distribution at u
    mu_v: dict node->weight for distribution at v
    dist_matrix: dict of shortest path distances
    """
    # Collect all support nodes
    support = sorted(set(list(mu_u.keys()) + list(mu_v.keys())))
    n = len(support)
    if n == 0:
        return 0.0

    # Build cost matrix
    C = np.zeros((n, n))
    for i, s in enumerate(support):
        for j, t in enumerate(support):
            if s == t:
                C[i, j] = 0
            else:
                C[i, j] = dist_matrix.get((s, t), dist_matrix.get((t, s), float("inf")))

    # Supply and demand vectors
    supply = np.array([mu_u.get(s, 0.0) for s in support])
    demand = np.array([mu_v.get(s, 0.0) for s in support])

    # Solve transport problem as LP
    # Variables: x_{ij} for i in supply, j in demand
    # min sum C_{ij} x_{ij}
    # s.t. sum_j x_{ij} = supply[i], sum_i x_{ij} = demand[j], x >= 0
    nn = n * n
    c = C.flatten()

    # Equality constraints
    A_eq = np.zeros((2 * n, nn))
    b_eq = np.zeros(2 * n)

    # Row sums = supply
    for i in range(n):
        for j in range(n):
            A_eq[i, i * n + j] = 1.0
        b_eq[i] = supply[i]

    # Column sums = demand
    for j in range(n):
        for i in range(n):
            A_eq[n + j, i * n + j] = 1.0
        b_eq[n + j] = demand[j]

    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if result.success:
        return result.fun
    else:
        return float("nan")


def compute_ollivier_ricci(G, sample_edges=None):
    """
    Compute Ollivier-Ricci curvature for edges of G.
    ORC(u,v) = 1 - W_1(mu_u, mu_v) / d(u,v)
    where mu_u = uniform on N(u), d = shortest path distance.
    """
    # Precompute shortest path distances (only within connected components)
    print("Computing shortest path distances...")
    t0 = time.time()

    # Work on largest connected component if graph is disconnected
    components = list(nx.connected_components(G))
    print(f"Connected components: {len(components)}")
    sizes = sorted([len(c) for c in components], reverse=True)[:5]
    print(f"Largest component sizes: {sizes}")

    # Compute shortest paths per component
    sp_dict = {}
    for comp in components:
        if len(comp) < 2:
            continue
        subg = G.subgraph(comp)
        sp = dict(nx.all_pairs_shortest_path_length(subg))
        for u in sp:
            for v in sp[u]:
                sp_dict[(u, v)] = sp[u][v]

    print(f"Shortest paths computed in {time.time()-t0:.1f}s")

    edges = list(G.edges())
    if sample_edges and len(edges) > sample_edges:
        random.seed(123)
        edges = random.sample(edges, sample_edges)

    print(f"Computing ORC for {len(edges)} edges...")
    t0 = time.time()

    orc = {}
    for idx, (u, v) in enumerate(edges):
        d_uv = sp_dict.get((u, v), None)
        if d_uv is None or d_uv == 0:
            continue

        # mu_u = uniform on N(u)
        neighbors_u = list(G.neighbors(u))
        neighbors_v = list(G.neighbors(v))

        if len(neighbors_u) == 0 or len(neighbors_v) == 0:
            continue

        mu_u = {n: 1.0 / len(neighbors_u) for n in neighbors_u}
        mu_v = {n: 1.0 / len(neighbors_v) for n in neighbors_v}

        w1 = wasserstein_1(mu_u, mu_v, sp_dict, neighbors_u, neighbors_v, None)
        if np.isnan(w1):
            continue

        orc[(u, v)] = 1.0 - w1 / d_uv

        if (idx + 1) % 500 == 0:
            print(f"  {idx+1}/{len(edges)} edges done...")

    print(f"ORC computed for {len(orc)} edges in {time.time()-t0:.1f}s")
    return orc


def stratify_by_rank(G, orc):
    """Stratify ORC by analytic rank of endpoints."""
    strata = defaultdict(list)

    for (u, v), curv in orc.items():
        r_u = G.nodes[u]["analytic_rank"]
        r_v = G.nodes[v]["analytic_rank"]
        key = tuple(sorted([r_u, r_v]))
        strata[key].append(curv)

    results = {}
    for key, values in sorted(strata.items()):
        arr = np.array(values)
        label = f"rank_{key[0]}_to_{key[1]}"
        results[label] = {
            "n_edges": len(values),
            "mean_orc": float(np.mean(arr)),
            "median_orc": float(np.median(arr)),
            "std_orc": float(np.std(arr)),
            "min_orc": float(np.min(arr)),
            "max_orc": float(np.max(arr)),
            "pct_positive": float(np.mean(arr > 0) * 100),
            "pct_negative": float(np.mean(arr < 0) * 100),
        }
        print(f"  {label}: n={len(values)}, mean={np.mean(arr):.4f}, "
              f"median={np.median(arr):.4f}, std={np.std(arr):.4f}")

    return results


def analyze_phase_transition(G, orc):
    """Check for sharp curvature change at rank boundaries."""
    # Compare within-rank vs cross-rank curvature
    within = []   # both endpoints same rank
    cross = []    # endpoints differ in rank
    cross_01 = [] # specifically rank 0 to rank 1

    for (u, v), curv in orc.items():
        r_u = G.nodes[u]["analytic_rank"]
        r_v = G.nodes[v]["analytic_rank"]
        if r_u == r_v:
            within.append(curv)
        else:
            cross.append(curv)
            if set([r_u, r_v]) == {0, 1}:
                cross_01.append(curv)

    within = np.array(within) if within else np.array([0.0])
    cross = np.array(cross) if cross else np.array([0.0])
    cross_01 = np.array(cross_01) if cross_01 else np.array([0.0])

    # Welch's t-test
    from scipy.stats import ttest_ind, mannwhitneyu

    results = {
        "within_rank": {
            "n": len(within),
            "mean": float(np.mean(within)),
            "std": float(np.std(within)),
        },
        "cross_rank": {
            "n": len(cross),
            "mean": float(np.mean(cross)),
            "std": float(np.std(cross)),
        },
        "cross_rank_0_to_1": {
            "n": len(cross_01),
            "mean": float(np.mean(cross_01)),
            "std": float(np.std(cross_01)),
        },
        "curvature_gap": float(np.mean(within) - np.mean(cross)),
    }

    if len(within) > 1 and len(cross) > 1:
        t_stat, p_val = ttest_ind(within, cross, equal_var=False)
        results["welch_t_stat"] = float(t_stat)
        results["welch_p_value"] = float(p_val)
        try:
            u_stat, u_pval = mannwhitneyu(within, cross, alternative="two-sided")
            results["mannwhitney_u"] = float(u_stat)
            results["mannwhitney_p"] = float(u_pval)
        except ValueError:
            pass

    return results


def main():
    print("=" * 70)
    print("L-function Ollivier-Ricci Curvature Analysis")
    print("=" * 70)

    # Step 1: Load data
    print("\n[1/5] Loading isogeny classes...")
    rows = load_isogeny_classes()

    # Step 2: Compute mod-p fingerprints
    print(f"\n[2/5] Computing mod-{MOD_P} fingerprints...")
    fingerprints = compute_mod_fingerprints(rows)

    # Step 3: Build similarity graph
    print("\n[3/5] Building similarity graph (top 1% by Hamming distance)...")
    G = build_similarity_graph(fingerprints)

    # Step 4: Compute Ollivier-Ricci curvature
    print("\n[4/5] Computing Ollivier-Ricci curvature...")
    orc = compute_ollivier_ricci(G)

    # Step 5: Stratify and analyze
    print("\n[5/5] Stratifying by analytic rank...")
    print("\nORC by rank stratum:")
    strata = stratify_by_rank(G, orc)

    print("\nPhase transition analysis:")
    phase = analyze_phase_transition(G, orc)
    print(f"  Within-rank mean ORC: {phase['within_rank']['mean']:.4f} (n={phase['within_rank']['n']})")
    print(f"  Cross-rank mean ORC:  {phase['cross_rank']['mean']:.4f} (n={phase['cross_rank']['n']})")
    print(f"  Curvature gap:        {phase['curvature_gap']:.4f}")
    if "welch_p_value" in phase:
        print(f"  Welch t-test p-value: {phase['welch_p_value']:.2e}")

    # Global summary
    all_orc = list(orc.values())
    all_arr = np.array(all_orc)
    global_stats = {
        "n_edges_with_orc": len(all_orc),
        "mean_orc": float(np.mean(all_arr)),
        "median_orc": float(np.median(all_arr)),
        "std_orc": float(np.std(all_arr)),
        "pct_positive": float(np.mean(all_arr > 0) * 100),
        "pct_negative": float(np.mean(all_arr < 0) * 100),
        "pct_zero": float(np.mean(all_arr == 0) * 100),
    }

    # Degree distribution
    degrees = [d for _, d in G.degree()]
    degree_stats = {
        "mean_degree": float(np.mean(degrees)),
        "median_degree": float(np.median(degrees)),
        "max_degree": int(np.max(degrees)),
        "min_degree": int(np.min(degrees)),
    }

    # Node rank distribution in graph
    node_ranks = defaultdict(int)
    for n in G.nodes():
        node_ranks[G.nodes[n]["analytic_rank"]] += 1

    # Assemble results
    results = {
        "metadata": {
            "script": "lfunction_ricci.py",
            "description": "Ollivier-Ricci curvature on EC isogeny class mod-5 fingerprint similarity graph",
            "n_sampled": len(rows),
            "mod_p": MOD_P,
            "top_percentile": TOP_PERCENTILE,
            "n_nodes_in_graph": G.number_of_nodes(),
            "n_edges_in_graph": G.number_of_edges(),
            "n_connected_components": nx.number_connected_components(G),
        },
        "degree_distribution": degree_stats,
        "node_rank_distribution": {str(k): v for k, v in sorted(node_ranks.items())},
        "global_orc": global_stats,
        "orc_by_rank_stratum": strata,
        "phase_transition": phase,
        "interpretation": {},
    }

    # Interpretation
    mean_orc = global_stats["mean_orc"]
    if mean_orc > 0.05:
        geom = "positively curved (clustered)"
    elif mean_orc < -0.05:
        geom = "negatively curved (spread out / tree-like)"
    else:
        geom = "approximately flat"

    results["interpretation"]["global_geometry"] = geom

    gap = phase["curvature_gap"]
    p_val = phase.get("welch_p_value", 1.0)
    if p_val < 0.01 and abs(gap) > 0.05:
        results["interpretation"]["phase_transition"] = (
            f"YES: significant curvature gap = {gap:.4f} (p={p_val:.2e}). "
            f"Within-rank edges are {'more clustered' if gap > 0 else 'more spread'} "
            f"than cross-rank edges."
        )
    elif p_val < 0.05:
        results["interpretation"]["phase_transition"] = (
            f"MARGINAL: curvature gap = {gap:.4f} (p={p_val:.2e}). "
            f"Suggestive but not conclusive."
        )
    else:
        results["interpretation"]["phase_transition"] = (
            f"NO: curvature gap = {gap:.4f} (p={p_val:.2e}). "
            f"No significant difference between within-rank and cross-rank curvature."
        )

    # Rank monotonicity check
    rank_means = {}
    for label, data in strata.items():
        rank_means[label] = data["mean_orc"]
    results["interpretation"]["rank_monotonicity"] = rank_means

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Global geometry: {geom} (mean ORC = {mean_orc:.4f})")
    print(f"Phase transition: {results['interpretation']['phase_transition']}")
    print(f"Rank curvature monotonicity: {rank_means}")

    return results


if __name__ == "__main__":
    main()
