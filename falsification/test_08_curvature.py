"""
Aletheia — Falsification Test 8
CLAIM: Arrow's impossibility and the Theorema Egregium share a curvature-based impossibility structure.
TEST: Compute Ollivier-Ricci curvature on the permutohedron graph and compare to S².

Methodology:
- Construct permutohedron graphs for n=3 and n=4
- Compute Ollivier-Ricci curvature on every edge using lazy random walk
- Lazy random walk: μ_x = (1/2)δ_x + (1/(2·deg(x))) Σ_{z~x} δ_z
- W₁ computed via linear programming (Earth Mover's Distance)
- κ(x,y) = 1 - W₁(μ_x, μ_y) / d(x,y)  where d(x,y) = 1 for edges
"""

import json
import itertools
import numpy as np
from scipy.optimize import linprog
from scipy.spatial.distance import cdist
import networkx as nx
from collections import defaultdict


def build_permutohedron(n):
    """
    Build the permutohedron graph for S_n.
    Vertices: all permutations of [1..n]
    Edges: between permutations differing by a single adjacent transposition.
    """
    perms = list(itertools.permutations(range(1, n + 1)))
    perm_to_idx = {p: i for i, p in enumerate(perms)}

    G = nx.Graph()
    for i, p in enumerate(perms):
        G.add_node(i, perm=p)

    for i, p in enumerate(perms):
        p_list = list(p)
        for k in range(n - 1):
            # Swap adjacent positions k and k+1
            q_list = p_list[:]
            q_list[k], q_list[k + 1] = q_list[k + 1], q_list[k]
            q = tuple(q_list)
            j = perm_to_idx[q]
            if not G.has_edge(i, j):
                G.add_edge(i, j)

    return G, perms


def lazy_random_walk_measure(G, node):
    """
    Lazy random walk measure at node x:
    μ_x = (1/2)δ_x + (1/(2·deg(x))) Σ_{z~x} δ_z
    Returns dict: node -> probability
    """
    neighbors = list(G.neighbors(node))
    deg = len(neighbors)
    mu = defaultdict(float)
    mu[node] = 0.5
    for z in neighbors:
        mu[z] += 0.5 / deg
    return mu


def wasserstein_1(G, mu_x, mu_y):
    """
    Compute W₁ (Earth Mover's Distance) between two measures on graph G
    using the graph shortest-path distance as ground metric.
    Solved via linear programming.
    """
    # Get all nodes that have nonzero mass in either measure
    all_nodes = sorted(set(mu_x.keys()) | set(mu_y.keys()))
    n = len(all_nodes)
    node_to_local = {v: i for i, v in enumerate(all_nodes)}

    # Supply and demand
    supply = np.array([mu_x.get(v, 0.0) for v in all_nodes])
    demand = np.array([mu_y.get(v, 0.0) for v in all_nodes])

    # Compute shortest path distances between all relevant nodes
    dist_matrix = np.zeros((n, n))
    # Use networkx shortest path lengths
    for i, u in enumerate(all_nodes):
        lengths = nx.single_source_shortest_path_length(G, u)
        for j, v in enumerate(all_nodes):
            dist_matrix[i, j] = lengths.get(v, float('inf'))

    # LP formulation for optimal transport:
    # minimize Σ_{i,j} d(i,j) * f(i,j)
    # subject to: Σ_j f(i,j) = supply[i] for all i
    #             Σ_i f(i,j) = demand[j] for all j
    #             f(i,j) >= 0

    num_vars = n * n
    # Cost vector
    c = dist_matrix.flatten()

    # Equality constraints
    # Row sums = supply: for each i, Σ_j f(i,j) = supply[i]
    # Col sums = demand: for each j, Σ_i f(i,j) = demand[j]
    A_eq = np.zeros((2 * n, num_vars))
    b_eq = np.zeros(2 * n)

    for i in range(n):
        for j in range(n):
            A_eq[i, i * n + j] = 1.0  # row sum constraint
            A_eq[n + j, i * n + j] = 1.0  # col sum constraint
        b_eq[i] = supply[i]
        b_eq[n + i] = demand[i]

    bounds = [(0, None)] * num_vars

    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    if not result.success:
        raise RuntimeError(f"LP failed: {result.message}")

    return result.fun


