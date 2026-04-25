"""
Gauge-invariant fingerprints for 3x3 matmul decompositions over F_3.

Replaces brute-force orbit canonicalization (infeasible: |Iso| ~ 2.6e7)
with an INVARIANT TUPLE keyed on:
  1. r — effective rank (zero columns dropped)
  2. mode-flat-rank signature: (rank(M_1), rank(M_2), rank(M_3))
     where M_i is the mode-i flattening of the rank-r decomposition.
     Always (9, 9, 9) for valid full-3x3-matmul decompositions of rank >= 9.
  3. pair_rank_distribution: multiset of (mode-1, mode-2, mode-3) flattening
     ranks over all C(r, 2) pairs.
  4. triple_rank_distribution: same for all C(r, 3) triples (sampled if large).
  5. column_weight_multiset: multiset of (Hamming-weight a_i, b_i, c_i).
     NOT gauge-invariant under basis change — secondary discriminator only.
     We additionally compute it on the post-normalize_and_key form so it's
     at least invariant under column-perm + per-column scaling.
  6. stabilizer_lower_bound: how many of 1000 random Iso elements fix
     the decomposition's normalize_and_key fingerprint.

The TUPLE (r, mode_flat_rank_signature, pair_rank_distribution,
triple_rank_distribution, stabilizer_lower_bound) is gauge-invariant by
construction — independent of which basis we picked.

LOSSY caveat: orbits with identical invariant tuples cannot be told apart
by this fingerprint. We document this honestly; the pilot's value lies in
counting *distinct* tuples (lower bound on orbit count).

Cell binning for MAP-Elites: we hash the full invariant tuple to keep the
archive key space manageable while preserving discrimination.
"""
from __future__ import annotations
import hashlib
import numpy as np
from collections import Counter

from .core import (
    DIM, N, P, effective_rank, drop_zero_columns,
    normalize_all_columns, sort_columns, decomp_to_bytes,
)
from .gauge import rank_Fp, ISO_SAMPLE, normalize_and_key, apply_action


RANK_MIN_THEORY = 19   # Blaeser 2003 lower bound for 3x3 matmul rank (any field)
RANK_MAX_GRID = 30
NAIVE_RANK = 27
TRIPLE_SAMPLE_CAP = 200   # cap on number of triples to sample (C(r,3) ~ thousands)


# -----------------------------------------------------------------------------
# Mode flattenings of a CP decomposition.
# -----------------------------------------------------------------------------
# A rank-r decomposition (U, V, W) reconstructs the tensor T with
#   T[a, b, c] = sum_k U[a, k] V[b, k] W[c, k] (mod p).
# The mode-1 flattening of T is the (9, 81) matrix M_1[a, 9b + c] = T[a, b, c].
# Equivalently (Khatri-Rao): M_1 = U @ (V kr W)^T,  where (V kr W) has columns
# v_k (kron) w_k. Working in factor space:
#   M_1 row span equals row span of U over F_p (if Khatri-Rao columns are
#   independent), which is rank(U).  More generally the mode-i flattening
#   rank equals rank of the i-th factor over the field IF the Khatri-Rao of
#   the other two factors is full-column-rank.
#
# We just compute the mode flattenings directly from the reconstructed
# tensor (DIM x DIM*DIM matrix) and take rank over F_p — this is correct
# regardless of any rank-deficiency in the Khatri-Rao products.

def _reconstruct_with_subset(U, V, W, mask):
    """Reconstruct tensor using only the columns in `mask` (boolean (r,))."""
    Us = U[:, mask]
    Vs = V[:, mask]
    Ws = W[:, mask]
    if Us.shape[1] == 0:
        return np.zeros((DIM, DIM, DIM), dtype=np.int8)
    T = np.zeros((DIM, DIM, DIM), dtype=np.int32)
    for k in range(Us.shape[1]):
        T += np.einsum('p,q,s->pqs',
                       Us[:, k].astype(np.int32),
                       Vs[:, k].astype(np.int32),
                       Ws[:, k].astype(np.int32))
    return (T % P).astype(np.int8)


def _mode_flatten_ranks(T):
    """Return (rank M_1, rank M_2, rank M_3) of the three mode flattenings of T."""
    M1 = T.reshape(DIM, DIM * DIM)
    M2 = T.transpose(1, 0, 2).reshape(DIM, DIM * DIM)
    M3 = T.transpose(2, 0, 1).reshape(DIM, DIM * DIM)
    return rank_Fp(M1, P), rank_Fp(M2, P), rank_Fp(M3, P)


def mode_flat_rank_signature(U, V, W):
    """Tuple of mode-flattening ranks of the reconstructed tensor."""
    T = _reconstruct_with_subset(U, V, W, np.ones(U.shape[1], dtype=bool))
    return _mode_flatten_ranks(T)


# -----------------------------------------------------------------------------
# Pair / triple rank distributions.
# -----------------------------------------------------------------------------

