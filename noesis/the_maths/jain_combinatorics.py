"""
Jain Combinatorics — Permutation/combination formulas and transfinite classification from Jain mathematics

Connects to: [catuskoti_logic, navya_nyaya_logic, context_dependent_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "jain_combinatorics"
OPERATIONS = {}


def jain_permutations(x):
    """Jain-style permutations (vikalpa) for n items: n!. Input: array. Output: array."""
    from math import factorial
    return np.array([float(factorial(int(max(0, v)))) for v in x])


OPERATIONS["jain_permutations"] = {
    "fn": jain_permutations,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Jain vikalpa (permutations) n! for each element"
}


def jain_combinations(x):
    """Jain-style combinations (bhanga): 2^n subsets of n items. Input: array. Output: array."""
    return np.power(2.0, np.clip(x, 0, 50))


OPERATIONS["jain_combinations"] = {
    "fn": jain_combinations,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Jain bhanga (combinations) 2^n for each element"
}


def jain_ncr_formula(x):
    """Jain nCr where n = length of x, r = each element. Input: array. Output: array."""
    n = len(x)
    result = []
    for v in x:
        r = int(np.clip(v, 0, n))
        from math import comb
        result.append(float(comb(n, r)))
    return np.array(result)


OPERATIONS["jain_ncr_formula"] = {
    "fn": jain_ncr_formula,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes C(n, r) where n=len(x) and r=each element value"
}


def three_tier_infinity_classify(x):
    """Classify magnitudes into Jain three-tier system: 0=enumerable (<10^10),
    1=innumerable (10^10..10^100), 2=infinite (>10^100). Input: array. Output: array."""
    result = np.zeros_like(x)
    result[np.abs(x) >= 1e10] = 1.0
    result[np.abs(x) >= 1e100] = 2.0
    return result


OPERATIONS["three_tier_infinity_classify"] = {
    "fn": three_tier_infinity_classify,
    "input_type": "array",
    "output_type": "array",
    "description": "Classifies values into Jain enumerable/innumerable/infinite tiers"
}


def lokavibhaga_factorial(x):
    """Factorial using the Lokavibhaga method: iterative product. Input: array. Output: array."""
    result = []
    for v in x:
        n = int(np.clip(v, 0, 20))
        prod = 1.0
        for i in range(1, n + 1):
            prod *= i
        result.append(prod)
    return np.array(result)


OPERATIONS["lokavibhaga_factorial"] = {
    "fn": lokavibhaga_factorial,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes factorial via iterative product (Lokavibhaga style)"
}


def jain_power_sequence(x):
    """Jain ascending power sequence: x[i]^i for i=1..n. Input: array. Output: array."""
    indices = np.arange(1, len(x) + 1, dtype=float)
    return np.power(np.abs(x), indices)


OPERATIONS["jain_power_sequence"] = {
    "fn": jain_power_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes x[i]^i power sequence"
}


def jain_geometric_sum(x):
    """Geometric series sum: sum of x[0]^0 + x[0]^1 + ... + x[0]^(n-1) where n=len(x).
    Input: array. Output: scalar."""
    r = x[0] if len(x) > 0 else 1.0
    n = len(x)
    if np.abs(r - 1.0) < 1e-12:
        return float(n)
    return float((1.0 - r ** n) / (1.0 - r))


OPERATIONS["jain_geometric_sum"] = {
    "fn": jain_geometric_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes geometric series sum with ratio x[0] and n=len(x) terms"
}


def enumerable_bound_test(x):
    """Test which elements are within Jain 'enumerable' bounds (< 10^10).
    Returns 1.0 for enumerable, 0.0 for beyond. Input: array. Output: array."""
    return (np.abs(x) < 1e10).astype(float)


OPERATIONS["enumerable_bound_test"] = {
    "fn": enumerable_bound_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Tests if each element is within Jain enumerable bounds"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
