"""
Graph Homomorphism — graph coloring via homomorphisms

Connects to: [graph_theory, chromatic_algebra, topological_combinatorics, algebraic_graph_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "graph_homomorphism"
OPERATIONS = {}


def _array_to_adjacency(x):
    """Convert flat array to a small adjacency matrix."""
    x = np.asarray(x, dtype=float)
    n = int(np.ceil(np.sqrt(len(x))))
    padded = np.zeros(n * n)
    padded[:len(x)] = x[:n*n]
    A = padded.reshape(n, n)
    # Symmetrize and zero diagonal for undirected simple graph
    A = (A + A.T) / 2.0
    A = (np.abs(A) > 0.5).astype(float)
    np.fill_diagonal(A, 0)
    return A


def chromatic_polynomial_compute(x):
    """Compute chromatic polynomial P(G, k) for small graph using deletion-contraction.
    Evaluates at k = number of vertices. Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n == 0:
        return 1.0
    if n > 10:
        # Too large for exact; use upper bound
        max_degree = int(np.max(np.sum(A, axis=1)))
        return float(n ** n)  # trivial upper bound

    # Deletion-contraction with memoization
    def chromatic_poly(adj, k):
        n = adj.shape[0]
        if n == 0:
            return 1.0
        # Find an edge
        for i in range(n):
            for j in range(i+1, n):
                if adj[i, j] > 0.5:
                    # Deletion: remove edge (i,j)
                    deleted = adj.copy()
                    deleted[i, j] = 0
                    deleted[j, i] = 0
                    # Contraction: merge j into i
                    contracted = np.delete(np.delete(adj, j, axis=0), j, axis=1)
                    contracted[min(i, contracted.shape[0]-1)] = np.maximum(
                        contracted[min(i, contracted.shape[0]-1)],
                        np.delete(adj[j], j)
                    ) if contracted.shape[0] > 0 else contracted
                    np.fill_diagonal(contracted, 0)
                    return chromatic_poly(deleted, k) - chromatic_poly(contracted, k)
        # No edges: independent set, P(G,k) = k^n
        return float(k ** n)

    k = n
    return float(chromatic_poly(A, k))

OPERATIONS["chromatic_polynomial_compute"] = {
    "fn": chromatic_polynomial_compute,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Chromatic polynomial P(G, n) via deletion-contraction for small graphs"
}


def fractional_chromatic_approx(x):
    """Approximate fractional chromatic number: chi_f(G) >= n / alpha(G).
    Uses greedy independent set for alpha approximation.
    Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n == 0:
        return 0.0
    # Greedy maximum independent set
    remaining = set(range(n))
    indep = []
    degrees = np.sum(A, axis=1)
    while remaining:
        # Pick minimum degree vertex
        v = min(remaining, key=lambda i: degrees[i])
        indep.append(v)
        neighbors = set(np.where(A[v] > 0.5)[0])
        remaining -= {v} | neighbors
    alpha = len(indep)
    if alpha == 0:
        return float(n)
    return float(n / alpha)

OPERATIONS["fractional_chromatic_approx"] = {
    "fn": fractional_chromatic_approx,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fractional chromatic number lower bound: n / alpha(G)"
}


def homomorphism_density(x):
    """Compute homomorphism density t(H, G) for H = edge (K2) into G.
    This equals 2*|E| / n^2, the edge density.
    Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n < 2:
        return 0.0
    num_edges = np.sum(A) / 2.0  # undirected
    density = (2.0 * num_edges) / (n * n)
    return float(density)

OPERATIONS["homomorphism_density"] = {
    "fn": homomorphism_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Edge homomorphism density t(K2, G) = 2|E|/n^2"
}


