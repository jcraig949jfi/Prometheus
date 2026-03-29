"""
Surreal Numbers — construction, addition, multiplication, comparison

Connects to: [game_theory, number_theory, ordinals, analysis]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Surreal numbers are represented as dyadic rationals m/2^k encoded as floats.
The "birthday" of a surreal number is the day it was created in Conway's
construction: day 0 = {|} = 0, day 1 = {0|} = 1 and {|0} = -1, etc.
"""

import numpy as np

FIELD_NAME = "surreal_numbers"
OPERATIONS = {}


def _to_dyadic(val):
    """Convert float to nearest dyadic rational m/2^k with bounded k."""
    max_k = 20
    for k in range(max_k + 1):
        m = round(val * (2 ** k))
        if abs(m / (2 ** k) - val) < 1e-12:
            return m, k
    # Fallback: approximate
    k = max_k
    m = round(val * (2 ** k))
    return m, k


def surreal_from_float(x):
    """Convert each float in x to its dyadic rational representation.
    Returns array of [numerator, denominator_power] pairs flattened.
    Input: array. Output: array."""
    result = []
    for val in x:
        m, k = _to_dyadic(val)
        result.extend([float(m), float(k)])
    return np.array(result)


OPERATIONS["surreal_from_float"] = {
    "fn": surreal_from_float,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert floats to dyadic rational pairs [m, k] where value = m/2^k"
}


def surreal_add(x):
    """Add surreal numbers represented as consecutive pairs in x.
    Pairs up elements and adds them: x[0]+x[1], x[2]+x[3], ...
    Surreal addition on dyadic rationals is ordinary addition.
    Input: array. Output: array."""
    result = []
    for i in range(0, len(x) - 1, 2):
        result.append(x[i] + x[i + 1])
    if len(x) % 2 == 1:
        result.append(x[-1])
    return np.array(result)


OPERATIONS["surreal_add"] = {
    "fn": surreal_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Surreal addition of consecutive pairs"
}


def surreal_multiply(x):
    """Multiply surreal numbers represented as consecutive pairs in x.
    Pairs up elements and multiplies: x[0]*x[1], x[2]*x[3], ...
    Surreal multiplication on dyadic rationals is ordinary multiplication.
    Input: array. Output: array."""
    result = []
    for i in range(0, len(x) - 1, 2):
        result.append(x[i] * x[i + 1])
    if len(x) % 2 == 1:
        result.append(x[-1])
    return np.array(result)


OPERATIONS["surreal_multiply"] = {
    "fn": surreal_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Surreal multiplication of consecutive pairs"
}


def surreal_negate(x):
    """Negate surreal numbers. In the surreal construction, -{X_L | X_R} = {-X_R | -X_L}.
    For dyadic rationals this is ordinary negation.
    Input: array. Output: array."""
    return -x


OPERATIONS["surreal_negate"] = {
    "fn": surreal_negate,
    "input_type": "array",
    "output_type": "array",
    "description": "Surreal negation of each element"
}


def surreal_birthday(x):
    """Compute the birthday (day of creation) for each surreal number in x.
    For a dyadic rational m/2^k in simplest form, the birthday is:
    - 0 has birthday 0
    - integers n have birthday |n|
    - m/2^k (k>0, m odd) has birthday |m|/2^k rounded up complexity.
    More precisely, birthday = number of steps to reach from 0 in Stern-Brocot tree.
    Input: array. Output: array."""
    results = []
    for val in x:
        if val == 0:
            results.append(0.0)
            continue
        m, k = _to_dyadic(val)
        # Simplify: remove common factors of 2
        while k > 0 and m % 2 == 0:
            m //= 2
            k -= 1
        if k == 0:
            # Integer: birthday = |m|
            results.append(float(abs(m)))
        else:
            # Dyadic rational m/2^k with m odd: birthday = |m| (depth in Stern-Brocot)
            # Actually the birthday is the depth in the surreal construction tree.
            # For m/2^k in lowest terms (m odd), birthday = floor(|m|/2^k) + k
            # More precisely: birthday = ceil(log2(|m|+1)) + k for proper dyadics
            # Simplification: the birthday equals the position in binary:
            # just count: integer part contributes floor(|val|), fractional contributes k
            results.append(float(abs(int(np.floor(abs(val)))) + k))
    return np.array(results)


