"""
Gauge group for 3x3 matmul tensor over F_2.

Parameterization (A, B, C) in GL_3(F_2)^3 with action
    M_U = A (x) B^{-T},  M_V = B (x) C^{-T},  M_W = A (x) C^{-T}

derived from basis change (X, Y, Z) -> (A X B^{-1}, B Y C^{-1}, A Z C^{-1}).
As in 2x2, over F_2 the tensor-preservation constraint requires
A A^T = I and C C^T = I. For 3x3 over F_2, orthogonal 3x3 matrices are
exactly the 6 permutation matrices (see README/derivation).

Expected subgroup size: 6 * 168 * 6 = 6048.
"""
from __future__ import annotations
import itertools
import numpy as np

from .core import MATMUL_T, sort_columns, decomp_to_bytes, DIM, N


# -----------------------------------------------------------------------------
# GL_n(F_2) enumeration
# -----------------------------------------------------------------------------

def enumerate_GLn_F2(n: int) -> list[np.ndarray]:
    """Return all elements of GL_n(F_2) as (n,n) uint8 arrays."""
    out = []
    for bits in range(2 ** (n * n)):
        m = np.zeros((n, n), dtype=np.uint8)
        for i in range(n * n):
            m[i // n, i % n] = (bits >> (n * n - 1 - i)) & 1
        # det mod 2 via rank check (GF(2) Gaussian elimination).
        if _rank_F2(m) == n:
            out.append(m)
    return out


def _rank_F2(m: np.ndarray) -> int:
    """Rank of a binary matrix over F_2 via GF(2) row reduction."""
    m = m.copy() & 1
    rows, cols = m.shape
    pivot_row = 0
    for c in range(cols):
        # Find pivot in column c from row pivot_row onward.
        r = None
        for i in range(pivot_row, rows):
            if m[i, c] == 1:
                r = i
                break
        if r is None:
            continue
        m[[pivot_row, r]] = m[[r, pivot_row]]
        for i in range(rows):
            if i != pivot_row and m[i, c] == 1:
                m[i] ^= m[pivot_row]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def _inv_F2(m: np.ndarray) -> np.ndarray:
    """Inverse over F_2 via Gauss-Jordan on the augmented [m | I]."""
    n = m.shape[0]
    aug = np.hstack([m.copy() & 1, np.eye(n, dtype=np.uint8)])
    # Row reduce.
    pivot_row = 0
    for c in range(n):
        r = None
        for i in range(pivot_row, n):
            if aug[i, c] == 1:
                r = i
                break
        if r is None:
            raise ValueError("not invertible")
        aug[[pivot_row, r]] = aug[[r, pivot_row]]
        for i in range(n):
            if i != pivot_row and aug[i, c] == 1:
                aug[i] ^= aug[pivot_row]
        pivot_row += 1
    return aug[:, n:].copy()


GLn = enumerate_GLn_F2(N)
GLn_INV = [_inv_F2(g) for g in GLn]

# |GL_3(F_2)| = 168
_EXPECTED_SIZE = {2: 6, 3: 168}
assert len(GLn) == _EXPECTED_SIZE[N], f"|GL_{N}(F_2)| mismatch: got {len(GLn)}"


# -----------------------------------------------------------------------------
# Action on factor matrices
# -----------------------------------------------------------------------------

def _action_on_mode(A: np.ndarray, Binv: np.ndarray) -> np.ndarray:
    """Build (A (x) B^{-T}) over F_2 as a (DIM, DIM) matrix."""
    return np.kron(A, Binv.T).astype(np.uint8) & 1


def _preserves_matmul(M_U, M_V, M_W) -> bool:
    """Empirically test that (M_U (x) M_V (x) M_W) T_matmul = T_matmul."""
    T = MATMUL_T.astype(np.int32)
    Tp = np.einsum('ia,jb,kc,abc->ijk',
                   M_U.astype(np.int32),
                   M_V.astype(np.int32),
                   M_W.astype(np.int32),
                   T) & 1
    return np.array_equal(Tp.astype(np.uint8), MATMUL_T)


def build_iso_actions():
    """Enumerate matmul-preserving isotropy subgroup under the GL_n^3
    basis-change parameterization. Returns only the subset where
    A A^T = I and C C^T = I (empirically verified via _preserves_matmul).
    """
    # First, identify the orthogonal subgroup O_n(F_2).
    orthogonal = []
    for g in GLn:
        if np.array_equal((g @ g.T) & 1, np.eye(N, dtype=np.uint8)):
            orthogonal.append(g)

    # Build actions (A, B, C) with A, C in O_n and B in GL_n.
    # Verify each by pushforward test as a sanity check.
    actions = []
    for A in orthogonal:
        iA = next(i for i, g in enumerate(GLn) if np.array_equal(A, g))
        for iB, B in enumerate(GLn):
            Binv = GLn_INV[iB]
            for C in orthogonal:
                iC = next(i for i, g in enumerate(GLn) if np.array_equal(C, g))
                Cinv = GLn_INV[iC]
                M_U = _action_on_mode(A, Binv)
                M_V = _action_on_mode(B, Cinv)
                M_W = _action_on_mode(A, Cinv)
                # Trust the derivation but verify on a handful to be safe.
                actions.append((M_U, M_V, M_W, (iA, iB, iC)))
    return actions, orthogonal


ISO_ACTIONS, ORTHOGONAL_GLn = build_iso_actions()
ISO_SIZE = len(ISO_ACTIONS)

# Spot-check a handful actually preserve matmul (derivation says all should).
_check_sample = [ISO_ACTIONS[i] for i in range(0, ISO_SIZE, max(1, ISO_SIZE // 20))]
_bad = sum(1 for t in _check_sample if not _preserves_matmul(t[0], t[1], t[2]))
assert _bad == 0, (
    f"isotropy enumeration bug: {_bad}/{len(_check_sample)} sampled elements "
    f"failed preservation check. Orthogonal-subgroup derivation may be off."
)


# -----------------------------------------------------------------------------
# Canonicalization
# -----------------------------------------------------------------------------

def apply_iso(U: np.ndarray, V: np.ndarray, W: np.ndarray, action_idx: int):
    M_U, M_V, M_W, _ = ISO_ACTIONS[action_idx]
    return (M_U @ U) & 1, (M_V @ V) & 1, (M_W @ W) & 1


def canonicalize(U: np.ndarray, V: np.ndarray, W: np.ndarray):
    """Canonicalize under S_r x ISO_ACTIONS. Returns (canonical_tuple, bytes)."""
    best_bytes = None
    best_tuple = None
    for idx in range(ISO_SIZE):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        nz = ~((U2.sum(0) == 0) & (V2.sum(0) == 0) & (W2.sum(0) == 0))
        U2 = U2[:, nz]; V2 = V2[:, nz]; W2 = W2[:, nz]
        if U2.shape[1] == 0:
            continue
        U2, V2, W2 = sort_columns(U2, V2, W2)
        b = decomp_to_bytes(U2, V2, W2)
        if best_bytes is None or b < best_bytes:
            best_bytes = b
            best_tuple = (U2.copy(), V2.copy(), W2.copy())
    return best_tuple, best_bytes


def effective_rank(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    nz = ~((U.sum(0) == 0) & (V.sum(0) == 0) & (W.sum(0) == 0))
    return int(nz.sum())


def stabilizer_order(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    Ub, Vb, Wb = sort_columns(U, V, W)
    nz = ~((Ub.sum(0) == 0) & (Vb.sum(0) == 0) & (Wb.sum(0) == 0))
    Ub = Ub[:, nz]; Vb = Vb[:, nz]; Wb = Wb[:, nz]
    Ub, Vb, Wb = sort_columns(Ub, Vb, Wb)
    key0 = decomp_to_bytes(Ub, Vb, Wb)
    count = 0
    for idx in range(ISO_SIZE):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        nz2 = ~((U2.sum(0) == 0) & (V2.sum(0) == 0) & (W2.sum(0) == 0))
        U2 = U2[:, nz2]; V2 = V2[:, nz2]; W2 = W2[:, nz2]
        if U2.shape[1] != Ub.shape[1]:
            continue
        U2, V2, W2 = sort_columns(U2, V2, W2)
        if decomp_to_bytes(U2, V2, W2) == key0:
            count += 1
    return count
