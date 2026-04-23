"""
MAP-Elites on CP decompositions of the 2x2 matmul tensor over F_2.

Genome: (U, V, W) each (4, R_MAX) uint8 over {0, 1}. Effective rank
is the number of non-zero columns after gauge-canonicalization.

Fitness: binary — 1 iff the decomposition reconstructs MATMUL_T, else 0.
Only valid decompositions (fitness = 1) populate the archive.

Archive cell: (rank, sparsity_bin, stabilizer_bin). Each cell stores
one canonical representative; orbit-hit counts track how many raw
genomes canonicalized into each cell during evolution.

Mutation operators (all F_2 safe):
  - bit_flip: flip N random bits across U, V, W
  - column_zero: zero out a random column (decrements effective rank)
  - column_replace: replace a random column with a random {0,1}^12
"""
from __future__ import annotations
import time
import numpy as np
from collections import defaultdict

from .core import (
    MATMUL_T, reconstruct, is_matmul_decomp, decomp_to_bytes, sort_columns,
)
from .gauge import (
    ISO_SIZE, canonicalize, effective_rank, stabilizer_order,
)
from .descriptors import (
    SPARSITY_BINS, RANK_MIN, RANK_MAX,
    canonical_sparsity, sparsity_bin, stabilizer_bin, cell_of,
)
from .known_decomps import naive_decomp, strassen_decomp


DIM = 4
R_MAX = 12


class Archive:
    """MAP-Elites archive: cell -> (canonical_bytes, U_c, V_c, W_c, stab).

    Tracks orbit-hit counts per cell (how many distinct raw genomes landed
    here, counted by their canonical form).
    """

    def __init__(self):
        self.cells: dict[tuple[int, int, int], dict] = {}
        # cell -> count of raw-genome submissions that canonicalized here
        self.hit_counts: dict[tuple[int, int, int], int] = defaultdict(int)
        # cell -> set of distinct canonical hashes seen (tracks orbit count)
        self.orbit_set: dict[tuple[int, int, int], set] = defaultdict(set)
        self.total_submissions = 0
        self.total_valid = 0

    def submit(self, U: np.ndarray, V: np.ndarray, W: np.ndarray) -> tuple[bool, tuple | None]:
        """Try to add a candidate to the archive.

        Returns (accepted, cell_coords). accepted=True iff the candidate is
        a valid matmul decomposition AND its cell was previously empty
        (under the same canonical form) OR it's a new canonical form in the cell.
        """
        self.total_submissions += 1
        if not is_matmul_decomp(U, V, W):
            return False, None
        self.total_valid += 1

        (U_c, V_c, W_c), bkey = canonicalize(U, V, W)
        stab = stabilizer_order(U_c, V_c, W_c)
        cell = cell_of(U_c, V_c, W_c, stab)

        self.hit_counts[cell] += 1
        self.orbit_set[cell].add(bkey)

        # Single-elite-per-cell (the first canonical form to occupy wins;
        # subsequent different canonical forms are tracked in orbit_set).
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

    def cell_count(self) -> int:
        return len(self.cells)

    def orbit_count(self) -> int:
        """Total distinct orbits across all cells."""
        return sum(len(s) for s in self.orbit_set.values())

    def cells_by_rank(self) -> dict[int, list]:
        """Group cells by effective rank."""
        out = defaultdict(list)
        for cell, info in self.cells.items():
            out[cell[0]].append((cell, info))
        return out

    def summary_lines(self) -> list[str]:
        lines = []
        lines.append(f"Archive: {self.cell_count()} cells, {self.orbit_count()} distinct orbits")
        lines.append(f"  submissions: {self.total_submissions}, valid: {self.total_valid}, "
                     f"fitness rate: {self.total_valid / max(1, self.total_submissions):.4f}")
        by_rank = self.cells_by_rank()
        for r in sorted(by_rank):
            n_cells = len(by_rank[r])
            n_orbits = sum(len(self.orbit_set[c]) for c, _ in by_rank[r])
            hits = sum(self.hit_counts[c] for c, _ in by_rank[r])
            lines.append(f"  rank {r}: {n_cells} cells, {n_orbits} distinct orbits, "
                         f"{hits} hits")
        return lines


