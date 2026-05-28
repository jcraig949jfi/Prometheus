"""W1 — closure under operation generator (stub, Stage 22).

Emits claims "Set S is closed under operation O" — for catalog
subsets, test whether applying an operation keeps you in the set.

From Sphinx domains G + H. Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


CLOSURE_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_isogeny_class_closed",
        "set_description": "isogeny class of an EC",
        "operation": "isogeny",
        "expected_holds": True,
        "rationale": "isogeny class is closed under further isogenies by definition",
    },
    {
        "id": "knot_satellite_operation_closure",
        "set_description": "knots of crossing_number ≤ 12",
        "operation": "satellite operation (Whitehead double)",
        "expected_holds": False,
        "rationale": (
            "satellite operation generally increases crossing number; "
            "set is not closed under it"
        ),
    },
    {
        "id": "ec_twist_within_conductor_class",
        "set_description": "EC with fixed conductor N",
        "operation": "quadratic twist by squarefree d coprime to N",
        "expected_holds": False,
        "rationale": (
            "twist by d coprime to N changes conductor to N·d^2 (after "
            "minimal model), exits the set"
        ),
    },
    {
        "id": "alternating_knots_under_connect_sum",
        "set_description": "alternating knots",
        "operation": "connect sum (K_1 # K_2)",
        "expected_holds": True,
        "rationale": "connect sum of alternating knots is alternating",
    },
]


class W1ClosureUnderOperationGenerator(Generator):
    generator_id = "w1"
    claim_kind = ClaimKind.CLOSURE_UNDER_OPERATION.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"w1: closure_under_operation ({len(CLOSURE_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(CLOSURE_CLAIMS):
            return None
        c = CLOSURE_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        verb = "IS" if c["expected_holds"] else "is NOT"
        canonical = (
            f"W1_CLOSURE[{c['id']}] {c['set_description']} "
            f"{verb} closed under {c['operation']} — {c['rationale']}"
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
                "set_description": c["set_description"],
                "operation": c["operation"],
                "expected_holds": c["expected_holds"],
                "rationale": c["rationale"],
                "logical_form": "closure_under_operation",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
