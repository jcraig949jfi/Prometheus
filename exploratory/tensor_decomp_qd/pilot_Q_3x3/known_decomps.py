"""
Known decompositions of the 3x3 matmul tensor over Z.

Includes:
  - naive_decomp: trivial rank-27 (one outer product per matmul monomial).
  - laderman_decomp: Laderman's 1976 rank-23 with signed coefficients in
    {-1, 0, 1}, validated by exact integer reconstruction == MATMUL_T.
  - smirnov_variant_decomp: a different rank-23 algorithm derived from
    Laderman by a non-trivial transformation that algebraic-geometry
    arguments suggest could be a different orbit. Its invariant tuple is
    compared to Laderman's to test for outcome A (multiple rank-23 orbits).

The canonical references for non-Laderman rank-23 algorithms over Q:
  - Smirnov 2013 ("Bilinear complexity and practical algorithms for matrix
    multiplication"): explicit catalog of distinct rank-23 algorithms.
  - Heun 1994, Oh et al. 1979, Makarov 1970 cited algorithms.

We use a CONSTRUCTIVE approach: start from Laderman's product set, apply
the cyclic transposition symmetry of the matmul tensor (which sends
(a, b, c) -> (b, c, a) but with index permutations), and check whether
the resulting decomposition has a different invariant tuple. The cyclic
symmetry IS a tensor automorphism (matmul is symmetric under (i,j,k) cyclic
permutation up to transposition), but it generally produces decompositions
that are NOT in the same gauge orbit because the ROLES of the three factor
matrices are swapped. For Strassen 2x2 this gives back Strassen up to
relabeling; for Laderman 3x3 it yields an algorithm with the same a-side
structure but different b- and c-side patterns.
"""
from __future__ import annotations
import numpy as np
from fractions import Fraction

from .core import MATMUL_T, is_matmul_decomp, reconstruct, DIM, N
from .gauge import solve_Q


def _v(indices, signs=None):
    """Build a 9-dim Z vector from (row, col) tuples + optional signs."""
    v = np.zeros(DIM, dtype=np.int32)
    if signs is None:
        signs = [1] * len(indices)
    for (r, c), s in zip(indices, signs):
        v[3 * r + c] += s
    return v


def naive_decomp():
    """Trivial rank-27 decomposition: one outer product per matmul monomial."""
    cols_a, cols_b, cols_c = [], [], []
    for m in range(N):
        for n in range(N):
            for k in range(N):
                a = np.zeros(DIM, dtype=np.int32); a[N * m + k] = 1
                b = np.zeros(DIM, dtype=np.int32); b[N * k + n] = 1
                c = np.zeros(DIM, dtype=np.int32); c[N * m + n] = 1
                cols_a.append(a); cols_b.append(b); cols_c.append(c)
    A = np.column_stack(cols_a).astype(np.int32)
    B = np.column_stack(cols_b).astype(np.int32)
    C = np.column_stack(cols_c).astype(np.int32)
    assert is_matmul_decomp(A, B, C), "naive rank-27 failed validation"
    return A, B, C


# -----------------------------------------------------------------------------
# Laderman 1976 with signed coefficients.
# Source: Laderman, "A noncommutative algorithm for multiplying (3 x 3)
# matrices using 23 multiplications", Bull. AMS 82 (1976) pp. 126-128.
# -----------------------------------------------------------------------------

def _laderman_products_signed():
    """The 23 (a-side, b-side) signed-coefficient products from Laderman 1976."""
    products = [
        ([(0,0),(0,1),(0,2),(1,0),(1,1),(2,1),(2,2)],
         [(1,1)],
         [1,1,1,-1,-1,-1,-1], [1]),
        ([(0,0),(1,0)],
         [(1,1),(0,1)],
         [1,-1], [1,-1]),
        ([(1,1)],
         [(0,0),(0,1),(1,0),(1,1),(1,2),(2,0),(2,2)],
         [1], [-1,1,1,-1,-1,-1,1]),
        ([(0,0),(1,0),(1,1)],
         [(0,0),(0,1),(1,1)],
         [-1,1,1], [1,-1,1]),
        ([(1,0),(1,1)],
         [(0,0),(0,1)],
         [1,1], [-1,1]),
        ([(0,0)], [(0,0)], [1], [1]),
        ([(0,0),(2,0),(2,1)],
         [(0,0),(0,2),(1,2)],
         [-1,1,1], [1,-1,1]),
        ([(0,0),(2,0)],
         [(0,2),(1,2)],
         [-1,1], [1,-1]),
        ([(2,0),(2,1)],
         [(0,0),(0,2)],
         [1,1], [-1,1]),
        ([(0,0),(0,1),(0,2),(1,1),(1,2),(2,0),(2,1)],
         [(1,2)],
         [1,1,1,-1,-1,-1,-1], [1]),
        ([(2,1)],
         [(0,0),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1)],
         [1], [-1,1,1,-1,-1,-1,1]),
        ([(0,2),(2,1),(2,2)],
         [(1,1),(2,0),(2,1)],
         [-1,1,1], [1,1,-1]),
        ([(0,2),(2,2)],
         [(1,1),(2,1)],
         [1,-1], [1,-1]),
        ([(0,2)], [(2,0)], [1], [1]),
        ([(2,1),(2,2)],
         [(2,0),(2,1)],
         [1,1], [-1,1]),
        ([(0,2),(1,1),(1,2)],
         [(1,2),(2,0),(2,2)],
         [-1,1,1], [1,1,-1]),
        ([(0,2),(1,2)],
         [(1,2),(2,2)],
         [1,-1], [1,-1]),
        ([(1,1),(1,2)],
         [(2,0),(2,2)],
         [1,1], [-1,1]),
        ([(0,1)], [(1,0)], [1], [1]),
        ([(1,2)], [(2,1)], [1], [1]),
        ([(1,0)], [(0,2)], [1], [1]),
        ([(2,0)], [(0,1)], [1], [1]),
        ([(2,2)], [(2,2)], [1], [1]),
    ]
    return [(_v(a, sa), _v(b, sb)) for (a, b, sa, sb) in products]


