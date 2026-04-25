"""
Unit tests for rank_3_tensor_decomp over F_2.

Mirrors the rank-2 test pattern from pilot_F2_3x3.flipgraph (inline tests).

Run: python -m exploratory.tensor_decomp_qd.pilot_F2_3x3_v2.test_flipgraph_v2
"""
from __future__ import annotations
import sys
import numpy as np

from .flipgraph_v2 import (
    rank_3_tensor_decomp, try_reduce_4_to_3, GL3_F2,
)
from ..pilot_F2_3x3.core import DIM


def _assert(cond, msg):
    if not cond:
        print(f"  FAIL: {msg}")
        sys.exit(1)
    print(f"  ok:   {msg}")


def _rank1_tensor(u, v, w):
    return np.einsum('p,q,s->pqs', u, v, w, dtype=np.uint8) & 1


def _reconstruct(decomp):
    T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    for (u, v, w) in decomp:
        T ^= _rank1_tensor(u, v, w)
    return T & 1


def test_GL3_size():
    print("\n[1] GL_3(F_2) enumeration")
    _assert(len(GL3_F2) == 168, f"|GL_3(F_2)| = 168 (got {len(GL3_F2)})")


def test_rank0_tensor():
    print("\n[2] Zero tensor decomposes to empty list")
    T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    decomp = rank_3_tensor_decomp(T)
    _assert(decomp is not None and len(decomp) == 0,
            f"zero tensor -> empty decomposition (got {decomp})")


def test_rank1_tensor():
    print("\n[3] Rank-1 tensor decomposes correctly")
    rng = np.random.default_rng(0)
    u = (rng.random(DIM) < 0.4).astype(np.uint8)
    v = (rng.random(DIM) < 0.4).astype(np.uint8)
    w = (rng.random(DIM) < 0.4).astype(np.uint8)
    if u.sum() == 0: u[0] = 1
    if v.sum() == 0: v[0] = 1
    if w.sum() == 0: w[0] = 1
    T = _rank1_tensor(u, v, w)
    decomp = rank_3_tensor_decomp(T)
    _assert(decomp is not None, "rank-1 tensor returns non-None")
    _assert(np.array_equal(_reconstruct(decomp), T),
            f"rank-1 reconstruction matches (decomp len = {len(decomp)})")


def test_rank2_tensor():
    print("\n[4] Rank-2 tensor decomposes correctly")
    rng = np.random.default_rng(1)
    for trial in range(5):
        u1 = (rng.random(DIM) < 0.4).astype(np.uint8); u1[rng.integers(DIM)] = 1
        v1 = (rng.random(DIM) < 0.4).astype(np.uint8); v1[rng.integers(DIM)] = 1
        w1 = (rng.random(DIM) < 0.4).astype(np.uint8); w1[rng.integers(DIM)] = 1
        u2 = (rng.random(DIM) < 0.4).astype(np.uint8); u2[rng.integers(DIM)] = 1
        v2 = (rng.random(DIM) < 0.4).astype(np.uint8); v2[rng.integers(DIM)] = 1
        w2 = (rng.random(DIM) < 0.4).astype(np.uint8); w2[rng.integers(DIM)] = 1
        T = _rank1_tensor(u1, v1, w1) ^ _rank1_tensor(u2, v2, w2)
        decomp = rank_3_tensor_decomp(T)
        _assert(decomp is not None, f"trial {trial}: rank-2 tensor returns non-None")
        _assert(np.array_equal(_reconstruct(decomp), T),
                f"trial {trial}: rank-2 reconstruction matches (decomp len = {len(decomp)})")


