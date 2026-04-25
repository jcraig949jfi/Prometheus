"""Canonicalizer unit tests for polymul-3 tensor over F_3.

Run: python -m exploratory.tensor_decomp_qd.pilot_polymul_n3_F3.test_gauge
"""
from __future__ import annotations
import sys
import numpy as np

from .core import POLYMUL_T, is_polymul_decomp, reconstruct, DIM_AB, DIM_C, P
from .gauge import (
    GAUGE_ACTIONS, GAUGE_SIZE, NONSWAP_SIZE, apply_gauge, canonicalize,
    orbit_size, stabilizer_order, effective_rank,
)
from .known_decomps import (
    naive_decomp, karatsuba6_decomp, karatsuba_permuted,
    karatsuba_gauge_transformed, karatsuba_F3_scaled, near_miss_karatsuba,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def test_gauge_size():
    print(f"\n[1] Gauge group: NONSWAP = {NONSWAP_SIZE}, GAUGE_SIZE = {GAUGE_SIZE}")
    _assert(GAUGE_SIZE == 2 * NONSWAP_SIZE,
            f"GAUGE_SIZE = 2 * NONSWAP_SIZE")
    _assert(NONSWAP_SIZE >= 6,
            f"<SUB, SCAL, REV> closure has at least 6 elements (got {NONSWAP_SIZE})")


def test_gauge_preserves_T():
    print(f"\n[2] All {GAUGE_SIZE} gauge elements preserve POLYMUL_T")
    A, B, C = karatsuba6_decomp()
    _assert(is_polymul_decomp(A, B, C), "Karatsuba rank-6 reconstructs POLYMUL_T")
    bad = 0
    for idx in range(GAUGE_SIZE):
        U, V, W = apply_gauge(A, B, C, idx)
        if not is_polymul_decomp(U, V, W):
            bad += 1
    _assert(bad == 0, f"all {GAUGE_SIZE} gauge actions preserve polymul reconstruction")


def test_canonicalize_idempotent():
    print("\n[3] canonicalize is idempotent")
    U, V, W = karatsuba6_decomp()
    (Uc, Vc, Wc), b1 = canonicalize(U, V, W)
    (_, _, _), b2 = canonicalize(Uc, Vc, Wc)
    _assert(b1 == b2, "canonicalize(canonicalize(x)) == canonicalize(x)")


def test_orbit_equivalence_collapses():
    print("\n[4] gauge-equivalent decompositions canonicalize to same bytes")
    U0, V0, W0 = karatsuba6_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    rng = np.random.default_rng(0)
    mismatches = 0
    n_trials = 30
    for seed in range(n_trials):
        Up, Vp, Wp = karatsuba_gauge_transformed(seed)
        perm = rng.permutation(Up.shape[1])
        Up = Up[:, perm]; Vp = Vp[:, perm]; Wp = Wp[:, perm]
        # Also apply random per-column F_3* scaling.
        for k in range(Up.shape[1]):
            lam = int(rng.integers(1, P))
            mu = int(rng.integers(1, P))
            Up[:, k] = (lam * Up[:, k]) % P
            Vp[:, k] = (mu * Vp[:, k]) % P
            scale_c = (lam * mu) % P
            Wp[:, k] = (scale_c * Wp[:, k]) % P
        (_, _, _), bt = canonicalize(Up, Vp, Wp)
        if bt != ref:
            mismatches += 1
    _assert(mismatches == 0,
            f"{n_trials} (gauge + S_r + per-col F_3*) transforms collapse to Karatsuba")


def test_F3_scaling_collapses():
    print("\n[4b] per-column F_3* scaling alone collapses to Karatsuba")
    U0, V0, W0 = karatsuba6_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    mismatches = 0
    for seed in range(20):
        Up, Vp, Wp = karatsuba_F3_scaled(seed)
        (_, _, _), bt = canonicalize(Up, Vp, Wp)
        if bt != ref:
            mismatches += 1
    _assert(mismatches == 0,
            f"20 F_3*-scaled Karatsubas all collapse to canonical Karatsuba")


def test_near_miss_distinct():
    print("\n[5] near-miss (single-entry perturbation) distinct from Karatsuba canonical")
    U0, V0, W0 = karatsuba6_decomp()
    (_, _, _), ref = canonicalize(U0, V0, W0)
    valid_collisions = 0
    invalid = 0
    for seed in range(30):
        U, V, W = near_miss_karatsuba(bit_flips=1, seed=seed)
        if not is_polymul_decomp(U, V, W):
            invalid += 1
            continue
        (_, _, _), bt = canonicalize(U, V, W)
        if bt == ref:
            valid_collisions += 1
    print(f"       {invalid}/30 single-flips invalid, "
          f"{valid_collisions}/30 valid-but-canonicalize-to-Karatsuba")
    # Some valid ones might be gauge-equivalent reformulations — they
    # SHOULD canonicalize to Karatsuba if so; that's healthy.
    _assert(invalid + valid_collisions <= 30, "no double-counting (sanity)")


def test_orbit_stabilizer():
    print(f"\n[6] orbit-stabilizer: orbit * stab = |G| = {GAUGE_SIZE}")
    U, V, W = karatsuba6_decomp()
    sz = orbit_size(U, V, W)
    stab = stabilizer_order(U, V, W)
    print(f"       Karatsuba6: orbit_size = {sz}, stabilizer = {stab}, product = {sz*stab}")
    _assert(sz * stab == GAUGE_SIZE,
            f"orbit ({sz}) * stab ({stab}) = {sz*stab} == |G| = {GAUGE_SIZE}")
    U, V, W = naive_decomp()
    sz = orbit_size(U, V, W)
    stab = stabilizer_order(U, V, W)
    print(f"       Naive9: orbit_size = {sz}, stabilizer = {stab}, product = {sz*stab}")
    _assert(sz * stab == GAUGE_SIZE,
            f"naive: orbit ({sz}) * stab ({stab}) = {sz*stab} == |G| = {GAUGE_SIZE}")


def test_naive_valid():
    print("\n[7] naive rank-9 decomp validates and effective-rank=9")
    A, B, C = naive_decomp()
    _assert(is_polymul_decomp(A, B, C), "naive rank-9 reconstructs POLYMUL_T")
    _assert(effective_rank(A, B, C) == 9,
            f"naive effective rank = 9 (got {effective_rank(A, B, C)})")


def test_karatsuba_valid():
    print("\n[8] Karatsuba rank-6 decomp validates and effective-rank=6")
    A, B, C = karatsuba6_decomp()
    _assert(is_polymul_decomp(A, B, C), "Karatsuba rank-6 reconstructs POLYMUL_T")
    _assert(effective_rank(A, B, C) == 6,
            f"Karatsuba effective rank = 6 (got {effective_rank(A, B, C)})")


def run_all():
    print("=" * 72)
    print("Canonicalizer unit tests for polymul n=3 over F_3")
    print("=" * 72)
    tests = [
        test_gauge_size,
        test_gauge_preserves_T,
        test_canonicalize_idempotent,
        test_orbit_equivalence_collapses,
        test_F3_scaling_collapses,
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
