"""
Icarus typed failure taxonomy + training-object schema.

Per the 2026-05-28 review reframe: Icarus is a failure-to-representation
instrumentation harness. The governing requirement is that EVERY cycle emits
a reusable training object -- not a binary verdict, but a typed record of:
what changed, what capability it claimed, what killed it, what survived
nearby, what future tier it threatens, what test would expose it.

This module defines the typed vocabulary + the TrainingObject dataclass.
Deterministic fields (failure_class, detected_by, blocked_promotion) are
derived from infrastructure state. Enriched fields (nearby_survivor,
future_tier_risk, regression_test_to_write) are populated by the Integrator
lens; we keep them separable so a future audit can compare the LLM-claimed
enrichment against the deterministic spine (Goodhart check).

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------

# Why a cycle ended where it did. Deterministically derivable from infra
# state (apply result + tdd result + skeptic verdict + integrator decision).
FAILURE_CLASSES = (
    "none",                  # cycle promoted cleanly, no failure
    "no_diff",               # generator produced nothing applyable
    "diff_apply_failed",     # patch did not apply
    "tdd_failed",            # tests failed or errored
    "tdd_vacuous",           # zero tests ran (vacuous pass rejected)
    "contract_break",        # a public-function contract silently changed
    "falsifier_rejected",    # skeptic probes broke the proposal
    "semantic_regression",   # lower-tier capability regressed
    "metric_shaped",         # promoted but improvement is metric- not capability-shaped
    "panel_error",           # a lens crashed / unparseable
    "promoted_with_debt",    # promoted despite an open contract-level minority report
)

# Finer-grained subclass. Free-ish but drawn from a curated set so kill-path
# clustering can group by signature.
FAILURE_SUBCLASSES = (
    "hunk_recount",                  # diff_apply_failed: wrong @@ line counts
    "context_mismatch",              # diff_apply_failed: hallucinated context
    "import_error",                  # tdd: module import failed
    "assertion_failed",              # tdd: a real assertion failed
    "zero_tests_collected",          # tdd_vacuous
    "input_output_alignment_lost",   # contract_break: cardinality/ordering
    "type_instability",             # contract_break: return type changed
    "exception_contract_changed",    # contract_break: raises where it returned
    "probe_break",                   # falsifier: adversarial input broke it
    "lower_tier_test_failed",        # semantic_regression
    "test_passes_by_construction",   # metric_shaped: test added that locks current behavior
    "docstring_claim_without_proof", # metric_shaped: claims capability, no demonstration
    "unparseable_lens_output",       # panel_error
    "none",
)

# What kind of move the Generator made this cycle.
PROPOSAL_TYPES = (
    "reasoner_logic_change",
    "batch_orchestration_change",
    "new_method",
    "representation_shift",
    "test_addition",
    "docstring_change",
    "refactor",
    "no_change",
    "unknown",
)


@dataclass
class TrainingObject:
    """The reusable artifact every cycle must emit. The bridge from
    Icarus-as-daemon to Icarus-as-substrate."""
    cycle: int
    tier_target: str
    strategy: str
    decision: str  # "mark_stable" | "park"

    # --- deterministic spine (derived from infra, not LLM) ---
    failure_class: str
    detected_by: str  # which lens / phase first surfaced the outcome-determining fact
    blocked_promotion: bool  # did this concern block promotion?
    diff_applied: bool
    tdd_all_passed: bool
    tests_run: int
    files_changed: list[str] = field(default_factory=list)

    # --- enriched fields (Integrator-populated; audit-separable) ---
    proposal_type: str = "unknown"
    failure_subclass: str = "none"
    nearby_survivor: Optional[str] = None       # what move WOULD have survived
    future_tier_risk: list[str] = field(default_factory=list)  # tiers this threatens
    regression_test_to_write: Optional[str] = None  # the test that would expose it
    representation_change_hint: Optional[str] = None  # what repr change makes the right move cheap

    # --- capability vs metric split (Goodhart instrument) ---
    improvement_kind: Optional[str] = None  # "capability" | "test_weakness" | "metric_shaped" | "none"
    improvement_rationale: Optional[str] = None

    # --- provenance ---
    ts: str = ""
    enrichment_source: str = "integrator"  # or "deterministic_only" if Integrator failed

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TrainingObject":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore
        return cls(**{k: v for k, v in d.items() if k in known})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify_deterministic_spine(
    cycle_n: int,
    tier_target: str,
    strategy: str,
    decision: str,
    apply_result: dict,
    tdd_result: dict,
    skeptic_report: Optional[dict],
    contract_report: Optional[dict],
    load_bearing_lens: str,
) -> dict:
    """Derive the non-LLM fields of the training object from infra state.
    This is the spine that the Integrator's enrichment is checked against."""
    applied = bool((apply_result or {}).get("applied"))
    tdd_passed = bool((tdd_result or {}).get("all_passed"))
    per_source = (tdd_result or {}).get("per_source", {}) or {}
    tests_run = 0
    for sub in per_source.values():
        if isinstance(sub, dict):
            tests_run += sub.get("passed", 0) + sub.get("failed", 0) + sub.get("errors", 0)

    files_changed = (apply_result or {}).get("files_changed", []) or []

    # Determine failure_class + subclass + detected_by deterministically
    failure_class = "none"
    failure_subclass = "none"
    detected_by = load_bearing_lens or "integrator"
    blocked = decision == "park"

    if decision == "mark_stable":
        # Promoted. Did a contract concern or skeptic minority survive into promotion?
        contract_flag = (contract_report or {}).get("contract_violation")
        skeptic_minority = (skeptic_report or {}).get("minority_position")
        if contract_flag:
            failure_class = "promoted_with_debt"
            failure_subclass = (contract_report or {}).get("violation_subclass", "input_output_alignment_lost")
            detected_by = "contract"
            blocked = False
        elif skeptic_minority:
            failure_class = "promoted_with_debt"
            failure_subclass = "input_output_alignment_lost"
            detected_by = "skeptic"
            blocked = False
        else:
            failure_class = "none"
    else:
        # Parked. Classify why.
        if not applied:
            reason = (apply_result or {}).get("reason", "")
            failure_class = "no_diff" if "no_diff" in reason or "empty" in reason else "diff_apply_failed"
            if "recount" in reason or "corrupt" in reason or "line" in reason:
                failure_subclass = "hunk_recount"
            elif "does not apply" in reason or "patch failed" in reason:
                failure_subclass = "context_mismatch"
            detected_by = "patcher"
        elif tests_run == 0:
            failure_class = "tdd_vacuous"
            failure_subclass = "zero_tests_collected"
            detected_by = "tdd"
        elif not tdd_passed:
            failure_class = "tdd_failed"
            failure_subclass = "assertion_failed"
            detected_by = "tdd"
        elif skeptic_report and (skeptic_report.get("probes_failed", 0) or 0) > 0:
            failure_class = "falsifier_rejected"
            failure_subclass = "probe_break"
            detected_by = "skeptic"
        elif contract_report and contract_report.get("contract_violation"):
            failure_class = "contract_break"
            failure_subclass = contract_report.get("violation_subclass", "input_output_alignment_lost")
            detected_by = "contract"

    return {
        "failure_class": failure_class,
        "failure_subclass": failure_subclass,
        "detected_by": detected_by,
        "blocked_promotion": blocked,
        "diff_applied": applied,
        "tdd_all_passed": tdd_passed,
        "tests_run": tests_run,
        "files_changed": files_changed,
    }


