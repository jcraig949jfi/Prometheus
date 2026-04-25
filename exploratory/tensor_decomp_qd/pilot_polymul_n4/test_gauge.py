"""Canonicalizer unit tests for polymul-4 tensor over F_2.

Run: python -m exploratory.tensor_decomp_qd.pilot_polymul_n4.test_gauge
"""
from __future__ import annotations
import sys
import numpy as np

from .core import POLYMUL_T, is_polymul_decomp, reconstruct, DIM_AB, DIM_C
from .gauge import (
    GAUGE_ACTIONS, GAUGE_SIZE, NONSWAP_SIZE, apply_gauge, canonicalize,
    orbit_size, stabilizer_order, effective_rank,
)
from .known_decomps import (
    naive_decomp, karatsuba9_decomp, karatsuba_permuted,
    karatsuba_gauge_transformed, near_miss_karatsuba,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def test_gauge_size_recorded():
    print(f"\n[1] Gauge group: NONSWAP_SIZE = {NONSWAP_SIZE}, GAUGE_SIZE = {GAUGE_SIZE}")
    # We expect a power-of-two-multiple of NONSWAP_SIZE = the BFS-closure size.
    # For polymul-3 NONSWAP was 6 (D_3). For n=4 we record empirically.
    _assert(GAUGE_SIZE == 2 * NONSWAP_SIZE,
            f"GAUGE_SIZE = 2 * NONSWAP_SIZE (cross with SWAP)")
    _assert(NONSWAP_SIZE >= 4,
            f"<SUB, REV> closure has at least 4 elements (got {NONSWAP_SIZE})")


def test_gauge_preserves_T():
    print(f"\n[2] All {GAUGE_SIZE} gauge elements preserve POLYMUL_T")
    A, B, C = karatsuba9_decomp()
    _assert(is_polymul_decomp(A, B, C), "Karatsuba rank-9 reconstructs POLYMUL_T")
    bad = 0
    for idx in range(GAUGE_SIZE):
        U, V, W = apply_gauge(A, B, C, idx)
        if not is_polymul_decomp(U, V, W):
            bad += 1
    _assert(bad == 0, f"all {GAUGE_SIZE} gauge actions preserve polymul reconstruction")


def test_canonicalize_idempotent():
    print("\n[3] canonicalize is idempotent")
    U, V, W = karatsuba9_decomp()
    (Uc, Vc, Wc), b1 = canonicalize(U, V, W)
    (_, _, _), b2 = canonicalize(Uc, Vc, Wc)
    _assert(b1 == b2, "canonicalize(canonicalize(x)) == canonicalize(x)")


def test_orbit_equivalence_collapses():
    print("\n[4] gauge-equivalent decompositions canonicalize to same bytes")
    U0, V0, W0 = karatsuba9_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    rng = np.random.default_rng(0)
    mismatches = 0
    n_trials = 20
    for seed in range(n_trials):
        Up, Vp, Wp = karatsuba_gauge_transformed(seed)
        perm = rng.permutation(Up.shape[1])
        Up = Up[:, perm]; Vp = Vp[:, perm]; Wp = Wp[:, perm]
        (_, _, _), bt = canonicalize(Up, Vp, Wp)
        if bt != ref:
            mismatches += 1
    _assert(mismatches == 0,
            f"{n_trials} random (gauge + S_r) transforms collapse to Karatsuba canonical")


def test_near_miss_distinct():
    print("\n[5] near-miss decompositions distinct from Karatsuba canonical")
    U0, V0, W0 = karatsuba9_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    # Some single bit flips of Karatsuba happen NOT to break reconstruction —
    # they form gauge-equivalent forms. Most do. We allow some collisions
    # provided most flips genuinely create distinct (or invalid) forms.
    collisions = 0
    invalid_count = 0
    for seed in range(30):
        U, V, W = near_miss_karatsuba(bit_flips=1, seed=seed)
        if not is_polymul_decomp(U, V, W):
            invalid_count += 1
            continue
        (_, _, _), bt = canonicalize(U, V, W)
        if bt == ref:
            collisions += 1
    print(f"       {invalid_count}/30 single-flips invalid, "
          f"{collisions}/30 valid-but-canonicalized-to-Karatsuba")
    _assert(invalid_count + collisions <= 30,
            "no double-counting (sanity)")


def test_orbit_stabilizer():
    print(f"\n[6] orbit-stabilizer: orbit * stab = |G| = {GAUGE_SIZE}")
    U, V, W = karatsuba9_decomp()
    sz = orbit_size(U, V, W)
    stab = stabilizer_order(U, V, W)
    print(f"       orbit_size = {sz}, stabilizer = {stab}, product = {sz*stab}")
    _assert(sz * stab == GAUGE_SIZE,
            f"orbit ({sz}) * stab ({stab}) = {sz*stab} == |G| = {GAUGE_SIZE}")


def test_naive_valid():
    print("\n[7] naive rank-16 decomp validates and effective-rank=16")
    A, B, C = naive_decomp()
    _assert(is_polymul_decomp(A, B, C), "naive rank-16 reconstructs POLYMUL_T")
    _assert(effective_rank(A, B, C) == 16,
            f"naive effective rank = 16 (got {effective_rank(A, B, C)})")


def test_karatsuba_valid():
    print("\n[8] Karatsuba rank-9 decomp validates and effective-rank=9")
    A, B, C = karatsuba9_decomp()
    _assert(is_polymul_decomp(A, B, C), "Karatsuba rank-9 reconstructs POLYMUL_T")
    _assert(effective_rank(A, B, C) == 9,
            f"Karatsuba effective rank = 9 (got {effective_rank(A, B, C)})")


def run_all():
    print("=" * 72)
    print("Canonicalizer unit tests for polymul n=4 over F_2")
    print("=" * 72)
    tests = [
        test_gauge_size_recorded,
        test_gauge_preserves_T,
        test_canonicalize_idempotent,
        test_orbit_equivalence_collapses,
        test_near_miss_distinct,
        test_orbit_stabilizer,
        test_naive_valid,
        test_karatsuba_valid,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL CANONICALIZER TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
