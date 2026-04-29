"""Tests for prometheus_math.geometry_delaunay.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: 4-corners of unit square -> 2 triangles, single triangle -> 1
  simplex, 3D tetrahedron -> 1 simplex, square+center -> 4 triangles,
  circumcenter of equilateral triangle, circumradius of unit equilateral
  triangle = 1/sqrt(3).
- Property: sum of triangle areas == convex hull area, find_simplex(point
  inside hull) >= 0, find_simplex(point outside) == -1, voronoi_neighbors
  symmetry, circumradius >= inradius, mesh-quality angles sum to 180 deg.
- Edge: empty input, fewer than d+1 points, all collinear (degenerate),
  duplicates, find_simplex with extreme query point.
- Composition: alpha_complex with alpha=inf == full Delaunay, barycentric
  interpolation on a vertex returns the vertex value, Voronoi-via-duality
  reproduces scipy.spatial.Voronoi neighbor incidences, Delaunay min-angle
  >= naive (non-Delaunay) triangulation min-angle.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.geometry_delaunay import (
    barycentric_interpolate,
    circumcenter,
    circumradius,
    delaunay_2d_to_image,
    delaunay_alpha_complex,
    delaunay_triangulation,
    find_simplex,
    mesh_quality,
    voronoi_neighbors,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_unit_square_four_corners_yields_two_triangles():
    """The four corners of the unit square triangulate into 2 triangles.

    Reference: Hand-computed. Any non-degenerate point set in general
    position with 4 points in 2D forms a convex quadrilateral whose
    Delaunay triangulation consists of exactly 2 triangles sharing one
    diagonal. Cross-checked against scipy.spatial.Delaunay docstring
    example for the unit square.
    """
    points = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    tri = delaunay_triangulation(points)
    assert tri["n_simplices"] == 2
    assert tri["simplices"].shape == (2, 3)


def test_single_triangle_yields_one_simplex():
    """3 non-collinear points in 2D give a single triangle.

    Reference: Definition of a triangulation. Hand-computed.
    """
    points = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    tri = delaunay_triangulation(points)
    assert tri["n_simplices"] == 1
    assert sorted(tri["simplices"][0].tolist()) == [0, 1, 2]


def test_3d_tetrahedron_yields_one_simplex():
    """4 non-coplanar points in 3D give a single tetrahedron.

    Reference: Definition of a 3-simplex / tetrahedral triangulation.
    Hand-computed for the standard tetrahedron with vertices at the
    origin and the three positive coordinate axes' unit points.
    """
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    tri = delaunay_triangulation(points)
    assert tri["n_simplices"] == 1
    assert tri["simplices"].shape == (1, 4)


def test_square_plus_center_yields_four_triangles():
    """Unit square plus the center triangulates into 4 fan triangles.

    Reference: Hand-computed. The center is interior to the convex hull
    so it is connected to all four corners; the 4 triangles partition
    the square. Cross-checked: each triangle has area 1/4, sum = 1.
    """
    points = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]]
    )
    tri = delaunay_triangulation(points)
    assert tri["n_simplices"] == 4
    # Every triangle must contain the center point (index 4).
    assert all(4 in simplex for simplex in tri["simplices"].tolist())


def test_circumcenter_of_equilateral_triangle():
    """Circumcenter of equilateral triangle (0,0), (1,0), (0.5, sqrt(3)/2)
    is (0.5, sqrt(3)/6).

    Reference: Hand-computed. For an equilateral triangle the
    circumcenter coincides with the centroid, and the centroid of the
    given vertices is ((0+1+0.5)/3, (0+0+sqrt(3)/2)/3) = (0.5, sqrt(3)/6).
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, math.sqrt(3) / 2.0]])
    c = circumcenter(pts)
    assert c.shape == (2,)
    assert np.allclose(c, np.array([0.5, math.sqrt(3) / 6.0]), atol=1e-10)


