"""
Known decompositions of the 2x2 matmul tensor over F_2.

Used for calibration unit tests: after canonicalization, these should all
(a) validate as correct decompositions, and (b) produce distinct canonical
forms whenever they represent distinct gauge orbits (or identical canonical
forms if they are gauge-equivalent).

Row-major vec convention: vec(X)[2*i + j] = X[i, j] with i, j in {0, 1}.
So column indices of a factor matrix run over {x11, x12, x21, x22}.

Strassen 1969 over F_2
----------------------
Sign flips vanish in F_2, so the seven products are:
  M1 = (x11 + x22)(y11 + y22)   contributes to z11 and z22
  M2 = (x21 + x22) y11           contributes to z21 and z22
  M3 = x11 (y12 + y22)           contributes to z12 and z22
  M4 = x22 (y21 + y11)           contributes to z11 and z21
  M5 = (x11 + x12) y22           contributes to z11 and z12
  M6 = (x21 + x11)(y11 + y12)    contributes to z11 and z22
  M7 = (x12 + x22)(y21 + y22)    contributes to z11 and z22

Over F_2 the c-columns are recomputed by expanding each product and
summing mod 2 to match Z = XY. We verify against MATMUL_T at load time.
"""
from __future__ import annotations
import numpy as np
from .core import MATMUL_T, is_matmul_decomp


def naive_decomp():
    """The trivial rank-8 decomposition: one outer product per summand
    in the matmul sum z_{mn} = sum_k x_{mk} y_{kn}.
    """
    cols_a = []
    cols_b = []
    cols_c = []
    for m in range(2):
        for n in range(2):
            for k in range(2):
                a = np.zeros(4, dtype=np.uint8); a[2 * m + k] = 1
                b = np.zeros(4, dtype=np.uint8); b[2 * k + n] = 1
                c = np.zeros(4, dtype=np.uint8); c[2 * m + n] = 1
                cols_a.append(a); cols_b.append(b); cols_c.append(c)
    A = np.column_stack(cols_a)
    B = np.column_stack(cols_b)
    C = np.column_stack(cols_c)
    assert is_matmul_decomp(A, B, C), "naive rank-8 decomp failed validation"
    return A, B, C


def strassen_decomp():
    """Strassen's rank-7 decomposition of 2x2 matmul over F_2.

    Built by specifying the seven products as (a-side, b-side) then deriving
    the c-side by direct expansion and comparison to the matmul tensor.
    """
    # a-side and b-side of each of the 7 products.
    # index key: 0 = x11, 1 = x12, 2 = x21, 3 = x22 (row-major vec)
    a_defs = [
        [1, 0, 0, 1],   # M1: x11 + x22
        [0, 0, 1, 1],   # M2: x21 + x22
        [1, 0, 0, 0],   # M3: x11
        [0, 0, 0, 1],   # M4: x22
        [1, 1, 0, 0],   # M5: x11 + x12
        [1, 0, 1, 0],   # M6: x21 + x11
        [0, 1, 0, 1],   # M7: x12 + x22
    ]
    b_defs = [
        [1, 0, 0, 1],   # M1: y11 + y22
        [1, 0, 0, 0],   # M2: y11
        [0, 1, 0, 1],   # M3: y12 + y22
        [1, 0, 1, 0],   # M4: y21 + y11  (over F_2 = y21 + y11)
        [0, 0, 0, 1],   # M5: y22
        [1, 1, 0, 0],   # M6: y11 + y12
        [0, 0, 1, 1],   # M7: y21 + y22
    ]
    # Strassen output formulas over F_2 (all signs become +):
    # z11 = M1 + M4 + M7 + M5       -> M1,M4,M5,M7 contribute to c-column with c[0]=1
    # z12 = M3 + M5                 -> M3,M5 contribute to c[1]=1
    # z21 = M2 + M4                 -> M2,M4 contribute to c[2]=1
    # z22 = M1 + M3 + M6 + M2       -> M1,M2,M3,M6 contribute to c[3]=1
    #
    # So each column c_i is the XOR pattern of which output positions M_i contributes to.
    c_defs = [[0, 0, 0, 0] for _ in range(7)]
    # M1 -> z11 and z22
    c_defs[0][0] = 1; c_defs[0][3] = 1
    # M2 -> z21 and z22
    c_defs[1][2] = 1; c_defs[1][3] = 1
    # M3 -> z12 and z22
    c_defs[2][1] = 1; c_defs[2][3] = 1
    # M4 -> z11 and z21
    c_defs[3][0] = 1; c_defs[3][2] = 1
    # M5 -> z11 and z12
    c_defs[4][0] = 1; c_defs[4][1] = 1
    # M6 -> z22
    c_defs[5][3] = 1
    # M7 -> z11
    c_defs[6][0] = 1

    A = np.array(a_defs, dtype=np.uint8).T
    B = np.array(b_defs, dtype=np.uint8).T
    C = np.array(c_defs, dtype=np.uint8).T
    assert is_matmul_decomp(A, B, C), (
        "Strassen rank-7 decomp over F_2 failed validation. "
        "c-column derivation needs fixing."
    )
    return A, B, C


def strassen_permuted(seed: int = 0):
    """Strassen with columns permuted by a fixed seeded permutation.
    Used to test that canonicalization collapses gauge-equivalent forms.
    """
    A, B, C = strassen_decomp()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(A.shape[1])
    return A[:, perm], B[:, perm], C[:, perm]


def _random_GL2(rng) -> np.ndarray:
    """Sample a uniform element of GL_2(F_2) (which has 6 elements)."""
    from .gauge import GL2
    return GL2[rng.integers(0, len(GL2))].copy()


def strassen_gauge_transformed(seed: int = 0):
    """Strassen transformed by a random matmul-isotropy element.
    Must canonicalize to the same form as strassen_decomp().
    """
    from .gauge import apply_iso, ISO_ACTIONS
    A, B, C = strassen_decomp()
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, len(ISO_ACTIONS)))
    U2, V2, W2 = apply_iso(A, B, C, idx)
    return U2, V2, W2


def near_miss_strassen(bit_flips: int = 1, seed: int = 0):
    """Strassen with `bit_flips` random bits flipped. Should NOT canonicalize
    to Strassen's canonical form, and should not reconstruct MATMUL_T.
    """
    A, B, C = strassen_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(bit_flips):
        mat_choice = rng.integers(0, 3)
        mat = (U, V, W)[mat_choice]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        mat[i, j] ^= 1
    return U, V, W
