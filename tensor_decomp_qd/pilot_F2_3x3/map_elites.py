"""
MAP-Elites for 3x3 matmul over F_2.

Design notes (informed by the 2x2 pilot's outcome-B diagnosis):
- Simple bit-flip mutation failed on 2x2 because valid decompositions are
  Hamming-isolated. We expect the same failure mode at 3x3 if we use
  *only* bit-flip. So we add RANK-REDUCING mutations that preserve
  validity by construction:
     (a) detect_and_cancel_duplicates: if two columns have equal (a, b, c),
         over F_2 their sum cancels; drop both. (Rank -= 2.)
     (b) drop_zero_columns: if a column has a=0 OR b=0 OR c=0, it contributes
         nothing; drop it. (Rank -= 1.)
     (c) detect_equivalent_cancellation: if (a_i,b_i,c_i)=(a_j,b_j,c_j)
         across columns, same as (a).
- We also try **block-swap mutation**: swap two columns then apply bit-flip
  to the swapped region. Sometimes lands on a different validity basin.
- Hard kill: forbidden cells at rank < Blaeser's 19 (any archive canonical
  landing there triggers a halt — canonicalizer is wrong or lower bound is).

Fitness: binary (valid matmul decomp or not).
"""
from __future__ import annotations
import time
import numpy as np
from collections import defaultdict

from .core import (
    MATMUL_T, reconstruct, is_matmul_decomp, decomp_to_bytes, sort_columns,
    DIM, N,
)
from .gauge import (
    ISO_SIZE, canonicalize, effective_rank, stabilizer_order,
)
from .descriptors import (
    SPARSITY_BINS, RANK_MIN_THEORY, RANK_MAX_GRID, NAIVE_RANK,
    canonical_sparsity, sparsity_bin, stabilizer_bin, cell_of,
)
from .known_decomps import naive_decomp, laderman_decomp


R_MAX = 30   # genome rank cap


class ForbiddenCellViolation(Exception):
    """Raised if a canonical decomposition lands below Blaeser's rank bound."""


class Archive:
    def __init__(self, rank_min_hard: int = RANK_MIN_THEORY):
        self.cells: dict[tuple[int, int, int], dict] = {}
        self.hit_counts: dict[tuple[int, int, int], int] = defaultdict(int)
        self.orbit_set: dict[tuple[int, int, int], set] = defaultdict(set)
        self.total_submissions = 0
        self.total_valid = 0
        self.rank_min_hard = rank_min_hard

    def submit(self, U, V, W):
        self.total_submissions += 1
        if not is_matmul_decomp(U, V, W):
            return False, None
        self.total_valid += 1

        (U_c, V_c, W_c), bkey = canonicalize(U, V, W)
        r_eff = effective_rank(U_c, V_c, W_c)

        # Hard kill: canonical rank below known lower bound = canonicalizer bug.
        if r_eff < self.rank_min_hard:
            raise ForbiddenCellViolation(
                f"canonical rank {r_eff} < Blaeser bound {self.rank_min_hard}. "
                f"Treat as canonicalizer failure until proven otherwise."
            )

        stab = stabilizer_order(U_c, V_c, W_c)
        cell = cell_of(U_c, V_c, W_c, stab)
        self.hit_counts[cell] += 1
        self.orbit_set[cell].add(bkey)

        if cell not in self.cells:
            self.cells[cell] = {
                'bkey': bkey,
                'U_c': U_c, 'V_c': V_c, 'W_c': W_c,
                'stab': stab,
                'rank': cell[0],
                'sparsity': canonical_sparsity(U_c, V_c, W_c),
            }
            return True, cell
        return False, cell

    def cell_count(self): return len(self.cells)

    def orbit_count(self):
        return sum(len(s) for s in self.orbit_set.values())

    def cells_by_rank(self):
        out = defaultdict(list)
        for cell, info in self.cells.items():
            out[cell[0]].append((cell, info))
        return out

    def min_rank_found(self):
        return min((c[0] for c in self.cells), default=None)

    def summary_lines(self):
        lines = []
        lines.append(f"Archive: {self.cell_count()} cells, {self.orbit_count()} distinct orbits")
        lines.append(f"  submissions: {self.total_submissions}, valid: {self.total_valid}, "
                     f"rate: {self.total_valid / max(1, self.total_submissions):.5f}")
        by_rank = self.cells_by_rank()
        for r in sorted(by_rank):
            n_cells = len(by_rank[r])
            n_orbits = sum(len(self.orbit_set[c]) for c, _ in by_rank[r])
            hits = sum(self.hit_counts[c] for c, _ in by_rank[r])
            lines.append(f"  rank {r:2d}: {n_cells:2d} cells, {n_orbits:2d} orbits, "
                         f"{hits:5d} hits")
        return lines


# -----------------------------------------------------------------------------
# Genome helpers
# -----------------------------------------------------------------------------

def random_genome(rng, r=R_MAX, density=0.3):
    U = (rng.random((DIM, r)) < density).astype(np.uint8)
    V = (rng.random((DIM, r)) < density).astype(np.uint8)
    W = (rng.random((DIM, r)) < density).astype(np.uint8)
    return U, V, W


def pad_genome(U, V, W, r=R_MAX):
    cur = U.shape[1]
    if cur >= r:
        return U[:, :r].copy(), V[:, :r].copy(), W[:, :r].copy()
    z = np.zeros((DIM, r - cur), dtype=np.uint8)
    return np.column_stack([U, z]), np.column_stack([V, z]), np.column_stack([W, z])


