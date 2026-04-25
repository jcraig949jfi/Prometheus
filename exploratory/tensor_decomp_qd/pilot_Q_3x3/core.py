"""
Core: 3x3 matmul tensor over Q (small-integer-bounded) and CP decompositions.

Design choice: coefficient representation is "small-integer-bounded Q" —
entries take values in {-K, ..., K} with K=2 by default. Rationale:

  * Pure Q via fractions.Fraction is exact but ~100x slower for the inner-loop
    reconstruction and Gaussian elimination calls that dominate run-time.
  * AlphaTensor restricts to {-1, 0, 1}; Laderman/Smirnov use {-1, 0, 1};
    Brent-equation solutions over Z with K=2 cover all known rank-23 matmul
    algorithms in the literature.
  * The QD archive only ever sees decompositions whose validity check is
    "reconstruct(A,B,C) == MATMUL_T as integer tensors" — no modular reduction.
    With K=2 and r<=30, the tensor entries before reduction are bounded by
    30 * 2^3 = 240, well within int32 range, so we never need bigints.

Row-major vec: vec(X)[3i + j] = X[i, j] for i, j in {0, 1, 2}.

The matmul-isotropy is GL_3(Q) x GL_3(Q) x GL_3(Q) (modulo the diagonal
scaling that preserves T) — INFINITE. We can't enumerate it; we sample
from a finite "small explicit subgroup": signed permutation matrices
(48 elements). Invariant-tuple canonicalization handles the rest.
"""
from __future__ import annotations
import numpy as np


N = 3
DIM = N * N           # = 9
K_DEFAULT = 2         # coefficient bound: entries in {-K, ..., K}


def matmul_tensor() -> np.ndarray:
    """The 3x3x3 matmul tensor T over Z (entries 0/1)."""
    T = np.zeros((DIM, DIM, DIM), dtype=np.int32)
    for m in range(N):
        for n in range(N):
            c = N * m + n
            for k in range(N):
                a = N * m + k
                b = N * k + n
                T[a, b, c] += 1
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Reconstruct tensor from factor matrices over Z (no mod reduction)."""
    assert A.shape == B.shape == C.shape
    assert A.shape[0] == DIM
    r = A.shape[1]
    T = np.zeros((DIM, DIM, DIM), dtype=np.int64)
    if r == 0:
        return T.astype(np.int32)
    for i in range(r):
        T += np.einsum('p,q,s->pqs',
                       A[:, i].astype(np.int64),
                       B[:, i].astype(np.int64),
                       C[:, i].astype(np.int64))
    return T.astype(np.int32)


MATMUL_T = matmul_tensor()


def is_matmul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    """Check exact integer equality with MATMUL_T."""
    return np.array_equal(reconstruct(A, B, C), MATMUL_T)


# -----------------------------------------------------------------------------
# Effective rank: drop zero columns (where any of a, b, c is all zero).
# -----------------------------------------------------------------------------

def effective_rank(U: np.ndarray, V: np.ndarray, W: np.ndarray) -> int:
    nz = ~(((U == 0).all(0)) | ((V == 0).all(0)) | ((W == 0).all(0)))
    return int(nz.sum())


def drop_zero_columns(U, V, W):
    nz = ~(((U == 0).all(0)) | ((V == 0).all(0)) | ((W == 0).all(0)))
    return U[:, nz], V[:, nz], W[:, nz]


# -----------------------------------------------------------------------------
# Per-column sign normalization (the small "easy" piece of the Q gauge).
# Each rank-1 term a (x) b (x) c is invariant under
#     (a, b, c) -> (lambda*a, mu*b, (lambda*mu)^{-1}*c).
# Restricting to lambda, mu in {-1, +1}, both choices preserve K-bound.
# We pick signs so that the first nonzero entry of a and b are POSITIVE.
# -----------------------------------------------------------------------------

def normalize_column_sign(a: np.ndarray, b: np.ndarray, c: np.ndarray):
    a = a.astype(np.int32)
    b = b.astype(np.int32)
    c = c.astype(np.int32)

    lam = 1
    for i in range(len(a)):
        if a[i] != 0:
            lam = 1 if a[i] > 0 else -1
            break

    mu = 1
    for i in range(len(b)):
        if b[i] != 0:
            mu = 1 if b[i] > 0 else -1
            break

    a_new = lam * a
    b_new = mu * b
    # (lambda*mu)^{-1} = lambda*mu since both are +/-1.
    c_new = (lam * mu) * c
    return a_new.astype(np.int32), b_new.astype(np.int32), c_new.astype(np.int32)


def normalize_all_columns(U: np.ndarray, V: np.ndarray, W: np.ndarray):
    U = U.astype(np.int32).copy()
    V = V.astype(np.int32).copy()
    W = W.astype(np.int32).copy()
    r = U.shape[1]
    for k in range(r):
        a, b, c = normalize_column_sign(U[:, k], V[:, k], W[:, k])
        U[:, k] = a; V[:, k] = b; W[:, k] = c
    return U, V, W


# -----------------------------------------------------------------------------
# Sort columns by lex key (as int tuple — entries are small ints).
# -----------------------------------------------------------------------------

def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    """Per-column lex key as a tuple of ints (3*DIM = 27 entries)."""
    stacked = np.vstack([A, B, C]).astype(np.int32)
    keys = []
    for j in range(stacked.shape[1]):
        keys.append(tuple(int(x) for x in stacked[:, j]))
    return keys


def sort_columns(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    keys = column_keys(A, B, C)
    order = sorted(range(len(keys)), key=lambda j: keys[j])
    A = A[:, order]; B = B[:, order]; C = C[:, order]
    return A, B, C