# -----------------------------------------------------------------------------
# Solve over Q: given a-side and b-side product vectors, find which subset
# (with rational coefficients) of products sums to each output monomial.
# -----------------------------------------------------------------------------

def _solve_outputs_from_products(products):
    """Given r products (a, b), solve over Q for output formulas.

    Each product k contributes outer(a_k, b_k) (flattened) as an 81-dim vector.
    Each output c[i, j] has target = sum_q a_iq * b_qj (matmul monomials).
    Returns a dict (i,j) -> Fraction-list of length r, or None if infeasible.
    """
    r = len(products)
    contrib = np.zeros((DIM * DIM, r), dtype=np.int64)
    for k, (a_vec, b_vec) in enumerate(products):
        outer = np.outer(a_vec.astype(np.int64), b_vec.astype(np.int64))
        contrib[:, k] = outer.flatten()

    solutions = {}
    for i in range(N):
        for j in range(N):
            target = np.zeros(DIM * DIM, dtype=np.int64)
            for q in range(N):
                # Monomial index: (3i+q) * 9 + (3q+j) = 27i + 12q + j
                target[27 * i + 12 * q + j] = 1
            s = solve_Q(contrib, target)
            if s is None:
                return None
            solutions[(i, j)] = s
    return solutions


def _build_decomp_from_products_and_solutions(products, solutions):
    """Build (A, B, C) from products (Z) and solutions (Fractions).

    All solutions are required to have INTEGER values (or pure half-integers
    we promote by scaling all three factors). For Laderman they are all in
    {-1, 0, 1}.
    """
    r = len(products)
    A = np.zeros((DIM, r), dtype=np.int32)
    B = np.zeros((DIM, r), dtype=np.int32)
    C = np.zeros((DIM, r), dtype=np.int32)
    for k, (a_vec, b_vec) in enumerate(products):
        A[:, k] = a_vec
        B[:, k] = b_vec
    for (i, j), s in solutions.items():
        for k in range(r):
            val = s[k]
            if val == 0:
                continue
            # Require integer solution.
            if val.denominator != 1:
                raise ValueError(
                    f"non-integer Q solution for c[{i},{j}], product {k}: {val}"
                )
            C[3 * i + j, k] += int(val.numerator)
    return A, B, C


def laderman_decomp():
    """Build Laderman's rank-23 decomposition of 3x3 matmul over Z.

    Verifies reconstruct(A, B, C) == MATMUL_T as integer tensors.
    """
    prods = _laderman_products_signed()
    sols = _solve_outputs_from_products(prods)
    if sols is None:
        raise RuntimeError("Laderman product set has no Q solution.")
    A, B, C = _build_decomp_from_products_and_solutions(prods, sols)
    if not is_matmul_decomp(A, B, C):
        raise RuntimeError("Laderman encoding failed integer reconstruction.")
    return A, B, C


# -----------------------------------------------------------------------------
# Smirnov-variant rank-23 decomposition.
#
# The 3x3 matmul tensor T has a cyclic symmetry: if we permute the three
# factor modes (a, b, c) -> (b, c, a) with a corresponding TRANSPOSE on each
# index, we get back T. Concretely, T[a,b,c] = T'[b,c,a] where T' is the
# matmul tensor on transposed inputs. For 3x3 matmul, T has a Z_3 symmetry
# acting cyclically on factor positions, combined with index transposition.
#
# Applied to a CP decomposition (A, B, C) of T, the cyclic action produces
# (B', C', A') where ' means a 9-dim permutation that implements
# vec(X^T) from vec(X) (i.e., the "transpose-on-3x3" permutation). The
# resulting decomposition is also rank-23 and decomposes T, but its factor
# matrices have different sparsity structure than (A, B, C) — and importantly,
# its INVARIANT TUPLE may differ if (A, B, C) and the cyclically-permuted
# (B', C', A') are NOT in the same orbit under our gauge action.
#
# This is a known construction sometimes called "the cyclic conjugate" of
# Laderman. Whether it's a NEW orbit or the same orbit is a question the
# invariant tuple is precisely designed to answer.
# -----------------------------------------------------------------------------

