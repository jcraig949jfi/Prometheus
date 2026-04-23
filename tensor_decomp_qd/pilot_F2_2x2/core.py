"""
Core: 2x2 matrix-multiplication tensor over F_2 and CP decompositions of it.

Conventions
-----------
Matrices X, Y, Z in M_2(F_2) are vectorized row-major:
    vec(X)[2*i + j] = X[i, j]   for i, j in {0, 1}

The matmul tensor T in F_2^4 x F_2^4 x F_2^4 encodes Z = X @ Y, i.e.
    Z[m, n] = sum_k X[m, k] * Y[k, n] (mod 2)

A rank-r CP decomposition is a triple (A, B, C) of (4, r) binary matrices
with columns (a_i, b_i, c_i) such that
    T = sum_{i=1..r} a_i (x) b_i (x) c_i    (over F_2)
where (x) is the outer product and the sum is mod 2.
"""
from __future__ import annotations
import numpy as np


def matmul_tensor() -> np.ndarray:
    """Construct the 2x2x2 matmul tensor T in F_2^4 x F_2^4 x F_2^4.

    Indexing: a runs over vec(X), b runs over vec(Y), c runs over vec(Z).
    T[a, b, c] = 1 iff the monomial X[vec^-1(a)] * Y[vec^-1(b)] appears in Z[vec^-1(c)].
    """
    T = np.zeros((4, 4, 4), dtype=np.uint8)
    # Z[m,n] = X[m,0]*Y[0,n] + X[m,1]*Y[1,n]
    for m in range(2):
        for n in range(2):
            c = 2 * m + n
            for k in range(2):
                a = 2 * m + k       # X[m, k]
                b = 2 * k + n       # Y[k, n]
                T[a, b, c] ^= 1     # F_2 add
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Reconstruct a tensor from factor matrices over F_2 via outer-product sum.

    A, B, C: (dim, r) uint8 matrices with entries in {0, 1}.
    Returns: (dim, dim, dim) uint8 tensor = sum_i outer(A[:,i], B[:,i], C[:,i]) mod 2.
    """
    assert A.shape == B.shape == C.shape
    r = A.shape[1]
    T = np.zeros((A.shape[0], B.shape[0], C.shape[0]), dtype=np.uint8)
    for i in range(r):
        # outer(a, b, c)[p,q,s] = a[p]*b[q]*c[s]
        T ^= np.einsum('p,q,s->pqs', A[:, i], B[:, i], C[:, i], dtype=np.uint8) & 1
    return T & 1


MATMUL_T = matmul_tensor()


def is_matmul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    """Return True iff (A, B, C) reconstructs the 2x2 matmul tensor over F_2."""
    return np.array_equal(reconstruct(A, B, C), MATMUL_T)


def decomp_to_bytes(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bytes:
    """Serialize a decomposition to bytes for hashing/equality (shape-aware)."""
    r = A.shape[1]
    # pack each column's 12 bits into a short bytestring for lex comparison
    out = bytearray()
    for k in range(r):
        col = np.concatenate([A[:, k], B[:, k], C[:, k]]).astype(np.uint8)
        # 12 bits -> 2 bytes
        b = 0
        for bit in col:
            b = (b << 1) | int(bit)
        out.extend(int(b).to_bytes(2, 'big'))
    return bytes(out)


def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> list[int]:
    """Per-column lex-key (12-bit int) used to sort columns (S_r quotient)."""
    r = A.shape[1]
    keys = []
    for k in range(r):
        v = 0
        for bit in A[:, k]:
            v = (v << 1) | int(bit)
        for bit in B[:, k]:
            v = (v << 1) | int(bit)
        for bit in C[:, k]:
            v = (v << 1) | int(bit)
        keys.append(v)
    return keys


def sort_columns(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    """Return (A', B', C') with columns sorted by lex-key (quotients by S_r)."""
    keys = column_keys(A, B, C)
    order = sorted(range(len(keys)), key=lambda i: keys[i])
    return A[:, order], B[:, order], C[:, order]
