"""N1 — active-disagreement generator.

Emits META-CLAIMS about substrate verifier behavior:

    On record R, verifier V1 emits verdict V1(R),
    verifier V2 emits verdict V2(R),
    and V1(R) ≠ V2(R).

By construction these are the HIGHEST-INFORMATION records the
substrate can emit: the substrate disagrees with itself, and the
disagreement is a structural signal about where verifiers are
miscalibrated.

Different from every existing generator: all current records are
claims ABOUT mathematical objects; n1 is a claim ABOUT verifier
behavior on those records.

Stage 5 / Stage 1-of-implementation: STUB. Emits hand-coded
disagreement examples without actually replaying records through
real verifiers. The shape is what we're testing here.

Plan: pivot/techne_5gen_plan_2026-05-27.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


STUB_DISAGREEMENTS: List[dict] = [
    {
        "subject_record_summary": (
            "F2_AFS[cov=1] determinant(knot:8_21) "
            "equal_mod_2 rank(ec:9240.e4)"
        ),
        "verifier_a": "sigma_kernel",
        "verdict_a": "SHADOW_CATALOG",
        "verifier_b": "fast_heuristic_check",
        "verdict_b": "REJECTED",
        "disagreement_axis": "verdict_disagreement",
        "candidate_explanation": (
            "sigma_kernel computes determinant exactly (15); "
            "fast_heuristic uses cached value that may be stale"
        ),
        "human_summary": (
            "sigma_kernel SHADOW vs fast_heuristic REJECTED on "
            "knot 8_21 / ec 9240.e4 parity claim"
        ),
    },
    {
        "subject_record_summary": (
            "A4_R2[knot.crossing_number, ec.conductor] r2=0.04"
        ),
        "verifier_a": "polyfit_dps_15",
        "verdict_a": "INCONCLUSIVE",
        "verifier_b": "polyfit_dps_30",
        "verdict_b": "REJECTED",
        "disagreement_axis": "precision_resolution_dependent",
        "candidate_explanation": (
            "low-precision fit borderline INCONCLUSIVE; "
            "high-precision shows the r2 is below WEAK_R2 threshold"
        ),
        "human_summary": (
            "polyfit dps=15 INCONCLUSIVE vs dps=30 REJECTED on "
            "crossing_number ↔ conductor correlation"
        ),
    },
    {
        "subject_record_summary": (
            "C5_specialization[parent=a2_record] kill_pattern=specific_violated"
        ),
        "verifier_a": "kill_pattern_classifier_v1",
        "verdict_a": "REJECTED:specific_violated",
        "verifier_b": "kill_pattern_classifier_v2",
        "verdict_b": "REJECTED:generic_value_mismatch",
        "disagreement_axis": "kill_pattern_attribution",
        "candidate_explanation": (
            "v1 attributes kill to specific feature; v2 attributes "
            "to generic mismatch — meta-disagreement about kill "
            "STRUCTURE not kill OUTCOME"
        ),
        "human_summary": (
            "kill-pattern classifier v1 vs v2 disagree on WHY a "
            "specific C5 record was killed"
        ),
    },
]


class N1ActiveDisagreementGenerator(Generator):
    generator_id = "n1"
    claim_kind = ClaimKind.VERIFIER_DISAGREEMENT.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return (
            f"n1: active-disagreement stub "
            f"({len(STUB_DISAGREEMENTS)} hand-coded verifier-disagreement records)"
        )

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(STUB_DISAGREEMENTS):
            return None
        d = STUB_DISAGREEMENTS[self._cursor]
        self._cursor += 1
        self.attempts += 1

        canonical = (
            f"N1_DISAGREE[{d['disagreement_axis']}] "
            f"{d['verifier_a']}={d['verdict_a']} vs "
            f"{d['verifier_b']}={d['verdict_b']} on "
            f"<{d['subject_record_summary']}>"
        )
        record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
        self.emitted.append(record_id)

        return TheseusRecord(
            record_id=record_id,
            generator_id=self.generator_id,
            batch_id=self.batch_id,
            emitted_at=datetime.now(timezone.utc).isoformat(),
            claim_kind=self.claim_kind,
            claim_payload={
                "subject_record_summary": d["subject_record_summary"],
                "verifier_a": d["verifier_a"],
                "verdict_a": d["verdict_a"],
                "verifier_b": d["verifier_b"],
                "verdict_b": d["verdict_b"],
                "disagreement_axis": d["disagreement_axis"],
                "candidate_explanation": d["candidate_explanation"],
                "logical_form": "verifier_disagreement_meta_claim",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
