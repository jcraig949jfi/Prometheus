"""
Orthogonal Polynomials — Chebyshev, Legendre, Hermite, Laguerre, Jacobi

Connects to: [hypergeometric_functions, approximation_theory, numerical_integration]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "orthogonal_polynomials"
OPERATIONS = {}


def chebyshev_t(x):
    """Chebyshev T_n(x). x=[n, x_val]. Or evaluate T_n at array values with n=int(x[0]). Input: array. Output: array."""
    n = int(x[0])
    pts = np.asarray(x[1:], dtype=np.float64)
    if len(pts) == 0:
        pts = np.array([0.5])
    # T_n(x) = cos(n * arccos(x)) for |x| <= 1
    result = np.cos(n * np.arccos(np.clip(pts, -1, 1)))
    return result


OPERATIONS["chebyshev_t"] = {
    "fn": chebyshev_t,
    "input_type": "array",
    "output_type": "array",
    "description": "Chebyshev polynomial of first kind T_n(x)"
}


def chebyshev_u(x):
    """Chebyshev U_n(x). x=[n, x_vals...]. Input: array. Output: array."""
    n = int(x[0])
    pts = np.asarray(x[1:], dtype=np.float64)
    if len(pts) == 0:
        pts = np.array([0.5])
    # U_n(x) = sin((n+1)*arccos(x)) / sin(arccos(x))
    theta = np.arccos(np.clip(pts, -1, 1))
    sin_theta = np.sin(theta)
    result = np.where(
        np.abs(sin_theta) > 1e-15,
        np.sin((n + 1) * theta) / sin_theta,
        (n + 1) * np.where(pts > 0, 1.0, (-1.0) ** n)
    )
    return result


OPERATIONS["chebyshev_u"] = {
    "fn": chebyshev_u,
    "input_type": "array",
    "output_type": "array",
    "description": "Chebyshev polynomial of second kind U_n(x)"
}


def legendre_p(x):
    """Legendre P_n(x) via recurrence. x=[n, x_vals...]. Input: array. Output: array."""
    n = int(x[0])
    pts = np.asarray(x[1:], dtype=np.float64)
    if len(pts) == 0:
        pts = np.array([0.5])
    if n == 0:
        return np.ones_like(pts)
    if n == 1:
        return pts.copy()
    p_prev = np.ones_like(pts)
    p_curr = pts.copy()
    for k in range(1, n):
        p_next = ((2 * k + 1) * pts * p_curr - k * p_prev) / (k + 1)
        p_prev = p_curr
        p_curr = p_next
    return p_curr


OPERATIONS["legendre_p"] = {
    "fn": legendre_p,
    "input_type": "array",
    "output_type": "array",
    "description": "Legendre polynomial P_n(x) via three-term recurrence"
}


def hermite_h(x):
    """Physicist's Hermite H_n(x). x=[n, x_vals...]. Input: array. Output: array."""
    n = int(x[0])
    pts = np.asarray(x[1:], dtype=np.float64)
    if len(pts) == 0:
        pts = np.array([0.5])
    if n == 0:
        return np.ones_like(pts)
    if n == 1:
        return 2 * pts
    h_prev = np.ones_like(pts)
    h_curr = 2 * pts
    for k in range(1, n):
        h_next = 2 * pts * h_curr - 2 * k * h_prev
        h_prev = h_curr
        h_curr = h_next
    return h_curr


OPERATIONS["hermite_h"] = {
    "fn": hermite_h,
    "input_type": "array",
    "output_type": "array",
    "description": "Physicist's Hermite polynomial H_n(x)"
}


def laguerre_l(x):
    """Laguerre L_n(x). x=[n, x_vals...]. Input: array. Output: array."""
    n = int(x[0])
    pts = np.asarray(x[1:], dtype=np.float64)
    if len(pts) == 0:
        pts = np.array([0.5])
    if n == 0:
        return np.ones_like(pts)
    if n == 1:
        return 1 - pts
    l_prev = np.ones_like(pts)
    l_curr = 1 - pts
    for k in range(1, n):
        l_next = ((2 * k + 1 - pts) * l_curr - k * l_prev) / (k + 1)
        l_prev = l_curr
        l_curr = l_next
    return l_curr


OPERATIONS["laguerre_l"] = {
    "fn": laguerre_l,
    "input_type": "array",
    "output_type": "array",
    "description": "Laguerre polynomial L_n(x)"
}


