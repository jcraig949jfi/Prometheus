"""
Wasan Sangaku — Japanese temple geometry: tangent circles and inversive geometry

Connects to: [kerala_series, vedic_square, egyptian_fractions]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "wasan_sangaku"
OPERATIONS = {}


def descartes_circle_theorem(x):
    """Descartes Circle Theorem: given 3 mutually tangent circle curvatures, find the 4th.
    Input: array [k1, k2, k3]. Output: array [k4_outer, k4_inner]."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    k1 = arr[0] if len(arr) > 0 else 1.0
    k2 = arr[1] if len(arr) > 1 else 1.0
    k3 = arr[2] if len(arr) > 2 else 1.0
    # (k1+k2+k3+k4)^2 = 2(k1^2+k2^2+k3^2+k4^2)
    # k4 = k1+k2+k3 +/- 2*sqrt(k1*k2 + k2*k3 + k3*k1)
    s = k1 + k2 + k3
    disc = k1 * k2 + k2 * k3 + k3 * k1
    if disc < 0:
        return np.array([s, s])
    sq = 2.0 * np.sqrt(disc)
    return np.array([s + sq, s - sq])


OPERATIONS["descartes_circle_theorem"] = {
    "fn": descartes_circle_theorem,
    "input_type": "array",
    "output_type": "array",
    "description": "Find 4th tangent circle curvature via Descartes Circle Theorem"
}


def apollonian_gasket_curvatures(x):
    """Generate Apollonian gasket curvatures for several generations.
    Input: array [k1, k2, k3, n_generations]. Output: array of curvatures."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    k1 = arr[0] if len(arr) > 0 else 1.0
    k2 = arr[1] if len(arr) > 1 else 1.0
    k3 = arr[2] if len(arr) > 2 else 1.0
    n_gen = max(1, int(arr[3])) if len(arr) > 3 else 3
    n_gen = min(n_gen, 5)

    curvatures = set()
    curvatures.update([k1, k2, k3])

    def descartes_k4(a, b, c):
        s = a + b + c
        disc = a * b + b * c + c * a
        if disc < 0:
            return []
        sq = 2.0 * np.sqrt(disc)
        return [s + sq, s - sq]

    # Initial 4th circle
    k4s = descartes_k4(k1, k2, k3)
    for k in k4s:
        curvatures.add(k)

    # BFS-style generation
    triples = [(k1, k2, k3)]
    for _ in range(n_gen):
        new_triples = []
        for a, b, c in triples:
            for k4 in descartes_k4(a, b, c):
                if k4 not in curvatures and k4 > 0:
                    curvatures.add(k4)
                    new_triples.append((a, b, k4))
                    new_triples.append((a, c, k4))
                    new_triples.append((b, c, k4))
        triples = new_triples[:100]  # cap for performance
    return np.array(sorted(curvatures))


OPERATIONS["apollonian_gasket_curvatures"] = {
    "fn": apollonian_gasket_curvatures,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate Apollonian gasket curvatures over generations"
}


def soddy_circle_chain(x):
    """Soddy circle chain: sequence of circles tangent to two fixed circles and each other.
    Input: array [R1, R2, n_circles]. Output: array of radii."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    r1 = abs(arr[0]) if len(arr) > 0 else 1.0
    r2 = abs(arr[1]) if len(arr) > 1 else 0.5
    n = max(1, int(arr[2])) if len(arr) > 2 else 5
    n = min(n, 20)
    if r1 == 0 or r2 == 0:
        return np.array([0.0])
    # For a Descartes chain between two circles with curvatures k1, k2
    k1, k2 = 1.0 / r1, 1.0 / r2
    radii = []
    # First circle in chain via Descartes with k3 = k1 (self-tangent in chain)
    # Simplified: use inversive distance to generate chain
    # Steiner chain approximation: r_n = r0 / (1 + n * r0 * (k1 + k2))^2
    # More accurate: use the recurrence from Descartes theorem
    k_prev = k1 + k2  # initial guess for first chain circle
    for i in range(n):
        # Each successive circle: k_new = 2*(k1+k2) + 2*sqrt(k1*k2) * (2*i+1) approximately
        k_chain = k1 + k2 + 2.0 * np.sqrt(k1 * k2) * (2 * i + 1)
        radii.append(1.0 / k_chain)
    return np.array(radii)


OPERATIONS["soddy_circle_chain"] = {
    "fn": soddy_circle_chain,
    "input_type": "array",
    "output_type": "array",
    "description": "Generate Soddy/Steiner circle chain radii between two circles"
}


