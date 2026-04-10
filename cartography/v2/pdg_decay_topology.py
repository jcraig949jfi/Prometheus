#!/usr/bin/env python3
"""
PDG Decay Topology — Spectral Gap Analysis

Build the particle decay graph from 226 PDG particles.
Directed edges: particle A -> particle B if A decays (width > 0) and mass_A > mass_B.
Compute spectral gap, longest chain, sinks, degree distribution.

Charon / Prometheus cartography
"""

import json
import pathlib
import numpy as np
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "physics" / "data" / "pdg" / "particles.json"
OUT  = pathlib.Path(__file__).resolve().parent / "pdg_decay_topology_results.json"


def load_particles():
    with open(DATA) as f:
        raw = json.load(f)
    particles = []
    for i, p in enumerate(raw):
        particles.append({
            "idx": i,
            "name": p["name"].strip(),
            "mc_id": p["mc_ids"][0],
            "mass_GeV": p["mass_GeV"],
            "width_GeV": p.get("width_GeV"),  # None for quarks etc.
        })
    return particles


def build_adjacency(particles):
    """
    Directed graph: edge from i -> j if particle i decays (width > 0)
    and mass_i > mass_j (kinematically allowed).
    Particles with width=None or width=0 are stable/confined — no outgoing edges.
    """
    n = len(particles)
    adj = [[] for _ in range(n)]      # adjacency list (outgoing)
    in_adj = [[] for _ in range(n)]   # incoming edges

    for i, pi in enumerate(particles):
        w = pi["width_GeV"]
        if w is None or w == 0:
            continue  # stable or confined — no decays
        mi = pi["mass_GeV"]
        for j, pj in enumerate(particles):
            if i == j:
                continue
            if pj["mass_GeV"] < mi:
                adj[i].append(j)
                in_adj[j].append(i)

    return adj, in_adj


def spectral_gap(adj, n):
    """
    Compute spectral gap (lambda_2) of the graph Laplacian.
    Use the undirected version: L = D - A where A_ij = 1 if edge i->j or j->i.
    """
    # Build symmetric adjacency matrix
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in adj[i]:
            A[i, j] = 1.0
            A[j, i] = 1.0  # symmetrize for Laplacian

    D = np.diag(A.sum(axis=1))
    L = D - A

    eigenvalues = np.linalg.eigvalsh(L)
    eigenvalues.sort()

    # lambda_1 is the smallest nonzero eigenvalue (the spectral gap)
    # eigenvalues[0] should be ~0 (connected component)
    # Find first eigenvalue > threshold
    threshold = 1e-8
    nonzero_eigs = [e for e in eigenvalues if e > threshold]
    lambda_1 = nonzero_eigs[0] if nonzero_eigs else 0.0
    lambda_2 = nonzero_eigs[1] if len(nonzero_eigs) > 1 else 0.0

    return {
        "lambda_1_spectral_gap": float(lambda_1),
        "lambda_2": float(lambda_2),
        "algebraic_connectivity": float(lambda_1),
        "largest_eigenvalue": float(eigenvalues[-1]),
        "num_zero_eigenvalues": int(sum(1 for e in eigenvalues if e < threshold)),
        "first_10_eigenvalues": [float(e) for e in eigenvalues[:10]],
    }


def longest_chain_bfs(adj, n):
    """
    Find the longest directed path (diameter) using BFS/DFS from each node.
    Since edges go heavier -> lighter, the graph is a DAG (no cycles).
    Use dynamic programming on topological order.
    """
    # Topological sort by mass (heaviest first = sources first)
    # Actually, edges go from heavier to lighter, so sort by decreasing mass
    # gives topological order.

    # dp[i] = length of longest path starting from node i
    dp = [0] * n
    parent = [-1] * n  # for reconstructing the path

    # Process in reverse topological order (lightest first)
    # so when we process a heavy node, all its children are done
    from functools import lru_cache

    # Build memo
    memo = {}

    def dfs(node):
        if node in memo:
            return memo[node]
        best = 0
        best_child = -1
        for child in adj[node]:
            val = 1 + dfs(child)
            if val > best:
                best = val
                best_child = child
        memo[node] = best
        parent[node] = best_child
        return best

    for i in range(n):
        dfs(i)

    # Find the node with the longest chain
    max_len = max(memo.values()) if memo else 0
    start = max(range(n), key=lambda i: memo[i])

    # Reconstruct chain
    chain = [start]
    current = start
    while parent[current] != -1:
        current = parent[current]
        chain.append(current)

    return max_len, chain


def find_sinks(adj, particles):
    """Sinks = nodes with no outgoing edges."""
    sinks = []
    for i, p in enumerate(particles):
        if len(adj[i]) == 0:
            sinks.append({
                "idx": i,
                "name": p["name"],
                "mc_id": p["mc_id"],
                "mass_GeV": p["mass_GeV"],
                "width_GeV": p["width_GeV"],
            })
    return sinks


