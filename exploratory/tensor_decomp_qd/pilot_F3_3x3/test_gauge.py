"""Unit tests for invariant-tuple canonicalization on 3x3 matmul over F_3.

The PRIMARY test is that the invariant tuple is unchanged under random
matmul-isotropy elements applied to a known decomposition. This is the
load-bearing claim: orbits of the gauge action have well-defined
fingerprints.

Tests:
  [1] |GL_3(F_3)| = 11232 (enumeration sanity)
  [2] |O_3(F_3)| = 48 (orthogonal subgroup sanity)
  [3] random_iso_action produces matmul-preserving actions
  [4] invariant_tuple is gauge-invariant under 50 random isotropy elements
      applied to naive rank-27
  [5] invariant_tuple is gauge-invariant under 50 random isotropy elements
      applied to Laderman rank-23
  [6] naive and Laderman have DIFFERENT invariant tuples (orbits distinct)
  [7] near-miss invariant tuples are usually different (lossy-but-useful)
  [8] mode_flat_rank_signature is (9, 9, 9) for both naive and Laderman
      (matmul tensor has rank-9 mode flattenings; any valid full decomp
      should reflect this)
"""
from __future__ import annotations
import sys
import numpy as np

from .core import is_matmul_decomp, effective_rank, DIM, N, P
from .gauge import (
    GLn, ORTHOGONAL_GLn, ISO_SAMPLE, ISO_SAMPLE_SIZE,
    random_iso_action, apply_action, _preserves_matmul,
)
from .descriptors import (
    invariant_tuple, invariant_tuple_hash,
    mode_flat_rank_signature, pair_rank_distribution,
    stabilizer_lower_bound,
)
from .known_decomps import (
    naive_decomp, laderman_decomp, naive_with_random_iso, near_miss_naive,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def test_GLn_size():
    print(f"\n[1] |GL_{N}(F_{P})| enumeration")
    _assert(len(GLn) == 11232, f"|GL_3(F_3)| = 11232 (got {len(GLn)})")


def test_orthogonal_subgroup():
    print(f"\n[2] F_3-orthogonal subgroup |O_3(F_3)|")
    _assert(len(ORTHOGONAL_GLn) == 48,
            f"|O_3(F_3)| = 48 (got {len(ORTHOGONAL_GLn)})")


def test_random_iso_preserves_matmul():
    print(f"\n[3] random_iso_action produces matmul-preserving actions")
    rng = np.random.default_rng(0)
    n_check = 50
    bad = 0
    for _ in range(n_check):
        M_U, M_V, M_W, _ = random_iso_action(rng)
        if not _preserves_matmul(M_U, M_V, M_W):
            bad += 1
    _assert(bad == 0, f"50/50 random isotropy actions preserve MATMUL_T (bad={bad})")


def _gauge_invariance_test(name, decomp_fn, n_actions=50):
    U, V, W = decomp_fn()
    # Compute base invariant tuple (skip triples for speed; pair_dist + stab is enough).
    base_tup = invariant_tuple(U, V, W, include_triples=False)
    base_hash = invariant_tuple_hash(base_tup)

    rng = np.random.default_rng(1234)
    mismatches = []
    for k in range(n_actions):
        M_U, M_V, M_W, _ = random_iso_action(rng)
        Up, Vp, Wp = apply_action(U, V, W, M_U, M_V, M_W)
        # Sanity: still a matmul decomp.
        if not is_matmul_decomp(Up, Vp, Wp):
            mismatches.append((k, "not matmul"))
            continue
        tup = invariant_tuple(Up, Vp, Wp, include_triples=False)
        h = invariant_tuple_hash(tup)
        if h != base_hash:
            mismatches.append((k, h))
    return base_tup, base_hash, mismatches


def test_invariance_naive():
    print(f"\n[4] invariant_tuple is gauge-invariant on naive (50 random isotropy elements)")
    base_tup, base_hash, mism = _gauge_invariance_test("naive", naive_decomp, n_actions=50)
    print(f"       base hash = {base_hash}")
    print(f"       base mode_sig = {base_tup[1]}, |pair_dist| = {len(base_tup[2])}")
    _assert(len(mism) == 0,
            f"50/50 isotropy-perturbed naive decompositions match base hash "
            f"(mismatches: {len(mism)})")


def test_invariance_laderman():
    print(f"\n[5] invariant_tuple is gauge-invariant on Laderman (50 random isotropy elements)")
    base_tup, base_hash, mism = _gauge_invariance_test("laderman", laderman_decomp, n_actions=50)
    print(f"       base hash = {base_hash}")
    print(f"       base mode_sig = {base_tup[1]}, |pair_dist| = {len(base_tup[2])}")
    _assert(len(mism) == 0,
            f"50/50 isotropy-perturbed Laderman decompositions match base hash "
            f"(mismatches: {len(mism)})")


def test_distinct_orbits():
    print(f"\n[6] naive and Laderman have DIFFERENT invariant tuples")
    A, B, C = naive_decomp()
    Ud, Vd, Wd = naive_decomp()
    naive_tup = invariant_tuple(A, B, C, include_triples=False)
    A2, B2, C2 = laderman_decomp()
    lad_tup = invariant_tuple(A2, B2, C2, include_triples=False)
    naive_hash = invariant_tuple_hash(naive_tup)
    lad_hash = invariant_tuple_hash(lad_tup)
    print(f"       naive hash = {naive_hash}, lad hash = {lad_hash}")
    _assert(naive_hash != lad_hash,
            "naive (rank 27) and Laderman (rank 23) yield distinct invariant hashes")


def test_near_miss_distinct():
    print(f"\n[7] near-miss perturbations of naive yield mostly distinct invariant tuples")
    A, B, C = naive_decomp()
    base_tup = invariant_tuple(A, B, C, include_triples=False)
    base_hash = invariant_tuple_hash(base_tup)
    n_distinct = 0
    n_total = 8
    for seed in range(n_total):
        Up, Vp, Wp = near_miss_naive(perturbations=2, seed=seed)
        # near-miss may be invalid; we only check the invariant hash differs.
        # (Even invalid decomps have a defined invariant tuple under our
        # definition — it just describes a different tensor.)
        tup = invariant_tuple(Up, Vp, Wp, include_triples=False)
        if invariant_tuple_hash(tup) != base_hash:
            n_distinct += 1
    print(f"       {n_distinct}/{n_total} near-miss perturbations have distinct hash")
    _assert(n_distinct >= n_total // 2,
            f"at least half of near-misses (got {n_distinct}/{n_total}) have distinct invariant tuple")


def test_mode_flat_rank_full():
    print(f"\n[8] mode-flattening rank signature is (9, 9, 9) for naive and Laderman")
    A, B, C = naive_decomp()
    sig_naive = mode_flat_rank_signature(A, B, C)
    A, B, C = laderman_decomp()
    sig_lad = mode_flat_rank_signature(A, B, C)
    print(f"       naive sig = {sig_naive}, Laderman sig = {sig_lad}")
    _assert(sig_naive == (9, 9, 9), f"naive mode-flatten signature is (9,9,9)")
    _assert(sig_lad == (9, 9, 9), f"Laderman mode-flatten signature is (9,9,9)")


def run_all():
    print("=" * 72)
    print(f"Invariant-tuple unit tests: 3x3 matmul over F_{P}")
    print("=" * 72)
    tests = [
        test_GLn_size,
        test_orthogonal_subgroup,
        test_random_iso_preserves_matmul,
        test_invariance_naive,
        test_invariance_laderman,
        test_distinct_orbits,
        test_near_miss_distinct,
        test_mode_flat_rank_full,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL UNIT TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
