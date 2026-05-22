"""7-axis metric schema for per-generator and per-batch yield."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# field() is used below


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
    error_messages: List[str] = field(default_factory=list)

    # Saturation telemetry (Fire #46): dup_rate within this batch's
    # in-process dedup. High dup_rate = generator's claim space
    # exhausted; bandit will downweight in next fire. Surfaces the
    # saturation Penelope reports downstream as 90% duplicates.
    dup_rate: float = 0.0  # 0..1, fraction of attempted emits that
                            # were duplicates of earlier in-batch records

    # Fire #59: novelty contribution. Number of cross-batch-novel
    # signatures (per signature_index) attributed to this gen in
    # the batch that produced these metrics. Lets the bandit prefer
    # gens that contribute *new shapes* over gens that merely produce
    # *many records*. Default 0 = no signal (legacy / pre-#59 history).
    novelty_signatures: int = 0

    @property
    def yield_score(self) -> float:
        """Collapsed score for bandit.

        Fire #60 formula (extending Fire #59):
          base = info_density × diversity × (1 / learner_delta_steps)
          novelty_rate = novelty_signatures / max(records_emitted, 1)
          score = base × (1 + 10 × novelty_rate) × (1 - 0.5 × dup_rate)

        Rationale:
        - Novelty bonus (Fire #59): rewards gens contributing new shapes,
          not just records.
        - Dup-rate penalty (Fire #60): downweights saturated gens (d1
          hit 99.9% dup in Fire #59) without zeroing them out — at
          100% dup the multiplier is 0.5, so the gen still gets some
          exploration probability and can recover if its source
          catalog refreshes.
        - Backwards-compatible: novelty=0 + dup_rate=0 (defaults)
          reproduce the base score exactly.
        """
        steps = max(self.learner_delta_steps, 1)
        base = (
            self.info_density_mean
            * max(self.diversity_mean, 0.01)
            / steps
        )
        if self.records_emitted > 0:
            novelty_rate = self.novelty_signatures / self.records_emitted
        else:
            novelty_rate = 0.0
        novelty_mult = 1.0 + 10.0 * novelty_rate
        saturation_mult = max(0.0, 1.0 - 0.5 * self.dup_rate)
        return base * novelty_mult * saturation_mult


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
