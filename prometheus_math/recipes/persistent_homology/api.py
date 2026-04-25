"""Thin facade over GUDHI for the persistent-homology recipe gallery.

This module is intentionally small: it exposes the handful of helpers that
every recipe in the gallery uses, so each recipe can stay focused on the
mathematical idea rather than backend boilerplate.

Backend selection
-----------------
Primary backend: GUDHI (https://gudhi.inria.fr).  GUDHI is preferred because
it covers the full pipeline used by these recipes -- Vietoris-Rips, cubical
sublevel-set persistence, bottleneck distance, Wasserstein distance, and
persistence-image vectorisation -- with a stable Python API.

If GUDHI is missing, every helper raises a single, clearly-worded ImportError
with the install hint (`pip install gudhi`).  We do not silently degrade.

Diagram convention
------------------
A "diagram" in this module is a list of ``(dim, (birth, death))`` tuples,
matching ``gudhi.SimplexTree.persistence`` output.  Infinite-persistence bars
use ``death == float('inf')``.  Helpers that need (birth, death) arrays
filter by dimension and drop the infinite bars themselves.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple, Dict

import numpy as np

try:
    import gudhi as _gd
    import gudhi.wasserstein as _gd_wasserstein
    import gudhi.representations as _gd_repr
    _HAS_GUDHI = True
except Exception:  # pragma: no cover - tested via skip
    _gd = None
    _gd_wasserstein = None
    _gd_repr = None
    _HAS_GUDHI = False


# ---------------------------------------------------------------------------
# Internal guards / type aliases
# ---------------------------------------------------------------------------

Diagram = List[Tuple[int, Tuple[float, float]]]


def _require_gudhi() -> None:
    if not _HAS_GUDHI:
        raise ImportError(
            "GUDHI is required for prometheus_math.recipes.persistent_homology. "
            "Install with `pip install gudhi`."
        )


def _connected_components_from_simplex_tree(st, n_vertices: int) -> int:
    """Count connected components of the final complex via union-find on edges."""
    parent = list(range(n_vertices))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for simplex, _filt in st.get_filtration():
        if len(simplex) == 2:
            union(int(simplex[0]), int(simplex[1]))
    roots = {find(i) for i in range(n_vertices)}
    return len(roots)


def _ensure_infinite_h0(diag: "Diagram", st, n_vertices: int) -> "Diagram":
    """Repair GUDHI's persistence output when it omits infinite H_0 bars.

    GUDHI's ``SimplexTree.persistence`` can return an empty list when no
    homology class is born and dies inside the filtration, even though the
    final complex has connected components.  We compute the number of
    components via union-find and append the missing ``(0, (0.0, inf))``
    bars so downstream code (Betti numbers, smoke tests) sees a coherent
    diagram.
    """
    if n_vertices == 0:
        return diag
    have_inf = sum(1 for d, (_b, x) in diag if d == 0 and math.isinf(x))
    expected = _connected_components_from_simplex_tree(st, n_vertices)
    missing = expected - have_inf
    if missing > 0:
        diag = list(diag) + [(0, (0.0, float("inf")))] * missing
    return diag


def _diag_pairs(diag: Diagram, dim: int, drop_inf: bool = True) -> np.ndarray:
    """Extract a (N, 2) array of (birth, death) for a fixed dimension."""
    rows = []
    for d, (b, x) in diag:
        if d != dim:
            continue
        if drop_inf and (math.isinf(x) or math.isnan(x)):
            continue
        rows.append((float(b), float(x)))
    if not rows:
        return np.zeros((0, 2), dtype=float)
    return np.asarray(rows, dtype=float)


# ---------------------------------------------------------------------------
# Vietoris-Rips persistence
# ---------------------------------------------------------------------------

def rips_persistence(
    points: np.ndarray,
    max_dim: int = 2,
    max_edge_length: float | None = None,
) -> Diagram:
    """Persistence diagram of the Vietoris-Rips complex on ``points``.

    Parameters
    ----------
    points
        (N, d) array of points in R^d.
    max_dim
        Maximum homological dimension to compute.  Internally the simplex
        tree is built up to dimension ``max_dim + 1`` so that ``H_{max_dim}``
        is fully resolved.
    max_edge_length
        Threshold for the Rips filtration.  Defaults to twice the diameter
        of the point cloud, which is enough to merge every component.
    """
    _require_gudhi()
    pts = np.asarray(points, dtype=float)
    if pts.ndim != 2 or pts.shape[0] == 0:
        raise ValueError("points must be a non-empty 2D array")
    if max_edge_length is None:
        # Diameter is conservative; * 2 guarantees H_0 closes for any cloud.
        diam = float(np.max(np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)))
        max_edge_length = 2.0 * (diam if diam > 0 else 1.0)
    rc = _gd.RipsComplex(points=pts, max_edge_length=max_edge_length)
    st = rc.create_simplex_tree(max_dimension=max_dim + 1)
    diag = list(st.persistence())
    return _ensure_infinite_h0(diag, st, pts.shape[0])


def persistence_diagram_from_distmat(
    D: np.ndarray,
    max_dim: int = 2,
    max_edge_length: float | None = None,
) -> Diagram:
    """Vietoris-Rips persistence directly from a precomputed distance matrix.

    Useful when the metric is not Euclidean (graph distances, edit distances,
    correlation distances, ...).  ``D`` must be a symmetric, non-negative
    (N, N) matrix with zero diagonal.
    """
    _require_gudhi()
    A = np.asarray(D, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1] or A.shape[0] == 0:
        raise ValueError("D must be a non-empty square matrix")
    if not np.allclose(A, A.T, atol=1e-10):
        raise ValueError("D must be symmetric")
    if np.any(A < -1e-12):
        raise ValueError("D must be non-negative")
    if max_edge_length is None:
        max_edge_length = float(A.max()) * 2.0 if A.size else 1.0
    # GUDHI accepts the lower-triangular distance matrix as a list of lists.
    n = A.shape[0]
    dm = [list(A[i, : i + 1]) for i in range(n)]
    rc = _gd.RipsComplex(distance_matrix=dm, max_edge_length=max_edge_length)
    st = rc.create_simplex_tree(max_dimension=max_dim + 1)
    diag = list(st.persistence())
    return _ensure_infinite_h0(diag, st, n)


# ---------------------------------------------------------------------------
# Diagram-level metrics
# ---------------------------------------------------------------------------

def bottleneck_distance(diag_a: Diagram, diag_b: Diagram, dim: int = 1) -> float:
    """Bottleneck distance between two diagrams restricted to dimension ``dim``.

    Reference: Edelsbrunner & Harer, *Computational Topology*, Section VIII.2.
    """
    _require_gudhi()
    A = _diag_pairs(diag_a, dim)
    B = _diag_pairs(diag_b, dim)
    return float(_gd.bottleneck_distance(A, B))


def wasserstein_distance(
    diag_a: Diagram,
    diag_b: Diagram,
    p: float = 2.0,
    dim: int = 1,
) -> float:
    """p-Wasserstein distance between two diagrams in dimension ``dim``.

    Wraps ``gudhi.wasserstein.wasserstein_distance`` (Hera backend).
    Internal-distance is L_inf, matching the standard PH convention.
    """
    _require_gudhi()
    A = _diag_pairs(diag_a, dim)
    B = _diag_pairs(diag_b, dim)
    return float(_gd_wasserstein.wasserstein_distance(A, B, order=p, internal_p=float("inf")))


# ---------------------------------------------------------------------------
# Vectorisation: persistence images
# ---------------------------------------------------------------------------

def persistence_image(
    diag: Diagram,
    dim: int = 1,
    resolution: int = 20,
    sigma: float = 0.1,
) -> np.ndarray:
    """Render a 2D persistence image for the dim-th part of ``diag``.

    Reference: Adams et al., "Persistence Images: A Stable Vector
    Representation of Persistent Homology", JMLR 18 (2017).
    """
    _require_gudhi()
    pairs = _diag_pairs(diag, dim)
    if pairs.shape[0] == 0:
        return np.zeros((resolution, resolution), dtype=float)
    pi = _gd_repr.PersistenceImage(
        bandwidth=sigma,
        resolution=[resolution, resolution],
    )
    pi.fit([pairs])
    img = pi.transform([pairs])[0]
    return np.asarray(img, dtype=float).reshape(resolution, resolution)


# ---------------------------------------------------------------------------
# Betti numbers
# ---------------------------------------------------------------------------

def betti_numbers_from_diagram(diag: Diagram) -> Dict[int, int]:
    """Betti numbers as the count of infinite-persistence bars per dimension.

    The Betti number ``beta_k(X)`` is the rank of ``H_k(X)``.  In a
    persistence diagram of the full filtration, ``beta_k`` equals the number
    of bars in dimension k that survive to infinity.
    """
    counts: Dict[int, int] = {}
    for d, (_b, x) in diag:
        if math.isinf(x):
            counts[d] = counts.get(d, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Time-series TDA: sliding-window embedding
# ---------------------------------------------------------------------------

def sliding_window_embed(ts: np.ndarray, dim: int, tau: int) -> np.ndarray:
    """Takens-style sliding-window embedding of a 1D time series.

    Returns an (M, dim) array where ``M = len(ts) - (dim - 1) * tau``.
    Each row is ``[ts[i], ts[i+tau], ts[i+2*tau], ..., ts[i+(dim-1)*tau]]``.

    Reference: Perea & Harer, "Sliding Windows and Persistence", Foundations
    of Computational Mathematics 15 (2015).
    """
    arr = np.asarray(ts, dtype=float).reshape(-1)
    if dim < 1:
        raise ValueError("dim must be >= 1")
    if tau < 1:
        raise ValueError("tau must be >= 1")
    M = arr.shape[0] - (dim - 1) * tau
    if M <= 0:
        raise ValueError(
            f"time series too short for embedding: need len >= (dim-1)*tau+1 = {(dim-1)*tau+1}, got {arr.shape[0]}"
        )
    out = np.empty((M, dim), dtype=float)
    for k in range(dim):
        out[:, k] = arr[k * tau : k * tau + M]
    return out


# ---------------------------------------------------------------------------
# Cubical (image / scalar field) sublevel-set persistence
# ---------------------------------------------------------------------------

def cubical_persistence(image_2d: np.ndarray) -> Diagram:
    """Sublevel-set persistence of a 2D scalar field (e.g. a grayscale image).

    Returns the diagram in the same ``[(dim, (birth, death))]`` shape as
    rips_persistence so that the rest of the gallery composes with it.
    """
    _require_gudhi()
    arr = np.asarray(image_2d, dtype=float)
    if arr.ndim != 2 or arr.size == 0:
        raise ValueError("image_2d must be a non-empty 2D array")
    cc = _gd.CubicalComplex(top_dimensional_cells=arr)
    cc.compute_persistence()
    return list(cc.persistence())


__all__ = [
    "rips_persistence",
    "persistence_diagram_from_distmat",
    "bottleneck_distance",
    "wasserstein_distance",
    "persistence_image",
    "betti_numbers_from_diagram",
    "sliding_window_embed",
    "cubical_persistence",
]