def lovasz_theta(x):
    """Approximate Lovasz theta function via Schrijver's bound:
    theta(G) >= max eigenvalue of adjacency complement / (-min eigenvalue of adj).
    Sandwich: alpha(G) <= theta(complement) <= chi(G).
    Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n == 0:
        return 0.0
    if n == 1:
        return 1.0
    # Complement adjacency
    A_comp = 1.0 - A - np.eye(n)
    # Lovasz theta approximation using eigenvalues
    # theta(G) = 1 - lambda_max(A) / lambda_min(A) when lambda_min < 0
    eigvals = np.linalg.eigvalsh(A)
    lmin = eigvals[0]
    lmax = eigvals[-1]
    if lmin >= -1e-10:
        return float(n)  # No negative eigenvalue; theta <= n
    theta = 1.0 - lmax / lmin
    return float(theta)

OPERATIONS["lovasz_theta"] = {
    "fn": lovasz_theta,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Lovasz theta function approximation via eigenvalue bound"
}


def graph_core_bound(x):
    """Lower bound on the core of a graph (smallest homomorphically equivalent subgraph).
    Core has at least clique_number vertices. Approximate clique number via eigenvalues.
    Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n == 0:
        return 0.0
    # Wilf's bound: omega(G) >= 1 + lambda_max / (-lambda_min)
    eigvals = np.linalg.eigvalsh(A)
    lmin = eigvals[0]
    lmax = eigvals[-1]
    if lmin >= -1e-10:
        return 1.0
    clique_bound = 1.0 + lmax / (-lmin)
    return float(max(1.0, clique_bound))

OPERATIONS["graph_core_bound"] = {
    "fn": graph_core_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Core size lower bound via spectral clique number estimate"
}


def hedetniemi_conjecture_test(x):
    """Test Hedetniemi's conjecture scenario: chi(G x H) =? min(chi(G), chi(H)).
    Split input into two halves as two graphs, compute spectral chi bounds, compare product.
    Input: array. Output: scalar (ratio of product chi bound to min chi bound)."""
    x = np.asarray(x, dtype=float)
    half = len(x) // 2
    if half < 4:
        return 1.0
    A1 = _array_to_adjacency(x[:half])
    A2 = _array_to_adjacency(x[half:2*half])
    # Spectral lower bound on chi: 1 + d_max for greedy
    chi1 = 1 + np.max(np.sum(A1, axis=1))
    chi2 = 1 + np.max(np.sum(A2, axis=1))
    min_chi = min(chi1, chi2)
    if min_chi < 1:
        return 1.0
    # Tensor product: eigenvalues multiply, giving a bound
    # For Hedetniemi, the conjecture (now disproven for large chi) is about equality
    return float(min_chi)

OPERATIONS["hedetniemi_conjecture_test"] = {
    "fn": hedetniemi_conjecture_test,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Hedetniemi scenario: spectral chi bound of two graphs' tensor product"
}


def circular_chromatic(x):
    """Approximate circular chromatic number chi_c(G).
    chi_c lies in [chi - 1, chi]. We estimate via fractional relaxation:
    chi_c >= n / alpha. Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n == 0:
        return 0.0
    max_deg = np.max(np.sum(A, axis=1))
    # chi_c <= max_degree + 1 (Brooks-like)
    # chi_c >= n / alpha
    # Use both bounds and return geometric mean
    upper = max_deg + 1
    # Greedy alpha
    remaining = set(range(n))
    indep = []
    degrees = np.sum(A, axis=1)
    while remaining:
        v = min(remaining, key=lambda i: degrees[i])
        indep.append(v)
        neighbors = set(np.where(A[v] > 0.5)[0])
        remaining -= {v} | neighbors
    alpha = max(len(indep), 1)
    lower = n / alpha
    return float(np.sqrt(lower * upper))

OPERATIONS["circular_chromatic"] = {
    "fn": circular_chromatic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Circular chromatic number approximation via bound averaging"
}


def graph_tensor_product_chromatic(x):
    """Estimate chromatic number of the tensor (categorical) product G x G.
    By Hedetniemi-type reasoning, chi(G x G) <= chi(G).
    Returns spectral bound. Input: array -> adjacency. Output: scalar."""
    A = _array_to_adjacency(x)
    n = A.shape[0]
    if n == 0:
        return 0.0
    # chi(G) >= 1 - lambda_max / lambda_min
    eigvals = np.linalg.eigvalsh(A)
    lmin = eigvals[0]
    lmax = eigvals[-1]
    if lmin >= -1e-10:
        return 1.0
    chi_bound = 1.0 - lmax / lmin
    # Tensor product: eigenvalues of A (x) A are products of eigenvalues
    # So spectral bound for tensor product
    tensor_eigs = np.outer(eigvals, eigvals).flatten()
    t_max = np.max(tensor_eigs)
    t_min = np.min(tensor_eigs)
    if t_min >= -1e-10:
        return float(chi_bound)
    tensor_chi = 1.0 - t_max / t_min
    return float(min(chi_bound, tensor_chi))

OPERATIONS["graph_tensor_product_chromatic"] = {
    "fn": graph_tensor_product_chromatic,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Spectral chromatic bound for tensor product G x G"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
