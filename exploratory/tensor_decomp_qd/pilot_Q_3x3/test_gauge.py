"""Unit tests for invariant-tuple canonicalization on 3x3 matmul over Q.

The PRIMARY test is that the invariant tuple is unchanged under random
matmul-isotropy elements (signed permutations) applied to a known
decomposition. This is the load-bearing claim: orbits of the gauge action
have well-defined fingerprints over Q.

Tests:
  [1] |SP_3| = 48 (signed-permutation enumeration sanity)
  [2] random_iso_action produces matmul-preserving actions
  [3] invariant_tuple is gauge-invariant under 50 random isotropy elements
      applied to naive rank-27
  [4] invariant_tuple is gauge-invariant under 50 random isotropy elements
      applied to Laderman rank-23
  [5] naive and Laderman have DIFFERENT invariant tuples
  [6] near-miss invariant tuples are usually different
  [7] mode_flat_rank_signature is (9, 9, 9) for both naive and Laderman
  [8] Smirnov-variants reconstruct correctly (over Z)
  [9] Smirnov-variants vs Laderman: invariant-tuple comparison (the outcome-A test)
"""
from __future__ import annotations
import sys
import numpy as np

from .core import is_matmul_decomp, effective_rank, DIM, N
from .gauge import (
    SIGNED_PERMS, ISO_SAMPLE, ISO_SAMPLE_SIZE,
    random_iso_action, apply_action, _preserves_matmul,
)
from .descriptors import (
    invariant_tuple, invariant_tuple_hash,
    mode_flat_rank_signature, pair_rank_distribution,
    L0_sparsity_multiset, L1_norm_multiset,
)
from .known_decomps import (
    naive_decomp, laderman_decomp,
    smirnov_variant_decomp, smirnov_variant2_decomp, laderman_transpose_decomp,
    naive_with_random_iso, near_miss_naive,
)


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def test_signed_perm_size():
    print(f"\n[1] |SP_3| (signed permutations) enumeration")
    _assert(len(SIGNED_PERMS) == 48, f"|SP_3| = 48 (got {len(SIGNED_PERMS)})")


def test_random_iso_preserves_matmul():
    print(f"\n[2] random_iso_action produces matmul-preserving actions")
    rng = np.random.default_rng(0)
    n_check = 50
    bad = 0
    for _ in range(n_check):
        M_U, M_V, M_W, _ = random_iso_action(rng)
        if not _preserves_matmul(M_U, M_V, M_W):
            bad += 1
    _assert(bad == 0, f"{n_check}/{n_check} random isotropy actions preserve MATMUL_T")


def _gauge_invariance_test(name, decomp_fn, n_actions=50):
    U, V, W = decomp_fn()
    base_tup = invariant_tuple(U, V, W, include_triples=False)
    base_hash = invariant_tuple_hash(base_tup)

    rng = np.random.default_rng(1234)
    mismatches = []
    for k in range(n_actions):
        M_U, M_V, M_W, _ = random_iso_action(rng)
        Up, Vp, Wp = apply_action(U, V, W, M_U, M_V, M_W)
        if not is_matmul_decomp(Up, Vp, Wp):
            mismatches.append((k, "not matmul"))
            continue
        tup = invariant_tuple(Up, Vp, Wp, include_triples=False)
        h = invariant_tuple_hash(tup)
        if h != base_hash:
            mismatches.append((k, h))
    return base_tup, base_hash, mismatches


def test_invariance_naive():
    print(f"\n[3] invariant_tuple is gauge-invariant on naive (50 SP_3-perm actions)")
    base_tup, base_hash, mism = _gauge_invariance_test("naive", naive_decomp, n_actions=50)
    print(f"       base hash = {base_hash}")
    print(f"       mode_sig = {base_tup[1]}, |pair_dist| = {len(base_tup[2])}")
    _assert(len(mism) == 0,
            f"50/50 isotropy-perturbed naive match base hash (mismatches: {len(mism)})")


def test_invariance_laderman():
    print(f"\n[4] invariant_tuple is gauge-invariant on Laderman (50 SP_3-perm actions)")
    base_tup, base_hash, mism = _gauge_invariance_test("laderman", laderman_decomp, n_actions=50)
    print(f"       base hash = {base_hash}")
    print(f"       mode_sig = {base_tup[1]}, |pair_dist| = {len(base_tup[2])}")
    _assert(len(mism) == 0,
            f"50/50 isotropy-perturbed Laderman match base hash (mismatches: {len(mism)})")


def test_distinct_orbits():
    print(f"\n[5] naive and Laderman have DIFFERENT invariant tuples")
    A, B, C = naive_decomp()
    naive_tup = invariant_tuple(A, B, C, include_triples=False)
    A2, B2, C2 = laderman_decomp()
    lad_tup = invariant_tuple(A2, B2, C2, include_triples=False)
    naive_hash = invariant_tuple_hash(naive_tup)
    lad_hash = invariant_tuple_hash(lad_tup)
    print(f"       naive hash = {naive_hash}, lad hash = {lad_hash}")
    _assert(naive_hash != lad_hash,
            "naive and Laderman yield distinct invariant hashes")


