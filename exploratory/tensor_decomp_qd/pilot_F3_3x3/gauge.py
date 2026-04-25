"""
Gauge group for 3x3 matmul over F_3.

Parameterization (A, B, C) in GL_3(F_3)^3 with action
    M_U = A (x) B^{-T},  M_V = B (x) C^{-T},  M_W = A (x) C^{-T}
Tensor-preservation: A A^T = I and C C^T = I (orthogonality mod 3).

Sizes (theoretical):
  |GL_3(F_3)| = 11232
  |O_3(F_3)|  = 48     (this 3x3 case has 48 orthogonal matrices over F_3)
  |Iso|       = 48 * 11232 * 48 = 25,878,528  (~2.6e7)

Brute-force enumeration of Iso is INFEASIBLE in this pilot. Instead we:
  - enumerate GL_3(F_3) (11232 elements; ~seconds)
  - filter to O_3(F_3)
  - provide a `random_iso_action(rng)` for SAMPLING from the matmul-isotropy
  - canonicalization is NOT brute-force — it uses gauge-INVARIANT TUPLES
    computed in descriptors.py

This module exposes only the primitives needed by the invariant-tuple
machinery (sampling from Iso, applying an Iso action, building basis-change
elements). Canonicalization itself is in descriptors.py via invariant tuple.
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, DIM, N, P, sort_columns, decomp_to_bytes, normalize_all_columns


# -----------------------------------------------------------------------------
# F_3 linear-algebra primitives.
# -----------------------------------------------------------------------------

def rref_Fp(A: np.ndarray, p: int = P):
    A = A.copy().astype(np.int64) % p
    m, n = A.shape
    pivots = []
    row = 0
    for c in range(n):
        r_pivot = None
        for rr in range(row, m):
            if A[rr, c] != 0:
                r_pivot = rr; break
        if r_pivot is None:
            continue
        A[[row, r_pivot]] = A[[r_pivot, row]]
        inv = pow(int(A[row, c]), -1, p)
        A[row] = (A[row] * inv) % p
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
    n = A.shape[0]
    aug = np.hstack([A.copy().astype(np.int64) % p, np.eye(n, dtype=np.int64)]) % p
    row = 0
    for c in range(n):
        r_pivot = None
        for rr in range(row, n):
            if aug[rr, c] != 0:
                r_pivot = rr; break
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


def det_Fp(M: np.ndarray, p: int = P) -> int:
    """Determinant of n x n matrix mod p via row reduction (parity tracking)."""
    A = M.copy().astype(np.int64) % p
    n = A.shape[0]
    det = 1
    row = 0
    for c in range(n):
        r_pivot = None
        for rr in range(row, n):
            if A[rr, c] != 0:
                r_pivot = rr; break
        if r_pivot is None:
            return 0
        if r_pivot != row:
            A[[row, r_pivot]] = A[[r_pivot, row]]
            det = (-det) % p
        det = (det * int(A[row, c])) % p
        inv = pow(int(A[row, c]), -1, p)
        A[row] = (A[row] * inv) % p
        for rr in range(row + 1, n):
            if A[rr, c] != 0:
                factor = A[rr, c]
                A[rr] = (A[rr] - factor * A[row]) % p
        row += 1
    return int(det)


# -----------------------------------------------------------------------------
# Enumerate GL_3(F_3) (~11232 elements; this fits easily in memory).
# -----------------------------------------------------------------------------

def enumerate_GLn_Fp(n: int, p: int = P) -> list[np.ndarray]:
    out = []
    for idx in range(p ** (n * n)):
        m = np.zeros((n, n), dtype=np.int8)
        tmp = idx
        for pos in range(n * n - 1, -1, -1):
            m[pos // n, pos % n] = tmp % p
            tmp //= p
        if rank_Fp(m, p) == n:
            out.append(m)
    return out


GLn = enumerate_GLn_Fp(N, P)
GLn_INV = [inv_Fp(g, P) for g in GLn]

_EXPECTED_GLN_SIZE = {(2, 3): 48, (3, 3): 11232}
assert len(GLn) == _EXPECTED_GLN_SIZE[(N, P)], (
    f"|GL_{N}(F_{P})| expected {_EXPECTED_GLN_SIZE[(N, P)]}, got {len(GLn)}"
)


# -----------------------------------------------------------------------------
# Orthogonal subgroup O_n(F_p): {g in GL_n : g g^T = I}.
# -----------------------------------------------------------------------------

def find_orthogonal_Fp(GLn_elements, p=P):
    out = []
    n = GLn_elements[0].shape[0]
    I = np.eye(n, dtype=np.int64)
    for g in GLn_elements:
        ggT = (g.astype(np.int64) @ g.astype(np.int64).T) % p
        if np.array_equal(ggT, I):
            out.append(g)
    return out


ORTHOGONAL_GLn = find_orthogonal_Fp(GLn, P)

# |O_3(F_3)| is 48 (well-known: order of orthogonal group over F_3 in dim 3).
_EXPECTED_ON = {(2, 3): 8, (3, 3): 48}
assert len(ORTHOGONAL_GLn) == _EXPECTED_ON[(N, P)], (
    f"|O_{N}(F_{P})| expected {_EXPECTED_ON[(N, P)]}, got {len(ORTHOGONAL_GLn)}"
)


# Indices into GLn for orthogonal elements (so we can look up inverses).
_GL_LOOKUP = {tuple(g.flatten().tolist()): i for i, g in enumerate(GLn)}


def _gl_index(g: np.ndarray) -> int:
    return _GL_LOOKUP[tuple(g.flatten().tolist())]


# -----------------------------------------------------------------------------
# Action on factor matrices via Kronecker products.
# -----------------------------------------------------------------------------

def _action_on_mode(A: np.ndarray, Binv: np.ndarray) -> np.ndarray:
    """(A (x) B^{-T}) mod p, returned as int8 (DIM, DIM)."""
    A64 = A.astype(np.int64)
    BinvT = Binv.T.astype(np.int64)
    return (np.kron(A64, BinvT) % P).astype(np.int8)


def build_iso_from_ABC(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    """Build (M_U, M_V, M_W) from a triple (A, B, C) with A, C orthogonal,
    B in GL_n. Returns the three factor-matrix-acting mod-p matrices."""
    iB = _gl_index(B)
    Binv = GLn_INV[iB]
    iC = _gl_index(C)
    Cinv = GLn_INV[iC]
    M_U = _action_on_mode(A, Binv)
    M_V = _action_on_mode(B, Cinv)
    M_W = _action_on_mode(A, Cinv)
    return M_U, M_V, M_W


def _preserves_matmul(M_U, M_V, M_W) -> bool:
    """Sanity check that an isotropy action preserves MATMUL_T."""
    T = MATMUL_T.astype(np.int64)
    Tp = np.einsum('ia,jb,kc,abc->ijk',
                   M_U.astype(np.int64),
                   M_V.astype(np.int64),
                   M_W.astype(np.int64), T) % P
    return np.array_equal(Tp.astype(np.int8), MATMUL_T)


def random_iso_action(rng: np.random.Generator):
    """Sample a uniform-random (A, B, C) and build the action triple."""
    iA = int(rng.integers(0, len(ORTHOGONAL_GLn)))
    iC = int(rng.integers(0, len(ORTHOGONAL_GLn)))
    iB = int(rng.integers(0, len(GLn)))
    A = ORTHOGONAL_GLn[iA]
    C = ORTHOGONAL_GLn[iC]
    B = GLn[iB]
    M_U, M_V, M_W = build_iso_from_ABC(A, B, C)
    return M_U, M_V, M_W, (A, B, C)


def apply_action(U, V, W, M_U, M_V, M_W):
    """Apply a precomputed isotropy action to a decomposition."""
    return (
        (M_U.astype(np.int64) @ U.astype(np.int64) % P).astype(np.int8),
        (M_V.astype(np.int64) @ V.astype(np.int64) % P).astype(np.int8),
        (M_W.astype(np.int64) @ W.astype(np.int64) % P).astype(np.int8),
    )


# -----------------------------------------------------------------------------
# Sub-orbit "best-bytes" within column-permutation + scaling — used for
# stabilizer estimation and a coarse normalized fingerprint within a sample.
# This is NOT a canonical orbit key (we'd need to enumerate full Iso for that);
# it's a normalized form within the small per-column gauge.
# -----------------------------------------------------------------------------

def normalize_and_key(U, V, W) -> bytes:
    """Drop zero columns, normalize per-column scaling, sort columns, hash.
    Two decompositions related by S_r and per-column F_3* scaling will produce
    equal keys; decompositions related by Iso (basis change) will generally NOT."""
    nz = ~((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    if not nz.any():
        return b""
    U = U[:, nz]; V = V[:, nz]; W = W[:, nz]
    U, V, W = normalize_all_columns(U, V, W)
    U, V, W = sort_columns(U, V, W)
    return decomp_to_bytes(U, V, W)


# Pre-build a sample of isotropy actions for repeated use (stabilizer sampling
# in descriptors.py, gauge tests, etc.). We sample with a fixed RNG seed for
# reproducibility.
def build_iso_sample(n_samples: int = 1000, seed: int = 12345):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_samples):
        M_U, M_V, M_W, _ = random_iso_action(rng)
        out.append((M_U, M_V, M_W))
    return out


# Default sample used by descriptors and tests (deterministic).
ISO_SAMPLE = build_iso_sample(n_samples=1000, seed=12345)
ISO_SAMPLE_SIZE = len(ISO_SAMPLE)
