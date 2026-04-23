"""
Flip-graph algebraic moves for tensor decompositions over F_2.

Two operators:

1. try_reduce_3_to_2(U, V, W, i, j, k) — attempt rank-reducing move.
   If T_ijk = a_i⊗b_i⊗c_i + a_j⊗b_j⊗c_j + a_k⊗b_k⊗c_k has tensor rank
   ≤ 2 over F_2, find a rank-2 decomposition and return a new
   (U', V', W') with rank reduced by 1 (3 columns -> 2 columns).

2. try_swap_2_to_2(U, V, W, i, j) — rank-preserving move.
   If S_ij = a_i⊗b_i⊗c_i + a_j⊗b_j⊗c_j has tensor rank = 2, find a
   DIFFERENT rank-2 decomposition (under an alternative F_2 basis of
   the mode-3 column space) and return a new (U', V', W').

Both moves preserve the global tensor (T_full unchanged ⟹ remains a
valid matmul decomposition). By construction.

Core primitive: rank_2_tensor_decomp — decompose a rank-≤2 tensor over
F_2 into a sum of ≤2 rank-1 tensors, or return None if tensor rank > 2.
"""
from __future__ import annotations
import numpy as np

from .core import DIM, MATMUL_T, is_matmul_decomp


# -----------------------------------------------------------------------------
# F_2 linear algebra primitives
# -----------------------------------------------------------------------------

def rref_F2(A):
    """Row reduce A (uint8 binary) over F_2. Returns (rref, rank, pivots)."""
    A = A.copy() & 1
    m, n = A.shape
    pivots = []
    row = 0
    for c in range(n):
        r_pivot = None
        for rr in range(row, m):
            if A[rr, c] == 1:
                r_pivot = rr
                break
        if r_pivot is None:
            continue
        A[[row, r_pivot]] = A[[r_pivot, row]]
        for rr in range(m):
            if rr != row and A[rr, c] == 1:
                A[rr] ^= A[row]
        pivots.append(c)
        row += 1
        if row >= m:
            break
    return A, len(pivots), pivots


def rank_F2(A):
    _, r, _ = rref_F2(A)
    return r


def col_basis_F2(A):
    """Return a basis for the column space of A over F_2, as a list of columns.

    Uses the fact: pivot columns of rref(A) index linearly-independent
    columns of A.
    """
    _, _, pivots = rref_F2(A)
    return [A[:, c].copy() for c in pivots]


def solve_F2(A, b):
    """Solve A x = b over F_2. Returns x (any solution) or None."""
    m, n = A.shape
    aug = np.hstack([A.copy() & 1, b.reshape(-1, 1) & 1])
    row = 0
    pivot_col = [-1] * n
    for c in range(n):
        r_pivot = None
        for rr in range(row, m):
            if aug[rr, c] == 1:
                r_pivot = rr; break
        if r_pivot is None:
            continue
        aug[[row, r_pivot]] = aug[[r_pivot, row]]
        for rr in range(m):
            if rr != row and aug[rr, c] == 1:
                aug[rr] ^= aug[row]
        pivot_col[c] = row
        row += 1
        if row >= m:
            break
    for rr in range(m):
        if aug[rr, :n].sum() == 0 and aug[rr, n] == 1:
            return None
    x = np.zeros(n, dtype=np.uint8)
    for c in range(n):
        if pivot_col[c] != -1:
            x[c] = aug[pivot_col[c], n]
    return x


def factor_rank1_matrix_F2(mat):
    """If a 9x9 matrix is rank 1 over F_2, return (u, v) such that mat = u v^T.

    If mat is zero, return (zeros, zeros). If rank > 1, return None.
    """
    if mat.sum() == 0:
        z = np.zeros(9, dtype=np.uint8)
        return z, z
    # Find a non-zero row — that's v (up to scale over F_2).
    for i in range(9):
        if mat[i].sum() > 0:
            v = mat[i].copy()
            break
    # u[j] = 1 iff mat[j] is non-zero (and equals v).
    u = np.zeros(9, dtype=np.uint8)
    for j in range(9):
        row = mat[j]
        if row.sum() == 0:
            u[j] = 0
        elif np.array_equal(row, v):
            u[j] = 1
        else:
            return None   # rank > 1
    return u, v


