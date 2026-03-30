"""
Convex Geometry — Support functions, Minkowski sums, mixed volumes, Brunn-Minkowski

Connects to: [polytope_combinatorics, discrete_morse_theory, sheaves_on_graphs]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "convex_geometry"
OPERATIONS = {}


def _to_2d_points(x):
    """Convert a flat array to 2D points. If length n, create n/2 points or
    use as radii at evenly spaced angles."""
    n = len(x)
    if n >= 4 and n % 2 == 0:
        return x.reshape(-1, 2)
    else:
        # Interpret as radii at evenly spaced angles
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        r = np.abs(x) + 0.1
        return np.column_stack([r * np.cos(angles), r * np.sin(angles)])


def _convex_hull_2d(points):
    """Compute 2D convex hull using gift wrapping. Returns indices in CCW order."""
    n = len(points)
    if n < 3:
        return np.arange(n)
    # Find leftmost point
    start = np.argmin(points[:, 0])
    hull = []
    current = start
    while True:
        hull.append(current)
        candidate = 0
        for i in range(n):
            if i == current:
                continue
            if candidate == current:
                candidate = i
                continue
            # Cross product to determine turn (2D: use scalar formula)
            vc = points[candidate] - points[current]
            vi = points[i] - points[current]
            cross = vc[0] * vi[1] - vc[1] * vi[0]
            if cross < 0:
                candidate = i
            elif cross == 0:
                # Take farther point
                d1 = np.sum((points[candidate] - points[current]) ** 2)
                d2 = np.sum((points[i] - points[current]) ** 2)
                if d2 > d1:
                    candidate = i
        current = candidate
        if current == start:
            break
        if len(hull) > n:
            break
    return np.array(hull)


def support_function(x):
    """Compute the support function h_K(u) = max_{p in K} <p, u> for several directions.
    Input: array (interpreted as 2D points). Output: array (support values at 8 directions)."""
    pts = _to_2d_points(x)
    n_dirs = 8
    angles = np.linspace(0, 2 * np.pi, n_dirs, endpoint=False)
    directions = np.column_stack([np.cos(angles), np.sin(angles)])
    h = np.array([np.max(pts @ d) for d in directions])
    return h


OPERATIONS["support_function"] = {
    "fn": support_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes support function of a 2D convex body at 8 directions"
}


def minkowski_sum_2d(x):
    """Compute Minkowski sum of two convex polygons derived from input.
    Splits input in half to form two polygons. Returns vertices of sum.
    Input: array. Output: matrix (vertices of Minkowski sum)."""
    pts = _to_2d_points(x)
    n = len(pts)
    half = max(n // 2, 2)
    P = pts[:half]
    Q = pts[half:] if n > half else pts[:2] * 0.5
    # Minkowski sum: for convex polygons, merge sorted edge vectors
    # Simple approach: take all pairwise sums of hull vertices
    hull_p = _convex_hull_2d(P)
    hull_q = _convex_hull_2d(Q)
    sums = []
    for i in hull_p:
        for j in hull_q:
            sums.append(P[i] + Q[j])
    sums = np.array(sums)
    hull_idx = _convex_hull_2d(sums)
    return sums[hull_idx]


OPERATIONS["minkowski_sum_2d"] = {
    "fn": minkowski_sum_2d,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes Minkowski sum of two 2D convex polygons"
}


def minkowski_difference_2d(x):
    """Compute Minkowski difference (erosion) P minus Q.
    Input: array. Output: matrix (vertices) or array if degenerate."""
    pts = _to_2d_points(x)
    n = len(pts)
    half = max(n // 2, 2)
    P = pts[:half]
    Q = pts[half:] if n > half else pts[:2] * 0.1
    # Minkowski difference via support function: h_{P-Q}(u) = h_P(u) - h_Q(u)
    n_dirs = 16
    angles = np.linspace(0, 2 * np.pi, n_dirs, endpoint=False)
    directions = np.column_stack([np.cos(angles), np.sin(angles)])
    h_p = np.array([np.max(P @ d) for d in directions])
    h_q = np.array([np.max(Q @ d) for d in directions])
    h_diff = h_p - h_q
    # Reconstruct approximate polygon from support function
    # Each support value gives a halfplane; intersection is the body
    # Approximate: place points at h_diff(u)*u
    result_pts = np.column_stack([h_diff * np.cos(angles), h_diff * np.sin(angles)])
    return result_pts


OPERATIONS["minkowski_difference_2d"] = {
    "fn": minkowski_difference_2d,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes approximate Minkowski difference of two 2D convex polygons"
}


def mixed_volume_2d(x):
    """Compute the mixed volume (mixed area) V(P,Q) for two 2D convex bodies.
    V(P,Q) = (Vol(P+Q) - Vol(P) - Vol(Q)) / 2.
    Input: array. Output: scalar."""
    pts = _to_2d_points(x)
    n = len(pts)
    half = max(n // 2, 2)
    P = pts[:half]
    Q = pts[half:] if n > half else pts[:2] * 0.5

    def poly_area(vertices):
        idx = _convex_hull_2d(vertices)
        v = vertices[idx]
        n_v = len(v)
        if n_v < 3:
            return 0.0
        area = 0.0
        for i in range(n_v):
            j = (i + 1) % n_v
            area += v[i, 0] * v[j, 1] - v[j, 0] * v[i, 1]
        return abs(area) / 2.0

    area_p = poly_area(P)
    area_q = poly_area(Q)
    # Minkowski sum vertices
    mink_sum = minkowski_sum_2d(x)
    area_sum = poly_area(mink_sum)
    mixed = (area_sum - area_p - area_q) / 2.0
    return float(mixed)


OPERATIONS["mixed_volume_2d"] = {
    "fn": mixed_volume_2d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes mixed volume (mixed area) V(P,Q) for two 2D convex bodies"
}


def brunn_minkowski_check(x):
    """Verify Brunn-Minkowski inequality: Vol(P+Q)^{1/d} >= Vol(P)^{1/d} + Vol(Q)^{1/d}.
    Input: array. Output: scalar (1.0 if satisfied, 0.0 otherwise)."""
    pts = _to_2d_points(x)
    n = len(pts)
    half = max(n // 2, 2)
    P = pts[:half]
    Q = pts[half:] if n > half else pts[:2] * 0.5
    d = 2  # dimension

    def poly_area(vertices):
        idx = _convex_hull_2d(vertices)
        v = vertices[idx]
        n_v = len(v)
        if n_v < 3:
            return 0.0
        area = 0.0
        for i in range(n_v):
            j = (i + 1) % n_v
            area += v[i, 0] * v[j, 1] - v[j, 0] * v[i, 1]
        return abs(area) / 2.0

    area_p = poly_area(P)
    area_q = poly_area(Q)
    mink_sum = minkowski_sum_2d(x)
    area_sum = poly_area(mink_sum)
    lhs = area_sum ** (1.0 / d)
    rhs = area_p ** (1.0 / d) + area_q ** (1.0 / d)
    return 1.0 if lhs >= rhs - 1e-10 else 0.0


OPERATIONS["brunn_minkowski_check"] = {
    "fn": brunn_minkowski_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Verifies the Brunn-Minkowski inequality for two 2D convex bodies"
}


def convex_hull_volume(x):
    """Compute the area (2D volume) of the convex hull of points.
    Input: array. Output: scalar."""
    pts = _to_2d_points(x)
    idx = _convex_hull_2d(pts)
    v = pts[idx]
    n_v = len(v)
    if n_v < 3:
        return 0.0
    area = 0.0
    for i in range(n_v):
        j = (i + 1) % n_v
        area += v[i, 0] * v[j, 1] - v[j, 0] * v[i, 1]
    return float(abs(area) / 2.0)


OPERATIONS["convex_hull_volume"] = {
    "fn": convex_hull_volume,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes area of the 2D convex hull"
}


def john_ellipsoid_approx(x):
    """Approximate the John ellipsoid (maximum volume inscribed ellipsoid).
    Returns [center_x, center_y, semi_axis_1, semi_axis_2, angle].
    Input: array. Output: array."""
    pts = _to_2d_points(x)
    # Approximate: use the covariance ellipse of the convex hull vertices
    idx = _convex_hull_2d(pts)
    hull_pts = pts[idx]
    center = np.mean(hull_pts, axis=0)
    centered = hull_pts - center
    if len(centered) < 2:
        return np.array([center[0], center[1], 1.0, 1.0, 0.0])
    cov = (centered.T @ centered) / len(centered)
    eigvals, eigvecs = np.linalg.eigh(cov)
    eigvals = np.maximum(eigvals, 1e-10)
    # John ellipsoid is contained in the body; scale down by sqrt(d)=sqrt(2)
    semi_axes = np.sqrt(eigvals) / np.sqrt(2)
    angle = np.arctan2(eigvecs[1, 0], eigvecs[0, 0])
    return np.array([center[0], center[1], semi_axes[0], semi_axes[1], angle])


OPERATIONS["john_ellipsoid_approx"] = {
    "fn": john_ellipsoid_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximates the John ellipsoid (max volume inscribed ellipsoid)"
}


def polar_dual_vertices(x):
    """Compute vertices of the polar dual K* = {y : <x,y> <= 1 for all x in K}.
    Approximation: for each hull facet with equation <n,x>=b, dual vertex is n/b.
    Input: array. Output: matrix."""
    pts = _to_2d_points(x)
    idx = _convex_hull_2d(pts)
    hull = pts[idx]
    n_h = len(hull)
    if n_h < 3:
        return hull
    # Ensure origin is inside (translate if needed)
    centroid = np.mean(hull, axis=0)
    hull_c = hull - centroid  # center at origin
    dual_verts = []
    for i in range(n_h):
        j = (i + 1) % n_h
        edge = hull_c[j] - hull_c[i]
        normal = np.array([-edge[1], edge[0]])
        normal = normal / (np.linalg.norm(normal) + 1e-15)
        # Support value in this direction
        b = np.dot(normal, hull_c[i])
        if abs(b) > 1e-10:
            dual_verts.append(normal / b)
        else:
            dual_verts.append(normal * 1e10)
    return np.array(dual_verts)


OPERATIONS["polar_dual_vertices"] = {
    "fn": polar_dual_vertices,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes vertices of the polar dual body"
}


def width_function(x):
    """Compute the width function w_K(u) = h_K(u) + h_K(-u) for several directions.
    Input: array. Output: array."""
    pts = _to_2d_points(x)
    n_dirs = 8
    angles = np.linspace(0, 2 * np.pi, n_dirs, endpoint=False)
    directions = np.column_stack([np.cos(angles), np.sin(angles)])
    widths = np.array([np.max(pts @ d) - np.min(pts @ d) for d in directions])
    return widths


OPERATIONS["width_function"] = {
    "fn": width_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes the width function (sum of support in opposite directions)"
}


def mahler_volume(x):
    """Compute the Mahler volume: Vol(K) * Vol(K*), an affine invariant.
    Input: array. Output: scalar."""
    vol_k = convex_hull_volume(x)
    dual = polar_dual_vertices(x)
    # Compute area of polar dual
    if len(dual) < 3:
        return float(vol_k)
    idx = _convex_hull_2d(dual)
    v = dual[idx]
    n_v = len(v)
    if n_v < 3:
        return float(vol_k)
    area = 0.0
    for i in range(n_v):
        j = (i + 1) % n_v
        area += v[i, 0] * v[j, 1] - v[j, 0] * v[i, 1]
    vol_dual = abs(area) / 2.0
    return float(vol_k * vol_dual)


OPERATIONS["mahler_volume"] = {
    "fn": mahler_volume,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes Mahler volume Vol(K) * Vol(K*), an affine invariant"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
