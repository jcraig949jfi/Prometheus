"""MAP-Elites evolutionary loop.

Phase 4 additions:
  - Pluggable mutation operator (classical / rank_shift / hybrid) from
    zoo.map_elites.mutation.
  - Optional two-site DMRG refinement (rank-adaptive) replacing one-site
    ALS when dmrg_sweeps > 0.
  - Generalized GridSpec supporting arbitrary 2D placement descriptors.
"""
import numpy as np
from dataclasses import dataclass, field

from ..functions.base import ZooFunction
from ..tt.core import tt_svd, relative_l2_error, max_possible_ranks
from ..tt.als import tt_evaluate_with_refinement
from ..tt.dmrg import tt_evaluate_with_dmrg
from ..descriptors.rank_profile import rank_profile_summary
from .grid import Archive, Elite, GridSpec
from .mutation import MutationConfig, mutate


@dataclass
class LoopConfig:
    n_generations: int = 50
    n_initial: int = 8
    max_bond: int = 32
    seed: int = 20260424
    als_sweeps: int = 0          # one-site ALS; 0 disables
    dmrg_sweeps: int = 0         # two-site DMRG; 0 disables. Takes precedence over ALS.
    dmrg_rel_tol: float = 1e-10
    mutation: MutationConfig = field(default_factory=MutationConfig)
    seed_strategy: str = "uniform_log_spaced"  # or "diversified" (Phase 5)


def _evaluate(func: ZooFunction, dense: np.ndarray, ranks: tuple[int, ...],
              generation: int, spec: GridSpec, config: LoopConfig) -> Elite:
    """Evaluate at `ranks`, optionally refine, score, and record descriptors."""
    if config.dmrg_sweeps > 0:
        tt, err_before, err = tt_evaluate_with_dmrg(
            dense, ranks, n_sweeps=config.dmrg_sweeps,
            rel_tol=config.dmrg_rel_tol, max_bond=config.max_bond,
        )
        extras = {
            "rel_error_before_refine": err_before,
            "rel_error_after_refine": err,
            "refinement_gain": float(err_before - err),
            "refinement_kind": "dmrg_two_site",
            "refinement_sweeps": config.dmrg_sweeps,
            "requested_ranks": list(ranks),
        }
    elif config.als_sweeps > 0:
        tt, err_before, err = tt_evaluate_with_refinement(
            dense, ranks, n_sweeps=config.als_sweeps,
        )
        extras = {
            "rel_error_before_refine": err_before,
            "rel_error_after_refine": err,
            "refinement_gain": float(err_before - err),
            "refinement_kind": "als_one_site",
            "refinement_sweeps": config.als_sweeps,
            "requested_ranks": list(ranks),
        }
    else:
        tt = tt_svd(dense, max_ranks=ranks)
        err = relative_l2_error(dense, tt.reconstruct())
        extras = {
            "refinement_kind": "none",
            "refinement_gain": 0.0,
            "requested_ranks": list(ranks),
        }

    # Descriptors from the OUTPUT ranks (two-site DMRG may have adapted them)
    extras.update(rank_profile_summary(tt.ranks))

    n_params = tt.n_params

    # Build an Elite pre-cell so the grid can read extras for placement
    elite = Elite(
        function_label=func.label,
        ranks=tt.ranks,
        n_params=n_params,
        rel_error=err,
        cell=(0, 0),
        generation=generation,
        extras=extras,
    )
    elite.cell = spec.cell_from_elite(elite)
    return elite


def _seed_ranks_uniform_log(rank_ceiling: tuple[int, ...], max_bond: int,
                            n_initial: int, rng: np.random.Generator) -> list[tuple[int, ...]]:
    caps = [min(max_bond, c) for c in rank_ceiling]
    levels = np.unique(np.round(np.logspace(0, np.log10(max(2, max(caps))),
                                            num=n_initial)).astype(int))
    seeds = []
    for lvl in levels:
        seeds.append(tuple(min(lvl, c) for c in caps))
    while len(seeds) < n_initial:
        seeds.append(tuple(int(rng.integers(1, c + 1)) for c in caps))
    return seeds[:n_initial]


def _seed_ranks_diversified(rank_ceiling: tuple[int, ...], max_bond: int,
                            n_initial: int, rng: np.random.Generator) -> list[tuple[int, ...]]:
    """Phase 5 seed strategy: mix of uniform / peaked / bimodal profiles to
    cover the entropy axis from the start.

    Splits n_initial into three groups:
      - uniform: (k, k, ..., k) at log-spaced k. Entropy near max.
      - peaked: rank concentrated at one bond, others at 1. Entropy near min.
      - bimodal: alternating high-low. Intermediate entropy.
    """
    caps = [min(max_bond, c) for c in rank_ceiling]
    n_bonds = len(caps)
    n_uniform = max(1, n_initial // 3)
    n_peaked = max(1, n_initial // 3)
    n_bimodal = n_initial - n_uniform - n_peaked

    seeds: list[tuple[int, ...]] = []

    # Uniform group
    levels = np.unique(np.round(np.logspace(0, np.log10(max(2, max(caps))),
                                            num=n_uniform)).astype(int))
    for lvl in levels[:n_uniform]:
        seeds.append(tuple(min(int(lvl), c) for c in caps))

    # Peaked group: rotate the peak across bonds
    for i in range(n_peaked):
        peak_idx = i % n_bonds
        prof = [1] * n_bonds
        prof[peak_idx] = caps[peak_idx]
        seeds.append(tuple(prof))

    # Bimodal group: alternating high-low with shifting phase
    for i in range(n_bimodal):
        shift = i % 2
        prof = []
        for k in range(n_bonds):
            if (k + shift) % 2 == 0:
                prof.append(caps[k])
            else:
                prof.append(1)
        seeds.append(tuple(prof))

    while len(seeds) < n_initial:
        seeds.append(tuple(int(rng.integers(1, c + 1)) for c in caps))

    return seeds[:n_initial]


def _seed_ranks(rank_ceiling: tuple[int, ...], max_bond: int,
                n_initial: int, rng: np.random.Generator,
                strategy: str = "uniform_log_spaced") -> list[tuple[int, ...]]:
    if strategy == "diversified":
        return _seed_ranks_diversified(rank_ceiling, max_bond, n_initial, rng)
    return _seed_ranks_uniform_log(rank_ceiling, max_bond, n_initial, rng)


def run(func: ZooFunction, config: LoopConfig | None = None,
        spec: GridSpec | None = None) -> Archive:
    config = config or LoopConfig()
    spec = spec or GridSpec()
    rng = np.random.default_rng(config.seed)

    dense = func.sample()
    rank_ceiling = max_possible_ranks(func.shape)
    archive = Archive(function_label=func.label, spec=spec)

    seeds = _seed_ranks(rank_ceiling, config.max_bond, config.n_initial, rng,
                        strategy=config.seed_strategy)
    for g, ranks in enumerate(seeds):
        elite = _evaluate(func, dense, ranks, generation=g, spec=spec, config=config)
        archive.try_place(elite)

    for g in range(config.n_initial, config.n_generations):
        if archive.cells:
            parents = list(archive.cells.values())
            parent_ranks = parents[int(rng.integers(0, len(parents)))].ranks
        else:
            parent_ranks = seeds[-1]
        child_ranks = mutate(parent_ranks, rng, rank_ceiling,
                             config.max_bond, config.mutation)
        elite = _evaluate(func, dense, child_ranks, generation=g, spec=spec, config=config)
        archive.try_place(elite)

    return archive
