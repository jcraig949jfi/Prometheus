"""MAP-Elites with LLM mutation alongside local mutation, on the polymul-n3
substrate over F_2.

Differences from sibling pilot_polymul_n3:
  - At each generation, with probability P_LLM_MUT, instead of (or in addition
    to) the local mutation, call llm_mutate on the parent. The Archive tracks
    which discoveries came from LLM proposals.
  - A BudgetCounter caps total LLM API calls (default 100/run for two-run
    side-by-side; default 200 if only one LLM run).
  - When the budget is exhausted, the loop falls back to local mutation only.

Hypothesis under test:
  Wrapping LLM mutation in a MAP-Elites archive surfaces additional orbits
  beyond what local mutation found in pilot_polymul_n3 (12 sub-optimal
  orbits at rank 9 on the same substrate).

NOT under test (out of scope for this pilot's budget):
  Whether LLM mutation can find rank < 6 (would beat Karatsuba — too high
  a bar at this budget; AlphaEvolve already operates in this space).
"""
from __future__ import annotations

import time
from typing import Optional

import numpy as np

from ..pilot_polymul_n3.core import (
    POLYMUL_T, DIM_AB, DIM_C, is_polymul_decomp,
)
from ..pilot_polymul_n3.gauge import (
    GAUGE_SIZE, canonicalize, effective_rank, stabilizer_order,
)
from ..pilot_polymul_n3.descriptors import (
    RANK_MIN_HARD, NAIVE_RANK, canonical_sparsity, sparsity_bin,
    stabilizer_bin, cell_of,
)
from ..pilot_polymul_n3.known_decomps import naive_decomp, karatsuba6_decomp
from ..pilot_polymul_n3.map_elites import (
    Archive, ForbiddenCellViolation, R_MAX,
    random_genome, pad_genome, mutate,
)

from .llm_mutate import BudgetCounter, llm_mutate, make_client


class LLMArchive(Archive):
    """Archive that tracks which orbits were discovered via LLM proposals."""

    def __init__(self, rank_min_hard: int = RANK_MIN_HARD):
        super().__init__(rank_min_hard=rank_min_hard)
        # Maps cell -> set of bkeys discovered via LLM proposals.
        self.llm_orbits: dict = {}
        # Counts of LLM-proposed candidates: (valid, novel-cell, novel-orbit).
        self.llm_valid = 0
        self.llm_novel_cell = 0
        self.llm_novel_orbit = 0

    def submit_with_source(self, U, V, W, source: str):
        """Submit a candidate and tag its source ('local' or 'llm')."""
        # Pre-compute orbit key to detect novelty *for this archive*.
        self.total_submissions += 1
        if not is_polymul_decomp(U, V, W):
            if source == "llm":
                pass  # invalidity already counted via budget.record_validity
            return False, None, False

        self.total_valid += 1
        if source == "llm":
            self.llm_valid += 1

        (U_c, V_c, W_c), bkey = canonicalize(U, V, W)
        r_eff = effective_rank(U_c, V_c, W_c)
        if r_eff < self.rank_min_hard:
            raise ForbiddenCellViolation(
                f"canonical rank {r_eff} < {self.rank_min_hard}. "
                f"Canonicalizer or fitness bug — investigate before continuing."
            )
        stab = stabilizer_order(U_c, V_c, W_c)
        cell = cell_of(U_c, V_c, W_c, stab)

        is_new_orbit = bkey not in self.orbit_set[cell]
        is_new_cell = cell not in self.cells

        self.hit_counts[cell] += 1
        self.orbit_set[cell].add(bkey)

        if cell not in self.cells:
            self.cells[cell] = {
                "bkey": bkey,
                "U_c": U_c, "V_c": V_c, "W_c": W_c,
                "stab": stab,
                "rank": cell[0],
                "sparsity": canonical_sparsity(U_c, V_c, W_c),
            }
            new_cell_added = True
        else:
            new_cell_added = False

        if source == "llm":
            if is_new_cell:
                self.llm_novel_cell += 1
            if is_new_orbit:
                self.llm_novel_orbit += 1
                self.llm_orbits.setdefault(cell, set()).add(bkey)

        return new_cell_added, cell, is_new_orbit

    def llm_summary_lines(self) -> list:
        return [
            f"LLM-attributed: {self.llm_valid} valid candidates, "
            f"{self.llm_novel_cell} new cells, "
            f"{self.llm_novel_orbit} new orbits",
        ]


