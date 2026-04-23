"""
Core: 2x2 matmul tensor over F_3 and CP decompositions of it.

Key differences from F_2 pilot:
  - Entries in {0, 1, 2} instead of {0, 1}.
  - Arithmetic is mod 3 (not mod 2). All accumulators use addition mod 3.
  - F_3* = {1, 2} has two non-trivial scalings, so per-column scaling
    gauge (lambda, mu) is real (not trivial like F_2). Canonicalization
    must quotient by it.

Row-major vec: vec(X)[2i + j] = X[i, j].
"""
from __future__ import annotations
import numpy as np


P = 3
N = 2
DIM = N * N   # = 4


def matmul_tensor() -> np.ndarray:
    """The 2x2x2 matmul tensor T in F_3^4 x F_3^4 x F_3^4."""
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
        T += np.einsum('p,q,s->pqs', A[:, i].astype(np.int32),
                       B[:, i].astype(np.int32), C[:, i].astype(np.int32))
    return (T % P).astype(np.int8)


MATMUL_T = matmul_tensor()


def is_matmul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    return np.array_equal(reconstruct(A, B, C), MATMUL_T)


# -----------------------------------------------------------------------------
# F_3 per-column canonical scaling
# -----------------------------------------------------------------------------
# Each rank-1 term a_i (x) b_i (x) c_i is invariant under the scaling
#   (a, b, c) -> (lambda*a, mu*b, (lambda*mu)^{-1}*c)
# for lambda, mu in F_3* = {1, 2}. Over F_3, 1^{-1} = 1 and 2^{-1} = 2
# (since 2*2 = 4 = 1 mod 3). So (lambda*mu)^{-1} = lambda*mu as well.
#
# Canonical choice: pick (lambda, mu) so that the FIRST nonzero entry of
# the scaled a-vector is 1, and the FIRST nonzero entry of the scaled
# b-vector is 1. This fully fixes the scaling gauge unless one of
# a or b is all-zero (in which case the column's contribution is 0).

def normalize_column(a: np.ndarray, b: np.ndarray, c: np.ndarray):
    """Return (a', b', c') = scaled column such that first-nonzero
    of each of a' and b' is 1, preserving tensor contribution
    a (x) b (x) c = a' (x) b' (x) c'.

    If a or b is all zero, the contribution is zero — return unchanged.
    """
    a = a.astype(np.int8) % P
    b = b.astype(np.int8) % P
    c = c.astype(np.int8) % P

    # Find scaling lambda for a-side.
    lam = 1
    for i in range(len(a)):
        if a[i] != 0:
            # Choose lam such that lam * a[i] = 1 mod 3.
            # a[i] is 1 or 2. inv(1)=1, inv(2)=2.
            lam = int(a[i])   # since a[i]*a[i] = 1 mod 3 for a[i] in {1, 2}
            break

    # Find scaling mu for b-side.
    mu = 1
    for i in range(len(b)):
        if b[i] != 0:
            mu = int(b[i])
            break

    a_new = (lam * a) % P
    b_new = (mu * b) % P
    # c scales by (lam * mu)^{-1} = lam * mu (since 1^{-1}=1, 2^{-1}=2 in F_3).
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
# Serialization / column keys / sort
# -----------------------------------------------------------------------------

# Each entry is in {0, 1, 2}, so 3 values. For hashing we pack a column's
# 3*DIM = 12 trits into a single integer in base 3.
_POW3 = np.array([P**i for i in range(3 * DIM - 1, -1, -1)], dtype=np.int64)


def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    stacked = np.vstack([A, B, C]).astype(np.int64) % P
    return (_POW3 @ stacked).astype(np.int64)


def sort_columns(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    keys = column_keys(A, B, C)
    order = np.argsort(keys, kind='stable')
    return A[:, order], B[:, order], C[:, order]


def decomp_to_bytes(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bytes:
    vals = column_keys(A, B, C)
    return vals.astype('>i8').tobytes()
