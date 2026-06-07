"""Combinatorial Hodge decomposition of an edge-flow on a graph (Stage 0 core).

Splits an edge-flow f into three orthogonal parts:

    f = grad(phi)  +  curl_adjoint(psi)  +  harmonic(h)

following combinatorial Hodge theory / HodgeRank
(Jiang, Lim, Yao, Ye, "Statistical ranking and combinatorial Hodge theory",
Math. Program. 127 (2011) 203-244).

Construction (canonical edge orientation = sorted vertex pair):
  B1  : node x edge incidence (boundary d1).  Column for edge (u<v): -1 at u, +1 at v.
  grad operator d0 = B1.T            (maps node potentials -> edge flows)
  B2  : edge x triangle incidence (boundary d2). Triangles = filled 3-cliques.
        Column for triangle (a<b<c): +1 at (a,b), -1 at (a,c), +1 at (b,c).
  curl_adjoint = B2                  (maps triangle potentials -> edge flows)

Because d1 d2 = 0 (i.e. B1 @ B2 = 0), im(d0) _|_ im(B2); projecting f onto each
independently leaves an orthogonal harmonic residual. Masses are squared-norm
fractions; ranks are subspace dimensions (graph properties, not flow properties):
  curl_rank      = rank(B2)                       (# independent filled cycles)
  harmonic_rank  = |E| - rank(B1) - rank(B2) = b1 (# holes, first Betti number)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import networkx as nx

__all__ = ["HodgeDecomposition", "hodge_decompose"]


@dataclass(frozen=True)
class HodgeDecomposition:
    edges: tuple                # ordered canonical edges aligning all vectors
    gradient: np.ndarray
    curl: np.ndarray
    harmonic: np.ndarray
    gradient_mass: float
    curl_mass: float
    harmonic_mass: float
    non_gradient_mass: float
    curl_rank: int
    harmonic_rank: int


def _canon(u, v):
    return (u, v) if u <= v else (v, u)


def _incidence_b1(nodes, edges):
    node_ix = {n: i for i, n in enumerate(nodes)}
    B1 = np.zeros((len(nodes), len(edges)))
    for j, (u, v) in enumerate(edges):       # u < v by construction
        B1[node_ix[u], j] = -1.0
        B1[node_ix[v], j] = +1.0
    return B1


def _incidence_b2(G, edges):
    """Edge x triangle incidence for all filled 3-cliques.

    Triangles are enumerated DIRECTLY via edge common-neighbours (O(E * degree)),
    NOT via nx.enumerate_all_cliques -- the latter generates cliques of every size
    (exponential on dense graphs: K30 -> ~2^30 cliques -> MemoryError). This is
    behaviour-preserving (identical triangle set) and scales to dense comparison graphs.
    """
    edge_ix = {e: i for i, e in enumerate(edges)}
    adj = {n: set(G.neighbors(n)) for n in G.nodes()}
    tri = set()
    for u, v in edges:                       # canonical u < v
        for w in adj[u] & adj[v]:
            tri.add(tuple(sorted((u, v, w))))
    triangles = sorted(tri)
    B2 = np.zeros((len(edges), len(triangles)))
    for k, (a, b, c) in enumerate(triangles):
        B2[edge_ix[(a, b)], k] += 1.0
        B2[edge_ix[(a, c)], k] += -1.0
        B2[edge_ix[(b, c)], k] += 1.0
    return B2


def hodge_decompose(G: nx.Graph, flow) -> HodgeDecomposition:
    """Decompose ``flow`` on graph ``G``.

    flow: dict {canonical_edge (u<v): value} covering every edge of G exactly.
    """
    if G.number_of_edges() == 0:
        raise ValueError("graph has no edges to decompose")
    for u, v in G.edges():
        if u == v:
            raise ValueError(f"self-loop ({u},{v}) is not a valid 1-cell")

    edges = tuple(sorted(_canon(u, v) for u, v in G.edges()))
    nodes = tuple(sorted(G.nodes()))

    try:
        f = np.array([float(flow[e]) for e in edges])
    except KeyError as exc:
        raise ValueError(f"flow missing a value for edge {exc.args[0]}") from None

    B1 = _incidence_b1(nodes, edges)         # |V| x |E|
    d0 = B1.T                                 # |E| x |V|  (gradient operator)
    B2 = _incidence_b2(G, edges)             # |E| x |T|  (curl adjoint)

    total_sq = float(f @ f)
    if total_sq == 0.0:
        raise ValueError("zero flow has no decomposition")

    # project onto im(d0) and im(B2); harmonic is the orthogonal residual
    grad = _project_onto_columns(d0, f)
    curl = _project_onto_columns(B2, f)
    harmonic = f - grad - curl

    grad_sq = float(grad @ grad)
    curl_sq = float(curl @ curl)
    harm_sq = float(harmonic @ harmonic)

    rank_b1 = int(np.linalg.matrix_rank(B1)) if B1.size else 0
    curl_rank = int(np.linalg.matrix_rank(B2)) if B2.size else 0
    harmonic_rank = len(edges) - rank_b1 - curl_rank

    return HodgeDecomposition(
        edges=edges,
        gradient=grad,
        curl=curl,
        harmonic=harmonic,
        gradient_mass=grad_sq / total_sq,
        curl_mass=curl_sq / total_sq,
        harmonic_mass=harm_sq / total_sq,
        non_gradient_mass=(curl_sq + harm_sq) / total_sq,
        curl_rank=curl_rank,
        harmonic_rank=harmonic_rank,
    )


def _project_onto_columns(A: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Orthogonal projection of f onto the column space of A (least squares)."""
    if A.size == 0 or A.shape[1] == 0:
        return np.zeros_like(f)
    coef, *_ = np.linalg.lstsq(A, f, rcond=None)
    return A @ coef
