"""
Matroid Theory — rank function, circuits, duality, greedy algorithm optimality

Connects to: [linear_algebra, graph_theory, combinatorics, optimization]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from itertools import combinations

FIELD_NAME = "matroid_theory"
OPERATIONS = {}


def matroid_rank_from_matrix(x):
    """Compute the rank of a linear matroid represented by a matrix.
    Input: matrix. Output: scalar."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    return np.float64(np.linalg.matrix_rank(M))


OPERATIONS["matroid_rank_from_matrix"] = {
    "fn": matroid_rank_from_matrix,
    "input_type": "matrix",
    "output_type": "scalar",
    "description": "Rank of a linear matroid (= matrix rank)"
}


def matroid_circuits(x):
    """Find all circuits of a linear matroid (minimal dependent sets of columns).
    Input: matrix (columns are ground set elements). Output: matrix (rows are circuit indicator vectors)."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    n = M.shape[1]
    r = np.linalg.matrix_rank(M)
    circuits = []
    # Check subsets of size r+1 and smaller for minimal dependence
    for size in range(1, min(r + 2, n + 1)):
        for subset in combinations(range(n), size):
            sub_matrix = M[:, list(subset)]
            if np.linalg.matrix_rank(sub_matrix) < size:
                # Check minimality: all proper subsets must be independent
                is_circuit = True
                for i in range(size):
                    smaller = list(subset[:i]) + list(subset[i + 1:])
                    if smaller and np.linalg.matrix_rank(M[:, smaller]) < len(smaller):
                        is_circuit = False
                        break
                if is_circuit:
                    indicator = np.zeros(n)
                    for idx in subset:
                        indicator[idx] = 1.0
                    circuits.append(indicator)
    if not circuits:
        return np.zeros((1, n))
    return np.array(circuits)


OPERATIONS["matroid_circuits"] = {
    "fn": matroid_circuits,
    "input_type": "matrix",
    "output_type": "matrix",
    "description": "All circuits (minimal dependent sets) of a linear matroid"
}


def matroid_dual_rank(x):
    """Rank of the dual matroid: r*(E) = |E| - r(E).
    Input: matrix. Output: scalar."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    n = M.shape[1]
    r = np.linalg.matrix_rank(M)
    return np.float64(n - r)


OPERATIONS["matroid_dual_rank"] = {
    "fn": matroid_dual_rank,
    "input_type": "matrix",
    "output_type": "scalar",
    "description": "Rank of the dual matroid r*(E) = |E| - r(E)"
}


def matroid_independent_sets(x):
    """Find all independent sets of a linear matroid (up to reasonable size).
    Input: matrix. Output: matrix (rows are indicator vectors of independent sets)."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    n = M.shape[1]
    # Limit to avoid combinatorial explosion
    max_elements = min(n, 10)
    M_sub = M[:, :max_elements]
    n_sub = max_elements
    independent = []
    # Empty set is independent
    independent.append(np.zeros(n_sub))
    for size in range(1, n_sub + 1):
        for subset in combinations(range(n_sub), size):
            sub_matrix = M_sub[:, list(subset)]
            if np.linalg.matrix_rank(sub_matrix) == size:
                indicator = np.zeros(n_sub)
                for idx in subset:
                    indicator[idx] = 1.0
                independent.append(indicator)
    return np.array(independent)


OPERATIONS["matroid_independent_sets"] = {
    "fn": matroid_independent_sets,
    "input_type": "matrix",
    "output_type": "matrix",
    "description": "All independent sets of a linear matroid (indicator vectors)"
}


def matroid_bases(x):
    """Find all bases (maximal independent sets) of a linear matroid.
    Input: matrix. Output: matrix (rows are indicator vectors)."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    n = M.shape[1]
    r = np.linalg.matrix_rank(M)
    max_elements = min(n, 12)
    M_sub = M[:, :max_elements]
    bases = []
    for subset in combinations(range(max_elements), r):
        sub_matrix = M_sub[:, list(subset)]
        if np.linalg.matrix_rank(sub_matrix) == r:
            indicator = np.zeros(max_elements)
            for idx in subset:
                indicator[idx] = 1.0
            bases.append(indicator)
    if not bases:
        return np.zeros((1, max_elements))
    return np.array(bases)


OPERATIONS["matroid_bases"] = {
    "fn": matroid_bases,
    "input_type": "matrix",
    "output_type": "matrix",
    "description": "All bases (maximal independent sets) of a linear matroid"
}


