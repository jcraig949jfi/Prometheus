"""Tests for prometheus_math.geometry_voronoi.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority (5+):
    - 3 collinear points along x-axis -> 2 perpendicular bisectors as ridges.
    - 4 corners of unit square -> 1 Voronoi vertex at center, 4 ridges.
    - voronoi_cell of center point in 5-point pattern (square + center)
      -> bounded square cell.
    - 4 generators at corners of [0,1]^2 with bbox clipping
      -> each cell has area 1/4 of bbox.
    - Equilateral triangle generators -> cells meet at the centroid.

- Property (5+):
    - #cells == #input points.
    - voronoi_neighbors agrees with Delaunay edges (duality).
    - For convex bbox clipping, total clipped area == bbox area.
    - Lloyd relaxation is non-divergent (energy non-increasing).
    - voronoi_neighbors is symmetric.

- Edge (5+):
    - Empty input -> ValueError.
    - Single point -> 1 unbounded cell covering everything.
    - 2 points -> 1 ridge (perpendicular bisector).
    - All collinear -> degenerate; handled gracefully.
    - bbox doesn't contain all generators -> ValueError.

- Composition (4+):
    - voronoi_neighbors(idx) ⊆ delaunay_neighbors of point idx (duality).
    - lloyd_relaxation converges to a CVT (centroids ≈ generators).
    - Sum of clipped voronoi_cell_area equals bbox area.
    - delaunay_dual_voronoi pairing consistency.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.geometry_voronoi import (
    centroidal_voronoi_tessellation,
    delaunay_dual_voronoi,
    is_unbounded_cell,
    lloyd_relaxation,
    voronoi_cell,
    voronoi_cell_area,
    voronoi_cell_bounded,
    voronoi_diagram,
    voronoi_neighbors,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_authority_three_collinear_points_two_bisectors():
    """3 collinear points along the x-axis yield exactly 2 finite ridges
    (the perpendicular bisectors between consecutive points).

    Reference: Hand-computed. For points (0,0), (1,0), (2,0) the
    Voronoi ridges are the vertical lines x=1/2 and x=3/2; both are
    unbounded (rays). scipy.spatial.Voronoi returns 2 ridges between
    finite point pairs (0-1) and (1-2). The (0-2) pair shares no ridge
    because point 1 lies between them.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    vd = voronoi_diagram(pts)
    rp = vd["ridge_points"]
    pairs = sorted(tuple(sorted(p)) for p in rp.tolist())
    assert pairs == [(0, 1), (1, 2)]


def test_authority_unit_square_one_vertex_at_center():
    """Voronoi of the unit-square corners has exactly one Voronoi vertex
    at (0.5, 0.5) and 4 ridges (one per pair of adjacent corners +
    diagonals; here all 4 corners share the central vertex).

    Reference: Hand-computed. The unit square's Voronoi diagram has
    the four perpendicular bisectors meeting at the centroid (0.5, 0.5).
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    vd = voronoi_diagram(pts)
    assert vd["vertices"].shape == (1, 2)
    assert np.allclose(vd["vertices"][0], np.array([0.5, 0.5]), atol=1e-10)
    assert vd["ridge_points"].shape[0] == 4


def test_authority_center_of_5point_pattern_is_bounded_diamond():
    """For the unit square + center pattern, the cell of the center
    point is the bounded diamond with vertices at the four edge
    midpoints (0,0.5), (0.5,0), (1,0.5), (0.5,1).

    Reference: Hand-computed. The perpendicular bisector between the
    center (0.5, 0.5) and the corner (0,0) is the line x + y = 0.5.
    Symmetrically the four bisectors form a diamond whose vertices lie
    at the edge midpoints of the unit square; the cell area is 0.5
    (= 1/2 * d1 * d2 with diagonals = 1).
    """
    pts = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]]
    )
    cell = voronoi_cell(4, pts)
    assert cell is not None
    arr = np.array(cell)
    # Diamond with vertices at edge midpoints — area 0.5.
    expected_verts = {(0.0, 0.5), (0.5, 0.0), (1.0, 0.5), (0.5, 1.0)}
    actual = {(round(x, 6), round(y, 6)) for x, y in arr}
    assert actual == expected_verts


def test_authority_corner_generators_clipped_to_quarter_bbox():
    """4 generators at corners of unit square + bbox=[0,1]^2:
    each cell has area 1/4.

    Reference: Hand-computed. The Voronoi partition of [0,1]^2 by its
    four corners is exactly the four sub-squares of side 1/2.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    bbox = (0.0, 0.0, 1.0, 1.0)
    for i in range(4):
        a = voronoi_cell_area(i, pts, bbox=bbox)
        assert math.isclose(a, 0.25, rel_tol=1e-9, abs_tol=1e-9)


