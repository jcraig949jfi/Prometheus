"""Epsilon-greedy bandit (v0.1 placeholder).

With probability epsilon: pick uniformly from never-fired or low-fire-
count generators (exploration). Otherwise: pick top-`n` by mean
yield_score (exploitation).

To replace with Thompson sampling / Bayesian bandit in Tier 1.
"""
from __future__ import annotations

import random
from typing import Dict, List

from theseus.bandit.base import Bandit
from theseus.scoring.metrics_schema import GeneratorMetrics


class EpsilonGreedyBandit(Bandit):
    def __init__(self, epsilon: float = 0.2, seed: int | None = None) -> None:
        self.epsilon = epsilon
        self._rng = random.Random(seed)
        self._history: Dict[str, List[float]] = {}

    def select(
        self,
        available: List[str],
        history: Dict[str, List[GeneratorMetrics]],
        n: int = 5,
    ) -> List[str]:
        if len(available) <= n:
            return list(available)

        # Update internal yield history from external history if provided
        for gid, ms in history.items():
            self._history.setdefault(gid, [])
            seen = len(self._history[gid])
            for m in ms[seen:]:
                self._history[gid].append(m.yield_score)

        # Exploration arm: include generators with fewest historical fires
        # Sort by fire count ascending; pick first n_explore
        n_explore = max(1, int(self.epsilon * n))
        fire_counts = sorted(
            available, key=lambda g: len(self._history.get(g, []))
        )
        exploration = fire_counts[:n_explore]

        # Exploitation arm: top yield_score among the rest
        remaining = [g for g in available if g not in exploration]

        def mean_yield(gid: str) -> float:
            ys = self._history.get(gid, [])
            return sum(ys) / max(len(ys), 1) if ys else 0.0

        exploitation = sorted(remaining, key=mean_yield, reverse=True)[
            : n - len(exploration)
        ]
        return exploration + exploitation

    def update(self, batch_metrics: Dict[str, GeneratorMetrics]) -> None:
        for gid, m in batch_metrics.items():
            self._history.setdefault(gid, []).append(m.yield_score)