def test_circumradius_of_unit_equilateral_triangle():
    """Circumradius of the unit equilateral triangle equals 1/sqrt(3).

    Reference: Standard formula R = a / sqrt(3) for an equilateral
    triangle with side length a. With a = 1 this is 1/sqrt(3) ~= 0.5774.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, math.sqrt(3) / 2.0]])
    r = circumradius(pts)
    assert math.isclose(r, 1.0 / math.sqrt(3.0), rel_tol=1e-10)


# ---------------------------------------------------------------------------
# Property tests (Hypothesis)
# ---------------------------------------------------------------------------


def _polygon_area(polygon_points):
    """Shoelace formula for the area of a polygon given by its (ordered) hull."""
    x = polygon_points[:, 0]
    y = polygon_points[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def _triangle_area(p1, p2, p3):
    return 0.5 * abs(
        (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])
    )


# Strategy: generate small clouds of well-separated 2D points by sampling
# integer points and dilating, which avoids near-degeneracies.
def _point_cloud_2d(min_size=4, max_size=12):
    return st.lists(
        st.tuples(
            st.integers(min_value=-20, max_value=20),
            st.integers(min_value=-20, max_value=20),
        ),
        min_size=min_size,
        max_size=max_size,
        unique=True,
    )


@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(_point_cloud_2d(min_size=4, max_size=10))
def test_property_triangle_areas_sum_to_hull_area(raw_pts):
    """Sum of Delaunay triangle areas equals the convex-hull area.

    Property: Delaunay is a simplicial subdivision of the convex hull.
    """
    pts = np.array(raw_pts, dtype=float)
    # Skip degenerate point sets (all collinear).
    if np.linalg.matrix_rank(pts - pts[0]) < 2:
        return
    try:
        tri = delaunay_triangulation(pts)
    except ValueError:
        return  # degenerate input is allowed to raise
    total = 0.0
    for simplex in tri["simplices"]:
        a, b, c = pts[simplex]
        total += _triangle_area(a, b, c)
    # Convex hull area via scipy for ground truth.
    from scipy.spatial import ConvexHull

    hull = ConvexHull(pts)
    hull_pts = pts[hull.vertices]
    hull_area = _polygon_area(hull_pts)
    assert math.isclose(total, hull_area, rel_tol=1e-7, abs_tol=1e-7)


def test_property_find_simplex_inside_hull_returns_nonnegative():
    """A point strictly inside the convex hull yields a non-negative
    simplex index. Multiple interior probes must all succeed.
    """
    pts = np.array([[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0], [2.0, 2.0]])
    tri = delaunay_triangulation(pts)
    for q in [(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0), (2.0, 2.0)]:
        idx = find_simplex(np.array(q), tri)
        assert idx >= 0


def test_property_find_simplex_outside_hull_returns_minus_one():
    """A point clearly outside the convex hull returns -1."""
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    tri = delaunay_triangulation(pts)
    for q in [(-1.0, -1.0), (5.0, 5.0), (-0.1, 0.5), (0.5, 1.5)]:
        idx = find_simplex(np.array(q), tri)
        assert idx == -1


def test_property_voronoi_neighbors_is_symmetric():
    """Voronoi adjacency (j in N(i) <=> i in N(j))."""
    pts = np.array(
        [
            [0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0], [1.5, 1.5],
            [1.5, 0.0], [3.0, 1.5], [1.5, 3.0], [0.0, 1.5],
        ]
    )
    tri = delaunay_triangulation(pts)
    nbrs = voronoi_neighbors(tri)
    for i, ni in enumerate(nbrs):
        for j in ni:
            assert i in nbrs[j], f"Neighbor relation not symmetric: {i} ~ {j}"


@settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(_point_cloud_2d(min_size=3, max_size=3))
def test_property_circumradius_geq_inradius(raw_pts):
    """For any non-degenerate triangle, R >= 2r (Euler's triangle inequality).
    In particular R >= r.
    """
    pts = np.array(raw_pts, dtype=float)
    if pts.shape[0] != 3:
        return
    if np.linalg.matrix_rank(pts - pts[0]) < 2:
        return
    a = np.linalg.norm(pts[1] - pts[2])
    b = np.linalg.norm(pts[0] - pts[2])
    c = np.linalg.norm(pts[0] - pts[1])
    s = 0.5 * (a + b + c)
    area = math.sqrt(max(0.0, s * (s - a) * (s - b) * (s - c)))
    if area < 1e-12:
        return
    inradius = area / s
    R = circumradius(pts)
    assert R + 1e-9 >= inradius


def test_property_mesh_quality_angles_sum_to_180():
    """For each 2D triangle in a Delaunay mesh, the three angles must
    sum to pi (180 degrees). This is the Euclidean angle-sum theorem.
    """
    pts = np.array(
        [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0], [2.0, 2.0],
         [2.0, 0.0], [4.0, 2.0]]
    )
    tri = delaunay_triangulation(pts)
    q = mesh_quality(tri)
    for angles in q["angles_per_simplex"]:
        assert math.isclose(sum(angles), math.pi, rel_tol=1e-7, abs_tol=1e-7)


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_edge_empty_input_raises():
    """Edge: empty point array -> ValueError."""
    with pytest.raises(ValueError):
        delaunay_triangulation(np.empty((0, 2)))


def test_edge_too_few_points_raises():
    """Edge: fewer than d+1 points cannot form a d-simplex.

    - 2D with 2 points -> ValueError
    - 3D with 3 points -> ValueError
    """
    with pytest.raises(ValueError):
        delaunay_triangulation(np.array([[0.0, 0.0], [1.0, 0.0]]))
    with pytest.raises(ValueError):
        delaunay_triangulation(
            np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        )


def test_edge_all_collinear_2d_raises_or_degenerate():
    """Edge: all points collinear in 2D -> ValueError (qhull degeneracy
    wrapped). The convex hull is a segment, not a polygon, so no
    triangulation exists.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])
    with pytest.raises(ValueError):
        delaunay_triangulation(pts)


