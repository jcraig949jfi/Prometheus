"""
Tropical Linear Algebra — linear algebra in the tropical semiring

Connects to: [optimization, algebraic_geometry, combinatorics, graph_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

In the max-plus tropical semiring: a (+) b = max(a,b), a (*) b = a + b.
The zero element is -inf, the unit element is 0.
"""

import numpy as np
from itertools import permutations

FIELD_NAME = "tropical_linear_algebra"
OPERATIONS = {}

NEG_INF = -np.inf


def _to_square(x):
    """Convert array to a square matrix."""
    n = int(np.round(np.sqrt(len(x))))
    if n * n != len(x):
        n = int(np.ceil(np.sqrt(len(x))))
        padded = np.full(n * n, NEG_INF)
        padded[:len(x)] = x
        return padded.reshape(n, n)
    return x.reshape(n, n)


def _trop_matmul(A, B):
    """Tropical matrix multiplication: C[i,j] = max_k (A[i,k] + B[k,j])."""
    n = A.shape[0]
    m = B.shape[1]
    C = np.full((n, m), NEG_INF)
    for i in range(n):
        for j in range(m):
            for k in range(A.shape[1]):
                val = A[i, k] + B[k, j]
                if val > C[i, j]:
                    C[i, j] = val
    return C


def tropical_matrix_rank(x):
    """Tropical rank: largest k such that the k x k tropical minors are not -inf.
    Input: array (flattened square matrix). Output: scalar."""
    A = _to_square(x)
    n = A.shape[0]
    rank = 0
    for k in range(1, n + 1):
        # Check all k x k submatrices
        from itertools import combinations
        found = False
        for rows in combinations(range(n), k):
            for cols in combinations(range(n), k):
                sub = A[np.ix_(rows, cols)]
                # Tropical determinant of sub
                det = NEG_INF
                for perm in permutations(range(k)):
                    val = sum(sub[i, perm[i]] for i in range(k))
                    if val > det:
                        det = val
                if det > NEG_INF:
                    found = True
                    break
            if found:
                break
        if found:
            rank = k
        else:
            break
    return float(rank)


OPERATIONS["tropical_matrix_rank"] = {
    "fn": tropical_matrix_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical rank of a matrix (max-plus semiring)"
}


def tropical_eigenvalue_max(x):
    """Maximum tropical eigenvalue: max over all cycles of (weight/length).
    For square matrix A, lambda = max over cycles c of (sum A[i,j] on c) / |c|.
    Input: array. Output: scalar."""
    A = _to_square(x)
    n = A.shape[0]
    # Karp's algorithm for maximum cycle mean
    # D[k][j] = max weight path of length k ending at j
    D = np.full((n + 1, n), NEG_INF)
    D[0, :] = 0.0
    for k in range(1, n + 1):
        for j in range(n):
            for i in range(n):
                if D[k - 1][i] > NEG_INF and A[i][j] > NEG_INF:
                    val = D[k - 1][i] + A[i][j]
                    if val > D[k][j]:
                        D[k][j] = val
    # lambda = max_j min_k (D[n][j] - D[k][j]) / (n - k)
    best = NEG_INF
    for j in range(n):
        if D[n][j] <= NEG_INF:
            continue
        worst_for_j = np.inf
        for k in range(n):
            if D[k][j] > NEG_INF:
                val = (D[n][j] - D[k][j]) / (n - k)
                if val < worst_for_j:
                    worst_for_j = val
        if worst_for_j < np.inf and worst_for_j > best:
            best = worst_for_j
    return float(best) if best > NEG_INF else 0.0


OPERATIONS["tropical_eigenvalue_max"] = {
    "fn": tropical_eigenvalue_max,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Maximum tropical eigenvalue (max cycle mean)"
}


def tropical_eigenvector(x):
    """Tropical eigenvector for the max eigenvalue via Kleene star (A - lambda*I)*.
    Input: array. Output: array."""
    A = _to_square(x)
    n = A.shape[0]
    lam = tropical_eigenvalue_max(x)
    # Subtract eigenvalue from diagonal (tropical: A[i,i] -= lam)
    B = A.copy()
    for i in range(n):
        B[i, i] = A[i, i] - lam if A[i, i] > NEG_INF else NEG_INF
    # Kleene star: I (+) B (+) B^2 (+) ... (+) B^(n-1)
    # Start with identity (tropical identity has 0 on diagonal, -inf elsewhere)
    star = np.full((n, n), NEG_INF)
    np.fill_diagonal(star, 0.0)
    Bk = star.copy()
    for _ in range(n - 1):
        Bk = _trop_matmul(Bk, B)
        star = np.maximum(star, Bk)
    # Eigenvector is any column of the Kleene star
    return star[:, 0]


OPERATIONS["tropical_eigenvector"] = {
    "fn": tropical_eigenvector,
    "input_type": "array",
    "output_type": "array",
    "description": "Tropical eigenvector via Kleene star"
}


def tropical_det(x):
    """Tropical determinant: max over permutations of sum A[i, sigma(i)].
    Input: array. Output: scalar."""
    A = _to_square(x)
    n = A.shape[0]
    best = NEG_INF
    for perm in permutations(range(n)):
        val = sum(A[i, perm[i]] for i in range(n))
        if val > best:
            best = val
    return float(best)


OPERATIONS["tropical_det"] = {
    "fn": tropical_det,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tropical determinant (max-weight perfect matching)"
}