# -----------------------------------------------------------------------------
# GL_2(F_2) — 6 elements — used for basis rotations in rank-2 col space.
# -----------------------------------------------------------------------------

GL2_F2 = [
    np.array([[1, 0], [0, 1]], dtype=np.uint8),
    np.array([[0, 1], [1, 0]], dtype=np.uint8),
    np.array([[1, 1], [0, 1]], dtype=np.uint8),
    np.array([[1, 0], [1, 1]], dtype=np.uint8),
    np.array([[0, 1], [1, 1]], dtype=np.uint8),
    np.array([[1, 1], [1, 0]], dtype=np.uint8),
]


# -----------------------------------------------------------------------------
# Rank-≤2 tensor decomposition over F_2
# -----------------------------------------------------------------------------

def rank_2_tensor_decomp(T):
    """Given T in F_2^{9x9x9}, return a list of rank-1 factors summing to T,
    or None if T has tensor rank > 2.

    Returns: list of (u, v, w) tuples, each u, v, w in F_2^9, length ≤ 2.
    """
    # Mode-3 flattening: M[p, q, s] -> M'[p*9+q, s].
    M = T.reshape(81, 9).astype(np.uint8)

    rM = rank_F2(M)
    if rM > 2:
        return None

    if rM == 0:
        return []   # T = 0

    # Find basis columns.
    basis = col_basis_F2(M)

    if rM == 1:
        u, v = factor_rank1_matrix_F2(basis[0].reshape(9, 9))
        if u is None:
            return None
        # Find w: w[s] such that M[:, s] = (u⊗v) * w[s].
        outer = np.outer(u, v).flatten() & 1
        w = np.zeros(9, dtype=np.uint8)
        for s in range(9):
            col = M[:, s]
            if col.sum() == 0:
                w[s] = 0
            elif np.array_equal(col, outer):
                w[s] = 1
            else:
                return None
        return [(u, v, w)]

    # rM == 2. Try all 6 basis rotations g in GL_2(F_2).
    c1, c2 = basis[0], basis[1]
    for g in GL2_F2:
        # X columns are linear combinations of (c1, c2) by g.
        X_col1 = (g[0, 0] * c1 + g[1, 0] * c2) & 1
        X_col2 = (g[0, 1] * c1 + g[1, 1] * c2) & 1
        f1 = factor_rank1_matrix_F2(X_col1.reshape(9, 9))
        f2 = factor_rank1_matrix_F2(X_col2.reshape(9, 9))
        if f1 is None or f2 is None:
            continue
        u1, v1 = f1
        u2, v2 = f2
        if u1.sum() == 0 and u2.sum() == 0:
            continue
        # Solve X @ [w1 w2]^T = M. For each s, find (w1_s, w2_s) such that
        # w1_s * X_col1 + w2_s * X_col2 = M[:, s].
        X_mat = np.column_stack([X_col1, X_col2])
        W = np.zeros((9, 2), dtype=np.uint8)
        ok = True
        for s in range(9):
            w = solve_F2(X_mat, M[:, s])
            if w is None:
                ok = False; break
            W[s] = w
        if not ok:
            continue
        # Validate: verify X_col1 ⊗ W[:, 0] + X_col2 ⊗ W[:, 1] reshape equals M.
        # (belt-and-suspenders)
        reconstructed = (np.outer(X_col1, W[:, 0]) ^ np.outer(X_col2, W[:, 1])) & 1
        if not np.array_equal(reconstructed, M):
            continue
        return [(u1, v1, W[:, 0]), (u2, v2, W[:, 1])]

    return None


# -----------------------------------------------------------------------------
# Flip-graph mutations
# -----------------------------------------------------------------------------

def compute_T_sum(U, V, W, cols):
    """Compute sum of rank-1 contributions over listed columns, as 9x9x9 tensor."""
    T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    for k in cols:
        T ^= np.einsum('p,q,s->pqs', U[:, k], V[:, k], W[:, k],
                       dtype=np.uint8) & 1
    return T & 1


