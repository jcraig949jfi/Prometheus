"""
Attempt to encode Laderman's 1976 rank-23 decomposition of 3x3 matmul.

Since this is memory-reconstructed (not sourced from a verified file),
we VALIDATE by reconstruction. If reconstruct(A, B, C) != MATMUL_T,
the encoding is wrong and the seed is rejected.

Over F_2, all sign distinctions collapse: (+) and (-) both become "include
this term as an XOR contribution." So we only need to get the *supports*
of each product's a-side, b-side, and output c-side right.

Entry indexing: a[i, j] with i, j in {0, 1, 2}. Row-major vec:
    vec(X)[3*i + j] = X[i, j]
so the entry name "a11" (1-indexed) is vec-index 0, "a12" is 1, ..., "a33" is 8.
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, reconstruct, DIM, N


def _v(indices):
    """Build a 9-dim 0/1 vector from a list of (i, j) with i, j in {0,1,2}."""
    v = np.zeros(DIM, dtype=np.uint8)
    for (i, j) in indices:
        v[3 * i + j] = 1
    return v


def laderman_attempt():
    """Encode candidate Laderman decomposition over F_2.

    Source: memory-reconstructed from multiple references; WILL BE VALIDATED
    before use. If reconstruct != MATMUL_T, this function raises.

    Returns (A, B, C) of shape (9, 23).
    """
    # Each product m_k has an "a-side" vector and "b-side" vector.
    # Over F_2, sign information is absorbed (all "-" become "+").
    # 1-indexed labels (a_ij) are translated to 0-indexed positions (i-1, j-1).

    # (a-side supports, b-side supports) for 23 products.
    # Each entry is a list of (row, col) tuples, 0-indexed.
    products = [
        # m1: a-side = a11+a12+a13+a21+a22+a32+a33, b-side = b22
        ([(0,0),(0,1),(0,2),(1,0),(1,1),(2,1),(2,2)], [(1,1)]),
        # m2: (a11 + a21) * (b22 + b12)
        ([(0,0),(1,0)], [(1,1),(0,1)]),
        # m3: a22 * (b11 + b12 + b21 + b22 + b23 + b31 + b33)   [F_2 absorbs signs]
        ([(1,1)], [(0,0),(0,1),(1,0),(1,1),(1,2),(2,0),(2,2)]),
        # m4: (a11 + a21 + a22) * (b11 + b12 + b22)
        ([(0,0),(1,0),(1,1)], [(0,0),(0,1),(1,1)]),
        # m5: (a21 + a22) * (b11 + b12)
        ([(1,0),(1,1)], [(0,0),(0,1)]),
        # m6: a11 * b11
        ([(0,0)], [(0,0)]),
        # m7: (a11 + a31 + a32) * (b11 + b13 + b23)
        ([(0,0),(2,0),(2,1)], [(0,0),(0,2),(1,2)]),
        # m8: (a11 + a31) * (b13 + b23)
        ([(0,0),(2,0)], [(0,2),(1,2)]),
        # m9: (a31 + a32) * (b11 + b13)
        ([(2,0),(2,1)], [(0,0),(0,2)]),
        # m10: (a11 + a12 + a13 + a22 + a23 + a31 + a32) * b23
        ([(0,0),(0,1),(0,2),(1,1),(1,2),(2,0),(2,1)], [(1,2)]),
        # m11: a32 * (b11 + b13 + b21 + b22 + b23 + b31 + b32)
        ([(2,1)], [(0,0),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1)]),
        # m12: (a13 + a32 + a33) * (b22 + b31 + b32)
        ([(0,2),(2,1),(2,2)], [(1,1),(2,0),(2,1)]),
        # m13: (a13 + a33) * (b22 + b32)
        ([(0,2),(2,2)], [(1,1),(2,1)]),
        # m14: a13 * b31
        ([(0,2)], [(2,0)]),
        # m15: (a32 + a33) * (b31 + b32)
        ([(2,1),(2,2)], [(2,0),(2,1)]),
        # m16: (a13 + a22 + a23) * (b23 + b31 + b33)
        ([(0,2),(1,1),(1,2)], [(1,2),(2,0),(2,2)]),
        # m17: (a13 + a23) * (b23 + b33)
        ([(0,2),(1,2)], [(1,2),(2,2)]),
        # m18: (a22 + a23) * (b31 + b33)
        ([(1,1),(1,2)], [(2,0),(2,2)]),
        # m19: a12 * b21
        ([(0,1)], [(1,0)]),
        # m20: a23 * b32
        ([(1,2)], [(2,1)]),
        # m21: a21 * b13
        ([(1,0)], [(0,2)]),
        # m22: a31 * b12
        ([(2,0)], [(0,1)]),
        # m23: a33 * b33
        ([(2,2)], [(2,2)]),
    ]

    # Output formulas — which products contribute to each c_{ij}.
    # c[i][j] gets a "1" at c-vector position 3*i+j for each product in the list.
    # (1-indexed labels -> 0-indexed positions.)
    output_formulas = {
        (0, 0): [6, 14, 19],
        (0, 1): [1, 4, 5, 6, 12, 14, 15],
        (0, 2): [6, 7, 9, 10, 12, 14, 16, 18],
        (1, 0): [2, 3, 4, 6, 16, 17, 18],
        (1, 1): [2, 4, 5, 6, 14, 16, 17, 18],
        (1, 2): [14, 16, 17, 18, 21],
        (2, 0): [6, 7, 8, 11, 12, 13, 14],
        (2, 1): [12, 13, 14, 15, 19],
        (2, 2): [6, 7, 8, 9, 14, 23],
    }

    r = 23
    A = np.zeros((DIM, r), dtype=np.uint8)
    B = np.zeros((DIM, r), dtype=np.uint8)
    C = np.zeros((DIM, r), dtype=np.uint8)

    for k, (a_supp, b_supp) in enumerate(products):
        A[:, k] = _v(a_supp)
        B[:, k] = _v(b_supp)

    # Fill C: product k contributes to c[i][j] iff (k+1) is in output_formulas[(i,j)]
    # (product indexing is 1-based in the formulas dict, but we use 0-based in arrays).
    for (i, j), prod_list in output_formulas.items():
        for pk_one_indexed in prod_list:
            pk = pk_one_indexed - 1
            if 0 <= pk < r:
                C[3 * i + j, pk] ^= 1

    return A, B, C


def test_laderman():
    """Validate the Laderman encoding reconstructs MATMUL_T."""
    A, B, C = laderman_attempt()
    recon = reconstruct(A, B, C)
    ok = np.array_equal(recon, MATMUL_T)
    if ok:
        print("Laderman encoding VALIDATES: reconstruct(A, B, C) == MATMUL_T")
        from .gauge import effective_rank
        print(f"  effective rank = {effective_rank(A, B, C)}")
        return A, B, C
    else:
        # Diagnostic: where does it differ?
        diff = (recon != MATMUL_T).astype(np.int32)
        n_diff = int(diff.sum())
        print(f"Laderman encoding INVALID: {n_diff} tensor entries differ from MATMUL_T")
        print(f"  (encoding is memory-reconstructed; aborting use of this seed)")
        return None


if __name__ == "__main__":
    test_laderman()