def degree_distribution(adj, in_adj, n):
    """Compute in-degree and out-degree distributions."""
    out_degrees = [len(adj[i]) for i in range(n)]
    in_degrees = [len(in_adj[i]) for i in range(n)]

    out_counter = Counter(out_degrees)
    in_counter = Counter(in_degrees)

    return {
        "out_degree": {
            "mean": float(np.mean(out_degrees)),
            "median": float(np.median(out_degrees)),
            "max": int(max(out_degrees)),
            "min": int(min(out_degrees)),
            "std": float(np.std(out_degrees)),
            "distribution": {str(k): v for k, v in sorted(out_counter.items())},
        },
        "in_degree": {
            "mean": float(np.mean(in_degrees)),
            "median": float(np.median(in_degrees)),
            "max": int(max(in_degrees)),
            "min": int(min(in_degrees)),
            "std": float(np.std(in_degrees)),
            "distribution": {str(k): v for k, v in sorted(in_counter.items())},
        },
    }


def identify_known_particles(particles):
    """Label well-known particles by mc_id."""
    known = {
        22: "photon", 11: "electron", 13: "muon", 15: "tau",
        12: "nu_e", 14: "nu_mu", 16: "nu_tau",
        2212: "proton", 2112: "neutron",
        211: "pi+", 111: "pi0",
        321: "K+", 311: "K0",
        24: "W+", 23: "Z0", 25: "Higgs",
        1: "d", 2: "u", 3: "s", 4: "c", 5: "b", 6: "t",
    }
    labels = {}
    for p in particles:
        mc = p["mc_id"]
        if mc in known:
            labels[p["idx"]] = known[mc]
        else:
            labels[p["idx"]] = p["name"]
    return labels


def main():
    import sys
    sys.setrecursionlimit(10000)

    particles = load_particles()
    n = len(particles)
    print(f"Loaded {n} particles")

    adj, in_adj = build_adjacency(particles)
    total_edges = sum(len(a) for a in adj)
    print(f"Built decay graph: {total_edges} directed edges")

    labels = identify_known_particles(particles)

    # Sinks
    sinks = find_sinks(adj, particles)
    print(f"\nSinks (stable/confined, no outgoing edges): {len(sinks)}")
    for s in sinks:
        lbl = labels.get(s["idx"], s["name"])
        print(f"  {lbl} (mc_id={s['mc_id']}, mass={s['mass_GeV']:.6f} GeV)")

    # Spectral gap
    print("\nComputing spectral gap...")
    spec = spectral_gap(adj, n)
    print(f"  Spectral gap (lambda_1): {spec['lambda_1_spectral_gap']:.6f}")
    print(f"  lambda_2: {spec['lambda_2']:.6f}")
    print(f"  Algebraic connectivity: {spec['algebraic_connectivity']:.6f}")
    print(f"  Largest eigenvalue: {spec['largest_eigenvalue']:.4f}")
    print(f"  Connected components: {spec['num_zero_eigenvalues']}")

    # Longest chain
    print("\nComputing longest decay chain...")
    max_len, chain = longest_chain_bfs(adj, n)
    print(f"  Longest chain length: {max_len}")
    chain_names = [f"{labels.get(i, particles[i]['name'])} ({particles[i]['mass_GeV']:.4f} GeV)"
                   for i in chain]
    print(f"  Chain: {' -> '.join(chain_names[:10])}")
    if len(chain) > 10:
        print(f"    ... ({len(chain) - 10} more)")

    # Degree distribution
    print("\nDegree distribution:")
    dd = degree_distribution(adj, in_adj, n)
    print(f"  Out-degree: mean={dd['out_degree']['mean']:.1f}, "
          f"max={dd['out_degree']['max']}, std={dd['out_degree']['std']:.1f}")
    print(f"  In-degree:  mean={dd['in_degree']['mean']:.1f}, "
          f"max={dd['in_degree']['max']}, std={dd['in_degree']['std']:.1f}")

    # Compile results
    results = {
        "metadata": {
            "task": "PDG Decay Topology — Spectral Gap Analysis",
            "n_particles": n,
            "n_edges": total_edges,
            "data_source": "cartography/physics/data/pdg/particles.json",
            "edge_rule": "directed edge A->B if width_A > 0 and mass_A > mass_B",
        },
        "spectral_analysis": spec,
        "longest_decay_chain": {
            "length": max_len,
            "chain": [
                {"name": labels.get(i, particles[i]["name"]),
                 "mc_id": particles[i]["mc_id"],
                 "mass_GeV": particles[i]["mass_GeV"]}
                for i in chain
            ],
        },
        "sinks": {
            "count": len(sinks),
            "particles": sinks,
            "interpretation": "Particles with no outgoing decay edges: truly stable (photon, electron, proton) or confined (quarks) or missing width measurement",
        },
        "degree_distribution": dd,
        "graph_properties": {
            "is_dag": True,  # edges only go heavier -> lighter
            "density": total_edges / (n * (n - 1)) if n > 1 else 0,
            "n_decaying": sum(1 for i in range(n) if len(adj[i]) > 0),
            "n_stable_or_confined": sum(1 for i in range(n) if len(adj[i]) == 0),
        },
    }

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")

    return results


if __name__ == "__main__":
    main()
