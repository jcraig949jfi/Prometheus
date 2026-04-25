"""Known decompositions of polymul tensor over F_2 with n = 4.

  - naive rank-16 (one product per (i, j) pair).
  - Karatsuba-composed rank-9 (split 4 = 2 + 2; recursively use Karatsuba-2).

Karatsuba-9 derivation
----------------------
Write p(x) = p_lo(x) + x^2 * p_hi(x), where p_lo = p_0 + p_1 x and
p_hi = p_2 + p_3 x. Same for q. Then
    p(x) q(x) = L(x) + x^2 X(x) + x^4 H(x)
where
    L = p_lo q_lo                                    (3 mults)
    H = p_hi q_hi                                    (3 mults)
    M = (p_lo + p_hi) (q_lo + q_hi)
    X = M - L - H = M + L + H over F_2               (no extra mults)

L, H, M each cost 3 multiplications via Karatsuba-2:
    L_a = p_0 q_0
    L_b = p_1 q_1
    L_c = (p_0 + p_1)(q_0 + q_1)
    L_0 = L_a;  L_2 = L_b;  L_1 = L_a + L_b + L_c           (over F_2)
And similarly for H (using p_2, p_3, q_2, q_3) and M (using p_lo + p_hi
sums). Total: 9 multiplications. Output reconstruction (over F_2):

    r_0 = L_a
    r_1 = L_a + L_b + L_c
    r_2 = L_a + L_b + M_a + H_a                       (= L_2 + X_0)
    r_3 = L_a + L_b + L_c + H_a + H_b + H_c
          + M_a + M_b + M_c                           (= X_1)
    r_4 = L_b + M_b + H_a + H_b                       (= X_2 + H_0)
    r_5 = H_a + H_b + H_c
    r_6 = H_b

Each product M_i contributes to multiple r_k as listed in c_cols below.
Verified bit-for-bit against POLYMUL_T.
"""
from __future__ import annotations
import numpy as np

from .core import POLYMUL_T, is_polymul_decomp, reconstruct, DIM_AB, DIM_C, N


def naive_decomp():
    """Rank-16 trivial decomp."""
    cols_a, cols_b, cols_c = [], [], []
    for i in range(N):
        for j in range(N):
            a = np.zeros(DIM_AB, dtype=np.uint8); a[i] = 1
            b = np.zeros(DIM_AB, dtype=np.uint8); b[j] = 1
            c = np.zeros(DIM_C, dtype=np.uint8);  c[i + j] = 1
            cols_a.append(a); cols_b.append(b); cols_c.append(c)
    A = np.column_stack(cols_a)
    B = np.column_stack(cols_b)
    C = np.column_stack(cols_c)
    assert is_polymul_decomp(A, B, C), "naive rank-16 decomp failed validation"
    return A, B, C


def karatsuba9_decomp():
    """Rank-9 Karatsuba-composed decomposition of polymul-4 over F_2.

    Products in order (L_a, L_b, L_c, H_a, H_b, H_c, M_a, M_b, M_c):

      L_a = p_0 q_0
      L_b = p_1 q_1
      L_c = (p_0 + p_1)(q_0 + q_1)
      H_a = p_2 q_2
      H_b = p_3 q_3
      H_c = (p_2 + p_3)(q_2 + q_3)
      M_a = (p_0 + p_2)(q_0 + q_2)
      M_b = (p_1 + p_3)(q_1 + q_3)
      M_c = (p_0 + p_1 + p_2 + p_3)(q_0 + q_1 + q_2 + q_3)

    Output coefficients (r_0..r_6) over F_2:

      r_0 = L_a
      r_1 = L_a + L_b + L_c
      r_2 = L_a + L_b + M_a + H_a
      r_3 = L_a + L_b + L_c + H_a + H_b + H_c + M_a + M_b + M_c
      r_4 = L_b + M_b + H_a + H_b
      r_5 = H_a + H_b + H_c
      r_6 = H_b
    """
    a_cols = [
        [1, 0, 0, 0],   # L_a: p_0
        [0, 1, 0, 0],   # L_b: p_1
        [1, 1, 0, 0],   # L_c: p_0 + p_1
        [0, 0, 1, 0],   # H_a: p_2
        [0, 0, 0, 1],   # H_b: p_3
        [0, 0, 1, 1],   # H_c: p_2 + p_3
        [1, 0, 1, 0],   # M_a: p_0 + p_2
        [0, 1, 0, 1],   # M_b: p_1 + p_3
        [1, 1, 1, 1],   # M_c: p_0 + p_1 + p_2 + p_3
    ]
    b_cols = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 1, 1, 1],
    ]
    # c_cols[i] is a 7-vector telling which r_k each product contributes to.
    c_cols = [
        # Product:    L_a L_b L_c H_a H_b H_c M_a M_b M_c
        # r_0       :  1   0   0   0   0   0   0   0   0
        # r_1       :  1   1   1   0   0   0   0   0   0
        # r_2       :  1   1   0   1   0   0   1   0   0
        # r_3       :  1   1   1   1   1   1   1   1   1
        # r_4       :  0   1   0   1   1   0   0   1   0
        # r_5       :  0   0   0   1   1   1   0   0   0
        # r_6       :  0   0   0   0   1   0   0   0   0
        [1, 1, 1, 1, 0, 0, 0],   # L_a -> r_0, r_1, r_2, r_3
        [0, 1, 1, 1, 1, 0, 0],   # L_b -> r_1, r_2, r_3, r_4
        [0, 1, 0, 1, 0, 0, 0],   # L_c -> r_1, r_3
        [0, 0, 1, 1, 1, 1, 0],   # H_a -> r_2, r_3, r_4, r_5
        [0, 0, 0, 1, 1, 1, 1],   # H_b -> r_3, r_4, r_5, r_6
        [0, 0, 0, 1, 0, 1, 0],   # H_c -> r_3, r_5
        [0, 0, 1, 1, 0, 0, 0],   # M_a -> r_2, r_3
        [0, 0, 0, 1, 1, 0, 0],   # M_b -> r_3, r_4
        [0, 0, 0, 1, 0, 0, 0],   # M_c -> r_3
    ]
    A = np.array(a_cols, dtype=np.uint8).T
    B = np.array(b_cols, dtype=np.uint8).T
    C = np.array(c_cols, dtype=np.uint8).T
    assert is_polymul_decomp(A, B, C), (
        "Karatsuba rank-9 decomp failed POLYMUL_T validation. "
        "C-side derivation is wrong."
    )
    return A, B, C


def karatsuba_permuted(seed: int = 0):
    A, B, C = karatsuba9_decomp()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(A.shape[1])
    return A[:, perm], B[:, perm], C[:, perm]


def karatsuba_gauge_transformed(seed: int = 0):
    from .gauge import GAUGE_ACTIONS, apply_gauge
    A, B, C = karatsuba9_decomp()
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, len(GAUGE_ACTIONS)))
    return apply_gauge(A, B, C, idx)


def near_miss_karatsuba(bit_flips: int = 1, seed: int = 0):
    A, B, C = karatsuba9_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(bit_flips):
        which = int(rng.integers(0, 3))
        mat = (U, V, W)[which]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        mat[i, j] ^= 1
    return U, V, W
