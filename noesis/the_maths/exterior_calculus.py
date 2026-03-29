"""
Exterior Calculus — differential forms numerics

Connects to: [differential_geometry, topology, physics, hodge_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Implements wedge products, Hodge stars, exterior derivatives,
pullbacks, and Laplace-Beltrami operators on flat spaces.
"""

import numpy as np

FIELD_NAME = "exterior_calculus"
OPERATIONS = {}


def wedge_product(x):
    """Wedge product of two 1-forms in R^n.
    Split x into two halves as 1-forms alpha, beta.
    Returns the 2-form alpha ^ beta (antisymmetric tensor).
    Input: array (even length). Output: array (flattened 2-form)."""
    n = len(x) // 2
    if n < 1:
        return np.array([0.0])
    alpha = x[:n]
    beta = x[n:2 * n]
    # 2-form components: (alpha ^ beta)_{ij} = alpha_i * beta_j - alpha_j * beta_i
    form2 = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            form2[i, j] = alpha[i] * beta[j] - alpha[j] * beta[i]
    # Return upper triangular part (independent components)
    result = []
    for i in range(n):
        for j in range(i + 1, n):
            result.append(form2[i, j])
    return np.array(result) if result else np.array([0.0])


OPERATIONS["wedge_product"] = {
    "fn": wedge_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Wedge product of two 1-forms"
}


def hodge_star_2d(x):
    """Hodge star operator in 2D flat space.
    For a 1-form (a, b) in R^2: *alpha = -b dx + a dy, i.e., rotation by 90 deg.
    For a 0-form f: *f = f * (dx ^ dy).
    Input: array. Output: array."""
    if len(x) == 1:
        # 0-form -> 2-form (just the scalar times volume form)
        return np.array([x[0]])
    elif len(x) == 2:
        # 1-form (a, b) -> 1-form (-b, a) (rotation by pi/2)
        return np.array([-x[1], x[0]])
    else:
        # Treat first two as a 1-form
        result = np.zeros_like(x)
        result[0] = -x[1]
        result[1] = x[0]
        # Higher components: *(...) as volume-form scalars
        for i in range(2, len(x)):
            result[i] = x[i]  # pass through
        return result


OPERATIONS["hodge_star_2d"] = {
    "fn": hodge_star_2d,
    "input_type": "array",
    "output_type": "array",
    "description": "Hodge star in 2D Euclidean space"
}


def hodge_star_3d(x):
    """Hodge star in 3D flat space.
    1-form (a,b,c) -> 2-form: *(dx) = dy^dz, *(dy) = dz^dx, *(dz) = dx^dy.
    2-form -> 1-form: *(dy^dz) = dx, etc.
    Input: array. Output: array."""
    if len(x) == 1:
        # 0-form -> 3-form (volume)
        return np.array([x[0]])
    elif len(x) == 3:
        # 1-form -> 2-form (same components, this is the cross product dual)
        # *(a dx + b dy + c dz) = a dy^dz + b dz^dx + c dx^dy
        return np.array([x[0], x[1], x[2]])
    else:
        # General: apply component-wise Hodge
        n = len(x)
        result = np.zeros(n)
        for i in range(min(n, 3)):
            result[i] = x[i]
        for i in range(3, n):
            result[i] = x[i]
        return result


OPERATIONS["hodge_star_3d"] = {
    "fn": hodge_star_3d,
    "input_type": "array",
    "output_type": "array",
    "description": "Hodge star in 3D Euclidean space"
}


def exterior_derivative_0form(x):
    """Exterior derivative of a 0-form (scalar field) sampled on a 1D grid.
    d(f) = df/dx * dx. Uses finite differences.
    Input: array (function samples). Output: array (1-form samples)."""
    n = len(x)
    if n < 2:
        return np.array([0.0])
    # Central differences for interior, forward/backward at boundaries
    df = np.zeros(n)
    df[0] = x[1] - x[0]
    df[-1] = x[-1] - x[-2]
    for i in range(1, n - 1):
        df[i] = (x[i + 1] - x[i - 1]) / 2.0
    return df


OPERATIONS["exterior_derivative_0form"] = {
    "fn": exterior_derivative_0form,
    "input_type": "array",
    "output_type": "array",
    "description": "Exterior derivative of a 0-form (gradient)"
}


def exterior_derivative_1form(x):
    """Exterior derivative of a 1-form on a 1D grid.
    For a 1-form omega = f(x) dx on a 1D manifold, d(omega) = 0
    (since there are no 2-forms in 1D).
    On a 2D grid (interpret x as n x 2): d(alpha) = (d alpha_2/dx - d alpha_1/dy) dx^dy.
    Input: array. Output: array."""
    n = len(x)
    if n < 4:
        # 1D case: d of a 1-form is 0
        return np.array([0.0])
    # Interpret as 2D: first half = alpha_x, second half = alpha_y
    half = n // 2
    alpha_x = x[:half]
    alpha_y = x[half:2 * half]
    # d(alpha) = (d alpha_y/dx - d alpha_x/dy) dx^dy
    # Approximate with finite differences
    d_alpha_y_dx = np.zeros(half)
    d_alpha_x_dy = np.zeros(half)
    for i in range(1, half):
        d_alpha_y_dx[i] = alpha_y[i] - alpha_y[i - 1]
        d_alpha_x_dy[i] = alpha_x[i] - alpha_x[i - 1]
    curl = d_alpha_y_dx - d_alpha_x_dy
    return curl


