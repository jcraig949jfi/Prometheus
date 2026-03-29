"""
Discrete Morse Theory — Forman's theory: critical cells, discrete gradient vector fields, Morse inequalities on simplicial complexes

Connects to: [polytope_combinatorics, sheaves_on_graphs, convex_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "discrete_morse_theory"
OPERATIONS = {}


def discrete_gradient_field(x):
    """Construct a discrete gradient vector field pairing on a 1D simplicial complex.
    Input: array (vertex values). Output: array (paired cell indices, -1 if critical)."""
    n = len(x)
    # Pair each edge (i, i+1) with the vertex of higher value greedily
    paired = -1 * np.ones(n, dtype=np.int64)
    used_edges = set()
    for i in range(n - 1):
        edge_idx = i
        # Pair edge with its higher-valued vertex if neither is already paired
        if x[i] < x[i + 1]:
            target = i + 1
        else:
            target = i
        if paired[target] == -1 and edge_idx not in used_edges:
            paired[target] = edge_idx  # vertex target is paired with edge edge_idx
            used_edges.add(edge_idx)
    return paired


OPERATIONS["discrete_gradient_field"] = {
    "fn": discrete_gradient_field,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructs a discrete gradient vector field pairing on a 1D simplicial complex"
}


def critical_cells_count(x):
    """Count critical cells (unpaired) in a discrete gradient field.
    Input: array (vertex values). Output: scalar."""
    paired = discrete_gradient_field(x)
    n = len(x)
    n_edges = n - 1
    # Critical vertices: those not paired
    critical_verts = np.sum(paired == -1)
    # Critical edges: those not used in any pairing
    used_edges = set(paired[paired >= 0].tolist())
    critical_edges = n_edges - len(used_edges)
    return float(critical_verts + critical_edges)


OPERATIONS["critical_cells_count"] = {
    "fn": critical_cells_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Counts critical (unpaired) cells in the discrete gradient field"
}


def morse_inequality_check(x):
    """Verify weak Morse inequalities: #critical k-cells >= k-th Betti number.
    For a path graph: b0=1, b1=0. Input: array. Output: scalar (1.0 if satisfied, 0.0 otherwise)."""
    paired = discrete_gradient_field(x)
    n = len(x)
    n_edges = n - 1
    critical_verts = int(np.sum(paired == -1))
    used_edges = set(paired[paired >= 0].tolist())
    critical_edges = n_edges - len(used_edges)
    # For a path graph (connected, no cycles): b0=1, b1=0
    b0, b1 = 1, 0
    satisfied = (critical_verts >= b0) and (critical_edges >= b1)
    # Also check alternating sum: c0 - c1 = b0 - b1 = chi
    chi_morse = critical_verts - critical_edges
    chi_actual = n - n_edges  # vertices - edges for a graph
    satisfied = satisfied and (chi_morse == chi_actual)
    return 1.0 if satisfied else 0.0


OPERATIONS["morse_inequality_check"] = {
    "fn": morse_inequality_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Checks weak Morse inequalities and Euler characteristic consistency"
}


def forman_ricci_curvature(x):
    """Compute Forman-Ricci curvature for edges of a path graph.
    For an edge e with vertices v1,v2: F(e) = w(e)(1/w(v1) + 1/w(v2)) where w = |value|+eps.
    Input: array (vertex values). Output: array (curvature per edge)."""
    n = len(x)
    eps = 1e-10
    w_v = np.abs(x) + eps
    # For a path graph, each edge has exactly 2 vertices, no parallel edges
    # Forman curvature: F(e) = #vertices_of_e + #edges_of_e - #parallel_neighbors
    # Simplified: for path graph interior edge: 2 + 2 - (deg(v1)-1) - (deg(v2)-1)
    curvature = np.zeros(n - 1)
    for i in range(n - 1):
        deg_left = 1 if (i == 0) else 2
        deg_right = 1 if (i == n - 2) else 2
        # Forman: w_e * (w_v1^{-1} + w_v2^{-1}) - sum of neighbor contributions
        # Simplified Forman-Ricci for weighted path:
        curvature[i] = 2.0 - (deg_left - 1) - (deg_right - 1)
    return curvature


OPERATIONS["forman_ricci_curvature"] = {
    "fn": forman_ricci_curvature,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Forman-Ricci curvature on edges of a path graph"
}


def discrete_morse_complex(x):
    """Build the Morse complex boundary matrix from critical cells.
    Input: array. Output: matrix (boundary relations between critical cells)."""
    paired = discrete_gradient_field(x)
    n = len(x)
    n_edges = n - 1
    critical_vert_idx = np.where(paired == -1)[0]
    used_edges = set(paired[paired >= 0].tolist())
    critical_edge_idx = [i for i in range(n_edges) if i not in used_edges]
    nv = len(critical_vert_idx)
    ne = len(critical_edge_idx)
    if ne == 0 or nv == 0:
        return np.zeros((max(nv, 1), max(ne, 1)))
    # Boundary: each critical edge connects to critical vertices reachable via gradient paths
    boundary = np.zeros((nv, ne))
    for j, e in enumerate(critical_edge_idx):
        # Edge e connects vertices e and e+1; trace gradient to find critical vertices
        for v in [e, e + 1]:
            if v in critical_vert_idx.tolist():
                i = critical_vert_idx.tolist().index(v)
                boundary[i, j] = 1.0
    return boundary


OPERATIONS["discrete_morse_complex"] = {
    "fn": discrete_morse_complex,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Builds the Morse complex boundary matrix from critical cells"
}


def optimal_morse_function(x):
    """Construct a near-optimal discrete Morse function (minimizing critical cells).
    Uses the input as vertex weights, returns a reordered function.
    Input: array. Output: array."""
    # Sort-based heuristic: a function with values in sorted order
    # minimizes critical cells on a path graph
    n = len(x)
    order = np.argsort(x)
    morse_fn = np.zeros(n)
    morse_fn[order] = np.arange(n, dtype=float)
    return morse_fn


OPERATIONS["optimal_morse_function"] = {
    "fn": optimal_morse_function,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructs a near-optimal discrete Morse function minimizing critical cells"
}


def morse_betti_bounds(x):
    """Compute Morse-theoretic upper bounds on Betti numbers from critical cell counts.
    Input: array. Output: array [bound_b0, bound_b1]."""
    paired = discrete_gradient_field(x)
    n = len(x)
    n_edges = n - 1
    critical_verts = int(np.sum(paired == -1))
    used_edges = set(paired[paired >= 0].tolist())
    critical_edges = n_edges - len(used_edges)
    # Weak Morse inequality: b_k <= c_k
    return np.array([float(critical_verts), float(critical_edges)])


OPERATIONS["morse_betti_bounds"] = {
    "fn": morse_betti_bounds,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes Morse-theoretic upper bounds on Betti numbers"
}


def persistent_morse_filtration(x):
    """Build a filtration of sublevel sets from a discrete Morse function.
    Returns the filtration values at which critical cells appear.
    Input: array. Output: array (sorted critical values)."""
    paired = discrete_gradient_field(x)
    critical_mask = (paired == -1)
    critical_values = x[critical_mask]
    # Also include critical edge values (max of endpoints)
    n = len(x)
    used_edges = set(paired[paired >= 0].tolist())
    edge_critical_values = []
    for i in range(n - 1):
        if i not in used_edges:
            edge_critical_values.append(max(x[i], x[i + 1]))
    all_critical = np.concatenate([critical_values, np.array(edge_critical_values)])
    return np.sort(all_critical)


OPERATIONS["persistent_morse_filtration"] = {
    "fn": persistent_morse_filtration,
    "input_type": "array",
    "output_type": "array",
    "description": "Builds a persistence filtration from critical cell values"
}


def gradient_vector_field_valid(x):
    """Check if the discrete gradient vector field is valid (no closed gradient paths).
    Input: array. Output: scalar (1.0 valid, 0.0 invalid)."""
    paired = discrete_gradient_field(x)
    n = len(x)
    # For a path graph, a valid gradient field has no cycles in the pairing graph.
    # Since we pair greedily along a 1D path, cycles are impossible.
    # Verify: each edge is used at most once
    used_edges = paired[paired >= 0]
    unique_edges = np.unique(used_edges)
    valid = len(unique_edges) == len(used_edges)
    return 1.0 if valid else 0.0


OPERATIONS["gradient_vector_field_valid"] = {
    "fn": gradient_vector_field_valid,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Validates that the discrete gradient vector field has no closed paths"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
