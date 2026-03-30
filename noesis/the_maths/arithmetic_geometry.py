"""
Arithmetic Geometry — height functions, Mordell-Weil (toy), rational points on conics

Connects to: [number_theory, algebraic_geometry, diophantine_equations, elliptic_curves]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import gcd

FIELD_NAME = "arithmetic_geometry"
OPERATIONS = {}


def naive_height(x):
    """Naive height of a rational number p/q: H(p/q) = max(|p|, |q|).
    Input: array [p, q] or array of numerators (denominators=1). Output: scalar or array.
    """
    if len(x) >= 2:
        # Treat pairs as (p, q)
        results = []
        for i in range(0, len(x) - 1, 2):
            p, q = abs(x[i]), abs(x[i + 1])
            if q == 0:
                q = 1
            results.append(max(p, q))
        return np.array(results)
    return np.abs(x)


OPERATIONS["naive_height"] = {
    "fn": naive_height,
    "input_type": "array",
    "output_type": "array",
    "description": "Naive height max(|p|,|q|) for rational numbers p/q"
}


def logarithmic_height(x):
    """Logarithmic (Weil) height: h(p/q) = log(max(|p|, |q|)).
    Input: array [p, q, ...]. Output: array.
    """
    results = []
    for i in range(0, len(x) - 1, 2):
        p, q = abs(x[i]), abs(x[i + 1])
        if q == 0:
            q = 1
        g = gcd(int(round(p)), int(round(max(q, 1))))
        p, q = p / g, q / g
        results.append(np.log(max(p, q, 1)))
    if not results:
        return np.log(np.abs(x) + 1)
    return np.array(results)


OPERATIONS["logarithmic_height"] = {
    "fn": logarithmic_height,
    "input_type": "array",
    "output_type": "array",
    "description": "Logarithmic height log(max(|p|,|q|)) for rational numbers"
}


def weil_height_projective(x):
    """Weil height for a projective point [x0 : x1 : ... : xn].
    H([x0:...:xn]) = max(|xi|) after clearing denominators.
    Input: array of projective coordinates. Output: scalar.
    """
    coords = np.abs(x)
    # Normalize to make smallest nonzero coordinate 1
    nonzero = coords[coords > 1e-12]
    if len(nonzero) == 0:
        return np.float64(0.0)
    normalized = coords / nonzero.min()
    return np.float64(np.log(np.max(normalized) + 1))


OPERATIONS["weil_height_projective"] = {
    "fn": weil_height_projective,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Weil height of a projective point"
}


def rational_points_on_circle(x):
    """Find rational points on the unit circle x^2 + y^2 = 1 with denominator up to N.
    Input: array (uses x[0] as bound N). Output: matrix of (x, y) pairs.
    Parametrization: x = (1-t^2)/(1+t^2), y = 2t/(1+t^2) for t = m/n.
    """
    N = max(int(np.abs(x[0])), 2)
    N = min(N, 20)  # Cap for performance
    points = set()
    for n in range(1, N + 1):
        for m in range(-N, N + 1):
            g = gcd(abs(m), n)
            t_num, t_den = m // g, n // g
            # x = (t_den^2 - t_num^2) / (t_den^2 + t_num^2)
            # y = 2 * t_num * t_den / (t_den^2 + t_num^2)
            denom = t_den**2 + t_num**2
            if denom == 0:
                continue
            px = (t_den**2 - t_num**2) / denom
            py = 2 * t_num * t_den / denom
            points.add((round(px, 10), round(py, 10)))
    pts = sorted(points)
    if not pts:
        return np.array([[1.0, 0.0]])
    return np.array(pts)


OPERATIONS["rational_points_on_circle"] = {
    "fn": rational_points_on_circle,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Rational points on the unit circle with bounded denominator"
}


def has_rational_point_conic(x):
    """Check if the conic ax^2 + by^2 = c has a rational point (simple local checks).
    Input: array [a, b, c]. Output: integer (1 = likely has point, 0 = no).
    Uses simple checks: if a,b,c have same sign and a,b > 0, c < 0, then no.
    """
    if len(x) < 3:
        return np.int64(0)
    a, b, c = x[0], x[1], x[2]
    if abs(c) < 1e-12:
        return np.int64(1)  # (0, 0) is a solution
    # If a and b have same sign and opposite to c, there are real solutions
    # Check if rational: try small denominators
    bound = 10
    for p in range(-bound, bound + 1):
        for q in range(-bound, bound + 1):
            val = a * p**2 + b * q**2
            if abs(val - c) < 1e-9:
                return np.int64(1)
    return np.int64(0)


OPERATIONS["has_rational_point_conic"] = {
    "fn": has_rational_point_conic,
    "input_type": "array",
    "output_type": "integer",
    "description": "Check if conic ax^2 + by^2 = c has a rational point (brute-force search)"
}


def hensel_local_solubility(x):
    """Check local solubility of x^2 = a mod p for small primes.
    Input: array [a]. Output: array of primes p where a is a quadratic residue.
    """
    a = int(round(x[0]))
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    residue_primes = []
    for p in primes:
        a_mod = a % p
        is_residue = False
        for r in range(p):
            if (r * r) % p == a_mod % p:
                is_residue = True
                break
        if is_residue:
            residue_primes.append(p)
    if not residue_primes:
        return np.array([0.0])
    return np.array(residue_primes, dtype=float)


OPERATIONS["hensel_local_solubility"] = {
    "fn": hensel_local_solubility,
    "input_type": "array",
    "output_type": "array",
    "description": "Primes p where a is a quadratic residue mod p (Hensel-style local check)"
}


def hasse_principle_check_diagonal(x):
    """Hasse principle check for diagonal form a*x^2 + b*y^2 + c*z^2 = 0.
    Input: array [a, b, c]. Output: integer (1=locally soluble everywhere checked, 0=obstruction found).
    Checks real solubility and mod-p solubility for small primes.
    """
    if len(x) < 3:
        return np.int64(0)
    a, b, c = float(x[0]), float(x[1]), float(x[2])

    # Real solubility: need not all same sign
    signs = [np.sign(a), np.sign(b), np.sign(c)]
    if all(s > 0 for s in signs) or all(s < 0 for s in signs):
        return np.int64(0)  # No real solution (except trivial)

    # Check mod small primes
    primes = [2, 3, 5, 7]
    ai, bi, ci = int(round(a)), int(round(b)), int(round(c))
    for p in primes:
        found = False
        for xx in range(p):
            for yy in range(p):
                for zz in range(p):
                    if xx == 0 and yy == 0 and zz == 0:
                        continue
                    if (ai * xx**2 + bi * yy**2 + ci * zz**2) % p == 0:
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            return np.int64(0)
    return np.int64(1)


OPERATIONS["hasse_principle_check_diagonal"] = {
    "fn": hasse_principle_check_diagonal,
    "input_type": "array",
    "output_type": "integer",
    "description": "Hasse principle check for ternary diagonal quadratic form"
}


def arithmetic_genus(x):
    """Arithmetic genus of a smooth projective curve of degree d in P^2.
    g = (d-1)(d-2)/2.
    Input: array (x[0] = degree). Output: integer.
    """
    d = max(int(round(np.abs(x[0]))), 1)
    g = (d - 1) * (d - 2) // 2
    return np.int64(g)


OPERATIONS["arithmetic_genus"] = {
    "fn": arithmetic_genus,
    "input_type": "array",
    "output_type": "integer",
    "description": "Arithmetic genus (d-1)(d-2)/2 of a degree-d smooth plane curve"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
