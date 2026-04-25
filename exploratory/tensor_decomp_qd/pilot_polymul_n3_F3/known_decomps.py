"""Known decompositions of polymul tensor over F_3 with n = 3.

  - naive rank-9 (one product per (i, j) pair).
  - Karatsuba-3-way rank-6 (signed Z-form reduced mod 3).

Karatsuba-3-way rank-6 derivation (over Z, then reduced mod 3):

  Products:
    M1 = p_0 q_0
    M2 = p_1 q_1
    M3 = p_2 q_2
    M4 = (p_0 + p_1)(q_0 + q_1)
    M5 = (p_0 + p_2)(q_0 + q_2)
    M6 = (p_1 + p_2)(q_1 + q_2)

  Output:
    r_0 = M1
    r_1 = M4 - M1 - M2
    r_2 = M5 - M1 - M3 + M2
    r_3 = M6 - M2 - M3
    r_4 = M3

  Reduce mod 3 (signs map -1 -> 2). Verified bit-for-bit against POLYMUL_T.

Why rank 6 (not 5) is our best known:
  Over the reals/rationals, polymul-3 has rank 5 via Toom-Cook with 5
  evaluation points (e.g., 0, 1, -1, 2, infinity). Over F_3 the field
  has only 3 elements (so 4 evaluation points including infinity) — not
  enough for Toom-Cook 3-way. Whether rank 5 is achievable over F_3
  by some other (non-evaluation) algorithm is, to my knowledge,
  unsettled. The pilot's hard floor is RANK_MIN_HARD = 5: rank < 5
  is provably impossible by parameter counting (5 outputs need 5
  multiplications), but rank 5 itself, if found, would be a discovery.
"""
from __future__ import annotations
import numpy as np

from .core import POLYMUL_T, is_polymul_decomp, reconstruct, DIM_AB, DIM_C, N, P


def naive_decomp():
    """Rank-9 trivial decomp: one outer-product per (p_i, q_j) pair."""
    cols_a, cols_b, cols_c = [], [], []
    for i in range(N):
        for j in range(N):
            a = np.zeros(DIM_AB, dtype=np.int8); a[i] = 1
            b = np.zeros(DIM_AB, dtype=np.int8); b[j] = 1
            c = np.zeros(DIM_C, dtype=np.int8);  c[i + j] = 1
            cols_a.append(a); cols_b.append(b); cols_c.append(c)
    A = np.column_stack(cols_a)
    B = np.column_stack(cols_b)
    C = np.column_stack(cols_c)
    assert is_polymul_decomp(A, B, C), "naive rank-9 decomp failed validation"
    return A, B, C


def karatsuba6_decomp():
    """Rank-6 Karatsuba-3-way over F_3 (signed Z-form reduced mod 3)."""
    a_cols = [
        [1, 0, 0],   # M1: p_0
        [0, 1, 0],   # M2: p_1
        [0, 0, 1],   # M3: p_2
        [1, 1, 0],   # M4: p_0 + p_1
        [1, 0, 1],   # M5: p_0 + p_2
        [0, 1, 1],   # M6: p_1 + p_2
    ]
    b_cols = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
    ]
    # Output coefficients of each product into each r_k, signed.
    # r_0 = M1
    # r_1 = M4 - M1 - M2
    # r_2 = M5 - M1 + M2 - M3
    # r_3 = M6 - M2 - M3
    # r_4 = M3
    # Column k in C is the (signed) contribution of product k to r_0..r_4.
    c_cols_signed = [
        [1, -1, -1,  0, 0],   # M1
        [0, -1,  1, -1, 0],   # M2
        [0,  0, -1, -1, 1],   # M3
        [0,  1,  0,  0, 0],   # M4
        [0,  0,  1,  0, 0],   # M5
        [0,  0,  0,  1, 0],   # M6
    ]
    A = np.array(a_cols, dtype=np.int8).T
    B = np.array(b_cols, dtype=np.int8).T
    C = (np.array(c_cols_signed, dtype=np.int64).T % P).astype(np.int8)
    assert is_polymul_decomp(A, B, C), (
        "Karatsuba rank-6 over F_3 failed validation"
    )
    return A, B, C


def karatsuba_permuted(seed: int = 0):
    A, B, C = karatsuba6_decomp()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(A.shape[1])
    return A[:, perm], B[:, perm], C[:, perm]


def karatsuba_gauge_transformed(seed: int = 0):
    from .gauge import GAUGE_ACTIONS, apply_gauge
    A, B, C = karatsuba6_decomp()
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, len(GAUGE_ACTIONS)))
    return apply_gauge(A, B, C, idx)


def karatsuba_F3_scaled(seed: int = 0):
    """Apply random per-column F_3* scaling (lambda, mu, (lambda*mu)^{-1}) to
    Karatsuba — must canonicalize back to the same form."""
    A, B, C = karatsuba6_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    r = U.shape[1]
    for k in range(r):
        lam = int(rng.integers(1, P))   # in {1, 2}
        mu = int(rng.integers(1, P))
        U[:, k] = (lam * U[:, k]) % P
        V[:, k] = (mu * V[:, k]) % P
        # (lam*mu)^{-1} mod 3: since {1,2}, 1^{-1}=1 and 2^{-1}=2.
        scale_c = (lam * mu) % P
        W[:, k] = (scale_c * W[:, k]) % P
    return U, V, W


def near_miss_karatsuba(bit_flips: int = 1, seed: int = 0):
    """Karatsuba with random ternary perturbations (entry e -> (e + delta) mod 3
    for delta in {1, 2})."""
    A, B, C = karatsuba6_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(bit_flips):
        which = int(rng.integers(0, 3))
        mat = (U, V, W)[which]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        delta = int(rng.integers(1, P))
        mat[i, j] = (int(mat[i, j]) + delta) % P
    return U, V, W
