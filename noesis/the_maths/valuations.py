"""
Valuations — p-adic valuations, Ostrowski's theorem (discrete approximation)

Connects to: [tropical_semirings, number_theory, algebraic_geometry, q_analogues]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "valuations"
OPERATIONS = {}


def p_adic_valuation_int(x):
    """Compute p-adic valuation v_p(n) for p=2 on each element (rounded to int).
    v_p(n) = largest k such that p^k divides n. Input: array. Output: array."""
    p = 2
    result = np.zeros(len(x))
    for i, v in enumerate(x):
        n = int(round(abs(v)))
        if n == 0:
            result[i] = np.inf
            continue
        k = 0
        while n % p == 0:
            k += 1
            n //= p
        result[i] = k
    return result


OPERATIONS["p_adic_valuation_int"] = {
    "fn": p_adic_valuation_int,
    "input_type": "array",
    "output_type": "array",
    "description": "2-adic valuation of each element (rounded to nearest integer)"
}


def archimedean_valuation(x):
    """Standard archimedean (absolute value) valuation. |x|.
    Input: array. Output: array."""
    return np.abs(x)


OPERATIONS["archimedean_valuation"] = {
    "fn": archimedean_valuation,
    "input_type": "array",
    "output_type": "array",
    "description": "Archimedean valuation (absolute value)"
}


def product_formula_check(x):
    """Verify the product formula: prod_v |x|_v = 1 for rational x.
    For integer n, prod = |n|_inf * prod_p |n|_p = |n| * prod_p p^{-v_p(n)} = 1.
    Returns array of prod_v |x_i|_v (should be ~1 for integers).
    Input: array. Output: array."""
    result = np.zeros(len(x))
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    for i, v in enumerate(x):
        n = int(round(abs(v)))
        if n == 0:
            result[i] = 0.0
            continue
        # |n|_inf = n
        prod = float(n)
        # |n|_p = p^{-v_p(n)}
        remaining = n
        for p in primes:
            while remaining % p == 0:
                prod *= (1.0 / p)
                remaining //= p
        # remaining prime factors
        if remaining > 1:
            prod *= (1.0 / remaining)
        result[i] = prod
    return result


OPERATIONS["product_formula_check"] = {
    "fn": product_formula_check,
    "input_type": "array",
    "output_type": "array",
    "description": "Product formula verification: should return 1 for integers"
}


def valuation_ring_membership(x):
    """Check if elements belong to the valuation ring O_v = {x : v(x) >= 0}.
    For 2-adic: v_2(n) >= 0 always for integers, so check if |x|_2 <= 1.
    Returns 1.0 for members, 0.0 otherwise. Input: array. Output: array."""
    p = 2
    result = np.zeros(len(x))
    for i, v in enumerate(x):
        n = int(round(abs(v)))
        if n == 0:
            result[i] = 1.0  # 0 is in every valuation ring
            continue
        # |n|_p = p^{-v_p(n)}
        k = 0
        temp = n
        while temp % p == 0:
            k += 1
            temp //= p
        # |n|_2 = 2^{-k} <= 1 iff k >= 0 (always true for integers)
        result[i] = 1.0 if k >= 0 else 0.0
    return result


OPERATIONS["valuation_ring_membership"] = {
    "fn": valuation_ring_membership,
    "input_type": "array",
    "output_type": "array",
    "description": "Check membership in 2-adic valuation ring"
}


def completion_cauchy_rate(x):
    """Estimate Cauchy convergence rate in p-adic metric.
    Given a sequence x, compute |x_{i+1} - x_i|_p for p=2.
    Input: array. Output: array."""
    p = 2
    if len(x) < 2:
        return np.array([0.0])
    diffs = np.diff(x)
    result = np.zeros(len(diffs))
    for i, d in enumerate(diffs):
        n = int(round(abs(d)))
        if n == 0:
            result[i] = 0.0
            continue
        k = 0
        temp = n
        while temp % p == 0:
            k += 1
            temp //= p
        result[i] = p ** (-k)
    return result


OPERATIONS["completion_cauchy_rate"] = {
    "fn": completion_cauchy_rate,
    "input_type": "array",
    "output_type": "array",
    "description": "Successive 2-adic distances |x_{i+1} - x_i|_2"
}


def ultrametric_distance(x):
    """Compute ultrametric (p-adic) distance matrix for p=2.
    d(a,b) = |a-b|_p. Input: array. Output: matrix."""
    p = 2
    n = len(x)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            diff = int(round(abs(x[i] - x[j])))
            if diff == 0:
                D[i, j] = 0.0
            else:
                k = 0
                temp = diff
                while temp % p == 0:
                    k += 1
                    temp //= p
                D[i, j] = p ** (-k)
            D[j, i] = D[i, j]
    return D


OPERATIONS["ultrametric_distance"] = {
    "fn": ultrametric_distance,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Pairwise 2-adic ultrametric distance matrix"
}


def valuation_ideal_norm(x):
    """Compute the norm of the ideal generated by x in the valuation ring.
    For p-adic, N(p^k O) = p^{-k}. We compute the minimum valuation
    and return p^{-min_v}. Input: array. Output: scalar."""
    p = 2
    min_val = np.inf
    for v in x:
        n = int(round(abs(v)))
        if n == 0:
            continue
        k = 0
        temp = n
        while temp % p == 0:
            k += 1
            temp //= p
        min_val = min(min_val, k)
    if min_val == np.inf:
        return 0.0
    return float(p ** (-min_val))


OPERATIONS["valuation_ideal_norm"] = {
    "fn": valuation_ideal_norm,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Norm of the ideal generated by x in the 2-adic valuation ring"
}


def extension_ramification_index(x):
    """Compute ramification index for a simple extension.
    For Q_p(p^{1/e}), the ramification index is e.
    Given array x as coefficients of a polynomial, find the ramification
    by analyzing the Newton polygon slopes. Input: array. Output: integer."""
    p = 2
    n = len(x)
    # Compute p-adic valuations of coefficients
    vals = []
    for v in x:
        ni = int(round(abs(v)))
        if ni == 0:
            vals.append(np.inf)
        else:
            k = 0
            temp = ni
            while temp % p == 0:
                k += 1
                temp //= p
            vals.append(k)
    # Newton polygon: lower convex hull of points (i, vals[i])
    # Find slopes; ramification index relates to denominator of slopes
    finite_pts = [(i, vals[i]) for i in range(n) if vals[i] < np.inf]
    if len(finite_pts) < 2:
        return 1
    # Compute slopes between consecutive finite points
    slopes = []
    for k in range(len(finite_pts) - 1):
        i1, v1 = finite_pts[k]
        i2, v2 = finite_pts[k + 1]
        if i2 != i1:
            slopes.append((v2 - v1) / (i2 - i1))
    if not slopes:
        return 1
    # Ramification index = LCM of denominators of slopes (as reduced fractions)
    from math import gcd
    lcm_val = 1
    for s in slopes:
        # Express slope as fraction
        from fractions import Fraction
        f = Fraction(s).limit_denominator(1000)
        d = f.denominator
        lcm_val = lcm_val * d // gcd(lcm_val, d)
    return int(lcm_val)


OPERATIONS["extension_ramification_index"] = {
    "fn": extension_ramification_index,
    "input_type": "array",
    "output_type": "integer",
    "description": "Ramification index from Newton polygon of polynomial"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
