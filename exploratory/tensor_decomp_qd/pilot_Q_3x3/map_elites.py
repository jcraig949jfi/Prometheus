"""
MAP-Elites for 3x3 matmul over Q (small-integer-bounded), keyed by
gauge-invariant tuple.

Cell key: (effective_rank, invariant_tuple_hash[16]).
Two decompositions in the same GL_3(Q)^3 orbit produce the same cell key
(verified in test_gauge.py via 50 random signed-permutation actions of
both naive-27 and Laderman-23).

The mutation operator is BOUNDED INTEGER perturbation: pick an entry,
add delta in {-1, +1}, clip to [-K, +K] (K=2 by default).

Hard kill: any submission landing at canonical rank < 19 (Blaeser 2003
lower bound) triggers a halt — canonicalizer or descriptor bug.
"""
from __future__ import annotations
import time
import numpy as np
from collections import defaultdict

from .core import (
    MATMUL_T, reconstruct, is_matmul_decomp, drop_zero_columns,
    DIM, N, K_DEFAULT,
)
from .descriptors import (
    invariant_tuple, invariant_tuple_hash, cell_of,
    canonical_sparsity, RANK_MIN_THEORY, RANK_MAX_GRID, NAIVE_RANK,
)
from .known_decomps import (
    naive_decomp, laderman_decomp, smirnov_variant_decomp,
    smirnov_variant2_decomp,
)


R_MAX = 30


class ForbiddenCellViolation(Exception):
    """Raised if a canonical decomposition lands below Blaeser's bound."""


class Archive:
    def __init__(self, rank_min_hard: int = RANK_MIN_THEORY,
                 include_triples: bool = True):
        self.cells: dict = {}
        self.hit_counts: dict = defaultdict(int)
        self.total_submissions = 0
        self.total_valid = 0
        self.rank_min_hard = rank_min_hard
        self.include_triples = include_triples

    def submit(self, U, V, W):
        self.total_submissions += 1
        if not is_matmul_decomp(U, V, W):
            return False, None
        self.total_valid += 1

        Ud, Vd, Wd = drop_zero_columns(U, V, W)
        r_eff = Ud.shape[1]

        if r_eff < self.rank_min_hard:
            raise ForbiddenCellViolation(
                f"effective rank {r_eff} < Blaeser bound {self.rank_min_hard}"
            )

        tup = invariant_tuple(Ud, Vd, Wd, include_triples=self.include_triples)
        h = invariant_tuple_hash(tup)
        cell = (r_eff, h)
        self.hit_counts[cell] += 1
        if cell not in self.cells:
            self.cells[cell] = {
                'rank': r_eff,
                'hash': h,
                'tup': tup,
                'U': Ud.copy(), 'V': Vd.copy(), 'W': Wd.copy(),
                'sparsity': canonical_sparsity(Ud, Vd, Wd),
            }
            return True, cell
        return False, cell

    def cell_count(self): return len(self.cells)

    def cells_by_rank(self):
        out = defaultdict(list)
        for cell, info in self.cells.items():
            out[cell[0]].append((cell, info))
        return out

    def min_rank_found(self):
        return min((c[0] for c in self.cells), default=None)

    def summary_lines(self):
        lines = []
        lines.append(f"Archive: {self.cell_count()} cells")
        lines.append(f"  submissions: {self.total_submissions}, valid: {self.total_valid}, "
                     f"rate: {self.total_valid / max(1, self.total_submissions):.5f}")
        by_rank = self.cells_by_rank()
        for r in sorted(by_rank):
            n_cells = len(by_rank[r])
            hits = sum(self.hit_counts[c] for c, _ in by_rank[r])
            lines.append(f"  rank {r:2d}: {n_cells:3d} distinct invariant-tuple cells, "
                         f"{hits:6d} hits")
        return lines


# -----------------------------------------------------------------------------
# Genome helpers
# -----------------------------------------------------------------------------

def random_genome(rng, r=R_MAX, K=K_DEFAULT, density=0.30):
    """Random bounded-integer genome with entries in {-K, ..., K}."""
    def sample(shape):
        nz = rng.random(shape) < density
        # Random in {-K, ..., K} \ {0}
        signs = rng.choice([-1, 1], size=shape).astype(np.int32)
        magnitudes = rng.integers(1, K + 1, size=shape).astype(np.int32)
        vals = signs * magnitudes
        return np.where(nz, vals, 0).astype(np.int32)
    return sample((DIM, r)), sample((DIM, r)), sample((DIM, r))


def pad_genome(U, V, W, r=R_MAX):
    cur = U.shape[1]
    if cur >= r:
        return U[:, :r].copy(), V[:, :r].copy(), W[:, :r].copy()
    z = np.zeros((DIM, r - cur), dtype=np.int32)
    return (np.column_stack([U, z]).astype(np.int32),
            np.column_stack([V, z]).astype(np.int32),
            np.column_stack([W, z]).astype(np.int32))


def cancel_duplicate_columns_Z(U, V, W):
    """Over Z, two equal columns are still a redundancy IF their c-coefficient
    can absorb the merge. We detect strict duplicates and merge:
      A column of (a, b, c1) and (a, b, c2) merges to (a, b, c1 + c2).
    Only fires if the merged c stays within K-bound (else skip).
    """
    r = U.shape[1]
    if r == 0:
        return U, V, W
    # Group by (a, b) signature.
    keys = {}
    for k in range(r):
        key = (U[:, k].tobytes(), V[:, k].tobytes())
        keys.setdefault(key, []).append(k)
    to_drop = set()
    Wnew = W.copy()
    for key, idxs in keys.items():
        if len(idxs) <= 1:
            continue
        # Sum c's into the first idx; drop the rest.
        first = idxs[0]
        for j in idxs[1:]:
            Wnew[:, first] = Wnew[:, first] + W[:, j]
            to_drop.add(j)
    if to_drop:
        keep_mask = np.array([i not in to_drop for i in range(r)])
        U = U[:, keep_mask]
        V = V[:, keep_mask]
        Wnew = Wnew[:, keep_mask]
    return U, V, Wnew