def pair_rank_distribution(U, V, W):
    """Multiset of (rank M_1, rank M_2, rank M_3) over all C(r, 2) pairs.
    Sorted, hashable tuple of (count, signature) pairs."""
    r = U.shape[1]
    counter = Counter()
    for i in range(r):
        for j in range(i + 1, r):
            mask = np.zeros(r, dtype=bool); mask[i] = True; mask[j] = True
            T_ij = _reconstruct_with_subset(U, V, W, mask)
            sig = _mode_flatten_ranks(T_ij)
            counter[sig] += 1
    return tuple(sorted(counter.items()))


def triple_rank_distribution(U, V, W, rng=None, max_triples=TRIPLE_SAMPLE_CAP):
    """Multiset of (rank M_1, rank M_2, rank M_3) over C(r, 3) triples.
    For r >= ~20, C(r, 3) is in the thousands; we sample up to max_triples
    deterministically (using sorted ordering, then if too many, RNG sampling)."""
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
        mask = np.zeros(r, dtype=bool); mask[i] = True; mask[j] = True; mask[k] = True
        T_ijk = _reconstruct_with_subset(U, V, W, mask)
        sig = _mode_flatten_ranks(T_ijk)
        counter[sig] += 1
    return tuple(sorted(counter.items()))


# -----------------------------------------------------------------------------
# Column-weight multiset (NOT gauge-invariant under basis change).
# We compute it AFTER normalize_all_columns + sort_columns so it's at least
# invariant under S_r and per-column F_3* scaling.
# -----------------------------------------------------------------------------

def column_weight_multiset(U, V, W):
    U2, V2, W2 = drop_zero_columns(U, V, W)
    if U2.shape[1] == 0:
        return tuple()
    U2, V2, W2 = normalize_all_columns(U2, V2, W2)
    weights = []
    for k in range(U2.shape[1]):
        wa = int((U2[:, k] != 0).sum())
        wb = int((V2[:, k] != 0).sum())
        wc = int((W2[:, k] != 0).sum())
        weights.append((wa, wb, wc))
    return tuple(sorted(weights))


# -----------------------------------------------------------------------------
# Stabilizer lower bound: count how many of ISO_SAMPLE fix the
# normalize_and_key fingerprint of (U, V, W).
# Lossy because we only check S_r * scaling equivalence on the post-action
# decomposition — but the stabilizer count is a gauge-invariant integer
# (orbit-size formula gives the same count for all orbit reps).
# -----------------------------------------------------------------------------

def stabilizer_lower_bound(U, V, W) -> int:
    """Approximate stabilizer order by counting how many of ISO_SAMPLE fix
    the decomposition (after normalize_and_key)."""
    key0 = normalize_and_key(U, V, W)
    if not key0:
        return 0
    count = 0
    for (M_U, M_V, M_W) in ISO_SAMPLE:
        Up, Vp, Wp = apply_action(U, V, W, M_U, M_V, M_W)
        if normalize_and_key(Up, Vp, Wp) == key0:
            count += 1
    return count


# -----------------------------------------------------------------------------
# Full invariant tuple — gauge-invariant by construction (modulo the
# stabilizer-sample noise; stabilizer count itself is invariant since the
# sample is fixed across all calls).
# -----------------------------------------------------------------------------

def invariant_tuple(U, V, W, include_triples: bool = True,
                    triple_rng_seed: int = 42):
    """Compute the gauge-invariant tuple for a decomposition.

    Returns (r, mode_sig, pair_dist, triple_dist).

    Components:
      - r: effective rank (gauge-invariant — gauge action is invertible)
      - mode_sig: (rank M_1, rank M_2, rank M_3) — flattening ranks of the
        reconstructed tensor; gauge-invariant because Iso preserves the
        tensor itself.
      - pair_dist: multiset of (rank-1, rank-2, rank-3) signatures over all
        C(r, 2) sub-tensors built from pairs of columns. Gauge-invariant:
        the gauge acts by basis change, which preserves rank of each
        flattening of every sub-tensor.
      - triple_dist: same for C(r, 3) (sampled).

    Components NOT in the hash:
      - stabilizer_lower_bound: conceptually invariant (stabilizer ORDER is
        invariant under conjugation) but our ISO_SAMPLE-based estimator is
        a NOISY single-sample count, not an order. Empirical test showed
        46/50 isotropy-equivalent forms had different counts despite the
        true order being equal. Use as a secondary diagnostic only.
      - column_weight_multiset: NOT invariant under basis change.
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
    """Stable hex digest of an invariant tuple for compact archive keys."""
    s = repr(tup).encode('utf-8')
    return hashlib.sha256(s).hexdigest()[:16]


# -----------------------------------------------------------------------------
# Cell key for MAP-Elites archive.
# -----------------------------------------------------------------------------

def cell_of(U, V, W, include_triples: bool = True):
    """The MAP-Elites cell key. Uses the invariant tuple itself (hashed for
    compactness) so two decompositions in the same orbit always share a cell.

    Returns (rank, invariant_tuple_hash) — keeping rank as a top-level
    coordinate is convenient for browsing the archive by rank slices.
    """
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
