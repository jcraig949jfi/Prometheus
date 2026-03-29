"""
Feynman Diagram Algebra — Graph polynomials and Feynman integral algebra (NOT pictures — algebra)

Connects to: [lattice_gauge_theory, tqft, tropical_qft]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "feynman_diagram_algebra"
OPERATIONS = {}


def _laplacian_matrix(n_vertices, edges):
    """Build graph Laplacian from edge list. edges: list of (i,j) tuples."""
    L = np.zeros((n_vertices, n_vertices))
    for i, j in edges:
        L[i, j] -= 1
        L[j, i] -= 1
        L[i, i] += 1
        L[j, j] += 1
    return L


def symanzik_first_polynomial(alpha):
    """First Symanzik polynomial U (also called Kirchhoff polynomial) for a one-loop graph.
    For a one-loop graph with n edges: U = sum of alpha_i (each alpha with one edge removed).
    U = alpha_1 + alpha_2 + ... + alpha_n.
    Input: alpha array (Schwinger parameters). Output: U scalar."""
    alpha = np.asarray(alpha, dtype=float)
    # For a one-loop (cycle) graph, U = sum of all alphas
    return np.float64(np.sum(alpha))

OPERATIONS["symanzik_first_polynomial"] = {
    "fn": symanzik_first_polynomial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "First Symanzik polynomial U for one-loop graph"
}


def symanzik_second_polynomial(alpha, p_ext=None):
    """Second Symanzik polynomial F for a one-loop graph with n edges and external momenta.
    F = sum_{i<j} alpha_i * alpha_j * s_{ij} where s_{ij} depends on momentum routing.
    For simplicity: F = sum_{i<j} alpha_i * alpha_j (unit external momenta).
    Input: alpha array. Output: F scalar."""
    alpha = np.asarray(alpha, dtype=float)
    n = len(alpha)
    F = 0.0
    for i in range(n):
        for j in range(i+1, n):
            F += alpha[i] * alpha[j]
    return np.float64(F)

OPERATIONS["symanzik_second_polynomial"] = {
    "fn": symanzik_second_polynomial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Second Symanzik polynomial F for one-loop graph"
}


def superficial_degree_divergence(n_loops, n_int_lines, d=4):
    """Superficial degree of divergence: omega = d*L - 2*I (scalar phi^4 theory).
    L = loops, I = internal lines. d = spacetime dimension.
    Input: array [L, I, ...]. Output: omega scalar."""
    arr = np.asarray(n_loops, dtype=float).ravel()
    L = int(arr[0])
    I = int(arr[1]) if len(arr) > 1 else int(n_int_lines)
    return np.float64(d * L - 2 * I)

OPERATIONS["superficial_degree_divergence"] = {
    "fn": lambda x: superficial_degree_divergence(x[0], x[1] if len(x)>1 else 2),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Superficial degree of divergence for scalar QFT diagram"
}


def symmetry_factor(n_vertices, n_edges_identical):
    """Symmetry factor 1/S for a Feynman diagram.
    For a diagram with n identical edges between same vertex pair: S = n!.
    For a self-loop: S = 2. General: product of local symmetries.
    Input: array [n_vertices, n_edges]. Output: S scalar."""
    arr = np.asarray(n_vertices, dtype=float).ravel()
    nv = int(arr[0])
    ne = int(arr[1]) if len(arr) > 1 else int(n_edges_identical)
    # Approximate: for a simple graph the symmetry factor comes from
    # automorphisms. For ne identical propagators: S = ne!
    import math
    S = float(math.factorial(min(ne, 20)))
    return np.float64(S)

OPERATIONS["symmetry_factor"] = {
    "fn": lambda x: symmetry_factor(x[0], x[1] if len(x)>1 else 1),
    "input_type": "array",
    "output_type": "scalar",
    "description": "Symmetry factor for Feynman diagram"
}


def one_loop_integral_scalar(p_sq, m_sq, d=4):
    """One-loop scalar bubble integral B_0(p^2, m^2) in d=4-2*epsilon.
    B_0 = integral d^d k / ((k^2+m^2)*((k+p)^2+m^2))
    For m>>p: B_0 ~ 1/(16*pi^2) * (2/epsilon - ln(m^2) + ...).
    Finite part at epsilon=0 with cutoff: B_0 ~ 1/(16*pi^2) * ln(Lambda^2/m^2).
    Simplified: return the finite combination.
    Input: p_sq array (external momentum squared). Output: integral array."""
    p_sq = np.asarray(p_sq, dtype=float)
    # For p^2 >> 4*m^2: B_0 ~ 1/(16*pi^2) * (2 - ln(p^2/m^2) + ...)
    # For p^2 << 4*m^2: B_0 ~ 1/(16*pi^2*m^2)
    # Use the exact result for equal masses:
    # B_0 = 1/(16*pi^2) * (2 - 2*sqrt(4*m^2/p^2 - 1)*arctan(1/sqrt(4*m^2/p^2-1)))
    # when p^2 < 4*m^2
    m_sq_val = float(m_sq) if not hasattr(m_sq, '__len__') else 1.0
    prefactor = 1.0 / (16.0 * np.pi**2)
    ratio = 4.0 * m_sq_val / np.clip(np.abs(p_sq), 1e-15, None)
    result = np.where(
        ratio > 1.0,
        prefactor * (2.0 - 2.0 * np.sqrt(ratio - 1.0) * np.arctan(1.0 / np.sqrt(ratio - 1.0))),
        prefactor * 2.0  # simplified for timelike
    )
    return result

OPERATIONS["one_loop_integral_scalar"] = {
    "fn": lambda x: one_loop_integral_scalar(x, 1.0),
    "input_type": "array",
    "output_type": "array",
    "description": "One-loop scalar bubble integral B_0(p^2, m^2)"
}


def graph_period(alpha):
    """Graph period (residue of the Feynman integral at the log-divergent point).
    For a one-loop n-gon in d=2n/(n-1) dimensions: period = Gamma(n - d/2) / prod(alpha)^{...}.
    Simplified for one-loop bubble (n=2): period = 1.
    For triangle (n=3): period = 1/(U^{d/2}) evaluated at alpha=1.
    Input: alpha array (Schwinger params at evaluation point). Output: period scalar."""
    alpha = np.asarray(alpha, dtype=float)
    n = len(alpha)
    U = np.sum(alpha)  # one-loop first Symanzik
    # Period of one-loop n-gon: Gamma(n-d/2) / U^{n-d/2} with d=2n/(n-1)
    # => exponent = n - n/(n-1) = n(n-2)/(n-1)
    if n <= 1:
        return np.float64(1.0)
    d_crit = 2.0 * n / (n - 1.0)
    exp = n - d_crit / 2.0
    from math import gamma as gamma_fn
    period = gamma_fn(exp) / U**exp
    return np.float64(period)

OPERATIONS["graph_period"] = {
    "fn": graph_period,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Graph period (residue at log-divergent point)"
}


def kirchhoff_polynomial(adj_matrix):
    """Kirchhoff (matrix-tree) polynomial: det of any cofactor of the Laplacian.
    Number of spanning trees = det(L_{00}) where L is the Laplacian.
    Input: flattened adjacency matrix or array. For 1D input, build cycle graph.
    Output: number of spanning trees (scalar)."""
    arr = np.asarray(adj_matrix, dtype=float)
    n = len(arr)
    # Interpret as a cycle graph with n vertices (each edge weight = arr[i])
    # Laplacian for weighted cycle:
    L = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        w = arr[i]
        L[i, i] += w
        L[j, j] += w
        L[i, j] -= w
        L[j, i] -= w
    # Kirchhoff polynomial = det of (n-1)x(n-1) minor
    cofactor = L[1:, 1:]
    return np.float64(np.linalg.det(cofactor))

OPERATIONS["kirchhoff_polynomial"] = {
    "fn": kirchhoff_polynomial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Kirchhoff polynomial (number of spanning trees) for weighted cycle"
}


def vacuum_bubble_count(n_vertices, valence=4):
    """Count vacuum bubble diagrams at given order in phi^valence theory.
    Number of vacuum diagrams with n vertices in phi^4: related to (4n-1)!! / S.
    Approximate: n_diagrams ~ (4n)! / (2^(2n) * (2n)! * n!).
    Input: n array (number of vertices). Output: count array."""
    n = np.asarray(n_vertices, dtype=float).astype(int)
    counts = np.zeros_like(n, dtype=float)
    for i, ni in enumerate(n.flat):
        ni = max(int(ni), 1)
        # (2*ni)! / (2^ni * ni!) for phi^4 vacuum bubbles at ni vertices
        from math import factorial
        if ni <= 10:
            num = factorial(2 * ni)
            den = 2**ni * factorial(ni)
            counts.flat[i] = num / den
        else:
            counts.flat[i] = np.exp(
                sum(np.log(range(1, 2*ni+1))) - ni*np.log(2) - sum(np.log(range(1, ni+1)))
            )
    return counts

OPERATIONS["vacuum_bubble_count"] = {
    "fn": vacuum_bubble_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Count of vacuum bubble diagrams in phi^4 theory"
}


def spanning_tree_contribution(edge_weights):
    """Sum over all spanning trees of a cycle graph: each tree contributes product of its edge weights.
    For a cycle with n edges, each spanning tree omits one edge.
    Contribution = sum_i product_{j!=i} w_j.
    Input: edge weight array. Output: total contribution scalar."""
    w = np.asarray(edge_weights, dtype=float)
    n = len(w)
    total_product = np.prod(w)
    # Each spanning tree of the cycle omits edge i: contribution = total_product / w_i
    contribution = np.sum(total_product / np.where(np.abs(w) < 1e-30, 1e-30, w))
    return np.float64(contribution)

OPERATIONS["spanning_tree_contribution"] = {
    "fn": spanning_tree_contribution,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Sum of spanning tree weight products for cycle graph"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
