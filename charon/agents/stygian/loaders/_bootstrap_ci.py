"""Nonparametric bootstrap CI primitive for composition loaders.

Per Erebos v3 Phase 1A ITER-33 + DR batch 2 convergence (graded
confidence > single point estimate). Used as a reusable Layer-1
sharpener for any loader that currently relies on a single
regression slope, mean, ratio, or scalar statistic and needs to
surface uncertainty into the seam.

Statistical contract:
- Resample the data WITH REPLACEMENT B times.
- Compute the statistic on each resample.
- Return percentile CI at the requested confidence level + the
  full bootstrap distribution (so downstream can compute coverage
  of specific thresholds).
- No parametric assumptions about the underlying distribution.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence


@dataclass(frozen=True)
class BootstrapCIResult:
    """Result of a nonparametric bootstrap.

    Attributes:
        statistic_observed: statistic computed on the original sample.
        statistic_distribution: B-element list of statistic values from
            the bootstrap resamples.
        ci_lower: lower bound of the percentile CI.
        ci_upper: upper bound of the percentile CI.
        confidence_level: requested confidence (e.g. 0.95).
        n_resamples: B (number of bootstrap samples actually drawn).
        n_sample: size of the original sample.
        seed: RNG seed used (None if entropy-driven).
        notes: optional human-readable string.
    """
    statistic_observed: Optional[float]
    statistic_distribution: list[float] = field(default_factory=list)
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    confidence_level: float = 0.95
    n_resamples: int = 0
    n_sample: int = 0
    seed: Optional[int] = None
    notes: str = ""

    def covers(self, value: float) -> bool:
        """True iff `value` is inside the CI [ci_lower, ci_upper]."""
        if self.ci_lower is None or self.ci_upper is None:
            return False
        return self.ci_lower <= value <= self.ci_upper

    def fraction_below(self, threshold: float) -> float:
        """Fraction of bootstrap statistics strictly below threshold."""
        if not self.statistic_distribution:
            return 0.0
        return sum(
            1 for s in self.statistic_distribution if s < threshold
        ) / len(self.statistic_distribution)

    def fraction_above(self, threshold: float) -> float:
        """Fraction of bootstrap statistics strictly above threshold."""
        if not self.statistic_distribution:
            return 0.0
        return sum(
            1 for s in self.statistic_distribution if s > threshold
        ) / len(self.statistic_distribution)


def bootstrap_ci(
    data: Sequence,
    statistic_fn: Callable[[Sequence], Optional[float]],
    n_resamples: int = 2000,
    confidence_level: float = 0.95,
    seed: Optional[int] = None,
) -> BootstrapCIResult:
    """Nonparametric bootstrap with percentile CI.

    Args:
        data: indexable sequence (list, tuple) — the original sample.
            Items can be anything; statistic_fn handles them.
        statistic_fn: callable taking the resample (same item type
            as data) and returning a float, or None if degenerate.
            None values are dropped from the bootstrap distribution
            (do NOT crash; failed resamples are simply omitted).
        n_resamples: B. Default 2000 — enough for stable percentile
            estimates at 95%; bump to 5000+ if going to 99%.
        confidence_level: e.g. 0.95 for a 2.5/97.5 percentile band.
        seed: optional RNG seed for reproducibility.

    Returns:
        BootstrapCIResult. If `data` is empty or has fewer than 2
        elements, returns a degenerate result with no CI.
    """
    n = len(data)
    if n < 2:
        return BootstrapCIResult(
            statistic_observed=None,
            n_sample=n,
            confidence_level=confidence_level,
            seed=seed,
            notes=f"bootstrap_ci: n={n} < 2; insufficient sample",
        )

    rng = random.Random(seed)

    statistic_observed = statistic_fn(data)

    distribution: list[float] = []
    for _ in range(n_resamples):
        resample = [data[rng.randrange(n)] for _ in range(n)]
        s = statistic_fn(resample)
        if s is not None and not (isinstance(s, float) and math.isnan(s)):
            distribution.append(float(s))

    if not distribution:
        return BootstrapCIResult(
            statistic_observed=statistic_observed,
            n_sample=n,
            n_resamples=n_resamples,
            confidence_level=confidence_level,
            seed=seed,
            notes=(
                "bootstrap_ci: all resamples produced None / NaN; "
                "no CI computable"
            ),
        )

    distribution.sort()
    alpha = 1.0 - confidence_level
    lo_pct = alpha / 2.0
    hi_pct = 1.0 - alpha / 2.0
    # Linear-interpolation percentile (matches numpy.percentile default)
    def _percentile(sorted_vals: list[float], p: float) -> float:
        if len(sorted_vals) == 1:
            return sorted_vals[0]
        idx = p * (len(sorted_vals) - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return sorted_vals[lo]
        frac = idx - lo
        return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac

    ci_lower = _percentile(distribution, lo_pct)
    ci_upper = _percentile(distribution, hi_pct)

    return BootstrapCIResult(
        statistic_observed=statistic_observed,
        statistic_distribution=distribution,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        confidence_level=confidence_level,
        n_resamples=len(distribution),
        n_sample=n,
        seed=seed,
        notes=(
            f"bootstrap_ci: B={len(distribution)}/{n_resamples} valid "
            f"resamples; percentile CI at confidence={confidence_level}"
        ),
    )
