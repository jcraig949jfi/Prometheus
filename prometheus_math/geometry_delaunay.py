"""prometheus_math.geometry_delaunay — Delaunay triangulation and friends.

A first-class API for Delaunay tessellation in arbitrary dimension,
backed by scipy.spatial.Delaunay (qhull). Provides:

- delaunay_triangulation(points) — full triangulation as a dict.
- find_simplex(point, triangulation) — point location.
- circumcenter / circumradius — geometry of a single simplex.
- voronoi_neighbors — Voronoi adjacency derived from the Delaunay dual.
- delaunay_alpha_complex — alpha filtration (TDA).
- mesh_quality — angle and aspect-ratio statistics.
- barycentric_interpolate — linear interpolation on the Delaunay mesh.
- delaunay_2d_to_image — render a 2D scalar field as an image.

Sibling: pm.geometry.convex_hull (#71).

References:
- de Berg, Cheong, van Kreveld, Overmars, "Computational Geometry"
  (3rd ed.), Springer 2008, Chapter 9 (Delaunay triangulations).
- Edelsbrunner & Mucke, "Three-dimensional alpha shapes",
  ACM TOG 1994 — alpha complex definition.
- scipy.spatial.Delaunay docs (qhull binding).

Failure-mode notes:
- qhull raises QhullError for collinear / coplanar / duplicate-only
  inputs; this module wraps those as ValueError per the math-tdd
  edge-case contract.
- 'find_simplex' on NaN inputs returns -1 (scipy passes NaNs through
  qhull as 'outside', which we honor).
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Set

import numpy as np

try:
    from scipy.spatial import Delaunay as _SciDelaunay
    try:
        from scipy.spatial import QhullError  # scipy >= 1.8
    except ImportError:  # pragma: no cover
        from scipy.spatial.qhull import QhullError  # legacy fallback
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "prometheus_math.geometry_delaunay requires scipy>=1.6"
    ) from exc


__all__ = [
    "delaunay_triangulation",
    "find_simplex",
    "circumcenter",
    "circumradius",
    "voronoi_neighbors",
    "delaunay_alpha_complex",
    "mesh_quality",
    "barycentric_interpolate",
    "delaunay_2d_to_image",
]


# ---------------------------------------------------------------------------
# Core triangulation
# ---------------------------------------------------------------------------


def _as_2d_array(points) -> np.ndarray:
    """Coerce input to a 2D float ndarray and validate the basic shape."""
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2:
        raise ValueError(
            f"points must be a 2D array of shape (n, d); got ndim={arr.ndim}"
        )
    if arr.size == 0 or arr.shape[0] == 0:
        raise ValueError("points must be a non-empty 2D array")
    return arr


def delaunay_triangulation(points) -> Dict[str, Any]:
    """Compute the Delaunay triangulation of ``points``.

    Parameters
    ----------
    points : array-like of shape (n, d)
        Input point coordinates. n >= d + 1 is required and the points
        must be in general position (not all collinear / coplanar).

    Returns
    -------
    dict with keys:
        simplices : ndarray (n_simplices, d+1) of int
            Vertex indices of each simplex.
        neighbors : ndarray (n_simplices, d+1) of int
            Index of the neighboring simplex across each face; -1 means
            the face is on the convex hull boundary.
        transform : ndarray (n_simplices, d+1, d)
            Affine transformation matrices used by scipy for fast point
            location and barycentric coordinates.
        points : ndarray (n, d)
            The input points (a copy).
        vertex_to_simplex : ndarray (n,) of int
            For each input point, the index of one simplex containing it.
        n_simplices : int
            Number of simplices.

    Raises
    ------
    ValueError
        If the input is empty, has fewer than d+1 points, or is
        degenerate (qhull failure).
    """
    pts = _as_2d_array(points)
    n, d = pts.shape
    if n < d + 1:
        raise ValueError(
            f"need at least d+1={d+1} points to triangulate in {d}D, got {n}"
        )
    try:
        scd = _SciDelaunay(pts)
    except QhullError as exc:
        raise ValueError(f"degenerate input for Delaunay: {exc}") from exc
    except ValueError as exc:
        # scipy itself can raise ValueError on certain shapes; rewrap.
        raise ValueError(f"degenerate input for Delaunay: {exc}") from exc

    return {
        "simplices": np.array(scd.simplices, dtype=int, copy=True),
        "neighbors": np.array(scd.neighbors, dtype=int, copy=True),
        "transform": np.array(scd.transform, copy=True),
        "points": np.array(pts, copy=True),
        "vertex_to_simplex": np.array(scd.vertex_to_simplex, dtype=int, copy=True),
        "n_simplices": int(scd.simplices.shape[0]),
        "_scipy": scd,  # internal handle for fast find_simplex
    }


def find_simplex(point, triangulation: Dict[str, Any]) -> int:
    """Index of the simplex containing ``point``; -1 if outside the hull.

    Parameters
    ----------
    point : array-like of shape (d,)
        Query point.
    triangulation : dict returned by :func:`delaunay_triangulation`.
    """
    q = np.asarray(point, dtype=float).reshape(1, -1)
    if not np.all(np.isfinite(q)):
        return -1
    scd = triangulation.get("_scipy")
    if scd is None:
        # Reconstruct from stored points (lossy but functional).
        scd = _SciDelaunay(triangulation["points"])
    idx = int(scd.find_simplex(q)[0])
    return idx


# ---------------------------------------------------------------------------
# Circumcenter / circumradius
# ---------------------------------------------------------------------------


def circumcenter(simplex_points) -> np.ndarray:
    """Circumcenter of a d-simplex given by its (d+1) vertices in d dims.

    Implementation: solve the linear system
        2 (p_i - p_0) . c = |p_i|^2 - |p_0|^2,    i = 1, ..., d
    for the center c. Works for any dimension d >= 1.
    """
    pts = np.asarray(simplex_points, dtype=float)
    if pts.ndim != 2:
        raise ValueError("simplex_points must be a 2D array of shape (d+1, d)")
    k, d = pts.shape
    if k != d + 1:
        raise ValueError(
            f"simplex with {k} vertices in {d}D is not a d-simplex (need d+1)"
        )
    A = 2.0 * (pts[1:] - pts[0])
    sq = np.sum(pts * pts, axis=1)
    b = sq[1:] - sq[0]
    try:
        c = np.linalg.solve(A, b)
    except np.linalg.LinAlgError as exc:
        raise ValueError(f"degenerate simplex for circumcenter: {exc}") from exc
    return c


def circumradius(simplex_points) -> float:
    """Circumradius: distance from the circumcenter to any vertex."""
    pts = np.asarray(simplex_points, dtype=float)
    c = circumcenter(pts)
    return float(np.linalg.norm(pts[0] - c))


# ---------------------------------------------------------------------------
# Voronoi neighbors via Delaunay dual
# ---------------------------------------------------------------------------


def voronoi_neighbors(triangulation: Dict[str, Any]) -> List[Set[int]]:
    """For each input point, the set of Voronoi-neighbor point indices.

    Two points are Voronoi neighbors iff they share an edge in the
    Delaunay graph; equivalently, iff they co-occur in some Delaunay
    simplex.
    """
    n = triangulation["points"].shape[0]
    nbrs: List[Set[int]] = [set() for _ in range(n)]
    for simplex in triangulation["simplices"]:
        verts = simplex.tolist()
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                a, b = int(verts[i]), int(verts[j])
                nbrs[a].add(b)
                nbrs[b].add(a)
    return nbrs


# ---------------------------------------------------------------------------
# Alpha complex
# ---------------------------------------------------------------------------


def delaunay_alpha_complex(points, alpha: float) -> List[List[int]]:
    """Subset of Delaunay simplices whose circumradius is <= alpha.

    The alpha complex is a standard tool in topological data analysis
    (Edelsbrunner & Mucke 1994).
    """
    tri = delaunay_triangulation(points)
    pts = tri["points"]
    out: List[List[int]] = []
    for simplex in tri["simplices"]:
        try:
            r = circumradius(pts[simplex])
        except ValueError:
            continue
        if r <= alpha:
            out.append([int(v) for v in simplex])
    return out


# ---------------------------------------------------------------------------
# Mesh quality
# ---------------------------------------------------------------------------


def _triangle_angles(p1, p2, p3) -> List[float]:
    """Three interior angles (radians) of triangle (p1, p2, p3)."""
    def ang(a, b, c):
        # angle at vertex a, between edges a->b and a->c
        u = b - a
        v = c - a
        cosv = float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v)))
        cosv = max(-1.0, min(1.0, cosv))
        return float(np.arccos(cosv))

    return [ang(p1, p2, p3), ang(p2, p1, p3), ang(p3, p1, p2)]


def mesh_quality(triangulation: Dict[str, Any]) -> Dict[str, Any]:
    """Quality stats for a 2D Delaunay mesh.

    Returns
    -------
    dict with keys:
        min_angle : float (radians) — global minimum angle.
        max_angle : float (radians) — global maximum angle.
        aspect_ratios : list[float] — circumradius / inradius per triangle.
        angles_per_simplex : list[list[float]] — three angles per triangle.

    Raises
    ------
    ValueError
        If the mesh is not 2D.
    """
    pts = triangulation["points"]
    if pts.shape[1] != 2:
        raise ValueError(
            "mesh_quality currently supports 2D triangulations only"
        )
    angles_per: List[List[float]] = []
    aspect: List[float] = []
    for simplex in triangulation["simplices"]:
        a, b, c = pts[simplex]
        angles = _triangle_angles(a, b, c)
        angles_per.append(angles)
        # aspect ratio = R / r
        ab = float(np.linalg.norm(a - b))
        bc = float(np.linalg.norm(b - c))
        ca = float(np.linalg.norm(c - a))
        s = 0.5 * (ab + bc + ca)
        area = max(0.0, s * (s - ab) * (s - bc) * (s - ca)) ** 0.5
        if area > 0:
            r_in = area / s
            R = circumradius(np.array([a, b, c]))
            aspect.append(R / r_in)
        else:
            aspect.append(float("inf"))
    flat = [x for row in angles_per for x in row]
    return {
        "min_angle": min(flat) if flat else 0.0,
        "max_angle": max(flat) if flat else 0.0,
        "aspect_ratios": aspect,
        "angles_per_simplex": angles_per,
    }


# ---------------------------------------------------------------------------
# Barycentric interpolation
# ---------------------------------------------------------------------------


def barycentric_interpolate(
    triangulation: Dict[str, Any],
    values: Sequence[float],
    query_point,
) -> float:
    """Linear interpolation of ``values`` at ``query_point`` using the
    Delaunay simplex barycentric coordinates.

    Returns NaN if ``query_point`` is outside the convex hull.
    """
    vals = np.asarray(values, dtype=float)
    pts = triangulation["points"]
    if vals.shape[0] != pts.shape[0]:
        raise ValueError(
            f"values length {vals.shape[0]} != number of points {pts.shape[0]}"
        )
    q = np.asarray(query_point, dtype=float)
    idx = find_simplex(q, triangulation)
    if idx < 0:
        return float("nan")
    simplex = triangulation["simplices"][idx]
    transform = triangulation["transform"][idx]
    d = pts.shape[1]
    # scipy convention: bary[:d] = transform[:d, :d] @ (q - transform[d, :])
    delta = q - transform[d]
    bary = transform[:d] @ delta
    last = 1.0 - bary.sum()
    bary_full = np.concatenate([bary, [last]])
    return float(np.dot(bary_full, vals[simplex]))


# ---------------------------------------------------------------------------
# 2D field rasterization
# ---------------------------------------------------------------------------


def delaunay_2d_to_image(points, values, resolution: int = 64) -> np.ndarray:
    """Render the 2D scalar field defined by Delaunay-interpolated
    ``values`` as a (resolution, resolution) image over the bounding
    box of ``points``.

    Pixels outside the convex hull are set to NaN.
    """
    pts = _as_2d_array(points)
    if pts.shape[1] != 2:
        raise ValueError("delaunay_2d_to_image requires 2D points")
    if resolution < 2:
        raise ValueError("resolution must be >= 2")
    tri = delaunay_triangulation(pts)
    xs = np.linspace(pts[:, 0].min(), pts[:, 0].max(), resolution)
    ys = np.linspace(pts[:, 1].min(), pts[:, 1].max(), resolution)
    img = np.full((resolution, resolution), np.nan, dtype=float)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            v = barycentric_interpolate(tri, values, np.array([x, y]))
            img[j, i] = v
    return img
