"""MAP-Elites for 2x2 matmul over F_3."""
from __future__ import annotations
import time
import numpy as np
from collections import defaultdict

from .core import MATMUL_T, reconstruct, is_matmul_decomp, DIM, N, P
from .gauge import canonicalize, effective_rank, stabilizer_order, ISO_SIZE
from .descriptors import (
    SPARSITY_BINS, RANK_MIN_THEORY, RANK_MAX_GRID, NAIVE_RANK,
    canonical_sparsity, sparsity_bin, stabilizer_bin, cell_of,
)
from .known_decomps import strassen_decomp, naive_decomp


R_MAX = 10


class ForbiddenCellViolation(Exception):
    pass


class Archive:
    def __init__(self, rank_min_hard: int = RANK_MIN_THEORY):
        self.cells: dict = {}
        self.hit_counts: dict = defaultdict(int)
        self.orbit_set: dict = defaultdict(set)
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
        if r_eff < self.rank_min_hard:
            raise ForbiddenCellViolation(
                f"canonical rank {r_eff} < {self.rank_min_hard} (Hopcroft-Kerr bound). "
                f"Canonicalizer failure."
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
    def orbit_count(self): return sum(len(s) for s in self.orbit_set.values())

    def cells_by_rank(self):
        out = defaultdict(list)
        for cell, info in self.cells.items():
            out[cell[0]].append((cell, info))
        return out

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


def random_genome(rng, r=R_MAX, density=0.4):
    """Random genome over F_3. Density = probability of nonzero entry."""
    def sample(shape):
        nz = rng.random(shape) < density
        vals = rng.integers(1, P, size=shape).astype(np.int8)
        return np.where(nz, vals, 0).astype(np.int8)
    return sample((DIM, r)), sample((DIM, r)), sample((DIM, r))


def pad_genome(U, V, W, r=R_MAX):
    cur = U.shape[1]
    if cur >= r:
        return U[:, :r].copy(), V[:, :r].copy(), W[:, :r].copy()
    z = np.zeros((DIM, r - cur), dtype=np.int8)
    return np.column_stack([U, z]), np.column_stack([V, z]), np.column_stack([W, z])


def mutate(U, V, W, rng,
           p_flip: float = 0.02,
           p_col_zero: float = 0.03,
           p_col_replace: float = 0.05,
           p_col_swap: float = 0.10):
    """F_3 mutation: ternary-flip entries (add delta in {1, 2} mod 3)."""
    U2 = U.copy(); V2 = V.copy(); W2 = W.copy()
    r = U2.shape[1]

    # Ternary flips per entry.
    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_flip
        deltas = rng.integers(1, P, size=M.shape).astype(np.int8)
        M[mask] = (M[mask] + deltas[mask]) % P

    if rng.random() < p_col_zero and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = 0; V2[:, col] = 0; W2[:, col] = 0

    if rng.random() < p_col_replace and r > 0:
        col = int(rng.integers(0, r))
        for M in (U2, V2, W2):
            for i in range(DIM):
                if rng.random() < 0.4:
                    M[i, col] = int(rng.integers(1, P))
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

    return U2, V2, W2


def run_evolution(
    n_generations: int = 1000,
    population_size: int = 40,
    seed: int = 0,
    seed_known: bool = True,
    verbose: bool = True,
):
    rng = np.random.default_rng(seed)
    archive = Archive()

    if seed_known:
        for name, fn in [("naive_decomp", naive_decomp), ("strassen_decomp", strassen_decomp)]:
            U, V, W = fn()
            U, V, W = pad_genome(U, V, W)
            acc, cell = archive.submit(U, V, W)
            if verbose:
                print(f"  seed {name}: {'+' if acc else '='} cell={cell}")

    # Initialize population around Strassen (small perturbations).
    population = []
    base = list(strassen_decomp())
    base = pad_genome(*base)
    for _ in range(population_size):
        U = base[0].copy(); V = base[1].copy(); W = base[2].copy()
        nflips = int(rng.integers(1, 5))
        for _ in range(nflips):
            which = rng.integers(0, 3)
            i = int(rng.integers(0, DIM))
            j = int(rng.integers(0, R_MAX))
            delta = int(rng.integers(1, P))
            [U, V, W][which][i, j] = (int([U, V, W][which][i, j]) + delta) % P
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
            child = mutate(U, V, W, rng)
            archive.submit(*child)
        except ForbiddenCellViolation as e:
            print(f"\n  *** HARD KILL at gen {gen}: {e}")
            return archive

        if verbose and (gen + 1) % 500 == 0:
            elapsed = time.time() - t0
            print(f"  gen {gen+1:5d}: cells={archive.cell_count()}, "
                  f"orbits={archive.orbit_count()}, valid={archive.total_valid}, "
                  f"elapsed={elapsed:.1f}s")

    return archive
