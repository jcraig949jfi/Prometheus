"""
Gradient Tracker — Multi-angle accumulation and gradient tracking for
the exploration protocol reform.

Receives coupling measurements from explore_ungated() across multiple
scorers and resolution levels. Determines which domain pairs earn
prosecution (full battery testing) based on:

1. Consistency: Do multiple scorers agree on sign? (AlignmentCoupling required)
2. Gradient: Does coupling increase with resolution? (positive slope = real signal)
3. Prosecution rate cap: No more than 20% of explored pairs pass.

Design approved via Agora adversarial review (Kairos + Claude_M1).
Constraint: AlignmentCoupling must be one of the agreeing scorers
(cosine and distributional are correlated through magnitude sensitivity).
"""
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class DomainPairMeasurement:
    """All measurements for a single domain pair across scorers and resolutions."""
    domain_a: str
    domain_b: str
    # scorer_name -> resolution -> coupling_score
    scores: dict[str, dict[int, float]] = field(default_factory=dict)

    def add(self, scorer: str, resolution: int, score: float):
        if scorer not in self.scores:
            self.scores[scorer] = {}
        self.scores[scorer][resolution] = score

    @property
    def scorers(self) -> list[str]:
        return list(self.scores.keys())

    def gradient(self, scorer: str) -> Optional[float]:
        """Compute slope of coupling vs log(resolution) for a scorer.
        Positive slope = signal grows with more data = likely real."""
        pts = self.scores.get(scorer, {})
        if len(pts) < 2:
            return None
        resolutions = sorted(pts.keys())
        x = np.log(np.array(resolutions, dtype=float))
        y = np.array([pts[r] for r in resolutions], dtype=float)
        # Simple linear regression
        x_mean = x.mean()
        y_mean = y.mean()
        denom = ((x - x_mean) ** 2).sum()
        if denom < 1e-12:
            return 0.0
        slope = ((x - x_mean) * (y - y_mean)).sum() / denom
        return float(slope)

    def mean_score(self, scorer: str) -> float:
        """Mean coupling score across resolutions."""
        pts = self.scores.get(scorer, {})
        if not pts:
            return 0.0
        return float(np.mean(list(pts.values())))

    def sign_positive(self, scorer: str) -> bool:
        """Is the mean coupling score positive (above baseline)?"""
        return self.mean_score(scorer) > 0.0


@dataclass
class ProsecutionCandidate:
    """A domain pair that passed the gradient tracker and earned prosecution."""
    domain_a: str
    domain_b: str
    agreeing_scorers: list[str]
    alignment_agrees: bool
    mean_gradient: float
    mean_score: float
    priority: float  # Higher = more promising


class GradientTracker:
    """
    Accumulates multi-angle coupling measurements and determines which
    domain pairs earn prosecution through the full battery.

    Usage:
        tracker = GradientTracker()
        # Feed measurements from explore_ungated()
        for pair, scorer, resolution, score in measurements:
            tracker.record(pair[0], pair[1], scorer, resolution, score)
        # Get prosecution queue
        candidates = tracker.prosecution_queue()
    """

    ALIGNMENT_SCORER = "alignment"  # Must be one of the agreeing scorers
    MIN_AGREEING_SCORERS = 2
    MAX_PROSECUTION_RATE = 0.20  # 20% cap per approved spec

    def __init__(
        self,
        min_agreeing: int = 2,
        max_prosecution_rate: float = 0.20,
        require_alignment: bool = True,
    ):
        self.min_agreeing = min_agreeing
        self.max_prosecution_rate = max_prosecution_rate
        self.require_alignment = require_alignment
        self._measurements: dict[tuple[str, str], DomainPairMeasurement] = {}

    def _key(self, domain_a: str, domain_b: str) -> tuple[str, str]:
        """Canonical key for a domain pair (sorted)."""
        return tuple(sorted([domain_a, domain_b]))

    def record(self, domain_a: str, domain_b: str, scorer: str,
               resolution: int, score: float):
        """Record a single coupling measurement."""
        key = self._key(domain_a, domain_b)
        if key not in self._measurements:
            self._measurements[key] = DomainPairMeasurement(
                domain_a=key[0], domain_b=key[1]
            )
        self._measurements[key].add(scorer, resolution, score)

    def _evaluate_pair(self, m: DomainPairMeasurement) -> Optional[ProsecutionCandidate]:
        """Evaluate a single domain pair for prosecution eligibility."""
        # Check which scorers show positive signal
        agreeing = [s for s in m.scorers if m.sign_positive(s)]

        # Must have enough agreeing scorers
        if len(agreeing) < self.min_agreeing:
            return None

        # Alignment must be among the agreeing scorers
        alignment_agrees = self.ALIGNMENT_SCORER in agreeing
        if self.require_alignment and not alignment_agrees:
            return None

        # Compute gradients for agreeing scorers
        gradients = []
        for s in agreeing:
            g = m.gradient(s)
            if g is not None:
                gradients.append(g)

        # At least one scorer must show positive gradient
        mean_gradient = float(np.mean(gradients)) if gradients else 0.0
        if mean_gradient <= 0 and gradients:
            return None

        # Compute priority: product of mean score and mean gradient
        mean_score = float(np.mean([m.mean_score(s) for s in agreeing]))
        priority = mean_score * (1.0 + max(mean_gradient, 0.0))

        return ProsecutionCandidate(
            domain_a=m.domain_a,
            domain_b=m.domain_b,
            agreeing_scorers=agreeing,
            alignment_agrees=alignment_agrees,
            mean_gradient=mean_gradient,
            mean_score=mean_score,
            priority=priority,
        )

    def prosecution_queue(self) -> list[ProsecutionCandidate]:
        """
        Return ordered list of domain pairs that earned prosecution.

        Applies the 20% prosecution rate cap: if more pairs pass the
        threshold, only the top 20% by priority are returned.
        """
        candidates = []
        for m in self._measurements.values():
            c = self._evaluate_pair(m)
            if c is not None:
                candidates.append(c)

        # Sort by priority (highest first)
        candidates.sort(key=lambda c: c.priority, reverse=True)

        # Apply prosecution rate cap
        n_total = len(self._measurements)
        max_candidates = max(1, int(n_total * self.max_prosecution_rate))
        if len(candidates) > max_candidates:
            candidates = candidates[:max_candidates]

        return candidates

    def summary(self) -> str:
        """Human-readable summary of tracker state."""
        n_total = len(self._measurements)
        candidates = self.prosecution_queue()
        n_candidates = len(candidates)
        rate = n_candidates / max(n_total, 1)

        lines = [
            f"GradientTracker: {n_total} domain pairs measured",
            f"  Prosecution candidates: {n_candidates} ({rate:.1%} rate)",
            f"  Rate cap: {self.max_prosecution_rate:.0%}",
            f"  Require alignment: {self.require_alignment}",
            "",
        ]
        for c in candidates[:10]:  # Top 10
            lines.append(
                f"  {c.domain_a} <-> {c.domain_b}: "
                f"priority={c.priority:.4f}, gradient={c.mean_gradient:.4f}, "
                f"scorers={c.agreeing_scorers}"
            )
        if len(candidates) > 10:
            lines.append(f"  ... and {len(candidates) - 10} more")

        return "\n".join(lines)
