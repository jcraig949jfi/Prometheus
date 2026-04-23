"""
Core: 3x3 matmul tensor over F_2 and CP decompositions of it.

Conventions mirror pilot_F2_2x2/core.py but generalized: vec is row-major
so vec(X)[3*i + j] = X[i, j] for i, j in {0, 1, 2}.

The matmul tensor T in F_2^9 x F_2^9 x F_2^9 encodes Z = X @ Y over F_2:
    Z[m, n] = sum_k X[m, k] * Y[k, n] (mod 2)

A rank-r decomposition is a triple (A, B, C) of (9, r) binary matrices.
"""
from __future__ import annotations
import numpy as np


N = 3              # matmul size (fixed for this pilot)
DIM = N * N        # = 9


def matmul_tensor() -> np.ndarray:
    """Construct the 3x3x3 matmul tensor T in F_2^9 x F_2^9 x F_2^9."""
    T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    for m in range(N):
        for n in range(N):
            c = N * m + n
            for k in range(N):
                a = N * m + k
                b = N * k + n
                T[a, b, c] ^= 1
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Reconstruct tensor from factor matrices over F_2."""
    assert A.shape == B.shape == C.shape
    assert A.shape[0] == DIM
    r = A.shape[1]
    T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    for i in range(r):
        T ^= np.einsum('p,q,s->pqs', A[:, i], B[:, i], C[:, i], dtype=np.uint8) & 1
    return T & 1


MATMUL_T = matmul_tensor()


def is_matmul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    return np.array_equal(reconstruct(A, B, C), MATMUL_T)


_POW2 = (1 << np.arange(3 * DIM - 1, -1, -1, dtype=np.int64)).astype(np.int64)


def _column_values(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Return an int64 array of per-column lex keys using vectorized bit packing.

    Each column's 3*DIM = 27 bits (for N=3) are packed as a single int64.
    """
    stacked = np.vstack([A, B, C]).astype(np.int64)   # (3*DIM, r)
    return (_POW2 @ stacked).astype(np.int64)          # (r,)


def decomp_to_bytes(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bytes:
    """Serialize a decomposition for hashing / equality (shape-aware)."""
    vals = _column_values(A, B, C)
    # 3*DIM = 27 bits for N=3; pack as 4-byte big-endian.
    return vals.astype('>i8').tobytes()  # 8 bytes per column is plenty


def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    return _column_values(A, B, C)


def sort_columns(A: np.ndarray, B: np.ndarray, C: np.ndarray):
    keys = _column_values(A, B, C)
    order = np.argsort(keys, kind='stable')
    return A[:, order], B[:, order], C[:, order]
