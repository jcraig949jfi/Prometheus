"""
Lambda Calculus — Church numerals, SKI combinators, beta reduction steps

Connects to: [automata_theory, type_theory, combinatorics, category_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "lambda_calculus"
OPERATIONS = {}


def church_numeral_to_int(x):
    """Convert array to Church numeral interpretation.
    Church numeral n applies f n times: the sum of the array rounded
    represents the numeral value.
    Input: array. Output: integer."""
    return int(max(0, round(np.sum(x))))


OPERATIONS["church_numeral_to_int"] = {
    "fn": church_numeral_to_int,
    "input_type": "array",
    "output_type": "integer",
    "description": "Interprets array sum as a Church numeral (non-negative integer)"
}


def church_successor(x):
    """Compute the successor of a Church numeral encoded as array.
    Adds 1 to each element, representing one additional application of f.
    Input: array. Output: array."""
    # Successor: n -> n+1. We increment the first element by 1.
    result = x.copy()
    result[0] = result[0] + 1.0
    return result


OPERATIONS["church_successor"] = {
    "fn": church_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes successor by adding 1 to the Church numeral encoding"
}


def church_add(x):
    """Church addition: split array into two halves representing two numerals,
    return array whose sum is the sum of both halves' sums.
    Input: array. Output: array."""
    mid = len(x) // 2
    a = np.sum(x[:mid])
    b = np.sum(x[mid:])
    # Result: array of length len(x) encoding a + b
    result = np.zeros(len(x))
    result[0] = a + b
    return result


OPERATIONS["church_add"] = {
    "fn": church_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Church addition: adds two numerals encoded as array halves"
}


def church_multiply(x):
    """Church multiplication: split array into two halves, return encoding of product.
    Input: array. Output: array."""
    mid = len(x) // 2
    a = np.sum(x[:mid])
    b = np.sum(x[mid:])
    result = np.zeros(len(x))
    result[0] = a * b
    return result


OPERATIONS["church_multiply"] = {
    "fn": church_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Church multiplication: multiplies two numerals encoded as array halves"
}


def ski_combinator_reduce(x):
    """Simulate SKI combinator reduction steps on array.
    S x y z = x z (y z). We model this as:
    For a 3+ element array [a, b, c, ...]: S-reduce to [a*c + b*c, ...]
    This captures the essence of S: applying and combining.
    Input: array. Output: array."""
    if len(x) < 3:
        return x.copy()
    result = np.zeros(max(1, len(x) - 2))
    # S combinator: S a b c = a c (b c)
    # We model numerically: first element = x[0]*x[2] + x[1]*x[2]
    result[0] = x[0] * x[2] + x[1] * x[2]
    # Remaining elements pass through
    for i in range(3, len(x)):
        result[i - 2] = x[i]
    return result


OPERATIONS["ski_combinator_reduce"] = {
    "fn": ski_combinator_reduce,
    "input_type": "array",
    "output_type": "array",
    "description": "Simulates one S-combinator reduction step on array elements"
}


def beta_reduction_count(x):
    """Estimate the number of beta reduction steps for a lambda term.
    Uses the structure of the array: count of pairs where x[i] > x[i+1]
    as a proxy for redex count (application sites needing reduction).
    Input: array. Output: integer."""
    if len(x) < 2:
        return 0
    # Count "redexes" as adjacent pairs where left > right (an application)
    count = 0
    for i in range(len(x) - 1):
        if x[i] > x[i + 1]:
            count += 1
    return int(count)


OPERATIONS["beta_reduction_count"] = {
    "fn": beta_reduction_count,
    "input_type": "array",
    "output_type": "integer",
    "description": "Estimates beta reduction steps from array structure (redex count)"
}


def lambda_term_depth(x):
    """Compute the nesting depth of a lambda term encoded as array.
    Positive values represent lambda abstractions (increase depth),
    negative values represent applications (decrease depth).
    Returns the maximum depth reached.
    Input: array. Output: integer."""
    depth = 0
    max_depth = 0
    for val in x:
        if val > 0:
            depth += 1
        elif val < 0:
            depth = max(0, depth - 1)
        max_depth = max(max_depth, depth)
    return int(max_depth)


OPERATIONS["lambda_term_depth"] = {
    "fn": lambda_term_depth,
    "input_type": "array",
    "output_type": "integer",
    "description": "Computes maximum nesting depth of lambda term encoded as array"
}


def fixed_point_combinator_approx(x):
    """Approximate the fixed point of a function f(x) = cos(x) iterated.
    Uses array values as starting points and iterates f until convergence.
    The Y combinator finds fixed points; here we find the numerical fixed
    point of cos, which is the Dottie number (~0.7391).
    Input: array. Output: array."""
    results = np.zeros(len(x))
    for i in range(len(x)):
        val = x[i]
        # Iterate cos until fixed point
        for _ in range(100):
            val = np.cos(val)
        results[i] = val
    return results


OPERATIONS["fixed_point_combinator_approx"] = {
    "fn": fixed_point_combinator_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Finds fixed point via iteration (Y-combinator analog), converges to Dottie number"
}


def de_bruijn_index(x):
    """Convert named variable references to de Bruijn indices.
    Array values represent variable binding distances. We normalize them
    to valid de Bruijn indices (non-negative integers relative to depth).
    Input: array. Output: array."""
    n = len(x)
    # De Bruijn indices: each element becomes its rank in sorted order
    # This is a canonical re-indexing (alpha-equivalence normalization)
    sorted_indices = np.argsort(np.argsort(x)).astype(float)
    return sorted_indices


OPERATIONS["de_bruijn_index"] = {
    "fn": de_bruijn_index,
    "input_type": "array",
    "output_type": "array",
    "description": "Converts array to de Bruijn index representation (rank-based re-indexing)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
