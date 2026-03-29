"""
Inca Quipu — Tree-structured hierarchical summation with pendant cords

Connects to: [mayan_vigesimal, rod_calculus, babylonian_sexagesimal]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "inca_quipu"
OPERATIONS = {}


def quipu_encode_decimal(x):
    """Encode numbers as quipu knot groups (base-10 digit arrays). Input: array. Output: matrix."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    max_digits = 6
    result = np.zeros((len(arr), max_digits), dtype=np.float64)
    for i, val in enumerate(arr):
        n = int(abs(val))
        for j in range(max_digits - 1, -1, -1):
            result[i, j] = n % 10
            n //= 10
    return result


OPERATIONS["quipu_encode_decimal"] = {
    "fn": quipu_encode_decimal,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Encode numbers as quipu knot groups (base-10 digits)"
}


def quipu_decode(x):
    """Decode quipu knot groups back to decimal numbers. Input: matrix. Output: array."""
    mat = np.asarray(x, dtype=np.float64)
    if mat.ndim == 1:
        mat = mat.reshape(1, -1)
    results = []
    for row in mat:
        val = 0
        for digit in row:
            val = val * 10 + int(digit)
        results.append(float(val))
    return np.array(results)


OPERATIONS["quipu_decode"] = {
    "fn": quipu_decode,
    "input_type": "matrix",
    "output_type": "array",
    "description": "Decode quipu knot groups to decimal numbers"
}


def hierarchical_sum(x):
    """Tree-structured hierarchical summation (quipu pendant groups). Input: array. Output: scalar.
    Treats array as a tree: pairs sum, then pairs of pairs sum, etc."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    level = arr.copy()
    while len(level) > 1:
        new_level = []
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                new_level.append(level[i] + level[i + 1])
            else:
                new_level.append(level[i])
        level = np.array(new_level)
    return float(level[0])


OPERATIONS["hierarchical_sum"] = {
    "fn": hierarchical_sum,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Tree-structured hierarchical summation (quipu style)"
}


def pendant_group_aggregate(x):
    """Group pendant cords and compute group sums. Input: array. Output: array.
    Groups of 3 (typical quipu grouping)."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    group_size = 3
    groups = []
    for i in range(0, len(arr), group_size):
        groups.append(np.sum(arr[i:i + group_size]))
    return np.array(groups)


OPERATIONS["pendant_group_aggregate"] = {
    "fn": pendant_group_aggregate,
    "input_type": "array",
    "output_type": "array",
    "description": "Aggregate pendant cord groups (sums of groups of 3)"
}


def subsidiary_cord_tree(x):
    """Build subsidiary cord tree structure: parent-child sum relationships. Input: array. Output: matrix.
    Row i: [value, parent_sum, depth, group_index]."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr)
    result = np.zeros((n, 4), dtype=np.float64)
    group_size = 3
    for i in range(n):
        group_idx = i // group_size
        group_start = group_idx * group_size
        group_end = min(group_start + group_size, n)
        parent_sum = np.sum(arr[group_start:group_end])
        depth = 0 if i % group_size == 0 else 1
        result[i] = [arr[i], parent_sum, depth, group_idx]
    return result


OPERATIONS["subsidiary_cord_tree"] = {
    "fn": subsidiary_cord_tree,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Build subsidiary cord tree with parent-child sum relationships"
}


def cross_cord_checksum(x):
    """Compute cross-cord checksum (column sums across pendant groups). Input: matrix. Output: array."""
    mat = np.asarray(x, dtype=np.float64)
    if mat.ndim == 1:
        # Reshape into rows of 3
        n = len(mat)
        cols = 3
        rows = (n + cols - 1) // cols
        padded = np.zeros(rows * cols)
        padded[:n] = mat
        mat = padded.reshape(rows, cols)
    return np.sum(mat, axis=0)


OPERATIONS["cross_cord_checksum"] = {
    "fn": cross_cord_checksum,
    "input_type": "matrix",
    "output_type": "array",
    "description": "Cross-cord checksum (column sums across pendant groups)"
}


def quipu_to_tree_matrix(x):
    """Convert quipu data to adjacency-like tree matrix. Input: array. Output: matrix.
    Creates a hierarchical adjacency matrix for the pendant structure."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr)
    # Create tree: root -> groups -> leaves
    # Total nodes = 1 (root) + ceil(n/3) (groups) + n (leaves)
    group_size = 3
    n_groups = (n + group_size - 1) // group_size
    total = 1 + n_groups + n
    adj = np.zeros((total, total), dtype=np.float64)
    # Root (0) connects to groups (1..n_groups)
    for g in range(n_groups):
        adj[0, 1 + g] = 1.0
        adj[1 + g, 0] = 1.0
    # Groups connect to leaves
    for i in range(n):
        g = i // group_size
        leaf_idx = 1 + n_groups + i
        adj[1 + g, leaf_idx] = arr[i]
        adj[leaf_idx, 1 + g] = arr[i]
    return adj


OPERATIONS["quipu_to_tree_matrix"] = {
    "fn": quipu_to_tree_matrix,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Convert quipu data to tree adjacency matrix"
}


def quipu_information_density(x):
    """Measure information density: bits per cord. Input: array. Output: scalar."""
    arr = np.asarray(x, dtype=np.float64).flatten()
    n = len(arr)
    if n == 0:
        return 0.0
    # Each cord can represent 0-9 knots per position, with up to ~6 positions
    # Information = log2 of range of representable values
    max_val = np.max(np.abs(arr))
    if max_val == 0:
        return 0.0
    total_bits = np.log2(max_val + 1) * n
    return float(total_bits / n)


OPERATIONS["quipu_information_density"] = {
    "fn": quipu_information_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Measure information density (bits per cord)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
