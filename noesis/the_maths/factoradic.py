"""
Factoradic -- Position i has weight i!, digit range [0,i]. Natural encoding of permutations.

Connects to: [primorial_base, mixed_radix, bijective_bases, combinatorial_species]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import factorial

FIELD_NAME = "factoradic"
OPERATIONS = {}


def to_factoradic(x):
    """Convert integer to factoradic digits. Input: array (uses first element). Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    if n == 0:
        return np.array([0.0])
    digits = []
    i = 1
    while n > 0:
        digits.append(n % (i + 1))
        n //= (i + 1)
        i += 1
    return np.array(digits[::-1], dtype=float)


OPERATIONS["to_factoradic"] = {
    "fn": to_factoradic,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert integer to factoradic representation"
}


def from_factoradic(digits):
    """Convert factoradic digits to integer. Input: array. Output: scalar."""
    digits = np.asarray(digits, dtype=int)
    n = len(digits)
    result = 0
    for i, d in enumerate(digits):
        place = n - 1 - i
        result += int(d) * factorial(place)
    return float(result)


OPERATIONS["from_factoradic"] = {
    "fn": from_factoradic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Convert factoradic digits back to integer"
}


def factoradic_to_permutation(x):
    """Convert factoradic (Lehmer code) to permutation. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0]))) if len(x) > 0 else 0
    # Get factoradic digits
    fac_digits = to_factoradic(np.array([float(n)]))
    size = len(fac_digits)
    # Lehmer code to permutation
    available = list(range(size))
    perm = []
    for d in fac_digits:
        idx = min(int(d), len(available) - 1)
        perm.append(available[idx])
        available.pop(idx)
    return np.array(perm, dtype=float)


OPERATIONS["factoradic_to_permutation"] = {
    "fn": factoradic_to_permutation,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert factoradic (Lehmer code) to permutation"
}


def permutation_to_factoradic(x):
    """Convert permutation to factoradic (Lehmer code). Input: array. Output: array."""
    x = np.asarray(x, dtype=int)
    n = len(x)
    # Compute Lehmer code: for each position, count elements to the right that are smaller
    lehmer = []
    for i in range(n):
        count = 0
        for j in range(i + 1, n):
            if x[j] < x[i]:
                count += 1
        lehmer.append(count)
    return np.array(lehmer, dtype=float)


OPERATIONS["permutation_to_factoradic"] = {
    "fn": permutation_to_factoradic,
    "input_type": "array",
    "output_type": "array",
    "description": "Convert permutation to factoradic via Lehmer code"
}


def factoradic_add(x):
    """Add two integers via factoradic. Input: array (split half). Output: array."""
    x = np.asarray(x, dtype=float)
    mid = len(x) // 2
    a = int(round(from_factoradic(np.clip(x[:mid], 0, 20).astype(int))))
    b = int(round(from_factoradic(np.clip(x[mid:], 0, 20).astype(int))))
    return to_factoradic(np.array([float(a + b)]))


OPERATIONS["factoradic_add"] = {
    "fn": factoradic_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Add two factoradic numbers"
}


def factoradic_successor(x):
    """Compute factoradic of n+1. Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    val = int(round(abs(x[0])))
    return to_factoradic(np.array([float(val + 1)]))


OPERATIONS["factoradic_successor"] = {
    "fn": factoradic_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute factoradic successor (n+1)"
}


def nth_permutation(x):
    """Get the nth permutation of [0..k-1]. Input: array [n, k]. Output: array."""
    x = np.asarray(x, dtype=float)
    n = int(round(abs(x[0])))
    k = int(round(abs(x[1]))) if len(x) > 1 else 4
    k = max(1, min(k, 12))  # Limit size
    n = n % factorial(k)
    # Factoradic decomposition for k digits
    digits = []
    for i in range(k, 0, -1):
        f = factorial(i - 1)
        digits.append(n // f)
        n %= f
    # Lehmer code to permutation
    available = list(range(k))
    perm = []
    for d in digits:
        idx = min(int(d), len(available) - 1)
        perm.append(available[idx])
        available.pop(idx)
    return np.array(perm, dtype=float)


OPERATIONS["nth_permutation"] = {
    "fn": nth_permutation,
    "input_type": "array",
    "output_type": "array",
    "description": "Get the nth permutation of k elements using factoradic"
}


def permutation_rank(x):
    """Compute the rank (index) of a permutation. Input: array (permutation). Output: scalar."""
    x = np.asarray(x, dtype=int)
    n = len(x)
    lehmer = []
    for i in range(n):
        count = 0
        for j in range(i + 1, n):
            if x[j] < x[i]:
                count += 1
        lehmer.append(count)
    rank = 0
    for i, d in enumerate(lehmer):
        rank += d * factorial(n - 1 - i)
    return float(rank)


OPERATIONS["permutation_rank"] = {
    "fn": permutation_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compute rank (index) of a permutation via Lehmer code"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