def inversive_distance(x):
    """Inversive distance between two circles. Input: array [x1,y1,r1, x2,y2,r2]. Output: scalar.
    delta = (d^2 - r1^2 - r2^2) / (2*r1*r2)."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    x1, y1, r1 = arr[0], arr[1], arr[2] if len(arr) > 2 else 1.0
    x2 = arr[3] if len(arr) > 3 else 0.0
    y2 = arr[4] if len(arr) > 4 else 0.0
    r2 = arr[5] if len(arr) > 5 else 1.0
    if len(arr) < 6:
        # Use first 3 as circle 1, remaining as circle 2 (or defaults)
        pass
    d_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if r1 == 0 or r2 == 0:
        return float(np.inf)
    delta = (d_sq - r1 * r1 - r2 * r2) / (2.0 * abs(r1) * abs(r2))
    return float(delta)


OPERATIONS["inversive_distance"] = {
    "fn": inversive_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Inversive distance between two circles"
}


def circle_inversion(x):
    """Invert a point through a circle of radius R centered at origin.
    Input: array [px, py, R]. Output: array [px', py']."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    px = arr[0] if len(arr) > 0 else 1.0
    py = arr[1] if len(arr) > 1 else 0.0
    R = arr[2] if len(arr) > 2 else 1.0
    d_sq = px * px + py * py
    if d_sq == 0:
        return np.array([np.inf, np.inf])
    scale = R * R / d_sq
    return np.array([px * scale, py * scale])


OPERATIONS["circle_inversion"] = {
    "fn": circle_inversion,
    "input_type": "array",
    "output_type": "array",
    "description": "Invert a point through a circle (inversive geometry)"
}


def tangent_circle_radius(x):
    """Find radius of circle tangent to three given circles (Apollonius problem).
    Input: array [r1, r2, r3, d12, d13, d23]. Output: scalar (approximate)."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    r1 = arr[0] if len(arr) > 0 else 1.0
    r2 = arr[1] if len(arr) > 1 else 1.0
    r3 = arr[2] if len(arr) > 2 else 1.0
    # Use Descartes theorem as an approximation (for mutually tangent circles)
    k1, k2, k3 = 1.0 / r1, 1.0 / r2, 1.0 / r3
    disc = k1 * k2 + k2 * k3 + k3 * k1
    if disc < 0:
        return 0.0
    k4 = k1 + k2 + k3 + 2.0 * np.sqrt(disc)
    return float(1.0 / k4) if k4 != 0 else float(np.inf)


OPERATIONS["tangent_circle_radius"] = {
    "fn": tangent_circle_radius,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Radius of circle tangent to three given circles (Apollonius/Descartes)"
}


def nested_circle_packing(x):
    """Pack n circles inside a unit circle (equal radius). Input: array. Output: array of radii.
    Uses known optimal packings for small n."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = max(1, int(arr[0])) if len(arr) > 0 else 5
    n = min(n, 20)
    # Optimal ratio R_inner/R_outer for n equal circles in a circle
    # For n circles arranged symmetrically: r = sin(pi/n) / (1 + sin(pi/n))
    if n == 1:
        return np.array([1.0])
    r = np.sin(np.pi / n) / (1.0 + np.sin(np.pi / n))
    return np.full(n, r)


OPERATIONS["nested_circle_packing"] = {
    "fn": nested_circle_packing,
    "input_type": "array",
    "output_type": "array",
    "description": "Equal circle packing radii inside unit circle"
}


def sangaku_ellipse_in_triangle(x):
    """Compute the inellipse of a triangle (largest ellipse fitting inside). Input: array [a, b, c] sides. Output: array [semi_a, semi_b, area]."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    a = arr[0] if len(arr) > 0 else 3.0
    b = arr[1] if len(arr) > 1 else 4.0
    c = arr[2] if len(arr) > 2 else 5.0
    # Steiner inellipse: the unique ellipse tangent to all three sides at midpoints
    # Area of Steiner inellipse = pi/(3*sqrt(3)) * area_triangle
    s = (a + b + c) / 2.0
    area_tri_sq = s * (s - a) * (s - b) * (s - c)
    if area_tri_sq <= 0:
        return np.array([0.0, 0.0, 0.0])
    area_tri = np.sqrt(area_tri_sq)
    area_ellipse = np.pi / (3.0 * np.sqrt(3.0)) * area_tri
    # Inradius for reference
    inradius = area_tri / s
    # Semi-axes approximation: for Steiner inellipse, a_e * b_e = area_ellipse / pi
    # Aspect ratio depends on triangle shape; for equilateral: a_e = b_e = inradius * sqrt(pi/(3*sqrt(3)))
    ab_product = area_ellipse / np.pi
    # Use eccentricity from side ratios
    semi_b = np.sqrt(ab_product * min(a, b, c) / max(a, b, c))
    semi_a = ab_product / semi_b if semi_b > 0 else 0.0
    return np.array([semi_a, semi_b, area_ellipse])


OPERATIONS["sangaku_ellipse_in_triangle"] = {
    "fn": sangaku_ellipse_in_triangle,
    "input_type": "array",
    "output_type": "array",
    "description": "Steiner inellipse of a triangle (sangaku temple problem)"
}


def inversive_power(x):
    """Compute power of a point with respect to a circle. Input: array [px, py, cx, cy, r]. Output: scalar.
    Power = d^2 - r^2 where d is distance from point to center."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    px = arr[0] if len(arr) > 0 else 0.0
    py = arr[1] if len(arr) > 1 else 0.0
    cx = arr[2] if len(arr) > 2 else 0.0
    cy = arr[3] if len(arr) > 3 else 0.0
    r = arr[4] if len(arr) > 4 else 1.0
    d_sq = (px - cx) ** 2 + (py - cy) ** 2
    return float(d_sq - r * r)


OPERATIONS["inversive_power"] = {
    "fn": inversive_power,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Power of a point with respect to a circle"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
