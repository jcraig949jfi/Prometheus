"""
Domain Theory — Scott domains, continuous lattices, fixed-point computation, denotational semantics

Connects to: [formal_logic_systems, abstract_rewriting, descriptive_complexity]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "domain_theory"
OPERATIONS = {}


def scott_topology_open_test(x):
    """Test if a subset is Scott-open in a flat domain.
    A set U is Scott-open if it is upward closed and inaccessible by directed suprema.
    For a flat domain on reals, the non-bottom elements form a Scott-open set.
    Input: array (values, 0 = bottom). Output: scalar (1 if all non-bottom, 0 otherwise)."""
    # In a flat domain, {non-bottom} is Scott-open
    # Test: is the given set entirely non-bottom?
    return float(np.all(np.abs(x) > 1e-10))


OPERATIONS["scott_topology_open_test"] = {
    "fn": scott_topology_open_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Test if input set is Scott-open in a flat domain (all non-bottom)"
}


def continuous_lattice_way_below(x):
    """Compute the way-below relation on [0,1] interval domain.
    In [0,1] with usual order, a << b iff a < b (for a > 0), and 0 << everything.
    Returns array: way_below[i] = number of elements x[j] that are way-below x[i].
    Input: array. Output: array."""
    n = len(x)
    result = np.zeros(n)
    for i in range(n):
        count = 0
        for j in range(n):
            if j != i and x[j] < x[i]:
                count += 1
            elif j != i and x[j] == 0:
                count += 1
        result[i] = count
    return result


OPERATIONS["continuous_lattice_way_below"] = {
    "fn": continuous_lattice_way_below,
    "input_type": "array",
    "output_type": "array",
    "description": "Count elements way-below each element in the interval domain [0,1]"
}


def kleene_chain_fixpoint(x):
    """Compute the least fixed point of f(v) = x * v + (1-x) via Kleene iteration.
    Starting from 0, iterate f until convergence. For |x| < 1, fixpoint = (1-x)/(1-x) = 1/(1+... ).
    Actually fixpoint of f(v) = a*v + b is b/(1-a) when |a|<1.
    Input: array. Output: array of fixpoints per element."""
    a = np.clip(x, -0.99, 0.99)
    b = 1.0 - a
    # Kleene iteration: start at 0, iterate
    v = np.zeros_like(a)
    for _ in range(200):
        v_new = a * v + b
        if np.max(np.abs(v_new - v)) < 1e-12:
            break
        v = v_new
    return v


OPERATIONS["kleene_chain_fixpoint"] = {
    "fn": kleene_chain_fixpoint,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute least fixed point of f(v) = x*v + (1-x) via Kleene chain iteration"
}


def denotational_factorial(x):
    """Denotational semantics of factorial: compute factorial for each element (rounded to int).
    Uses iterative computation. Input: array. Output: array."""
    vals = np.clip(np.abs(np.round(x)), 0, 20).astype(int)
    results = np.zeros(len(x))
    for i, v in enumerate(vals):
        f = 1
        for j in range(1, v + 1):
            f *= j
        results[i] = float(f)
    return results


OPERATIONS["denotational_factorial"] = {
    "fn": denotational_factorial,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute factorial of each element (denotational semantics of recursive def)"
}


def domain_product(x):
    """Compute the product domain: pair each adjacent element (x[0],x[1]), (x[2],x[3])...
    Return the componentwise max of each pair (join in product domain).
    Input: array. Output: array."""
    n = len(x)
    pairs = n // 2
    if pairs == 0:
        return x.copy()
    result = np.zeros(pairs)
    for i in range(pairs):
        result[i] = max(x[2 * i], x[2 * i + 1])
    return result


OPERATIONS["domain_product"] = {
    "fn": domain_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Product domain: componentwise join (max) of adjacent pairs"
}


def domain_function_space_size(x):
    """Estimate the size of the function space [D -> D] for a flat domain of size n.
    For a flat domain with n proper elements + bottom, the continuous functions
    number (n+1)^n + n (roughly). We return log2 of this.
    Input: array (len = domain size). Output: scalar."""
    n = len(x)
    # |[D_bot -> D_bot]| for flat D with n elements = (n+1)^n + ... but simplified:
    # Each strict function maps n elements to n+1 choices, plus bottom maps to anything
    # Monotone continuous: bottom -> anything, each element -> anything
    # = (n+1)^(n+1) total monotone functions on flat domain
    size_log = (n + 1) * np.log2(n + 1)
    return float(size_log)


OPERATIONS["domain_function_space_size"] = {
    "fn": domain_function_space_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Log2 of function space size for flat domain of given cardinality"
}


def scott_continuous_check(x):
    """Check if a function (given by samples) is Scott-continuous.
    A monotone function on a chain is Scott-continuous iff it preserves suprema of directed sets.
    We check monotonicity on sorted input as a necessary condition.
    Input: array (function values at sorted domain points). Output: scalar (0 or 1)."""
    sorted_x = np.sort(x)
    # Treat x as f applied to sorted domain; check if f-values are monotone
    # (necessary for Scott-continuity)
    diffs = np.diff(x)
    return float(np.all(diffs >= -1e-10))


OPERATIONS["scott_continuous_check"] = {
    "fn": scott_continuous_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check monotonicity (necessary for Scott-continuity) of function samples"
}


def fixed_point_iteration_count(x):
    """Count iterations to reach fixed point of f(v) = cos(v * x[0]) starting from 0.
    Input: array (uses x[0] as parameter). Output: scalar (iteration count)."""
    a = x[0] if len(x) > 0 else 1.0
    v = 0.0
    for i in range(1, 1001):
        v_new = np.cos(v * a)
        if abs(v_new - v) < 1e-10:
            return float(i)
        v = v_new
    return 1000.0


OPERATIONS["fixed_point_iteration_count"] = {
    "fn": fixed_point_iteration_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count iterations for cos(v*a) to reach a fixed point from v=0"
}


def flat_domain_lift(x):
    """Lift values into a flat domain: map 0 -> bottom (NaN), others stay.
    This models the lifted flat domain D_bottom. Input: array. Output: array."""
    result = x.copy()
    result[np.abs(x) < 1e-10] = np.nan
    return result


OPERATIONS["flat_domain_lift"] = {
    "fn": flat_domain_lift,
    "input_type": "array",
    "output_type": "array",
    "description": "Lift to flat domain: map zero-elements to bottom (NaN)"
}


def domain_approximation_chain(x):
    """Build an approximation chain: return cumulative maxima (ascending chain in info order).
    In domain theory, an approximation chain x0 <= x1 <= ... converges to sup.
    Input: array. Output: array (cumulative max)."""
    return np.maximum.accumulate(x)


OPERATIONS["domain_approximation_chain"] = {
    "fn": domain_approximation_chain,
    "input_type": "array",
    "output_type": "array",
    "description": "Build ascending approximation chain via cumulative maximum"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
