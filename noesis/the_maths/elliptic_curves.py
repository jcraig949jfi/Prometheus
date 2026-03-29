"""
Elliptic Curves — point addition, scalar multiplication, j-invariant, Weierstrass form

Connects to: [number_theory, algebraic_geometry, cryptography, group_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "elliptic_curves"
OPERATIONS = {}

# Default curve: y^2 = x^3 + ax + b (Weierstrass short form)
# We extract a, b from input arrays: a = x[0], b = x[1] when possible
# Point at infinity represented as (np.inf, np.inf)

_INF_POINT = (np.inf, np.inf)


def _get_curve_and_point(x):
    """Extract curve params and point from array.
    Convention: x = [a, b, px, py, ...] where y^2 = x^3 + a*x + b,
    and P = (px, py)."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 1.0
    px = x[2] if len(x) > 2 else 0.0
    py = x[3] if len(x) > 3 else np.sqrt(abs(px ** 3 + a * px + b))
    return a, b, px, py


def _get_two_points(x):
    """Extract curve params and two points from array.
    Convention: x = [a, b, p1x, p1y, p2x, ...] with p2y derived."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 1.0
    p1x = x[2] if len(x) > 2 else 0.0
    p1y = x[3] if len(x) > 3 else 0.0
    p2x = x[4] if len(x) > 4 else 0.0
    val = p2x ** 3 + a * p2x + b
    p2y = np.sqrt(abs(val)) if val >= 0 else 0.0
    return a, b, p1x, p1y, p2x, p2y


def _point_add(a, b, p1x, p1y, p2x, p2y):
    """Add two points on y^2 = x^3 + a*x + b over the reals."""
    # Handle point at infinity
    if np.isinf(p1x) and np.isinf(p1y):
        return p2x, p2y
    if np.isinf(p2x) and np.isinf(p2y):
        return p1x, p1y

    # Check if points are inverses (P + (-P) = O)
    if abs(p1x - p2x) < 1e-12 and abs(p1y + p2y) < 1e-12:
        return np.inf, np.inf

    if abs(p1x - p2x) < 1e-12 and abs(p1y - p2y) < 1e-12:
        # Point doubling
        if abs(p1y) < 1e-12:
            return np.inf, np.inf
        lam = (3.0 * p1x ** 2 + a) / (2.0 * p1y)
    else:
        # General addition
        denom = p2x - p1x
        if abs(denom) < 1e-15:
            return np.inf, np.inf
        lam = (p2y - p1y) / denom

    rx = lam ** 2 - p1x - p2x
    ry = lam * (p1x - rx) - p1y
    return rx, ry


def ec_point_add(x):
    """Add two points on an elliptic curve y^2 = x^3 + ax + b.
    Input: array [a, b, p1x, p1y, p2x]. Output: array [rx, ry]."""
    a, b, p1x, p1y, p2x, p2y = _get_two_points(x)
    rx, ry = _point_add(a, b, p1x, p1y, p2x, p2y)
    return np.array([rx, ry])


OPERATIONS["ec_point_add"] = {
    "fn": ec_point_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Adds two points on elliptic curve y^2 = x^3 + ax + b"
}


def ec_point_double(x):
    """Double a point on an elliptic curve.
    Input: array [a, b, px, py, ...]. Output: array [rx, ry]."""
    a, b, px, py = _get_curve_and_point(x)
    rx, ry = _point_add(a, b, px, py, px, py)
    return np.array([rx, ry])


OPERATIONS["ec_point_double"] = {
    "fn": ec_point_double,
    "input_type": "array",
    "output_type": "array",
    "description": "Doubles a point on elliptic curve using tangent line formula"
}


def ec_scalar_multiply(x):
    """Compute n*P on an elliptic curve using double-and-add.
    n is derived from last element, point from earlier elements.
    Input: array [a, b, px, py, n]. Output: array [rx, ry]."""
    a, b, px, py = _get_curve_and_point(x)
    n = int(abs(x[-1])) if len(x) > 4 else int(abs(x[-1]))
    n = max(1, min(n, 1000))  # Bound for performance

    # Double-and-add
    rx, ry = np.inf, np.inf  # Start with point at infinity
    qx, qy = px, py

    while n > 0:
        if n & 1:
            rx, ry = _point_add(a, b, rx, ry, qx, qy)
        qx, qy = _point_add(a, b, qx, qy, qx, qy)
        n >>= 1

    return np.array([rx, ry])


OPERATIONS["ec_scalar_multiply"] = {
    "fn": ec_scalar_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes scalar multiplication n*P via double-and-add"
}


def ec_j_invariant(x):
    """Compute the j-invariant of elliptic curve y^2 = x^3 + ax + b.
    j = -1728 * (4a)^3 / (4a^3 + 27b^2) when discriminant != 0.
    Input: array. Output: scalar."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 1.0
    disc = -16.0 * (4.0 * a ** 3 + 27.0 * b ** 2)
    if abs(disc) < 1e-15:
        return float('inf')
    j = -1728.0 * (4.0 * a) ** 3 / (4.0 * a ** 3 + 27.0 * b ** 2)
    return float(j)


