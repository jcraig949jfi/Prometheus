"""
Constraint Feasibility — Validity checking operators for construct-check chains

Connects to: [optimization_landscapes, representation_converters, category_composition, invariant_extractors]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "constraint_feasibility"
OPERATIONS = {}


def is_probability_distribution(x):
    """Check if array is a valid probability distribution. Input: array. Output: scalar (0 or 1)."""
    if np.any(x < -1e-10):
        return 0.0
    if abs(np.sum(x) - 1.0) > 1e-6:
        return 0.0
    return 1.0


OPERATIONS["is_probability_distribution"] = {
    "fn": is_probability_distribution,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if array forms a valid probability distribution"
}


def is_positive_definite(x):
    """Check if matrix formed from array is positive definite. Input: array. Output: scalar (0 or 1)."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        return 0.0
    mat = x.reshape(n, n)
    mat = (mat + mat.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(mat)
    return 1.0 if np.all(eigenvalues > -1e-10) else 0.0


OPERATIONS["is_positive_definite"] = {
    "fn": is_positive_definite,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if matrix formed from array is positive semi-definite"
}


def is_connected_graph(x):
    """Check if adjacency matrix represents a connected graph. Input: array. Output: scalar (0 or 1)."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        return 0.0
    adj = x.reshape(n, n)
    adj = ((adj + adj.T) > 0).astype(float)
    np.fill_diagonal(adj, 0)
    # BFS
    visited = set([0])
    queue = [0]
    while queue:
        node = queue.pop(0)
        for neighbor in range(n):
            if adj[node, neighbor] > 0 and neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return 1.0 if len(visited) == n else 0.0


OPERATIONS["is_connected_graph"] = {
    "fn": is_connected_graph,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if adjacency matrix represents a connected graph"
}


def is_stochastic_matrix(x):
    """Check if matrix is (row) stochastic: non-negative with rows summing to 1. Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        return 0.0
    mat = x.reshape(n, n)
    if np.any(mat < -1e-10):
        return 0.0
    row_sums = mat.sum(axis=1)
    return 1.0 if np.allclose(row_sums, 1.0, atol=1e-6) else 0.0


OPERATIONS["is_stochastic_matrix"] = {
    "fn": is_stochastic_matrix,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if matrix is row-stochastic"
}


def is_symmetric(x):
    """Check if matrix is symmetric. Input: array. Output: scalar (0 or 1)."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        return 0.0
    mat = x.reshape(n, n)
    return 1.0 if np.allclose(mat, mat.T, atol=1e-10) else 0.0


OPERATIONS["is_symmetric"] = {
    "fn": is_symmetric,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if matrix formed from array is symmetric"
}


def is_orthogonal(x):
    """Check if matrix is orthogonal (Q^T Q = I). Input: array. Output: scalar (0 or 1)."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        return 0.0
    mat = x.reshape(n, n)
    product = mat.T @ mat
    return 1.0 if np.allclose(product, np.eye(n), atol=1e-6) else 0.0


OPERATIONS["is_orthogonal"] = {
    "fn": is_orthogonal,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if matrix is orthogonal"
}


def satisfies_triangle_inequality(x):
    """Check if all triples in array satisfy triangle inequality as distances. Input: array. Output: scalar."""
    n = len(x)
    if n < 3:
        return 1.0
    # Treat array as pairwise distances of a small set
    # Check consecutive triples
    for i in range(n - 2):
        a, b, c = abs(x[i]), abs(x[i + 1]), abs(x[i + 2])
        if a > b + c or b > a + c or c > a + b:
            return 0.0
    return 1.0


OPERATIONS["satisfies_triangle_inequality"] = {
    "fn": satisfies_triangle_inequality,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if consecutive triples satisfy triangle inequality"
}


def is_valid_permutation(x):
    """Check if array is a valid permutation of 0..n-1. Input: array. Output: scalar (0 or 1)."""
    n = len(x)
    rounded = np.round(x).astype(int)
    if np.any(rounded < 0) or np.any(rounded >= n):
        return 0.0
    return 1.0 if len(set(rounded)) == n else 0.0


OPERATIONS["is_valid_permutation"] = {
    "fn": is_valid_permutation,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if array is a valid permutation"
}


def constraint_violation_degree(x):
    """Continuous measure of how far array is from being a probability distribution. Input: array. Output: scalar."""
    negativity = np.sum(np.maximum(-x, 0))
    sum_deviation = abs(np.sum(x) - 1.0)
    return float(negativity + sum_deviation)


OPERATIONS["constraint_violation_degree"] = {
    "fn": constraint_violation_degree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Continuous measure of probability distribution constraint violation"
}


def feasibility_distance(x):
    """Distance to nearest feasible point (probability simplex). Input: array. Output: scalar."""
    # Project onto probability simplex and measure distance
    # Simplex projection via sorting algorithm
    n = len(x)
    u = np.sort(x)[::-1]
    cssv = np.cumsum(u)
    rho = np.max(np.where(u + (1.0 - cssv) / (np.arange(n) + 1) > 0)[0]) if np.any(u + (1.0 - cssv) / (np.arange(n) + 1) > 0) else 0
    theta = (cssv[rho] - 1.0) / (rho + 1)
    projected = np.maximum(x - theta, 0)
    return float(np.linalg.norm(x - projected))


OPERATIONS["feasibility_distance"] = {
    "fn": feasibility_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euclidean distance from array to probability simplex"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
