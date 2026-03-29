"""
Pseudo-Riemannian Geometry — Geometry with multiple time dimensions, signature (p,q)

Connects to: [causal_set_theory, spin_foam, noncommutative_geometry_connes]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "pseudo_riemannian"
OPERATIONS = {}


def metric_signature_classify(x):
    """Classify metric signature (p,q) from eigenvalue signs of a symmetric matrix.
    Input: array (flattened square matrix). Output: array [p, q]."""
    n = int(np.sqrt(len(x)))
    if n * n != len(x):
        n = int(np.ceil(np.sqrt(len(x))))
    mat = np.zeros((n, n))
    mat.flat[:len(x)] = x[:n*n]
    mat = (mat + mat.T) / 2
    eigvals = np.linalg.eigvalsh(mat)
    p = int(np.sum(eigvals > 1e-10))
    q = int(np.sum(eigvals < -1e-10))
    return np.array([p, q], dtype=float)


OPERATIONS["metric_signature_classify"] = {
    "fn": metric_signature_classify,
    "input_type": "array",
    "output_type": "array",
    "description": "Classify metric signature (p,q) from eigenvalue signs"
}


def geodesic_equation_step(x):
    """One step of geodesic equation: d^2 x^mu/dtau^2 + Gamma^mu_{ab} dx^a/dtau dx^b/dtau = 0.
    Input: array [position, velocity] in 1D with simple metric g=diag(x).
    Output: array of updated [position, velocity] after dt=0.01."""
    n = len(x) // 2
    pos = x[:n]
    vel = x[n:2*n]
    dt = 0.01
    # Simple Christoffel symbol approximation for diagonal metric g_ii = 1 + 0.1*pos_i
    g = 1.0 + 0.1 * pos
    dg = 0.1 * np.ones_like(pos)
    # Gamma^i_ii = dg_i / (2 g_i) for diagonal metric
    gamma = dg / (2.0 * g)
    accel = -gamma * vel * vel
    new_vel = vel + accel * dt
    new_pos = pos + new_vel * dt
    return np.concatenate([new_pos, new_vel])


OPERATIONS["geodesic_equation_step"] = {
    "fn": geodesic_equation_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One Euler step of the geodesic equation with diagonal metric"
}


def wave_equation_wellposedness(x):
    """Check well-posedness of wave equation for given signature.
    Input: array representing eigenvalues of metric. Output: scalar (1=well-posed, 0=ill-posed).
    Well-posed (hyperbolic) iff exactly one time dimension (one negative eigenvalue)."""
    eigvals = x
    n_neg = np.sum(eigvals < -1e-10)
    n_pos = np.sum(eigvals > 1e-10)
    # Well-posed (hyperbolic) if signature is (n-1,1) or (1,n-1)
    well_posed = 1.0 if (n_neg == 1 or n_pos == 1) and (n_neg + n_pos == len(x)) else 0.0
    return np.float64(well_posed)


OPERATIONS["wave_equation_wellposedness"] = {
    "fn": wave_equation_wellposedness,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if wave equation is well-posed for given metric eigenvalues"
}


def isometry_group_dimension(x):
    """Dimension of isometry group for constant-curvature pseudo-Riemannian manifold.
    Input: array of length >= 1, first element = manifold dimension n.
    Output: scalar n(n+1)/2 (maximal symmetry)."""
    n = int(x[0])
    return np.float64(n * (n + 1) / 2)


OPERATIONS["isometry_group_dimension"] = {
    "fn": isometry_group_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dimension of isometry group for maximally symmetric space: n(n+1)/2"
}


def causal_structure_type(x):
    """Determine causal structure type from metric signature eigenvalues.
    Input: array of eigenvalues. Output: scalar code.
    0=Riemannian(all+), 1=Lorentzian(one-), 2=ultrahyperbolic(multiple-)."""
    n_neg = int(np.sum(x < -1e-10))
    if n_neg == 0:
        return np.float64(0)
    elif n_neg == 1:
        return np.float64(1)
    else:
        return np.float64(2)


OPERATIONS["causal_structure_type"] = {
    "fn": causal_structure_type,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Classify causal structure: 0=Riemannian, 1=Lorentzian, 2=ultrahyperbolic"
}


def light_cone_topology(x):
    """Compute topology indicator of the light cone for signature (p,q).
    Input: array [p, q]. Output: scalar.
    Light cone in R^{p,q} is S^{p-1} x S^{q-1} (product of spheres), return (p-1)*(q-1) as topological indicator."""
    p = max(int(x[0]), 1)
    q = max(int(x[1]) if len(x) > 1 else 0, 0)
    # Light cone topology S^{p-1} x S^{q-1}: Euler characteristic
    # chi(S^n) = 1 + (-1)^n
    if q == 0:
        return np.float64(0)  # No light cone in Riemannian
    chi_p = 1 + (-1) ** (p - 1)
    chi_q = 1 + (-1) ** (q - 1)
    return np.float64(chi_p * chi_q)


OPERATIONS["light_cone_topology"] = {
    "fn": light_cone_topology,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euler characteristic of light cone topology S^{p-1} x S^{q-1}"
}


def signature_dependent_curvature(x):
    """Compute Ricci scalar for a diagonal metric given as array.
    Input: array of diagonal metric components g_ii.
    Output: scalar (approximate Ricci scalar for perturbation around flat)."""
    g = x.copy()
    g[g == 0] = 1.0
    n = len(g)
    # For diagonal metric g_ii, approximate Ricci scalar
    # R ~ -sum_i (d^2 g_ii / dx_i^2) / g_ii  (linearized)
    # Use finite differences treating array values as sampled metric
    if n < 3:
        return np.float64(0.0)
    d2g = np.zeros(n)
    for i in range(1, n - 1):
        d2g[i] = (g[i + 1] - 2 * g[i] + g[i - 1])
    R = -np.sum(d2g[1:-1] / g[1:-1])
    return np.float64(R)


OPERATIONS["signature_dependent_curvature"] = {
    "fn": signature_dependent_curvature,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Approximate Ricci scalar from diagonal metric components"
}


def ultrahyperbolic_check(x):
    """Check if metric is ultrahyperbolic (more than one time dimension).
    Input: array of metric eigenvalues. Output: scalar (1=ultrahyperbolic, 0=not)."""
    n_neg = int(np.sum(x < -1e-10))
    n_pos = int(np.sum(x > 1e-10))
    is_ultra = 1.0 if (n_neg >= 2 and n_pos >= 2) else 0.0
    return np.float64(is_ultra)


OPERATIONS["ultrahyperbolic_check"] = {
    "fn": ultrahyperbolic_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check if signature is ultrahyperbolic (p>=2, q>=2)"
}


def killing_vector_count(x):
    """Estimate number of Killing vectors from metric symmetry.
    Input: array (flattened square matrix representing metric).
    Output: scalar count of approximate symmetries."""
    n = int(np.sqrt(len(x)))
    if n * n > len(x):
        n = n - 1
    mat = np.zeros((n, n))
    mat.flat[:min(len(x), n*n)] = x[:n*n]
    mat = (mat + mat.T) / 2
    # Check how close to identity (maximally symmetric) metric is
    identity = np.eye(n)
    if np.allclose(mat, np.zeros_like(mat)):
        return np.float64(0)
    # Normalize
    scale = np.max(np.abs(mat))
    if scale > 0:
        normed = mat / scale
    else:
        return np.float64(0)
    # Deviation from scaled identity
    deviation = np.linalg.norm(normed - np.sign(normed[0, 0]) * identity) / n
    # Max Killing vectors = n(n+1)/2, reduce by deviation
    max_kv = n * (n + 1) / 2
    estimated = max_kv * np.exp(-deviation)
    return np.float64(np.round(estimated))


OPERATIONS["killing_vector_count"] = {
    "fn": killing_vector_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimate Killing vector count from metric symmetry structure"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
