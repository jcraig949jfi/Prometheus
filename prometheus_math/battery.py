"""Battery strength — how many members of a falsification battery actually discriminate.

Motivated by cycle 028's audit of `discovery_pipeline`'s kill path, where two of four checks
returned the same verdict for every candidate measured.

The distinction this module exists to make precise is between a battery's **advertised** size —
how many checks it contains — and its **measured** discriminating size — how many of them
separate any pair of candidates. A member that returns the same verdict for everything
contributes zero bits and is observationally identical to a member that is not there. That is
canon R11's hedging forecaster, relocated from forecasting to falsification.

Two things this deliberately does NOT do.

It does not call a non-firing member useless. A check guarding a rare failure mode has zero
resolution until the rare failure arrives, and that is correct behaviour. What it reports is a
measurement over the candidates actually seen, which is why `n_candidates` is part of the result.

And it does not distinguish a member that CANNOT fire from one that merely HAS not. That
distinction is structural rather than statistical — it needs the member's source, not more
samples — and cycle 028 found both kinds in one battery. `member_resolution` measures; deciding
which kind you have is a reading task.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, List, Mapping, Sequence

from prometheus_math.partition import entropy, induced_partition

__all__ = ["member_resolution", "BatteryStrength", "battery_strength", "BatteryError"]


class BatteryError(ValueError):
    """Raised when the verdict table cannot support a strength measurement."""


def _validate(verdicts: Mapping[str, Sequence[Hashable]]) -> int:
    if not verdicts:
        raise BatteryError("a battery with no members has no strength to measure")
    lengths = {len(v) for v in verdicts.values()}
    if len(lengths) != 1:
        raise BatteryError(f"members disagree on candidate count: {sorted(lengths)}")
    n = lengths.pop()
    if n == 0:
        raise BatteryError(
            "no candidates: a battery's strength over an empty set is undefined, not zero")
    return n


def member_resolution(verdicts: Mapping[str, Sequence[Hashable]]) -> Dict[str, float]:
    """Bits each member contributes over the candidate set — the entropy of its verdict column.

    Zero exactly when the member returned the same verdict for every candidate.
    """
    n = _validate(verdicts)
    return {name: entropy(induced_partition(list(range(n)), lambda i, col=col: col[i]), n)
            for name, col in verdicts.items()}


@dataclass(frozen=True)
class BatteryStrength:
    """Advertised size against measured discriminating size."""

    n_candidates: int
    resolution: Dict[str, float]

    @property
    def advertised(self) -> int:
        return len(self.resolution)

    @property
    def discriminating(self) -> int:
        return sum(1 for bits in self.resolution.values() if bits > 1e-12)

    @property
    def silent_members(self) -> List[str]:
        return sorted(name for name, bits in self.resolution.items() if bits <= 1e-12)

    @property
    def total_bits(self) -> float:
        """Sum of member resolutions. An UPPER bound on the battery's joint discriminating
        power, not the power itself — correlated members double-count here."""
        return sum(self.resolution.values())

    def report(self) -> str:  # pragma: no cover - reporting only
        silent = ", ".join(self.silent_members) or "none"
        return (f"battery of {self.advertised} advertised, {self.discriminating} discriminating "
                f"over {self.n_candidates} candidates; silent: {silent}")


def battery_strength(verdicts: Mapping[str, Sequence[Hashable]]) -> BatteryStrength:
    """Measure a battery from its verdict table: {member name: verdict per candidate}."""
    n = _validate(verdicts)
    return BatteryStrength(n_candidates=n, resolution=member_resolution(verdicts))