def jacobi_p(x):
    """Jacobi P_n^(alpha,beta)(x). x=[n, alpha, beta, x_vals...]. Input: array. Output: array."""
    n = int(x[0])
    alpha = float(x[1])
    beta = float(x[2])
    pts = np.asarray(x[3:], dtype=np.float64)
    if len(pts) == 0:
        pts = np.array([0.5])
    if n == 0:
        return np.ones_like(pts)
    if n == 1:
        return 0.5 * ((alpha - beta) + (alpha + beta + 2) * pts)
    p_prev = np.ones_like(pts)
    p_curr = 0.5 * ((alpha - beta) + (alpha + beta + 2) * pts)
    for k in range(1, n):
        k2 = 2 * k
        a1 = 2 * (k + 1) * (k + alpha + beta + 1) * (k2 + alpha + beta)
        a2 = (k2 + alpha + beta + 1) * (alpha ** 2 - beta ** 2)
        a3 = (k2 + alpha + beta) * (k2 + alpha + beta + 1) * (k2 + alpha + beta + 2)
        a4 = 2 * (k + alpha) * (k + beta) * (k2 + alpha + beta + 2)
        if abs(a1) < 1e-15:
            break
        p_next = ((a2 + a3 * pts) * p_curr - a4 * p_prev) / a1
        p_prev = p_curr
        p_curr = p_next
    return p_curr


OPERATIONS["jacobi_p"] = {
    "fn": jacobi_p,
    "input_type": "array",
    "output_type": "array",
    "description": "Jacobi polynomial P_n^(alpha,beta)(x)"
}


def polynomial_recurrence_eval(x):
    """Evaluate generic three-term recurrence p_{n+1} = (a_n*x+b_n)*p_n - c_n*p_{n-1}. x=[n, x_val]. Input: array. Output: scalar."""
    n = int(x[0])
    x_val = float(x[1])
    # Default: Chebyshev-like recurrence a_n=2, b_n=0, c_n=1 (for n>=1)
    if n == 0:
        return 1.0
    if n == 1:
        return x_val
    p_prev, p_curr = 1.0, x_val
    for _ in range(1, n):
        p_next = 2 * x_val * p_curr - p_prev
        p_prev = p_curr
        p_curr = p_next
    return float(p_curr)


OPERATIONS["polynomial_recurrence_eval"] = {
    "fn": polynomial_recurrence_eval,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Evaluate polynomial via Chebyshev-type three-term recurrence"
}


def gauss_quadrature_nodes(x):
    """Compute Gauss-Legendre quadrature nodes and weights for n points. x=[n]. Input: array. Output: matrix."""
    n = int(x[0])
    if n < 1 or n > 100:
        n = min(max(n, 1), 100)
    # Golub-Welsch algorithm: eigenvalues of tridiagonal Jacobi matrix
    i = np.arange(1, n, dtype=np.float64)
    beta = i / np.sqrt(4 * i * i - 1)
    J = np.diag(beta, -1) + np.diag(beta, 1)
    nodes, vecs = np.linalg.eigh(J)
    weights = 2 * vecs[0, :] ** 2
    # Return as 2-row matrix: [nodes; weights]
    return np.vstack([nodes, weights])


OPERATIONS["gauss_quadrature_nodes"] = {
    "fn": gauss_quadrature_nodes,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Gauss-Legendre quadrature nodes and weights via Golub-Welsch"
}


def orthogonality_check(x):
    """Check <P_m, P_n> = 0 for Legendre polynomials. x=[m, n]. Input: array. Output: scalar."""
    m = int(x[0])
    n = int(x[1])
    # Use Gauss quadrature to integrate P_m(x)*P_n(x) on [-1,1]
    nq = max(m + n + 1, 5)
    i = np.arange(1, nq, dtype=np.float64)
    beta = i / np.sqrt(4 * i * i - 1)
    J = np.diag(beta, -1) + np.diag(beta, 1)
    nodes, vecs = np.linalg.eigh(J)
    weights = 2 * vecs[0, :] ** 2

    def _legendre(deg, pts):
        if deg == 0:
            return np.ones_like(pts)
        if deg == 1:
            return pts.copy()
        p0, p1 = np.ones_like(pts), pts.copy()
        for k in range(1, deg):
            p0, p1 = p1, ((2 * k + 1) * pts * p1 - k * p0) / (k + 1)
        return p1

    integral = np.sum(weights * _legendre(m, nodes) * _legendre(n, nodes))
    return float(integral)


OPERATIONS["orthogonality_check"] = {
    "fn": orthogonality_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Inner product <P_m, P_n> for Legendre polynomials (0 if m!=n)"
}


def christoffel_darboux(x):
    """Christoffel-Darboux sum for Legendre: sum_{k=0}^{n} (2k+1)/2 * P_k(x)*P_k(y). x=[n, x_val, y_val]. Input: array. Output: scalar."""
    n = int(x[0])
    xv = float(x[1])
    yv = float(x[2]) if len(x) > 2 else float(x[1])

    def _legendre_seq(deg, t):
        if deg == 0:
            return [1.0]
        vals = [1.0, t]
        for k in range(1, deg):
            vals.append(((2 * k + 1) * t * vals[-1] - k * vals[-2]) / (k + 1))
        return vals

    px = _legendre_seq(n, xv)
    py = _legendre_seq(n, yv)
    # Direct sum
    result = sum((2 * k + 1) / 2.0 * px[k] * py[k] for k in range(n + 1))
    return float(result)


OPERATIONS["christoffel_darboux"] = {
    "fn": christoffel_darboux,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Christoffel-Darboux kernel sum for Legendre polynomials"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
