"""
Known decompositions of the 3x3 matmul tensor over F_2.

Seeded:
- naive rank-27 (trivial)
- Laderman rank-23 (pending — to be sourced and verified in a later pass)
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, DIM, N


def laderman_decomp():
    """Laderman's 1976 rank-23 decomposition of 3x3 matmul over F_2.

    Validated via laderman_solve.py (given product definitions, solved for
    output formulas; reconstruction matches MATMUL_T).
    """
    from .laderman_solve import solve_outputs_from_products, build_laderman_from_solution
    solutions = solve_outputs_from_products()
    if solutions is None:
        raise RuntimeError("Laderman product set no longer decomposes MATMUL_T (regression?)")
    A, B, C = build_laderman_from_solution(solutions)
    assert is_matmul_decomp(A, B, C), "Laderman decomp failed validation"
    return A, B, C


def naive_decomp():
    """The trivial rank-27 decomposition: one outer-product per matmul monomial."""
    cols_a, cols_b, cols_c = [], [], []
    for m in range(N):
        for n in range(N):
            for k in range(N):
                a = np.zeros(DIM, dtype=np.uint8); a[N * m + k] = 1
                b = np.zeros(DIM, dtype=np.uint8); b[N * k + n] = 1
                c = np.zeros(DIM, dtype=np.uint8); c[N * m + n] = 1
                cols_a.append(a); cols_b.append(b); cols_c.append(c)
    A = np.column_stack(cols_a)
    B = np.column_stack(cols_b)
    C = np.column_stack(cols_c)
    assert is_matmul_decomp(A, B, C), "naive rank-27 decomp failed validation"
    return A, B, C


def naive_gauge_transformed(seed: int = 0):
    """Naive decomp with a random matmul-isotropy element applied.
    Must canonicalize to the same form as naive_decomp()."""
    from .gauge import ISO_SIZE, apply_iso
    A, B, C = naive_decomp()
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, ISO_SIZE))
    return apply_iso(A, B, C, idx)


def naive_permuted(seed: int = 0):
    """Naive decomp with columns permuted."""
    A, B, C = naive_decomp()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(A.shape[1])
    return A[:, perm], B[:, perm], C[:, perm]


def near_miss_naive(bit_flips: int = 1, seed: int = 0):
    """Naive decomp with `bit_flips` random bits flipped.
    Should NOT canonicalize to naive's canonical form.
    """
    A, B, C = naive_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(bit_flips):
        mat_choice = rng.integers(0, 3)
        mat = (U, V, W)[mat_choice]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        mat[i, j] ^= 1
    return U, V, W