def build_training_object(
    cycle_n: int,
    tier_target: str,
    strategy: str,
    decision: str,
    apply_result: dict,
    tdd_result: dict,
    skeptic_report: Optional[dict],
    contract_report: Optional[dict],
    integrator_report: Optional[dict],
    load_bearing_lens: str,
) -> TrainingObject:
    """Assemble the full training object: deterministic spine + Integrator
    enrichment. If the Integrator failed, fall back to spine-only."""
    spine = classify_deterministic_spine(
        cycle_n, tier_target, strategy, decision,
        apply_result, tdd_result, skeptic_report, contract_report, load_bearing_lens,
    )

    enrich = (integrator_report or {}).get("training_enrichment", {}) or {}
    enrichment_source = "integrator" if enrich else "deterministic_only"

    return TrainingObject(
        cycle=cycle_n,
        tier_target=tier_target,
        strategy=strategy,
        decision=decision,
        ts=_now_iso(),
        enrichment_source=enrichment_source,
        # spine
        failure_class=spine["failure_class"],
        detected_by=spine["detected_by"],
        blocked_promotion=spine["blocked_promotion"],
        diff_applied=spine["diff_applied"],
        tdd_all_passed=spine["tdd_all_passed"],
        tests_run=spine["tests_run"],
        files_changed=spine["files_changed"],
        # enriched (Integrator) -- with spine subclass as fallback
        proposal_type=enrich.get("proposal_type", "unknown"),
        failure_subclass=enrich.get("failure_subclass", spine["failure_subclass"]),
        nearby_survivor=enrich.get("nearby_survivor"),
        future_tier_risk=enrich.get("future_tier_risk", []) or [],
        regression_test_to_write=enrich.get("regression_test_to_write"),
        representation_change_hint=enrich.get("representation_change_hint"),
        improvement_kind=enrich.get("improvement_kind"),
        improvement_rationale=enrich.get("improvement_rationale"),
    )


def write_training_object(obj: TrainingObject, cycle_dir: Path) -> Path:
    """Persist the training object as cycles/cycle_N/training_object.json."""
    out = cycle_dir / "training_object.json"
    try:
        out.write_text(json.dumps(obj.to_dict(), indent=2, default=str),
                       encoding="utf-8")
    except Exception:
        pass
    # Also append to a swarm-wide training stream for cross-cycle mining
    stream = Path(r"D:\Prometheus\agents\icarus\state\training_stream.jsonl")
    try:
        stream.parent.mkdir(parents=True, exist_ok=True)
        with open(stream, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj.to_dict(), default=str) + "\n")
    except Exception:
        pass
    return out
