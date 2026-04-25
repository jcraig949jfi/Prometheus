"""Core: polynomial-multiplication tensor over F_2 and CP decompositions.

Conventions
-----------
Polynomials p(x) of degree <= n-1 are stored as coefficient vectors
(p_0, p_1, ..., p_{n-1}) with p_i in F_2. Same for q. The product
r(x) = p(x) q(x) has coefficients (r_0, ..., r_{2n-2}) with
    r_k = sum_{i + j = k} p_i q_j     (mod 2)

The polymul tensor T is in F_2^n (x) F_2^n (x) F_2^{2n-1} with
    T[i, j, k] = 1   iff   i + j = k   (else 0)

This is fundamentally less saturated than the matmul tensor: each
output coefficient is a sum of (at most) n monomials in pq, and
the "Cauchy" diagonal structure leaves more room for non-trivial
low-rank decompositions to be locally connected.

A rank-r CP decomposition is a triple (A, B, C) where
  A is (n,  r),  B is (n, r),  C is (2n-1, r)
all with entries in F_2, satisfying
    T = sum_{i=1..r} a_i (x) b_i (x) c_i    (over F_2)
"""
from __future__ import annotations
import numpy as np


N = 3                  # degree-2 polynomials
DIM_AB = N             # input mode dimension
DIM_C = 2 * N - 1      # output mode dimension = 5 for n = 3


def polymul_tensor() -> np.ndarray:
    """Construct the polymul tensor T in F_2^n (x) F_2^n (x) F_2^{2n-1}.

    T[i, j, k] = 1 iff i + j = k.
    """
    T = np.zeros((DIM_AB, DIM_AB, DIM_C), dtype=np.uint8)
    for i in range(DIM_AB):
        for j in range(DIM_AB):
            T[i, j, i + j] = 1
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Reconstruct a tensor from factor matrices over F_2 via outer-product sum.

    A, B: (n, r) uint8.  C: (2n-1, r) uint8.
    Returns: (n, n, 2n-1) uint8 = sum_i outer(A[:,i], B[:,i], C[:,i]) mod 2.
    """
    assert A.shape[0] == DIM_AB and B.shape[0] == DIM_AB and C.shape[0] == DIM_C, (
        f"shape mismatch: A {A.shape}, B {B.shape}, C {C.shape}"
    )
    assert A.shape[1] == B.shape[1] == C.shape[1], "rank mismatch across factors"
    r = A.shape[1]
    T = np.zeros((DIM_AB, DIM_AB, DIM_C), dtype=np.uint8)
    for i in range(r):
        T ^= np.einsum('p,q,s->pqs', A[:, i], B[:, i], C[:, i], dtype=np.uint8) & 1
    return T & 1


POLYMUL_T = polymul_tensor()


def is_polymul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    """Return True iff (A, B, C) reconstructs the polymul tensor over F_2."""
    return np.array_equal(reconstruct(A, B, C), POLYMUL_T)


# -----------------------------------------------------------------------------
# Serialization / column keys
# -----------------------------------------------------------------------------

def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> list[int]:
    """Per-column lex key (integer) used to sort columns (S_r quotient).

    Column k packs (A[:,k], B[:,k], C[:,k]) into a single int with
    A's bits highest-order, then B's, then C's.
    """
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
    """Return (A', B', C') with columns sorted by lex key (S_r quotient)."""
    keys = column_keys(A, B, C)
    order = sorted(range(len(keys)), key=lambda i: keys[i])
    return A[:, order], B[:, order], C[:, order]


_BIT_WIDTH = DIM_AB + DIM_AB + DIM_C   # 11 bits per column


def decomp_to_bytes(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bytes:
    """Serialize a (sorted) decomp to bytes for hashing/equality."""
    keys = column_keys(A, B, C)
    # Each key fits in 11 bits => 2 bytes per column.
    out = bytearray()
    for v in keys:
        out.extend(int(v).to_bytes(2, 'big'))
    return bytes(out)
