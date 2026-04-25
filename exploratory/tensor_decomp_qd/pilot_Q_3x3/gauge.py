"""
Gauge group for 3x3 matmul over Q (small-integer-bounded).

The full matmul-isotropy over Q is GL_3(Q) x GL_3(Q) x GL_3(Q) modulo
the central torus that fixes T — INFINITE. We can't enumerate it.

Two pragmatic moves:
  1. SAMPLE from an explicit finite subgroup that preserves bounded-integer
     coefficients: signed permutation matrices SP_3 = {+/-1 * S_3 generators}.
     |SP_3| = 2^3 * 6 = 48. The induced action on factor matrices is via
     Kronecker products, and signed permutations preserve the integer
     {-K,..,K} bound.

  2. Optionally include a finite set of small-integer GL_3(Z) elements with
     entries in {-1, 0, 1} for richer gauge-invariance testing. These do NOT
     preserve the K-bound but they DO preserve the rank-1 integer structure
     of the decomposition, so the rank-based invariants remain valid under
     them.

The 50-random-action invariance test in test_gauge.py uses signed
permutations (which preserve K-bound and are matmul-isotropy elements).

EXACT RANK OVER Q
-----------------

We compute rank over Q by exact Gaussian elimination using fractions.Fraction.
This is the load-bearing primitive for invariant-tuple computation. Numpy
floating-point rank is unreliable on small-integer matrices with rank-cliff
behavior (a 9x81 integer matrix with true rank 8 may show numerical rank 9).
"""
from __future__ import annotations
import itertools
from fractions import Fraction
import numpy as np

from .core import MATMUL_T, DIM, N


# -----------------------------------------------------------------------------
# Exact rank over Q via fractions.Fraction Gaussian elimination.
# -----------------------------------------------------------------------------

def rank_Q(A: np.ndarray) -> int:
    """Exact rank over Q. A is an integer (or rational) matrix."""
    if A.size == 0:
        return 0
    m, n = A.shape
    # Convert to Fraction. Use int() to coerce numpy ints.
    M = [[Fraction(int(A[i, j])) for j in range(n)] for i in range(m)]
    rank = 0
    col = 0
    row = 0
    while row < m and col < n:
        # Find pivot.
        piv = None
        for r in range(row, m):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            col += 1
            continue
        if piv != row:
            M[row], M[piv] = M[piv], M[row]
        inv = Fraction(1, 1) / M[row][col]
        for c2 in range(col, n):
            M[row][c2] *= inv
        for r in range(m):
            if r != row and M[r][col] != 0:
                factor = M[r][col]
                for c2 in range(col, n):
                    M[r][c2] -= factor * M[row][c2]
        rank += 1
        row += 1
        col += 1
    return rank


def solve_Q(A: np.ndarray, b: np.ndarray):
    """Solve A x = b over Q with integer A, b. Returns x (Fractions list) or None.

    Used by Laderman / Smirnov product-then-solve construction.
    """
    m, n = A.shape
    aug = [[Fraction(int(A[i, j])) for j in range(n)] + [Fraction(int(b[i]))]
           for i in range(m)]
    pivot_col = [-1] * n
    row = 0
    for c in range(n):
        piv = None
        for r in range(row, m):
            if aug[r][c] != 0:
                piv = r; break
        if piv is None:
            continue
        if piv != row:
            aug[row], aug[piv] = aug[piv], aug[row]
        inv = Fraction(1, 1) / aug[row][c]
        for c2 in range(c, n + 1):
            aug[row][c2] *= inv
        for r in range(m):
            if r != row and aug[r][c] != 0:
                factor = aug[r][c]
                for c2 in range(c, n + 1):
                    aug[r][c2] -= factor * aug[row][c2]
        pivot_col[c] = row
        row += 1
        if row >= m:
            break
    # Consistency check.
    for r in range(m):
        if all(aug[r][cc] == 0 for cc in range(n)) and aug[r][n] != 0:
            return None
    # Free vars = 0.
    x = [Fraction(0)] * n
    for c in range(n):
        if pivot_col[c] != -1:
            x[c] = aug[pivot_col[c]][n]
    return x


# -----------------------------------------------------------------------------
# Signed permutation matrices: SP_n = {+/-1 * permutations of S_n}.
# |SP_3| = 48. These are an explicit finite subgroup of GL_3(Z) that
# preserves bounded-integer coefficient sets.
# -----------------------------------------------------------------------------