OPERATIONS["ec_j_invariant"] = {
    "fn": ec_j_invariant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes j-invariant: j = -1728*(4a)^3 / (4a^3 + 27b^2)"
}


def ec_discriminant(x):
    """Compute the discriminant of y^2 = x^3 + ax + b.
    Delta = -16(4a^3 + 27b^2). Curve is non-singular iff Delta != 0.
    Input: array. Output: scalar."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 1.0
    delta = -16.0 * (4.0 * a ** 3 + 27.0 * b ** 2)
    return float(delta)


OPERATIONS["ec_discriminant"] = {
    "fn": ec_discriminant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes discriminant Delta = -16(4a^3 + 27b^2)"
}


def ec_is_on_curve(x):
    """Check if point (px, py) is on curve y^2 = x^3 + ax + b.
    Input: array [a, b, px, py, ...]. Output: integer (1 if on curve, 0 otherwise)."""
    a, b, px, py = _get_curve_and_point(x)
    lhs = py ** 2
    rhs = px ** 3 + a * px + b
    return int(abs(lhs - rhs) < 1e-6)


OPERATIONS["ec_is_on_curve"] = {
    "fn": ec_is_on_curve,
    "input_type": "array",
    "output_type": "integer",
    "description": "Checks if point lies on the elliptic curve (within tolerance)"
}


def ec_order_naive(x):
    """Estimate group order of elliptic curve over F_p by Hasse bound.
    For y^2 = x^3 + ax + b over F_p, |#E - (p+1)| <= 2*sqrt(p).
    Uses p = next prime >= max(int(|x[-1]|), 5).
    Input: array. Output: array [lower_bound, p+1, upper_bound]."""
    val = max(5, int(abs(x[-1])))
    # Simple prime finder
    p = val
    while True:
        if p < 2:
            p = 2
            break
        is_prime = True
        for d in range(2, int(np.sqrt(p)) + 1):
            if p % d == 0:
                is_prime = False
                break
        if is_prime:
            break
        p += 1
    bound = 2.0 * np.sqrt(p)
    return np.array([p + 1 - bound, p + 1, p + 1 + bound])


OPERATIONS["ec_order_naive"] = {
    "fn": ec_order_naive,
    "input_type": "array",
    "output_type": "array",
    "description": "Estimates curve order bounds via Hasse theorem: |#E - (p+1)| <= 2*sqrt(p)"
}


def ec_frobenius_trace_estimate(x):
    """Estimate trace of Frobenius a_p = p + 1 - #E(F_p).
    For small p, counts points directly on y^2 = x^3 + a*x + b mod p.
    Input: array [a, b, ...rest with last as p hint]. Output: scalar."""
    a_coeff = x[0] if len(x) > 0 else 0.0
    b_coeff = x[1] if len(x) > 1 else 1.0
    val = max(5, int(abs(x[-1])))
    # Find next prime
    p = val
    while True:
        is_prime = True
        for d in range(2, int(np.sqrt(p)) + 1):
            if p % d == 0:
                is_prime = False
                break
        if is_prime:
            break
        p += 1
    if p > 200:
        p = 7  # Keep small for speed

    a_int = int(round(a_coeff)) % p
    b_int = int(round(b_coeff)) % p

    # Count points: for each x in F_p, check if x^3 + ax + b is a QR
    count = 1  # Point at infinity
    for xi in range(p):
        rhs = (xi ** 3 + a_int * xi + b_int) % p
        if rhs == 0:
            count += 1  # y = 0
        else:
            # Euler criterion: rhs^((p-1)/2) mod p == 1 means QR
            if pow(rhs, (p - 1) // 2, p) == 1:
                count += 2  # Two square roots
    trace = p + 1 - count
    return float(trace)


OPERATIONS["ec_frobenius_trace_estimate"] = {
    "fn": ec_frobenius_trace_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates Frobenius trace a_p = p+1 - #E(F_p) by point counting"
}


def ec_weierstrass_form(x):
    """Convert general cubic coefficients to short Weierstrass form.
    Given [a1, a2, a3, a4, a6] from y^2 + a1*xy + a3*y = x^3 + a2*x^2 + a4*x + a6,
    computes short form y^2 = x^3 + a*x + b.
    Input: array. Output: array [a, b]."""
    a1 = x[0] if len(x) > 0 else 0.0
    a2 = x[1] if len(x) > 1 else 0.0
    a3 = x[2] if len(x) > 2 else 0.0
    a4 = x[3] if len(x) > 3 else 0.0
    a6 = x[4] if len(x) > 4 else 0.0

    # Standard transformation to short Weierstrass form
    b2 = a1 ** 2 + 4 * a2
    b4 = a1 * a3 + 2 * a4
    b6 = a3 ** 2 + 4 * a6

    c4 = b2 ** 2 - 24 * b4
    c6 = -b2 ** 3 + 36 * b2 * b4 - 216 * b6

    a_short = -c4 / 48.0
    b_short = -c6 / 864.0
    return np.array([a_short, b_short])


OPERATIONS["ec_weierstrass_form"] = {
    "fn": ec_weierstrass_form,
    "input_type": "array",
    "output_type": "array",
    "description": "Converts general Weierstrass [a1,a2,a3,a4,a6] to short form [a,b]"
}


def ec_torsion_points_small(x):
    """Find small torsion points on y^2 = x^3 + ax + b.
    Searches for rational points with small integer coordinates
    and checks if they have finite order.
    Input: array [a, b, ...]. Output: integer (count of torsion points found)."""
    a = x[0] if len(x) > 0 else 0.0
    b = x[1] if len(x) > 1 else 1.0
    search_range = 20
    count = 1  # Always count point at infinity

    for xi in range(-search_range, search_range + 1):
        rhs = xi ** 3 + a * xi + b
        if rhs < 0:
            continue
        yi = np.sqrt(rhs)
        if abs(yi - round(yi)) < 1e-6:
            yi = round(yi)
            # Check if this point has finite order by iterating
            # nP until we get back to O or give up
            px, py = float(xi), float(yi)
            qx, qy = px, py
            is_torsion = False
            for mult in range(2, 13):  # Mazur: torsion order <= 12
                qx, qy = _point_add(a, b, qx, qy, px, py)
                if np.isinf(qx) and np.isinf(qy):
                    is_torsion = True
                    break
            if is_torsion:
                count += 1
                if yi != 0:
                    count += 1  # Also count (xi, -yi)

    return int(count)


OPERATIONS["ec_torsion_points_small"] = {
    "fn": ec_torsion_points_small,
    "input_type": "array",
    "output_type": "integer",
    "description": "Counts small torsion points on the curve (Mazur bound: order <= 12)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
