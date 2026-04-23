"""
Orbit-correctness unit tests for the canonicalizer.

These MUST pass before running MAP-Elites. Each test is a hard
kill-criterion for the canonicalizer design.

Run: python -m tensor_decomp_qd.pilot_F2_2x2.test_gauge
"""
from __future__ import annotations
import sys
import numpy as np

from .core import MATMUL_T, is_matmul_decomp, reconstruct
from .gauge import (
    GL2, ISO_ACTIONS, ISO_SIZE, apply_iso, canonicalize, orbit_size,
    stabilizer_order, sort_columns,
)
from .known_decomps import (
    naive_decomp, strassen_decomp, strassen_permuted,
    strassen_gauge_transformed, near_miss_strassen,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    else:
        print(f"  ok:   {msg}")


def test_GL2_is_correct():
    print("\n[1] GL_2(F_2) enumeration")
    _assert(len(GL2) == 6, f"|GL_2(F_2)| = 6 (got {len(GL2)})")
    # All 6 are invertible: det = 1 over F_2.
    for g in GL2:
        det = (int(g[0, 0]) * int(g[1, 1]) - int(g[0, 1]) * int(g[1, 0])) & 1
        _assert(det == 1, f"element {g.tolist()} has det=1 mod 2")


def test_iso_preserves_matmul():
    print(f"\n[2] matmul isotropy subgroup ({ISO_SIZE} elements) preserves reconstruction")
    U0, V0, W0 = strassen_decomp()
    _assert(is_matmul_decomp(U0, V0, W0), "Strassen decomp reconstructs matmul tensor")
    _assert(ISO_SIZE > 1, f"matmul isotropy subgroup must be non-trivial (got {ISO_SIZE})")
    bad = 0
    for idx in range(len(ISO_ACTIONS)):
        U, V, W = apply_iso(U0, V0, W0, idx)
        if not is_matmul_decomp(U, V, W):
            bad += 1
    _assert(bad == 0,
            f"all {ISO_SIZE} filtered isotropy transforms preserve matmul reconstruction (bad={bad})")


def test_canonicalize_idempotent():
    print("\n[3] canonicalize is idempotent")
    U, V, W = strassen_decomp()
    (Uc, Vc, Wc), b1 = canonicalize(U, V, W)
    (Uc2, Vc2, Wc2), b2 = canonicalize(Uc, Vc, Wc)
    _assert(b1 == b2, "canonicalize(canonicalize(x)) == canonicalize(x)")


def test_orbit_equivalence_collapses():
    print("\n[4] gauge-equivalent decompositions canonicalize to the same bytes")
    U0, V0, W0 = strassen_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    # Try 20 random gauge transforms + column permutations.
    rng = np.random.default_rng(0)
    mismatches = 0
    for seed in range(20):
        Up, Vp, Wp = strassen_gauge_transformed(seed)
        perm = rng.permutation(Up.shape[1])
        Up = Up[:, perm]; Vp = Vp[:, perm]; Wp = Wp[:, perm]
        (_, _, _), bt = canonicalize(Up, Vp, Wp)
        if bt != ref:
            mismatches += 1
    _assert(mismatches == 0,
            "20 random (isotropy + column-perm) transforms all collapse to Strassen's canonical form")


def test_near_miss_distinct():
    print("\n[5] near-miss decompositions do NOT collapse to Strassen's canonical form")
    U0, V0, W0 = strassen_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    collisions = 0
    for seed in range(10):
        U, V, W = near_miss_strassen(bit_flips=1, seed=seed)
        # Near-miss probably doesn't reconstruct matmul; canonicalize anyway.
        (_, _, _), bt = canonicalize(U, V, W)
        if bt == ref:
            collisions += 1
    _assert(collisions == 0,
            f"10 single-bit-flip variants are distinct from Strassen canonical ({collisions} collisions)")


def test_orbit_size_strassen():
    print(f"\n[6] Strassen orbit size: orbit * stabilizer = |Iso subgroup| = {ISO_SIZE}")
    U, V, W = strassen_decomp()
    sz = orbit_size(U, V, W)
    stab = stabilizer_order(U, V, W)
    print(f"       orbit_size = {sz}, stabilizer_order = {stab}, orbit*stab = {sz*stab}")
    _assert(sz * stab == ISO_SIZE,
            f"orbit-stabilizer theorem: orbit * stabilizer = |Iso| = {ISO_SIZE}")


def test_naive_decomp_valid():
    print("\n[7] naive rank-8 decomposition reconstructs matmul tensor")
    A, B, C = naive_decomp()
    _assert(is_matmul_decomp(A, B, C), "naive rank-8 validates")


def test_strassen_decomp_valid():
    print("\n[8] Strassen rank-7 decomposition reconstructs matmul tensor")
    A, B, C = strassen_decomp()
    _assert(is_matmul_decomp(A, B, C), "Strassen rank-7 validates")
    # And rank is 7, not less.
    from .gauge import effective_rank
    _assert(effective_rank(A, B, C) == 7,
            f"effective rank = 7 (no dead columns) [got {effective_rank(A, B, C)}]")


def run_all():
    print("=" * 72)
    print("Canonicalizer unit tests (must ALL pass before MAP-Elites)")
    print("=" * 72)
    tests = [
        test_GL2_is_correct,
        test_iso_preserves_matmul,
        test_canonicalize_idempotent,
        test_orbit_equivalence_collapses,
        test_near_miss_distinct,
        test_orbit_size_strassen,
        test_naive_decomp_valid,
        test_strassen_decomp_valid,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL CANONICALIZER TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
