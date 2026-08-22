"""Calibration scoring — Brier, ECE, and Murphy's vector partition.

Canon v2.0 §3 names Brier scoring in the R11 entry ("report {solved / probable /
under-constrained} and be right about it (Brier-scored)"), so this is the primitive that rung
needs rather than a general-purpose statistics library.

The decomposition is the load-bearing part. A single number cannot separate the two ways a
forecaster fails, and the R11 circuits demonstrate both: a forecaster that always reports the
base rate is perfectly RELIABLE and carries no information, while one that is confidently wrong
is unreliable and informative. Murphy's partition splits the Brier score into exactly those
components.

Reference: A. H. Murphy, "A New Vector Partition of the Probability Score",
*Journal of Applied Meteorology* 12 (1973), 595–600.

    BS = reliability − resolution + uncertainty

Binning by *distinct forecast value* makes the identity exact rather than approximate, which is
why `murphy_decomposition` does that and `expected_calibration_error` takes a bin count instead.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

__all__ = ["brier_score", "expected_calibration_error", "murphy_decomposition",
           "MurphyPartition", "CalibrationError"]


class CalibrationError(ValueError):
    """Raised on inputs for which a calibration score is undefined."""


def _validate(forecasts: Sequence[float], outcomes: Sequence[int]) -> None:
    if len(forecasts) != len(outcomes):
        raise CalibrationError(
            f"{len(forecasts)} forecasts against {len(outcomes)} outcomes")
    if not forecasts:
        raise CalibrationError("no forecasts: a calibration score over nothing is not 0, "
                               "it is undefined")
    for p in forecasts:
        if not 0.0 <= p <= 1.0:
            raise CalibrationError(f"forecast {p} outside [0, 1]")
    for y in outcomes:
        if y not in (0, 1):
            raise CalibrationError(f"outcome {y!r} is not binary")


def brier_score(forecasts: Sequence[float], outcomes: Sequence[int]) -> float:
    """Mean squared error of probabilistic forecasts. Lower is better; range [0, 1].

    A PROPER scoring rule: it is minimised in expectation by reporting one's true belief, which
    is the property that makes it resistant to the hedging strategies a bare accuracy score
    rewards.
    """
    _validate(forecasts, outcomes)
    return sum((p - y) ** 2 for p, y in zip(forecasts, outcomes)) / len(forecasts)


def expected_calibration_error(forecasts: Sequence[float], outcomes: Sequence[int],
                               bins: int = 10) -> float:
    """Weighted mean gap between stated confidence and observed frequency, over `bins` bins.

    ECE is the metric the R11 traps are built to game, and it is included precisely so that the
    tests can show it being gamed: a forecaster that always reports the base rate scores ECE ≈ 0
    while carrying no information at all.
    """
    _validate(forecasts, outcomes)
    if bins < 1:
        raise CalibrationError(f"bins must be at least 1, got {bins}")
    n = len(forecasts)
    buckets: Dict[int, List[Tuple[float, int]]] = {}
    for p, y in zip(forecasts, outcomes):
        idx = min(int(p * bins), bins - 1)          # p == 1.0 belongs to the last bin
        buckets.setdefault(idx, []).append((p, y))
    total = 0.0
    for rows in buckets.values():
        mean_p = sum(p for p, _ in rows) / len(rows)
        mean_y = sum(y for _, y in rows) / len(rows)
        total += len(rows) * abs(mean_p - mean_y)
    return total / n


@dataclass(frozen=True)
class MurphyPartition:
    """Brier score split into its three components (Murphy 1973).

    reliability  — mean squared gap between forecast and observed frequency at that forecast.
                   0 is perfect. This is what "calibrated" means.
    resolution   — how far the conditional frequencies move away from the base rate. HIGHER is
                   better; 0 means the forecasts carry no information.
    uncertainty  — the base rate's own variance, ȳ(1−ȳ). A property of the battery, not of the
                   forecaster, and therefore not something a forecaster can be credited with.
    """

    brier: float
    reliability: float
    resolution: float
    uncertainty: float

    @property
    def identity_residual(self) -> float:
        """`brier − (reliability − resolution + uncertainty)`; exact to floating point."""
        return self.brier - (self.reliability - self.resolution + self.uncertainty)

    @property
    def skill(self) -> float:
        """Brier skill score against the base-rate forecaster: 1 is perfect, 0 is no better
        than always reporting the base rate, negative is worse than that.

        This is the number that separates the hedger from a real forecaster, and it is why
        reliability alone is never the R11 verdict.
        """
        if self.uncertainty == 0.0:
            raise CalibrationError(
                "skill is undefined on a degenerate battery (every outcome identical, so the "
                "base-rate forecaster is already perfect and there is nothing to be better "
                "than). Returning 0.0 here would read as 'no skill' — the fifth instance of the "
                "answering-outside-your-domain bug class, found cycle 039. Use "
                "`skill_or(default)` to opt in to a value explicitly.")
        return (self.resolution - self.reliability) / self.uncertainty

    def skill_or(self, default: float) -> float:
        """Explicit opt-in to a default when skill is undefined. Fine — the caller said so."""
        if self.uncertainty == 0.0:
            return default
        return (self.resolution - self.reliability) / self.uncertainty


def murphy_decomposition(forecasts: Sequence[float],
                         outcomes: Sequence[int]) -> MurphyPartition:
    """Partition the Brier score into reliability, resolution and uncertainty.

    Bins by DISTINCT FORECAST VALUE, which makes the identity exact:

        BS = reliability − resolution + uncertainty

    (With range-binning the identity only holds approximately, and a test that asserted it
    would be testing the bin count rather than the mathematics.)
    """
    _validate(forecasts, outcomes)
    n = len(forecasts)
    base = sum(outcomes) / n

    groups: Dict[float, List[int]] = {}
    for p, y in zip(forecasts, outcomes):
        groups.setdefault(p, []).append(y)

    reliability = resolution = 0.0
    for p, ys in groups.items():
        k = len(ys)
        mean_y = sum(ys) / k
        reliability += k * (p - mean_y) ** 2
        resolution += k * (mean_y - base) ** 2
    reliability /= n
    resolution /= n

    return MurphyPartition(
        brier=brier_score(forecasts, outcomes),
        reliability=reliability,
        resolution=resolution,
        uncertainty=base * (1.0 - base),
    )
