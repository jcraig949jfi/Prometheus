"""Core: polynomial-multiplication tensor over F_3 with n = 3.

Polynomials p(x) of degree <= 2 are stored as (p_0, p_1, p_2) with
p_i in F_3 = {0, 1, 2}. Product r(x) = p(x) q(x) has 5 coefficients,
    r_k = sum_{i + j = k} p_i q_j   (mod 3)

Polymul tensor T in F_3^3 (x) F_3^3 (x) F_3^5 with T[i, j, k] = 1
iff i+j=k.

Per-column F_3* scaling gauge
-----------------------------
Each rank-1 term a_i (x) b_i (x) c_i is invariant under
    (a, b, c) -> (lambda a, mu b, (lambda mu)^{-1} c)
for lambda, mu in F_3* = {1, 2}. Over F_3, 1^{-1} = 1 and 2^{-1} = 2,
so (lambda mu)^{-1} = lambda mu. Canonical choice: scale so first nonzero
of a is 1 and first nonzero of b is 1.
"""
from __future__ import annotations
import numpy as np


P = 3
N = 3
DIM_AB = N             # 3
DIM_C = 2 * N - 1      # 5


def polymul_tensor() -> np.ndarray:
    T = np.zeros((DIM_AB, DIM_AB, DIM_C), dtype=np.int8)
    for i in range(DIM_AB):
        for j in range(DIM_AB):
            T[i, j, i + j] = 1
    return T


def reconstruct(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    assert A.shape[0] == DIM_AB and B.shape[0] == DIM_AB and C.shape[0] == DIM_C, (
        f"shape mismatch: A {A.shape}, B {B.shape}, C {C.shape}"
    )
    assert A.shape[1] == B.shape[1] == C.shape[1], "rank mismatch"
    r = A.shape[1]
    T = np.zeros((DIM_AB, DIM_AB, DIM_C), dtype=np.int32)
    for i in range(r):
        T += np.einsum('p,q,s->pqs', A[:, i].astype(np.int32),
                       B[:, i].astype(np.int32), C[:, i].astype(np.int32))
    return (T % P).astype(np.int8)


POLYMUL_T = polymul_tensor()


def is_polymul_decomp(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
    return np.array_equal(reconstruct(A, B, C), POLYMUL_T)


# -----------------------------------------------------------------------------
# F_3 per-column scaling normalization
# -----------------------------------------------------------------------------

def normalize_column(a: np.ndarray, b: np.ndarray, c: np.ndarray):
    """Return (a', b', c') with first-nonzero of a' = 1 and first-nonzero
    of b' = 1, preserving a (x) b (x) c.
    """
    a = a.astype(np.int8) % P
    b = b.astype(np.int8) % P
    c = c.astype(np.int8) % P

    lam = 1
    for i in range(len(a)):
        if a[i] != 0:
            # In F_3, 1^{-1} = 1, 2^{-1} = 2. Choose lam so lam * a[i] = 1.
            lam = int(a[i])  # since a[i]^2 = 1 mod 3 for a[i] in {1, 2}
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
# Serialization
# -----------------------------------------------------------------------------
# Each column has DIM_AB + DIM_AB + DIM_C = 11 trits => 11 base-3 digits.
_POW3 = np.array([P**i for i in range(DIM_AB + DIM_AB + DIM_C - 1, -1, -1)],
                 dtype=np.int64)


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
