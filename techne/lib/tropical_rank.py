"""TOOL_TROPICAL_RANK — Baker-Norine rank of a divisor on a finite graph.

Computes the Riemann-Roch rank r(D) for a divisor D on a connected
multigraph G, where the rank is defined via the chip-firing game
(Baker-Norine 2007). For a divisor D of degree d >= 0:

    r(D) = max { k : for every effective E of degree k, D - E ~ some effective }

with r(D) = -1 if D is not linearly equivalent to any effective divisor.

Interface:
    tropical_rank(adjacency, divisor) -> int
    tropical_rank_graph(vertices, edges, degrees) -> int       # verbose form
    is_winnable(adjacency, divisor) -> bool                    # equivalent to rank >= 0

Wraps `chipfiring` 1.1.3 (pure-Python chip-firing library).

Forged: 2026-04-22 | Tier: 1 (chipfiring wrapper) | REQ-012
Tested against: Riemann-Roch on small graphs.
    K_3 (triangle, genus 1): rank(D) = deg(D) - 1 for deg >= 2.
    K_4 (tetrahedron, genus 3): r(3-chip config) = 0.
"""
from typing import Sequence, Tuple, List, Union
import numpy as np

# chipfiring initializes multiprocessing state; import lazily at call time
# to keep the import side-effect contained.
_chipfiring = None


def _ensure_chipfiring():
    global _chipfiring
    if _chipfiring is None:
        import chipfiring as _cf
        _chipfiring = _cf
    return _chipfiring


def _adjacency_to_edges(adjacency) -> Tuple[List[str], List[Tuple[str, str, int]]]:
    """Convert a symmetric adjacency matrix to (vertices, edges) with labels.

    Vertex labels become 'v0', 'v1', ..., 'v{n-1}'.
    Edge multiplicities = adjacency[i,j] (for i < j).
    """
    A = np.asarray(adjacency)
    n = A.shape[0]
    if A.shape != (n, n):
        raise ValueError(f"adjacency must be square, got {A.shape}")
    verts = [f'v{i}' for i in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            mult = int(A[i, j])
            if mult != 0:
                # chipfiring wants (u, v, mult) with positive mult
                edges.append((verts[i], verts[j], mult))
    return verts, edges


def tropical_rank(adjacency, divisor: Sequence[int]) -> int:
    """Tropical (Baker-Norine) rank of a divisor on the graph given by adjacency.

    Parameters
    ----------
    adjacency : 2D array-like
        Symmetric non-negative integer matrix; entries are edge multiplicities.
        Self-loops (diagonal) ignored (harmless for chip-firing).
    divisor : sequence of ints, length = |V|
        Chip counts at each vertex, in the same order as rows of `adjacency`.

    Returns
    -------
    int — Baker-Norine rank r(D) >= -1. Returns -1 iff D is not winnable.

    Examples
    --------
    >>> # K_3 (triangle): genus 1, Riemann-Roch predicts r(D) = deg(D) - 1
    >>> A = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    >>> tropical_rank(A, [2, 0, 0])       # deg 2
    1
    >>> tropical_rank(A, [3, 0, 0])       # deg 3
    2
    """
    cf = _ensure_chipfiring()
    verts, edges = _adjacency_to_edges(adjacency)
    if len(divisor) != len(verts):
        raise ValueError(
            f"divisor length {len(divisor)} != number of vertices {len(verts)}"
        )
    G = cf.CFGraph(set(verts), edges)
    degrees = [(verts[i], int(divisor[i])) for i in range(len(verts))]
    D = cf.CFDivisor(G, degrees)
    r = cf.rank(D)
    return int(r.rank)


def tropical_rank_graph(vertices: Sequence, edges: Sequence, degrees: Sequence) -> int:
    """Tropical rank given explicit vertex labels and edges.

    Parameters
    ----------
    vertices : sequence of hashable labels
    edges : sequence of (u, v) or (u, v, multiplicity)
        Multiplicity defaults to 1 if not specified.
    degrees : sequence of (vertex_label, chip_count) pairs

    Returns
    -------
    int — r(D)
    """
    cf = _ensure_chipfiring()
    V = {str(v) for v in vertices}
    E = []
    for edge in edges:
        if len(edge) == 2:
            u, v = edge
            m = 1
        else:
            u, v, m = edge
        E.append((str(u), str(v), int(m)))
    G = cf.CFGraph(V, E)
    deg_list = [(str(v), int(d)) for v, d in degrees]
    D = cf.CFDivisor(G, deg_list)
    return int(cf.rank(D).rank)


def is_winnable(adjacency, divisor: Sequence[int]) -> bool:
    """True iff D is linearly equivalent to an effective divisor (i.e. r(D) >= 0)."""
    return tropical_rank(adjacency, divisor) >= 0
