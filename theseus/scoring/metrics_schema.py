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

    # Fire #62: lifetime exploration premium. 1 - (unique_sigs /
    # total_seen) from the signature_index. Probed at flush time by
    # daemon; cached here for serialization into the journal AND for
    # use in yield_score. c5 at ~9% lifetime saturation gets boost
    # `1 + alpha × 0.91`; saturated gens get boost ~1x. This is the
    # signal that lets the bandit actually distinguish explorers
    # from recyclers — single-batch novelty was too noisy.
    lifetime_saturation: float = -1.0  # -1.0 = unknown (legacy / no probe)

    @property
    def yield_score(self) -> float:
        """Collapsed score for bandit.

        Fire #62 formula (replaces Fire #59 rate-based):
          base = info_density × diversity × (1 / learner_delta_steps)
          exploration_boost = 1 + 5 × max(0, 1 - lifetime_saturation)
                              when lifetime_saturation in [0, 1]
                              else 1 (no signal)
          score = base × exploration_boost × (1 - 0.5 × dup_rate)

        Rationale (per Fire #61 falsification):
        - Rate-based novelty was too weak: 35 novel / 1.3M records
          gave boost 1.0003 — invisible to bandit hydration.
        - Lifetime saturation is a stable, accumulated signal: c5 at
          9% sat means it's CONSISTENTLY producing new shapes (not
          just one good batch).
        - 5x scale: c5 (sat=0.09) → boost 1 + 5×0.91 = 5.55x.
          Saturated gens (sat=1.0) → boost 1.0. The bandit gets a
          clear differentiator.
        - Backwards-compatible: lifetime_saturation default -1 (legacy
          history) reproduces the pre-#62 base × (1 - 0.5 × dup_rate)
          score.

        novelty_signatures field is preserved (informational; written
        to journal) but no longer drives the score.
        """
        steps = max(self.learner_delta_steps, 1)
        base = (
            self.info_density_mean
            * max(self.diversity_mean, 0.01)
            / steps
        )
        # Exploration premium from lifetime saturation
        if 0.0 <= self.lifetime_saturation <= 1.0:
            exploration_boost = 1.0 + 5.0 * (1.0 - self.lifetime_saturation)
        else:
            exploration_boost = 1.0  # no signal yet
        saturation_mult = max(0.0, 1.0 - 0.5 * self.dup_rate)
        return base * exploration_boost * saturation_mult


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
