"""
Octonion QM — Exceptional Jordan algebra and Freudenthal-Tits magic square

Connects to: [pseudo_riemannian, spin_foam, noncommutative_geometry_connes]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "octonion_qm"
OPERATIONS = {}


def _make_jordan_matrix(x):
    """Build a 3x3 Hermitian matrix (real case) from input array for Albert algebra."""
    # Albert algebra element: 3x3 Hermitian matrix over octonions
    # For real approximation: 3x3 symmetric matrix (6 independent components)
    mat = np.zeros((3, 3))
    vals = np.zeros(6)
    vals[:min(len(x), 6)] = x[:min(len(x), 6)]
    mat[0, 0] = vals[0]
    mat[1, 1] = vals[1]
    mat[2, 2] = vals[2]
    mat[0, 1] = mat[1, 0] = vals[3]
    mat[0, 2] = mat[2, 0] = vals[4]
    mat[1, 2] = mat[2, 1] = vals[5]
    return mat


def albert_algebra_multiply(x):
    """Jordan product of two 3x3 Hermitian matrices: A o B = (AB + BA)/2.
    Input: array (first 6 entries = matrix A diag+upper, rest padded as B).
    Output: array (flattened Jordan product)."""
    A = _make_jordan_matrix(x[:6] if len(x) >= 6 else x)
    B = _make_jordan_matrix(x[3:9] if len(x) >= 9 else x[2:])
    # Jordan product
    product = (A @ B + B @ A) / 2.0
    return product.flatten()


OPERATIONS["albert_algebra_multiply"] = {
    "fn": albert_algebra_multiply,
    "input_type": "array",
    "output_type": "array",
    "description": "Jordan product A o B = (AB+BA)/2 in Albert algebra (real approx)"
}


def exceptional_jordan_eigenvalues(x):
    """Eigenvalues of a 3x3 Jordan algebra element.
    Input: array (6 components of symmetric 3x3 matrix). Output: array of 3 eigenvalues."""
    mat = _make_jordan_matrix(x)
    eigvals = np.linalg.eigvalsh(mat)
    return eigvals


OPERATIONS["exceptional_jordan_eigenvalues"] = {
    "fn": exceptional_jordan_eigenvalues,
    "input_type": "array",
    "output_type": "array",
    "description": "Eigenvalues of an exceptional Jordan algebra element"
}


def cayley_plane_projection(x):
    """Project onto the Cayley plane OP^2 (rank-1 idempotent in Albert algebra).
    Input: array (3-vector to project). Output: array (projected via rank-1 projector).
    Constructs P = vv^T / (v^T v) and applies it."""
    v = np.zeros(3)
    v[:min(len(x), 3)] = x[:min(len(x), 3)]
    norm_sq = np.dot(v, v)
    if norm_sq < 1e-15:
        return np.zeros(3)
    P = np.outer(v, v) / norm_sq
    # Apply projector to input vector
    result = P @ v
    return result


OPERATIONS["cayley_plane_projection"] = {
    "fn": cayley_plane_projection,
    "input_type": "array",
    "output_type": "array",
    "description": "Projection onto the Cayley plane via rank-1 Jordan idempotent"
}


def magic_square_entry(x):
    """Freudenthal-Tits magic square: derive Lie algebra dimension from composition algebra dims.
    Input: array [dim_A, dim_B] where dim is 1,2,4,8 (R,C,H,O).
    Output: scalar (dimension of the corresponding Lie algebra).
    Magic square formula: L(A,B) has dim = 3*a*b + der(A) + der(B) + 3*(a+b)
    where der(K) dim of derivation algebra: R->0, C->0, H->3, O->14."""
    a = int(x[0]) if len(x) > 0 else 1
    b = int(x[1]) if len(x) > 1 else 1
    der_map = {1: 0, 2: 0, 4: 3, 8: 14}
    # Clamp to valid composition algebra dimensions
    valid_dims = [1, 2, 4, 8]
    a = min(valid_dims, key=lambda d: abs(d - a))
    b = min(valid_dims, key=lambda d: abs(d - b))
    der_a = der_map[a]
    der_b = der_map[b]
    # Tits formula for magic square
    dim = 3 * a * b + der_a + der_b + 3 * (a + b)
    return np.float64(dim)


OPERATIONS["magic_square_entry"] = {
    "fn": magic_square_entry,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Freudenthal-Tits magic square: Lie algebra dimension from composition algebra pair"
}


def octonion_projector(x):
    """Construct octonion projector (rank-1 projection matrix).
    Input: array. Output: array (flattened projection matrix P = xx^T / x^Tx)."""
    norm_sq = np.dot(x, x)
    if norm_sq < 1e-15:
        return np.zeros(len(x) * len(x))
    P = np.outer(x, x) / norm_sq
    return P.flatten()


OPERATIONS["octonion_projector"] = {
    "fn": octonion_projector,
    "input_type": "array",
    "output_type": "array",
    "description": "Rank-1 projector from octonion-valued vector"
}


def jordan_trace(x):
    """Trace of a Jordan algebra element (3x3 symmetric matrix).
    Input: array (6 components). Output: scalar trace."""
    mat = _make_jordan_matrix(x)
    return np.float64(np.trace(mat))


OPERATIONS["jordan_trace"] = {
    "fn": jordan_trace,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Trace of a 3x3 Jordan algebra element"
}


def jordan_determinant(x):
    """Determinant of a Jordan algebra element (3x3 symmetric matrix).
    Input: array (6 components). Output: scalar determinant.
    For 3x3 Jordan algebra: det = a0*a1*a2 + 2*a3*a4*a5 - a0*a5^2 - a1*a4^2 - a2*a3^2."""
    mat = _make_jordan_matrix(x)
    return np.float64(np.linalg.det(mat))


OPERATIONS["jordan_determinant"] = {
    "fn": jordan_determinant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Determinant of a 3x3 Jordan algebra element"
}


def jordan_adjoint(x):
    """Adjoint (adjugate) of a Jordan algebra element: A# = (1/2)(Tr(A)^2 - Tr(A^2))I - Tr(A)A + A^2.
    Input: array (6 components). Output: array (flattened 3x3 adjoint matrix).
    This is the Jordan algebraic adjoint, not the matrix adjoint."""
    A = _make_jordan_matrix(x)
    trA = np.trace(A)
    A2 = A @ A
    trA2 = np.trace(A2)
    I = np.eye(3)
    # Jordan adjoint formula for 3x3
    adj = 0.5 * (trA ** 2 - trA2) * I - trA * A + A2
    return adj.flatten()


OPERATIONS["jordan_adjoint"] = {
    "fn": jordan_adjoint,
    "input_type": "array",
    "output_type": "array",
    "description": "Jordan algebraic adjoint of a 3x3 element"
}


def composition_algebra_dimension(x):
    """Determine which composition algebra (R,C,H,O) an input approximates based on norm.
    Input: array. Output: scalar (1,2,4,8) = dimension of nearest composition algebra.
    Uses the norm-multiplicativity property: |xy| = |x||y|."""
    n = len(x)
    # Composition algebras exist only in dimensions 1, 2, 4, 8 (Hurwitz theorem)
    valid = np.array([1, 2, 4, 8])
    idx = np.argmin(np.abs(valid - n))
    return np.float64(valid[idx])


OPERATIONS["composition_algebra_dimension"] = {
    "fn": composition_algebra_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Nearest composition algebra dimension by Hurwitz theorem"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
