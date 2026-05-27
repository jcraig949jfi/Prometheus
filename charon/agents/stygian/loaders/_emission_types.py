"""Typed emission types for composition loaders.

Per Erebos v3 + DR amendment §3.4 (DR Anti-Pattern D: single-verdict
instead of curve). Loaders that operate over a parameter (G02 / G04
/ G10 / G16 / G17 / G23) should emit `SurvivalCurve` rather than the
single-verdict dict-based `BatteryLoaderResult` shape. The verdict
becomes a derived feature of the curve, not the primary output.

ITER-17 (G23 multi-law) and ITER-18 (G17 phase-transition sweep)
both informally produced curves. This module promotes the discipline
to substrate-level convention.

Backward-compat: SurvivalCurve.to_battery_result() converts to the
legacy dict shape the executor already consumes.

Reading: pivot/erebos_v3_amendment_dr_synthesis_2026-05-27.md §3.4
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass(frozen=True)
class SurvivalCurve:
    """First-class emission type for parameter-sweep loaders.

    The curve carries the FULL sweep result. The summary verdict is
    derived from the curve at the kill_pattern_registry's discretion,
    not invented by the loader.
    """
    parameter_name: str                 # e.g., "threshold_M"
    parameter_values: list[float]       # e.g., [1.20, 1.22, ..., 1.40]
    observed_values: list[float]        # per-parameter observed
    null_p05_values: list[float]        # per-parameter null lower bound
    null_p95_values: list[float]        # per-parameter null upper bound
    summary_verdict: str                # derived, not primary
    summary_kill_pattern: Optional[str] = None
    phase_transition_index: Optional[int] = None
    confidence_intervals: dict[str, tuple[float, float]] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        # Validate shape on construction so downstream consumers can
        # assume well-formedness.
        n = len(self.parameter_values)
        if len(self.observed_values) != n:
            raise ValueError(
                f"SurvivalCurve: observed_values length {len(self.observed_values)} "
                f"!= parameter_values length {n}"
            )
        if len(self.null_p05_values) != n:
            raise ValueError(
                f"SurvivalCurve: null_p05_values length {len(self.null_p05_values)} "
                f"!= parameter_values length {n}"
            )
        if len(self.null_p95_values) != n:
            raise ValueError(
                f"SurvivalCurve: null_p95_values length {len(self.null_p95_values)} "
                f"!= parameter_values length {n}"
            )
        if self.phase_transition_index is not None:
            if not (0 <= self.phase_transition_index < n):
                raise ValueError(
                    f"SurvivalCurve: phase_transition_index "
                    f"{self.phase_transition_index} out of bounds [0, {n})"
                )
        # CI validation: lo <= hi
        for key, (lo, hi) in self.confidence_intervals.items():
            if lo > hi:
                raise ValueError(
                    f"SurvivalCurve: CI for {key!r} has lo={lo} > hi={hi}"
                )

    def detect_phase_transition(
        self,
        outcome_predicate: Callable[[int], bool],
    ) -> Optional[int]:
        """Return the first index where the outcome predicate flips.

        outcome_predicate(idx) returns True if the curve "survives"
        at parameter_values[idx] (observed > null_p95) and False if
        it doesn't. Phase transition is the first index where the
        outcome changes from severable to surviving (or vice versa).
        """
        n = len(self.parameter_values)
        if n < 2:
            return None
        prev = outcome_predicate(0)
        for i in range(1, n):
            curr = outcome_predicate(i)
            if curr != prev:
                return i
            prev = curr
        return None

    def default_outcome_predicate(self, idx: int) -> bool:
        """Default: 'survives' = observed > null_p95.

        Loaders can supply a different predicate to detect_phase_transition;
        this is the substrate's default semantic."""
        return self.observed_values[idx] > self.null_p95_values[idx]

    def to_battery_result(self) -> dict:
        """Convert to the legacy BatteryLoaderResult dict shape for
        backward compatibility with the existing executor / kill_ledger.

        The curve is preserved in the `survival_curve` field; the
        derived summary verdict and kill_pattern are top-level for
        downstream consumers that only read the legacy shape.
        """
        return {
            "verdict": self.summary_verdict,
            "kill_pattern": self.summary_kill_pattern,
            "parameter_name": self.parameter_name,
            "n_parameter_values": len(self.parameter_values),
            "phase_transition_index": self.phase_transition_index,
            "phase_transition_value": (
                self.parameter_values[self.phase_transition_index]
                if self.phase_transition_index is not None else None
            ),
            "survival_curve": {
                "parameter_values": list(self.parameter_values),
                "observed_values": list(self.observed_values),
                "null_p05_values": list(self.null_p05_values),
                "null_p95_values": list(self.null_p95_values),
            },
            "confidence_intervals": dict(self.confidence_intervals),
            "notes": self.notes,
        }

    def summary_stats(self) -> dict:
        """Quick numerical summary for ledger inspection."""
        return {
            "max_observed": max(self.observed_values),
            "min_observed": min(self.observed_values),
            "max_gap_obs_vs_null_p95": max(
                obs - p95 for obs, p95 in zip(
                    self.observed_values, self.null_p95_values
                )
            ),
            "n_severable": sum(
                1 for i in range(len(self.parameter_values))
                if not self.default_outcome_predicate(i)
            ),
            "n_surviving": sum(
                1 for i in range(len(self.parameter_values))
                if self.default_outcome_predicate(i)
            ),
        }
