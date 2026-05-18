"""Bandit ABC."""
from __future__ import annotations

import abc
from typing import Dict, List

from theseus.scoring.metrics_schema import GeneratorMetrics


class Bandit(abc.ABC):
    """Selects the next batch's active generator set given history."""

    @abc.abstractmethod
    def select(
        self,
        available: List[str],
        history: Dict[str, List[GeneratorMetrics]],
        n: int = 5,
    ) -> List[str]:
        """Pick `n` generator_ids from `available` given per-generator
        metric history (chronological list of past batch metrics).
        """

    @abc.abstractmethod
    def update(self, batch_metrics: Dict[str, GeneratorMetrics]) -> None:
        """Update internal state from a completed batch's metrics."""
