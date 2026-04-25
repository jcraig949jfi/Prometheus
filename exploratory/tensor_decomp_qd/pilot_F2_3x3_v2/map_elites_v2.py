"""
MAP-Elites v2 for 3x3 matmul over F_2 — adds 4-to-3 flip-graph mutations.

Builds on pilot_F2_3x3.map_elites; this file overrides the mutate() function
to additionally try try_reduce_4_to_3 (and re-applies the 3-to-2 / 2-to-2
moves from v1 to keep the move-set monotonically richer).

Same Archive class, same forbidden-cell discipline, same parameters.
"""
from __future__ import annotations
import time
import numpy as np
from collections import defaultdict

# Re-use almost everything from v1.
from ..pilot_F2_3x3.core import (
    MATMUL_T, reconstruct, is_matmul_decomp, decomp_to_bytes, sort_columns,
    DIM, N,
)
from ..pilot_F2_3x3.gauge import (
    ISO_SIZE, canonicalize, effective_rank, stabilizer_order,
)
from ..pilot_F2_3x3.descriptors import (
    SPARSITY_BINS, RANK_MIN_THEORY, RANK_MAX_GRID, NAIVE_RANK,
    canonical_sparsity, sparsity_bin, stabilizer_bin, cell_of,
)
from ..pilot_F2_3x3.known_decomps import naive_decomp, laderman_decomp
from ..pilot_F2_3x3.map_elites import (
    Archive, ForbiddenCellViolation, R_MAX,
    random_genome, pad_genome,
    drop_zero_columns, cancel_duplicate_columns,
)
from ..pilot_F2_3x3.flipgraph import (
    try_reduce_3_to_2 as _v1_try_reduce_3_to_2,
    try_swap_2_to_2 as _v1_try_swap_2_to_2,
)
from .flipgraph_v2 import try_reduce_4_to_3


# Wrappers that suppress a known TypeError edge case in v1's
# rank_2_tensor_decomp (line 167 of v1's flipgraph.py: when the single basis
# column reshapes to a non-rank-1 9x9 matrix, factor_rank1_matrix_F2 returns
# None and the unpack `u, v = ...` raises TypeError instead of returning None).
# We catch and treat as "move does not apply" — preserves v1 semantics for
# the cases v1 handled correctly, without modifying v1 code.

def try_reduce_3_to_2(U, V, W, i, j, k):
    try:
        return _v1_try_reduce_3_to_2(U, V, W, i, j, k)
    except TypeError:
        return None


def try_swap_2_to_2(U, V, W, i, j):
    try:
        return _v1_try_swap_2_to_2(U, V, W, i, j)
    except TypeError:
        return None


# Mutation: add 4-to-3 to the existing repertoire.
def mutate_v2(U, V, W, rng,
              p_bitflip: float = 0.01,
              p_col_zero: float = 0.03,
              p_col_replace: float = 0.05,
              p_col_swap: float = 0.10,
              p_cancel_check: float = 0.40,
              p_drop_zero_check: float = 0.40,
              p_3to2: float = 0.10,
              p_2to2: float = 0.10,
              p_4to3: float = 0.10,
              flipgraph_attempts: int = 5):
    """v2 mutation: same as v1 plus optional flip-graph moves (3-to-2, 2-to-2,
    and the new 4-to-3). Each flip-graph move is attempted on a small random
    subset of column tuples per call, since exhaustive search is expensive."""
    U2 = U.copy(); V2 = V.copy(); W2 = W.copy()
    r = U2.shape[1]

    # (1) Bit flips.
    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_bitflip
        M[mask] ^= 1

    # (2) Zero a random column.
    if rng.random() < p_col_zero and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = 0; V2[:, col] = 0; W2[:, col] = 0

    # (3) Replace a random column.
    if rng.random() < p_col_replace and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)
        V2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)
        W2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)

    # (4) Swap component between two columns.
    if rng.random() < p_col_swap and r >= 2:
        i, j = rng.choice(r, size=2, replace=False)
        which = rng.integers(0, 3)
        if which == 0:
            U2[:, [i, j]] = U2[:, [j, i]]
        elif which == 1:
            V2[:, [i, j]] = V2[:, [j, i]]
        else:
            W2[:, [i, j]] = W2[:, [j, i]]

    # (5) Validity-preserving rank-reducers.
    if rng.random() < p_cancel_check:
        U2, V2, W2 = cancel_duplicate_columns(U2, V2, W2)
    if rng.random() < p_drop_zero_check:
        U2, V2, W2 = drop_zero_columns(U2, V2, W2)

    # (6) Flip-graph 3-to-2 (rank reduction by 1; replaces 3 cols with 2).
    if rng.random() < p_3to2 and U2.shape[1] >= 3:
        rr = U2.shape[1]
        for _ in range(flipgraph_attempts):
            i, j, k = rng.choice(rr, size=3, replace=False)
            res = try_reduce_3_to_2(U2, V2, W2, int(i), int(j), int(k))
            if res is not None:
                U2, V2, W2 = res
                break

    # (7) Flip-graph 2-to-2 (alternative rank-2 decomp; rank preserved).
    if rng.random() < p_2to2 and U2.shape[1] >= 2:
        rr = U2.shape[1]
        for _ in range(flipgraph_attempts):
            i, j = rng.choice(rr, size=2, replace=False)
            res = try_swap_2_to_2(U2, V2, W2, int(i), int(j))
            if res is not None:
                U2, V2, W2 = res
                break

    # (8) NEW: Flip-graph 4-to-3 (rank reduction by 1; replaces 4 cols with 3).
    if rng.random() < p_4to3 and U2.shape[1] >= 4:
        rr = U2.shape[1]
        for _ in range(flipgraph_attempts):
            i, j, k, l = rng.choice(rr, size=4, replace=False)
            res = try_reduce_4_to_3(U2, V2, W2, int(i), int(j), int(k), int(l))
            if res is not None:
                U2, V2, W2 = res
                break

    return U2, V2, W2


