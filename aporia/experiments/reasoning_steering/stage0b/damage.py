"""Stage 0b Axis-2 damage scorer (RATIFIED metric, emit-schema freeze §3).

damage(coeffs, mahler) = -(EvidenceField Axis 2 battery-survival depth n_passed)
                       = -(number of falsifiers the candidate passed before kill).

Chain: DiscoveryPipeline.process_candidate -> .kill_vector
       -> build_evidence_field(kill_vector=...).battery_survival_depth.n_passed.

The pipeline is built once per scorer (in-memory SigmaKernel) and reused across
candidates. This is the only scalar the Hodge decomposer reads (as edge Delta-damage):
more survival (more falsifiers passed) => more negative damage => closer to a well.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from prometheus_math.discovery_pipeline import DiscoveryPipeline
from prometheus_math.evidence_field import build_evidence_field
from sigma_kernel.bind_eval import BindEvalExtension
from sigma_kernel.sigma_kernel import SigmaKernel

__all__ = ["Axis2Damage", "Axis2DamageScorer", "margins_from_kill_vector"]


def margins_from_kill_vector(kv) -> dict:
    """Per-falsifier margin vector {falsifier_name: float margin} from a KillVector.

    Drops components whose margin is None or non-finite. This is the per-state vector
    v(s) the relational flow (v0.3) compares pairwise.
    """
    components = getattr(kv, "components", None)
    if components is None:
        raise ValueError("kill_vector has no .components")
    out = {}
    for c in components:
        m = getattr(c, "margin", None)
        if m is None:
            continue
        mf = float(m)
        if not math.isfinite(mf):
            continue
        out[getattr(c, "falsifier_name", "?")] = mf
    return out


@dataclass(frozen=True)
class Axis2Damage:
    damage: int               # = -n_passed (non-positive)
    n_passed: int
    n_total: int
    passed: tuple
    failed: tuple


class Axis2DamageScorer:
    """Scores a polynomial's battery-survival-depth damage. Reusable across calls."""

    def __init__(self):
        kernel = SigmaKernel(":memory:")
        self._pipeline = DiscoveryPipeline(kernel=kernel, ext=BindEvalExtension(kernel))

    def score(self, coeffs, mahler: float) -> Axis2Damage:
        if not coeffs:
            raise ValueError("coeffs must be non-empty")
        if not math.isfinite(mahler):
            raise ValueError(f"mahler measure must be finite, got {mahler}")
        record = self._pipeline.process_candidate(list(coeffs), float(mahler))
        bsd = build_evidence_field(kill_vector=record.kill_vector).battery_survival_depth
        return Axis2Damage(
            damage=-int(bsd.n_passed),
            n_passed=int(bsd.n_passed),
            n_total=int(bsd.n_total),
            passed=tuple(bsd.falsifiers_passed),
            failed=tuple(bsd.falsifiers_failed),
        )

    def margin_vector(self, coeffs, mahler: float) -> dict:
        """Per-falsifier margin vector for a state (the v0.3 relational measurement)."""
        if not coeffs:
            raise ValueError("coeffs must be non-empty")
        if not math.isfinite(mahler):
            raise ValueError(f"mahler measure must be finite, got {mahler}")
        record = self._pipeline.process_candidate(list(coeffs), float(mahler))
        return margins_from_kill_vector(record.kill_vector)
