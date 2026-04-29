"""prometheus_math.geometry_voronoi — Voronoi diagrams and friends.

A first-class API for Voronoi tessellation in 2D (with bbox clipping for
unbounded cells), backed by scipy.spatial.Voronoi (qhull) and shapely
for polygon clipping. Provides:

- voronoi_diagram(points) — full diagram as a dict.
- voronoi_cell(idx, points) — bounded polygon vertices, or None if the
  cell is unbounded.
- voronoi_cell_bounded(idx, points, bbox=None) — polygon clipped to bbox.
- is_unbounded_cell(idx, voronoi) — bool predicate.
- voronoi_neighbors(idx, voronoi) — neighbor cell indices via duality.
- voronoi_cell_area(idx, points, bbox=None) — cell area, with clipping
  for unbounded cells when a bbox is supplied.
- lloyd_relaxation(points, n_iter, bbox) — apply Lloyd's algorithm.
- centroidal_voronoi_tessellation(n_points, bbox, n_iter, seed) — random
  initialization + Lloyd to produce a CVT.
- delaunay_dual_voronoi(points) — both Delaunay and Voronoi together.

Sibling: pm.geometry_delaunay (#72), pm.geometry_convex_hull (#71).

References:
- de Berg, Cheong, van Kreveld, Overmars, "Computational Geometry"
  (3rd ed.), Springer 2008, Chapter 7 (Voronoi diagrams).
- Aurenhammer & Klein, "Voronoi diagrams" (Handbook of Computational
  Geometry, 2000).
- Du, Faber & Gunzburger, "Centroidal Voronoi tessellations:
  applications and algorithms", SIAM Review 41(4), 1999.
- scipy.spatial.Voronoi docs (qhull binding).

Failure-mode notes:
- qhull raises QhullError on degenerate input (collinear points in 2D);
  this module wraps as ValueError per the math-tdd edge-case contract,
  with explicit handling for n=1 and n=2 generators (below qhull's
  d+1 minimum) and for all-collinear inputs (we synthesize the diagram
  via perpendicular bisectors).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    from scipy.spatial import Voronoi as _SciVoronoi
    try:
        from scipy.spatial import QhullError  # scipy >= 1.8
    except ImportError:  # pragma: no cover
        from scipy.spatial.qhull import QhullError  # legacy fallback
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "prometheus_math.geometry_voronoi requires scipy>=1.6"
    ) from exc

try:
    from shapely.geometry import Polygon as _ShapelyPolygon
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "prometheus_math.geometry_voronoi requires shapely>=2.0"
    ) from exc


__all__ = [
    "voronoi_diagram",
    "voronoi_cell",
    "voronoi_cell_bounded",
    "is_unbounded_cell",
    "voronoi_neighbors",
    "voronoi_cell_area",
    "lloyd_relaxation",
    "centroidal_voronoi_tessellation",
    "delaunay_dual_voronoi",
]


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def _as_2d_array(points) -> np.ndarray:
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2:
        raise ValueError(
            f"points must be a 2D array of shape (n, d); got ndim={arr.ndim}"
        )
    if arr.size == 0 or arr.shape[0] == 0:
        raise ValueError("points must be a non-empty 2D array")
    return arr


def _check_bbox(bbox) -> Tuple[float, float, float, float]:
    if bbox is None:
        raise ValueError("bbox is required")
    if len(bbox) != 4:
        raise ValueError("bbox must be (xmin, ymin, xmax, ymax)")
    xmin, ymin, xmax, ymax = (float(b) for b in bbox)
    if not (xmin < xmax and ymin < ymax):
        raise ValueError(
            f"bbox must satisfy xmin<xmax and ymin<ymax; got {bbox}"
        )
    return xmin, ymin, xmax, ymax


def _bbox_polygon(bbox) -> _ShapelyPolygon:
    xmin, ymin, xmax, ymax = _check_bbox(bbox)
    return _ShapelyPolygon(
        [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    )


# ---------------------------------------------------------------------------
# Core diagram
# ---------------------------------------------------------------------------


def _is_collinear_2d(pts: np.ndarray) -> bool:
    if pts.shape[0] < 3:
        return True
    return np.linalg.matrix_rank(pts - pts[0], tol=1e-12) < 2


def _synthesize_collinear_voronoi(pts: np.ndarray) -> Dict[str, Any]:
    """Hand-roll a Voronoi-like dict for collinear / sub-d+1 input.

    qhull rejects these degenerate cases. We emit ridges between
    consecutive points along the line, and no finite vertices. Cells
    are all unbounded.
    """
    n = pts.shape[0]
    if n == 1:
        return {
            "points": pts.copy(),
            "vertices": np.empty((0, pts.shape[1])),
            "ridge_points": np.empty((0, 2), dtype=int),
            "ridge_vertices": [],
            "regions": [[]],
            "point_region": np.array([0], dtype=int),
        }
    # Sort by projection along the line direction.
    if pts.shape[0] >= 2:
        v = pts[-1] - pts[0]
        nv = np.linalg.norm(v)
        if nv < 1e-15:
            # All points equal — treat as singleton.
            return _synthesize_collinear_voronoi(pts[:1])
        u = v / nv
        proj = (pts - pts[0]) @ u
        order = np.argsort(proj)
        ridges = []
        for k in range(n - 1):
            i, j = int(order[k]), int(order[k + 1])
            ridges.append([i, j])
        return {
            "points": pts.copy(),
            "vertices": np.empty((0, pts.shape[1])),
            "ridge_points": np.array(ridges, dtype=int),
            "ridge_vertices": [[-1, -1] for _ in ridges],
            "regions": [[] for _ in range(n)],
            "point_region": np.arange(n, dtype=int),
        }
    return {
        "points": pts.copy(),
        "vertices": np.empty((0, pts.shape[1])),
        "ridge_points": np.empty((0, 2), dtype=int),
        "ridge_vertices": [],
        "regions": [[] for _ in range(n)],
        "point_region": np.arange(n, dtype=int),
    }


def voronoi_diagram(points) -> Dict[str, Any]:
    """Compute the Voronoi diagram of ``points``.

    Parameters
    ----------
    points : array-like of shape (n, d)
        Input generator coordinates.

    Returns
    -------
    dict with keys:
        points : ndarray (n, d) — input generators.
        vertices : ndarray (m, d) — finite Voronoi vertices.
        ridge_points : ndarray (k, 2) of int — generator pairs sharing
            each ridge.
        ridge_vertices : list[list[int]] — Voronoi-vertex indices for
            each ridge; -1 indicates a vertex at infinity.
        regions : list[list[int]] — for each region, the Voronoi-vertex
            indices forming its boundary; -1 entries mean the region is
            unbounded.
        point_region : ndarray (n,) of int — index into ``regions`` for
            each input generator.

    Raises
    ------
    ValueError
        On empty input. Degenerate inputs (single point, two points,
        all-collinear) are handled gracefully via a synthesized
        Voronoi-like dict.
    """
    pts = _as_2d_array(points)
    n, d = pts.shape

    # Below qhull's hard floor of d+1 generators, or all-collinear in 2D:
    if n <= d or (d == 2 and _is_collinear_2d(pts)):
        out = _synthesize_collinear_voronoi(pts)
        out["_scipy"] = None
        return out

    try:
        scv = _SciVoronoi(pts)
    except QhullError as exc:
        # Fallback: try the synthesized form.
        if d == 2 and _is_collinear_2d(pts):
            out = _synthesize_collinear_voronoi(pts)
            out["_scipy"] = None
            return out
        raise ValueError(f"degenerate input for Voronoi: {exc}") from exc

    return {
        "points": np.array(pts, copy=True),
        "vertices": np.array(scv.vertices, copy=True),
        "ridge_points": np.array(scv.ridge_points, dtype=int, copy=True),
        "ridge_vertices": [list(rv) for rv in scv.ridge_vertices],
        "regions": [list(r) for r in scv.regions],
        "point_region": np.array(scv.point_region, dtype=int, copy=True),
        "_scipy": scv,
    }


# ---------------------------------------------------------------------------
# Cell predicates / extraction
# ---------------------------------------------------------------------------


def is_unbounded_cell(idx: int, voronoi: Dict[str, Any]) -> bool:
    """True iff cell ``idx`` is unbounded (touches infinity)."""
    region_idx = int(voronoi["point_region"][idx])
    region = voronoi["regions"][region_idx]
    if not region:  # empty -> unbounded by convention (n=1 case).
        return True
    return any(v == -1 for v in region)


def voronoi_cell(
    idx: int, points
) -> Optional[List[Tuple[float, ...]]]:
    """Polygon vertices of cell ``idx``; ``None`` if unbounded.

    Returned vertices are in the order scipy / qhull provides them
    (counter-clockwise around the cell in 2D).
    """
    pts = _as_2d_array(points)
    vd = voronoi_diagram(pts)
    if is_unbounded_cell(idx, vd):
        return None
    region_idx = int(vd["point_region"][idx])
    region = vd["regions"][region_idx]
    verts = vd["vertices"]
    return [tuple(verts[v]) for v in region]


def voronoi_cell_bounded(
    idx: int,
    points,
    bbox: Optional[Tuple[float, float, float, float]] = None,
) -> List[Tuple[float, ...]]:
    """Polygon vertices of cell ``idx``, clipped to ``bbox`` if needed.

    For finite cells, returns the cell vertices intersected with the
    bbox (or the cell itself if bbox is None). For unbounded cells,
    requires ``bbox``: clips the cell by reconstructing it as the
    half-plane intersection inside the bbox.

    Raises
    ------
    ValueError
        If bbox is required but not supplied; if bbox does not contain
        all generators.
    """
    pts = _as_2d_array(points)
    vd = voronoi_diagram(pts)

    if bbox is not None:
        xmin, ymin, xmax, ymax = _check_bbox(bbox)
        # Validate generators inside bbox.
        if (
            (pts[:, 0] < xmin - 1e-12).any()
            or (pts[:, 0] > xmax + 1e-12).any()
            or (pts[:, 1] < ymin - 1e-12).any()
            or (pts[:, 1] > ymax + 1e-12).any()
        ):
            raise ValueError("bbox does not contain all generators")
        bbox_poly = _bbox_polygon(bbox)
    else:
        if is_unbounded_cell(idx, vd):
            raise ValueError(
                "bbox is required to clip an unbounded cell; got bbox=None"
            )
        bbox_poly = None

    if not is_unbounded_cell(idx, vd):
        region_idx = int(vd["point_region"][idx])
        verts = vd["vertices"]
        poly_pts = [verts[v] for v in vd["regions"][region_idx]]
        poly = _ShapelyPolygon(poly_pts)
        if bbox_poly is not None:
            poly = poly.intersection(bbox_poly)
        if poly.is_empty:
            return []
        return _polygon_to_vertices(poly)

    # Unbounded cell: build it as the intersection of half-planes
    # implied by the perpendicular bisectors with each Voronoi neighbor,
    # clipped to bbox.
    poly = bbox_poly
    g = pts[idx]
    nbrs = voronoi_neighbors(idx, vd)
    for j in nbrs:
        h = pts[j]
        # Half-plane: (x - midpoint) . (h - g) <= 0
        mid = 0.5 * (g + h)
        n = h - g
        # Clip the polygon by this half-plane.
        poly = _clip_halfplane(poly, mid, n)
        if poly.is_empty:
            return []
    return _polygon_to_vertices(poly)


def _polygon_to_vertices(poly) -> List[Tuple[float, ...]]:
    if poly.is_empty:
        return []
    if poly.geom_type == "Polygon":
        coords = list(poly.exterior.coords)
        # Drop the closing repeated vertex.
        if coords and coords[0] == coords[-1]:
            coords = coords[:-1]
        return [(float(x), float(y)) for x, y in coords]
    if poly.geom_type == "MultiPolygon":
        # Concatenate polygons (rare; happens when bbox carves the cell).
        out: List[Tuple[float, ...]] = []
        for p in poly.geoms:
            out.extend(_polygon_to_vertices(p))
        return out
    return []


def _clip_halfplane(
    poly: _ShapelyPolygon,
    point: np.ndarray,
    normal: np.ndarray,
) -> _ShapelyPolygon:
    """Clip ``poly`` to the half-plane ``{x : (x - point) . normal <= 0}``.

    Implemented as the intersection of ``poly`` with a large rectangle
    that covers exactly that half-plane (extending from the boundary
    line opposite to ``normal``).
    """
    if poly.is_empty:
        return poly
    minx, miny, maxx, maxy = poly.bounds
    diag = max(maxx - minx, maxy - miny) * 10.0 + 1.0
    n = normal / max(np.linalg.norm(normal), 1e-15)
    t = np.array([-n[1], n[0]])  # tangent direction along the boundary
    # Two points on the boundary line, far apart along ``t``.
    p0 = np.asarray(point, dtype=float) - t * diag
    p1 = np.asarray(point, dtype=float) + t * diag
    # Push them into the half-plane (opposite to ``n``) by ``2*diag``.
    p2 = p1 - n * 2 * diag
    p3 = p0 - n * 2 * diag
    half = _ShapelyPolygon([tuple(p0), tuple(p1), tuple(p2), tuple(p3)])
    return poly.intersection(half)


def voronoi_neighbors(idx: int, voronoi: Dict[str, Any]) -> List[int]:
    """Indices of cells sharing a ridge with cell ``idx``."""
    out: List[int] = []
    rp = voronoi["ridge_points"]
    for a, b in rp.tolist():
        if a == idx:
            out.append(int(b))
        elif b == idx:
            out.append(int(a))
    return sorted(set(out))


# ---------------------------------------------------------------------------
# Areas
# ---------------------------------------------------------------------------


def _polygon_area_shoelace(verts: List[Tuple[float, float]]) -> float:
    if len(verts) < 3:
        return 0.0
    arr = np.asarray(verts, dtype=float)
    x, y = arr[:, 0], arr[:, 1]
    return 0.5 * float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def voronoi_cell_area(
    idx: int,
    points,
    bbox: Optional[Tuple[float, float, float, float]] = None,
) -> float:
    """Area of cell ``idx`` (clipped to bbox if supplied).

    For unbounded cells without a bbox, returns ``inf``.
    """
    pts = _as_2d_array(points)
    if bbox is None:
        cell = voronoi_cell(idx, pts)
        if cell is None:
            return float("inf")
        return _polygon_area_shoelace([(c[0], c[1]) for c in cell])
    cell = voronoi_cell_bounded(idx, pts, bbox=bbox)
    if not cell:
        return 0.0
    return _polygon_area_shoelace([(c[0], c[1]) for c in cell])


# ---------------------------------------------------------------------------
# Lloyd relaxation / CVT
# ---------------------------------------------------------------------------


def _polygon_centroid(verts: List[Tuple[float, float]]) -> np.ndarray:
    """Centroid of a simple polygon via the standard area-weighted formula."""
    arr = np.asarray(verts, dtype=float)
    if arr.shape[0] < 3:
        return arr.mean(axis=0)
    x, y = arr[:, 0], arr[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y1 - x1 * y
    A = 0.5 * cross.sum()
    if abs(A) < 1e-15:
        return arr.mean(axis=0)
    cx = ((x + x1) * cross).sum() / (6.0 * A)
    cy = ((y + y1) * cross).sum() / (6.0 * A)
    return np.array([cx, cy])


def lloyd_relaxation(
    points,
    n_iter: int = 10,
    bbox: Optional[Tuple[float, float, float, float]] = None,
) -> np.ndarray:
    """Apply Lloyd's algorithm ``n_iter`` times.

    Each iteration replaces every generator with the centroid of its
    (clipped) Voronoi cell. Requires ``bbox`` for boundary clipping.
    """
    pts = _as_2d_array(points).copy()
    if bbox is None:
        # Use the bounding box of the input as default.
        xmin, ymin = pts.min(axis=0)
        xmax, ymax = pts.max(axis=0)
        # Pad by 10% to avoid coincident generators on boundary.
        dx = (xmax - xmin) * 0.1 + 1.0
        dy = (ymax - ymin) * 0.1 + 1.0
        bbox = (xmin - dx, ymin - dy, xmax + dx, ymax + dy)
    _check_bbox(bbox)

    for _ in range(int(n_iter)):
        new_pts = pts.copy()
        for i in range(pts.shape[0]):
            cell = voronoi_cell_bounded(i, pts, bbox=bbox)
            if not cell:
                continue
            new_pts[i] = _polygon_centroid(cell)
        pts = new_pts
    return pts


def centroidal_voronoi_tessellation(
    n_points: int,
    bbox: Tuple[float, float, float, float],
    n_iter: int = 20,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate a CVT inside ``bbox`` by random init + Lloyd relaxation."""
    if n_points <= 0:
        raise ValueError(f"n_points must be > 0; got {n_points}")
    xmin, ymin, xmax, ymax = _check_bbox(bbox)
    rng = np.random.default_rng(seed)
    pts = np.column_stack(
        [
            rng.uniform(xmin, xmax, size=n_points),
            rng.uniform(ymin, ymax, size=n_points),
        ]
    )
    return lloyd_relaxation(pts, n_iter=n_iter, bbox=bbox)


# ---------------------------------------------------------------------------
# Joint Delaunay-Voronoi
# ---------------------------------------------------------------------------


def delaunay_dual_voronoi(points) -> Dict[str, Any]:
    """Compute Delaunay and Voronoi simultaneously.

    Returns a dict with keys ``delaunay`` (the Delaunay dict from
    :mod:`prometheus_math.geometry_delaunay`) and ``voronoi`` (the
    Voronoi dict). The two are the dual of each other: each Delaunay
    simplex's circumcenter is a Voronoi vertex.
    """
    from .geometry_delaunay import delaunay_triangulation

    return {
        "delaunay": delaunay_triangulation(points),
        "voronoi": voronoi_diagram(points),
    }