# -----------------------------------------------------------------------------
# Mutation operators
# -----------------------------------------------------------------------------

def drop_zero_columns(U, V, W):
    """If a column has a=0 OR b=0 OR c=0, that outer product is 0; can drop.

    Returns potentially-smaller (U, V, W) with zero columns removed.
    """
    mask_zero = ((U.sum(0) == 0) | (V.sum(0) == 0) | (W.sum(0) == 0))
    if mask_zero.any():
        keep = ~mask_zero
        U = U[:, keep]; V = V[:, keep]; W = W[:, keep]
    return U, V, W


def cancel_duplicate_columns(U, V, W):
    """Over F_2, two identical columns (same a, b, c) sum to zero; drop both.

    Also catches columns that come in pairs where the contribution cancels
    symmetrically.
    """
    r = U.shape[1]
    # Find duplicates by hashing (a, b, c) columns.
    keys = []
    for k in range(r):
        keys.append(bytes(U[:, k].tobytes() + V[:, k].tobytes() + W[:, k].tobytes()))
    seen = {}
    to_drop = set()
    for i, key in enumerate(keys):
        if key in seen and seen[key] not in to_drop and i not in to_drop:
            to_drop.add(i); to_drop.add(seen[key])
            del seen[key]
        else:
            if key not in seen:
                seen[key] = i
    if to_drop:
        keep_mask = np.array([i not in to_drop for i in range(r)])
        U = U[:, keep_mask]; V = V[:, keep_mask]; W = W[:, keep_mask]
    return U, V, W


def mutate(U, V, W, rng,
           p_bitflip: float = 0.01,
           p_col_zero: float = 0.03,
           p_col_replace: float = 0.05,
           p_col_swap: float = 0.10,
           p_cancel_check: float = 0.40,
           p_drop_zero_check: float = 0.40):
    """Apply randomized mutation. Returns new (U, V, W)."""
    U2 = U.copy(); V2 = V.copy(); W2 = W.copy()
    r = U2.shape[1]

    # (1) Bit flips across factor matrices.
    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_bitflip
        M[mask] ^= 1

    # (2) Zero out a random column (so effective rank may drop if valid).
    if rng.random() < p_col_zero and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = 0; V2[:, col] = 0; W2[:, col] = 0

    # (3) Replace a random column.
    if rng.random() < p_col_replace and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)
        V2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)
        W2[:, col] = (rng.random(DIM) < 0.3).astype(np.uint8)

    # (4) Swap two columns' (a, b, c) components independently — may produce
    #     useful validity-preserving re-wirings.
    if rng.random() < p_col_swap and r >= 2:
        i, j = rng.choice(r, size=2, replace=False)
        # randomly swap a, b, or c components between columns (not all three).
        which = rng.integers(0, 3)
        if which == 0:
            U2[:, [i, j]] = U2[:, [j, i]]
        elif which == 1:
            V2[:, [i, j]] = V2[:, [j, i]]
        else:
            W2[:, [i, j]] = W2[:, [j, i]]

    # (5) Validity-preserving rank-reducers (applied after random moves):
    if rng.random() < p_cancel_check:
        U2, V2, W2 = cancel_duplicate_columns(U2, V2, W2)
    if rng.random() < p_drop_zero_check:
        U2, V2, W2 = drop_zero_columns(U2, V2, W2)

    return U2, V2, W2


# -----------------------------------------------------------------------------
# Evolution loop
# -----------------------------------------------------------------------------

def run_evolution(
    n_generations: int = 1000,
    population_size: int = 40,
    seed: int = 0,
    seed_known: bool = True,
    verbose: bool = True,
    rank_min_hard: int = RANK_MIN_THEORY,
):
    rng = np.random.default_rng(seed)
    archive = Archive(rank_min_hard=rank_min_hard)

    if seed_known:
        for name, fn in [("naive_decomp", naive_decomp), ("laderman_decomp", laderman_decomp)]:
            U, V, W = fn()
            U, V, W = pad_genome(U, V, W)
            acc, cell = archive.submit(U, V, W)
            if verbose:
                print(f"  seed {name}: {'+' if acc else '='} cell={cell}")

    # Initialize population with perturbations of naive decomp (higher base-rate
    # of landing valid neighbors than pure random).
    population = []
    base_U, base_V, base_W = pad_genome(*naive_decomp())
    for _ in range(population_size):
        # small perturbation of naive
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
        # Parent selection: 70% from archive, 30% from population.
        if archive.cell_count() > 0 and rng.random() < 0.7:
            cells = list(archive.cells.values())
            info = cells[int(rng.integers(0, len(cells)))]
            U, V, W = info['U_c'], info['V_c'], info['W_c']
            U, V, W = pad_genome(U, V, W)
        else:
            idx = int(rng.integers(0, len(population)))
            U, V, W = population[idx]

        try:
            child = mutate(U, V, W, rng)
            archive.submit(*child)
        except ForbiddenCellViolation as e:
            print(f"\n  *** HARD KILL at gen {gen}: {e}")
            print(f"      Archive state will be reported; canonicalizer must be audited.")
            return archive

        if verbose and (gen + 1) % 200 == 0:
            elapsed = time.time() - t0
            mr = archive.min_rank_found()
            print(f"  gen {gen+1:5d}: cells={archive.cell_count()}, "
                  f"orbits={archive.orbit_count()}, valid={archive.total_valid}, "
                  f"min_rank={mr}, elapsed={elapsed:.1f}s")

    return archive
