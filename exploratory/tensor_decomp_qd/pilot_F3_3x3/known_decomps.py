"""
Known decompositions of the 3x3 matmul tensor over F_3.

Includes:
  - naive_decomp: trivial rank-27 (one outer product per matmul monomial)
  - laderman_decomp: Laderman's rank-23 over F_3, validated via
    products-then-solve (same method as pilot_F2_3x3/laderman_solve.py).

Laderman's coefficients are all in {-1, 0, 1}. Reduced mod 3:
  -1 -> 2,  0 -> 0,  1 -> 1.
This reduction is clean (no division required), so Laderman's products
defined as signed sums work directly over F_3.
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, reconstruct, DIM, N, P


def _v(indices, signs=None):
    """Build a 9-dim F_3 vector from (row, col) tuples + optional signs."""
    v = np.zeros(DIM, dtype=np.int8)
    if signs is None:
        signs = [1] * len(indices)
    for (r, c), s in zip(indices, signs):
        v[3 * r + c] = (v[3 * r + c] + s) % P
    return v


def naive_decomp():
    """Trivial rank-27 decomposition: one outer product per matmul monomial."""
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
    assert is_matmul_decomp(A, B, C), "naive rank-27 failed validation"
    return A, B, C


# -----------------------------------------------------------------------------
# Laderman's 23 products (a-side, b-side) over F_3.
# Sourced from Laderman 1976; signed coefficients reduced mod 3 (-1 -> 2).
# These are the SAME PRODUCT SUPPORTS as in pilot_F2_3x3/laderman_attempt.py
# but with explicit signs that we previously absorbed.
#
# We use the same approach as pilot_F2_3x3: define candidate products,
# then SOLVE for the output formulas via Gaussian elimination over F_3.
# If the products are right, solutions exist; reconstruction validates.
# -----------------------------------------------------------------------------

def _laderman_products_unsigned():
    """The F_2 product supports as-is (ignoring sign info).
    These match pilot_F2_3x3/laderman_attempt.py."""
    products = [
        ([(0,0),(0,1),(0,2),(1,0),(1,1),(2,1),(2,2)], [(1,1)]),
        ([(0,0),(1,0)], [(1,1),(0,1)]),
        ([(1,1)], [(0,0),(0,1),(1,0),(1,1),(1,2),(2,0),(2,2)]),
        ([(0,0),(1,0),(1,1)], [(0,0),(0,1),(1,1)]),
        ([(1,0),(1,1)], [(0,0),(0,1)]),
        ([(0,0)], [(0,0)]),
        ([(0,0),(2,0),(2,1)], [(0,0),(0,2),(1,2)]),
        ([(0,0),(2,0)], [(0,2),(1,2)]),
        ([(2,0),(2,1)], [(0,0),(0,2)]),
        ([(0,0),(0,1),(0,2),(1,1),(1,2),(2,0),(2,1)], [(1,2)]),
        ([(2,1)], [(0,0),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1)]),
        ([(0,2),(2,1),(2,2)], [(1,1),(2,0),(2,1)]),
        ([(0,2),(2,2)], [(1,1),(2,1)]),
        ([(0,2)], [(2,0)]),
        ([(2,1),(2,2)], [(2,0),(2,1)]),
        ([(0,2),(1,1),(1,2)], [(1,2),(2,0),(2,2)]),
        ([(0,2),(1,2)], [(1,2),(2,2)]),
        ([(1,1),(1,2)], [(2,0),(2,2)]),
        ([(0,1)], [(1,0)]),
        ([(1,2)], [(2,1)]),
        ([(1,0)], [(0,2)]),
        ([(2,0)], [(0,1)]),
        ([(2,2)], [(2,2)]),
    ]
    return [(_v(asupp), _v(bsupp)) for asupp, bsupp in products]


def _laderman_products_signed():
    """Laderman's products with signed coefficients (mod 3: -1 -> 2).

    Sources: Laderman 1976 "A noncommutative algorithm for multiplying (3 x 3)
    matrices using 23 multiplications" — signs reproduced from the cited
    formulas in the paper.

    NOTE: the exact sign pattern in published versions of Laderman differs
    across textbooks. We try the unsigned version first (which works over F_2
    and over any field where supports give an integer-coefficient solution);
    if the products-then-solve approach fails over F_3 with unsigned, we'll
    fall back on signed variants.
    """
    # Laderman's original signed products (Bull. AMS 82, 1976).
    # Each entry: (a_supports, b_supports, a_signs, b_signs).
    # 0-indexed entries (i, j) for a_{i+1, j+1} and b_{i+1, j+1}.
    products = [
        # m1 = (a11 + a12 + a13 - a21 - a22 - a32 - a33) * b22
        ([(0,0),(0,1),(0,2),(1,0),(1,1),(2,1),(2,2)],
         [(1,1)],
         [1,1,1,-1,-1,-1,-1], [1]),
        # m2 = (a11 - a21) * (b22 - b12)
        ([(0,0),(1,0)],
         [(1,1),(0,1)],
         [1,-1], [1,-1]),
        # m3 = a22 * (-b11 + b12 + b21 - b22 - b23 - b31 + b33)   [signs uncertain]
        # We attempt the published sign pattern; if it fails, the build catches it.
        ([(1,1)],
         [(0,0),(0,1),(1,0),(1,1),(1,2),(2,0),(2,2)],
         [1], [-1,1,1,-1,-1,-1,1]),
        # m4 = (-a11 + a21 + a22) * (b11 - b12 + b22)
        ([(0,0),(1,0),(1,1)],
         [(0,0),(0,1),(1,1)],
         [-1,1,1], [1,-1,1]),
        # m5 = (a21 + a22) * (-b11 + b12)
        ([(1,0),(1,1)],
         [(0,0),(0,1)],
         [1,1], [-1,1]),
        # m6 = a11 * b11
        ([(0,0)], [(0,0)], [1], [1]),
        # m7 = (-a11 + a31 + a32) * (b11 - b13 + b23)
        ([(0,0),(2,0),(2,1)],
         [(0,0),(0,2),(1,2)],
         [-1,1,1], [1,-1,1]),
        # m8 = (-a11 + a31) * (b13 - b23)
        ([(0,0),(2,0)],
         [(0,2),(1,2)],
         [-1,1], [1,-1]),
        # m9 = (a31 + a32) * (-b11 + b13)
        ([(2,0),(2,1)],
         [(0,0),(0,2)],
         [1,1], [-1,1]),
        # m10 = (a11 + a12 + a13 - a22 - a23 - a31 - a32) * b23
        ([(0,0),(0,1),(0,2),(1,1),(1,2),(2,0),(2,1)],
         [(1,2)],
         [1,1,1,-1,-1,-1,-1], [1]),
        # m11 = a32 * (-b11 + b13 + b21 - b22 - b23 - b31 + b32)
        ([(2,1)],
         [(0,0),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1)],
         [1], [-1,1,1,-1,-1,-1,1]),
        # m12 = (-a13 + a32 + a33) * (b22 + b31 - b32)
        ([(0,2),(2,1),(2,2)],
         [(1,1),(2,0),(2,1)],
         [-1,1,1], [1,1,-1]),
        # m13 = (a13 - a33) * (b22 - b32)
        ([(0,2),(2,2)],
         [(1,1),(2,1)],
         [1,-1], [1,-1]),
        # m14 = a13 * b31
        ([(0,2)], [(2,0)], [1], [1]),
        # m15 = (a32 + a33) * (-b31 + b32)
        ([(2,1),(2,2)],
         [(2,0),(2,1)],
         [1,1], [-1,1]),
        # m16 = (-a13 + a22 + a23) * (b23 + b31 - b33)
        ([(0,2),(1,1),(1,2)],
         [(1,2),(2,0),(2,2)],
         [-1,1,1], [1,1,-1]),
        # m17 = (a13 - a23) * (b23 - b33)
        ([(0,2),(1,2)],
         [(1,2),(2,2)],
         [1,-1], [1,-1]),
        # m18 = (a22 + a23) * (-b31 + b33)
        ([(1,1),(1,2)],
         [(2,0),(2,2)],
         [1,1], [-1,1]),
        # m19 = a12 * b21
        ([(0,1)], [(1,0)], [1], [1]),
        # m20 = a23 * b32
        ([(1,2)], [(2,1)], [1], [1]),
        # m21 = a21 * b13
        ([(1,0)], [(0,2)], [1], [1]),
        # m22 = a31 * b12
        ([(2,0)], [(0,1)], [1], [1]),
        # m23 = a33 * b33
        ([(2,2)], [(2,2)], [1], [1]),
    ]
    return [(_v(a, sa), _v(b, sb)) for (a, b, sa, sb) in products]


# -----------------------------------------------------------------------------
# Solve over F_3: given a-side and b-side product vectors, find which subset
# (with F_3 coefficients) of products sums to each output monomial pattern.
# -----------------------------------------------------------------------------

def _solve_Fp(A, b, p=P):
    """Solve A @ x = b over F_p. Returns x (any solution) or None."""
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


def _solve_outputs_from_products(products):
    """Given r products (a, b), solve for output formulas.

    Each product k contributes outer(a_k, b_k) (flattened) as a 81-dim vector.
    Each output c[i, j] has target = sum_q a_iq * b_qj (the matmul monomials).
    Other monomials must cancel (target = 0 there).
    """
    r = len(products)
    contrib = np.zeros((DIM * DIM, r), dtype=np.int8)
    for k, (a_vec, b_vec) in enumerate(products):
        outer = np.outer(a_vec.astype(np.int64), b_vec.astype(np.int64)) % P
        contrib[:, k] = outer.flatten().astype(np.int8)

    solutions = {}
    for i in range(N):
        for j in range(N):
            target = np.zeros(DIM * DIM, dtype=np.int8)
            for q in range(N):
                # Monomial index: (3i+q) * 9 + (3q+j) = 27i + 12q + j
                target[27 * i + 12 * q + j] = 1
            s = _solve_Fp(contrib, target, p=P)
            if s is None:
                return None
            solutions[(i, j)] = s
    return solutions


def _build_decomp_from_products_and_solutions(products, solutions):
    r = len(products)
    A = np.zeros((DIM, r), dtype=np.int8)
    B = np.zeros((DIM, r), dtype=np.int8)
    C = np.zeros((DIM, r), dtype=np.int8)
    for k, (a_vec, b_vec) in enumerate(products):
        A[:, k] = a_vec
        B[:, k] = b_vec
    for (i, j), s in solutions.items():
        for k in range(r):
            if s[k] != 0:
                C[3 * i + j, k] = (C[3 * i + j, k] + s[k]) % P
    return A, B, C


def laderman_decomp():
    """Build Laderman's rank-23 decomposition of 3x3 matmul over F_3.

    Tries unsigned product supports first (which match the F_2 pilot's
    laderman_attempt and are known to span over F_2). If the products-then-
    solve fails over F_3, falls back to the signed product version.
    """
    # First try: unsigned products (often work because monomial supports
    # carry enough info; signs only matter for cancellations).
    prods = _laderman_products_unsigned()
    sols = _solve_outputs_from_products(prods)
    if sols is not None:
        A, B, C = _build_decomp_from_products_and_solutions(prods, sols)
        if is_matmul_decomp(A, B, C):
            return A, B, C

    # Fallback: signed products.
    prods = _laderman_products_signed()
    sols = _solve_outputs_from_products(prods)
    if sols is not None:
        A, B, C = _build_decomp_from_products_and_solutions(prods, sols)
        if is_matmul_decomp(A, B, C):
            return A, B, C

    raise RuntimeError(
        "Laderman product set does not decompose 3x3 matmul over F_3 — "
        "neither unsigned nor signed variant produced a valid decomp."
    )


def laderman_or_none():
    """Return Laderman decomp or None if encoding fails (for graceful pilot run)."""
    try:
        return laderman_decomp()
    except Exception as e:
        return None


def naive_with_random_iso(seed: int = 0):
    """Naive decomposition with a random matmul-isotropy element applied."""
    from .gauge import random_iso_action, apply_action
    A, B, C = naive_decomp()
    rng = np.random.default_rng(seed)
    M_U, M_V, M_W, _ = random_iso_action(rng)
    return apply_action(A, B, C, M_U, M_V, M_W)


def near_miss_naive(perturbations: int = 1, seed: int = 0):
    """Perturb naive's entries (additive ternary; will usually break validity)."""
    A, B, C = naive_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(perturbations):
        which = rng.integers(0, 3)
        mat = (U, V, W)[which]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        delta = int(rng.integers(1, P))
        mat[i, j] = (int(mat[i, j]) + delta) % P
    return U, V, W
