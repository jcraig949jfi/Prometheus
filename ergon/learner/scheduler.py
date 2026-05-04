"""ergon.learner.scheduler — operator-class scheduler with minimum-share enforcement.

Per pivot/ergon_learner_proposal_v8.md S3.5.4:

The scheduler decides which mutation operator class fires on each
episode. Default routing weights LLM-prior-shaped operators (neural,
external_llm) higher because they have stronger selection signal in
many domains. But that creates a failure mode: under cell-fill-rate
selection pressure, the non-prior operators (uniform, anti_prior,
structured_null) get squeezed out exactly when they're most needed for
exploration.

V8's mitigation: minimum-share enforcement at the SCHEDULER level (not
cell-selection level). Even when cell-fill metrics favor LLM-derived
operators, the scheduler reserves >=15% of episodes for non-prior
exploration:
  - uniform >=5%
  - anti_prior >=5%
  - structured_null >=5%

Plus coverage-pressure reweighting (per v8 S3.5.2): cells filled by
LLM-prior operators get downweighted in cell-selection. At MVP scope
(no neural/external_llm yet), this is a no-op until v0.5.

The scheduler exposes a single method `next_operator_class(episode_idx,
archive)` that returns the operator class to fire. The scheduler is
deterministic given the seed; reproducibility is a requirement for
substrate-grade pilots.
"""
from __future__ import annotations

import random
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional

from ergon.learner.archive import MAPElitesArchive
from ergon.learner.genome import MutationOperatorClass


# Per v8 S3.5.4: minimum proposal-share floors
DEFAULT_MIN_SHARES = {
    "uniform": 0.05,
    "anti_prior": 0.05,
    "structured_null": 0.05,
}


# Default operator weights at MVP (no neural / external_llm yet).
# Sum to 1.0; minimum-share enforcement adjusts dynamically.
DEFAULT_OPERATOR_WEIGHTS_MVP = {
    "structural": 0.50,
    "symbolic": 0.30,
    "uniform": 0.07,
    "structured_null": 0.07,
    "anti_prior": 0.06,
}


@dataclass
class SchedulerStats:
    """Per-window statistics for the scheduler's behavior.

    Used by Trial 2 acceptance check: `tertiary criterion: F_TRIVIAL_BAND_REJECT
    rate within [5%, 30%]; no axis with >70% concentration` and the per-
    operator min-share enforcement check.
    """
    episode_idx: int
    operator_call_counts: Dict[str, int] = field(default_factory=dict)
    minimum_share_violations: Dict[str, int] = field(default_factory=dict)
    coverage_pressure_active: bool = False


class OperatorScheduler:
    """Operator-class scheduler with minimum-share enforcement.

    Constructed with operator weights (default MVP weights). On each
    `next_operator_class` call:
      1. Check if any operator's actual share has fallen below its
         minimum (within the lookback window).
      2. If yes: force-select the under-shared operator.
      3. Otherwise: sample from the operator weight distribution.

    Lookback window default = 100 episodes. The scheduler tracks
    operator-class call counts in a sliding window so that minimum-share
    enforcement is local-temporal, not just cumulative-from-zero.
    """

    def __init__(
        self,
        operator_weights: Optional[Dict[MutationOperatorClass, float]] = None,
        min_shares: Optional[Dict[MutationOperatorClass, float]] = None,
        lookback_window: int = 100,
        seed: Optional[int] = None,
    ):
        self.operator_weights = dict(operator_weights or DEFAULT_OPERATOR_WEIGHTS_MVP)
        self.min_shares = dict(min_shares or DEFAULT_MIN_SHARES)
        self.lookback_window = lookback_window
        self._rng = random.Random(seed)

        # Sliding window of recent operator selections
        self._recent: Deque[MutationOperatorClass] = deque(maxlen=lookback_window)

        # Cumulative counts (for full-history reporting)
        self._cumulative_counts: Counter = Counter()

        # Validation: weights must sum to ~1.0; min_shares must sum to <= 1.0
        weight_sum = sum(self.operator_weights.values())
        if not 0.99 <= weight_sum <= 1.01:
            raise ValueError(
                f"operator_weights must sum to ~1.0; got {weight_sum:.3f}"
            )
        share_sum = sum(self.min_shares.values())
        if share_sum > 1.0:
            raise ValueError(
                f"sum of min_shares cannot exceed 1.0; got {share_sum:.3f}"
            )

    def next_operator_class(
        self,
        episode_idx: int = 0,
        archive: Optional[MAPElitesArchive] = None,
    ) -> MutationOperatorClass:
        """Return the next operator class to fire.

        Algorithm:
          1. If any operator with a min_share is under-shared in the
             current sliding window (and we're past warm-up), force-select it.
          2. Otherwise, sample from operator_weights distribution.
          3. Update sliding window + cumulative counts.

        Warm-up: for the first `lookback_window` episodes, no min-share
        enforcement (the window isn't full yet, so all min-share checks
        would trip incorrectly). Use weight-based sampling exclusively.
        """
        # Determine if any operator is under its min-share
        chosen: Optional[MutationOperatorClass] = None

        if len(self._recent) >= self.lookback_window:
            window_counts = Counter(self._recent)
            window_size = len(self._recent)
            for op, min_share in self.min_shares.items():
                actual_share = window_counts.get(op, 0) / window_size
                if actual_share < min_share:
                    # Force-select the most under-shared operator
                    if chosen is None or actual_share < (
                        window_counts.get(chosen, 0) / window_size
                    ):
                        chosen = op

        if chosen is None:
            # Weight-based sampling
            classes = list(self.operator_weights.keys())
            weights = list(self.operator_weights.values())
            chosen = self._rng.choices(classes, weights=weights, k=1)[0]

        # Update tracking
        self._recent.append(chosen)
        self._cumulative_counts[chosen] += 1

        return chosen

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def cumulative_shares(self) -> Dict[MutationOperatorClass, float]:
        """Cumulative share of each operator class across all episodes."""
        total = sum(self._cumulative_counts.values())
        if total == 0:
            return {}
        return {
            op: count / total
            for op, count in self._cumulative_counts.items()
        }

    def window_shares(self) -> Dict[MutationOperatorClass, float]:
        """Operator class shares within the current sliding window."""
        window_size = len(self._recent)
        if window_size == 0:
            return {}
        window_counts = Counter(self._recent)
        return {
            op: count / window_size
            for op, count in window_counts.items()
        }

    def check_min_share_compliance(self) -> Dict[MutationOperatorClass, Dict[str, float]]:
        """Per-operator min-share compliance check.

        Returns: op -> {min_share, actual_share, compliant}
        """
        windows = self.window_shares()
        out = {}
        for op, min_share in self.min_shares.items():
            actual = windows.get(op, 0.0)
            out[op] = {
                "min_share": min_share,
                "actual_share": actual,
                "compliant": actual >= min_share,
            }
        return out

    def stats(self, episode_idx: int) -> SchedulerStats:
        """Snapshot stats for diagnostics."""
        compliance = self.check_min_share_compliance()
        violations = {
            op: 1
            for op, info in compliance.items()
            if not info["compliant"]
        }
        return SchedulerStats(
            episode_idx=episode_idx,
            operator_call_counts=dict(self._cumulative_counts),
            minimum_share_violations=violations,
            coverage_pressure_active=False,  # v0.5+
        )
