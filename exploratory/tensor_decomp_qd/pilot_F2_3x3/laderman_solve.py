"""
Given candidate a-side and b-side supports for 23 products, SOLVE for the
output formulas (which subset of products sums to each z_{ij}) over F_2.

If the product supports are correct, a solution exists (every output
can be written as a linear combination of products). If no solution
exists, the product supports are wrong.

This lets us validate Laderman's *product* definitions independently
of remembering the output formulas correctly.
"""
from __future__ import annotations
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, reconstruct, DIM, N
from .laderman_attempt import laderman_attempt


def solve_outputs_from_products():
    """Given the 23 products from laderman_attempt, solve for output formulas."""
    A, B, _ = laderman_attempt()    # ignore C, we're resolving it
    r = A.shape[1]

    # Each product k contributes the monomial set A_k * B_k (Cartesian product).
    # Monomial index: (p, q, u, v) -> 9*9 index = (3p+q) * 9 + (3u+v), 0-81.
    # But we only care about "a_{pq} * b_{qv}" terms that appear in matmul —
    # i.e., where q == u (middle index of matmul). Non-matmul monomials must
    # cancel to zero across the chosen subset.

    # Product k contribution as 81-dim vector:
    # contrib_k[9*(3p+q) + (3u+v)] = A[3p+q, k] * B[3u+v, k]
    # i.e., outer product of column k of A and column k of B, flattened.
    contrib = np.zeros((81, r), dtype=np.uint8)
    for k in range(r):
        outer = np.outer(A[:, k], B[:, k]) & 1    # (9, 9) uint8
        contrib[:, k] = outer.flatten()

    # For each output c[i, j], target is z_{ij} = sum_q a_{iq} b_{qj}
    # Monomial support: (p=i, q, u=q, v=j) for q in 0..2
    # Monomial index: (3i+q) * 9 + (3q+j) = 27i + 9q + 3q + j = 27i + 12q + j
    # for q in {0, 1, 2}.
    # Also: all OTHER monomials must sum to 0 across chosen subset.
    solutions = {}
    for i in range(N):
        for j in range(N):
            target = np.zeros(81, dtype=np.uint8)
            for q in range(N):
                target[27 * i + 12 * q + j] = 1

            # Solve contrib @ s = target over F_2 using Gaussian elimination.
            s = solve_F2(contrib, target)
            if s is None:
                print(f"  c[{i}][{j}]: NO SOLUTION — product set insufficient")
                return None
            solutions[(i, j)] = s

    return solutions


def solve_F2(A: np.ndarray, b: np.ndarray):
    """Solve A x = b over F_2. Returns x or None if no solution."""
    m, n = A.shape
    aug = np.hstack([A.copy() & 1, b.reshape(-1, 1) & 1])
    row = 0
    pivot_col = [-1] * (n + 1)
    for c in range(n):
        # Find pivot.
        r_pivot = None
        for rr in range(row, m):
            if aug[rr, c] == 1:
                r_pivot = rr
                break
        if r_pivot is None:
            continue
        aug[[row, r_pivot]] = aug[[r_pivot, row]]
        for rr in range(m):
            if rr != row and aug[rr, c] == 1:
                aug[rr] ^= aug[row]
        pivot_col[c] = row
        row += 1
        if row >= m:
            break

    # Check consistency: no row with only last column = 1.
    for rr in range(m):
        if aug[rr, :n].sum() == 0 and aug[rr, n] == 1:
            return None

    # Back-substitute to find a solution (choose free vars = 0).
    x = np.zeros(n, dtype=np.uint8)
    for c in range(n):
        if pivot_col[c] != -1:
            x[c] = aug[pivot_col[c], n]
    return x


def build_laderman_from_solution(solutions):
    """Given solved output formulas, construct (A, B, C)."""
    A, B, _ = laderman_attempt()
    r = A.shape[1]
    C = np.zeros((DIM, r), dtype=np.uint8)
    for (i, j), s in solutions.items():
        for k in range(r):
            if s[k]:
                C[3 * i + j, k] ^= 1
    return A, B, C


if __name__ == "__main__":
    print("Solving for output formulas given candidate Laderman products...")
    solutions = solve_outputs_from_products()
    if solutions is None:
        print("\nPRODUCT SET IS INSUFFICIENT — the 23 candidate products do not span the matmul tensor.")
        print("Either the product definitions are wrong, or rank < 23 decomp requires different products.")
    else:
        print("\nSolutions found for all 9 outputs. Constructing full decomposition...")
        A, B, C = build_laderman_from_solution(solutions)
        if is_matmul_decomp(A, B, C):
            print("VALIDATION: reconstruct(A, B, C) == MATMUL_T")
            from .gauge import effective_rank, stabilizer_order, canonicalize
            print(f"  effective rank = {effective_rank(A, B, C)}")
            stab = stabilizer_order(A, B, C)
            print(f"  stabilizer order = {stab}")
            print(f"  canonicalizing...")
            (_, _, _), bkey = canonicalize(A, B, C)
            print(f"  canonical form bytes[:16]: {bkey[:16].hex()}")

            # Print the output formulas for future reference.
            print("\nSolved output formulas (1-indexed product numbers):")
            for (i, j), s in solutions.items():
                products = [k + 1 for k, v in enumerate(s) if v]
                print(f"  c[{i+1}][{j+1}] = sum of products {products}")
        else:
            print("REGRESSION: solution found but reconstruct != MATMUL_T")