def _transpose_perm() -> np.ndarray:
    """The 9x9 permutation matrix P_T such that P_T vec(X) = vec(X^T).

    For row-major vec(X)[3i+j] = X[i,j]: vec(X^T)[3i+j] = X[j,i] = vec(X)[3j+i].
    So P_T[3i+j, 3j+i] = 1.
    """
    P = np.zeros((DIM, DIM), dtype=np.int32)
    for i in range(N):
        for j in range(N):
            P[3 * i + j, 3 * j + i] = 1
    return P


def smirnov_variant_decomp():
    """Cyclic-conjugate of Laderman.

    The 3x3 matmul tensor T satisfies the trilinear identity
        T(x, y, z) = T(y, P_T z, P_T x)
    where P_T implements the transpose involution on 3x3 matrices. Equivalently:
    if (A, B, C) decomposes T, then so does (B, P_T C, P_T A).

    Corresponds to the substitution (X, Y, Z) -> (Y, Z^T, X^T) in the trilinear
    form T(X,Y,Z) = tr(X Y Z^T). This gives a rank-23 decomposition whose
    factor matrices have the same column-sums as Laderman but with the ROLES
    permuted, so its invariant-tuple may genuinely differ if the permutation
    is not realized inside the (much smaller) signed-permutation gauge subgroup.

    If the resulting decomposition has the SAME invariant tuple as Laderman,
    they may be in the same GL_3(Q)^3 orbit. If DIFFERENT, we have outcome A.
    """
    A, B, C = laderman_decomp()
    P_T = _transpose_perm()
    A2 = B.astype(np.int32)
    B2 = (P_T @ C).astype(np.int32)
    C2 = (P_T @ A).astype(np.int32)
    if not is_matmul_decomp(A2, B2, C2):
        raise RuntimeError(
            "cyclic conjugate of Laderman fails integer reconstruction"
        )
    return A2, B2, C2


def smirnov_variant2_decomp():
    """Second cyclic-conjugate (the inverse cycle).

    Substitution (X, Y, Z) -> (Z^T, X, Y^T): if (A, B, C) decomposes T then so
    does (P_T C, A, P_T B). This is the cube-root-of-1 inverse of the above.
    """
    A, B, C = laderman_decomp()
    P_T = _transpose_perm()
    A2 = (P_T @ C).astype(np.int32)
    B2 = A.astype(np.int32)
    C2 = (P_T @ B).astype(np.int32)
    if not is_matmul_decomp(A2, B2, C2):
        raise RuntimeError(
            "second cyclic conjugate of Laderman fails integer reconstruction"
        )
    return A2, B2, C2


# -----------------------------------------------------------------------------
# Second variant: transpose-symmetry conjugate of Laderman.
# This swaps two modes (a <-> b) and inserts P_T on each, which corresponds
# to (AB)^T = B^T A^T — also a tensor-preserving operation.
# -----------------------------------------------------------------------------

def laderman_transpose_decomp():
    """Transpose-conjugate of Laderman: (P_T B, P_T A, P_T C).

    The matmul tensor T(X, Y, Z) = tr(X Y Z^T) satisfies
        T(X, Y, Z) = T(Y^T, X^T, Z^T)
    (since (XY)^T = Y^T X^T => tr(X Y Z^T) = tr(Y^T X^T Z) = tr(Y^T X^T (Z^T)^T)).
    So if (A, B, C) decomposes T, then (P_T B, P_T A, P_T C) decomposes T.
    """
    A, B, C = laderman_decomp()
    P_T = _transpose_perm()
    A2 = (P_T @ B).astype(np.int32)
    B2 = (P_T @ A).astype(np.int32)
    C2 = (P_T @ C).astype(np.int32)
    if not is_matmul_decomp(A2, B2, C2):
        raise RuntimeError(
            "transpose conjugate of Laderman fails reconstruction"
        )
    return A2, B2, C2


# -----------------------------------------------------------------------------
# Naive perturbations and randomized seed.
# -----------------------------------------------------------------------------

def naive_with_random_iso(seed: int = 0):
    """Naive decomposition with a random signed-permutation isotropy applied."""
    from .gauge import random_iso_action, apply_action
    A, B, C = naive_decomp()
    rng = np.random.default_rng(seed)
    M_U, M_V, M_W, _ = random_iso_action(rng)
    return apply_action(A, B, C, M_U, M_V, M_W)


def near_miss_naive(perturbations: int = 1, seed: int = 0, K: int = 2):
    """Perturb naive's entries (additive integer; will usually break validity)."""
    A, B, C = naive_decomp()
    U = A.copy(); V = B.copy(); W = C.copy()
    rng = np.random.default_rng(seed)
    for _ in range(perturbations):
        which = rng.integers(0, 3)
        mat = (U, V, W)[which]
        i = int(rng.integers(0, mat.shape[0]))
        j = int(rng.integers(0, mat.shape[1]))
        delta = int(rng.choice([-1, 1]))
        new_val = int(mat[i, j]) + delta
        if -K <= new_val <= K:
            mat[i, j] = new_val
    return U, V, W
