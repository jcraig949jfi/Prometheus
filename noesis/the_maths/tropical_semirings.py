"""
Tropical Semirings — min-plus, max-plus, shortest path algebra

Connects to: [valuations, graph_theory, optimization, linear_algebra]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "tropical_semirings"
OPERATIONS = {}

_INF = 1e18


def _to_square_matrix(x):
    """Reshape flat array into a square matrix, padding if needed."""
    n = int(np.ceil(np.sqrt(len(x))))
    padded = np.full(n * n, _INF)
    padded[:len(x)] = x
    return padded.reshape(n, n), n


def minplus_matrix_multiply(x):
    """Min-plus (tropical) matrix multiplication. Reshapes input into two square
    matrices and computes C[i,j] = min_k(A[i,k] + B[k,j]).
    Input: array. Output: matrix."""
    half = len(x) // 2
    if half == 0:
        return np.array([[x[0]]])
    A, n = _to_square_matrix(x[:half])
    B, m = _to_square_matrix(x[half:])
    s = min(n, m)
    A, B = A[:s, :s], B[:s, :s]
    C = np.full((s, s), _INF)
    for i in range(s):
        for j in range(s):
            for k in range(s):
                C[i, j] = min(C[i, j], A[i, k] + B[k, j])
    return C


OPERATIONS["minplus_matrix_multiply"] = {
    "fn": minplus_matrix_multiply,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Min-plus tropical matrix multiplication"
}


def maxplus_matrix_multiply(x):
    """Max-plus (tropical) matrix multiplication.
    C[i,j] = max_k(A[i,k] + B[k,j]). Input: array. Output: matrix."""
    half = len(x) // 2
    if half == 0:
        return np.array([[x[0]]])
    A, n = _to_square_matrix(x[:half])
    B, m = _to_square_matrix(x[half:])
    s = min(n, m)
    A[:s, :s][A[:s, :s] >= _INF] = -_INF
    B[:s, :s][B[:s, :s] >= _INF] = -_INF
    A, B = A[:s, :s], B[:s, :s]
    C = np.full((s, s), -_INF)
    for i in range(s):
        for j in range(s):
            for k in range(s):
                C[i, j] = max(C[i, j], A[i, k] + B[k, j])
    return C


OPERATIONS["maxplus_matrix_multiply"] = {
    "fn": maxplus_matrix_multiply,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Max-plus tropical matrix multiplication"
}


def minplus_vector_convolve(x):
    """Min-plus convolution of two vectors. Split x in half: a, b.
    c[k] = min_{i+j=k} (a[i] + b[j]). Input: array. Output: array."""
    half = len(x) // 2
    if half == 0:
        return x.copy()
    a = x[:half]
    b = x[half:2 * half]
    n = len(a)
    m = len(b)
    c = np.full(n + m - 1, _INF)
    for i in range(n):
        for j in range(m):
            c[i + j] = min(c[i + j], a[i] + b[j])
    return c


OPERATIONS["minplus_vector_convolve"] = {
    "fn": minplus_vector_convolve,
    "input_type": "array",
    "output_type": "array",
    "description": "Min-plus convolution of two vectors (split from input)"
}


def maxplus_eigenvalue(x):
    """Max-plus eigenvalue (maximum cycle mean) of a matrix.
    lambda = max over cycles C of (sum of weights / length of cycle).
    Uses Karp's algorithm on the square matrix. Input: array. Output: scalar."""
    A, n = _to_square_matrix(x)
    A[A >= _INF] = -_INF
    # Karp's algorithm: compute D[k][v] = max weight of k-edge path ending at v
    D = np.full((n + 1, n), -_INF)
    D[0, :] = 0.0
    for k in range(1, n + 1):
        for v in range(n):
            for u in range(n):
                if D[k - 1][u] > -_INF and A[u][v] > -_INF:
                    D[k][v] = max(D[k][v], D[k - 1][u] + A[u][v])
    # lambda = max_v min_k (D[n][v] - D[k][v]) / (n - k)
    lam = -_INF
    for v in range(n):
        if D[n][v] <= -_INF:
            continue
        local_min = _INF
        for k in range(n):
            if D[k][v] > -_INF:
                local_min = min(local_min, (D[n][v] - D[k][v]) / (n - k))
        if local_min < _INF:
            lam = max(lam, local_min)
    return float(lam) if lam > -_INF else 0.0


OPERATIONS["maxplus_eigenvalue"] = {
    "fn": maxplus_eigenvalue,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Max-plus eigenvalue (maximum cycle mean) via Karp's algorithm"
}