OPERATIONS["exterior_derivative_1form"] = {
    "fn": exterior_derivative_1form,
    "input_type": "array",
    "output_type": "array",
    "description": "Exterior derivative of a 1-form (curl-like)"
}


def pullback_linear(x):
    """Pullback of a 1-form by a linear map. If phi: R^m -> R^n is linear
    (encoded as matrix A) and alpha is a 1-form on R^n, then
    phi*(alpha) = A^T alpha.
    Input: array. Output: array."""
    n = len(x)
    # Split: first part is the 1-form, construct a simple linear map
    # Use a rotation matrix as the map
    dim = min(n, 3)
    alpha = x[:dim]
    theta = x[0] if n > 0 else 0.0
    # 2D rotation pullback
    if dim >= 2:
        A = np.array([[np.cos(theta), -np.sin(theta)],
                       [np.sin(theta), np.cos(theta)]])
        form = alpha[:2]
        result = A.T @ form
        return np.concatenate([result, alpha[2:]])
    return alpha


OPERATIONS["pullback_linear"] = {
    "fn": pullback_linear,
    "input_type": "array",
    "output_type": "array",
    "description": "Pullback of a 1-form by a linear map (rotation)"
}


def interior_product(x):
    """Interior product (contraction) of a vector field with a 2-form.
    iota_v(omega)_j = sum_i v_i * omega_{ij}.
    Split x: first third = vector, rest = 2-form components.
    Input: array. Output: array."""
    n = len(x)
    dim = max(2, n // 3)
    v = x[:dim]
    # Reconstruct antisymmetric 2-form from remaining components
    n_2form = dim * (dim - 1) // 2
    form_flat = x[dim:dim + n_2form] if dim + n_2form <= n else np.zeros(n_2form)
    omega = np.zeros((dim, dim))
    idx = 0
    for i in range(dim):
        for j in range(i + 1, dim):
            if idx < len(form_flat):
                omega[i, j] = form_flat[idx]
                omega[j, i] = -form_flat[idx]
                idx += 1
    # Interior product: (iota_v omega)_j = sum_i v[i] * omega[i, j]
    result = np.zeros(dim)
    for j in range(dim):
        for i in range(dim):
            result[j] += v[i] * omega[i, j]
    return result


OPERATIONS["interior_product"] = {
    "fn": interior_product,
    "input_type": "array",
    "output_type": "array",
    "description": "Interior product of vector field with 2-form"
}


def codifferential(x):
    """Codifferential delta = (-1)^{n(k-1)+1} * d * (Hodge star applied twice).
    In flat space: delta = -div for 1-forms.
    Input: array (1-form samples on grid). Output: array."""
    n = len(x)
    if n < 3:
        return np.array([0.0])
    # delta(alpha) = -d*(* alpha) in 1D = negative divergence
    # For 1D 1-form sampled on grid: delta = -d/dx of the coefficient
    div = np.zeros(n)
    div[0] = -(x[1] - x[0])
    div[-1] = -(x[-1] - x[-2])
    for i in range(1, n - 1):
        div[i] = -(x[i + 1] - x[i - 1]) / 2.0
    return div


OPERATIONS["codifferential"] = {
    "fn": codifferential,
    "input_type": "array",
    "output_type": "array",
    "description": "Codifferential (adjoint of exterior derivative)"
}


def laplace_beltrami_flat(x):
    """Laplace-Beltrami operator on flat space: Delta = d*delta + delta*d.
    For a 0-form on a 1D grid, this reduces to the standard Laplacian d^2f/dx^2.
    Input: array (0-form samples). Output: array."""
    n = len(x)
    if n < 3:
        return np.array([0.0])
    # Standard 1D Laplacian via finite differences
    lap = np.zeros(n)
    for i in range(1, n - 1):
        lap[i] = x[i - 1] - 2 * x[i] + x[i + 1]
    lap[0] = x[1] - 2 * x[0] + x[0]  # Neumann-like BC
    lap[-1] = x[-2] - 2 * x[-1] + x[-1]
    return lap


OPERATIONS["laplace_beltrami_flat"] = {
    "fn": laplace_beltrami_flat,
    "input_type": "array",
    "output_type": "array",
    "description": "Laplace-Beltrami operator on flat 1D domain"
}


def deRham_cohomology_rank(x):
    """Estimate de Rham cohomology ranks (Betti numbers) from a discrete
    chain complex. Interpret x as dimensions of chain groups C_0, C_1, ...
    and estimate Betti numbers via Euler characteristic constraints.
    Input: array. Output: array."""
    n = len(x)
    dims = np.abs(x).astype(int)
    # Build boundary matrices of appropriate dimensions and estimate rank
    betti = np.zeros(n)
    prev_rank = 0
    for k in range(n):
        # beta_k = dim(C_k) - rank(d_k) - rank(d_{k-1})
        # Approximate: rank(d_k) ~ min(dim(C_k), dim(C_{k+1})) * some factor
        if k < n - 1:
            rank_dk = min(dims[k], dims[k + 1] if k + 1 < n else 0) // 2
        else:
            rank_dk = 0
        betti[k] = max(0, dims[k] - rank_dk - prev_rank)
        prev_rank = rank_dk
    return betti


OPERATIONS["deRham_cohomology_rank"] = {
    "fn": deRham_cohomology_rank,
    "input_type": "array",
    "output_type": "array",
    "description": "Estimated Betti numbers (de Rham cohomology ranks)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
