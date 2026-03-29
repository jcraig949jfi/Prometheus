"""
Representation Theory — character tables for small groups, tensor products of representations

Connects to: [abstract_algebra, linear_algebra, finite_fields, harmonic_analysis]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "representation_theory"
OPERATIONS = {}


def cyclic_group_characters(x):
    """Character table of cyclic group Z/nZ where n = len(x).
    Rows are irreducible characters, columns are group elements.
    chi_k(g^j) = omega^{kj} where omega = e^{2*pi*i/n}.
    Input: array. Output: matrix (complex)."""
    n = len(np.asarray(x))
    omega = np.exp(2j * np.pi / n)
    table = np.zeros((n, n), dtype=complex)
    for k in range(n):
        for j in range(n):
            table[k, j] = omega ** (k * j)
    return table


OPERATIONS["cyclic_group_characters"] = {
    "fn": cyclic_group_characters,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Character table of cyclic group Z/nZ, n = len(input)"
}


def symmetric_group_s3_characters(x):
    """Character table of S3 (symmetric group on 3 elements).
    S3 has 3 conjugacy classes: {e}, {(12),(13),(23)}, {(123),(132)}.
    3 irreps: trivial (dim 1), sign (dim 1), standard (dim 2).
    Input: array (ignored). Output: matrix (3x3)."""
    # Columns: class of e, class of transpositions, class of 3-cycles
    # Row 0: trivial representation
    # Row 1: sign representation
    # Row 2: standard (2-dim) representation
    table = np.array([
        [1, 1, 1],
        [1, -1, 1],
        [2, 0, -1]
    ], dtype=float)
    return table


OPERATIONS["symmetric_group_s3_characters"] = {
    "fn": symmetric_group_s3_characters,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Character table of S3: trivial, sign, standard representations"
}


def character_inner_product(x):
    """Inner product of two characters for a finite group.
    Input: array of length 2k; first half is chi1 values on conjugacy classes,
    second half is chi2 values. Assumes equal-size conjugacy classes (cyclic group).
    <chi1, chi2> = (1/n) * sum(chi1(g) * conj(chi2(g))).
    Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=complex)
    mid = len(arr) // 2
    chi1 = arr[:mid]
    chi2 = arr[mid:2 * mid]
    n = len(chi1)
    if n == 0:
        return 0.0
    # For cyclic groups, each conjugacy class has size 1
    inner = np.sum(chi1 * np.conj(chi2)) / n
    return float(np.real(inner))


OPERATIONS["character_inner_product"] = {
    "fn": character_inner_product,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Inner product of two characters (assuming cyclic group / uniform class sizes)"
}


def tensor_product_decomposition(x):
    """Decompose tensor product of two representations of a cyclic group Z/nZ.
    For cyclic groups: chi_a tensor chi_b = chi_{(a+b) mod n}.
    Input: array [a, b, n]. Output: array (multiplicities of each irrep).
    If input doesn't have exactly 3 elements, uses first two as rep indices mod len(x)."""
    arr = np.asarray(x, dtype=int)
    if len(arr) >= 3:
        a, b, n = int(arr[0]), int(arr[1]), int(arr[2])
    else:
        n = max(len(arr), 2)
        a, b = int(arr[0]) % n, int(arr[1 % len(arr)]) % n
    n = max(n, 1)
    multiplicities = np.zeros(n, dtype=int)
    idx = (a + b) % n
    multiplicities[idx] = 1
    return multiplicities


OPERATIONS["tensor_product_decomposition"] = {
    "fn": tensor_product_decomposition,
    "input_type": "array",
    "output_type": "array",
    "description": "Tensor product decomposition for cyclic group reps: chi_a x chi_b = chi_{a+b mod n}"
}


def regular_representation_matrix(x):
    """Left regular representation matrix for element g in Z/nZ.
    The regular representation of g acts by permuting basis vectors: e_j -> e_{(g+j) mod n}.
    Uses first element of x as g, len(x) as n.
    Input: array. Output: matrix."""
    arr = np.asarray(x, dtype=int)
    n = len(arr)
    g = int(arr[0]) % n
    mat = np.zeros((n, n), dtype=float)
    for j in range(n):
        mat[(g + j) % n, j] = 1.0
    return mat


OPERATIONS["regular_representation_matrix"] = {
    "fn": regular_representation_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Left regular representation matrix for element g in Z/nZ"
}


def representation_dimension(x):
    """Dimension of a representation given its character (dimension = chi(identity) = chi[0]).
    Input: array (character values). Output: scalar."""
    arr = np.asarray(x, dtype=complex)
    return float(np.real(arr[0]))


OPERATIONS["representation_dimension"] = {
    "fn": representation_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dimension of representation = character evaluated at identity element"
}


def character_table_verify(x):
    """Verify orthogonality of rows of a character table (matrix).
    For a valid character table of a group of order n with equal-size classes,
    the row orthogonality gives <chi_i, chi_j> = delta_{ij}.
    Input: array (flattened square matrix). Output: scalar (max deviation from orthogonality)."""
    arr = np.asarray(x, dtype=complex)
    n = int(np.sqrt(len(arr)))
    if n * n > len(arr):
        n = int(np.floor(np.sqrt(len(arr))))
    if n == 0:
        return 0.0
    table = arr[:n*n].reshape(n, n)
    # Row orthogonality: (1/n) * table @ table^dagger should be identity
    product = table @ np.conj(table.T) / n
    deviation = np.max(np.abs(product - np.eye(n)))
    return float(deviation)


OPERATIONS["character_table_verify"] = {
    "fn": character_table_verify,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Max deviation from row orthogonality in a character table"
}


def induced_representation_dim(x):
    """Dimension of induced representation Ind_H^G(rho).
    dim(Ind_H^G(rho)) = [G:H] * dim(rho) = (|G|/|H|) * dim(rho).
    Input: array [|G|, |H|, dim_rho]. Output: scalar."""
    arr = np.asarray(x, dtype=float)
    if len(arr) >= 3:
        g_order, h_order, dim_rho = float(arr[0]), float(arr[1]), float(arr[2])
    else:
        # Fallback: use array values as group order, subgroup order, dim
        g_order = float(arr[0]) if len(arr) > 0 else 1
        h_order = float(arr[1]) if len(arr) > 1 else 1
        dim_rho = 1.0
    if h_order == 0:
        h_order = 1
    index = g_order / h_order
    return float(index * dim_rho)


OPERATIONS["induced_representation_dim"] = {
    "fn": induced_representation_dim,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dimension of induced representation: [G:H] * dim(rho)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
