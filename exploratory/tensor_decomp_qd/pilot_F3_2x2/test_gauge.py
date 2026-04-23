"""Canonicalizer unit tests for 2x2 matmul over F_3."""
from __future__ import annotations
import sys
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, DIM, N, P
from .gauge import (
    GLn, ORTHOGONAL_GLn, ISO_ACTIONS, ISO_SIZE, apply_iso,
    canonicalize, stabilizer_order, effective_rank,
)
from .known_decomps import (
    naive_decomp, strassen_decomp, strassen_gauge_transformed,
    near_miss_strassen,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def test_GLn_size():
    print(f"\n[1] |GL_{N}(F_{P})| enumeration")
    _assert(len(GLn) == 48, f"|GL_2(F_3)| = 48 (got {len(GLn)})")


def test_orthogonal_subgroup():
    print(f"\n[2] F_3-orthogonal subgroup")
    _assert(len(ORTHOGONAL_GLn) == 8,
            f"|O_2(F_3)| = 8 (got {len(ORTHOGONAL_GLn)}) — 8 signed permutation matrices")


def test_iso_size():
    print(f"\n[3] matmul isotropy subgroup size")
    _assert(ISO_SIZE == 3072,
            f"|Iso| = 8 * 48 * 8 = 3072 (got {ISO_SIZE})")
    # Sample-preserve check.
    U0, V0, W0 = strassen_decomp()
    rng = np.random.default_rng(0)
    sample = rng.choice(ISO_SIZE, size=50, replace=False)
    bad = 0
    for idx in sample:
        U, V, W = apply_iso(U0, V0, W0, int(idx))
        if not is_matmul_decomp(U, V, W):
            bad += 1
    _assert(bad == 0, f"50 sampled isotropy actions preserve matmul (bad={bad})")


def test_canonicalize_idempotent():
    print("\n[4] canonicalize is idempotent")
    U, V, W = strassen_decomp()
    (Uc, Vc, Wc), b1 = canonicalize(U, V, W)
    (_, _, _), b2 = canonicalize(Uc, Vc, Wc)
    _assert(b1 == b2, "canonicalize(canonicalize(x)) == canonicalize(x)")


def test_orbit_equivalence_collapses():
    print("\n[5] gauge-equivalent decompositions canonicalize to same bytes")
    U0, V0, W0 = strassen_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    mismatches = 0
    rng = np.random.default_rng(0)
    for seed in range(15):
        Up, Vp, Wp = strassen_gauge_transformed(seed)
        # Also apply column-scaling manually: multiply column 0 by lambda, ...
        # (this is part of the gauge we normalize over).
        r = Up.shape[1]
        perm = rng.permutation(r)
        Up = Up[:, perm]; Vp = Vp[:, perm]; Wp = Wp[:, perm]
        # Random F_3* scaling per column (1 or 2 for lambda, mu).
        for k in range(r):
            lam = int(rng.integers(1, 3))
            mu = int(rng.integers(1, 3))
            Up[:, k] = (lam * Up[:, k]) % P
            Vp[:, k] = (mu * Vp[:, k]) % P
            Wp[:, k] = ((lam * mu) * Wp[:, k]) % P    # (lam*mu)^{-1} = lam*mu in F_3
        (_, _, _), bt = canonicalize(Up, Vp, Wp)
        if bt != ref:
            mismatches += 1
    _assert(mismatches == 0,
            "15 random (isotropy + column-perm + F_3 scaling) transforms collapse to Strassen canonical")


def test_near_miss_distinct():
    print("\n[6] near-miss decompositions distinct from Strassen canonical")
    U0, V0, W0 = strassen_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    collisions = 0
    for seed in range(10):
        U, V, W = near_miss_strassen(bit_flips=1, seed=seed)
        (_, _, _), bt = canonicalize(U, V, W)
        if bt == ref:
            collisions += 1
    _assert(collisions == 0,
            f"10 single-entry-perturbation variants distinct from Strassen canonical")


def test_orbit_stabilizer():
    print(f"\n[7] Strassen orbit-stabilizer: orbit * stab = |Iso| = {ISO_SIZE}")
    U, V, W = strassen_decomp()
    stab = stabilizer_order(U, V, W)
    print(f"       stabilizer_order = {stab}, expected orbit = {ISO_SIZE // stab}")
    _assert(ISO_SIZE % stab == 0, f"|Iso| % stab = 0 (Lagrange): {ISO_SIZE} % {stab}")
    _assert(stab >= 1, "stabilizer contains identity")


def test_naive_and_strassen_validate():
    print("\n[8] naive and Strassen both reconstruct MATMUL_T")
    A, B, C = naive_decomp()
    _assert(is_matmul_decomp(A, B, C) and effective_rank(A, B, C) == 8,
            "naive rank-8 validates")
    A, B, C = strassen_decomp()
    _assert(is_matmul_decomp(A, B, C) and effective_rank(A, B, C) == 7,
            "Strassen rank-7 validates")


def run_all():
    print("=" * 72)
    print(f"Canonicalizer unit tests for 2x2 matmul over F_{P}")
    print("=" * 72)
    tests = [
        test_GLn_size,
        test_orthogonal_subgroup,
        test_iso_size,
        test_canonicalize_idempotent,
        test_orbit_equivalence_collapses,
        test_near_miss_distinct,
        test_orbit_stabilizer,
        test_naive_and_strassen_validate,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL CANONICALIZER TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
