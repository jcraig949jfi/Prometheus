"""
Known decompositions of the 2x2 matmul tensor over F_3.

Includes naive rank-8 and Strassen rank-7 (verified via products-then-solve
analogous to the F_2 3x3 pilot's Laderman approach).

Row-major vec: vec(X)[2i + j] = X[i, j] for i, j in {0, 1}.
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, reconstruct, DIM, N, P


def _v(indices, signs=None):
    """Build a 4-dim F_3 vector from (row, col) tuples + optional signs."""
    v = np.zeros(DIM, dtype=np.int8)
    if signs is None:
        signs = [1] * len(indices)
    for (r, c), s in zip(indices, signs):
        v[2 * r + c] = (v[2 * r + c] + s) % P
    return v


def naive_decomp():
    """Trivial rank-8 decomposition: one monomial per column."""
    cols_a, cols_b, cols_c = [], [], []
    for m in range(N):
        for n in range(N):
            for k in range(N):
                a = np.zeros(DIM, dtype=np.int8); a[N * m + k] = 1
                b = np.zeros(DIM, dtype=np.int8); b[N * k + n] = 1
                c = np.zeros(DIM, dtype=np.int8); c[N * m + n] = 1
                cols_a.append(a); cols_b.append(b); cols_c.append(c)
    A = np.column_stack(cols_a)
    B = np.column_stack(cols_b)
    C = np.column_stack(cols_c)
    assert is_matmul_decomp(A, B, C)
    return A, B, C


def _strassen_products():
    """Strassen's 7 products as (a-side, b-side) vectors in F_3.

    Using original signed coefficients (reduced mod 3: -1 -> 2).
      M1 = (a11 + a22) * (b11 + b22)
      M2 = (a21 + a22) * b11
      M3 = a11 * (b12 - b22)                  a-side [a11], b-side [b12, -b22]
      M4 = a22 * (b21 - b11)
      M5 = (a11 + a12) * b22
      M6 = (a21 - a11) * (b11 + b12)
      M7 = (a12 - a22) * (b21 + b22)
    """
    # Use (row, col) 0-indexed entries: a11 -> (0,0), a12 -> (0,1), a21 -> (1,0), a22 -> (1,1)
    # signs 1 or -1 (mod 3: 1 or 2)
    prods = [
        # M1: a11+a22, b11+b22
        (_v([(0,0),(1,1)], [1,1]), _v([(0,0),(1,1)], [1,1])),
        # M2: a21+a22, b11
        (_v([(1,0),(1,1)], [1,1]), _v([(0,0)], [1])),
        # M3: a11, b12-b22
        (_v([(0,0)], [1]),          _v([(0,1),(1,1)], [1,-1])),
        # M4: a22, b21-b11
        (_v([(1,1)], [1]),          _v([(1,0),(0,0)], [1,-1])),
        # M5: a11+a12, b22
        (_v([(0,0),(0,1)], [1,1]), _v([(1,1)], [1])),
        # M6: a21-a11, b11+b12
        (_v([(1,0),(0,0)], [1,-1]), _v([(0,0),(0,1)], [1,1])),
        # M7: a12-a22, b21+b22
        (_v([(0,1),(1,1)], [1,-1]), _v([(1,0),(1,1)], [1,1])),
    ]
    return prods


def _solve_strassen_outputs():
    """Solve for Strassen's output formulas over F_3 given the products."""
    prods = _strassen_products()
    r = len(prods)

    # Each product k contributes a 16-dim (= 4x4 flattened) monomial vector:
    # contrib_k[4a + b] = A[a, k] * B[b, k] for a, b in 0..3.
    contrib = np.zeros((DIM * DIM, r), dtype=np.int8)
    for k, (a_vec, b_vec) in enumerate(prods):
        outer = np.outer(a_vec.astype(np.int64), b_vec.astype(np.int64)) % P
        contrib[:, k] = outer.flatten().astype(np.int8)

    # Target for each output c[i, j] = sum_q a[i, q] * b[q, j].
    # Monomial index: 4*(2i+q) + (2q+j) for q in 0..1.
    solutions = {}
    for i in range(N):
        for j in range(N):
            target = np.zeros(DIM * DIM, dtype=np.int8)
            for q in range(N):
                target[4 * (2 * i + q) + (2 * q + j)] = 1
            s = _solve_Fp(contrib, target, p=P)
            if s is None:
                return None
            solutions[(i, j)] = s
    return solutions


def _solve_Fp(A, b, p=P):
    """Solve A @ x = b mod p. Returns x or None."""
    m, n = A.shape
    aug = np.hstack([A.copy().astype(np.int64) % p,
                     b.reshape(-1, 1).astype(np.int64) % p]) % p
    row = 0
    pivot_col = [-1] * n
    for c in range(n):
        r_pivot = None
        for rr in range(row, m):
            if aug[rr, c] != 0:
                r_pivot = rr; break
        if r_pivot is None:
            continue
        aug[[row, r_pivot]] = aug[[r_pivot, row]]
        inv = pow(int(aug[row, c]), -1, p)
        aug[row] = (aug[row] * inv) % p
        for rr in range(m):
            if rr != row and aug[rr, c] != 0:
                factor = aug[rr, c]
                aug[rr] = (aug[rr] - factor * aug[row]) % p
        pivot_col[c] = row
        row += 1
        if row >= m:
            break
    for rr in range(m):
        if aug[rr, :n].sum() == 0 and aug[rr, n] != 0:
            return None
    x = np.zeros(n, dtype=np.int8)
    for c in range(n):
        if pivot_col[c] != -1:
            x[c] = aug[pivot_col[c], n]
    return x


def strassen_decomp():
    """Strassen rank-7 decomposition of 2x2 matmul over F_3.

    Products encoded from classic Strassen formulas with signed coefficients
    reduced mod 3 (−1 → 2). Output formulas solved analytically via
    Gaussian elimination. Validated against MATMUL_T.
    """
    prods = _strassen_products()
    solutions = _solve_strassen_outputs()
    if solutions is None:
        raise RuntimeError("Strassen products don't span matmul over F_3 (encoding error)")

    r = len(prods)
    A = np.zeros((DIM, r), dtype=np.int8)
    B = np.zeros((DIM, r), dtype=np.int8)
    C = np.zeros((DIM, r), dtype=np.int8)
    for k, (a_vec, b_vec) in enumerate(prods):
        A[:, k] = a_vec
        B[:, k] = b_vec
    for (i, j), s in solutions.items():
        for k in range(r):
            if s[k] != 0:
                C[2 * i + j, k] = (C[2 * i + j, k] + s[k]) % P

    assert is_matmul_decomp(A, B, C), "Strassen over F_3 failed validation"
    return A, B, C


def strassen_gauge_transformed(seed=0):
    from .gauge import ISO_SIZE, apply_iso
    A, B, C = strassen_decomp()
    rng = np.random.default_rng(seed)
    idx = int(rng.integers(0, ISO_SIZE))
    return apply_iso(A, B, C, idx)


def near_miss_strassen(bit_flips=1, seed=0):
    """Flip random entries in Strassen (may not produce valid decomp).
    Over F_3, a "flip" changes entry e to e+1 mod 3 (ternary flip)."""
    A, B, C = strassen_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(bit_flips):
        which = rng.integers(0, 3)
        mat = (U, V, W)[which]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        delta = int(rng.integers(1, P))
        mat[i, j] = (int(mat[i, j]) + delta) % P
    return U, V, W
