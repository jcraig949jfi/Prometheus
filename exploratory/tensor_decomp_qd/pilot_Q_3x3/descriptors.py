"""
Gauge-invariant fingerprints for 3x3 matmul decompositions over Q.

Replaces brute-force orbit canonicalization (infeasible: |GL_3(Q)|^3 is
INFINITE) with an INVARIANT TUPLE keyed on:

  1. r — effective rank (zero columns dropped)
  2. mode_flat_rank_signature: (rank(M_1), rank(M_2), rank(M_3))
     where M_i is the mode-i flattening of the reconstructed tensor,
     computed exactly over Q via fractions.Fraction Gaussian elimination.
  3. pair_rank_distribution: multiset of (rank-1, rank-2, rank-3)
     flattening ranks over all C(r, 2) pairs.
  4. triple_rank_distribution: same for C(r, 3) (sampled if large).

Field-agnostic vs F_p:
  - rank: same definition (rank over Q vs over F_p). Computed exactly via
    fractions, never floating point.
  - mode_flat_rank_signature, pair_rank_distribution, triple_rank_distribution:
    same definitions, with rank_Q replacing rank_Fp.
  - Hamming weight (F_p) -> L^0 sparsity (count of nonzero entries) over Z.
    Useful as a tie-breaker but NOT gauge-invariant under basis change.
  - stabilizer_lower_bound: count of fixed elements in our finite ISO_SAMPLE.
    Like the F_3 version, this is a noisy estimator and NOT in the hash.

The TUPLE (r, mode_flat_rank_signature, pair_rank_distribution,
triple_rank_distribution) is gauge-invariant by construction under
ANY GL_3(Q)^3 element (not just signed permutations) because rank of a
flattening is preserved by basis change.

LOSSY caveat: as in F_3, "different cell" => different orbit, but
"same cell" does NOT prove same orbit. We document this honestly.
"""
from __future__ import annotations
import hashlib
import numpy as np
from collections import Counter

from .core import (
    DIM, N, effective_rank, drop_zero_columns,
    normalize_all_columns, sort_columns,
)
from .gauge import rank_Q, ISO_SAMPLE, apply_action


RANK_MIN_THEORY = 19         # Blaeser 2003 lower bound for 3x3 matmul rank
RANK_MAX_GRID = 30
NAIVE_RANK = 27
TRIPLE_SAMPLE_CAP = 100      # cap (C(23,3) = 1771; we sample 100 for speed)


# -----------------------------------------------------------------------------
# Mode flattenings of a CP decomposition.
# -----------------------------------------------------------------------------

def _reconstruct_with_subset(U, V, W, mask):
    """Reconstruct integer tensor using only columns in `mask`."""
    Us = U[:, mask]
    Vs = V[:, mask]
    Ws = W[:, mask]
    if Us.shape[1] == 0:
        return np.zeros((DIM, DIM, DIM), dtype=np.int32)
    T = np.zeros((DIM, DIM, DIM), dtype=np.int64)
    for k in range(Us.shape[1]):
        T += np.einsum('p,q,s->pqs',
                       Us[:, k].astype(np.int64),
                       Vs[:, k].astype(np.int64),
                       Ws[:, k].astype(np.int64))
    return T.astype(np.int32)


def _mode_flatten_ranks(T):
    """Tuple (rank M_1, rank M_2, rank M_3) over Q of the three flattenings."""
    M1 = T.reshape(DIM, DIM * DIM)
    M2 = T.transpose(1, 0, 2).reshape(DIM, DIM * DIM)
    M3 = T.transpose(2, 0, 1).reshape(DIM, DIM * DIM)
    return rank_Q(M1), rank_Q(M2), rank_Q(M3)


def mode_flat_rank_signature(U, V, W):
    """Mode-flattening rank signature of the reconstructed tensor."""
    T = _reconstruct_with_subset(U, V, W, np.ones(U.shape[1], dtype=bool))
    return _mode_flatten_ranks(T)


# -----------------------------------------------------------------------------
# Pair / triple rank distributions.
# -----------------------------------------------------------------------------

def pair_rank_distribution(U, V, W):
    """Multiset of (rank M_1, rank M_2, rank M_3) over all C(r, 2) pairs."""
    r = U.shape[1]
    counter = Counter()
    for i in range(r):
        for j in range(i + 1, r):
            mask = np.zeros(r, dtype=bool)
            mask[i] = True; mask[j] = True
            T_ij = _reconstruct_with_subset(U, V, W, mask)
            sig = _mode_flatten_ranks(T_ij)
            counter[sig] += 1
    return tuple(sorted(counter.items()))


def triple_rank_distribution(U, V, W, rng=None, max_triples=TRIPLE_SAMPLE_CAP):
    """Multiset of mode-flat rank sigs over C(r, 3) triples (sampled)."""
    r = U.shape[1]
    all_triples = []
    for i in range(r):
        for j in range(i + 1, r):
            for k in range(j + 1, r):
                all_triples.append((i, j, k))
    if len(all_triples) > max_triples:
        if rng is None:
            rng = np.random.default_rng(99)
        idx = rng.choice(len(all_triples), size=max_triples, replace=False)
        all_triples = [all_triples[i] for i in idx]
    counter = Counter()
    for (i, j, k) in all_triples:
        mask = np.zeros(r, dtype=bool)
        mask[i] = True; mask[j] = True; mask[k] = True
        T_ijk = _reconstruct_with_subset(U, V, W, mask)
        sig = _mode_flatten_ranks(T_ijk)
        counter[sig] += 1
    return tuple(sorted(counter.items()))