OPERATIONS["surreal_birthday"] = {
    "fn": surreal_birthday,
    "input_type": "array",
    "output_type": "array",
    "description": "Birthday (creation day) of each surreal number"
}


def surreal_compare(x):
    """Compare consecutive pairs of surreal numbers.
    Returns -1, 0, or 1 for each pair: x[0] vs x[1], x[2] vs x[3], ...
    Input: array. Output: array."""
    result = []
    for i in range(0, len(x) - 1, 2):
        diff = x[i] - x[i + 1]
        if abs(diff) < 1e-15:
            result.append(0.0)
        elif diff < 0:
            result.append(-1.0)
        else:
            result.append(1.0)
    if len(x) % 2 == 1:
        result.append(0.0)  # unpaired element: no comparison
    return np.array(result)


OPERATIONS["surreal_compare"] = {
    "fn": surreal_compare,
    "input_type": "array",
    "output_type": "array",
    "description": "Compare consecutive pairs: -1 (less), 0 (equal), 1 (greater)"
}


def surreal_simplest_between(x):
    """Find the simplest surreal number between consecutive pairs.
    For each pair (a, b) with a < b, the simplest surreal between them is
    the one with smallest birthday. For dyadic rationals, this is found
    by binary search in the surreal number tree.
    Input: array. Output: array."""
    results = []
    for i in range(0, len(x) - 1, 2):
        a, b = min(x[i], x[i + 1]), max(x[i], x[i + 1])
        if abs(a - b) < 1e-15:
            results.append(a)
            continue
        # If an integer lies between a and b, it's simplest
        lo_int = int(np.ceil(a)) if a != int(a) else int(a) + 1
        if lo_int < b or (lo_int == b and b == int(b)):
            # Check if there's an integer strictly between
            candidate = int(np.ceil(a))
            if a < candidate < b:
                results.append(float(candidate))
                continue
            if a < candidate <= b and candidate < b:
                results.append(float(candidate))
                continue
        # If 0 is between a and b
        if a < 0 < b:
            results.append(0.0)
            continue
        # Binary search for simplest dyadic rational
        # Start with midpoint and simplify
        lo, hi = a, b
        for _ in range(53):  # precision of float64
            mid = (lo + hi) / 2.0
            # Round to simplest dyadic
            m, k = _to_dyadic(mid)
            while k > 0 and m % 2 == 0:
                m //= 2
                k -= 1
            candidate = m / (2.0 ** k)
            if a < candidate < b:
                results.append(float(candidate))
                break
            elif candidate <= a:
                lo = mid
            else:
                hi = mid
        else:
            results.append(float((a + b) / 2.0))
    if len(x) % 2 == 1:
        results.append(float(x[-1]))
    return np.array(results)


OPERATIONS["surreal_simplest_between"] = {
    "fn": surreal_simplest_between,
    "input_type": "array",
    "output_type": "array",
    "description": "Simplest surreal number strictly between each consecutive pair"
}


def dyadic_rational_to_surreal(x):
    """Interpret x as pairs (m, k) and convert to surreal values m / 2^k.
    Input: array [m0, k0, m1, k1, ...]. Output: array of surreal values."""
    results = []
    for i in range(0, len(x) - 1, 2):
        m = x[i]
        k = x[i + 1]
        results.append(float(m / (2.0 ** k)))
    if len(x) % 2 == 1:
        results.append(float(x[-1]))
    return np.array(results)


OPERATIONS["dyadic_rational_to_surreal"] = {
    "fn": dyadic_rational_to_surreal,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert (m, k) pairs to surreal values m/2^k"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
