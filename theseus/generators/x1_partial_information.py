"""X1 — partial information / absence-of-evidence generator (stub, Stage 22).

Emits claims that hold given a partial catalog view but may fail
with the full view. Tests substrate robustness to closed-world
reasoning.

From Sphinx domain L (Uncertainty). Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


PARTIAL_INFO_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_rank_max_in_first_100_conductors",
        "partial_view": "EC with conductor ≤ 100",
        "claim_under_partial": "max rank = 1",
        "claim_under_full": "max rank ≥ 3 (rank-3 EC exists at conductor 5077)",
        "robustness_label": "FRAGILE: claim was a small-conductor artifact",
    },
    {
        "id": "knot_signature_distribution_under_8_crossings",
        "partial_view": "knots with crossing_number ≤ 8",
        "claim_under_partial": "signature ∈ {-4, -2, 0, 2, 4}",
        "claim_under_full": (
            "signature distribution extends to wider range as crossings increase"
        ),
        "robustness_label": "FRAGILE: bounded-crossing subset hides tail",
    },
    {
        "id": "ec_torsion_subgroup_under_50_conductors",
        "partial_view": "EC with conductor ≤ 50",
        "claim_under_partial": "torsion subgroup ⊆ {Z/n for n ≤ 6}",
        "claim_under_full": (
            "Mazur's theorem: torsion ⊆ {Z/n for n=1..10,12, Z/2×Z/2n for n=1..4} "
            "(15 specific groups)"
        ),
        "robustness_label": "INCOMPLETE: partial view missed several Mazur groups",
    },
]


class X1PartialInformationGenerator(Generator):
    generator_id = "x1"
    claim_kind = ClaimKind.PARTIAL_INFORMATION.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"x1: partial_information ({len(PARTIAL_INFO_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(PARTIAL_INFO_CLAIMS):
            return None
        c = PARTIAL_INFO_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        canonical = (
            f"X1_PARTIAL[{c['id']}] partial: '{c['claim_under_partial']}' "
            f"vs full: '{c['claim_under_full']}' — {c['robustness_label']}"
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
                "claim_id": c["id"],
                "partial_view": c["partial_view"],
                "claim_under_partial": c["claim_under_partial"],
                "claim_under_full": c["claim_under_full"],
                "robustness_label": c["robustness_label"],
                "logical_form": "partial_information_fragility",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
