"""Sprint-1 ablation harnesses (Phase 2, ITER-45 - ITER-54).

Each experiment is a self-contained module that:
  - defines its hypothesis + metric + pass threshold (from the
    roadmap v2 doc; not re-derived per iteration)
  - ships the harness to compute the metric
  - records a SprintResult that the ITER-55 verdict tabulates

Per Doctrine v1.0 §"the kill condition": if Sprint-1 fails >= 4
of 10 experiments, the architecture is paused per v3 section 6.
This is the architecture's own falsification route.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SprintResult:
    """One Sprint-1 experiment's verdict + supporting data.

    Attributes:
        experiment_id: "A1" through "A10".
        hypothesis: one-line summary of what was tested.
        metric_name: short metric label.
        metric_value: numeric value of the metric.
        pass_threshold: the pre-committed numeric threshold.
        comparator: ">" / "<" / ">=" / "<=" — how to compare value
            to threshold.
        passed: True iff the comparator returns true.
        notes: human-readable supporting context (sample size,
            run parameters, qualifications).
        protocol_summary: 1-2 line summary of what was actually
            measured.
    """
    experiment_id: str
    hypothesis: str
    metric_name: str
    metric_value: float
    pass_threshold: float
    comparator: str
    passed: bool
    protocol_summary: str
    notes: str = ""

    def verdict_string(self) -> str:
        """One-line summary for the Sprint-1 findings ledger."""
        return (
            f"{self.experiment_id}: {'PASS' if self.passed else 'FAIL'} "
            f"({self.metric_name} = {self.metric_value:.4f} "
            f"{self.comparator} {self.pass_threshold:.4f})"
        )
