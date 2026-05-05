"""Mutation operators for TT rank profiles.

The Phase 2/3 operator perturbs a single bond by +/-1. Total rank moves
with parameter count, which is why (log_params, log_error) collapsed to
a 1D ridge on frontier functions.

Phase 4 adds a rank-shift operator that transfers rank BETWEEN bonds,
leaving the total approximately constant. This drives variance along
rank_entropy / rank_concentration without inflating the parameter budget.

Default strategy: hybrid(p_shift=0.5) — half of mutations are classical
single-bond perturbations (drive the params axis), half are rank shifts
(drive the shape axis).
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class MutationConfig:
    strategy: str = "hybrid"  # "classical" | "rank_shift" | "hybrid"
    p_shift: float = 0.5      # probability of rank-shift under hybrid
    shift_magnitude: int = 1  # amount transferred between bonds (default 1)


def _clamp(ranks: list[int], rank_ceiling: tuple[int, ...], max_bond: int) -> list[int]:
    return [max(1, min(max_bond, rank_ceiling[i], r)) for i, r in enumerate(ranks)]


def _mutate_classical(ranks: tuple[int, ...], rng: np.random.Generator,
                      rank_ceiling: tuple[int, ...], max_bond: int) -> tuple[int, ...]:
    r = list(ranks)
    idx = int(rng.integers(0, len(r)))
    delta = int(rng.choice([-1, +1]))
    r[idx] += delta
    r = _clamp(r, rank_ceiling, max_bond)
    return tuple(r)


def _mutate_rank_shift(ranks: tuple[int, ...], rng: np.random.Generator,
                       rank_ceiling: tuple[int, ...], max_bond: int,
                       shift_magnitude: int = 1) -> tuple[int, ...]:
    """Pick two distinct bonds; decrement one, increment the other by the same
    amount. If the donor bond would go below 1, fall back to classical +/-1.
    """
    r = list(ranks)
    if len(r) < 2:
        return _mutate_classical(ranks, rng, rank_ceiling, max_bond)
    a, b = rng.choice(len(r), size=2, replace=False)
    a, b = int(a), int(b)
    # donor = a, receiver = b
    if r[a] - shift_magnitude < 1:
        # Fallback: classical mutation if donor can't afford
        return _mutate_classical(ranks, rng, rank_ceiling, max_bond)
    r[a] -= shift_magnitude
    r[b] += shift_magnitude
    r = _clamp(r, rank_ceiling, max_bond)
    return tuple(r)


def mutate(ranks: tuple[int, ...], rng: np.random.Generator,
           rank_ceiling: tuple[int, ...], max_bond: int,
           config: MutationConfig | None = None) -> tuple[int, ...]:
    config = config or MutationConfig()
    if config.strategy == "classical":
        return _mutate_classical(ranks, rng, rank_ceiling, max_bond)
    if config.strategy == "rank_shift":
        return _mutate_rank_shift(ranks, rng, rank_ceiling, max_bond,
                                  shift_magnitude=config.shift_magnitude)
    # hybrid
    if rng.random() < config.p_shift:
        return _mutate_rank_shift(ranks, rng, rank_ceiling, max_bond,
                                  shift_magnitude=config.shift_magnitude)
    return _mutate_classical(ranks, rng, rank_ceiling, max_bond)