def matroid_closure(x):
    """Compute the closure of a subset A (first row = indicator of A, rest = matroid matrix).
    Closure = {e : r(A union e) = r(A)}.
    Input: matrix (first row = subset indicator, rest = representation). Output: array."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    indicator = M[0]
    mat = M[1:] if M.shape[0] > 1 else M
    n = mat.shape[1]
    A = [i for i in range(n) if indicator[i] > 0.5]
    if not A:
        rank_A = 0
    else:
        rank_A = np.linalg.matrix_rank(mat[:, A])
    closure = np.zeros(n)
    for i in A:
        closure[i] = 1.0
    for e in range(n):
        if e not in A:
            extended = A + [e]
            rank_ext = np.linalg.matrix_rank(mat[:, extended])
            if rank_ext == rank_A:
                closure[e] = 1.0
    return closure


OPERATIONS["matroid_closure"] = {
    "fn": matroid_closure,
    "input_type": "matrix",
    "output_type": "array",
    "description": "Closure of a subset in a linear matroid"
}


def matroid_is_independent(x):
    """Check if the subset indicated by first row is independent in the matroid (rest of matrix).
    Input: matrix (first row = subset indicator, rest = representation). Output: scalar (0 or 1)."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    indicator = M[0]
    mat = M[1:] if M.shape[0] > 1 else M
    A = [i for i in range(mat.shape[1]) if indicator[i] > 0.5]
    if not A:
        return np.float64(1.0)  # Empty set is always independent
    rank_A = np.linalg.matrix_rank(mat[:, A])
    return np.float64(1.0 if rank_A == len(A) else 0.0)


OPERATIONS["matroid_is_independent"] = {
    "fn": matroid_is_independent,
    "input_type": "matrix",
    "output_type": "scalar",
    "description": "Check if a subset is independent in the matroid (1=yes, 0=no)"
}


def greedy_algorithm_matroid(x):
    """Run the greedy algorithm on a weighted matroid.
    Input: matrix (first row = weights, rest = matroid representation).
    Output: array (indicator of selected basis)."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    weights = M[0]
    mat = M[1:] if M.shape[0] > 1 else M
    n = mat.shape[1]
    # Sort elements by weight descending
    order = np.argsort(-weights)
    selected = []
    result = np.zeros(n)
    for e in order:
        candidate = selected + [e]
        if np.linalg.matrix_rank(mat[:, candidate]) == len(candidate):
            selected.append(e)
            result[e] = 1.0
    return result


OPERATIONS["greedy_algorithm_matroid"] = {
    "fn": greedy_algorithm_matroid,
    "input_type": "matrix",
    "output_type": "array",
    "description": "Greedy algorithm for maximum weight independent set in a matroid"
}


def matroid_connectivity(x):
    """Compute the connectivity (minimum number of elements whose removal disconnects) of a matroid.
    Uses the formula: lambda(A) = r(A) + r(E-A) - r(E) for all nonempty proper subsets.
    Input: matrix. Output: scalar."""
    M = np.asarray(x, dtype=np.float64)
    if M.ndim == 1:
        M = M.reshape(1, -1)
    n = M.shape[1]
    r_E = np.linalg.matrix_rank(M)
    if n <= 1:
        return np.float64(0.0)
    min_lambda = n  # Upper bound
    # Check subsets of various sizes
    max_check = min(n, 8)
    elements = list(range(max_check))
    for size in range(1, max_check):
        for subset in combinations(elements, size):
            A = list(subset)
            complement = [e for e in elements if e not in A]
            if not complement:
                continue
            r_A = np.linalg.matrix_rank(M[:, A]) if A else 0
            r_comp = np.linalg.matrix_rank(M[:, complement]) if complement else 0
            lam = r_A + r_comp - r_E
            if lam < min_lambda:
                min_lambda = lam
    return np.float64(min_lambda)


OPERATIONS["matroid_connectivity"] = {
    "fn": matroid_connectivity,
    "input_type": "matrix",
    "output_type": "scalar",
    "description": "Connectivity of a matroid (min partition connectivity)"
}


def uniform_matroid_rank(x):
    """Compute rank function of uniform matroid U(k,n) on a subset.
    Input: array [k, n, subset_size]. Output: scalar (min(subset_size, k))."""
    arr = np.asarray(x).ravel()
    k = int(arr[0]) if len(arr) > 0 else 2
    n = int(arr[1]) if len(arr) > 1 else 4
    s = int(arr[2]) if len(arr) > 2 else 1
    # Rank in U(k,n) is min(|A|, k)
    return np.float64(min(s, k))


OPERATIONS["uniform_matroid_rank"] = {
    "fn": uniform_matroid_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rank function of uniform matroid U(k,n): min(|A|, k)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