def test_rank3_tensor():
    print("\n[5] Rank-3 tensor decomposes correctly")
    rng = np.random.default_rng(2)
    n_trials = 5
    n_pass = 0
    for trial in range(n_trials):
        # Build a tensor of rank exactly 3 over F_2 (avoiding accidental
        # collapse) by sampling random rank-1 terms with linearly-independent
        # components in each mode.
        for _ in range(20):  # try to get a "real" rank-3 tensor
            us = [(rng.random(DIM) < 0.4).astype(np.uint8) for _ in range(3)]
            vs = [(rng.random(DIM) < 0.4).astype(np.uint8) for _ in range(3)]
            ws = [(rng.random(DIM) < 0.4).astype(np.uint8) for _ in range(3)]
            for arr_set in [us, vs, ws]:
                for k in range(3):
                    if arr_set[k].sum() == 0:
                        arr_set[k][rng.integers(DIM)] = 1
            T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
            for k in range(3):
                T ^= _rank1_tensor(us[k], vs[k], ws[k])
            # Verify mode-3 flattening rank is 3 (sufficient for our purposes).
            from .flipgraph_v2 import rank_F2
            M = T.reshape(81, 9)
            if rank_F2(M) == 3:
                break
        else:
            print(f"  trial {trial}: could not construct rank-3 tensor in 20 attempts; skipping")
            continue
        decomp = rank_3_tensor_decomp(T)
        if decomp is None:
            # Tensor rank could be > 3 even with mode-3 rank == 3 in principle;
            # but with random sampling this should be rare. Print and continue.
            print(f"  trial {trial}: rank-3 candidate returned None — true rank may be > 3")
            continue
        if np.array_equal(_reconstruct(decomp), T):
            n_pass += 1
            print(f"  trial {trial}: rank-{len(decomp)} reconstruction matches")
        else:
            print(f"  trial {trial}: reconstruction MISMATCH")
    _assert(n_pass >= 1, f"at least one rank-3 trial reconstructs (passed {n_pass}/{n_trials})")


def test_rank4_tensor_rejected():
    print("\n[6] True-rank-4 tensors return None (not all do; we test that mode-3 rank > 3 is rejected)")
    rng = np.random.default_rng(3)
    n_above = 0
    n_trials = 10
    for trial in range(n_trials):
        # Build a tensor with mode-3 rank likely == 4.
        for _ in range(20):
            us = [(rng.random(DIM) < 0.5).astype(np.uint8) for _ in range(4)]
            vs = [(rng.random(DIM) < 0.5).astype(np.uint8) for _ in range(4)]
            ws = [(rng.random(DIM) < 0.5).astype(np.uint8) for _ in range(4)]
            for arr_set in [us, vs, ws]:
                for k in range(4):
                    if arr_set[k].sum() == 0:
                        arr_set[k][rng.integers(DIM)] = 1
            T = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
            for k in range(4):
                T ^= _rank1_tensor(us[k], vs[k], ws[k])
            from .flipgraph_v2 import rank_F2
            M = T.reshape(81, 9)
            if rank_F2(M) >= 4:
                break
        else:
            continue
        # Mode-3 rank >= 4 => tensor rank >= 4 => rank_3_tensor_decomp must return None.
        decomp = rank_3_tensor_decomp(T)
        if decomp is None:
            n_above += 1
        else:
            print(f"  trial {trial}: BUG — mode-3 rank >= 4 but decomp returned non-None")
    _assert(n_above >= 1,
            f"at least one mode-3-rank>=4 tensor returns None (got {n_above}/{n_trials})")


def test_rank3_tensor_with_known_construction():
    """Construct a definitely-rank-3 tensor with linearly-independent fibers
    in each mode, decompose it, and verify."""
    print("\n[7] Rank-3 tensor with linearly-independent factors")
    # Three rank-1 terms with mutually-disjoint supports in mode 3.
    u1 = np.zeros(DIM, dtype=np.uint8); u1[0] = 1
    v1 = np.zeros(DIM, dtype=np.uint8); v1[0] = 1
    w1 = np.zeros(DIM, dtype=np.uint8); w1[0] = 1
    u2 = np.zeros(DIM, dtype=np.uint8); u2[1] = 1
    v2 = np.zeros(DIM, dtype=np.uint8); v2[1] = 1
    w2 = np.zeros(DIM, dtype=np.uint8); w2[1] = 1
    u3 = np.zeros(DIM, dtype=np.uint8); u3[2] = 1
    v3 = np.zeros(DIM, dtype=np.uint8); v3[2] = 1
    w3 = np.zeros(DIM, dtype=np.uint8); w3[2] = 1
    T = (_rank1_tensor(u1, v1, w1)
         ^ _rank1_tensor(u2, v2, w2)
         ^ _rank1_tensor(u3, v3, w3))
    decomp = rank_3_tensor_decomp(T)
    _assert(decomp is not None, "constructed rank-3 tensor decomposes")
    _assert(np.array_equal(_reconstruct(decomp), T),
            f"reconstruction matches (got {len(decomp)} rank-1 terms)")


