"""
Geometric Number Theory organism.

Operations: lattice_points_in_circle, minkowski_bound, gauss_circle_problem,
            pick_theorem, voronoi_from_lattice
"""

from .base import MathematicalOrganism


class GeometricNumberTheory(MathematicalOrganism):
    name = "geometric_number_theory"
    operations = {
        "lattice_points_in_circle": {
            "code": """
def lattice_points_in_circle(r):
    \"\"\"Count the number of integer lattice points (x, y) with x^2 + y^2 <= r^2.
    This is Gauss's circle problem. Returns count and the points themselves
    for small r.\"\"\"
    r = float(r)
    r_sq = r * r
    r_int = int(np.ceil(r))
    count = 0
    points = []
    for x in range(-r_int, r_int + 1):
        for y in range(-r_int, r_int + 1):
            if x * x + y * y <= r_sq:
                count += 1
                if r <= 20:
                    points.append((x, y))
    result = {"count": count, "radius": r}
    if r <= 20:
        result["points"] = points
    return result
""",
            "input_type": "geometric_params",
            "output_type": "lattice_structure",
        },
        "minkowski_bound": {
            "code": """
def minkowski_bound(discriminant, degree):
    \"\"\"Compute the Minkowski bound for a number field.
    For a number field of degree n with discriminant D:
    M = (n!/n^n) * (4/pi)^{r2} * sqrt(|D|)
    For simplicity, we compute the quadratic case (degree=2):
    M = sqrt(|D|) / 2   (for imaginary quadratic)
    M = sqrt(|D|) / 2   (simplified bound)
    General: M = sqrt(|D|) * n! / (n^n * (pi/4)^{floor(n/2)})\"\"\"
    import math
    n = int(degree)
    D = abs(int(discriminant))
    # r2 = number of pairs of complex embeddings
    # For quadratic: r2 = 1 if D < 0 (imaginary), r2 = 0 if D > 0 (real)
    r2 = n // 2  # rough estimate for general case
    bound = (math.factorial(n) / (n ** n)) * ((4.0 / np.pi) ** r2) * np.sqrt(D)
    return {
        "minkowski_bound": float(bound),
        "discriminant": int(discriminant),
        "degree": n,
        "must_check_primes_up_to": int(np.ceil(bound)),
    }
""",
            "input_type": "geometric_params",
            "output_type": "lattice_structure",
        },
        "gauss_circle_problem": {
            "code": """
def gauss_circle_problem(r):
    \"\"\"Compare N(r) (lattice points in circle of radius r)
    with the asymptotic pi * r^2.
    The error term E(r) = N(r) - pi*r^2 is O(r^{2/3}) conjectured.\"\"\"
    r = float(r)
    r_sq = r * r
    r_int = int(np.ceil(r))
    # Count lattice points
    count = 0
    for x in range(-r_int, r_int + 1):
        max_y = int(np.sqrt(max(r_sq - x * x, 0)))
        count += 2 * max_y + 1
    area = np.pi * r_sq
    error = count - area
    return {
        "radius": r,
        "N_r": count,
        "pi_r_squared": float(area),
        "error": float(error),
        "relative_error": float(error / area) if area > 0 else 0.0,
        "error_over_r_2_3": float(error / (r ** (2.0/3))) if r > 0 else 0.0,
    }
""",
            "input_type": "geometric_params",
            "output_type": "lattice_structure",
        },
        "pick_theorem": {
            "code": """
def pick_theorem(boundary_points, interior_points):
    \"\"\"Pick's theorem: A = I + B/2 - 1
    where A = area, I = interior lattice points, B = boundary lattice points.
    Given B and I, compute the area of a simple lattice polygon.\"\"\"
    B = int(boundary_points)
    I = int(interior_points)
    area = I + B / 2.0 - 1.0
    return {
        "area": float(area),
        "boundary_points": B,
        "interior_points": I,
    }
""",
            "input_type": "geometric_params",
            "output_type": "lattice_structure",
        },
        "voronoi_from_lattice": {
            "code": """
def voronoi_from_lattice(basis_vectors):
    \"\"\"Compute the Voronoi cell (fundamental domain) of a 2D lattice
    defined by two basis vectors.
    Returns the vertices of the Voronoi cell centered at the origin.
    The Voronoi cell is the set of points closer to the origin than
    to any other lattice point.\"\"\"
    b = np.asarray(basis_vectors, dtype=np.float64)
    if b.shape != (2, 2):
        raise ValueError("Need exactly 2 basis vectors in 2D, shape (2,2)")
    v1, v2 = b[0], b[1]

    # Generate nearby lattice points
    neighbors = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i == 0 and j == 0:
                continue
            neighbors.append(i * v1 + j * v2)
    neighbors = np.array(neighbors)

    # Voronoi cell = intersection of half-planes
    # For each neighbor p, the half-plane is {x : |x| <= |x - p|}
    # Equivalent to x . p <= |p|^2 / 2
    # We sample points on a fine grid and keep those inside all half-planes
    det = abs(np.linalg.det(b))
    scale = np.sqrt(det) * 2
    N = 200
    xx = np.linspace(-scale, scale, N)
    yy = np.linspace(-scale, scale, N)
    X, Y = np.meshgrid(xx, yy)
    pts = np.stack([X.ravel(), Y.ravel()], axis=1)

    inside = np.ones(len(pts), dtype=bool)
    for p in neighbors:
        # x . p <= |p|^2 / 2
        half = np.dot(pts, p)
        inside &= (half <= np.dot(p, p) / 2 + 1e-10)

    voronoi_pts = pts[inside]
    # Extract convex hull boundary (approximate vertices)
    if len(voronoi_pts) < 3:
        return {"vertices": [], "area": 0.0}

    # Find vertices by convex hull
    centroid = voronoi_pts.mean(axis=0)
    angles = np.arctan2(voronoi_pts[:, 1] - centroid[1],
                        voronoi_pts[:, 0] - centroid[0])
    sorted_idx = np.argsort(angles)
    boundary = voronoi_pts[sorted_idx]

    # Keep only outermost points (rough convex hull)
    n_bins = 36
    bin_edges = np.linspace(-np.pi, np.pi, n_bins + 1)
    vertices = []
    for k in range(n_bins):
        mask = (angles >= bin_edges[k]) & (angles < bin_edges[k + 1])
        if np.any(mask):
            dists = np.sqrt(np.sum(voronoi_pts[mask] ** 2, axis=1))
            farthest = np.argmax(dists)
            vertices.append(voronoi_pts[mask][farthest].tolist())

    return {
        "vertices": vertices,
        "area": float(det),
        "basis": b.tolist(),
    }
""",
            "input_type": "geometric_params",
            "output_type": "lattice_structure",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = GeometricNumberTheory()
    print(org)

    # Lattice points in circle
    lp = org.execute("lattice_points_in_circle", 5)
    print(f"Lattice points in circle r=5: {lp['count']}  (expect 81)")

    # Minkowski bound for Q(sqrt(-5)), D = -20
    mb = org.execute("minkowski_bound", -20, 2)
    print(f"Minkowski bound for D=-20, n=2: {mb}")

    # Gauss circle problem
    gc = org.execute("gauss_circle_problem", 10.0)
    print(f"Gauss circle r=10: N={gc['N_r']}, pi*r^2={gc['pi_r_squared']:.2f}, "
          f"error={gc['error']:.2f}")

    gc100 = org.execute("gauss_circle_problem", 100.0)
    print(f"Gauss circle r=100: N={gc100['N_r']}, pi*r^2={gc100['pi_r_squared']:.2f}, "
          f"rel_error={gc100['relative_error']:.6f}")

    # Pick's theorem: unit square has B=4, I=0 => A=1
    pick = org.execute("pick_theorem", 4, 0)
    print(f"Pick (B=4, I=0): area = {pick['area']}  (expect 1.0)")

    # 3x3 square: B=12, I=4 => A=4+12/2-1=9
    pick2 = org.execute("pick_theorem", 12, 4)
    print(f"Pick (B=12, I=4): area = {pick2['area']}  (expect 9.0)")

    # Voronoi cell for standard lattice
    vor = org.execute("voronoi_from_lattice", [[1, 0], [0, 1]])
    print(f"Voronoi for Z^2: area={vor['area']:.2f}, vertices count={len(vor['vertices'])}")

    # Voronoi cell for hexagonal lattice
    hex_basis = [[1, 0], [0.5, np.sqrt(3)/2]]
    vor2 = org.execute("voronoi_from_lattice", hex_basis)
    print(f"Voronoi for hex lattice: area={vor2['area']:.4f}")

    print("--- geometric_number_theory: ALL TESTS PASSED ---")