def enumerate_signed_permutations(n: int = N) -> list[np.ndarray]:
    """All n x n signed permutation matrices (|SP_n| = 2^n * n!)."""
    out = []
    perms = list(itertools.permutations(range(n)))
    for p in perms:
        # Permutation matrix.
        Pmat = np.zeros((n, n), dtype=np.int32)
        for i, pi in enumerate(p):
            Pmat[i, pi] = 1
        for signs in itertools.product([1, -1], repeat=n):
            S = np.diag(signs).astype(np.int32)
            out.append(S @ Pmat)
    return out


SIGNED_PERMS = enumerate_signed_permutations(N)
assert len(SIGNED_PERMS) == 48, f"|SP_3| expected 48, got {len(SIGNED_PERMS)}"


def inv_signed_perm(M: np.ndarray) -> np.ndarray:
    """Inverse of a signed permutation matrix (= its transpose; det = +/-1)."""
    return M.T.astype(np.int32)


# -----------------------------------------------------------------------------
# Action on factor matrices via Kronecker products.
#
# The matmul tensor T_{ab,bc,ac} satisfies, for any A in GL_3(Q):
#   if M_U = A (x) B^{-T}, M_V = B (x) C^{-T}, M_W = A (x) C^{-T}
# then (M_U,M_V,M_W) preserves T.
#
# We restrict (A, B, C) to signed permutations (in particular: A, C orthogonal
# in the +/-I sense, i.e. A^{-T} = A and similarly for C — true for any signed
# permutation matrix since they are orthogonal over Z).
# -----------------------------------------------------------------------------

def _action_on_mode(A: np.ndarray, Binv: np.ndarray) -> np.ndarray:
    """A (x) B^{-T} as integer DIM x DIM matrix."""
    A32 = A.astype(np.int32)
    BinvT = Binv.T.astype(np.int32)
    return np.kron(A32, BinvT).astype(np.int32)


def build_iso_from_ABC(A, B, C):
    """Build (M_U, M_V, M_W) from (A, B, C) signed permutations.

    For signed permutation matrices, A^{-1} = A^T, so this is exact integer
    arithmetic with no fractions.
    """
    Binv = B.T.astype(np.int32)   # signed-perm inverse
    Cinv = C.T.astype(np.int32)
    M_U = _action_on_mode(A, Binv)
    M_V = _action_on_mode(B, Cinv)
    M_W = _action_on_mode(A, Cinv)
    return M_U, M_V, M_W


def random_iso_action(rng: np.random.Generator):
    """Sample uniformly from SP_3 x SP_3 x SP_3 (48^3 = 110,592 total actions).

    All such actions preserve MATMUL_T over Z and preserve integer entries.
    Note the set of actions that PRESERVE the K-bound after multiplication
    is a subset; rank-based invariants don't depend on K-bound.
    """
    iA = int(rng.integers(0, len(SIGNED_PERMS)))
    iB = int(rng.integers(0, len(SIGNED_PERMS)))
    iC = int(rng.integers(0, len(SIGNED_PERMS)))
    A = SIGNED_PERMS[iA]
    B = SIGNED_PERMS[iB]
    C = SIGNED_PERMS[iC]
    M_U, M_V, M_W = build_iso_from_ABC(A, B, C)
    return M_U, M_V, M_W, (A, B, C)


def _preserves_matmul(M_U, M_V, M_W) -> bool:
    """Sanity check: the action preserves MATMUL_T over Z."""
    T = MATMUL_T.astype(np.int64)
    Tp = np.einsum('ia,jb,kc,abc->ijk',
                   M_U.astype(np.int64),
                   M_V.astype(np.int64),
                   M_W.astype(np.int64), T)
    return np.array_equal(Tp.astype(np.int32), MATMUL_T)


def apply_action(U, V, W, M_U, M_V, M_W):
    """Apply isotropy action to a decomposition (integer arithmetic)."""
    return (
        (M_U.astype(np.int32) @ U.astype(np.int32)).astype(np.int32),
        (M_V.astype(np.int32) @ V.astype(np.int32)).astype(np.int32),
        (M_W.astype(np.int32) @ W.astype(np.int32)).astype(np.int32),
    )


# Pre-build a sample of isotropy actions for repeated use.
def build_iso_sample(n_samples: int = 200, seed: int = 12345):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_samples):
        M_U, M_V, M_W, _ = random_iso_action(rng)
        out.append((M_U, M_V, M_W))
    return out


ISO_SAMPLE = build_iso_sample(n_samples=200, seed=12345)
ISO_SAMPLE_SIZE = len(ISO_SAMPLE)
