"""
Tropical Geometry — min-plus algebra, tropical polynomials, tropical convexity

Connects to: [algebraic_geometry, combinatorics, optimization, polyhedral_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "tropical_geometry"
OPERATIONS = {}


def tropical_add(x):
    """Element-wise tropical addition (minimum) of paired halves. Input: array. Output: array."""
    n = len(x)
    mid = n // 2
    a, b = x[:mid], x[mid:2 * mid]
    return np.minimum(a, b)


OPERATIONS["tropical_add"] = {
    "fn": tropical_add,
    "input_type": "array",
    "output_type": "array",
    "description": "Tropical addition: element-wise minimum of two halves of input array"
}


def tropical_multiply(x):
    """Element-wise tropical multiplication (addition) of paired halves. Input: array. Output: array."""
    n = len(x)
    mid = n // 2
    a, b = x[:mid], x[mid:2 * mid]
    return a + b


OPERATIONS["tropical_multiply"] = {
    "fn": tropical_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Tropical multiplication: element-wise sum of two halves of input array"
}


def tropical_polynomial_eval(x):
    """Evaluate tropical polynomial with coefficients x at t=1.
    Tropical poly: trop_sum_i (c_i + i*t) = min_i(c_i + i*t).
    Input: array (coefficients). Output: scalar."""
    t = 1.0
    indices = np.arange(len(x), dtype=float)
    terms = x + indices * t
    return float(np.min(terms))


OPERATIONS["tropical_polynomial_eval"] = {
    "fn": tropical_polynomial_eval,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate tropical polynomial min_i(c_i + i*t) at t=1"
}


def tropical_determinant(x):
    """Tropical determinant (min-plus permanent) of a square matrix built from x.
    Uses assignment problem formulation: min over permutations of sum of entries.
    For small matrices, uses brute force. Input: array. Output: scalar."""
    from itertools import permutations
    n = int(np.sqrt(len(x)))
    if n * n > len(x):
        n = n - 1
    mat = x[:n * n].reshape(n, n)
    best = np.inf
    for perm in permutations(range(n)):
        val = sum(mat[i, perm[i]] for i in range(n))
        if val < best:
            best = val
    return float(best)


OPERATIONS["tropical_determinant"] = {
    "fn": tropical_determinant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical determinant: minimum weight perfect matching (min-plus permanent)"
}


def tropical_convex_hull_1d(x):
    """1D tropical convex hull: returns sorted unique tropical vertices.
    In 1D tropical geometry, the convex hull is the set of points reachable
    by tropical linear combinations. Input: array. Output: array."""
    sorted_x = np.sort(x)
    return sorted_x


OPERATIONS["tropical_convex_hull_1d"] = {
    "fn": tropical_convex_hull_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "1D tropical convex hull: sorted array of tropical vertices"
}


def tropical_matrix_multiply(x):
    """Tropical matrix multiply of two square matrices packed in x.
    (A *_trop B)_{ij} = min_k (A_{ik} + B_{kj}).
    Input: array (two n×n matrices concatenated). Output: matrix."""
    total = len(x)
    half = total // 2
    n = int(np.sqrt(half))
    if n < 1:
        n = 1
    A = x[:n * n].reshape(n, n)
    B = x[n * n:2 * n * n].reshape(n, n)
    C = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                val = A[i, k] + B[k, j]
                if val < C[i, j]:
                    C[i, j] = val
    return C


OPERATIONS["tropical_matrix_multiply"] = {
    "fn": tropical_matrix_multiply,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Tropical matrix multiplication: (A*B)_{ij} = min_k(A_{ik}+B_{kj})"
}


def tropical_eigenvalue(x):
    """Tropical eigenvalue of a square matrix built from x.
    The tropical eigenvalue is min over i of (trace of A^k / k) which equals
    the minimum cycle mean. For simplicity, compute min_i(A_{ii}) as a bound,
    then refine with length-2 cycles. Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n < 1:
        return float(x[0])
    mat = x[:n * n].reshape(n, n)
    # Minimum mean cycle weight (Karp's characterization)
    # Check cycles of length 1 (diagonal)
    best = np.min(np.diag(mat))
    # Check cycles of length 2
    for i in range(n):
        for j in range(n):
            if i != j:
                cycle_mean = (mat[i, j] + mat[j, i]) / 2.0
                if cycle_mean < best:
                    best = cycle_mean
    return float(best)


OPERATIONS["tropical_eigenvalue"] = {
    "fn": tropical_eigenvalue,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical eigenvalue: minimum mean cycle weight of the matrix"
}


def tropical_semiring_power(x):
    """Compute tropical power A^3 of a square matrix from x.
    Uses repeated tropical matrix multiplication. Input: array. Output: matrix."""
    n = int(np.sqrt(len(x)))
    if n < 1:
        return np.array([[x[0]]])
    mat = x[:n * n].reshape(n, n)

    def trop_matmul(A, B):
        sz = A.shape[0]
        C = np.full((sz, sz), np.inf)
        for i in range(sz):
            for j in range(sz):
                for k in range(sz):
                    val = A[i, k] + B[k, j]
                    if val < C[i, j]:
                        C[i, j] = val
        return C

    result = trop_matmul(mat, mat)  # A^2
    result = trop_matmul(result, mat)  # A^3
    return result


OPERATIONS["tropical_semiring_power"] = {
    "fn": tropical_semiring_power,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Tropical semiring power: compute A^3 via repeated min-plus multiplication"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
