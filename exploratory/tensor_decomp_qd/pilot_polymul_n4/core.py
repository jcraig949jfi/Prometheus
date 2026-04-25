"""Core: polynomial-multiplication tensor over F_2 with n = 4 (degree-3 polys).

Conventions
-----------
Polynomials p(x) of degree <= n-1 = 3 are stored as (p_0, p_1, p_2, p_3) over F_2.
The product r(x) = p(x) q(x) has 2n-1 = 7 coefficients,
    r_k = sum_{i + j = k} p_i q_j   (mod 2)

Polymul tensor T in F_2^4 (x) F_2^4 (x) F_2^7 with T[i, j, k] = 1 iff i+j=k.
"""
from __future__ import annotations
import numpy as np


N = 4                  # degree-3 polynomials
DIM_AB = N             # input mode dim = 4
DIM_C = 2 * N - 1      # output mode dim = 7


def polymul_tensor() -> np.ndarray:
    T = np.zeros((DIM_AB, DIM_AB, DIM_C), dtype=np.uint8)
    for i in range(DIM_AB):
        for j in range(DIM_AB):
            T[i, j, i + j] = 1
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
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
    return np.array_equal(reconstruct(A, B, C), POLYMUL_T)


# -----------------------------------------------------------------------------
# Serialization / column keys
# -----------------------------------------------------------------------------

def column_keys(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> list[int]:
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
    keys = column_keys(A, B, C)
    order = sorted(range(len(keys)), key=lambda i: keys[i])
    return A[:, order], B[:, order], C[:, order]


_BIT_WIDTH = DIM_AB + DIM_AB + DIM_C   # 15 bits per column => 2 bytes


def decomp_to_bytes(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bytes:
    keys = column_keys(A, B, C)
    out = bytearray()
    for v in keys:
        out.extend(int(v).to_bytes(2, 'big'))
    return bytes(out)