def test_near_miss_distinct():
    print(f"\n[6] near-miss perturbations of naive yield mostly distinct tuples")
    A, B, C = naive_decomp()
    base_tup = invariant_tuple(A, B, C, include_triples=False)
    base_hash = invariant_tuple_hash(base_tup)
    n_distinct = 0
    n_total = 8
    for seed in range(n_total):
        Up, Vp, Wp = near_miss_naive(perturbations=2, seed=seed)
        tup = invariant_tuple(Up, Vp, Wp, include_triples=False)
        if invariant_tuple_hash(tup) != base_hash:
            n_distinct += 1
    print(f"       {n_distinct}/{n_total} near-miss perturbations have distinct hash")
    _assert(n_distinct >= n_total // 2,
            f"at least half near-misses have distinct hash ({n_distinct}/{n_total})")


def test_mode_flat_rank_full():
    print(f"\n[7] mode-flattening signature is (9, 9, 9) for naive and Laderman")
    A, B, C = naive_decomp()
    sig_naive = mode_flat_rank_signature(A, B, C)
    A, B, C = laderman_decomp()
    sig_lad = mode_flat_rank_signature(A, B, C)
    print(f"       naive sig = {sig_naive}, Laderman sig = {sig_lad}")
    _assert(sig_naive == (9, 9, 9), "naive sig is (9,9,9)")
    _assert(sig_lad == (9, 9, 9), "Laderman sig is (9,9,9)")


def test_smirnov_variants_reconstruct():
    print(f"\n[8] Smirnov / cyclic / transpose variants of Laderman reconstruct over Z")
    A, B, C = smirnov_variant_decomp()
    _assert(is_matmul_decomp(A, B, C),
            f"smirnov_variant (cyclic) reconstructs MATMUL_T, shape {A.shape}")
    A, B, C = smirnov_variant2_decomp()
    _assert(is_matmul_decomp(A, B, C),
            f"smirnov_variant2 (cyclic^2) reconstructs MATMUL_T, shape {A.shape}")
    A, B, C = laderman_transpose_decomp()
    _assert(is_matmul_decomp(A, B, C),
            f"laderman_transpose reconstructs MATMUL_T, shape {A.shape}")


def test_outcome_A_search():
    """The outcome-A test: do the Smirnov / cyclic-conjugate variants of
    Laderman lie in DIFFERENT GL_3(Q)^3 orbits than Laderman?

    Note: the cyclic-conjugate construction uses the matmul tensor's Z_3
    AUTOMORPHISM (slot-swap of the three factor positions, combined with
    the transpose involution on each factor). This automorphism is NOT
    a GL_3(Q)^3 element — it permutes the three factor matrices. So
    distinct invariant tuples here would mean "distinct orbits under
    GL_3(Q)^3 (the standard gauge)", which IS outcome A.

    Same invariant tuple is consistent with two scenarios:
      (a) the tuple is too coarse (lossy);
      (b) the cyclic action IS realized inside GL_3(Q)^3 (i.e., they ARE
          in the same orbit).

    We document either result honestly.
    """
    print(f"\n[9] Outcome-A test: cyclic-conjugate vs Laderman invariant tuples")
    A, B, C = laderman_decomp()
    lad_tup = invariant_tuple(A, B, C, include_triples=True)
    lad_hash = invariant_tuple_hash(lad_tup)
    print(f"       Laderman              hash = {lad_hash}")

    A, B, C = smirnov_variant_decomp()
    sm1_tup = invariant_tuple(A, B, C, include_triples=True)
    sm1_hash = invariant_tuple_hash(sm1_tup)
    print(f"       cyclic-conjugate-1    hash = {sm1_hash}  "
          f"{'DIFFERENT' if sm1_hash != lad_hash else 'same'}")

    A, B, C = smirnov_variant2_decomp()
    sm2_tup = invariant_tuple(A, B, C, include_triples=True)
    sm2_hash = invariant_tuple_hash(sm2_tup)
    print(f"       cyclic-conjugate-2    hash = {sm2_hash}  "
          f"{'DIFFERENT' if sm2_hash != lad_hash else 'same'}")

    A, B, C = laderman_transpose_decomp()
    tr_tup = invariant_tuple(A, B, C, include_triples=True)
    tr_hash = invariant_tuple_hash(tr_tup)
    print(f"       Laderman-transpose    hash = {tr_hash}  "
          f"{'DIFFERENT' if tr_hash != lad_hash else 'same'}")

    distinct = len({lad_hash, sm1_hash, sm2_hash, tr_hash})
    print(f"       distinct rank-23 invariant tuples found: {distinct}")
    if distinct > 1:
        print(f"       OUTCOME A: multiple rank-23 invariant tuples found.")
    else:
        print(f"       OUTCOME B: all variants share invariant tuple "
              f"(either same orbit, or tuple too coarse).")


def run_all():
    print("=" * 72)
    print(f"Invariant-tuple unit tests: 3x3 matmul over Q (small-int-bounded)")
    print("=" * 72)
    tests = [
        test_signed_perm_size,
        test_random_iso_preserves_matmul,
        test_invariance_naive,
        test_invariance_laderman,
        test_distinct_orbits,
        test_near_miss_distinct,
        test_mode_flat_rank_full,
        test_smirnov_variants_reconstruct,
        test_outcome_A_search,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL UNIT TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