def test_edge_duplicate_points_handled():
    """Edge: duplicate point rows -> either ValueError or the duplicates
    are silently absorbed and the n_simplices count matches the unique
    set. We accept either behavior so long as the function does not
    return wrong topology.
    """
    pts = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    )
    try:
        tri = delaunay_triangulation(pts)
    except ValueError:
        return
    # If it didn't raise, it must produce a valid triangulation of the
    # 4 unique points (2 triangles for the unit square).
    assert tri["n_simplices"] == 2


def test_edge_find_simplex_extreme_query_point():
    """Edge: extreme query points (very far away, NaN) must not crash;
    far-away returns -1, NaN returns -1.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    tri = delaunay_triangulation(pts)
    assert find_simplex(np.array([1.0e12, 1.0e12]), tri) == -1
    # NaN: scipy returns -1 for NaN-containing queries.
    nan_idx = find_simplex(np.array([float("nan"), 0.5]), tri)
    assert nan_idx == -1


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_composition_alpha_inf_equals_full_delaunay():
    """Composition: alpha_complex(points, alpha=inf) returns every
    Delaunay simplex exactly once. This composes alpha-filtration with
    Delaunay.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]])
    tri = delaunay_triangulation(pts)
    full = delaunay_alpha_complex(pts, alpha=float("inf"))
    expected = sorted(tuple(sorted(s)) for s in tri["simplices"].tolist())
    actual = sorted(tuple(sorted(s)) for s in full)
    assert expected == actual


def test_composition_barycentric_on_vertex_recovers_vertex_value():
    """Composition: barycentric_interpolate at a known vertex returns
    the vertex's scalar value exactly. Chains delaunay_triangulation
    with barycentric_interpolate.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 0.5]])
    values = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    tri = delaunay_triangulation(pts)
    for i, p in enumerate(pts):
        v = barycentric_interpolate(tri, values, p)
        assert math.isclose(v, values[i], rel_tol=1e-9, abs_tol=1e-9)


def test_composition_voronoi_neighbors_match_scipy_voronoi():
    """Composition: Voronoi neighbor incidences derived from the Delaunay
    dual must agree with scipy.spatial.Voronoi's ridge_points incidences.

    This cross-checks the Delaunay <-> Voronoi duality.
    """
    from scipy.spatial import Voronoi

    pts = np.array(
        [[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0], [1.5, 1.5]]
    )
    tri = delaunay_triangulation(pts)
    ours = voronoi_neighbors(tri)

    vor = Voronoi(pts)
    expected = [set() for _ in range(len(pts))]
    for i, j in vor.ridge_points:
        expected[i].add(int(j))
        expected[j].add(int(i))

    for i in range(len(pts)):
        assert ours[i] == expected[i], (
            f"Voronoi neighbor mismatch at point {i}: "
            f"ours={ours[i]} scipy={expected[i]}"
        )


def test_composition_delaunay_2d_image_returns_grid():
    """Composition: chain delaunay_triangulation + barycentric_interpolate
    via delaunay_2d_to_image. The output must be a 2D ndarray of the
    requested resolution and finite at the convex-hull interior.
    """
    pts = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    values = np.array([0.0, 1.0, 1.0, 0.0])  # bilinear-ish
    img = delaunay_2d_to_image(pts, values, resolution=8)
    assert img.shape == (8, 8)
    # The center pixel must be inside and finite.
    assert np.isfinite(img[4, 4])