def run_evolution_llm(
    n_generations: int = 1000,
    population_size: int = 50,
    seed: int = 0,
    seed_known: bool = True,
    p_llm_mut: float = 0.07,           # ~7% of mutations go through the LLM
    llm_budget: int = 100,             # hard cap on LLM API calls
    use_llm: bool = True,              # off => baseline; on => LLM-augmented
    verbose: bool = True,
    log_path: Optional[str] = None,
):
    rng = np.random.default_rng(seed)
    archive = LLMArchive()
    budget = BudgetCounter(max_calls=llm_budget if use_llm else 0)

    client = None
    if use_llm:
        try:
            client = make_client()
        except Exception as e:                 # noqa: BLE001
            print(f"  WARN: failed to construct LLM client ({type(e).__name__}: {e}); "
                  "falling back to baseline.")
            client = None
            use_llm = False

    # Seed with known decompositions.
    if seed_known:
        for name, fn in [("naive_decomp", naive_decomp),
                         ("karatsuba6_decomp", karatsuba6_decomp)]:
            U, V, W = fn()
            U, V, W = pad_genome(U, V, W)
            acc, cell, _ = archive.submit_with_source(U, V, W, "local")
            if verbose:
                print(f"  seed {name}: {'+' if acc else '='} cell={cell}")

    # Initialize population: half random, half perturbations of seeds.
    population = []
    base_kar = list(karatsuba6_decomp())
    base_kar = list(pad_genome(*base_kar))
    for _ in range(population_size // 2):
        U, V, W = random_genome(rng)
        population.append((U, V, W))
        archive.submit_with_source(U, V, W, "local")
    for _ in range(population_size - population_size // 2):
        U = base_kar[0].copy(); V = base_kar[1].copy(); W = base_kar[2].copy()
        nflips = int(rng.integers(1, 5))
        for _ in range(nflips):
            which = int(rng.integers(0, 3))
            mat = (U, V, W)[which]
            i = int(rng.integers(0, mat.shape[0]))
            j = int(rng.integers(0, mat.shape[1]))
            mat[i, j] ^= 1
        population.append((U, V, W))
        archive.submit_with_source(U, V, W, "local")

    t0 = time.time()
    for gen in range(n_generations):
        # Pick parent: archive elite (70%) or population (30%).
        if archive.cell_count() > 0 and rng.random() < 0.7:
            cells = list(archive.cells.values())
            info = cells[int(rng.integers(0, len(cells)))]
            U, V, W = info["U_c"], info["V_c"], info["W_c"]
            U, V, W = pad_genome(U, V, W)
        else:
            idx = int(rng.integers(0, len(population)))
            U, V, W = population[idx]

        # Decide LLM vs local.
        use_llm_this_gen = (
            use_llm
            and client is not None
            and budget.can_call()
            and rng.random() < p_llm_mut
        )

        try:
            if use_llm_this_gen:
                cand = llm_mutate(U, V, W, client, budget, log_path=log_path)
                if cand is None:
                    # API or parse failure; fall back to local.
                    child = mutate(U, V, W, rng)
                    archive.submit_with_source(*child, source="local")
                else:
                    valid = is_polymul_decomp(*cand)
                    budget.record_validity(valid)
                    new_cell, cell, novel_orbit = archive.submit_with_source(
                        *cand, source="llm"
                    )
                    if novel_orbit:
                        budget.record_novel_orbit()
            else:
                child = mutate(U, V, W, rng)
                archive.submit_with_source(*child, source="local")
        except ForbiddenCellViolation as e:
            print(f"\n  *** HARD KILL at gen {gen}: {e}")
            return archive, budget

        if verbose and (gen + 1) % 250 == 0:
            elapsed = time.time() - t0
            bsum = budget.summary()
            print(
                f"  gen {gen+1:5d}: cells={archive.cell_count()}, "
                f"orbits={archive.orbit_count()}, "
                f"valid={archive.total_valid}, "
                f"llm_used={bsum['api_attempts']}/{bsum['api_attempts'] + bsum['budget_remaining']}, "
                f"elapsed={elapsed:.1f}s"
            )

    return archive, budget
