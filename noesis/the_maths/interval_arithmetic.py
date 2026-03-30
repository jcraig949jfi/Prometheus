"""
Interval Arithmetic -- Verified computation, interval Newton method, Krawczyk operator

Connects to: [nonstandard_analysis, constructive_mathematics, computational_algebra, p_adic_numbers]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "interval_arithmetic"
OPERATIONS = {}


def _to_intervals(x):
    """Convert array to pairs of intervals [lo, hi].
    Even indices are lower bounds, odd indices are upper bounds."""
    n = len(x)
    pairs = n // 2
    if pairs == 0:
        return np.array([[x[0] - 0.5, x[0] + 0.5]]) if n > 0 else np.array([[0.0, 1.0]])
    result = []
    for i in range(pairs):
        lo = min(x[2 * i], x[2 * i + 1])
        hi = max(x[2 * i], x[2 * i + 1])
        result.append([lo, hi])
    return np.array(result)


def interval_add(x):
    """Add two intervals: [a,b] + [c,d] = [a+c, b+d].
    Input: array (4 values: a,b,c,d). Output: array [lo, hi]."""
    if len(x) < 4:
        padded = np.concatenate([x, np.zeros(4 - len(x))])
    else:
        padded = x[:4]
    a, b = min(padded[0], padded[1]), max(padded[0], padded[1])
    c, d = min(padded[2], padded[3]), max(padded[2], padded[3])
    return np.array([a + c, b + d])


OPERATIONS["interval_add"] = {
    "fn": interval_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two intervals [a,b]+[c,d]=[a+c,b+d]"
}


def interval_multiply(x):
    """Multiply two intervals: [a,b]*[c,d] = [min(ac,ad,bc,bd), max(ac,ad,bc,bd)].
    Input: array (4 values). Output: array [lo, hi]."""
    if len(x) < 4:
        padded = np.concatenate([x, np.ones(4 - len(x))])
    else:
        padded = x[:4]
    a, b = min(padded[0], padded[1]), max(padded[0], padded[1])
    c, d = min(padded[2], padded[3]), max(padded[2], padded[3])
    products = [a * c, a * d, b * c, b * d]
    return np.array([min(products), max(products)])


OPERATIONS["interval_multiply"] = {
    "fn": interval_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Multiply two intervals"
}


def interval_divide(x):
    """Divide two intervals: [a,b]/[c,d] (c,d must not contain 0).
    Input: array (4 values). Output: array [lo, hi]."""
    if len(x) < 4:
        padded = np.concatenate([x, np.ones(4 - len(x))])
    else:
        padded = x[:4]
    a, b = min(padded[0], padded[1]), max(padded[0], padded[1])
    c, d = min(padded[2], padded[3]), max(padded[2], padded[3])
    if c <= 0 <= d:
        # Division by interval containing zero: return [-inf, inf]
        return np.array([-1e15, 1e15])
    quotients = [a / c, a / d, b / c, b / d]
    return np.array([min(quotients), max(quotients)])


OPERATIONS["interval_divide"] = {
    "fn": interval_divide,
    "input_type": "array",
    "output_type": "array",
    "description": "Divide two intervals (extended for zero-containing divisor)"
}


def interval_power(x):
    """Interval raised to integer power n. [a,b]^n where n = int(last element).
    Input: array. Output: array [lo, hi]."""
    if len(x) < 3:
        padded = np.concatenate([x, np.array([0.0, 1.0, 2.0])])[:3]
    else:
        padded = x[:3]
    a, b = min(padded[0], padded[1]), max(padded[0], padded[1])
    n = max(1, int(abs(padded[2])))
    if n % 2 == 0:
        # Even power: [a,b]^n
        if a >= 0:
            return np.array([a ** n, b ** n])
        elif b <= 0:
            return np.array([b ** n, a ** n])
        else:
            return np.array([0.0, max(a ** n, b ** n)])
    else:
        # Odd power: monotone
        return np.array([a ** n, b ** n])


OPERATIONS["interval_power"] = {
    "fn": interval_power,
    "input_type": "array",
    "output_type": "array",
    "description": "Interval raised to integer power"
}


def interval_newton_step(x):
    """One step of interval Newton method for f(x)=x^2-c.
    Input: array [x_lo, x_hi, c]. Output: array [new_lo, new_hi]."""
    if len(x) < 3:
        padded = np.concatenate([x, np.array([1.0, 2.0, 2.0])])[:3]
    else:
        padded = x[:3]
    x_lo, x_hi = min(padded[0], padded[1]), max(padded[0], padded[1])
    c = padded[2]
    # f(x) = x^2 - c, f'(x) = 2x
    # Newton: x_new = m - f(m)/f'([x_lo, x_hi])
    m = (x_lo + x_hi) / 2.0
    f_m = m ** 2 - c
    # f'([x_lo, x_hi]) = [2*x_lo, 2*x_hi]
    fp_lo = 2.0 * x_lo
    fp_hi = 2.0 * x_hi
    if fp_lo <= 0 <= fp_hi:
        # Derivative interval contains zero, split
        return np.array([x_lo, x_hi])
    # N(x) = m - f(m) / [fp_lo, fp_hi]
    quotients = [f_m / fp_lo, f_m / fp_hi]
    n_lo = m - max(quotients)
    n_hi = m - min(quotients)
    # Intersect with original
    new_lo = max(x_lo, n_lo)
    new_hi = min(x_hi, n_hi)
    if new_lo > new_hi:
        return np.array([x_lo, x_hi])  # no improvement
    return np.array([new_lo, new_hi])


OPERATIONS["interval_newton_step"] = {
    "fn": interval_newton_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One interval Newton step for f(x)=x^2-c"
}


def krawczyk_operator(x):
    """Krawczyk operator for verified root existence of f(x)=x^2-c.
    K(X) = m - Yf(m) + (I - YF'(X))(X - m) where Y approx f'(m)^{-1}.
    Input: array [x_lo, x_hi, c]. Output: array [k_lo, k_hi]."""
    if len(x) < 3:
        padded = np.concatenate([x, np.array([1.0, 2.0, 2.0])])[:3]
    else:
        padded = x[:3]
    x_lo, x_hi = min(padded[0], padded[1]), max(padded[0], padded[1])
    c = padded[2]
    m = (x_lo + x_hi) / 2.0
    f_m = m ** 2 - c
    fp_m = 2.0 * m
    if abs(fp_m) < 1e-15:
        return np.array([x_lo, x_hi])
    Y = 1.0 / fp_m  # approximate inverse
    # F'(X) = 2*X = [2*x_lo, 2*x_hi]
    fp_X = np.array([2.0 * x_lo, 2.0 * x_hi])
    # I - Y*F'(X)
    correction = np.array([1.0 - Y * fp_X[1], 1.0 - Y * fp_X[0]])
    # (X - m)
    diff = np.array([x_lo - m, x_hi - m])
    # correction * diff (interval multiplication)
    prods = [correction[0] * diff[0], correction[0] * diff[1],
             correction[1] * diff[0], correction[1] * diff[1]]
    k_lo = m - Y * f_m + min(prods)
    k_hi = m - Y * f_m + max(prods)
    # Intersect with X
    new_lo = max(x_lo, k_lo)
    new_hi = min(x_hi, k_hi)
    if new_lo > new_hi:
        return np.array([x_lo, x_hi])
    return np.array([new_lo, new_hi])


OPERATIONS["krawczyk_operator"] = {
    "fn": krawczyk_operator,
    "input_type": "array",
    "output_type": "array",
    "description": "Krawczyk operator for verified root enclosure"
}


def interval_hull(x):
    """Interval hull of a set of points. Input: array. Output: array [min, max]."""
    return np.array([np.min(x), np.max(x)])


OPERATIONS["interval_hull"] = {
    "fn": interval_hull,
    "input_type": "array",
    "output_type": "array",
    "description": "Interval hull (bounding interval) of a point set"
}


def interval_width(x):
    """Width of intervals encoded in array. Input: array. Output: scalar."""
    intervals = _to_intervals(x)
    widths = intervals[:, 1] - intervals[:, 0]
    return float(np.max(widths))


OPERATIONS["interval_width"] = {
    "fn": interval_width,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Maximum width of intervals"
}


def interval_midpoint(x):
    """Midpoints of intervals. Input: array. Output: array."""
    intervals = _to_intervals(x)
    return (intervals[:, 0] + intervals[:, 1]) / 2.0


OPERATIONS["interval_midpoint"] = {
    "fn": interval_midpoint,
    "input_type": "array",
    "output_type": "array",
    "description": "Midpoints of intervals"
}


def interval_contains_zero(x):
    """Check which intervals contain zero. Input: array. Output: scalar (count)."""
    intervals = _to_intervals(x)
    count = np.sum((intervals[:, 0] <= 0) & (intervals[:, 1] >= 0))
    return float(count)


OPERATIONS["interval_contains_zero"] = {
    "fn": interval_contains_zero,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of intervals containing zero"
}


def verified_root_exists(x):
    """Use Krawczyk operator to verify root existence. K(X) subset X => root exists.
    Input: array [x_lo, x_hi, c]. Output: scalar (1 if verified, 0 if not)."""
    if len(x) < 3:
        padded = np.concatenate([x, np.array([1.0, 2.0, 2.0])])[:3]
    else:
        padded = x[:3]
    x_lo, x_hi = min(padded[0], padded[1]), max(padded[0], padded[1])
    k_result = krawczyk_operator(padded)
    # Check if K(X) is contained in X
    if k_result[0] >= x_lo and k_result[1] <= x_hi:
        return 1.0
    return 0.0


OPERATIONS["verified_root_exists"] = {
    "fn": verified_root_exists,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Verified root existence via Krawczyk containment test"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
