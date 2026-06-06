"""Synthetic control generators for Stage 0 (protocol v0.2 §4 #5-#8).

Each generator returns a ``ControlGraph`` carrying a graph, an edge-flow, and the
KNOWN Hodge structure it was built to have (``expected``). The 0a runner feeds these
through the decomposer and checks recovered == declared, proving the instrument can
see nothing in no-structure data and recover planted structure where it exists,
BEFORE any real failure data is touched.

This iteration ships #5 (no-cycle/no-void) and #6 (planted-cycle); #7 (planted-hole)
and #8 (operator-artifact) follow.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import networkx as nx

__all__ = ["ControlGraph", "circulation_flow", "no_cycle_graph", "planted_cycle_graph"]


@dataclass(frozen=True)
class ControlGraph:
    G: nx.Graph
    flow: dict
    kind: str
    expected: dict
    seed: int
    n_planted: int = 0
    meta: dict = field(default_factory=dict)


def _canon(u, v):
    return (u, v) if u <= v else (v, u)


def circulation_flow(cycle) -> dict:
    """Unit flow circulating once around ``cycle`` (a list of vertices), in
    canonical (sorted-pair) edge orientation."""
    flow = {}
    n = len(cycle)
    for i in range(n):
        a, b = cycle[i], cycle[(i + 1) % n]
        e = _canon(a, b)
        flow[e] = 1.0 if (a, b) == e else -1.0
    return flow


def _random_tree_edges(nodes, rng) -> list:
    """A uniform-ish random tree: attach each new node to a random earlier node."""
    edges = []
    for i in range(1, len(nodes)):
        j = int(rng.integers(0, i))
        edges.append(_canon(nodes[i], nodes[j]))
    return edges


def no_cycle_graph(n_nodes: int = 8, seed: int = 0) -> ControlGraph:
    """Control #5 — a tree with a gradient flow: zero curl, zero harmonic.

    Any flow on a tree is a gradient (the cycle space is empty), so the decomposer
    must read non_gradient_mass ~ 0. We use an explicit gradient of random node
    potentials so the flow is non-trivial.
    """
    if n_nodes < 2:
        raise ValueError("no_cycle_graph needs n_nodes >= 2 (a tree needs an edge)")
    rng = np.random.default_rng(seed)
    nodes = list(range(n_nodes))
    edges = _random_tree_edges(nodes, rng)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    phi = {v: float(rng.standard_normal()) for v in nodes}
    flow = {(u, v): phi[v] - phi[u] for (u, v) in edges}  # u<v canonical
    return ControlGraph(
        G=G,
        flow=flow,
        kind="no_cycle",
        expected={"curl_rank": 0, "harmonic_rank": 0, "non_gradient_mass": "zero"},
        seed=seed,
        n_planted=0,
    )


def planted_cycle_graph(
    n_triangles: int = 3, seed: int = 0, with_backbone: bool = True
) -> ControlGraph:
    """Control #6 — k disjoint filled triangles, each carrying a circulation.

    A filled 3-clique with a circulating flow is PURE CURL, so curl_rank == k and
    harmonic_rank == 0. An optional tree backbone connects the triangles (adding no
    new cycle and no new triangle) and carries a gradient flow, so the graph is not
    a disjoint union of identical pieces.
    """
    if n_triangles < 1:
        raise ValueError("planted_cycle_graph needs n_triangles >= 1")
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    flow: dict = {}
    triangle_anchors = []
    for t in range(n_triangles):
        a, b, c = 3 * t, 3 * t + 1, 3 * t + 2
        G.add_edges_from([_canon(a, b), _canon(b, c), _canon(a, c)])
        # circulating flow scaled by a nonzero random magnitude
        mag = float(rng.uniform(0.5, 2.0))
        for e, val in circulation_flow([a, b, c]).items():
            flow[e] = flow.get(e, 0.0) + mag * val
        triangle_anchors.append(a)

    if with_backbone and n_triangles > 1:
        # connect triangle anchors in a chain via single edges (no new triangle/cycle)
        for t in range(n_triangles - 1):
            u, v = triangle_anchors[t], triangle_anchors[t + 1]
            e = _canon(u, v)
            G.add_edge(*e)
            flow[e] = float(rng.standard_normal())  # gradient-ish background

    return ControlGraph(
        G=G,
        flow=flow,
        kind="planted_cycle",
        expected={
            "curl_rank": n_triangles,
            "harmonic_rank": 0,
            "non_gradient_mass": "positive",
        },
        seed=seed,
        n_planted=n_triangles,
        meta={"with_backbone": with_backbone},
    )
