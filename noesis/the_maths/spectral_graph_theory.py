"""
Spectral Graph Theory — graph Laplacian eigenvalues, Cheeger inequality, Fiedler vector

Connects to: [linear_algebra, graph_theory, differential_geometry, optimization]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "spectral_graph_theory"
OPERATIONS = {}


def _adjacency_from_array(x):
    """Build a symmetric adjacency matrix from an array.
    Treats the array as edge weights of a path graph: edge i-(i+1) with weight |x[i]|."""
    arr = np.asarray(x, dtype=float)
    n = len(arr)
    adj = np.zeros((n, n), dtype=float)
    for i in range(n - 1):
        w = abs(arr[i])
        adj[i, i + 1] = w
        adj[i + 1, i] = w
    return adj


def graph_laplacian(x):
    """Compute the combinatorial graph Laplacian L = D - A for a path graph.
    Input: array. Output: matrix."""
    adj = _adjacency_from_array(x)
    degree = np.diag(adj.sum(axis=1))
    return degree - adj


OPERATIONS["graph_laplacian"] = {
    "fn": graph_laplacian,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Combinatorial Laplacian L = D - A for weighted path graph"
}


def laplacian_eigenvalues(x):
    """Eigenvalues of the graph Laplacian, sorted ascending.
    Input: array. Output: array."""
    L = graph_laplacian(x)
    eigvals = np.sort(np.real(np.linalg.eigvalsh(L)))
    return eigvals


OPERATIONS["laplacian_eigenvalues"] = {
    "fn": laplacian_eigenvalues,
    "input_type": "array",
    "output_type": "array",
    "description": "Sorted eigenvalues of the graph Laplacian"
}


def fiedler_vector(x):
    """Fiedler vector: eigenvector corresponding to the second smallest eigenvalue
    of the Laplacian (algebraic connectivity). Used for graph partitioning.
    Input: array. Output: array."""
    L = graph_laplacian(x)
    eigvals, eigvecs = np.linalg.eigh(L)
    # Sort by eigenvalue
    idx = np.argsort(eigvals)
    # Second smallest eigenvalue's eigenvector
    return eigvecs[:, idx[1]]


OPERATIONS["fiedler_vector"] = {
    "fn": fiedler_vector,
    "input_type": "array",
    "output_type": "array",
    "description": "Fiedler vector (eigenvector of second-smallest Laplacian eigenvalue)"
}


def algebraic_connectivity(x):
    """Algebraic connectivity: second smallest eigenvalue of the Laplacian (lambda_2).
    A graph is connected iff lambda_2 > 0.
    Input: array. Output: scalar."""
    eigvals = laplacian_eigenvalues(x)
    if len(eigvals) < 2:
        return 0.0
    return float(eigvals[1])


OPERATIONS["algebraic_connectivity"] = {
    "fn": algebraic_connectivity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Algebraic connectivity lambda_2 (second smallest Laplacian eigenvalue)"
}


def cheeger_bound(x):
    """Cheeger inequality bounds on the isoperimetric number h(G).
    lambda_2 / 2 <= h(G) <= sqrt(2 * lambda_2 * d_max).
    Returns array [lower_bound, upper_bound].
    Input: array. Output: array."""
    adj = _adjacency_from_array(x)
    d_max = float(np.max(adj.sum(axis=1)))
    lam2 = algebraic_connectivity(x)
    lower = lam2 / 2.0
    upper = np.sqrt(2.0 * lam2 * d_max) if d_max > 0 else 0.0
    return np.array([lower, upper])


OPERATIONS["cheeger_bound"] = {
    "fn": cheeger_bound,
    "input_type": "array",
    "output_type": "array",
    "description": "Cheeger inequality bounds [lambda_2/2, sqrt(2*lambda_2*d_max)]"
}


def spectral_gap(x):
    """Spectral gap: difference between two largest eigenvalues of adjacency matrix.
    Larger spectral gap indicates better expansion properties.
    Input: array. Output: scalar."""
    adj = _adjacency_from_array(x)
    eigvals = np.sort(np.real(np.linalg.eigvalsh(adj)))[::-1]  # descending
    if len(eigvals) < 2:
        return 0.0
    return float(eigvals[0] - eigvals[1])


OPERATIONS["spectral_gap"] = {
    "fn": spectral_gap,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spectral gap: difference of two largest adjacency eigenvalues"
}


def number_spanning_trees(x):
    """Number of spanning trees via Kirchhoff's matrix tree theorem:
    t(G) = (1/n) * product of nonzero Laplacian eigenvalues.
    Input: array. Output: scalar."""
    eigvals = laplacian_eigenvalues(x)
    n = len(eigvals)
    if n <= 1:
        return 1.0
    # Product of nonzero eigenvalues divided by n
    nonzero = eigvals[eigvals > 1e-10]
    if len(nonzero) == 0:
        return 0.0
    product = np.prod(nonzero)
    return float(product / n)


OPERATIONS["number_spanning_trees"] = {
    "fn": number_spanning_trees,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of spanning trees via Kirchhoff's theorem"
}


def graph_energy(x):
    """Graph energy: sum of absolute values of adjacency matrix eigenvalues.
    Input: array. Output: scalar."""
    adj = _adjacency_from_array(x)
    eigvals = np.linalg.eigvalsh(adj)
    return float(np.sum(np.abs(eigvals)))


OPERATIONS["graph_energy"] = {
    "fn": graph_energy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Graph energy: sum of |eigenvalues| of adjacency matrix"
}


def normalized_laplacian_spectrum(x):
    """Eigenvalues of the normalized Laplacian L_norm = D^{-1/2} L D^{-1/2}.
    All eigenvalues are in [0, 2]. For a connected graph, exactly one eigenvalue is 0.
    Input: array. Output: array."""
    adj = _adjacency_from_array(x)
    n = adj.shape[0]
    degrees = adj.sum(axis=1)
    # Handle isolated vertices
    d_inv_sqrt = np.zeros(n)
    for i in range(n):
        if degrees[i] > 1e-10:
            d_inv_sqrt[i] = 1.0 / np.sqrt(degrees[i])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L = np.diag(degrees) - adj
    L_norm = D_inv_sqrt @ L @ D_inv_sqrt
    eigvals = np.sort(np.real(np.linalg.eigvalsh(L_norm)))
    return eigvals


OPERATIONS["normalized_laplacian_spectrum"] = {
    "fn": normalized_laplacian_spectrum,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalues of the normalized Laplacian D^{-1/2} L D^{-1/2}"
}


def spectral_radius(x):
    """Spectral radius: largest absolute eigenvalue of the adjacency matrix.
    Input: array. Output: scalar."""
    adj = _adjacency_from_array(x)
    eigvals = np.linalg.eigvalsh(adj)
    return float(np.max(np.abs(eigvals)))


OPERATIONS["spectral_radius"] = {
    "fn": spectral_radius,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spectral radius: max |eigenvalue| of adjacency matrix"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
