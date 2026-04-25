"""
Core: 3x3 matmul tensor over F_3 and CP decompositions of it.

Differences from existing pilots:
  - 3x3 matmul -> DIM=9, 27 nonzero tensor entries.
  - F_3 arithmetic (entries in {0, 1, 2}, addition mod 3).
  - Per-column scaling gauge under F_3* = {1, 2} matters (must normalize).

Row-major vec: vec(X)[3i + j] = X[i, j] for i, j in {0, 1, 2}.

The matmul-isotropy under the basis-change parameterization has size
~|O_3(F_3)|^2 * |GL_3(F_3)| = 48^2 * 11232 ~ 2.6e7 — too large for
brute-force orbit enumeration. This pilot uses INVARIANT-TUPLE
canonicalization instead (see descriptors.py).
"""
from __future__ import annotations
import numpy as np


P = 3
N = 3
DIM = N * N   # = 9


def matmul_tensor() -> np.ndarray:
    """The 3x3x3 matmul tensor T in F_3^9 x F_3^9 x F_3^9."""
    T = np.zeros((DIM, DIM, DIM), dtype=np.int8)
    for m in range(N):
        for n in range(N):
            c = N * m + n
            for k in range(N):
                a = N * m + k
                b = N * k + n
                T[a, b, c] = (T[a, b, c] + 1) % P
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Reconstruct tensor from factor matrices over F_3."""
    assert A.shape == B.shape == C.shape
    assert A.shape[0] == DIM
    r = A.shape[1]
    T = np.zeros((DIM, DIM, DIM), dtype=np.int32)
    for i in range(r):
        T += np.einsum('p,q,s->pqs',
                       A[:, i].astype(np.int32),
                       B[:, i].astype(np.int32),
                       C[:, i].astype(np.int32))
    return (T % P).astype(np.int8)


MATMUL_T = matmul_tensor()


def is_matmul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    return np.array_equal(reconstruct(A, B, C), MATMUL_T)


# -----------------------------------------------------------------------------
# F_3 per-column canonical scaling (same idea as pilot_F3_2x2).
# -----------------------------------------------------------------------------
# Each rank-1 term a_i (x) b_i (x) c_i is invariant under
#     (a, b, c) -> (lambda*a, mu*b, (lambda*mu)^{-1}*c),  lambda, mu in F_3*.
# In F_3, F_3* = {1, 2} and 2 is its own inverse, so (lambda*mu)^{-1} = lambda*mu.
# Canonicalization picks (lambda, mu) so that the first nonzero entry of each
# of a' and b' is 1.

def normalize_column(a: np.ndarray, b: np.ndarray, c: np.ndarray):
    a = a.astype(np.int8) % P
    b = b.astype(np.int8) % P
    c = c.astype(np.int8) % P

    lam = 1
    for i in range(len(a)):
        if a[i] != 0:
            lam = int(a[i])   # inv(1)=1, inv(2)=2 in F_3
            break

    mu = 1
    for i in range(len(b)):
        if b[i] != 0:
            mu = int(b[i])
            break

    a_new = (lam * a) % P
    b_new = (mu * b) % P
    scale_c = (lam * mu) % P
    c_new = (scale_c * c) % P
    return a_new.astype(np.int8), b_new.astype(np.int8), c_new.astype(np.int8)


def normalize_all_columns(U: np.ndarray, V: np.ndarray, W: np.ndarray):
    U = U.copy(); V = V.copy(); W = W.copy()
    r = U.shape[1]
    for k in range(r):
        a, b, c = normalize_column(U[:, k], V[:, k], W[:, k])
        U[:, k] = a; V[:, k] = b; W[:, k] = c
    return U, V, W


# -----------------------------------------------------------------------------
# Effective rank: drop zero columns (where any of a, b, c is all zero).
# -----------------------------------------------------------------------------

def effective_rank(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    nz = ~((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    return int(nz.sum())


def drop_zero_columns(U, V, W):
    nz = ~((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    return U[:, nz], V[:, nz], W[:, nz]


# -----------------------------------------------------------------------------
# Serialization (used for sub-orbit deduplication; NOT a canonical orbit key).
# -----------------------------------------------------------------------------

_POW3 = np.array([P**i for i in range(3 * DIM - 1, -1, -1)], dtype=object)


def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Per-column lex key as a Python int (3*DIM = 27 trits)."""
    stacked = np.vstack([A, B, C]).astype(np.int64) % P
    # Use object dtype to avoid overflow; 27 trits = 3^27 < 2^43, fits int64,
    # but we keep object for safety.
    out = np.zeros(stacked.shape[1], dtype=np.int64)
    pw = 1
    for row in range(3 * DIM - 1, -1, -1):
        out += stacked[row] * pw
        pw *= P
    return out


def sort_columns(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    keys = column_keys(A, B, C)
    order = np.argsort(keys, kind='stable')
    return A[:, order], B[:, order], C[:, order]


def decomp_to_bytes(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bytes:
    vals = column_keys(A, B, C)
    return vals.astype('>i8').tobytes()
