"""MAP-Elites evolutionary loop.

Each individual is a rank tuple. Mutation = perturb one bond rank by +/-1.
Evaluation = TT-SVD at those ranks, optionally refined by a constrained
ALS sweep budget (Phase 2), then placed in the grid.

Constraint on refinement (per James 2026-04-24): keep n_sweeps small
(default 1) and apply uniformly to every evaluation. Per-elite
optimization budgets that vary across cells would turn the archive
into a measurement of "where did we spend compute" rather than
"which approximations exist."
"""
import numpy as np
from dataclasses import dataclass

from ..functions.base import ZooFunction
from ..tt.core import tt_svd, relative_l2_error, max_possible_ranks
from ..tt.als import tt_evaluate_with_refinement
from .grid import Archive, Elite, GridSpec


@dataclass
class LoopConfig:
    n_generations: int = 50
    n_initial: int = 8         # seed ranks
    max_bond: int = 32         # hard ceiling on per-bond rank
    seed: int = 20260424
    als_sweeps: int = 0        # P2: number of ALS sweeps per evaluation (0 = TT-SVD only)


def _evaluate(func: ZooFunction, dense: np.ndarray, ranks: tuple[int, ...],
              generation: int, spec: GridSpec, als_sweeps: int = 0) -> Elite:
    """Run TT-SVD (and optional ALS refinement) at the requested ranks."""
    if als_sweeps > 0:
        tt, err_before, err = tt_evaluate_with_refinement(
            dense, ranks, n_sweeps=als_sweeps,
        )
        extras = {
            "rel_error_before_refine": err_before,
            "rel_error_after_refine": err,
            "refinement_gain": float(err_before - err),
            "als_sweeps": als_sweeps,
        }
    else:
        tt = tt_svd(dense, max_ranks=ranks)
        err = relative_l2_error(dense, tt.reconstruct())
        extras = None

    n_params = tt.n_params
    cell = spec.cell(n_params, err)
    return Elite(
        function_label=func.label,
        ranks=tt.ranks,
        n_params=n_params,
        rel_error=err,
        cell=cell,
        generation=generation,
        extras=extras,
    )


def _mutate(ranks: tuple[int, ...], rng: np.random.Generator,
            rank_ceiling: tuple[int, ...], max_bond: int) -> tuple[int, ...]:
    r = list(ranks)
    # Flip a coin on direction, pick one bond
    idx = int(rng.integers(0, len(r)))
    delta = int(rng.choice([-1, +1]))
    r[idx] = max(1, min(max_bond, rank_ceiling[idx], r[idx] + delta))
    return tuple(r)


def _seed_ranks(n_bonds: int, rank_ceiling: tuple[int, ...], max_bond: int,
                n_initial: int, rng: np.random.Generator) -> list[tuple[int, ...]]:
    """Seed with a log-spaced rank sweep so the initial population spans compression regimes."""
    caps = [min(max_bond, c) for c in rank_ceiling]
    # Uniform ranks at log-spaced levels
    levels = np.unique(np.round(np.logspace(0, np.log10(max(2, max(caps))),
                                            num=n_initial)).astype(int))
    seeds = []
    for lvl in levels:
        seeds.append(tuple(min(lvl, c) for c in caps))
    while len(seeds) < n_initial:
        seeds.append(tuple(int(rng.integers(1, c + 1)) for c in caps))
    return seeds[:n_initial]


def run(func: ZooFunction, config: LoopConfig | None = None,
        spec: GridSpec | None = None) -> Archive:
    config = config or LoopConfig()
    spec = spec or GridSpec()
    rng = np.random.default_rng(config.seed)

    dense = func.sample()
    rank_ceiling = max_possible_ranks(func.shape)
    archive = Archive(function_label=func.label, spec=spec)

    # Seed population
    seeds = _seed_ranks(len(rank_ceiling), rank_ceiling, config.max_bond,
                        config.n_initial, rng)
    population: list[tuple[int, ...]] = []
    for g, ranks in enumerate(seeds):
        elite = _evaluate(func, dense, ranks, generation=g, spec=spec,
                          als_sweeps=config.als_sweeps)
        archive.try_place(elite)
        population.append(elite.ranks)

    # Evolve
    for g in range(config.n_initial, config.n_generations):
        if archive.cells:
            parents = list(archive.cells.values())
            parent_ranks = parents[int(rng.integers(0, len(parents)))].ranks
        else:
            parent_ranks = population[-1]
        child_ranks = _mutate(parent_ranks, rng, rank_ceiling, config.max_bond)
        elite = _evaluate(func, dense, child_ranks, generation=g, spec=spec,
                          als_sweeps=config.als_sweeps)
        archive.try_place(elite)

    return archive
