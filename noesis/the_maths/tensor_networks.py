"""
Tensor Networks -- Matrix product states, MERA contraction, bond dimension, entanglement entropy

Connects to: [clifford_algebra, representation_theory, homological_algebra, information_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "tensor_networks"
OPERATIONS = {}


def _array_to_mps(x, bond_dim=2):
    """Convert array to a simple MPS with given bond dimension."""
    n = len(x)
    # Each site tensor A[i] has shape (bond_dim, d, bond_dim) where d=physical dim
    # For simplicity, d=2 (qubit-like)
    d = 2
    tensors = []
    for i in range(n):
        A = np.zeros((bond_dim, d, bond_dim))
        # Fill with array values
        A[0, 0, 0] = np.cos(x[i])
        A[0, 1, 1] = np.sin(x[i])
        if bond_dim > 1:
            A[1, 0, 1] = np.sin(x[i]) * 0.5
            A[1, 1, 0] = np.cos(x[i]) * 0.5
        tensors.append(A)
    return tensors


def matrix_product_state_contract(x):
    """Contract an MPS to get the full state vector. Input: array. Output: array."""
    tensors = _array_to_mps(x)
    n = len(tensors)
    if n == 0:
        return np.array([1.0])
    # Contract left to right
    # Start with first tensor, trace over left boundary
    result = tensors[0][0, :, :]  # shape (d, chi)
    for i in range(1, n):
        # result has shape (..., chi), tensor has shape (chi, d, chi)
        # Contract: sum over chi index
        new_result = np.einsum('...i,ijk->...jk', result, tensors[i])
        shape = new_result.shape
        result = new_result.reshape(-1, shape[-1])
    # Trace over right boundary
    result = result[:, 0]  # take first component of right bond
    # Normalize
    norm = np.linalg.norm(result)
    if norm > 0:
        result = result / norm
    return result


OPERATIONS["matrix_product_state_contract"] = {
    "fn": matrix_product_state_contract,
    "input_type": "array",
    "output_type": "array",
    "description": "Contract MPS tensors to obtain full state vector"
}


def mps_bond_dimension(x):
    """Compute effective bond dimension needed to represent state.
    Input: array. Output: scalar."""
    n = len(x)
    if n <= 1:
        return 1.0
    # Build a matrix from the array (reshape as bipartition)
    mid = n // 2
    rows = 2 ** min(mid, 8)
    cols = 2 ** min(n - mid, 8)
    # Create a state vector
    state = np.zeros(max(rows, cols))
    state[:min(len(x), len(state))] = x[:min(len(x), len(state))]
    norm = np.linalg.norm(state)
    if norm > 0:
        state /= norm
    # Reshape and SVD
    dim = min(rows, cols, len(state))
    mat_r = int(np.sqrt(dim))
    if mat_r < 1:
        mat_r = 1
    mat_c = dim // mat_r
    if mat_r * mat_c == 0:
        return 1.0
    mat = state[:mat_r * mat_c].reshape(mat_r, mat_c)
    svd_vals = np.linalg.svd(mat, compute_uv=False)
    # Effective bond dim = number of significant singular values
    threshold = 1e-10
    return float(np.sum(svd_vals > threshold))


OPERATIONS["mps_bond_dimension"] = {
    "fn": mps_bond_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Effective bond dimension from Schmidt decomposition"
}


def mps_entanglement_entropy(x):
    """Entanglement entropy at the middle bipartition. Input: array. Output: scalar."""
    n = len(x)
    state = x / (np.linalg.norm(x) + 1e-30)
    mid = n // 2
    if mid == 0:
        mid = 1
    mat = state[:mid * (n - mid) if mid * (n - mid) <= n else n]
    rows = mid
    cols = len(mat) // rows if rows > 0 else 1
    if rows * cols == 0:
        return 0.0
    mat = mat[:rows * cols].reshape(rows, cols)
    svd_vals = np.linalg.svd(mat, compute_uv=False)
    svd_vals = svd_vals[svd_vals > 1e-30]
    probs = svd_vals ** 2
    probs = probs / np.sum(probs)
    entropy = -np.sum(probs * np.log(probs + 1e-30))
    return float(entropy)


OPERATIONS["mps_entanglement_entropy"] = {
    "fn": mps_entanglement_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Von Neumann entanglement entropy at middle bipartition"
}


def tensor_train_decompose(x):
    """Decompose array into tensor train (TT) cores via successive SVDs.
    Returns flattened TT cores. Input: array. Output: array."""
    n = len(x)
    if n < 4:
        return x.copy()
    # Reshape into matrix and SVD
    rows = 2
    cols = n // 2
    mat = x[:rows * cols].reshape(rows, cols)
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    rank = min(len(S), 2)
    core1 = U[:, :rank]  # (rows, rank)
    remainder = np.diag(S[:rank]) @ Vt[:rank, :]  # (rank, cols)
    return np.concatenate([core1.ravel(), remainder.ravel()])


OPERATIONS["tensor_train_decompose"] = {
    "fn": tensor_train_decompose,
    "input_type": "array",
    "output_type": "array",
    "description": "Tensor train decomposition via successive SVDs"
}


def tensor_train_round(x):
    """TT-rounding: truncate bond dimensions. Input: array. Output: array."""
    n = len(x)
    rows = int(np.sqrt(n))
    if rows < 2:
        rows = 2
    cols = n // rows
    if rows * cols == 0:
        return x.copy()
    mat = x[:rows * cols].reshape(rows, cols)
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    # Truncate to rank 1
    approx = S[0] * np.outer(U[:, 0], Vt[0, :])
    return approx.ravel()


OPERATIONS["tensor_train_round"] = {
    "fn": tensor_train_round,
    "input_type": "array",
    "output_type": "array",
    "description": "TT-rounding via SVD truncation to lower bond dimension"
}


def mera_coarse_grain_step(x):
    """One MERA coarse-graining step: disentangle then isometry.
    Input: array (state on fine lattice). Output: array (coarse-grained state)."""
    n = len(x)
    if n < 2:
        return x.copy()
    # Disentangler: pairwise unitary on adjacent sites
    disentangled = np.zeros(n)
    for i in range(0, n - 1, 2):
        # Simple 2-site operation (Hadamard-like)
        a, b = x[i], x[i + 1]
        disentangled[i] = (a + b) / np.sqrt(2)
        disentangled[i + 1] = (a - b) / np.sqrt(2)
    if n % 2 == 1:
        disentangled[-1] = x[-1]
    # Isometry: coarse-grain by keeping every other site
    coarse = disentangled[::2]
    norm = np.linalg.norm(coarse)
    if norm > 0:
        coarse = coarse / norm
    return coarse


OPERATIONS["mera_coarse_grain_step"] = {
    "fn": mera_coarse_grain_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One MERA coarse-graining step (disentangle + isometry)"
}


def tensor_trace(x):
    """Trace of a tensor (interpreted as matrix). Input: array. Output: scalar."""
    n = len(x)
    side = int(np.sqrt(n))
    if side * side > n:
        side -= 1
    if side < 1:
        return float(x[0]) if n > 0 else 0.0
    mat = x[:side * side].reshape(side, side)
    return float(np.trace(mat))


OPERATIONS["tensor_trace"] = {
    "fn": tensor_trace,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Trace of tensor reshaped as square matrix"
}


def tensor_network_contract_pair(x):
    """Contract two tensors (first half x second half) over shared index.
    Input: array. Output: array."""
    n = len(x)
    half = n // 2
    a = x[:half]
    b = x[half:2 * half]
    if len(a) == 0 or len(b) == 0:
        return x.copy()
    # Reshape each as matrices and multiply
    side_a = int(np.sqrt(len(a)))
    if side_a < 1:
        side_a = 1
    cols_a = len(a) // side_a
    side_b = cols_a
    cols_b = len(b) // side_b if side_b > 0 else len(b)
    if side_a * cols_a == 0 or side_b * cols_b == 0:
        return x.copy()
    A_mat = a[:side_a * cols_a].reshape(side_a, cols_a)
    B_mat = b[:side_b * cols_b].reshape(side_b, cols_b)
    result = A_mat @ B_mat
    return result.ravel()


OPERATIONS["tensor_network_contract_pair"] = {
    "fn": tensor_network_contract_pair,
    "input_type": "array",
    "output_type": "array",
    "description": "Contract two tensors over shared bond index"
}


def bond_dimension_truncate(x):
    """Truncate to target bond dimension (rank-2 approximation).
    Input: array. Output: array."""
    n = len(x)
    side = int(np.sqrt(n))
    if side < 2:
        return x.copy()
    cols = n // side
    mat = x[:side * cols].reshape(side, cols)
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    rank = min(2, len(S))
    approx = U[:, :rank] @ np.diag(S[:rank]) @ Vt[:rank, :]
    return approx.ravel()


OPERATIONS["bond_dimension_truncate"] = {
    "fn": bond_dimension_truncate,
    "input_type": "array",
    "output_type": "array",
    "description": "Truncate tensor to target bond dimension via SVD"
}


def isometry_check(x):
    """Check if reshaped array forms an isometry (V^T V = I). Input: array. Output: scalar (deviation from isometry)."""
    n = len(x)
    rows = int(np.sqrt(n))
    if rows < 2:
        return float(abs(np.linalg.norm(x) - 1.0))
    cols = n // rows
    if rows * cols == 0:
        return 1.0
    mat = x[:rows * cols].reshape(rows, cols)
    if rows >= cols:
        product = mat.T @ mat
        identity = np.eye(cols)
    else:
        product = mat @ mat.T
        identity = np.eye(rows)
    return float(np.linalg.norm(product - identity))


OPERATIONS["isometry_check"] = {
    "fn": isometry_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Frobenius norm deviation from isometry condition"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
