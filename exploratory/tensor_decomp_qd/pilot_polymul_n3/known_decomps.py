"""Known decompositions of the polymul tensor over F_2 with n = 3.

  - naive rank-9 (one product per (i, j) pair).
  - rank-6 Karatsuba-style algorithm:
        M1 = p_0 * q_0
        M2 = p_2 * q_2
        M3 = p_1 * q_1
        M4 = (p_0 + p_1)(q_0 + q_1)
        M5 = (p_1 + p_2)(q_1 + q_2)
        M6 = (p_0 + p_2)(q_0 + q_2)

    Output formulas over F_2 (signs collapse):
        r_0 = M1
        r_1 = M1 + M3 + M4
        r_2 = M1 + M2 + M3 + M6
        r_3 = M2 + M3 + M5
        r_4 = M2

    This is a 3-way Karatsuba composition: corner products at the
    diagonal (M1, M2, M3) plus pairwise cross-sums (M4, M5, M6) for
    the three off-diagonal output coefficients. Each M_i may contribute
    to multiple r_k's; the c-column lists those k's. Verified
    bit-for-bit against POLYMUL_T.
"""
from __future__ import annotations
import numpy as np

from .core import POLYMUL_T, is_polymul_decomp, reconstruct, DIM_AB, DIM_C, N


def naive_decomp():
    """Rank-9 trivial decomp: one outer-product per (p_i, q_j) pair, each
    contributing 1 to the output coefficient r_{i+j}.
    """
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
    assert is_polymul_decomp(A, B, C), "naive rank-9 decomp failed validation"
    return A, B, C


def karatsuba6_decomp():
    """Rank-6 Karatsuba-style decomposition of polymul-3 over F_2.

    Products:
      M1 = p0 q0                       a-side e0,    b-side e0
      M2 = p2 q2                       a-side e2,    b-side e2
      M3 = p1 q1                       a-side e1,    b-side e1
      M4 = (p0+p1)(q0+q1)              a-side e0+e1, b-side e0+e1
      M5 = (p1+p2)(q1+q2)              a-side e1+e2, b-side e1+e2
      M6 = (p0+p2)(q0+q2)              a-side e0+e2, b-side e0+e2

    Output formulas over F_2:
      r0 = M1
      r1 = M1 + M3 + M4
      r2 = M1 + M2 + M3 + M6
      r3 = M2 + M3 + M5
      r4 = M2

    Reading off which output positions each product contributes to:
      M1 -> r0, r1, r2
      M2 -> r2, r3, r4
      M3 -> r1, r2, r3
      M4 -> r1
      M5 -> r3
      M6 -> r2
    """
    a_cols = [
        [1, 0, 0],  # M1: p0
        [0, 0, 1],  # M2: p2
        [0, 1, 0],  # M3: p1
        [1, 1, 0],  # M4: p0 + p1
        [0, 1, 1],  # M5: p1 + p2
        [1, 0, 1],  # M6: p0 + p2
    ]
    b_cols = [
        [1, 0, 0],  # M1: q0
        [0, 0, 1],  # M2: q2
        [0, 1, 0],  # M3: q1
        [1, 1, 0],  # M4: q0 + q1
        [0, 1, 1],  # M5: q1 + q2
        [1, 0, 1],  # M6: q0 + q2
    ]
    c_cols = [
        [1, 1, 1, 0, 0],  # M1 -> r0, r1, r2
        [0, 0, 1, 1, 1],  # M2 -> r2, r3, r4
        [0, 1, 1, 1, 0],  # M3 -> r1, r2, r3
        [0, 1, 0, 0, 0],  # M4 -> r1
        [0, 0, 0, 1, 0],  # M5 -> r3
        [0, 0, 1, 0, 0],  # M6 -> r2
    ]
    A = np.array(a_cols, dtype=np.uint8).T
    B = np.array(b_cols, dtype=np.uint8).T
    C = np.array(c_cols, dtype=np.uint8).T
    assert is_polymul_decomp(A, B, C), (
        "Karatsuba rank-6 decomp failed POLYMUL_T validation. "
        "C-side derivation is wrong."
    )
    return A, B, C


def karatsuba_permuted(seed: int = 0):
    """Rank-6 Karatsuba with columns permuted by a fixed seed."""
    A, B, C = karatsuba6_decomp()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(A.shape[1])
    return A[:, perm], B[:, perm], C[:, perm]


def karatsuba_gauge_transformed(seed: int = 0):
    """Rank-6 Karatsuba transformed by a random gauge element.
    Must canonicalize to the same form as karatsuba6_decomp().
    """
    from .gauge import GAUGE_ACTIONS, apply_gauge
    A, B, C = karatsuba6_decomp()
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, len(GAUGE_ACTIONS)))
    return apply_gauge(A, B, C, idx)


def near_miss_karatsuba(bit_flips: int = 1, seed: int = 0):
    """Karatsuba with random bit flips. Should NOT canonicalize to Karatsuba."""
    A, B, C = karatsuba6_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(bit_flips):
        which = int(rng.integers(0, 3))
        mat = (U, V, W)[which]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        mat[i, j] ^= 1
    return U, V, W
