"""7-axis metric schema for per-generator and per-batch yield."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GeneratorMetrics:
    """Per-generator yield over a batch."""

    generator_id: str
    records_emitted: int = 0
    wall_seconds: float = 0.0

    # 7 axes
    throughput: float = 0.0  # records / hour
    info_density_mean: float = 0.0  # 0..1, mean over emissions
    diversity_mean: float = 0.0  # 0..1, mean cosine distance from corpus
    build_cost_hours: float = 0.0  # one-time, declared by generator
    run_cost_per_claim: float = 0.0  # compute + tokens (estimated)
    novelty_estimate: float = 0.0  # heuristic, 0..1
    learner_delta_steps: int = 99  # lower = better; 1 = direct training record

    # Verdict breakdown
    kills: int = 0
    confirmations: int = 0
    inconclusive: int = 0
    errors: int = 0

    @property
    def yield_score(self) -> float:
        """Collapsed score for bandit. v0.1 formula:
        info_density × diversity × (1 / learner_delta_steps)
        """
        steps = max(self.learner_delta_steps, 1)
        return (
            self.info_density_mean
            * max(self.diversity_mean, 0.01)
            / steps
        )


@dataclass
class BatchMetrics:
    """Per-batch aggregate."""

    batch_id: str
    started_at: str = ""
    ended_at: str = ""
    duration_hours: float = 0.0
    active_generators: List[str] = field(default_factory=list)
    per_generator: Dict[str, GeneratorMetrics] = field(default_factory=dict)
    total_records: int = 0
    total_kills: int = 0
    total_confirmations: int = 0
    total_inconclusive: int = 0
    total_errors: int = 0

    def add(self, m: GeneratorMetrics) -> None:
        self.per_generator[m.generator_id] = m
        self.total_records += m.records_emitted
        self.total_kills += m.kills
        self.total_confirmations += m.confirmations
        self.total_inconclusive += m.inconclusive
        self.total_errors += m.errors