# Stats counter for which mutation actually fired (so we can report).
class FireCounter:
    def __init__(self):
        self.n_3to2 = 0
        self.n_2to2 = 0
        self.n_4to3 = 0


def mutate_v2_with_counter(U, V, W, rng, counter: FireCounter,
                           p_bitflip=0.01, p_col_zero=0.03, p_col_replace=0.05,
                           p_col_swap=0.10, p_cancel_check=0.40,
                           p_drop_zero_check=0.40, p_3to2=0.10, p_2to2=0.10,
                           p_4to3=0.10, flipgraph_attempts=5):
    """Same as mutate_v2 but increments counter when a flip-graph move fires."""
    U2 = U.copy(); V2 = V.copy(); W2 = W.copy()
    r = U2.shape[1]

    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_bitflip
        M[mask] ^= 1

    if rng.random() < p_col_zero and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = 0; V2[:, col] = 0; W2[:, col] = 0

    if rng.random() < p_col_replace and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)
        V2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)
        W2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)

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
        U2, V2, W2 = cancel_duplicate_columns(U2, V2, W2)
    if rng.random() < p_drop_zero_check:
        U2, V2, W2 = drop_zero_columns(U2, V2, W2)

    if rng.random() < p_3to2 and U2.shape[1] >= 3:
        rr = U2.shape[1]
        for _ in range(flipgraph_attempts):
            i, j, k = rng.choice(rr, size=3, replace=False)
            res = try_reduce_3_to_2(U2, V2, W2, int(i), int(j), int(k))
            if res is not None:
                U2, V2, W2 = res
                counter.n_3to2 += 1
                break

    if rng.random() < p_2to2 and U2.shape[1] >= 2:
        rr = U2.shape[1]
        for _ in range(flipgraph_attempts):
            i, j = rng.choice(rr, size=2, replace=False)
            res = try_swap_2_to_2(U2, V2, W2, int(i), int(j))
            if res is not None:
                U2, V2, W2 = res
                counter.n_2to2 += 1
                break

    if rng.random() < p_4to3 and U2.shape[1] >= 4:
        rr = U2.shape[1]
        for _ in range(flipgraph_attempts):
            i, j, k, l = rng.choice(rr, size=4, replace=False)
            res = try_reduce_4_to_3(U2, V2, W2, int(i), int(j), int(k), int(l))
            if res is not None:
                U2, V2, W2 = res
                counter.n_4to3 += 1
                break

    return U2, V2, W2


def run_evolution_v2(
    n_generations: int = 500,
    population_size: int = 30,
    seed: int = 0,
    seed_known: bool = True,
    verbose: bool = True,
    rank_min_hard: int = RANK_MIN_THEORY,
):
    rng = np.random.default_rng(seed)
    archive = Archive(rank_min_hard=rank_min_hard)
    counter = FireCounter()

    if seed_known:
        for name, fn in [("naive_decomp", naive_decomp), ("laderman_decomp", laderman_decomp)]:
            U, V, W = fn()
            U, V, W = pad_genome(U, V, W)
            acc, cell = archive.submit(U, V, W)
            if verbose:
                print(f"  seed {name}: {'+' if acc else '='} cell={cell}")

    population = []
    base_U, base_V, base_W = pad_genome(*naive_decomp())
    for _ in range(population_size):
        U = base_U.copy(); V = base_V.copy(); W = base_W.copy()
        n_flips = int(rng.integers(1, 4))
        for _ in range(n_flips):
            which = rng.integers(0, 3)
            i = int(rng.integers(0, DIM))
            j = int(rng.integers(0, R_MAX))
            [U, V, W][which][i, j] ^= 1
        population.append((U, V, W))
        archive.submit(U, V, W)

    t0 = time.time()
    for gen in range(n_generations):
        if archive.cell_count() > 0 and rng.random() < 0.7:
            cells = list(archive.cells.values())
            info = cells[int(rng.integers(0, len(cells)))]
            U, V, W = info['U_c'], info['V_c'], info['W_c']
            U, V, W = pad_genome(U, V, W)
        else:
            idx = int(rng.integers(0, len(population)))
            U, V, W = population[idx]

        try:
            child = mutate_v2_with_counter(U, V, W, rng, counter)
            archive.submit(*child)
        except ForbiddenCellViolation as e:
            print(f"\n  *** HARD KILL at gen {gen}: {e}")
            return archive, counter

        if verbose and (gen + 1) % 100 == 0:
            elapsed = time.time() - t0
            mr = archive.min_rank_found()
            print(f"  gen {gen+1:5d}: cells={archive.cell_count()}, "
                  f"orbits={archive.orbit_count()}, valid={archive.total_valid}, "
                  f"min_rank={mr}, fires(3->2={counter.n_3to2}, 2->2={counter.n_2to2}, "
                  f"4->3={counter.n_4to3}), elapsed={elapsed:.1f}s")

    return archive, counter