def shortest_path_matrix(x):
    """All-pairs shortest paths via Floyd-Warshall on min-plus matrix.
    Input: array (flattened adjacency). Output: matrix."""
    A, n = _to_square_matrix(x)
    D = A.copy()
    for i in range(n):
        D[i, i] = 0.0
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i, k] + D[k, j] < D[i, j]:
                    D[i, j] = D[i, k] + D[k, j]
    return D


OPERATIONS["shortest_path_matrix"] = {
    "fn": shortest_path_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "All-pairs shortest paths via Floyd-Warshall in min-plus algebra"
}


def tropical_rank(x):
    """Tropical rank (Barvinok rank) approximation. The tropical rank is the
    minimum r such that A = B (+) C where B is n x r and C is r x n in
    min-plus. We approximate via checking column tropical dependence.
    Input: array. Output: integer."""
    A, n = _to_square_matrix(x)
    # Simple heuristic: tropical rank >= number of tropically independent columns
    # Column j is tropically dependent on others if for all i:
    # A[i,j] = min_k!=j (A[i,k] + c_k) for some constants c_k
    # We use a greedy approach
    rank = 0
    used = []
    for j in range(n):
        if not used:
            used.append(j)
            rank += 1
            continue
        # Check if column j is a tropical linear combination of used columns
        # Try: for each candidate column u, compute shift = min_i (A[i,j] - A[i,u])
        dependent = False
        if len(used) >= 1:
            best = np.full(n, _INF)
            for u in used:
                shift = np.min(A[:, j] - A[:, u])
                candidate = A[:, u] + shift
                best = np.minimum(best, candidate)
            if np.allclose(best, A[:, j], atol=1e-10):
                dependent = True
        if not dependent:
            used.append(j)
            rank += 1
    return int(rank)


OPERATIONS["tropical_rank"] = {
    "fn": tropical_rank,
    "input_type": "array",
    "output_type": "integer",
    "description": "Approximate tropical rank of a matrix"
}


def minplus_permanent(x):
    """Tropical permanent in min-plus: min over permutations of sum A[i,sigma(i)].
    This is the assignment problem. For small n, use brute force.
    Input: array. Output: scalar."""
    A, n = _to_square_matrix(x)
    if n > 10:
        n = 10
        A = A[:n, :n]
    # Hungarian-like: for small n, use itertools
    from itertools import permutations
    if n > 8:
        # Use greedy approximation for larger n
        remaining = list(range(n))
        total = 0.0
        for i in range(n):
            best_j = min(remaining, key=lambda j: A[i, j])
            total += A[i, best_j]
            remaining.remove(best_j)
        return float(total)
    best = _INF
    for perm in permutations(range(n)):
        s = sum(A[i, perm[i]] for i in range(n))
        best = min(best, s)
    return float(best)


OPERATIONS["minplus_permanent"] = {
    "fn": minplus_permanent,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Min-plus permanent (optimal assignment cost)"
}


def maxplus_determinant(x):
    """Tropical determinant in max-plus: max over permutations of sum A[i,sigma(i)]
    (with sign, but in tropical algebra typically unsigned).
    Input: array. Output: scalar."""
    A, n = _to_square_matrix(x)
    A[A >= _INF] = -_INF
    if n > 10:
        n = 10
        A = A[:n, :n]
    from itertools import permutations
    if n > 8:
        remaining = list(range(n))
        total = 0.0
        for i in range(n):
            best_j = max(remaining, key=lambda j: A[i, j])
            total += A[i, best_j]
            remaining.remove(best_j)
        return float(total)
    best = -_INF
    for perm in permutations(range(n)):
        s = sum(A[i, perm[i]] for i in range(n))
        best = max(best, s)
    return float(best)


OPERATIONS["maxplus_determinant"] = {
    "fn": maxplus_determinant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Max-plus determinant (max weight matching)"
}


def tropical_halfspace(x):
    """Determine membership of a point in a tropical halfspace.
    A tropical halfspace is {y : min_j(a_j + y_j) <= min_j(b_j + y_j)}.
    Split x into 3 parts: a, b, y. Returns 1.0 if in halfspace, 0.0 otherwise.
    Input: array. Output: scalar."""
    third = len(x) // 3
    if third == 0:
        return 1.0
    a = x[:third]
    b = x[third:2 * third]
    y = x[2 * third:3 * third]
    lhs = np.min(a + y)
    rhs = np.min(b + y)
    return 1.0 if lhs <= rhs else 0.0


OPERATIONS["tropical_halfspace"] = {
    "fn": tropical_halfspace,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical halfspace membership test"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