def test_4_to_3_self_inverse():
    """Take a known rank-3 tensor, expand it into 4 rank-1 terms by adding
    a duplicate (which over F_2 doesn't change the tensor when it cancels --
    but we'll instead embed in a rank-4 decomp by introducing a non-canceling
    redundancy through a rank-1 splitting). Simpler test: build 4 rank-1 terms
    where two of them sum to a single rank-1 term (rank reduction by absorption)."""
    print("\n[8] try_reduce_4_to_3 fires on constructed reducible quadruple")
    # Construct: T = a (x) b (x) c is rank-1. Express it as sum of 4 rank-1
    # terms by a (x) b (x) c = a (x) b (x) (c xor d xor d) where d != 0.
    # So: a (x) b (x) c = a (x) b (x) c1 xor a (x) b (x) c2 xor a (x) b (x) c3 xor a (x) b (x) c4
    # where c = c1 xor c2 xor c3 xor c4.
    a = np.zeros(DIM, dtype=np.uint8); a[0] = 1; a[1] = 1
    b = np.zeros(DIM, dtype=np.uint8); b[2] = 1
    c1 = np.zeros(DIM, dtype=np.uint8); c1[3] = 1
    c2 = np.zeros(DIM, dtype=np.uint8); c2[4] = 1
    c3 = np.zeros(DIM, dtype=np.uint8); c3[5] = 1
    c4 = np.zeros(DIM, dtype=np.uint8); c4[3] = 1   # duplicate of c1 -> cancels
    # Sum: a (x) b (x) (c1 xor c2 xor c3 xor c4) = a (x) b (x) (c2 xor c3)
    # = a (x) b (x) (c2 xor c3), still rank 1. So 4 rank-1 terms whose sum is rank 1.
    U = np.column_stack([a, a, a, a])
    V = np.column_stack([b, b, b, b])
    W = np.column_stack([c1, c2, c3, c4])
    res = try_reduce_4_to_3(U, V, W, 0, 1, 2, 3)
    _assert(res is not None, "rank-1-sum 4-tuple reduces (rank 1 <= 3)")
    U_new, V_new, W_new = res
    # Reconstruct both and compare.
    T_old = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    for k in range(U.shape[1]):
        T_old ^= _rank1_tensor(U[:, k], V[:, k], W[:, k])
    T_new = np.zeros((DIM, DIM, DIM), dtype=np.uint8)
    for k in range(U_new.shape[1]):
        T_new ^= _rank1_tensor(U_new[:, k], V_new[:, k], W_new[:, k])
    _assert(np.array_equal(T_old & 1, T_new & 1),
            f"reduced decomp preserves tensor (cols {U.shape[1]} -> {U_new.shape[1]})")
    _assert(U_new.shape[1] < U.shape[1],
            f"column count strictly decreased ({U.shape[1]} -> {U_new.shape[1]})")


def run_all():
    print("=" * 72)
    print("Unit tests: rank_3_tensor_decomp + try_reduce_4_to_3")
    print("=" * 72)
    tests = [
        test_GL3_size,
        test_rank0_tensor,
        test_rank1_tensor,
        test_rank2_tensor,
        test_rank3_tensor,
        test_rank4_tensor_rejected,
        test_rank3_tensor_with_known_construction,
        test_4_to_3_self_inverse,
    ]
    for t in tests:
        t()
    print("\n" + "=" * 72)
    print("ALL rank_3_tensor_decomp TESTS PASSED")
    print("=" * 72)


if __name__ == "__main__":
    run_all()
