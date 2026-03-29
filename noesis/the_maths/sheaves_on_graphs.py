"""
Sheaves on Graphs — Sheaf Laplacian, sheaf cohomology, opinion dynamics as sheaf diffusion

Connects to: [discrete_morse_theory, convex_geometry, renormalization_group]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "sheaves_on_graphs"
OPERATIONS = {}


def _path_graph_incidence(n):
    """Build incidence matrix for a path graph on n vertices (n-1 edges)."""
    B = np.zeros((n, n - 1))
    for i in range(n - 1):
        B[i, i] = -1.0
        B[i + 1, i] = 1.0
    return B


def _sheaf_stalks_from_array(x):
    """Interpret array as vertex stalk dimensions (all dim-1 here) and build
    a sheaf on the path graph. Returns (n_vertices, incidence, restriction_maps)."""
    n = len(x)
    B = _path_graph_incidence(n)
    # Restriction maps: for edge (i, i+1), maps from edge stalk to vertex stalks
    # Use x values as scaling for restriction maps (dim-1 stalks)
    restrictions = []
    for i in range(n - 1):
        # Linear map from edge stalk to vertex stalk (scalars here)
        r_tail = x[i] / (np.abs(x[i]) + 1e-10)
        r_head = x[i + 1] / (np.abs(x[i + 1]) + 1e-10)
        restrictions.append((r_tail, r_head))
    return n, B, restrictions


def sheaf_laplacian(x):
    """Compute the sheaf Laplacian L_F = delta^T * delta for a sheaf on a path graph.
    Input: array (vertex values as stalk data). Output: matrix."""
    n = len(x)
    # Coboundary map delta: C^0 -> C^1
    # For scalar stalks with restriction maps r_{e,v}
    _, _, restrictions = _sheaf_stalks_from_array(x)
    delta = np.zeros((n - 1, n))
    for i in range(n - 1):
        r_tail, r_head = restrictions[i]
        delta[i, i] = -r_tail
        delta[i, i + 1] = r_head
    # Sheaf Laplacian
    L = delta.T @ delta
    return L


OPERATIONS["sheaf_laplacian"] = {
    "fn": sheaf_laplacian,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes the sheaf Laplacian L_F = delta^T delta on a path graph"
}


def sheaf_coboundary(x):
    """Build the sheaf coboundary operator delta: C^0(F) -> C^1(F).
    Input: array. Output: matrix."""
    n = len(x)
    _, _, restrictions = _sheaf_stalks_from_array(x)
    delta = np.zeros((n - 1, n))
    for i in range(n - 1):
        r_tail, r_head = restrictions[i]
        delta[i, i] = -r_tail
        delta[i, i + 1] = r_head
    return delta


OPERATIONS["sheaf_coboundary"] = {
    "fn": sheaf_coboundary,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Builds the sheaf coboundary operator delta: C^0 -> C^1"
}


def sheaf_cohomology_dimension(x):
    """Compute dimension of H^0(G, F) = ker(delta) for the sheaf on a path graph.
    Input: array. Output: scalar."""
    delta = sheaf_coboundary(x)
    # H^0 = ker(delta)
    _, s, _ = np.linalg.svd(delta)
    tol = 1e-10
    rank = np.sum(s > tol)
    n = delta.shape[1]
    nullity = n - rank  # dim ker(delta)
    return float(nullity)


OPERATIONS["sheaf_cohomology_dimension"] = {
    "fn": sheaf_cohomology_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes dimension of sheaf cohomology H^0(G, F) = ker(delta)"
}


def sheaf_diffusion_step(x):
    """One step of sheaf diffusion: x_{t+1} = x_t - dt * L_F * x_t.
    Input: array. Output: array."""
    L = sheaf_laplacian(x)
    dt = 0.1
    x_new = x - dt * L @ x
    return x_new


OPERATIONS["sheaf_diffusion_step"] = {
    "fn": sheaf_diffusion_step,
    "input_type": "array",
    "output_type": "array",
    "description": "Performs one step of sheaf Laplacian diffusion"
}


def opinion_dynamics_sheaf(x):
    """Simulate opinion dynamics as sheaf diffusion (Laplacian consensus).
    Runs multiple diffusion steps. Input: array. Output: array (converged opinions)."""
    n = len(x)
    # Use standard graph Laplacian for opinion dynamics (constant sheaf)
    L = np.zeros((n, n))
    for i in range(n - 1):
        L[i, i] += 1
        L[i + 1, i + 1] += 1
        L[i, i + 1] -= 1
        L[i + 1, i] -= 1
    dt = 0.1
    opinions = x.copy()
    for _ in range(50):
        opinions = opinions - dt * L @ opinions
    return opinions


OPERATIONS["opinion_dynamics_sheaf"] = {
    "fn": opinion_dynamics_sheaf,
    "input_type": "array",
    "output_type": "array",
    "description": "Simulates opinion dynamics via sheaf diffusion to consensus"
}


def sheaf_consistency_radius(x):
    """Compute the consistency radius: ||delta(x)||, measuring how far x is
    from being a global section. Input: array. Output: scalar."""
    delta = sheaf_coboundary(x)
    dx = delta @ x
    return float(np.linalg.norm(dx))


OPERATIONS["sheaf_consistency_radius"] = {
    "fn": sheaf_consistency_radius,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes consistency radius ||delta(x)|| measuring deviation from global section"
}


def cellular_sheaf_from_graph(x):
    """Construct a cellular sheaf data structure from vertex values on a path graph.
    Returns the sheaf Laplacian eigenvalues as a spectral descriptor.
    Input: array. Output: array (eigenvalues of sheaf Laplacian)."""
    L = sheaf_laplacian(x)
    eigvals = np.linalg.eigvalsh(L)
    return eigvals


OPERATIONS["cellular_sheaf_from_graph"] = {
    "fn": cellular_sheaf_from_graph,
    "input_type": "array",
    "output_type": "array",
    "description": "Constructs cellular sheaf and returns sheaf Laplacian eigenvalues"
}


def sheaf_restriction_map(x):
    """Compute the restriction maps for each edge as a matrix.
    For scalar stalks, returns array of restriction scalars [r_tail, r_head] per edge.
    Input: array. Output: matrix (n-1 x 2)."""
    _, _, restrictions = _sheaf_stalks_from_array(x)
    n = len(x)
    R = np.zeros((n - 1, 2))
    for i, (rt, rh) in enumerate(restrictions):
        R[i, 0] = rt
        R[i, 1] = rh
    return R


OPERATIONS["sheaf_restriction_map"] = {
    "fn": sheaf_restriction_map,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Computes restriction maps for each edge of the sheaf"
}


def harmonic_sheaf_representative(x):
    """Find the harmonic representative in H^0: projection onto ker(L_F).
    Input: array. Output: array."""
    L = sheaf_laplacian(x)
    eigvals, eigvecs = np.linalg.eigh(L)
    tol = 1e-8
    # Project onto eigenspace with eigenvalue ~0
    harmonic = np.zeros_like(x)
    for i in range(len(eigvals)):
        if eigvals[i] < tol:
            harmonic += np.dot(eigvecs[:, i], x) * eigvecs[:, i]
    return harmonic


OPERATIONS["harmonic_sheaf_representative"] = {
    "fn": harmonic_sheaf_representative,
    "input_type": "array",
    "output_type": "array",
    "description": "Projects onto the harmonic (kernel of sheaf Laplacian) representative"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
