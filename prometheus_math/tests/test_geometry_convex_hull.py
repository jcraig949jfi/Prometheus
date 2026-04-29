"""Tests for prometheus_math.geometry_convex_hull.

Project #71 — pm.geometry.convex_hull (qhull bindings).

Test categories follow techne/skills/math-tdd.md:
  Authority    — output matches authoritative reference values
                 (textbook polygon / polyhedron volumes & areas).
  Property     — invariants hold across many inputs (Hypothesis).
  Edge         — empty / singleton / collinear / 1-D / duplicate /
                 too-few-points-for-dimension.
  Composition  — chains with extreme_points, is_in_convex_hull, the
                 shoelace formula, and the bounding-sphere diameter.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math import geometry_convex_hull as gch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _shoelace(poly):
    """Signed area of a 2-D polygon by the shoelace formula.

    Reference: standard textbook (e.g. Berg et al., 'Computational
    Geometry', §1.1).  Returns absolute value; the sign depends on
    orientation.
    """
    n = len(poly)
    s = 0.0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


# ---------------------------------------------------------------------------
# AUTHORITY tests (≥3)
# ---------------------------------------------------------------------------


def test_authority_2d_unit_square():
    """Unit-square corners → 4 vertices, area 1, perimeter 4.

    Reference: hand-computation; the unit square [0,1]² has area 1
    and perimeter 4.  All four corners are extreme.
    """
    pts = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
    h = gch.convex_hull(pts)
    assert len(h["vertices"]) == 4
    assert math.isclose(h["volume"], 1.0, abs_tol=1e-12)
    assert math.isclose(h["area"], 4.0, abs_tol=1e-12)


def test_authority_3d_unit_cube():
    """Unit-cube corners → 8 vertices, volume 1, surface area 6.

    Reference: hand-computation; the unit cube [0,1]³ has volume 1 and
    surface area 6 (six unit-square faces).
    """
    cube = np.array(list(itertools.product([0.0, 1.0], repeat=3)))
    h = gch.convex_hull(cube)
    assert len(h["vertices"]) == 8
    assert math.isclose(h["volume"], 1.0, abs_tol=1e-12)
    assert math.isclose(h["area"], 6.0, abs_tol=1e-12)


def test_authority_2d_right_triangle():
    """Right triangle (0,0),(1,0),(0,1) → 3 vertices, area 0.5.

    Reference: triangle area = 1/2 * base * height = 1/2 * 1 * 1.
    Perimeter = 1 + 1 + sqrt(2).
    """
    pts = np.array([[0, 0], [1, 0], [0, 1]], dtype=float)
    h = gch.convex_hull(pts)
    assert len(h["vertices"]) == 3
    assert math.isclose(h["volume"], 0.5, abs_tol=1e-12)
    assert math.isclose(h["area"], 2.0 + math.sqrt(2.0), abs_tol=1e-12)


def test_authority_2d_interior_point_excluded():
    """Square with an interior centre point → still 4 hull vertices.

    Reference: convexity — the centroid of a convex region is interior
    and never extreme.  Hand-computed.
    """
    pts = np.array(
        [[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]], dtype=float
    )
    h = gch.convex_hull(pts)
    assert len(h["vertices"]) == 4
    assert 4 not in set(h["vertices"].tolist())  # interior excluded
    assert math.isclose(h["volume"], 1.0, abs_tol=1e-12)


def test_authority_1d_interval():
    """1-D cloud → hull is the bounding interval; volume = length.

    Reference: in 1-D the convex hull of {x_i} is [min, max] and its
    "volume" (Lebesgue measure on R) is max - min.
    """
    pts = np.array([[1.0], [3.0], [2.0], [-1.0]])
    h = gch.convex_hull(pts)
    assert math.isclose(h["volume"], 4.0, abs_tol=1e-12)
    # min coord = -1 at idx 3, max coord = 3 at idx 1, length = 4.
    assert set(h["vertices"].tolist()) == {1, 3}
    assert math.isclose(gch.convex_hull_volume(pts), 4.0, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# PROPERTY tests (≥3, Hypothesis)
# ---------------------------------------------------------------------------


_coord = st.floats(
    min_value=-50.0, max_value=50.0, allow_nan=False, allow_infinity=False
)


@st.composite
def _points_2d(draw, min_n=4, max_n=20):
    n = draw(st.integers(min_value=min_n, max_value=max_n))
    pts = draw(
        st.lists(
            st.tuples(_coord, _coord), min_size=n, max_size=n, unique=True
        )
    )
    return np.array(pts, dtype=float)


@settings(max_examples=40, deadline=None)
@given(_points_2d())
def test_property_centroid_inside_hull(pts):
    """The centroid of any non-empty 2-D cloud lies in its convex hull.

    Property: the centroid is a convex combination of the points, and a
    convex hull is closed under convex combinations.
    """
    # Reject geometrically degenerate clouds (collinear) — those give
    # a 0-area hull and find_simplex is brittle.
    h = gch.convex_hull(pts)
    if h["degenerate"] or h["volume"] < 1e-9:
        return
    centroid = pts.mean(axis=0)
    assert gch.is_in_convex_hull(centroid, pts) is True


@settings(max_examples=40, deadline=None)
@given(_points_2d())
def test_property_invariant_under_permutation(pts):
    """Permuting the input does not change the hull's vertex *set*
    (when interpreted as point coordinates) or its volume / area.

    Property: convex hull is a set-valued operation; it does not depend
    on the input ordering, only on the multiset of input coordinates.
    """
    perm = np.random.RandomState(0).permutation(len(pts))
    pts_perm = pts[perm]
    h1 = gch.convex_hull(pts)
    h2 = gch.convex_hull(pts_perm)
    assert math.isclose(h1["volume"], h2["volume"], abs_tol=1e-9)
    assert math.isclose(h1["area"], h2["area"], abs_tol=1e-9)
    # Vertex coordinate sets agree.
    set1 = {tuple(np.round(pts[i], 9)) for i in h1["vertices"]}
    set2 = {tuple(np.round(pts_perm[i], 9)) for i in h2["vertices"]}
    assert set1 == set2


@settings(max_examples=40, deadline=None)
@given(_points_2d())
def test_property_extreme_points_subset(pts):
    """|extreme_points(P)| <= |P|, and every index returned is valid.

    Property: extreme points are a subset of the input.
    """
    ex = gch.extreme_points(pts)
    assert len(ex) <= len(pts)
    assert all(0 <= i < len(pts) for i in ex)


@settings(max_examples=40, deadline=None)
@given(_points_2d())
def test_property_diameter_symmetric(pts):
    """Diameter is symmetric: d(P) is realised by an unordered pair.

    Property: distance is symmetric, so swapping (idx_a, idx_b) does
    not change d.
    """
    d, a, b = gch.convex_hull_diameter(pts)
    assert d >= 0.0
    direct = float(np.linalg.norm(pts[a] - pts[b]))
    assert math.isclose(d, direct, abs_tol=1e-9)


@settings(max_examples=20, deadline=None)
@given(_points_2d(min_n=4, max_n=10))
def test_property_volume_invariant_under_interior_addition(pts):
    """Adding the centroid (an interior point) does not change vol.

    Property: a convex hull is determined by its extreme points; adding
    an interior point leaves the hull unchanged.
    """
    h = gch.convex_hull(pts)
    if h["degenerate"] or h["volume"] < 1e-9:
        return
    centroid = pts.mean(axis=0)
    pts2 = np.vstack([pts, centroid[None, :]])
    h2 = gch.convex_hull(pts2)
    assert math.isclose(h["volume"], h2["volume"], abs_tol=1e-9)


@settings(max_examples=30, deadline=None)
@given(_points_2d())
def test_property_volume_nonnegative(pts):
    """Convex-hull volume is always non-negative.

    Property: Lebesgue measure of any set is ≥ 0.
    """
    assert gch.convex_hull_volume(pts) >= 0.0


# ---------------------------------------------------------------------------
# EDGE-CASE tests (≥3)
# ---------------------------------------------------------------------------


def test_edge_empty_input():
    """Empty input must raise ValueError.

    Edges covered: empty list, empty ndarray.
    """
    with pytest.raises(ValueError):
        gch.convex_hull([])
    with pytest.raises(ValueError):
        gch.convex_hull(np.array([]))


def test_edge_single_point():
    """Singleton input → trivial hull (volume=0, vertices=[0]).

    Edge: 1 point in 2-D is too few for Qhull; we fall back to a
    geometric trivial hull.
    """
    h = gch.convex_hull(np.array([[3.5, -2.0]]))
    assert h["vertices"].tolist() == [0]
    assert h["volume"] == 0.0
    assert h["area"] == 0.0
    assert h["degenerate"] is True


def test_edge_two_points_2d_segment():
    """Two 2-D points → segment "hull" with both as vertices and vol=0.

    Edge: 2 points in 2-D is below the d+1 = 3 threshold for Qhull.
    """
    pts = np.array([[0.0, 0.0], [3.0, 4.0]])
    h = gch.convex_hull(pts)
    assert set(h["vertices"].tolist()) == {0, 1}
    assert h["volume"] == 0.0


def test_edge_collinear_points():
    """All-collinear 2-D points → degenerate hull, volume 0.

    Edge: Qhull raises QhullError on a flat initial simplex; we handle
    it by returning a degenerate hull with the unique-coordinate
    indices as vertices.
    """
    pts = np.array([[0, 0], [1, 1], [2, 2], [3, 3]], dtype=float)
    h = gch.convex_hull(pts)
    assert h["degenerate"] is True
    assert h["volume"] == 0.0
    assert set(h["vertices"].tolist()) == {0, 1, 2, 3}


def test_edge_duplicate_points_ignored():
    """Duplicates in the input do not add new hull vertices.

    Edge: Qhull discards exact duplicates internally; the unit-square
    test is unaffected by replicating one of its corners.
    """
    pts = np.array(
        [
            [0, 0], [1, 0], [1, 1], [0, 1],
            [0, 0],  # duplicate of corner 0
            [1, 0],  # duplicate of corner 1
        ],
        dtype=float,
    )
    h = gch.convex_hull(pts)
    # Volume / area unchanged.
    assert math.isclose(h["volume"], 1.0, abs_tol=1e-12)
    assert math.isclose(h["area"], 4.0, abs_tol=1e-12)


def test_edge_too_few_points_high_dim():
    """3 points in 4-D (< d+1 = 5) → degenerate hull, no error.

    Edge: pathological scale — too few points to span the dimension.
    Per the spec this is "ValueError or graceful handling"; we choose
    graceful.
    """
    pts = np.array(
        [[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=float
    )
    h = gch.convex_hull(pts)
    assert h["degenerate"] is True
    assert h["volume"] == 0.0


def test_edge_high_dim_4d_simplex():
    """5 affinely-independent points in 4-D → 4-simplex, volume 1/24.

    Edge: smallest non-degenerate input in 4-D.  The standard 4-simplex
    {0, e_1, e_2, e_3, e_4} has 4-volume 1 / 4! = 1/24.
    """
    pts = np.vstack([np.zeros(4), np.eye(4)])
    h = gch.convex_hull(pts)
    assert math.isclose(h["volume"], 1.0 / 24.0, abs_tol=1e-12)


def test_edge_malformed_3d_input():
    """3-D ndarray (non 2-D) → ValueError.

    Edge: malformed input.
    """
    with pytest.raises(ValueError):
        gch.convex_hull(np.zeros((2, 3, 4)))


# ---------------------------------------------------------------------------
# COMPOSITION tests (≥2)
# ---------------------------------------------------------------------------


def test_composition_extreme_points_idempotence():
    """convex_hull(extreme_points(P)) has the same volume as convex_hull(P).

    Composition: the hull is determined by its extreme set, so dropping
    interior points and recomputing gives the same hull.
    """
    rng = np.random.RandomState(7)
    pts = rng.rand(40, 2) * 10.0
    h1 = gch.convex_hull(pts)
    ex = gch.extreme_points(pts)
    sub = pts[ex]
    h2 = gch.convex_hull(sub)
    assert math.isclose(h1["volume"], h2["volume"], abs_tol=1e-9)
    assert math.isclose(h1["area"], h2["area"], abs_tol=1e-9)


def test_composition_vertex_is_in_hull():
    """Every vertex of the hull is itself in the hull.

    Composition: chains convex_hull → extreme_points → is_in_convex_hull.
    """
    rng = np.random.RandomState(13)
    pts = rng.rand(20, 2) * 5.0
    for i in gch.extreme_points(pts):
        assert gch.is_in_convex_hull(pts[i], pts) is True


def test_composition_diameter_le_bounding_sphere():
    """Diameter ≤ 2 * radius of any enclosing sphere.

    Composition: chains convex_hull_diameter against a bounding-sphere
    radius (max distance from centroid).  This is a classical fact:
    the diameter of a set is at most the diameter of any enclosing
    sphere.
    """
    rng = np.random.RandomState(21)
    pts = rng.rand(30, 3) * 10.0
    centroid = pts.mean(axis=0)
    radius = float(np.linalg.norm(pts - centroid, axis=1).max())
    d, _, _ = gch.convex_hull_diameter(pts)
    assert d <= 2.0 * radius + 1e-9


def test_composition_2d_polygon_shoelace_matches_area():
    """Polygon-area via the shoelace formula equals convex_hull_area
    (which is *perimeter* in 2-D), so we check shoelace == volume.

    Composition: chains convex_hull_2d_polygon against the independent
    shoelace formula and convex_hull_volume.
    """
    rng = np.random.RandomState(33)
    pts = rng.rand(25, 2) * 4.0
    poly = gch.convex_hull_2d_polygon(pts)
    area = _shoelace(poly)
    assert math.isclose(area, gch.convex_hull_volume(pts), abs_tol=1e-9)


def test_composition_delaunay_count_against_hull_facets():
    """For a 2-D point cloud, the Delaunay triangulation has at least
    as many simplices as the hull has edges minus 2 (Euler-style).

    Composition: chains delaunay_triangulation_count against
    convex_hull_facets, asserting a structural relationship.

    For n points with h on the hull and t triangles in the Delaunay
    triangulation, we have t = 2 n - h - 2 (a standard 2-D identity).
    """
    rng = np.random.RandomState(99)
    n = 25
    pts = rng.rand(n, 2)
    h_facets = len(gch.convex_hull_facets(pts))   # = h hull edges
    t = gch.delaunay_triangulation_count(pts)
    assert t == 2 * n - h_facets - 2