def tropical_adjoint(x):
    """Tropical adjoint matrix: (adj A)[i,j] = tropical det of A with row j, col i removed.
    Input: array. Output: array."""
    A = _to_square(x)
    n = A.shape[0]
    adj = np.full((n, n), NEG_INF)
    for i in range(n):
        for j in range(n):
            # Remove row j, col i
            rows = [r for r in range(n) if r != j]
            cols = [c for c in range(n) if c != i]
            if len(rows) == 0:
                adj[i, j] = 0.0
                continue
            sub = A[np.ix_(rows, cols)]
            m = len(rows)
            best = NEG_INF
            for perm in permutations(range(m)):
                val = sum(sub[k, perm[k]] for k in range(m))
                if val > best:
                    best = val
            adj[i, j] = best
    return adj.flatten()


OPERATIONS["tropical_adjoint"] = {
    "fn": tropical_adjoint,
    "input_type": "array",
    "output_type": "array",
    "description": "Tropical adjoint (cofactor) matrix"
}


def tropical_system_solve(x):
    """Solve tropical linear system A (*) x = b in max-plus algebra.
    Uses A^# (adjoint) approach. First n*n entries = A, last n = b.
    Input: array. Output: array."""
    # Interpret: first part is matrix, last sqrt-sized part is vector
    n = int(np.round(np.sqrt(len(x))))
    if n * n + n <= len(x):
        A = x[:n * n].reshape(n, n)
        b = x[n * n:n * n + n]
    else:
        A = _to_square(x)
        n = A.shape[0]
        b = np.zeros(n)
    # x_j = min_i (b_i - A[i,j]) in max-plus dual
    result = np.zeros(n)
    for j in range(n):
        vals = []
        for i in range(n):
            if A[i, j] > NEG_INF:
                vals.append(b[i] - A[i, j])
        result[j] = min(vals) if vals else NEG_INF
    return result


OPERATIONS["tropical_system_solve"] = {
    "fn": tropical_system_solve,
    "input_type": "array",
    "output_type": "array",
    "description": "Solve tropical linear system via residuation"
}


def tropical_svd_approx(x):
    """Approximate tropical SVD: decompose A ~ U (*) S (*) V^T in max-plus.
    Returns singular values (diagonal of S). Input: array. Output: array."""
    A = _to_square(x)
    n = A.shape[0]
    # Tropical singular values approximate: eigenvalues of A^T (*) A
    At = A.T.copy()
    AtA = _trop_matmul(At, A)
    # Compute tropical eigenvalue for successive powers
    vals = []
    B = AtA.copy()
    for k in range(1, n + 1):
        trace_val = max(B[i, i] for i in range(n))
        vals.append(trace_val / k if trace_val > NEG_INF else 0.0)
        B = _trop_matmul(B, AtA)
    return np.array(sorted(vals, reverse=True))


OPERATIONS["tropical_svd_approx"] = {
    "fn": tropical_svd_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Approximate tropical singular values"
}


def tropical_polynomial_root(x):
    """Roots of a tropical polynomial: given coefficients a_i, the tropical roots
    are the breakpoints of the piecewise-linear function max_i(a_i + i*t).
    Input: array (coefficients). Output: array (roots)."""
    n = len(x)
    if n < 2:
        return np.array([0.0])
    # Tropical roots = differences of successive terms in concave hull
    # For coefficients a_0, ..., a_{n-1}, roots are a_{i} - a_{i+1} for
    # successive terms in the upper concave envelope
    # Build upper concave envelope
    points = [(i, x[i]) for i in range(n) if x[i] > NEG_INF]
    if len(points) < 2:
        return np.array([0.0])
    # Convex hull (upper) via Graham-like scan
    hull = []
    for p in sorted(points):
        while len(hull) >= 2:
            # Check if last point is below the line from hull[-2] to p
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            x3, y3 = p
            if (y2 - y1) * (x3 - x1) <= (y3 - y1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(p)
    # Roots are negative slopes between consecutive hull points
    roots = []
    for k in range(len(hull) - 1):
        slope = (hull[k + 1][1] - hull[k][1]) / (hull[k + 1][0] - hull[k][0])
        roots.append(-slope)
    return np.array(roots) if roots else np.array([0.0])


OPERATIONS["tropical_polynomial_root"] = {
    "fn": tropical_polynomial_root,
    "input_type": "array",
    "output_type": "array",
    "description": "Roots of a tropical polynomial (breakpoints of max)"
}


def hungarian_algorithm_cost(x):
    """Optimal assignment cost via a simplified Hungarian method.
    Input: array (flattened cost matrix). Output: scalar (min cost)."""
    A = _to_square(x)
    n = A.shape[0]
    # For small n, brute force
    if n <= 6:
        best = np.inf
        for perm in permutations(range(n)):
            cost = sum(A[i, perm[i]] for i in range(n))
            if cost < best:
                best = cost
        return float(best)
    # Fallback for larger: greedy approximation
    used_cols = set()
    total = 0.0
    for i in range(n):
        best_j = -1
        best_val = np.inf
        for j in range(n):
            if j not in used_cols and A[i, j] < best_val:
                best_val = A[i, j]
                best_j = j
        used_cols.add(best_j)
        total += best_val
    return float(total)


OPERATIONS["hungarian_algorithm_cost"] = {
    "fn": hungarian_algorithm_cost,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Minimum cost assignment (Hungarian algorithm)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
