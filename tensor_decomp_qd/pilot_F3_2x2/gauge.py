"""
Gauge group for 2x2 matmul over F_3.

Same structure as F_2 pilot:
  - Matmul isotropy subgroup under the parameterization
    M_U = A (x) B^{-T}, M_V = B (x) C^{-T}, M_W = A (x) C^{-T}
    where (A, B, C) in GL_2(F_3)^3.
  - Tensor-preservation over F_p requires A A^T = I and C C^T = I
    (orthogonality mod p). Over F_3 this is non-trivial.

Expected: |GL_2(F_3)| = 48, |O_2(F_3)| = 8, isotropy subgroup size = 8*48*8 = 3072.
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, DIM, N, P, sort_columns, decomp_to_bytes, normalize_all_columns


# -----------------------------------------------------------------------------
# F_3 linear algebra primitives
# -----------------------------------------------------------------------------

def rref_Fp(A: np.ndarray, p: int = P):
    """Row-reduce A mod p. Returns (rref, rank, pivots)."""
    A = A.copy().astype(np.int64) % p
    m, n = A.shape
    pivots = []
    row = 0
    for c in range(n):
        # Find pivot.
        r_pivot = None
        for rr in range(row, m):
            if A[rr, c] != 0:
                r_pivot = rr
                break
        if r_pivot is None:
            continue
        A[[row, r_pivot]] = A[[r_pivot, row]]
        # Normalize pivot row so A[row, c] = 1.
        inv = pow(int(A[row, c]), -1, p)
        A[row] = (A[row] * inv) % p
        # Eliminate other rows.
        for rr in range(m):
            if rr != row and A[rr, c] != 0:
                factor = A[rr, c]
                A[rr] = (A[rr] - factor * A[row]) % p
        pivots.append(c)
        row += 1
        if row >= m:
            break
    return A.astype(np.int8), len(pivots), pivots


def rank_Fp(A, p=P):
    _, r, _ = rref_Fp(A, p)
    return r


def inv_Fp(A: np.ndarray, p: int = P):
    """Invert A over F_p via Gauss-Jordan on [A | I]."""
    n = A.shape[0]
    aug = np.hstack([A.copy().astype(np.int64) % p,
                     np.eye(n, dtype=np.int64)]) % p
    row = 0
    for c in range(n):
        r_pivot = None
        for rr in range(row, n):
            if aug[rr, c] != 0:
                r_pivot = rr
                break
        if r_pivot is None:
            raise ValueError("not invertible over F_p")
        aug[[row, r_pivot]] = aug[[r_pivot, row]]
        inv = pow(int(aug[row, c]), -1, p)
        aug[row] = (aug[row] * inv) % p
        for rr in range(n):
            if rr != row and aug[rr, c] != 0:
                factor = aug[rr, c]
                aug[rr] = (aug[rr] - factor * aug[row]) % p
        row += 1
    return aug[:, n:].astype(np.int8)


def det_Fp_2x2(m, p=P):
    """Determinant mod p for 2x2 matrices."""
    return (int(m[0, 0]) * int(m[1, 1]) - int(m[0, 1]) * int(m[1, 0])) % p


def enumerate_GLn_Fp(n: int, p: int = P) -> list[np.ndarray]:
    """All invertible n x n matrices over F_p."""
    out = []
    for idx in range(p ** (n * n)):
        m = np.zeros((n, n), dtype=np.int8)
        tmp = idx
        for pos in range(n * n - 1, -1, -1):
            m[pos // n, pos % n] = tmp % p
            tmp //= p
        # Check invertible.
        r = rank_Fp(m, p)
        if r == n:
            out.append(m)
    return out


GLn = enumerate_GLn_Fp(N, P)
GLn_INV = [inv_Fp(g, P) for g in GLn]

_EXPECTED_GLN_SIZE = {
    (2, 3): 48,
    (3, 3): 11232,
}
assert len(GLn) == _EXPECTED_GLN_SIZE[(N, P)], (
    f"|GL_{N}(F_{P})| expected {_EXPECTED_GLN_SIZE[(N, P)]}, got {len(GLn)}"
)


# -----------------------------------------------------------------------------
# F_3-orthogonal subgroup of GL_n
# -----------------------------------------------------------------------------

def find_orthogonal_Fp(GLn_elements, p=P):
    """Return list of elements g in GLn with g @ g.T = I mod p."""
    out = []
    n = GLn_elements[0].shape[0]
    I = np.eye(n, dtype=np.int64)
    for g in GLn_elements:
        ggT = (g.astype(np.int64) @ g.astype(np.int64).T) % p
        if np.array_equal(ggT, I):
            out.append(g)
    return out


ORTHOGONAL_GLn = find_orthogonal_Fp(GLn, P)


# -----------------------------------------------------------------------------
# Matmul isotropy action
# -----------------------------------------------------------------------------

def _action_on_mode(A: np.ndarray, Binv: np.ndarray) -> np.ndarray:
    """Build (A (x) B^{-T}) mod p."""
    A64 = A.astype(np.int64)
    BinvT = Binv.T.astype(np.int64)
    return (np.kron(A64, BinvT) % P).astype(np.int8)


def _preserves_matmul(M_U, M_V, M_W) -> bool:
    """Check (M_U (x) M_V (x) M_W) T_matmul = T_matmul mod p."""
    T = MATMUL_T.astype(np.int64)
    Tp = np.einsum('ia,jb,kc,abc->ijk',
                   M_U.astype(np.int64),
                   M_V.astype(np.int64),
                   M_W.astype(np.int64), T) % P
    return np.array_equal(Tp.astype(np.int8), MATMUL_T)


def build_iso_actions():
    """Enumerate matmul-preserving isotropy subgroup.

    For the parameterization above with A, C orthogonal and B arbitrary.
    Over F_3 orthogonal 2x2 matrices have 8 elements.
    Expected size: 8 * 48 * 8 = 3072.
    """
    actions = []
    for A in ORTHOGONAL_GLn:
        iA = next(i for i, g in enumerate(GLn) if np.array_equal(A, g))
        for iB, B in enumerate(GLn):
            Binv = GLn_INV[iB]
            for C in ORTHOGONAL_GLn:
                iC = next(i for i, g in enumerate(GLn) if np.array_equal(C, g))
                Cinv = GLn_INV[iC]
                M_U = _action_on_mode(A, Binv)
                M_V = _action_on_mode(B, Cinv)
                M_W = _action_on_mode(A, Cinv)
                actions.append((M_U, M_V, M_W, (iA, iB, iC)))
    return actions


ISO_ACTIONS = build_iso_actions()
ISO_SIZE = len(ISO_ACTIONS)

# Validate a sample actually preserves matmul.
_sample = [ISO_ACTIONS[i] for i in range(0, ISO_SIZE, max(1, ISO_SIZE // 20))]
_bad = sum(1 for t in _sample if not _preserves_matmul(t[0], t[1], t[2]))
assert _bad == 0, f"isotropy enumeration bug: {_bad}/{len(_sample)} sampled elements failed"


# -----------------------------------------------------------------------------
# Canonicalization
# -----------------------------------------------------------------------------

def apply_iso(U: np.ndarray, V: np.ndarray, W: np.ndarray, action_idx: int):
    M_U, M_V, M_W, _ = ISO_ACTIONS[action_idx]
    return (
        (M_U.astype(np.int64) @ U.astype(np.int64) % P).astype(np.int8),
        (M_V.astype(np.int64) @ V.astype(np.int64) % P).astype(np.int8),
        (M_W.astype(np.int64) @ W.astype(np.int64) % P).astype(np.int8),
    )


def canonicalize(U, V, W):
    """Canonicalize under S_r x scaling-gauge x matmul-isotropy over F_3."""
    best_bytes = None
    best_tuple = None
    for idx in range(ISO_SIZE):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        # Drop zero columns (a or b or c all zero — contribution = 0).
        nz = ~((U2.sum(0) == 0) | (V2.sum(0) == 0) | (W2.sum(0) == 0))
        if not nz.any():
            continue
        U2 = U2[:, nz]; V2 = V2[:, nz]; W2 = W2[:, nz]
        # Normalize per-column scaling.
        U2, V2, W2 = normalize_all_columns(U2, V2, W2)
        # Sort columns.
        U2, V2, W2 = sort_columns(U2, V2, W2)
        b = decomp_to_bytes(U2, V2, W2)
        if best_bytes is None or b < best_bytes:
            best_bytes = b
            best_tuple = (U2.copy(), V2.copy(), W2.copy())
    return best_tuple, best_bytes


def effective_rank(U, V, W) -> int:
    nz = ~((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    return int(nz.sum())


def stabilizer_order(U, V, W) -> int:
    """Order of the stabilizer subgroup in matmul isotropy for this decomp
    (up to S_r x scaling gauge normalization).
    """
    Ub, Vb, Wb = U, V, W
    nz = ~((Ub.sum(0) == 0) | (Vb.sum(0) == 0) | (Wb.sum(0) == 0))
    Ub = Ub[:, nz]; Vb = Vb[:, nz]; Wb = Wb[:, nz]
    Ub, Vb, Wb = normalize_all_columns(Ub, Vb, Wb)
    Ub, Vb, Wb = sort_columns(Ub, Vb, Wb)
    key0 = decomp_to_bytes(Ub, Vb, Wb)
    count = 0
    for idx in range(ISO_SIZE):
        U2, V2, W2 = apply_iso(U, V, W, idx)
        nz2 = ~((U2.sum(0) == 0) | (V2.sum(0) == 0) | (W2.sum(0) == 0))
        if not nz2.any():
            continue
        U2 = U2[:, nz2]; V2 = V2[:, nz2]; W2 = W2[:, nz2]
        U2, V2, W2 = normalize_all_columns(U2, V2, W2)
        U2, V2, W2 = sort_columns(U2, V2, W2)
        if decomp_to_bytes(U2, V2, W2) == key0:
            count += 1
    return count