def compute_ollivier_ricci(G):
    """
    Compute Ollivier-Ricci curvature for every edge in G.
    κ(x,y) = 1 - W₁(μ_x, μ_y) / d(x,y)
    For edges, d(x,y) = 1.
    """
    curvatures = {}
    edges = list(G.edges())
    total = len(edges)

    for idx, (u, v) in enumerate(edges):
        mu_u = lazy_random_walk_measure(G, u)
        mu_v = lazy_random_walk_measure(G, v)
        w1 = wasserstein_1(G, mu_u, mu_v)
        kappa = 1.0 - w1  # d(u,v) = 1
        curvatures[(u, v)] = kappa

        if (idx + 1) % 10 == 0 or idx == total - 1:
            print(f"  Edge {idx+1}/{total}: kappa = {kappa:.6f}")

    return curvatures


def curvature_stats(curvatures):
    vals = list(curvatures.values())
    return {
        "mean": float(np.mean(vals)),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
        "std": float(np.std(vals)),
        "num_edges": len(vals),
        "num_positive": int(sum(1 for v in vals if v > 1e-10)),
        "num_zero": int(sum(1 for v in vals if abs(v) <= 1e-10)),
        "num_negative": int(sum(1 for v in vals if v < -1e-10)),
    }


def main():
    print("=" * 70)
    print("ALETHEIA — FALSIFICATION TEST 8")
    print("Ollivier-Ricci curvature on permutohedron graphs")
    print("=" * 70)

    # ---- n=3 (sanity check) ----
    print("\n--- n=3: Permutohedron (6 vertices, hexagonal graph) ---")
    G3, perms3 = build_permutohedron(3)
    print(f"  Vertices: {G3.number_of_nodes()}, Edges: {G3.number_of_edges()}")
    print(f"  Degree sequence: {sorted(set(dict(G3.degree()).values()))}")

    curv3 = compute_ollivier_ricci(G3)
    stats3 = curvature_stats(curv3)
    print(f"\n  n=3 Curvature stats:")
    print(f"    Mean:  {stats3['mean']:.6f}")
    print(f"    Min:   {stats3['min']:.6f}")
    print(f"    Max:   {stats3['max']:.6f}")
    print(f"    Std:   {stats3['std']:.6f}")
    print(f"    Positive: {stats3['num_positive']}, Zero: {stats3['num_zero']}, Negative: {stats3['num_negative']}")

    # ---- n=4 (main test) ----
    print("\n--- n=4: Permutohedron (24 vertices) ---")
    G4, perms4 = build_permutohedron(4)
    print(f"  Vertices: {G4.number_of_nodes()}, Edges: {G4.number_of_edges()}")
    print(f"  Degree sequence: {sorted(set(dict(G4.degree()).values()))}")

    curv4 = compute_ollivier_ricci(G4)
    stats4 = curvature_stats(curv4)
    print(f"\n  n=4 Curvature stats:")
    print(f"    Mean:  {stats4['mean']:.6f}")
    print(f"    Min:   {stats4['min']:.6f}")
    print(f"    Max:   {stats4['max']:.6f}")
    print(f"    Std:   {stats4['std']:.6f}")
    print(f"    Positive: {stats4['num_positive']}, Zero: {stats4['num_zero']}, Negative: {stats4['num_negative']}")

    # Print all unique curvature values for n=4
    unique_vals = sorted(set(round(v, 8) for v in curv4.values()))
    print(f"\n  Unique curvature values (n=4): {unique_vals}")

    # ---- Verdict ----
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    all_positive_n3 = stats3['num_negative'] == 0 and stats3['num_zero'] == 0
    all_positive_n4 = stats4['num_negative'] == 0 and stats4['num_zero'] == 0

    print(f"  n=3 uniformly positive curvature: {all_positive_n3}")
    print(f"  n=4 uniformly positive curvature: {all_positive_n4}")

    # S² comparison
    print(f"\n  S² (unit sphere): constant Gaussian curvature K=1 everywhere")
    print(f"  Permutohedron n=3: {'constant' if stats3['std'] < 1e-8 else 'variable'} Ollivier-Ricci curvature")
    print(f"  Permutohedron n=4: {'constant' if stats4['std'] < 1e-8 else 'variable'} Ollivier-Ricci curvature")

    if all_positive_n3 and all_positive_n4:
        if stats4['std'] < 1e-8:
            result = "PASS"
            confidence = "HIGH"
            evidence = (
                f"Permutohedron has CONSTANT positive Ollivier-Ricci curvature "
                f"(κ = {stats4['mean']:.6f} for all edges in n=4, "
                f"κ = {stats3['mean']:.6f} for all edges in n=3). "
                f"This mirrors S² which has constant positive Gaussian curvature. "
                f"The geometric parallel between Arrow's impossibility (preference aggregation "
                f"on the permutohedron) and the Theorema Egregium (curvature invariance on S²) "
                f"is structurally grounded: both live on positively curved spaces where "
                f"curvature obstructs flattening / faithful projection."
            )
        else:
            result = "PASS"
            confidence = "MODERATE"
            evidence = (
                f"Permutohedron has UNIFORMLY POSITIVE but non-constant Ollivier-Ricci curvature "
                f"(n=4: mean={stats4['mean']:.6f}, range=[{stats4['min']:.6f}, {stats4['max']:.6f}]). "
                f"S² has constant curvature, so the analogy holds qualitatively "
                f"(both positively curved → impossibility of flattening) but differs quantitatively "
                f"(permutohedron curvature varies while S² is homogeneous)."
            )
    elif all_positive_n3 and not all_positive_n4:
        result = "FAIL"
        confidence = "HIGH"
        evidence = (
            f"n=3 permutohedron has positive curvature but n=4 does NOT. "
            f"n=4 stats: {stats4['num_negative']} negative edges, {stats4['num_zero']} zero edges. "
            f"The geometric analogy breaks at the scale relevant to Arrow's theorem (n≥3 voters/alternatives). "
            f"Curvature-based impossibility structure is not preserved."
        )
    else:
        result = "FAIL"
        confidence = "HIGH"
        evidence = (
            f"Permutohedron does NOT have uniformly positive Ollivier-Ricci curvature. "
            f"n=3: {stats3['num_negative']} negative, {stats3['num_zero']} zero edges. "
            f"n=4: {stats4['num_negative']} negative, {stats4['num_zero']} zero edges. "
            f"The claimed curvature-based parallel between Arrow and Gauss is not supported."
        )

    if result == "PASS":
        implications = (
            "Supports the meta-thesis that impossibility theorems across domains share "
            "geometric structure. The permutohedron's positive curvature provides a concrete "
            "mechanism for why preference aggregation is impossible: you cannot flatten a "
            "positively curved space without distortion, just as you cannot flatten S² "
            "(Theorema Egregium). This strengthens Papers 3-4 of the Noesis framework."
        )
    else:
        implications = (
            "The Arrow-Gauss analogy is at best metaphorical, not structural. "
            "Papers claiming a shared curvature-based impossibility mechanism need revision. "
            "The impossibility in Arrow may stem from combinatorial/algebraic structure "
            "rather than differential-geometric curvature."
        )

    print(f"\n  RESULT: {result}")
    print(f"  CONFIDENCE: {confidence}")
    print(f"  EVIDENCE: {evidence}")

    # ---- Save results ----
    output = {
        "test": 8,
        "paper": "Arrow ↔ Map Projection",
        "claim": "Arrow's impossibility and the Theorema Egregium share a curvature-based impossibility structure",
        "result": result,
        "confidence": confidence,
        "evidence": evidence,
        "curvature_stats": {
            "mean": round(stats4['mean'], 8),
            "min": round(stats4['min'], 8),
            "max": round(stats4['max'], 8),
            "std": round(stats4['std'], 8),
        },
        "n3_curvature": {
            "mean": round(stats3['mean'], 8),
            "min": round(stats3['min'], 8),
            "max": round(stats3['max'], 8),
        },
        "n4_curvature": {
            "mean": round(stats4['mean'], 8),
            "min": round(stats4['min'], 8),
            "max": round(stats4['max'], 8),
        },
        "n3_detail": {
            "vertices": G3.number_of_nodes(),
            "edges": G3.number_of_edges(),
            "all_positive": all_positive_n3,
            "unique_curvatures": sorted(set(round(v, 8) for v in curv3.values())),
        },
        "n4_detail": {
            "vertices": G4.number_of_nodes(),
            "edges": G4.number_of_edges(),
            "all_positive": all_positive_n4,
            "unique_curvatures": sorted(set(round(v, 8) for v in curv4.values())),
        },
        "implications_for_other_papers": implications,
    }

    with open("F:/Prometheus/falsification/test_08_result.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n  Results saved to F:/Prometheus/falsification/test_08_result.json")


if __name__ == "__main__":
    main()
