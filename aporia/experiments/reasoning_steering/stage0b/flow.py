"""Relational comparison-flow builder (Stage 0b, v0.3).

Builds the edge flow the Hodge decomposer reads, on the COMPLETE graph of states:

    flow(i, j) = Σ_k  sign( margin_k(state_j) − margin_k(state_i) )

over the falsifiers k present in BOTH states' margin vectors (Condorcet pairwise
comparison). The `sign` non-linearity is what lets the flow be non-conservative:
linear aggregation would collapse to a node-potential gradient. Non-transitive
comparisons (a≻b, b≻c, c≻a) produce circulation (curl); transitive ones are a pure
gradient.
"""
from __future__ import annotations

import networkx as nx

__all__ = ["relational_flow"]


def _sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def relational_flow(vectors):
    """Build (G, flow) from per-state margin vectors.

    vectors : list of dict {falsifier_name: margin}; node id = list index.
    Returns (networkx complete Graph, {canonical_edge (i<j): float flow}).
    """
    n = len(vectors)
    if n < 2:
        raise ValueError("need >= 2 states for a comparison graph")
    G = nx.complete_graph(n)
    flow = {}
    for i in range(n):
        vi = vectors[i]
        for j in range(i + 1, n):
            vj = vectors[j]
            shared = set(vi) & set(vj)
            flow[(i, j)] = float(sum(_sign(vj[k] - vi[k]) for k in shared))
    return G, flow