def try_reduce_3_to_2(U, V, W, i, j, k):
    """If T_ijk has rank ≤ 2, return (U', V', W') with columns i, j, k
    replaced by the rank-≤2 decomposition (1 fewer columns total).

    Returns None if T_ijk has rank > 2 (move does not apply).
    """
    assert i != j and j != k and i != k
    T_ijk = compute_T_sum(U, V, W, [i, j, k])
    decomp = rank_2_tensor_decomp(T_ijk)
    if decomp is None:
        return None

    # Build new factor matrices: drop columns {i, j, k}, append the new ones.
    keep = [c for c in range(U.shape[1]) if c not in (i, j, k)]
    U_new = U[:, keep].copy()
    V_new = V[:, keep].copy()
    W_new = W[:, keep].copy()
    for (u, v, w) in decomp:
        if u.sum() == 0 or v.sum() == 0 or w.sum() == 0:
            continue   # trivial, skip
        U_new = np.column_stack([U_new, u])
        V_new = np.column_stack([V_new, v])
        W_new = np.column_stack([W_new, w])
    return U_new, V_new, W_new


def try_swap_2_to_2(U, V, W, i, j):
    """If S_ij has rank = 2, try to find an alternative rank-2 decomposition
    (by trying all 6 basis rotations in GL_2(F_2)). Returns a new (U', V', W')
    with columns i, j replaced by the alternative, or None if no alternative
    exists.
    """
    assert i != j
    S_ij = compute_T_sum(U, V, W, [i, j])
    decomp = rank_2_tensor_decomp(S_ij)
    if decomp is None or len(decomp) < 2:
        return None
    # The canonical "first" decomposition returned by rank_2_tensor_decomp
    # corresponds to ONE choice of g in GL_2(F_2). To get an alternative,
    # we reshape the choice: iterate through all 6 g's and pick the first
    # that gives a DIFFERENT result from the current (i, j).

    # Recompute with all g's.
    M = S_ij.reshape(81, 9).astype(np.uint8)
    rM = rank_F2(M)
    if rM != 2:
        return None
    basis = col_basis_F2(M)
    c1, c2 = basis[0], basis[1]

    current_cols = {bytes(U[:, i].tobytes() + V[:, i].tobytes() + W[:, i].tobytes()),
                    bytes(U[:, j].tobytes() + V[:, j].tobytes() + W[:, j].tobytes())}

    for g in GL2_F2:
        X_col1 = (g[0, 0] * c1 + g[1, 0] * c2) & 1
        X_col2 = (g[0, 1] * c1 + g[1, 1] * c2) & 1
        f1 = factor_rank1_matrix_F2(X_col1.reshape(9, 9))
        f2 = factor_rank1_matrix_F2(X_col2.reshape(9, 9))
        if f1 is None or f2 is None:
            continue
        u1, v1 = f1; u2, v2 = f2
        X_mat = np.column_stack([X_col1, X_col2])
        W_sol = np.zeros((9, 2), dtype=np.uint8)
        ok = True
        for s in range(9):
            w = solve_F2(X_mat, M[:, s])
            if w is None:
                ok = False; break
            W_sol[s] = w
        if not ok:
            continue
        # Check if decomp differs from current.
        new1 = bytes(u1.tobytes() + v1.tobytes() + W_sol[:, 0].tobytes())
        new2 = bytes(u2.tobytes() + v2.tobytes() + W_sol[:, 1].tobytes())
        new_cols = {new1, new2}
        if new_cols == current_cols:
            continue   # same decomp
        # Build output.
        keep = [c for c in range(U.shape[1]) if c not in (i, j)]
        U_new = U[:, keep].copy()
        V_new = V[:, keep].copy()
        W_new = W[:, keep].copy()
        for (u, v, w) in [(u1, v1, W_sol[:, 0]), (u2, v2, W_sol[:, 1])]:
            if u.sum() == 0 or v.sum() == 0 or w.sum() == 0:
                continue
            U_new = np.column_stack([U_new, u])
            V_new = np.column_stack([V_new, v])
            W_new = np.column_stack([W_new, w])
        return U_new, V_new, W_new

    return None
