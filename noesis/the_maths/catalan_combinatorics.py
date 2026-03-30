"""
Catalan Combinatorics — Dyck paths, non-crossing partitions, ballot sequences, triangulations

Connects to: [combinatorics, lattice_paths, tree_enumeration, partition_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from math import comb, factorial

FIELD_NAME = "catalan_combinatorics"
OPERATIONS = {}


def catalan_number(x):
    """Compute the n-th Catalan number C(n) = (2n choose n) / (n+1).
    Input: array. Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        n = max(int(val), 0)
        results.append(float(comb(2 * n, n) // (n + 1)))
    return np.array(results)


OPERATIONS["catalan_number"] = {
    "fn": catalan_number,
    "input_type": "array",
    "output_type": "array",
    "description": "n-th Catalan number C(n) = C(2n,n)/(n+1)"
}


def dyck_path_count(x):
    """Count Dyck paths of length 2n (same as Catalan number).
    Input: array. Output: array."""
    return catalan_number(x)


OPERATIONS["dyck_path_count"] = {
    "fn": dyck_path_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of Dyck paths of length 2n (equals C_n)"
}


def dyck_path_area(x):
    """Expected area under a random Dyck path of length 2n.
    E[area] = n*(n+1)/2 * C(n-1)/C(n) = n*(n+1)/(2*(2n-1)) * n for large n.
    Exact: sum of areas / C_n. We use the known formula: E[area] = n(n+1)/(2(n+1)) * C(n) ...
    Actually E[area under Dyck path of semilength n] = C(2n+1, n) - C(2n,n) = n*C(n)/(n+1).
    More precisely: total area over all Dyck paths of semilength n = 4^n - C(2n,n).
    Input: array. Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        n = max(int(val), 0)
        if n == 0:
            results.append(0.0)
        else:
            # Total area summed over all Dyck paths of semilength n = 4^n - C(2n,n)
            total_area = 4 ** n - comb(2 * n, n)
            cn = comb(2 * n, n) // (n + 1)
            results.append(float(total_area) / float(cn) if cn > 0 else 0.0)
    return np.array(results)


OPERATIONS["dyck_path_area"] = {
    "fn": dyck_path_area,
    "input_type": "array",
    "output_type": "array",
    "description": "Expected area under a random Dyck path of semilength n"
}


def non_crossing_partition_count(x):
    """Number of non-crossing partitions of [n], equals Catalan number C(n).
    Input: array. Output: array."""
    return catalan_number(x)


OPERATIONS["non_crossing_partition_count"] = {
    "fn": non_crossing_partition_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of non-crossing partitions of [n] (equals C_n)"
}


def ballot_sequence_count(x):
    """Number of ballot sequences of length 2n where candidate A always leads.
    This equals C(n) the Catalan number (bijection with Dyck paths).
    Input: array. Output: array."""
    return catalan_number(x)


OPERATIONS["ballot_sequence_count"] = {
    "fn": ballot_sequence_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of ballot sequences of length 2n (equals C_n)"
}


def triangulation_count(x):
    """Number of triangulations of a convex (n+2)-gon equals C(n).
    Input: array. Output: array."""
    return catalan_number(x)


OPERATIONS["triangulation_count"] = {
    "fn": triangulation_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of triangulations of a convex (n+2)-gon (equals C_n)"
}


def motzkin_number(x):
    """Compute the n-th Motzkin number M(n).
    M(n) = sum_{k=0}^{floor(n/2)} C(n, 2k) * C_k where C_k is Catalan.
    Input: array. Output: array."""
    results = []
    for val in np.asarray(x).ravel():
        n = max(int(val), 0)
        s = 0
        for k in range(n // 2 + 1):
            ck = comb(2 * k, k) // (k + 1)
            s += comb(n, 2 * k) * ck
        results.append(float(s))
    return np.array(results)


OPERATIONS["motzkin_number"] = {
    "fn": motzkin_number,
    "input_type": "array",
    "output_type": "array",
    "description": "n-th Motzkin number (Dyck paths with flat steps)"
}


def narayana_number(x):
    """Compute the Narayana number N(n, k) = (1/n)*C(n,k)*C(n,k-1).
    Input: matrix (each row [n, k]). Output: array."""
    arr = np.asarray(x)
    if arr.ndim == 1:
        # Interpret as pairs: [n1, k1, n2, k2, ...]
        if len(arr) % 2 != 0:
            arr = np.append(arr, 1.0)  # default k=1 for unpaired last element
        arr = arr.reshape(-1, 2)
    results = []
    for row in arr:
        n = max(int(row[0]), 1)
        k = max(int(row[1]), 1)
        k = min(k, n)
        val = comb(n, k) * comb(n, k - 1) // n
        results.append(float(val))
    return np.array(results)


OPERATIONS["narayana_number"] = {
    "fn": narayana_number,
    "input_type": "matrix",
    "output_type": "array",
    "description": "Narayana number N(n,k) = C(n,k)*C(n,k-1)/n"
}


def catalan_triangle(x):
    """Compute the Catalan triangle T(n,k) = (n-k+1)/(n+1) * C(n+k, k) for row n.
    Input: array (row indices). Output: matrix."""
    results = []
    max_n = 0
    rows_to_compute = []
    for val in np.asarray(x).ravel():
        n = max(int(val), 0)
        rows_to_compute.append(n)
        if n > max_n:
            max_n = n
    for n in rows_to_compute:
        row = []
        for k in range(max_n + 1):
            if k > n:
                row.append(0.0)
            else:
                # Ballot problem form: T(n,k) = (n-k+1)/(n+1) * C(n+k, k)
                val = (n - k + 1) * comb(n + k, k) // (n + 1)
                row.append(float(val))
        results.append(row)
    return np.array(results)


OPERATIONS["catalan_triangle"] = {
    "fn": catalan_triangle,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Catalan triangle T(n,k) = (n-k+1)/(n+1) * C(n+k,k)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
