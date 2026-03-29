"""
Partition Theory — integer partitions, partition function p(n), Ferrers diagrams, conjugate partitions

Connects to: [number_theory, combinatorics, q_series, modular_forms, catalan_combinatorics]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb

FIELD_NAME = "partition_theory"
OPERATIONS = {}


def _partition_table(n_max):
    """Compute partition function p(k) for k = 0..n_max via dynamic programming."""
    p = [0] * (n_max + 1)
    p[0] = 1
    for k in range(1, n_max + 1):
        for j in range(k, n_max + 1):
            p[j] += p[j - k]
    return p


def partition_function_p(x):
    """Compute the partition function p(n) for each element.
    Input: array. Output: array."""
    vals = [max(int(v), 0) for v in np.asarray(x).ravel()]
    n_max = max(vals) if vals else 0
    table = _partition_table(n_max)
    return np.array([float(table[v]) for v in vals])


OPERATIONS["partition_function_p"] = {
    "fn": partition_function_p,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of integer partitions p(n)"
}


def partitions_into_distinct(x):
    """Count partitions of n into distinct parts via DP.
    Input: array. Output: array."""
    vals = [max(int(v), 0) for v in np.asarray(x).ravel()]
    n_max = max(vals) if vals else 0
    # DP: each part used at most once
    dp = [0] * (n_max + 1)
    dp[0] = 1
    for k in range(1, n_max + 1):
        for j in range(n_max, k - 1, -1):
            dp[j] += dp[j - k]
    return np.array([float(dp[v]) for v in vals])


OPERATIONS["partitions_into_distinct"] = {
    "fn": partitions_into_distinct,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of partitions of n into distinct parts"
}


def partition_conjugate(x):
    """Given a partition as a sorted descending array, compute its conjugate.
    Input: array (a partition in descending order). Output: array."""
    parts = sorted([int(v) for v in np.asarray(x).ravel() if v > 0], reverse=True)
    if not parts:
        return np.array([0.0])
    # Conjugate: column lengths of Ferrers diagram
    max_part = parts[0]
    conjugate = []
    for i in range(1, max_part + 1):
        conjugate.append(float(sum(1 for p in parts if p >= i)))
    return np.array(conjugate)


OPERATIONS["partition_conjugate"] = {
    "fn": partition_conjugate,
    "input_type": "array",
    "output_type": "array",
    "description": "Conjugate partition (transpose of Ferrers diagram)"
}


def partition_rank(x):
    """Compute the rank of a partition: largest part minus number of parts.
    Input: array (partition in descending order). Output: scalar."""
    parts = sorted([int(v) for v in np.asarray(x).ravel() if v > 0], reverse=True)
    if not parts:
        return np.float64(0.0)
    return np.float64(parts[0] - len(parts))


OPERATIONS["partition_rank"] = {
    "fn": partition_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rank of a partition (largest part - number of parts)"
}


def partition_crank(x):
    """Compute the crank of a partition.
    If no 1s: crank = largest part.
    If has 1s: crank = (# parts > # of 1s) - (# of 1s).
    Input: array (partition). Output: scalar."""
    parts = sorted([int(v) for v in np.asarray(x).ravel() if v > 0], reverse=True)
    if not parts:
        return np.float64(0.0)
    num_ones = sum(1 for p in parts if p == 1)
    if num_ones == 0:
        return np.float64(parts[0])
    else:
        mu = sum(1 for p in parts if p > num_ones)
        return np.float64(mu - num_ones)


OPERATIONS["partition_crank"] = {
    "fn": partition_crank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Crank of a partition (Andrews-Garvan)"
}


def durfee_square_size(x):
    """Size of the Durfee square: largest d such that partition has >= d parts each >= d.
    Input: array (partition). Output: scalar."""
    parts = sorted([int(v) for v in np.asarray(x).ravel() if v > 0], reverse=True)
    d = 0
    for i, p in enumerate(parts):
        if p >= i + 1:
            d = i + 1
        else:
            break
    return np.float64(d)


OPERATIONS["durfee_square_size"] = {
    "fn": durfee_square_size,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Size of the Durfee square of a partition"
}


def euler_pentagonal_coefficients(x):
    """Coefficients of Euler's pentagonal number theorem:
    prod(1-q^k) = sum (-1)^k q^{k(3k-1)/2}.
    Input: array (number of terms). Output: array."""
    n = max(int(np.asarray(x).ravel()[0]), 1)
    n = min(n, 500)
    coeffs = np.zeros(n)
    # Pentagonal numbers: k(3k-1)/2 for k = 0, +-1, +-2, ...
    for k in range(-n, n + 1):
        idx = k * (3 * k - 1) // 2
        if 0 <= idx < n:
            coeffs[idx] += (-1) ** k
    return coeffs


OPERATIONS["euler_pentagonal_coefficients"] = {
    "fn": euler_pentagonal_coefficients,
    "input_type": "array",
    "output_type": "array",
    "description": "Coefficients of Euler's pentagonal number theorem expansion"
}


def restricted_partition_count(x):
    """Count partitions of n with parts <= m. Input as pairs [n, m].
    Input: array (interpreted as [n1, m1, n2, m2, ...]). Output: array."""
    arr = np.asarray(x).ravel()
    if len(arr) % 2 != 0:
        arr = np.append(arr, arr[-1])
    results = []
    for i in range(0, len(arr), 2):
        n = max(int(arr[i]), 0)
        m = max(int(arr[i + 1]), 1)
        # DP for partitions of n with parts <= m
        dp = [0] * (n + 1)
        dp[0] = 1
        for k in range(1, m + 1):
            for j in range(k, n + 1):
                dp[j] += dp[j - k]
        results.append(float(dp[n]))
    return np.array(results)


OPERATIONS["restricted_partition_count"] = {
    "fn": restricted_partition_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of partitions of n with parts at most m"
}


def partition_generating_function_coeffs(x):
    """Coefficients of the partition generating function prod 1/(1-q^k) up to q^n.
    Input: array (first element = n). Output: array."""
    n = max(int(np.asarray(x).ravel()[0]), 0)
    n = min(n, 500)
    table = _partition_table(n)
    return np.array([float(v) for v in table])


OPERATIONS["partition_generating_function_coeffs"] = {
    "fn": partition_generating_function_coeffs,
    "input_type": "array",
    "output_type": "array",
    "description": "Coefficients [p(0), p(1), ..., p(n)] of partition generating function"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