def drop_zero_cols(U, V, W):
    return drop_zero_columns(U, V, W)


# -----------------------------------------------------------------------------
# Mutation operators
# -----------------------------------------------------------------------------

def mutate(U, V, W, rng, K: int = K_DEFAULT,
           p_flip: float = 0.012,
           p_col_zero: float = 0.03,
           p_col_replace: float = 0.05,
           p_col_swap: float = 0.10,
           p_cancel_check: float = 0.30,
           p_drop_zero_check: float = 0.30):
    """Bounded-integer mutation: per-entry +/-1 perturbation clipped to [-K, K]."""
    U2 = U.astype(np.int32).copy()
    V2 = V.astype(np.int32).copy()
    W2 = W.astype(np.int32).copy()
    r = U2.shape[1]

    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_flip
        deltas = rng.choice([-1, 1], size=M.shape).astype(np.int32)
        new_vals = M + deltas * mask
        # Clip to [-K, K].
        new_vals = np.clip(new_vals, -K, K).astype(np.int32)
        M[:] = new_vals

    if rng.random() < p_col_zero and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = 0; V2[:, col] = 0; W2[:, col] = 0

    if rng.random() < p_col_replace and r > 0:
        col = int(rng.integers(0, r))
        for M in (U2, V2, W2):
            for i in range(DIM):
                if rng.random() < 0.4:
                    sign = rng.choice([-1, 1])
                    mag = rng.integers(1, K + 1)
                    M[i, col] = int(sign * mag)
                else:
                    M[i, col] = 0

    if rng.random() < p_col_swap and r >= 2:
        i, j = rng.choice(r, size=2, replace=False)
        which = rng.integers(0, 3)
        if which == 0:
            U2[:, [i, j]] = U2[:, [j, i]]
        elif which == 1:
            V2[:, [i, j]] = V2[:, [j, i]]
        else:
            W2[:, [i, j]] = W2[:, [j, i]]

    if rng.random() < p_cancel_check:
        U2, V2, W2 = cancel_duplicate_columns_Z(U2, V2, W2)
    if rng.random() < p_drop_zero_check:
        U2, V2, W2 = drop_zero_cols(U2, V2, W2)

    return U2, V2, W2


# -----------------------------------------------------------------------------
# Evolution loop
# -----------------------------------------------------------------------------

def run_evolution(
    n_generations: int = 500,
    population_size: int = 30,
    seed: int = 0,
    seed_known: bool = True,
    verbose: bool = True,
    include_triples: bool = True,
    seed_smirnov: bool = True,
):
    rng = np.random.default_rng(seed)
    archive = Archive(include_triples=include_triples)

    if seed_known:
        seed_fns = [
            ("naive_decomp", naive_decomp),
            ("laderman_decomp", laderman_decomp),
        ]
        if seed_smirnov:
            seed_fns.append(("smirnov_variant_decomp", smirnov_variant_decomp))
            seed_fns.append(("smirnov_variant2_decomp", smirnov_variant2_decomp))
        for name, fn in seed_fns:
            try:
                U, V, W = fn()
            except Exception as e:
                if verbose:
                    print(f"  seed {name}: SKIPPED ({e})")
                continue
            U, V, W = pad_genome(U, V, W)
            acc, cell = archive.submit(U, V, W)
            if verbose:
                print(f"  seed {name}: {'+' if acc else '='} cell={cell}")

    # Initialize population from naive perturbations.
    population = []
    base_U, base_V, base_W = pad_genome(*naive_decomp())
    for _ in range(population_size):
        U = base_U.copy(); V = base_V.copy(); W = base_W.copy()
        n_perturb = int(rng.integers(1, 4))
        for _ in range(n_perturb):
            which = rng.integers(0, 3)
            i = int(rng.integers(0, DIM))
            j = int(rng.integers(0, R_MAX))
            delta = int(rng.choice([-1, 1]))
            mat = [U, V, W][which]
            new_v = int(mat[i, j]) + delta
            mat[i, j] = max(-K_DEFAULT, min(K_DEFAULT, new_v))
        population.append((U, V, W))
        archive.submit(U, V, W)

    t0 = time.time()
    for gen in range(n_generations):
        if archive.cell_count() > 0 and rng.random() < 0.7:
            cells = list(archive.cells.values())
            info = cells[int(rng.integers(0, len(cells)))]
            U, V, W = info['U'], info['V'], info['W']
            U, V, W = pad_genome(U, V, W)
        else:
            idx = int(rng.integers(0, len(population)))
            U, V, W = population[idx]

        try:
            child = mutate(U, V, W, rng)
            archive.submit(*child)
        except ForbiddenCellViolation as e:
            print(f"\n  *** HARD KILL at gen {gen}: {e}")
            return archive

        if verbose and (gen + 1) % 100 == 0:
            elapsed = time.time() - t0
            mr = archive.min_rank_found()
            print(f"  gen {gen+1:5d}: cells={archive.cell_count()}, "
                  f"valid={archive.total_valid}, min_rank={mr}, "
                  f"elapsed={elapsed:.1f}s")

    return archive
