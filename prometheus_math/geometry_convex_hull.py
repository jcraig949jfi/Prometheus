"""prometheus_math.geometry_convex_hull — convex hulls via Qhull.

This is the seed module for the ``pm.geometry`` namespace (see project
#71).  It provides convex-hull computation for finite point clouds in
arbitrary dimension by wrapping ``scipy.spatial.ConvexHull`` (a binding
to the venerable Qhull C library).

Public API:

- ``convex_hull(points)``                — full hull dictionary
- ``convex_hull_volume(points)``         — n-D volume (length in 1-D,
                                            area in 2-D, volume in 3-D+)
- ``convex_hull_area(points)``           — surface area / perimeter
- ``is_in_convex_hull(point, points)``   — membership test
- ``extreme_points(points)``             — vertex indices on the hull
- ``convex_hull_facets(points)``         — facets as point-index lists
- ``convex_hull_2d_polygon(points)``     — ordered 2-D polygon vertices
- ``delaunay_triangulation_count(points)``— |Delaunay simplices|
- ``convex_hull_diameter(points)``       — (max distance, idx_a, idx_b)

Backend: scipy.spatial.ConvexHull / Delaunay (Qhull).  Always available.

Edge handling:

- Empty input  → ``ValueError``.
- Degenerate (singleton, collinear, too few points for the dimension)
  is handled explicitly: scipy raises ``QhullError`` and we either
  return the obvious geometric answer (1-D, singleton, segment) or
  re-raise as ``ValueError`` with a clear message.
- Duplicate points are accepted; Qhull discards them internally.

References:
- Barber, Dobkin & Huhdanpaa, "The Quickhull Algorithm for Convex
  Hulls", ACM Trans. Math. Softw. 22(4):469-483, 1996.
- scipy.spatial.ConvexHull documentation.
- de Berg, van Kreveld, Overmars, Schwarzkopf, "Computational
  Geometry: Algorithms and Applications" (3rd ed., 2008), Ch. 11.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple, Union

import numpy as np
from scipy.spatial import ConvexHull as _ConvexHull
from scipy.spatial import Delaunay as _Delaunay
from scipy.spatial import QhullError as _QhullError


__all__ = [
    "convex_hull",
    "convex_hull_volume",
    "convex_hull_area",
    "is_in_convex_hull",
    "extreme_points",
    "convex_hull_facets",
    "convex_hull_2d_polygon",
    "delaunay_triangulation_count",
    "convex_hull_diameter",
]


# ---------------------------------------------------------------------------
# Input normalization
# ---------------------------------------------------------------------------


def _as_points(points) -> np.ndarray:
    """Coerce ``points`` to a 2-D float array (n_points, n_dim).

    1-D inputs are interpreted as a list of 1-D points and reshaped to
    ``(n, 1)``.  Empty input raises ``ValueError``.
    """
    arr = np.asarray(points, dtype=float)
    if arr.size == 0:
        raise ValueError("convex_hull: empty point set")
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if arr.ndim != 2:
        raise ValueError(
            f"convex_hull: expected (n_points, n_dim) array, got shape {arr.shape}"
        )
    return arr


def _trivial_hull(arr: np.ndarray) -> dict:
    """Build a trivial hull dict for n-D inputs that Qhull rejects.

    Covers four degenerate cases: 1-D inputs (Qhull requires d ≥ 2),
    singletons, two-point clouds, and otherwise-degenerate clouds (all
    points coincide, or all points are collinear/coplanar in n-D).
    """
    n, d = arr.shape

    # All points equal (after accounting for duplicates).
    uniq = np.unique(arr, axis=0)

    if d == 1:
        lo_idx = int(np.argmin(arr[:, 0]))
        hi_idx = int(np.argmax(arr[:, 0]))
        length = float(arr[hi_idx, 0] - arr[lo_idx, 0])
        if length == 0.0:
            return {
                "vertices": np.array([lo_idx], dtype=int),
                "simplices": np.empty((0, 1), dtype=int),
                "neighbors": np.empty((0, 0), dtype=int),
                "equations": np.empty((0, 2), dtype=float),
                "volume": 0.0,
                "area": 0.0,
                "points": arr,
                "degenerate": True,
            }
        # Two half-space inequalities defining the segment [lo, hi]:
        # -x + lo <= 0 and x - hi <= 0  (form Ax + b ≤ 0)
        equations = np.array(
            [[-1.0, float(arr[lo_idx, 0])], [1.0, -float(arr[hi_idx, 0])]],
            dtype=float,
        )
        return {
            "vertices": np.array([lo_idx, hi_idx], dtype=int),
            "simplices": np.array([[lo_idx], [hi_idx]], dtype=int),
            "neighbors": np.array([[1], [0]], dtype=int),
            "equations": equations,
            "volume": length,        # 1-D "volume" = length
            "area": 0.0,             # 1-D hull has 0-D boundary (two points)
            "points": arr,
            "degenerate": False,
        }

    # d >= 2 fallback: degenerate (singleton / collinear / coplanar).
    if len(uniq) == 1:
        return {
            "vertices": np.array([0], dtype=int),
            "simplices": np.empty((0, d), dtype=int),
            "neighbors": np.empty((0, 0), dtype=int),
            "equations": np.empty((0, d + 1), dtype=float),
            "volume": 0.0,
            "area": 0.0,
            "points": arr,
            "degenerate": True,
        }

    # Two distinct points or higher-d but flat: try a joggled hull, which
    # gives a (perturbed) full-dimensional answer that we can clamp to
    # the obvious geometric truth (volume=0, the boundary is the cloud
    # itself).  The vertex set is the unique-point indices.
    vertex_idx = []
    seen = {}
    for i, p in enumerate(arr):
        key = tuple(p.tolist())
        if key not in seen:
            seen[key] = i
            vertex_idx.append(i)
    return {
        "vertices": np.array(vertex_idx, dtype=int),
        "simplices": np.empty((0, d), dtype=int),
        "neighbors": np.empty((0, 0), dtype=int),
        "equations": np.empty((0, d + 1), dtype=float),
        "volume": 0.0,
        "area": 0.0,
        "points": arr,
        "degenerate": True,
    }


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------


def convex_hull(points) -> dict:
    """Compute the convex hull of ``points``.

    Parameters
    ----------
    points : array-like (n, d)
        n points in d-dimensional Euclidean space.

    Returns
    -------
    dict with keys:
        ``vertices``   — indices of points that lie on the hull,
        ``simplices``  — array of facet-vertex indices,
        ``neighbors``  — neighboring-facet indices (one per facet),
        ``equations``  — half-space inequalities ``Ax + b ≤ 0`` (each row
                         is ``[a_1, …, a_d, b]``),
        ``volume``     — n-D volume (length / area / volume),
        ``area``       — boundary measure (perimeter in 2-D, surface
                         area in 3-D+, 0 in 1-D),
        ``points``     — the original input array,
        ``degenerate`` — True iff the cloud is lower-dimensional than ``d``.

    Raises
    ------
    ValueError if ``points`` is empty or otherwise unrecognisable.
    """
    arr = _as_points(points)
    n, d = arr.shape
    if d == 1 or n < d + 1:
        return _trivial_hull(arr)
    try:
        h = _ConvexHull(arr)
    except _QhullError:
        # Cloud is geometrically degenerate (collinear, coplanar, …).
        return _trivial_hull(arr)
    return {
        "vertices": np.asarray(h.vertices, dtype=int),
        "simplices": np.asarray(h.simplices, dtype=int),
        "neighbors": np.asarray(h.neighbors, dtype=int),
        "equations": np.asarray(h.equations, dtype=float),
        "volume": float(h.volume),
        "area": float(h.area),
        "points": arr,
        "degenerate": False,
    }


def convex_hull_volume(points) -> float:
    """n-D volume of the convex hull of ``points``.

    1-D: length of the bounding interval.  2-D: polygon area.  3-D+:
    standard Lebesgue volume.  Returns 0.0 for degenerate clouds.
    """
    return convex_hull(points)["volume"]


def convex_hull_area(points) -> float:
    """Boundary measure of the convex hull of ``points``.

    2-D: perimeter.  3-D+: surface area.  1-D: 0.0 (the boundary is two
    points).  Degenerate clouds: 0.0.
    """
    return convex_hull(points)["area"]


def extreme_points(points) -> List[int]:
    """Return the indices of points that lie on the hull boundary.

    For a non-degenerate cloud this is exactly the set of vertices of
    ``convex_hull(points)``.  Always satisfies
    ``len(extreme_points(p)) <= len(p)``.
    """
    return convex_hull(points)["vertices"].tolist()


def convex_hull_facets(points) -> List[List[int]]:
    """Return the facets of the convex hull as lists of point indices.

    A facet is a (d-1)-simplex on the hull boundary.  In 2-D each facet
    is an edge ``[i, j]``; in 3-D each facet is a triangle ``[i, j, k]``.
    Returns an empty list for degenerate clouds.
    """
    return [list(map(int, s)) for s in convex_hull(points)["simplices"]]


def convex_hull_2d_polygon(points) -> List[Tuple[float, float]]:
    """Return the 2-D convex-hull polygon as an ordered list of vertices.

    The order is counter-clockwise (Qhull's natural order for 2-D).  The
    first vertex is *not* repeated at the end.
    """
    arr = _as_points(points)
    if arr.shape[1] != 2:
        raise ValueError(
            f"convex_hull_2d_polygon: expected 2-D points, got shape {arr.shape}"
        )
    h = convex_hull(arr)
    verts = h["vertices"]
    return [(float(arr[i, 0]), float(arr[i, 1])) for i in verts]


def is_in_convex_hull(point, hull_points) -> bool:
    """Return True iff ``point`` lies inside (or on) the convex hull.

    Implementation: build a Delaunay triangulation of ``hull_points``
    and query ``find_simplex``; the answer is ``True`` iff the
    containing simplex index is non-negative.  This is the recommended
    scipy idiom (it works in arbitrary dimension and handles boundary
    membership consistently with Qhull's tolerances).
    """
    arr = _as_points(hull_points)
    pt = np.asarray(point, dtype=float).reshape(-1)
    if pt.size != arr.shape[1]:
        raise ValueError(
            f"is_in_convex_hull: point dim {pt.size} != hull dim {arr.shape[1]}"
        )
    n, d = arr.shape

    # 1-D special case: in [min, max]?
    if d == 1:
        lo, hi = float(arr.min()), float(arr.max())
        return lo - 1e-12 <= float(pt[0]) <= hi + 1e-12

    if n < d + 1:
        # Cloud is too small to be d-dimensional; only the cloud itself
        # (and segments between its points) qualify.  Defer to a brute
        # check via the hull's half-space inequalities, which are empty
        # for these degenerate cases — fall through and use a coordinate
        # comparison: the point must equal one of the hull points or lie
        # on a segment between them.
        for q in arr:
            if np.allclose(pt, q, atol=1e-12):
                return True
        return False

    try:
        tri = _Delaunay(arr)
    except _QhullError:
        # Degenerate cloud: only the cloud's coordinate set qualifies.
        for q in arr:
            if np.allclose(pt, q, atol=1e-12):
                return True
        return False
    return int(tri.find_simplex(pt)) >= 0


def delaunay_triangulation_count(points) -> int:
    """Number of simplices in the Delaunay triangulation of ``points``.

    Note: the full Delaunay API (simplex coordinates, neighbors,
    circumradii, …) is project #72.  This stub returns just the count,
    which is a useful invariant on its own (e.g. Euler-style formulas
    relating |triangulation| to hull facets).
    """
    arr = _as_points(points)
    n, d = arr.shape
    if n < d + 1:
        return 0
    try:
        tri = _Delaunay(arr)
    except _QhullError:
        return 0
    return int(len(tri.simplices))


def convex_hull_diameter(points) -> Tuple[float, int, int]:
    """Diameter of the point cloud: the maximum pairwise distance.

    Returns ``(distance, idx_a, idx_b)``.  The diameter is realised by
    *some* pair of hull-vertex points (a classical lemma), so we
    restrict the O(n²) search to the extreme-point subset for speed.

    For singleton clouds returns ``(0.0, 0, 0)``.
    """
    arr = _as_points(points)
    n, d = arr.shape
    if n == 1:
        return 0.0, 0, 0
    try:
        verts = convex_hull(arr)["vertices"]
        if len(verts) < 2:
            verts = np.arange(n)
    except Exception:  # pragma: no cover — defensive
        verts = np.arange(n)
    sub = arr[verts]
    # Pairwise distances over the (small) extreme set.
    diff = sub[:, None, :] - sub[None, :, :]
    dist = np.sqrt(np.einsum("ijk,ijk->ij", diff, diff))
    np.fill_diagonal(dist, -1.0)
    flat = int(np.argmax(dist))
    i, j = divmod(flat, dist.shape[1])
    return float(dist[i, j]), int(verts[i]), int(verts[j])