def test_authority_equilateral_triangle_meets_at_centroid():
    """The 3 cells of an equilateral triangle pattern meet at the
    centroid (= circumcenter for equilateral triangles).

    Reference: Hand-computed. For vertices (0,0), (1,0), (0.5, sqrt(3)/2)
    the centroid is (0.5, sqrt(3)/6). Voronoi has exactly 1 finite vertex
    located at the circumcenter.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, math.sqrt(3) / 2.0]])
    vd = voronoi_diagram(pts)
    assert vd["vertices"].shape == (1, 2)
    expected = np.array([0.5, math.sqrt(3) / 6.0])
    assert np.allclose(vd["vertices"][0], expected, atol=1e-10)


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


def _point_cloud_2d(min_size=4, max_size=10):
    return st.lists(
        st.tuples(
            st.integers(min_value=-20, max_value=20),
            st.integers(min_value=-20, max_value=20),
        ),
        min_size=min_size,
        max_size=max_size,
        unique=True,
    )


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(_point_cloud_2d(min_size=4, max_size=10))
def test_property_cell_count_equals_point_count(raw_pts):
    """Number of Voronoi cells == number of input points."""
    pts = np.array(raw_pts, dtype=float)
    if np.linalg.matrix_rank(pts - pts[0]) < 2:
        return
    try:
        vd = voronoi_diagram(pts)
    except ValueError:
        return
    assert len(vd["point_region"]) == pts.shape[0]


def test_property_neighbors_match_delaunay_edges():
    """voronoi_neighbors agrees with Delaunay edges (duality).
    For points in general position (no four cocircular), two generators
    are Voronoi neighbors iff they share a Delaunay edge.
    """
    from prometheus_math.geometry_delaunay import (
        delaunay_triangulation,
        voronoi_neighbors as delaunay_voronoi_neighbors,
    )

    rng = np.random.default_rng(123)
    pts = rng.uniform(0.0, 1.0, size=(12, 2))  # general position
    vd = voronoi_diagram(pts)
    tri = delaunay_triangulation(pts)
    delaunay_nbrs = delaunay_voronoi_neighbors(tri)
    for i in range(pts.shape[0]):
        ours = set(voronoi_neighbors(i, vd))
        assert ours == delaunay_nbrs[i], (
            f"mismatch at point {i}: voronoi={ours} delaunay={delaunay_nbrs[i]}"
        )


def test_property_clipped_area_covers_bbox():
    """For convex bbox clipping, total area == bbox area."""
    rng = np.random.default_rng(42)
    pts = rng.uniform(0.0, 1.0, size=(8, 2))
    bbox = (0.0, 0.0, 1.0, 1.0)
    total = 0.0
    for i in range(pts.shape[0]):
        total += voronoi_cell_area(i, pts, bbox=bbox)
    assert math.isclose(total, 1.0, rel_tol=1e-7, abs_tol=1e-7)


def test_property_lloyd_relaxation_energy_non_increasing():
    """Lloyd's algorithm strictly does not increase the CVT energy
    (sum_i integral_{V_i} |x - g_i|^2 dx). Empirically the energy
    monotone-decreases until fixpoint.
    """
    rng = np.random.default_rng(0)
    pts = rng.uniform(0.0, 1.0, size=(12, 2))
    bbox = (0.0, 0.0, 1.0, 1.0)
    energies = []
    cur = pts.copy()
    for _ in range(5):
        # Approximate energy via centroid-distance on each cell.
        e = 0.0
        for i in range(cur.shape[0]):
            cell = voronoi_cell_bounded(i, cur, bbox=bbox)
            if not cell:
                continue
            arr = np.array(cell)
            centroid = arr.mean(axis=0)
            e += float(np.sum((cur[i] - centroid) ** 2))
        energies.append(e)
        cur = lloyd_relaxation(cur, n_iter=1, bbox=bbox)
    # Each next energy should be <= previous + small slack.
    for i in range(1, len(energies)):
        assert energies[i] <= energies[i - 1] + 1e-9


def test_property_neighbors_symmetric():
    """voronoi_neighbors is symmetric: j in N(i) <=> i in N(j)."""
    rng = np.random.default_rng(7)
    pts = rng.uniform(0.0, 1.0, size=(10, 2))
    vd = voronoi_diagram(pts)
    for i in range(pts.shape[0]):
        for j in voronoi_neighbors(i, vd):
            assert i in voronoi_neighbors(j, vd)


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_edge_empty_input_raises():
    """Edge: empty input -> ValueError."""
    with pytest.raises(ValueError):
        voronoi_diagram(np.empty((0, 2)))


def test_edge_single_point_one_unbounded_cell():
    """Edge: single point -> 1 cell that covers everything (unbounded).

    scipy.spatial.Voronoi requires >= d+1 input points, but our
    facade should handle the degenerate case.
    """
    pts = np.array([[0.5, 0.5]])
    vd = voronoi_diagram(pts)
    assert len(vd["point_region"]) == 1
    # The single cell is fully unbounded.
    assert is_unbounded_cell(0, vd)
    # voronoi_cell returns None for unbounded cell.
    assert voronoi_cell(0, pts) is None


def test_edge_two_points_one_ridge():
    """Edge: 2 points -> exactly 1 ridge (the perpendicular bisector)."""
    pts = np.array([[0.0, 0.0], [2.0, 0.0]])
    vd = voronoi_diagram(pts)
    assert vd["ridge_points"].shape[0] == 1
    pair = sorted(vd["ridge_points"][0].tolist())
    assert pair == [0, 1]


def test_edge_all_collinear_handled():
    """Edge: all collinear in 2D -> handled gracefully.
    The ridges are the perpendicular bisectors between consecutive
    points; no Voronoi vertices in 2D.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])
    vd = voronoi_diagram(pts)
    # 4 collinear -> 3 ridges between consecutive pairs.
    assert vd["ridge_points"].shape[0] == 3


