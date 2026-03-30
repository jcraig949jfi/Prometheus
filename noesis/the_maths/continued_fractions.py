"""
Continued Fractions — convergents, best rational approximations, Stern-Brocot

Connects to: [number_theory, approximation_theory, dynamical_systems, diophantine_equations]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "continued_fractions"
OPERATIONS = {}


def to_continued_fraction(x):
    """Compute continued fraction coefficients [a_0; a_1, a_2, ...] of x[0].
    Uses up to 15 terms. Input: array. Output: array."""
    val = float(x[0])
    coeffs = []
    for _ in range(15):
        a = int(np.floor(val))
        coeffs.append(float(a))
        frac = val - a
        if abs(frac) < 1e-10:
            break
        val = 1.0 / frac
    return np.array(coeffs)


OPERATIONS["to_continued_fraction"] = {
    "fn": to_continued_fraction,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute continued fraction expansion [a0; a1, a2, ...] of first element"
}


def from_continued_fraction(x):
    """Evaluate continued fraction [a_0; a_1, a_2, ...] given as array x.
    Returns the rational number as a float. Input: array. Output: scalar."""
    if len(x) == 0:
        return 0.0
    val = float(x[-1])
    for i in range(len(x) - 2, -1, -1):
        if abs(val) < 1e-15:
            val = float(x[i])
        else:
            val = float(x[i]) + 1.0 / val
    return float(val)


OPERATIONS["from_continued_fraction"] = {
    "fn": from_continued_fraction,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate continued fraction [a0; a1, ...] to a floating point number"
}


def convergents(x):
    """Compute convergents p_k/q_k of continued fraction of x[0].
    Returns flat array [p_0, q_0, p_1, q_1, ...]. Input: array. Output: array."""
    cf = to_continued_fraction(x)
    result = []
    # p_{-1}=1, p_{-2}=0; q_{-1}=0, q_{-2}=1
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0
    for a in cf:
        a = int(a)
        p = a * p_prev1 + p_prev2
        q = a * q_prev1 + q_prev2
        result.extend([float(p), float(q)])
        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q
    return np.array(result)


OPERATIONS["convergents"] = {
    "fn": convergents,
    "input_type": "array",
    "output_type": "array",
    "description": "Convergents of continued fraction of x[0] as [p0,q0,p1,q1,...]"
}


def best_rational_approx(x):
    """Find the best rational approximation p/q to x[0] with q <= x[1] (or q<=10).
    Returns [p, q, error]. Input: array. Output: array."""
    target = float(x[0])
    max_q = int(round(x[1])) if len(x) > 1 else 10
    max_q = max(1, max_q)
    best_p, best_q, best_err = 0, 1, abs(target)
    cf = to_continued_fraction(np.array([target]))
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0
    for a in cf:
        a = int(a)
        p = a * p_prev1 + p_prev2
        q = a * q_prev1 + q_prev2
        if q > max_q:
            # Check intermediate convergents (semiconvergents)
            if q_prev1 > 0:
                max_a = (max_q - q_prev2) // q_prev1
                for k in range(1, int(max_a) + 1):
                    pk = k * p_prev1 + p_prev2
                    qk = k * q_prev1 + q_prev2
                    if qk <= max_q:
                        err = abs(target - pk / qk)
                        if err < best_err:
                            best_p, best_q, best_err = pk, qk, err
            break
        err = abs(target - p / q)
        if err < best_err:
            best_p, best_q, best_err = p, q, err
        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q
    return np.array([float(best_p), float(best_q), best_err])


OPERATIONS["best_rational_approx"] = {
    "fn": best_rational_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Best rational approximation p/q to x[0] with denominator <= x[1]"
}


def stern_brocot_path(x):
    """Compute path in the Stern-Brocot tree to reach the fraction closest to x[0].
    Returns array of 0s (left) and 1s (right). Input: array. Output: array."""
    target = abs(float(x[0]))
    if target < 1e-15:
        return np.array([0.0])
    path = []
    # Stern-Brocot tree mediant walk
    lo_p, lo_q = 0, 1
    hi_p, hi_q = 1, 0  # represents infinity
    for _ in range(30):
        med_p = lo_p + hi_p
        med_q = lo_q + hi_q
        if med_q > 1e8:
            break
        med = med_p / med_q
        if abs(med - target) < 1e-10:
            break
        elif target < med:
            path.append(0.0)  # left
            hi_p, hi_q = med_p, med_q
        else:
            path.append(1.0)  # right
            lo_p, lo_q = med_p, med_q
    if not path:
        path = [1.0]
    return np.array(path)


OPERATIONS["stern_brocot_path"] = {
    "fn": stern_brocot_path,
    "input_type": "array",
    "output_type": "array",
    "description": "Path in Stern-Brocot tree (0=left, 1=right) to approximate x[0]"
}


def mediant(x):
    """Compute the mediant of two fractions a/b and c/d.
    x = [a, b, c, d], mediant = (a+c)/(b+d). Input: array. Output: array."""
    a = int(round(x[0]))
    b = max(1, int(round(x[1])))
    c = int(round(x[2])) if len(x) > 2 else 1
    d = max(1, int(round(x[3]))) if len(x) > 3 else 1
    num = a + c
    den = b + d
    return np.array([float(num), float(den), num / den])


OPERATIONS["mediant"] = {
    "fn": mediant,
    "input_type": "array",
    "output_type": "array",
    "description": "Mediant of fractions x[0]/x[1] and x[2]/x[3]: (a+c)/(b+d)"
}


def gauss_map(x):
    """Apply the Gauss map T(x) = {1/x} (fractional part of 1/x) iteratively.
    Returns the orbit [x, T(x), T^2(x), ...] for up to 10 steps.
    Input: array. Output: array."""
    val = float(x[0])
    if val <= 0 or val >= 1:
        val = val - np.floor(val)
        if val < 1e-15:
            val = 0.5  # fallback
    orbit = [val]
    for _ in range(9):
        if abs(val) < 1e-15:
            break
        val = 1.0 / val - np.floor(1.0 / val)
        orbit.append(val)
    return np.array(orbit)


OPERATIONS["gauss_map"] = {
    "fn": gauss_map,
    "input_type": "array",
    "output_type": "array",
    "description": "Orbit of the Gauss map T(x) = {1/x} starting from fractional part of x[0]"
}


def khinchin_mean(x):
    """Compute the geometric mean of continued fraction coefficients of x[0],
    which should approach Khinchin's constant K ~ 2.6854520010... for almost all reals.
    Input: array. Output: scalar."""
    cf = to_continued_fraction(x)
    # Skip a_0, use a_1, a_2, ... (partial quotients)
    if len(cf) <= 1:
        return float(cf[0]) if len(cf) > 0 else 1.0
    partial_quotients = cf[1:]
    partial_quotients = partial_quotients[partial_quotients > 0]
    if len(partial_quotients) == 0:
        return 1.0
    geometric_mean = np.exp(np.mean(np.log(partial_quotients)))
    return float(geometric_mean)


OPERATIONS["khinchin_mean"] = {
    "fn": khinchin_mean,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Geometric mean of CF partial quotients (approaches Khinchin's constant)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