# -----------------------------------------------------------------------------
# L^0 sparsity / L^1 sum (NOT gauge-invariant under basis change). Available
# as a tie-breaker after sign + permutation normalization only.
# -----------------------------------------------------------------------------

def L0_sparsity_multiset(U, V, W):
    """Multiset of (nonzero_count_a, nonzero_count_b, nonzero_count_c) per col."""
    Ud, Vd, Wd = drop_zero_columns(U, V, W)
    if Ud.shape[1] == 0:
        return tuple()
    Ud, Vd, Wd = normalize_all_columns(Ud, Vd, Wd)
    weights = []
    for k in range(Ud.shape[1]):
        wa = int((Ud[:, k] != 0).sum())
        wb = int((Vd[:, k] != 0).sum())
        wc = int((Wd[:, k] != 0).sum())
        weights.append((wa, wb, wc))
    return tuple(sorted(weights))


def L1_norm_multiset(U, V, W):
    """Multiset of (sum|a|, sum|b|, sum|c|) per column."""
    Ud, Vd, Wd = drop_zero_columns(U, V, W)
    if Ud.shape[1] == 0:
        return tuple()
    Ud, Vd, Wd = normalize_all_columns(Ud, Vd, Wd)
    weights = []
    for k in range(Ud.shape[1]):
        wa = int(np.abs(Ud[:, k]).sum())
        wb = int(np.abs(Vd[:, k]).sum())
        wc = int(np.abs(Wd[:, k]).sum())
        weights.append((wa, wb, wc))
    return tuple(sorted(weights))


# -----------------------------------------------------------------------------
# Stabilizer lower bound under our finite ISO_SAMPLE (signed permutations).
# Noisy single-sample estimator; NOT in the hash. Available diagnostic only.
# -----------------------------------------------------------------------------

def stabilizer_lower_bound(U, V, W) -> int:
    """Count how many SP_3-action triples in ISO_SAMPLE leave the (sign+perm)
    canonical key invariant."""
    base = _normalize_key(U, V, W)
    if base is None:
        return 0
    count = 0
    for (M_U, M_V, M_W) in ISO_SAMPLE:
        Up, Vp, Wp = apply_action(U, V, W, M_U, M_V, M_W)
        kk = _normalize_key(Up, Vp, Wp)
        if kk == base:
            count += 1
    return count


def _normalize_key(U, V, W):
    """Sign + permutation canonical key (lossy under basis change)."""
    Ud, Vd, Wd = drop_zero_columns(U, V, W)
    if Ud.shape[1] == 0:
        return tuple()
    Ud, Vd, Wd = normalize_all_columns(Ud, Vd, Wd)
    Ud, Vd, Wd = sort_columns(Ud, Vd, Wd)
    return (
        Ud.astype(np.int32).tobytes(),
        Vd.astype(np.int32).tobytes(),
        Wd.astype(np.int32).tobytes(),
    )


# -----------------------------------------------------------------------------
# Full invariant tuple — gauge-invariant by construction over Q.
# -----------------------------------------------------------------------------

def invariant_tuple(U, V, W, include_triples: bool = True,
                    triple_rng_seed: int = 42):
    """Compute the gauge-invariant tuple over Q.

    Returns (r, mode_sig, pair_dist, triple_dist).

    Components:
      - r: effective rank (gauge-invariant — gauge action is invertible).
      - mode_sig: (rank M_1, rank M_2, rank M_3) of the reconstructed tensor
        over Q. Gauge-invariant because the gauge preserves the tensor.
      - pair_dist: multiset over C(r, 2) sub-tensors. Gauge-invariant: the
        gauge acts by basis change which preserves rank of every flattening
        of every sub-tensor.
      - triple_dist: same for C(r, 3) (sampled).
    """
    Ud, Vd, Wd = drop_zero_columns(U, V, W)
    r = Ud.shape[1]
    if r == 0:
        return (0, (0, 0, 0), (), ())

    mode_sig = mode_flat_rank_signature(Ud, Vd, Wd)
    pair_dist = pair_rank_distribution(Ud, Vd, Wd)
    if include_triples:
        rng = np.random.default_rng(triple_rng_seed)
        trip_dist = triple_rank_distribution(Ud, Vd, Wd, rng=rng)
    else:
        trip_dist = ()
    return (r, mode_sig, pair_dist, trip_dist)


def invariant_tuple_hash(tup) -> str:
    """Stable hex digest of the tuple."""
    s = repr(tup).encode('utf-8')
    return hashlib.sha256(s).hexdigest()[:16]


def cell_of(U, V, W, include_triples: bool = True):
    """MAP-Elites cell key."""
    tup = invariant_tuple(U, V, W, include_triples=include_triples)
    r = tup[0]
    return (r, invariant_tuple_hash(tup)), tup


def canonical_sparsity(U, V, W) -> float:
    Ud, Vd, Wd = drop_zero_columns(U, V, W)
    if Ud.shape[1] == 0:
        return 1.0
    Ud, Vd, Wd = normalize_all_columns(Ud, Vd, Wd)
    total = Ud.size + Vd.size + Wd.size
    zeros = (Ud == 0).sum() + (Vd == 0).sum() + (Wd == 0).sum()
    return float(zeros) / total
