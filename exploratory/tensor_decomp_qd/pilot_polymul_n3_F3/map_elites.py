"""MAP-Elites on CP decompositions of polymul-3 over F_3.

Genome: (U, V, W) with U, V each (3, R_MAX) and W (5, R_MAX), entries in
{0, 1, 2}. Effective rank = #non-zero columns after gauge-canonicalization.
Fitness: binary 1 iff (U, V, W) reconstructs POLYMUL_T.

Mutation: ternary perturbations (e -> (e + delta) mod 3 with delta in {1, 2}).
"""
from __future__ import annotations
import time
import numpy as np
from collections import defaultdict

from .core import (
    POLYMUL_T, reconstruct, is_polymul_decomp, decomp_to_bytes,
    DIM_AB, DIM_C, P,
)
from .gauge import (
    GAUGE_SIZE, canonicalize, effective_rank, stabilizer_order,
)
from .descriptors import (
    SPARSITY_BINS, RANK_MIN_HARD, RANK_MAX_GRID, NAIVE_RANK,
    canonical_sparsity, sparsity_bin, stabilizer_bin, cell_of,
)
from .known_decomps import naive_decomp, karatsuba6_decomp


R_MAX = 12


class ForbiddenCellViolation(Exception):
    pass


class Archive:

    def __init__(self, rank_min_hard: int = RANK_MIN_HARD):
        self.cells: dict[tuple[int, int, int], dict] = {}
        self.hit_counts: dict[tuple[int, int, int], int] = defaultdict(int)
        self.orbit_set: dict[tuple[int, int, int], set] = defaultdict(set)
        self.total_submissions = 0
        self.total_valid = 0
        self.rank_min_hard = rank_min_hard

    def submit(self, U: np.ndarray, V: np.ndarray, W: np.ndarray):
        self.total_submissions += 1
        if not is_polymul_decomp(U, V, W):
            return False, None
        self.total_valid += 1

        (U_c, V_c, W_c), bkey = canonicalize(U, V, W)
        r_eff = effective_rank(U_c, V_c, W_c)
        if r_eff < self.rank_min_hard:
            raise ForbiddenCellViolation(
                f"canonical rank {r_eff} < {self.rank_min_hard} (polymul-3 F_3 hard floor). "
                f"Investigate before continuing."
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

    def cell_count(self) -> int:
        return len(self.cells)

    def orbit_count(self) -> int:
        return sum(len(s) for s in self.orbit_set.values())

    def cells_by_rank(self) -> dict[int, list]:
        out = defaultdict(list)
        for cell, info in self.cells.items():
            out[cell[0]].append((cell, info))
        return out

    def summary_lines(self) -> list[str]:
        lines = []
        lines.append(f"Archive: {self.cell_count()} cells, "
                     f"{self.orbit_count()} distinct orbits")
        lines.append(f"  submissions: {self.total_submissions}, "
                     f"valid: {self.total_valid}, "
                     f"rate: {self.total_valid / max(1, self.total_submissions):.5f}")
        by_rank = self.cells_by_rank()
        for r in sorted(by_rank):
            n_cells = len(by_rank[r])
            n_orbits = sum(len(self.orbit_set[c]) for c, _ in by_rank[r])
            hits = sum(self.hit_counts[c] for c, _ in by_rank[r])
            lines.append(f"  rank {r:2d}: {n_cells:2d} cells, "
                         f"{n_orbits:3d} orbits, {hits:6d} hits")
        return lines


# -----------------------------------------------------------------------------
# Genome operations (F_3)
# -----------------------------------------------------------------------------

def random_genome(rng: np.random.Generator, r: int = R_MAX, density: float = 0.5):
    """Random F_3-valued genome: each entry independently U(0,1,2) with
    prob (1 - density) zero, density/2 each of 1 and 2."""
    Us = rng.random((DIM_AB, r))
    Vs = rng.random((DIM_AB, r))
    Ws = rng.random((DIM_C, r))
    def _ternary(M):
        out = np.zeros_like(M, dtype=np.int8)
        out[M < density / 2] = 1
        out[(M >= density / 2) & (M < density)] = 2
        return out
    return _ternary(Us), _ternary(Vs), _ternary(Ws)


def pad_genome(U: np.ndarray, V: np.ndarray, W: np.ndarray, r: int = R_MAX):
    cur = U.shape[1]
    if cur >= r:
        return U[:, :r].copy(), V[:, :r].copy(), W[:, :r].copy()
    zU = np.zeros((DIM_AB, r - cur), dtype=np.int8)
    zV = np.zeros((DIM_AB, r - cur), dtype=np.int8)
    zW = np.zeros((DIM_C, r - cur), dtype=np.int8)
    return (np.column_stack([U, zU]),
            np.column_stack([V, zV]),
            np.column_stack([W, zW]))


def mutate(U, V, W, rng: np.random.Generator,
           p_perturb: float = 0.04,
           p_col_zero: float = 0.02,
           p_col_replace: float = 0.05,
           p_col_swap: float = 0.05,
           p_col_scale: float = 0.05):
    """Ternary perturbation: each entry has p_perturb chance of flipping by
    delta in {1, 2}. Plus column-level operations including F_3* scaling
    of the per-column gauge that's NORMALLY quotiented out — but we don't
    want that to be a free move; the canonicalizer will collapse it.
    """
    U2 = U.copy().astype(np.int8)
    V2 = V.copy().astype(np.int8)
    W2 = W.copy().astype(np.int8)
    r = U2.shape[1]

    for M in (U2, V2, W2):
        mask = rng.random(M.shape) < p_perturb
        delta = rng.integers(1, P, size=M.shape).astype(np.int8)
        M[mask] = (M[mask] + delta[mask]) % P

    if rng.random() < p_col_zero and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = 0
        V2[:, col] = 0
        W2[:, col] = 0

    if rng.random() < p_col_replace and r > 0:
        col = int(rng.integers(0, r))
        U2[:, col] = rng.integers(0, P, DIM_AB).astype(np.int8)
        V2[:, col] = rng.integers(0, P, DIM_AB).astype(np.int8)
        W2[:, col] = rng.integers(0, P, DIM_C).astype(np.int8)

    if rng.random() < p_col_swap and r >= 2:
        i, j = rng.choice(r, size=2, replace=False)
        which = int(rng.integers(0, 3))
        if which == 0:
            U2[:, [i, j]] = U2[:, [j, i]]
        elif which == 1:
            V2[:, [i, j]] = V2[:, [j, i]]
        else:
            W2[:, [i, j]] = W2[:, [j, i]]

    # F_3* per-column scaling — this is in the gauge we quotient out; it lets
    # the search explore equivalent forms cheaply.
    if rng.random() < p_col_scale and r > 0:
        col = int(rng.integers(0, r))
        which = int(rng.integers(0, 3))
        if which == 0:
            U2[:, col] = (2 * U2[:, col]) % P
            W2[:, col] = (2 * W2[:, col]) % P  # to keep contribution invariant
        elif which == 1:
            V2[:, col] = (2 * V2[:, col]) % P
            W2[:, col] = (2 * W2[:, col]) % P
        else:
            # Scale all of u, v by 2 then c by 2*2 = 4 = 1 (no change to c).
            U2[:, col] = (2 * U2[:, col]) % P
            V2[:, col] = (2 * V2[:, col]) % P

    return U2, V2, W2


# -----------------------------------------------------------------------------
# Evolution loop
# -----------------------------------------------------------------------------

def run_evolution(
    n_generations: int = 1500,
    population_size: int = 80,
    seed: int = 0,
    seed_known: bool = True,
    verbose: bool = True,
):
    rng = np.random.default_rng(seed)
    archive = Archive()

    if seed_known:
        for name, fn in [("naive_decomp", naive_decomp),
                         ("karatsuba6_decomp", karatsuba6_decomp)]:
            U, V, W = fn()
            U, V, W = pad_genome(U, V, W)
            acc, cell = archive.submit(U, V, W)
            if verbose:
                print(f"  seed {name}: {'+' if acc else '='} cell={cell}")

    population = []
    base_kar = list(karatsuba6_decomp())
    base_kar = list(pad_genome(*base_kar))
    for _ in range(population_size // 2):
        U, V, W = random_genome(rng)
        population.append((U, V, W))
        archive.submit(U, V, W)
    for _ in range(population_size - population_size // 2):
        U = base_kar[0].copy(); V = base_kar[1].copy(); W = base_kar[2].copy()
        nflips = int(rng.integers(1, 5))
        for _ in range(nflips):
            which = int(rng.integers(0, 3))
            mat = (U, V, W)[which]
            i = int(rng.integers(0, mat.shape[0]))
            j = int(rng.integers(0, mat.shape[1]))
            delta = int(rng.integers(1, P))
            mat[i, j] = (int(mat[i, j]) + delta) % P
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

        if verbose and (gen + 1) % 250 == 0:
            elapsed = time.time() - t0
            print(f"  gen {gen+1:5d}: cells={archive.cell_count()}, "
                  f"orbits={archive.orbit_count()}, valid={archive.total_valid}, "
                  f"elapsed={elapsed:.1f}s")

    return archive
