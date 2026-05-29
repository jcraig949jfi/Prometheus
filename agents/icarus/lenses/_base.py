"""
Icarus Lens base class + LensReport schema.

A Lens observes a cycle from one specific perspective. It does NOT decide.
It produces characterized information (typed signal vectors + confidence +
qualitative read) that an Integrator later synthesizes.

The crucial design principle: lens outputs are PRESERVED even when the
cycle is parked. The cycle directory becomes a multi-perspective record,
not a pass/fail audit trail.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any


# The 5 axes lenses score along. Each axis is 0.0-1.0; 0=worst, 1=best.
# - tier_proximity: how close is current code to passing the tier target?
# - novelty: how genuinely new vs. derivative is the proposal?
# - regression_risk: how likely is this change to break lower-tier capabilities?
#                    (HIGH SCORE = LOW RISK; inverted so all axes "more is better")
# - structural_simplicity: how clean/minimal is the change relative to its gain?
# - evidence_quality: how well-supported is the proposal by tests/data/probes?
SCORING_AXES = (
    "tier_proximity",
    "novelty",
    "regression_risk",
    "structural_simplicity",
    "evidence_quality",
)


@dataclass
class LensReport:
    """Typed output of one lens's observation of one cycle."""
    lens_name: str
    model_used: str
    cycle_n: int
    ts: str
    qualitative_summary: str
    axes: dict[str, float]  # keyed by SCORING_AXES; values 0.0-1.0
    confidence: float  # 0.0-1.0; how confident is THIS lens in its own read
    key_observations: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    minority_position: Optional[str] = None  # used by Skeptic
    raw_response_excerpt: Optional[str] = None  # for debugging
    error: Optional[str] = None  # if lens failed to produce a real report
    tokens_used: int = 0
    cost_estimate_usd: float = 0.0
    extra: dict = field(default_factory=dict)  # lens-specific structured payload

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LensReport":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore
        return cls(**{k: v for k, v in d.items() if k in known})

    @classmethod
    def empty_with_error(cls, lens_name: str, cycle_n: int, error: str,
                          model_used: str = "unknown") -> "LensReport":
        """Construct an error report. Returned when a lens fails -- the
        Integrator still gets a typed object to integrate."""
        return cls(
            lens_name=lens_name,
            model_used=model_used,
            cycle_n=cycle_n,
            ts=_now_iso(),
            qualitative_summary=f"[lens_error] {error}",
            axes={a: 0.5 for a in SCORING_AXES},  # neutral
            confidence=0.0,
            error=error,
        )


@dataclass
class CycleContext:
    """Shared context passed to every lens. Lenses populate fields as they
    run, so downstream lenses can read upstream outputs."""
    cycle_n: int
    source_dir: Path
    tier_target: str
    tier_challenge: dict
    last_stable_id: str
    recent_parks: list[dict] = field(default_factory=list)
    wisdom: str = ""
    # Variation-seeding signal. One of: "minimal", "structural", "exploratory".
    # Generator + Diagnostician inject a strategy-specific suffix into their
    # prompts. Rotating per cycle exposes which kinds of moves the panel
    # rewards/punishes -- empirical data for the v3 design.
    cycle_strategy: str = "structural"
    # Failure-direction (failure must emit direction): the current tier's probe
    # schema (proactive) + the prior cycle's actual candidate exception
    # (reactive). Surfaced to the Generator so a crash/wrong-field becomes a
    # navigable signal instead of a silent tdd_failed.
    tier_probe_schema: Optional[dict] = None
    last_failure_direction: Optional[dict] = None

    # Populated as the panel runs:
    diagnostician_report: Optional[LensReport] = None
    historian_report: Optional[LensReport] = None
    generator_report: Optional[LensReport] = None
    proposed_diff: Optional[str] = None
    diff_applied: bool = False
    apply_result: Optional[dict] = None
    tdd_result: Optional[dict] = None
    contract_report: Optional[dict] = None       # deterministic Contract Lens output
    contract_lens_report: Optional[LensReport] = None
    skeptic_report: Optional[LensReport] = None
    integrator_report: Optional[LensReport] = None
    # Open Skeptic/Contract debts inherited from prior cycles (mandatory follow-up)
    open_debts: list = field(default_factory=list)


class Lens(ABC):
    """Base class for all lenses. Subclass and implement observe()."""
    name: str = "lens_base"
    model_preference: str = "claude"  # "claude" | "gemini" | "deepseek"

    @abstractmethod
    def observe(self, ctx: CycleContext) -> LensReport:
        """Observe the cycle from this lens's perspective. Return a typed
        LensReport. MUST NOT raise -- catch internal exceptions and return
        LensReport.empty_with_error()."""
        raise NotImplementedError


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_lens_report(report: LensReport, cycle_dir: Path) -> Path:
    """Persist a LensReport to cycles/cycle_N/lenses/<name>.json."""
    lens_dir = cycle_dir / "lenses"
    lens_dir.mkdir(parents=True, exist_ok=True)
    out = lens_dir / f"{report.lens_name}.json"
    try:
        out.write_text(json.dumps(report.to_dict(), indent=2, default=str),
                       encoding="utf-8")
    except Exception as e:
        print(f"[lens] write {out} failed: {e}", file=sys.stderr)
    return out


def read_lens_report(cycle_dir: Path, lens_name: str) -> Optional[LensReport]:
    p = cycle_dir / "lenses" / f"{lens_name}.json"
    if not p.exists():
        return None
    try:
        return LensReport.from_dict(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return None


def axes_summary(reports: list[LensReport]) -> dict:
    """Compute consensus + disagreement per axis across multiple lens reports."""
    summary = {}
    for axis in SCORING_AXES:
        vals = [r.axes.get(axis, 0.5) for r in reports if not r.error]
        if not vals:
            summary[axis] = {"mean": 0.5, "spread": 0.0, "n": 0}
            continue
        mean = sum(vals) / len(vals)
        spread = max(vals) - min(vals)
        summary[axis] = {
            "mean": round(mean, 3),
            "spread": round(spread, 3),
            "n": len(vals),
        }
    return summary


def lens_agreement_patterns(reports: list[LensReport]) -> dict:
    """Identify which axes the lenses agree on (low spread) vs disagree on
    (high spread). Spread threshold of 0.3 is the boundary."""
    axes = axes_summary(reports)
    all_agree_positive = []
    all_agree_negative = []
    disagreement_axes = []
    for axis, data in axes.items():
        if data["n"] < 2:
            continue
        if data["spread"] <= 0.3:
            if data["mean"] >= 0.6:
                all_agree_positive.append(axis)
            elif data["mean"] <= 0.4:
                all_agree_negative.append(axis)
        else:
            disagreement_axes.append(axis)
    return {
        "all_agree_positive": all_agree_positive,
        "all_agree_negative": all_agree_negative,
        "disagreement_axes": disagreement_axes,
        "axes_detail": axes,
    }
