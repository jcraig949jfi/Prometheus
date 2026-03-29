"""
Braid Groups -- Artin generators, Burau representation, and braid closure

Connects to: [knot_invariants, hecke_algebras, quantum_groups, topology]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "braid_groups"
OPERATIONS = {}


def artin_generator_matrix(x):
    """Burau representation matrix for Artin generator sigma_i on n strands.
    Uses unreduced Burau with variable t = x[0], generator index i = int(x[1]),
    number of strands n = int(x[2]).
    Input: array (t, i, n). Output: matrix(n, n)."""
    t = x[0] if len(x) > 0 else 0.5
    i = int(x[1]) if len(x) > 1 else 1
    n = int(x[2]) if len(x) > 2 else 3
    i = max(1, min(i, n - 1))  # clamp to valid range
    n = max(2, n)
    mat = np.eye(n)
    idx = i - 1  # 0-based
    mat[idx, idx] = 1 - t
    mat[idx, idx + 1] = t
    mat[idx + 1, idx] = 1
    mat[idx + 1, idx + 1] = 0
    return mat

OPERATIONS["artin_generator_matrix"] = {
    "fn": artin_generator_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Burau matrix for Artin generator sigma_i on n strands"
}


def burau_representation(x):
    """Reduced Burau representation matrix for sigma_i.
    t = x[0], i = int(x[1]), n = int(x[2]).
    Output: (n-1)x(n-1) matrix."""
    t = x[0] if len(x) > 0 else 0.5
    i = int(x[1]) if len(x) > 1 else 1
    n = int(x[2]) if len(x) > 2 else 3
    n = max(2, n)
    i = max(1, min(i, n - 1))
    dim = n - 1
    mat = np.eye(dim)
    idx = i - 1  # 0-based in reduced rep
    if idx == 0:
        mat[0, 0] = -t
        if dim > 1:
            mat[0, 1] = 1
    elif idx == dim:
        mat[idx - 1, idx - 1] = 1
    else:
        if idx - 1 >= 0:
            mat[idx - 1, idx - 1] = 1
            mat[idx - 1, idx] = 0  # already 0 if off-diag wasn't set
        mat[idx, idx] = -t
        if idx - 1 >= 0:
            mat[idx, idx - 1] = t
        if idx + 1 < dim:
            mat[idx, idx + 1] = 1
    return mat

OPERATIONS["burau_representation"] = {
    "fn": burau_representation,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Reduced Burau representation matrix for Artin generator"
}


def braid_word_to_matrix(x):
    """Convert braid word (sequence of signed generator indices) to Burau matrix.
    x[0] = t parameter, x[1] = n (strands), remaining = braid word.
    Positive = sigma_i, negative = sigma_i^{-1}.
    Input: array. Output: matrix."""
    t = x[0] if len(x) > 0 else 0.5
    n = int(x[1]) if len(x) > 1 else 3
    n = max(2, n)
    word = x[2:] if len(x) > 2 else np.array([1.0, -2.0, 1.0])
    mat = np.eye(n)
    for gen in word:
        i = int(abs(gen))
        if i < 1 or i >= n:
            continue
        g = artin_generator_matrix(np.array([t, float(i), float(n)]))
        if gen < 0:
            g = np.linalg.inv(g)
        mat = mat @ g
    return mat

OPERATIONS["braid_word_to_matrix"] = {
    "fn": braid_word_to_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Product of Burau matrices for a braid word"
}


def braid_compose(x):
    """Compose two braid words. First half and second half of array.
    Returns concatenated braid word.
    Input: array (split at midpoint). Output: array."""
    mid = len(x) // 2
    w1 = x[:mid]
    w2 = x[mid:]
    return np.concatenate([w1, w2])

OPERATIONS["braid_compose"] = {
    "fn": braid_compose,
    "input_type": "array",
    "output_type": "array",
    "description": "Compose two braid words by concatenation"
}


def braid_inverse(x):
    """Inverse of a braid word: reverse order and negate each generator.
    Input: array. Output: array."""
    return -x[::-1]

OPERATIONS["braid_inverse"] = {
    "fn": braid_inverse,
    "input_type": "array",
    "output_type": "array",
    "description": "Inverse braid word (reverse and negate generators)"
}


def braid_closure_linking(x):
    """Compute the writhe (sum of signs) of a braid word, which gives
    the linking number of the closure.
    Input: array (braid word). Output: scalar."""
    return np.sum(np.sign(x))

OPERATIONS["braid_closure_linking"] = {
    "fn": braid_closure_linking,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Writhe / linking number of the braid closure"
}


def braid_writhe(x):
    """Writhe of a braid: sum of signs of crossings.
    Input: array (braid word). Output: scalar."""
    return np.sum(np.sign(x))

OPERATIONS["braid_writhe"] = {
    "fn": braid_writhe,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Writhe (algebraic crossing number) of braid word"
}


def braid_permutation(x):
    """Permutation induced by a braid word on n strands.
    x[0] = n, rest = braid word.
    Input: array. Output: array (permutation)."""
    n = int(x[0]) if len(x) > 0 else 3
    n = max(2, n)
    word = x[1:] if len(x) > 1 else np.array([1.0])
    perm = np.arange(n, dtype=float)
    for gen in word:
        i = int(abs(gen))
        if 1 <= i < n:
            # sigma_i and sigma_i^{-1} induce the same transposition
            perm[i - 1], perm[i] = perm[i], perm[i - 1]
    return perm

OPERATIONS["braid_permutation"] = {
    "fn": braid_permutation,
    "input_type": "array",
    "output_type": "array",
    "description": "Permutation of strands induced by braid word"
}


def alexander_from_burau(x):
    """Compute Alexander polynomial evaluation from reduced Burau matrix.
    The Alexander polynomial Delta(t) is related to det(I - B) where B
    is the reduced Burau matrix. Evaluate at t = x[0].
    x[0]=t, x[1]=n (strands), x[2:] = braid word.
    Input: array. Output: scalar."""
    t = x[0] if len(x) > 0 else 0.5
    n = int(x[1]) if len(x) > 1 else 3
    n = max(2, n)
    word = x[2:] if len(x) > 2 else np.array([1.0, -2.0, 1.0])
    # Build reduced Burau matrix for the full braid word
    dim = n - 1
    mat = np.eye(dim)
    for gen in word:
        i = int(abs(gen))
        if i < 1 or i >= n:
            continue
        g = burau_representation(np.array([t, float(i), float(n)]))
        if gen < 0:
            g = np.linalg.inv(g)
        mat = mat @ g
    # Alexander polynomial ~ det(I - B) up to units in Z[t, t^{-1}]
    alex = np.linalg.det(np.eye(dim) - mat)
    return float(np.real(alex))

OPERATIONS["alexander_from_burau"] = {
    "fn": alexander_from_burau,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Alexander polynomial evaluation via reduced Burau representation"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