# -----------------------------------------------------------------------------
# Genome operations
# -----------------------------------------------------------------------------

def random_genome(rng: np.random.Generator, r: int = R_MAX, density: float = 0.5):
    """Random dense genome at fixed rank r (may have zero columns => effective rank < r)."""
    U = (rng.random((DIM, r)) < density).astype(np.uint8)
    V = (rng.random((DIM, r)) < density).astype(np.uint8)
    W = (rng.random((DIM, r)) < density).astype(np.uint8)
    return U, V, W


def pad_genome(U: np.ndarray, V: np.ndarray, W: np.ndarray, r: int = R_MAX):
    """Pad a genome to the full R_MAX rank with zero columns (so shapes match)."""
    cur = U.shape[1]
    if cur >= r:
        return U[:, :r].copy(), V[:, :r].copy(), W[:, :r].copy()
    z = np.zeros((DIM, r - cur), dtype=np.uint8)
    return (np.column_stack([U, z]),
            np.column_stack([V, z]),
            np.column_stack([W, z]))


def mutate(U: np.ndarray, V: np.ndarray, W: np.ndarray,
           rng: np.random.Generator,
           p_bitflip: float = 0.04,
           p_col_zero: float = 0.02,
           p_col_replace: float = 0.05):
    """Apply randomized mutation. Returns a new (U, V, W)."""
    U2 = U.copy(); V2 = V.copy(); W2 = W.copy()
    r = U2.shape[1]

    # Bit flips across all three factor matrices.
    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_bitflip
        M[mask] ^= 1

    # Zero out a random column (decrement effective rank).
    if rng.random() < p_col_zero:
        col = int(rng.integers(0, r))
        U2[:, col] = 0; V2[:, col] = 0; W2[:, col] = 0

    # Replace a random column with a fresh random vector.
    if rng.random() < p_col_replace:
        col = int(rng.integers(0, r))
        U2[:, col] = (rng.random(DIM) < 0.5).astype(np.uint8)
        V2[:, col] = (rng.random(DIM) < 0.5).astype(np.uint8)
        W2[:, col] = (rng.random(DIM) < 0.5).astype(np.uint8)

    return U2, V2, W2


# -----------------------------------------------------------------------------
# Evolution loop
# -----------------------------------------------------------------------------

def run_evolution(
    n_generations: int = 500,
    population_size: int = 60,
    seed: int = 0,
    seed_known: bool = True,
    verbose: bool = True,
):
    """Run MAP-Elites for tensor-decomposition search over F_2, 2x2 matmul."""
    rng = np.random.default_rng(seed)
    archive = Archive()

    # Seed with known decompositions.
    if seed_known:
        for decomp_fn in (strassen_decomp, naive_decomp):
            U, V, W = decomp_fn()
            U, V, W = pad_genome(U, V, W)
            accepted, cell = archive.submit(U, V, W)
            if verbose:
                tag = "+" if accepted else "="
                print(f"  seed {decomp_fn.__name__}: {tag} cell={cell}")

    # Initialize random population.
    population = []
    for _ in range(population_size):
        U, V, W = random_genome(rng)
        population.append((U, V, W))
        archive.submit(U, V, W)

    # Evolution loop.
    t0 = time.time()
    for gen in range(n_generations):
        # Pick a parent: from archive (70%) or random population (30%).
        if archive.cell_count() > 0 and rng.random() < 0.7:
            cells = list(archive.cells.values())
            parent_info = cells[int(rng.integers(0, len(cells)))]
            # reconstruct genome from canonical form (pad to R_MAX)
            U, V, W = parent_info['U_c'], parent_info['V_c'], parent_info['W_c']
            U, V, W = pad_genome(U, V, W)
        else:
            idx = int(rng.integers(0, len(population)))
            U, V, W = population[idx]

        child = mutate(U, V, W, rng)
        archive.submit(*child)

        # Report periodically.
        if verbose and (gen + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  gen {gen+1:4d}: cells={archive.cell_count()}, "
                  f"orbits={archive.orbit_count()}, valid={archive.total_valid}, "
                  f"subs={archive.total_submissions}, elapsed={elapsed:.1f}s")

    return archive
