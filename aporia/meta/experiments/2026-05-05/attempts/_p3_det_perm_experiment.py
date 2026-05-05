"""Calibration anchor for harmonia_E_03_det_vs_perm.md.

Computes determinant and permanent of n x n random integer matrices
for small n; reports timing, formula counts, and the empirical
asymptotic gap.

This is NOT an attack on Valiant's conjecture. It is a sanity-anchor
that the algorithmic gap (poly for det, n*2^n via Ryser for perm) is
visible at the scale we can actually compute.

Run: python _p3_det_perm_experiment.py
"""
from __future__ import annotations

import math
import random
import time

import numpy as np


def perm_naive(M):
    """O(n!) over permutations. Correct, slow."""
    n = M.shape[0]
    from itertools import permutations
    total = 0
    for sigma in permutations(range(n)):
        prod = 1
        for i in range(n):
            prod *= M[i, sigma[i]]
        total += prod
    return total


def perm_ryser(M):
    """O(n * 2^n) Ryser's formula:
        perm(M) = (-1)^n * sum_{S subset {0..n-1}} (-1)^|S| * prod_i (sum_{j in S} M_ij)
    Best known asymptotic for exact permanent of an arbitrary matrix.
    """
    n = M.shape[0]
    total = 0
    for mask in range(1 << n):
        # row sums restricted to columns in mask
        cols = [j for j in range(n) if (mask >> j) & 1]
        if not cols:
            continue
        # product over rows of sum of M[i, j] for j in cols
        prod = 1
        for i in range(n):
            s = 0
            for j in cols:
                s += M[i, j]
            prod *= s
        sign = (-1) ** (n - len(cols))
        total += sign * prod
    return total


def det_lu(M):
    """Float-domain LU determinant via numpy. O(n^3). Correct up to fp."""
    return np.linalg.det(M.astype(float))


def det_exact(M):
    """Exact integer determinant via cofactor expansion. O(n!)."""
    n = M.shape[0]
    if n == 1:
        return int(M[0, 0])
    total = 0
    for j in range(n):
        sub = np.delete(np.delete(M, 0, 0), j, 1)
        sign = (-1) ** j
        total += sign * int(M[0, j]) * det_exact(sub)
    return total


def main():
    print("=== det vs perm: small-n calibration anchor ===\n")
    print(f"{'n':>3} {'det_lu':>14s} {'det_exact':>14s} {'perm_naive':>14s} {'perm_ryser':>14s} "
          f"{'t_det':>8s} {'t_perm_n':>10s} {'t_perm_r':>10s} {'mult_det':>10s} {'mult_perm':>14s}")
    print('-' * 130)

    rng = np.random.default_rng(20260505)
    for n in range(1, 8):
        # small-integer matrix so sympy-style exact arithmetic stays cheap
        M = rng.integers(low=-3, high=4, size=(n, n))

        t = time.perf_counter()
        d_lu = det_lu(M)
        t_det = time.perf_counter() - t

        # only run det_exact for small n to avoid factorial explosion
        if n <= 6:
            t = time.perf_counter()
            d_exact = det_exact(M)
            t_det_exact = time.perf_counter() - t
        else:
            d_exact = None
            t_det_exact = None

        if n <= 7:
            t = time.perf_counter()
            p_naive = perm_naive(M)
            t_perm_n = time.perf_counter() - t
        else:
            p_naive = None
            t_perm_n = None

        t = time.perf_counter()
        p_ryser = perm_ryser(M)
        t_perm_r = time.perf_counter() - t

        # Theoretical multiplication counts (rough):
        # - Gaussian elimination on n x n: ~ (2/3) n^3 mults
        # - Naive permanent: n! * n mults
        # - Ryser: 2^n * n mults
        mult_det = (2 / 3) * n ** 3
        mult_perm = math.factorial(n) * n

        d_str = f'{d_lu:.2f}' if d_lu is not None else 'n/a'
        de_str = f'{d_exact}' if d_exact is not None else 'n/a'
        pn_str = f'{p_naive}' if p_naive is not None else 'n/a'
        pr_str = f'{p_ryser}'
        td_str = f'{t_det:.5f}' if t_det is not None else 'n/a'
        tpn_str = f'{t_perm_n:.5f}' if t_perm_n is not None else 'n/a'
        tpr_str = f'{t_perm_r:.5f}'
        print(f'{n:>3d} {d_str:>14s} {de_str:>14s} {pn_str:>14s} {pr_str:>14s} '
              f'{td_str:>8s} {tpn_str:>10s} {tpr_str:>10s} '
              f'{mult_det:>10.1f} {mult_perm:>14.0f}')

    print()
    print("Sanity:")
    print(" - det and perm should differ in sign-pattern only (perm has all '+'; det alternates).")
    print(" - For n=2: det=ad-bc, perm=ad+bc. They agree iff bc=0.")
    print(" - For n=3 with all positive: perm > |det| typically; det can even be 0 with perm > 0.")

    # Specific: 2x2 ad+bc vs ad-bc
    A = np.array([[1, 2], [3, 4]])
    print(f"\n A = {A.tolist()}")
    print(f"   det = 1*4 - 2*3 = -2 (computed: {det_exact(A)})")
    print(f"   perm = 1*4 + 2*3 = 10 (computed: {perm_ryser(A)})")

    print("\n=== Empirical Mignon-Ressayre witness (small n) ===")
    print("Mignon-Ressayre 2004 says dc(perm_n) >= n^2 / 2.")
    print("So to express perm_n as a determinant of a single matrix with ENTRIES")
    print("AFFINE in the inputs, that matrix must be at least n^2/2 x n^2/2.")
    print("This experiment cannot verify the lower bound (it is non-constructive).")
    print("It can only sanity-check that the formulas behave as expected.\n")
    for n in range(1, 6):
        print(f"  n = {n}:  n^2/2 lower bound on dc(perm_n) = {n*n // 2}")
    print()
    print("The Grenet 2014 explicit upper-bound construction expresses perm_n as a")
    print("det of a (2^n - 1) x (2^n - 1) matrix with affine entries — exponential.")
    print("So the gap is between Omega(n^2) lower and 2^n upper bounds; closing")
    print("this gap is part of Valiant's conjecture's open status.")


if __name__ == '__main__':
    main()
