"""
Canonicalizer unit tests for 3x3 matmul over F_2.

Mirrors pilot_F2_2x2/test_gauge.py. Must all pass before MAP-Elites.
Run: python -m tensor_decomp_qd.pilot_F2_3x3.test_gauge
"""
from __future__ import annotations
import sys
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, reconstruct, DIM, N
from .gauge import (
    GLn, ORTHOGONAL_GLn, ISO_ACTIONS, ISO_SIZE, apply_iso,
    canonicalize, stabilizer_order, effective_rank, sort_columns,
)
from .known_decomps import (
    naive_decomp, naive_permuted, naive_gauge_transformed, near_miss_naive,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def test_GLn_size():
    print(f"\n[1] GL_{N}(F_2) enumeration")
    _assert(len(GLn) == 168, f"|GL_3(F_2)| = 168 (got {len(GLn)})")


def test_orthogonal_subgroup():
    print(f"\n[2] F_2-orthogonal subgroup of GL_{N}(F_2)")
    _assert(len(ORTHOGONAL_GLn) == 6,
            f"|O_3(F_2)| = 6 (the 6 permutation matrices) -> got {len(ORTHOGONAL_GLn)}")
    # Verify each is a permutation matrix.
    all_perm = True
    for g in ORTHOGONAL_GLn:
        row_ok = all(int(g[i].sum()) == 1 for i in range(N))
        col_ok = all(int(g[:, j].sum()) == 1 for j in range(N))
        if not (row_ok and col_ok):
            all_perm = False
    _assert(all_perm, "all orthogonal elements are permutation matrices")


def test_iso_size_and_preservation():
    print(f"\n[3] matmul isotropy subgroup: size and preservation")
    _assert(ISO_SIZE == 6 * 168 * 6,
            f"|Iso| = 6 * 168 * 6 = 6048 (got {ISO_SIZE})")
    U0, V0, W0 = naive_decomp()
    _assert(is_matmul_decomp(U0, V0, W0),
            "naive rank-27 decomp reconstructs matmul tensor")
    # Sample a random subset (full check is expensive).
    rng = np.random.default_rng(0)
    sample = rng.choice(ISO_SIZE, size=100, replace=False)
    bad = 0
    for idx in sample:
        U, V, W = apply_iso(U0, V0, W0, int(idx))
        if not is_matmul_decomp(U, V, W):
            bad += 1
    _assert(bad == 0,
            f"100 sampled isotropy actions preserve matmul (bad={bad})")


def test_canonicalize_idempotent():
    print("\n[4] canonicalize is idempotent")
    U, V, W = naive_decomp()
    (Uc, Vc, Wc), b1 = canonicalize(U, V, W)
    (_, _, _), b2 = canonicalize(Uc, Vc, Wc)
    _assert(b1 == b2, "canonicalize(canonicalize(x)) == canonicalize(x)")


def test_orbit_equivalence_collapses():
    print("\n[5] gauge-equivalent decompositions collapse to same bytes")
    U0, V0, W0 = naive_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    mismatches = 0
    # 10 random gauge transforms + column permutations (canonicalize is slow).
    rng = np.random.default_rng(0)
    for seed in range(10):
        Up, Vp, Wp = naive_gauge_transformed(seed)
        perm = rng.permutation(Up.shape[1])
        Up = Up[:, perm]; Vp = Vp[:, perm]; Wp = Wp[:, perm]
        (_, _, _), bt = canonicalize(Up, Vp, Wp)
        if bt != ref:
            mismatches += 1
    _assert(mismatches == 0,
            "10 random (isotropy + column-perm) transforms collapse to naive canonical form")


def test_near_miss_distinct():
    print("\n[6] near-miss decompositions do NOT collapse to naive canonical")
    U0, V0, W0 = naive_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    collisions = 0
    for seed in range(5):
        U, V, W = near_miss_naive(bit_flips=1, seed=seed)
        (_, _, _), bt = canonicalize(U, V, W)
        if bt == ref:
            collisions += 1
    _assert(collisions == 0,
            f"5 single-bit-flip variants are distinct from naive canonical")


def test_orbit_stabilizer_naive():
    print("\n[7] Naive orbit * stabilizer = |Iso subgroup|")
    U, V, W = naive_decomp()
    stab = stabilizer_order(U, V, W)
    # Orbit size = ISO_SIZE / stabilizer.
    expected_orbit = ISO_SIZE // stab
    print(f"       stabilizer_order = {stab}, expected_orbit_size = {expected_orbit}")
    _assert(ISO_SIZE % stab == 0,
            f"orbit-stabilizer: {ISO_SIZE} % {stab} = 0 (Lagrange divides)")
    _assert(stab >= 1, "stabilizer contains at least the identity")


def test_effective_rank_naive():
    print("\n[8] naive decomp has effective rank 27")
    U, V, W = naive_decomp()
    _assert(effective_rank(U, V, W) == 27,
            f"effective rank = 27 (got {effective_rank(U, V, W)})")


def run_all():
    print("=" * 72)
    print(f"Canonicalizer unit tests for {N}x{N} matmul over F_2")
    print("=" * 72)
    tests = [
        test_GLn_size,
        test_orthogonal_subgroup,
        test_iso_size_and_preservation,
        test_canonicalize_idempotent,
        test_orbit_equivalence_collapses,
        test_near_miss_distinct,
        test_orbit_stabilizer_naive,
        test_effective_rank_naive,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL CANONICALIZER TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
