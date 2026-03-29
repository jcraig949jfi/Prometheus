"""
TQFT — Topological quantum field theory via Frobenius algebras

Connects to: [cosmic_topology, feynman_diagram_algebra, tropical_qft]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "tqft"
OPERATIONS = {}


def frobenius_multiply(a, b):
    """Frobenius algebra multiplication: m: A x A -> A.
    For a commutative Frobenius algebra of dimension n, multiplication is
    encoded in structure constants c_{ij}^k. Use diagonal (semisimple) algebra:
    e_i * e_j = delta_{ij} * lambda_i * e_i.
    Input: a array (first vector), b = same length. Output: product array."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(b) < len(a):
        b = np.resize(b, a.shape)
    # Semisimple: componentwise multiply with structure constants = 1
    return a * b

OPERATIONS["frobenius_multiply"] = {
    "fn": lambda x: frobenius_multiply(x, x),
    "input_type": "array",
    "output_type": "array",
    "description": "Frobenius algebra multiplication (semisimple)"
}


def frobenius_comultiply(a):
    """Frobenius comultiplication: Delta: A -> A x A.
    For semisimple algebra: Delta(e_i) = (1/lambda_i) * e_i (x) e_i.
    With lambda_i = a_i (the components), output the tensor product diagonal.
    Input: a array of dim n. Output: (n,n) matrix with Delta(a) on diagonal."""
    a = np.asarray(a, dtype=float)
    n = len(a)
    # Comultiplication maps e_i -> e_i (x) e_i (semisimple, normalized)
    result = np.zeros((n, n))
    for i in range(n):
        result[i, i] = a[i]  # diagonal tensor product
    return result

OPERATIONS["frobenius_comultiply"] = {
    "fn": frobenius_comultiply,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Frobenius comultiplication (semisimple)"
}


def frobenius_unit():
    """Frobenius unit: eta: k -> A. Returns the unit element.
    For semisimple: eta(1) = sum_i e_i.
    Input: (ignored). Output: unit vector of default dim=5."""
    return np.ones(5)

OPERATIONS["frobenius_unit"] = {
    "fn": lambda x: frobenius_unit(),
    "input_type": "array",
    "output_type": "array",
    "description": "Frobenius algebra unit element"
}


def frobenius_counit(a):
    """Frobenius counit (trace): epsilon: A -> k.
    epsilon(sum a_i e_i) = sum a_i * lambda_i. For semisimple with lambda=1: epsilon = sum.
    Input: a array. Output: scalar."""
    a = np.asarray(a, dtype=float)
    return np.float64(np.sum(a))

OPERATIONS["frobenius_counit"] = {
    "fn": frobenius_counit,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Frobenius counit (trace map)"
}


def cobordism_compose(M1, M2):
    """Compose two cobordisms (as linear maps represented by matrices).
    Composition is matrix multiplication M2 . M1.
    Input: M1 as array (auto-shaped to square matrix). Output: composed matrix."""
    a = np.asarray(M1, dtype=float)
    n = int(np.sqrt(len(a)))
    if n * n != len(a):
        n = len(a)
        # Treat as diagonal matrices
        return np.diag(a) @ np.diag(a)
    M = a.reshape(n, n)
    return M @ M  # compose with itself

OPERATIONS["cobordism_compose"] = {
    "fn": lambda x: cobordism_compose(x, x),
    "input_type": "array",
    "output_type": "matrix",
    "description": "Compose cobordisms (matrix multiplication)"
}


def partition_function_genus_g(dim_A, lambda_vals, g):
    """2D TQFT partition function for genus-g surface.
    Z(Sigma_g) = sum_i lambda_i^{2-2g} for semisimple Frobenius algebra.
    Input: lambda_vals array (eigenvalues of handle operator). g from first param.
    Output: Z scalar."""
    lam = np.asarray(lambda_vals, dtype=float) if not np.isscalar(lambda_vals) else np.asarray(dim_A, dtype=float)
    g_val = int(g) if not hasattr(g, '__len__') else 1
    # Z(Sigma_g) = sum_i lambda_i^{2g-2} (convention: handle element eigenvalues)
    # For g=0: Z = sum lambda_i^{-2} (need nonzero); g=1: Z = dim(A)
    if g_val == 1:
        return np.float64(len(lam))
    lam_nz = lam[np.abs(lam) > 1e-15]
    Z = np.sum(lam_nz ** (2 * g_val - 2))
    return np.float64(Z)

OPERATIONS["partition_function_genus_g"] = {
    "fn": lambda x: partition_function_genus_g(x, x, 2),
    "input_type": "array",
    "output_type": "scalar",
    "description": "2D TQFT partition function for genus-g surface"
}


def pants_decomposition_count(g):
    """Number of distinct pants decompositions of genus-g surface.
    A genus-g surface decomposes into 2g-2 pairs of pants (for g>=2).
    The number of distinct decompositions grows as (6g-6)!! / (3g-3)! approximately.
    Input: g array (genus values). Output: pants pair count array = 2g-2."""
    g = np.asarray(g, dtype=float).astype(int)
    # Number of pairs of pants = 2g - 2 (for g >= 2)
    result = np.maximum(2 * g - 2, 0).astype(float)
    return result

OPERATIONS["pants_decomposition_count"] = {
    "fn": pants_decomposition_count,
    "input_type": "array",
    "output_type": "array",
    "description": "Number of pairs of pants in decomposition of genus-g surface"
}


def tqft_dimension_from_algebra(structure_constants):
    """Dimension of TQFT state space = dim(A) for a Frobenius algebra A.
    For a semisimple algebra, this equals the number of simple summands.
    Input: structure constants array (length = dim). Output: dim scalar."""
    a = np.asarray(structure_constants, dtype=float)
    return np.float64(len(a))

OPERATIONS["tqft_dimension_from_algebra"] = {
    "fn": tqft_dimension_from_algebra,
    "input_type": "array",
    "output_type": "scalar",
    "description": "TQFT state space dimension from Frobenius algebra"
}


def frobenius_trace(a):
    """Frobenius trace: the pairing <a, b> = epsilon(m(a,b)).
    Self-pairing: <a, a> = epsilon(a*a) = sum a_i^2 for semisimple.
    Input: a array. Output: trace scalar."""
    a = np.asarray(a, dtype=float)
    return np.float64(np.sum(a ** 2))

OPERATIONS["frobenius_trace"] = {
    "fn": frobenius_trace,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Frobenius trace (self-pairing)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
