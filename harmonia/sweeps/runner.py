"""
Sweep runner — orchestrates Pattern 30, Pattern 20, Pattern 19 on a SIGNATURE.

Called by the ingestion path before any tensor mutation:
  agora.register_specimen.register() -> sweep_signature() -> BLOCK halts
  agora.tensor.push.push_tensor()    -> retrospective sweep on cell diffs

Each sweep returns an individual verdict; the runner merges them:
  any BLOCK => overall BLOCK
  any WARN => overall WARN (no BLOCK)
  all CLEAR => overall CLEAR

Override path: conductor can pass `override=True` with a justification
string; the sweep still runs and its output is recorded, but a BLOCK
does not halt the ingestion. Overrides are logged to sweep_results_log.md.
"""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from harmonia.sweeps.pattern_30 import (
    CouplingCheck,
    Pattern30Result,
    sweep as sweep_pattern_30,
)
from harmonia.sweeps.pattern_20 import (
    Pattern20Check,
    Pattern20Result,
    sweep as sweep_pattern_20,
)
from harmonia.sweeps.pattern_19 import (
    PriorRecord,
    NewMeasurement,
    Pattern19Result,
    sweep as sweep_pattern_19,
)


@dataclass
class SweepVerdict:
    pattern: str
    verdict: str            # CLEAR | WARN | BLOCK
    rationale: str
    details: dict = field(default_factory=dict)


@dataclass
class SweepOutcome:
    overall: str            # CLEAR | WARN | BLOCK
    verdicts: list
    blocked: bool
    warnings: list
    override: bool = False
    override_reason: str = ""
    at: str = ""

    def to_provenance_block(self) -> dict:
        return {
            "sweeps": [asdict(v) for v in self.verdicts],
            "overall": self.overall,
            "override": self.override,
            "override_reason": self.override_reason,
            "at": self.at,
        }


def _merge(verdicts: list) -> str:
    has_block = any(v.verdict == "BLOCK" for v in verdicts)
    has_warn = any(v.verdict == "WARN" for v in verdicts)
    if has_block:
        return "BLOCK"
    if has_warn:
        return "WARN"
    return "CLEAR"


def sweep_signature(
    coupling_check: Optional[CouplingCheck] = None,
    pattern20_check: Optional[Pattern20Check] = None,
    pattern19_new: Optional[NewMeasurement] = None,
    pattern19_prior: Optional[PriorRecord] = None,
    override: bool = False,
    override_reason: str = "",
) -> SweepOutcome:
    """Run all three sweeps on a proposed SIGNATURE; return composite outcome."""
    verdicts: list = []

    if coupling_check is not None:
        r30: Pattern30Result = sweep_pattern_30(coupling_check)
        verdicts.append(SweepVerdict(
            pattern="Pattern 30",
            verdict=r30.verdict,
            rationale=r30.rationale,
            details={
                "level": r30.level,
                "name": r30.name,
                "connecting_identity": r30.connecting_identity,
            },
        ))
    else:
        verdicts.append(SweepVerdict(
            pattern="Pattern 30",
            verdict="WARN",
            rationale=(
                "no coupling_check supplied; Pattern 30 could not auto-verify. "
                "For correlational claims this is BLOCK-worthy; for non-"
                "correlational claims (variance deficit, sign-uniform, "
                "calibration anchor) this is expected"
            ),
            details={"level": None, "name": "NO_CHECK"},
        ))

    if pattern20_check is not None:
        r20: Pattern20Result = sweep_pattern_20(pattern20_check)
        verdicts.append(SweepVerdict(
            pattern="Pattern 20",
            verdict=r20.verdict,
            rationale=r20.rationale,
            details={
                "ratio": r20.ratio,
                "sign_agreement": r20.sign_agreement,
                "small_n_strata": list(r20.small_n_strata),
            },
        ))
    else:
        verdicts.append(SweepVerdict(
            pattern="Pattern 20",
            verdict="CLEAR",
            rationale="no pooled/stratified pair supplied; not applicable",
            details={},
        ))

    if pattern19_new is not None:
        r19: Pattern19Result = sweep_pattern_19(pattern19_new, pattern19_prior)
        verdicts.append(SweepVerdict(
            pattern="Pattern 19",
            verdict=r19.verdict,
            rationale=r19.rationale,
            details=r19.provenance_delta,
        ))
    else:
        verdicts.append(SweepVerdict(
            pattern="Pattern 19",
            verdict="CLEAR",
            rationale="no prior-comparison supplied; not applicable",
            details={},
        ))

    overall = _merge(verdicts)
    blocked = (overall == "BLOCK") and not override
    warnings = [v for v in verdicts if v.verdict == "WARN"]

    return SweepOutcome(
        overall=overall,
        verdicts=verdicts,
        blocked=blocked,
        warnings=warnings,
        override=override,
        override_reason=override_reason,
        at=dt.datetime.now(dt.timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Append-only sweep results log
# ---------------------------------------------------------------------------

SWEEP_LOG_PATH = (
    Path(__file__).resolve().parent.parent / "memory" / "sweep_results_log.md"
)


def log_outcome(outcome: SweepOutcome, context: dict) -> None:
    """Append one entry to sweep_results_log.md. Context describes what
    ingestion call the sweep guarded (e.g. feature_id + task_id)."""
    SWEEP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "at": outcome.at,
        "context": context,
        "overall": outcome.overall,
        "blocked": outcome.blocked,
        "override": outcome.override,
        "override_reason": outcome.override_reason,
        "verdicts": [asdict(v) for v in outcome.verdicts],
    }
    with SWEEP_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write("\n## " + outcome.at + " — " + context.get("context_id", "?") + "\n\n")
        f.write("```json\n")
        f.write(json.dumps(entry, indent=2, default=str))
        f.write("\n```\n")


class SweepBlocked(Exception):
    """Raised when a sweep returns BLOCK and override is not set."""
    def __init__(self, outcome: SweepOutcome):
        self.outcome = outcome
        block_reasons = [
            f"{v.pattern}: {v.rationale}"
            for v in outcome.verdicts if v.verdict == "BLOCK"
        ]
        super().__init__(
            "Sweep BLOCK — ingestion halted. To override, pass "
            "override=True with a justification.\n  "
            + "\n  ".join(block_reasons)
        )
