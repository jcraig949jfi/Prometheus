"""BB1 — false dichotomy generator (stub, Stage 23).

Emits claims demonstrating that ≥3 distinct categories exist in
contexts where a binary distinction is commonly assumed.

From Sphinx domain J (Common Sense). Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


DICHOTOMY_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_reduction_not_binary",
        "naive_binary": "good vs bad reduction",
        "actual_categories": (
            "good, multiplicative (split / non-split), "
            "additive (potentially good / potentially multiplicative)"
        ),
        "category_count": 5,
        "rationale": (
            "Kodaira/Néron classification: ≥5 reduction types"
        ),
    },
    {
        "id": "knot_amphichirality_not_binary",
        "naive_binary": "amphichiral vs chiral",
        "actual_categories": (
            "positive amphichiral, negative amphichiral, "
            "fully amphichiral, chiral"
        ),
        "category_count": 4,
        "rationale": (
            "amphichirality has direction (positive/negative) and full vs "
            "partial; binary split misses structure"
        ),
    },
    {
        "id": "ec_torsion_classification_15_groups",
        "naive_binary": "trivial torsion vs nontrivial torsion",
        "actual_categories": (
            "Mazur's 15 distinct torsion structures: Z/n for n ∈ {1..10,12} "
            "and Z/2×Z/2n for n ∈ {1..4}"
        ),
        "category_count": 15,
        "rationale": "Mazur's theorem enumerates exactly 15 groups",
    },
    {
        "id": "knot_genus_not_binary",
        "naive_binary": "genus-0 (unknot) vs genus-positive",
        "actual_categories": (
            "genus 0, 1, 2, 3, ..., ∞ (countable)"
        ),
        "category_count": -1,  # infinite
        "rationale": (
            "knot genus is a non-negative integer; the binary "
            "trivial/nontrivial split flattens a Z-graded invariant"
        ),
    },
]


class Bb1FalseDichotomyGenerator(Generator):
    generator_id = "bb1"
    claim_kind = ClaimKind.FALSE_DICHOTOMY.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"bb1: false_dichotomy ({len(DICHOTOMY_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(DICHOTOMY_CLAIMS):
            return None
        c = DICHOTOMY_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        ncat = (
            str(c["category_count"]) if c["category_count"] >= 0
            else "countably infinite"
        )
        canonical = (
            f"BB1_FALSE_DI[{c['id']}] '{c['naive_binary']}' actually has "
            f"{ncat} categories: {c['actual_categories']}"
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
                "naive_binary": c["naive_binary"],
                "actual_categories": c["actual_categories"],
                "category_count": c["category_count"],
                "rationale": c["rationale"],
                "logical_form": "false_dichotomy",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