def test_edge_bbox_does_not_contain_generators_raises():
    """Edge: bbox that doesn't contain all generators -> ValueError."""
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    bbox = (0.25, 0.25, 0.75, 0.75)  # excludes the corners
    with pytest.raises(ValueError):
        voronoi_cell_bounded(0, pts, bbox=bbox)


def test_edge_centroidal_invalid_bbox_raises():
    """Edge: CVT with invalid bbox (xmin >= xmax) -> ValueError."""
    with pytest.raises(ValueError):
        centroidal_voronoi_tessellation(8, bbox=(1.0, 0.0, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_voronoi_neighbors_subset_of_delaunay():
    """Composition: voronoi_neighbors(i) ⊆ delaunay_neighbors(i).

    Chains pm.geometry_voronoi.voronoi_neighbors with
    pm.geometry_delaunay.voronoi_neighbors (Delaunay-derived).
    """
    from prometheus_math.geometry_delaunay import (
        delaunay_triangulation,
        voronoi_neighbors as delaunay_voronoi_neighbors,
    )

    rng = np.random.default_rng(3)
    pts = rng.uniform(0.0, 1.0, size=(15, 2))
    vd = voronoi_diagram(pts)
    tri = delaunay_triangulation(pts)
    dnbrs = delaunay_voronoi_neighbors(tri)
    for i in range(pts.shape[0]):
        vnbrs = set(voronoi_neighbors(i, vd))
        assert vnbrs.issubset(dnbrs[i])


def test_composition_lloyd_converges_to_cvt():
    """Composition: lloyd_relaxation converges to a CVT.
    After enough iterations the generators coincide with the centroids
    of their Voronoi cells (within tolerance).
    """
    rng = np.random.default_rng(11)
    pts = rng.uniform(0.0, 1.0, size=(10, 2))
    bbox = (0.0, 0.0, 1.0, 1.0)
    relaxed = lloyd_relaxation(pts, n_iter=80, bbox=bbox)
    # Use the area-weighted centroid (matching what lloyd_relaxation uses
    # internally) for the CVT fixpoint check.
    from prometheus_math.geometry_voronoi import _polygon_centroid

    diffs = []
    for i in range(relaxed.shape[0]):
        cell = voronoi_cell_bounded(i, relaxed, bbox=bbox)
        if not cell:
            continue
        centroid = _polygon_centroid(cell)
        diffs.append(float(np.linalg.norm(relaxed[i] - centroid)))
    # CVT fixpoint: centroids ≈ generators (area-weighted).
    assert max(diffs) < 1e-2


def test_composition_total_cell_area_equals_bbox():
    """Composition: sum_i voronoi_cell_area(i, ..., bbox) == bbox area."""
    rng = np.random.default_rng(5)
    pts = rng.uniform(0.0, 1.0, size=(7, 2))
    bbox = (0.0, 0.0, 1.0, 1.0)
    total = sum(voronoi_cell_area(i, pts, bbox=bbox) for i in range(pts.shape[0]))
    assert math.isclose(total, 1.0, rel_tol=1e-7, abs_tol=1e-7)


def test_composition_delaunay_dual_voronoi_consistency():
    """Composition: delaunay_dual_voronoi consistency.
    Each Voronoi vertex corresponds to a Delaunay simplex's circumcenter,
    and the voronoi.vertices count equals the delaunay simplex count for
    points in general position.
    """
    pts = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]]
    )
    pair = delaunay_dual_voronoi(pts)
    n_simplices = pair["delaunay"]["n_simplices"]
    n_v_vertices = pair["voronoi"]["vertices"].shape[0]
    assert n_v_vertices == n_simplices
    # Spot-check: each voronoi vertex equals a delaunay simplex circumcenter.
    from prometheus_math.geometry_delaunay import circumcenter

    sim = pair["delaunay"]["simplices"]
    centers = np.array([circumcenter(pts[s]) for s in sim])
    # Order can differ; match by nearest neighbor.
    v_vertices = pair["voronoi"]["vertices"]
    for c in centers:
        d = np.min(np.linalg.norm(v_vertices - c, axis=1))
        assert d < 1e-9
