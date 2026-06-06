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

__all__ = [
    "ControlGraph",
    "circulation_flow",
    "no_cycle_graph",
    "planted_cycle_graph",
    "planted_hole_graph",
    "operator_artifact_graph",
]


@dataclass(frozen=True)
class ControlGraph:
    G: nx.Graph
    flow: dict
    kind: str
    expected: dict
    seed: int
    n_planted: int = 0
    edge_operators: dict | None = None   # edge -> operator/emitter label (#8, nulls)
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


def planted_hole_graph(
    n_holes: int = 2, hole_len: int = 4, seed: int = 0, with_backbone: bool = True
) -> ControlGraph:
    """Control #7 — k disjoint CHORDLESS cycles (holes), each carrying a circulation.

    A chordless cycle of length >= 4 has no triangle to fill, so a circulation
    around it is PURE HARMONIC: harmonic_rank == k, curl_rank == 0. An optional tree
    backbone of bridges joins the holes (a bridge is in no cycle, so it adds neither
    a hole nor a triangle) and carries a gradient background.
    """
    if n_holes < 1:
        raise ValueError("planted_hole_graph needs n_holes >= 1")
    if hole_len < 4:
        raise ValueError("hole_len must be >= 4 (length 3 is a triangle = curl)")
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    flow: dict = {}
    hole_anchors = []
    for h in range(n_holes):
        verts = [h * hole_len + i for i in range(hole_len)]
        cyc_edges = [_canon(verts[i], verts[(i + 1) % hole_len]) for i in range(hole_len)]
        G.add_edges_from(cyc_edges)
        mag = float(rng.uniform(0.5, 2.0))
        for e, val in circulation_flow(verts).items():
            flow[e] = flow.get(e, 0.0) + mag * val
        hole_anchors.append(verts[0])

    if with_backbone and n_holes > 1:
        for h in range(n_holes - 1):
            u, v = hole_anchors[h], hole_anchors[h + 1]
            e = _canon(u, v)
            G.add_edge(*e)
            flow[e] = float(rng.standard_normal())

    return ControlGraph(
        G=G,
        flow=flow,
        kind="planted_hole",
        expected={
            "curl_rank": 0,
            "harmonic_rank": n_holes,
            "non_gradient_mass": "positive",
        },
        seed=seed,
        n_planted=n_holes,
        meta={"hole_len": hole_len, "with_backbone": with_backbone},
    )


def operator_artifact_graph(operator_counts: dict, n_nodes: int = 8, seed: int = 0) -> ControlGraph:
    """Control #8 — operator-labelled flow on RANDOMIZED topology (the floor).

    Edges carry operator labels matching ``operator_counts`` exactly, and the flow
    on each edge is its operator's signature value, so the flow carries operator
    structure but NO planted topological structure. Whatever non_gradient_mass the
    decomposer reads here is the operator-induced false-positive floor that a real
    claim must clear (protocol v0.2 §4 #8; the operator-vs-state-curl distinction).
    """
    if not operator_counts or any(c <= 0 for c in operator_counts.values()):
        raise ValueError("operator_counts must be a non-empty map of positive counts")
    if n_nodes < 2:
        raise ValueError("operator_artifact_graph needs n_nodes >= 2")
    n_edges = int(sum(operator_counts.values()))
    max_edges = n_nodes * (n_nodes - 1) // 2
    if n_edges > max_edges:
        raise ValueError(f"{n_edges} edges exceed the {max_edges} possible on {n_nodes} nodes")

    rng = np.random.default_rng(seed)
    all_possible = [(i, j) for i in range(n_nodes) for j in range(i + 1, n_nodes)]
    chosen = rng.choice(len(all_possible), size=n_edges, replace=False)
    edges = [all_possible[k] for k in chosen]

    labels = []
    for op, c in operator_counts.items():
        labels.extend([op] * int(c))
    rng.shuffle(labels)
    signature = {op: float(rng.standard_normal()) for op in operator_counts}

    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    G.add_edges_from(edges)
    edge_operators = {e: labels[i] for i, e in enumerate(edges)}
    flow = {e: signature[edge_operators[e]] for e in edges}

    return ControlGraph(
        G=G,
        flow=flow,
        kind="operator_artifact",
        expected={"floor": True},
        seed=seed,
        n_planted=0,
        edge_operators=edge_operators,
        meta={"signature": signature, "operator_counts": dict(operator_counts)},
    )
