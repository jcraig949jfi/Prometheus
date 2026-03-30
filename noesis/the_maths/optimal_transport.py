"""
Optimal Transport — Wasserstein distance, Sinkhorn algorithm, earth mover's distance

Connects to: [measure_theory, optimization, probability_theory, linear_programming]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "optimal_transport"
OPERATIONS = {}


def wasserstein_1d(x):
    """1D Wasserstein-1 distance between two empirical distributions.
    Input: array of length 2n, first half is samples from P, second half from Q. Output: scalar.
    W_1 = integral |F_P^{-1}(t) - F_Q^{-1}(t)| dt = (1/n)*sum|sort(P)-sort(Q)|.
    """
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    p = np.sort(x[:n])
    q = np.sort(x[n:2*n])
    # Handle unequal sizes by interpolating
    if len(p) != len(q):
        m = min(len(p), len(q))
        p = p[:m]
        q = q[:m]
    return np.float64(np.mean(np.abs(p - q)))


OPERATIONS["wasserstein_1d"] = {
    "fn": wasserstein_1d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "1D Wasserstein-1 (earth mover) distance between two empirical distributions"
}


def sinkhorn_distance(x):
    """Sinkhorn distance between two discrete distributions using entropic regularization.
    Input: array of length 2n, first half is distribution a, second half is b. Output: scalar.
    Uses a ground cost |i-j| and regularization epsilon=0.1.
    """
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    a = np.abs(x[:n]) + 1e-12
    b = np.abs(x[n:2*n]) + 1e-12
    a = a / a.sum()
    b = b / b.sum()

    na, nb = len(a), len(b)
    # Cost matrix: |i - j|
    C = np.abs(np.arange(na)[:, None] - np.arange(nb)[None, :]).astype(float)
    eps = 0.1

    K = np.exp(-C / eps)
    u = np.ones(na)
    for _ in range(100):
        v = b / (K.T @ u + 1e-300)
        u = a / (K @ v + 1e-300)

    P = np.diag(u) @ K @ np.diag(v)
    return np.float64(np.sum(P * C))


OPERATIONS["sinkhorn_distance"] = {
    "fn": sinkhorn_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Sinkhorn (entropy-regularized) optimal transport distance"
}


def earth_mover_1d(x):
    """Earth mover's distance for 1D distributions via CDF difference.
    Input: array of length 2n. Output: scalar.
    EMD = sum |CDF_P(i) - CDF_Q(i)| for the discrete case.
    """
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    a = np.abs(x[:n]) + 1e-12
    b = np.abs(x[n:2*n]) + 1e-12
    a = a / a.sum()
    b = b / b.sum()
    cdf_a = np.cumsum(a)
    cdf_b = np.cumsum(b)
    return np.float64(np.sum(np.abs(cdf_a - cdf_b)))


OPERATIONS["earth_mover_1d"] = {
    "fn": earth_mover_1d,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Earth mover's distance between two 1D discrete distributions"
}


def cost_matrix_euclidean(x):
    """Euclidean cost matrix C[i,j] = |x_i - x_j|^2.
    Input: array of 1D point locations. Output: matrix.
    """
    return (x[:, None] - x[None, :])**2


OPERATIONS["cost_matrix_euclidean"] = {
    "fn": cost_matrix_euclidean,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Pairwise squared Euclidean cost matrix from 1D point locations"
}


def optimal_transport_plan_1d(x):
    """Optimal transport plan for 1D distributions (just the sorted coupling).
    Input: array of length 2n. Output: matrix (n x 2) of matched pairs.
    In 1D, the optimal plan matches sorted samples.
    """
    n = len(x) // 2
    if n < 1:
        return np.array([[0.0]])
    p = np.sort(x[:n])
    q = np.sort(x[n:2*n])
    m = min(len(p), len(q))
    return np.column_stack([p[:m], q[:m]])


OPERATIONS["optimal_transport_plan_1d"] = {
    "fn": optimal_transport_plan_1d,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Optimal 1D transport plan as sorted matched pairs"
}


def entropy_regularized_ot(x):
    """Entropy-regularized OT cost as a function of epsilon.
    Input: array of length 2n. Output: array of OT costs at eps=[0.01, 0.1, 1.0].
    """
    n = len(x) // 2
    if n < 1:
        return np.array([0.0, 0.0, 0.0])
    a = np.abs(x[:n]) + 1e-12
    b = np.abs(x[n:2*n]) + 1e-12
    a = a / a.sum()
    b = b / b.sum()

    na, nb = len(a), len(b)
    C = np.abs(np.arange(na)[:, None] - np.arange(nb)[None, :]).astype(float)

    results = []
    for eps in [0.01, 0.1, 1.0]:
        K = np.exp(-C / eps)
        u = np.ones(na)
        for _ in range(200):
            v = b / (K.T @ u + 1e-300)
            u = a / (K @ v + 1e-300)
        P = np.diag(u) @ K @ np.diag(v)
        results.append(np.sum(P * C))
    return np.array(results)


OPERATIONS["entropy_regularized_ot"] = {
    "fn": entropy_regularized_ot,
    "input_type": "array",
    "output_type": "array",
    "description": "Entropy-regularized OT costs at different regularization strengths"
}


def wasserstein_barycenter_1d(x):
    """Wasserstein barycenter of two 1D distributions (equal weights).
    Input: array of length 2n. Output: array of length n (the barycenter samples).
    In 1D, the barycenter is simply the pointwise average of sorted samples.
    """
    n = len(x) // 2
    if n < 1:
        return x
    p = np.sort(x[:n])
    q = np.sort(x[n:2*n])
    m = min(len(p), len(q))
    return 0.5 * (p[:m] + q[:m])


OPERATIONS["wasserstein_barycenter_1d"] = {
    "fn": wasserstein_barycenter_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "Wasserstein barycenter of two 1D empirical distributions"
}


def kantorovich_dual_1d(x):
    """Kantorovich dual potentials for 1D optimal transport.
    Input: array of length 2n. Output: array of dual potential values (length n).
    For 1D with cost |x-y|, the dual potential phi(x) = CDF-based transform.
    """
    n = len(x) // 2
    if n < 1:
        return x
    a = np.abs(x[:n]) + 1e-12
    b = np.abs(x[n:2*n]) + 1e-12
    a = a / a.sum()
    b = b / b.sum()
    # Dual potential: phi_i such that the optimal cost = sum(a*phi) + sum(b*psi)
    # For 1D sorted matching: phi_i = c(i, sigma(i)) - psi_{sigma(i)}
    # Simple approach: phi as cumulative cost differences
    cdf_a = np.cumsum(a)
    cdf_b = np.cumsum(b)
    m = min(len(cdf_a), len(cdf_b))
    phi = np.cumsum(cdf_b[:m] - cdf_a[:m])
    return phi


OPERATIONS["kantorovich_dual_1d"] = {
    "fn": kantorovich_dual_1d,
    "input_type": "array",
    "output_type": "array",
    "description": "Kantorovich dual potentials for 1D optimal transport"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
