"""Z1 — order dependence generator (stub, Stage 23).

Emits claims testing f(g(X)) vs g(f(X)) for catalog operations.
When the two differ, the operations don't commute.

From Sphinx domain D (Temporal / Ordering). Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


ORDER_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_twist_and_reduce_noncommute",
        "operations": ("twist by d", "reduction at p"),
        "claim_summary": (
            "twist-then-reduce ≠ reduce-then-twist when p | d "
            "(reduction type changes)"
        ),
        "expected_commute": False,
    },
    {
        "id": "knot_mirror_and_reverse_commute",
        "operations": ("mirror", "reverse orientation"),
        "claim_summary": (
            "mirror and reverse commute for any knot K: "
            "rev(mirror(K)) = mirror(rev(K))"
        ),
        "expected_commute": True,
    },
    {
        "id": "ec_isogeny_dual_and_reduction",
        "operations": ("dual isogeny", "reduction at p"),
        "claim_summary": (
            "dual-then-reduce = reduce-then-dual (isogeny commutes with "
            "good reduction)"
        ),
        "expected_commute": True,
    },
    {
        "id": "knot_connect_sum_and_mirror",
        "operations": ("connect sum K_1 # K_2", "mirror"),
        "claim_summary": (
            "mirror(K_1 # K_2) = mirror(K_1) # mirror(K_2) — commutes"
        ),
        "expected_commute": True,
    },
]


class Z1OrderDependenceGenerator(Generator):
    generator_id = "z1"
    claim_kind = ClaimKind.ORDER_DEPENDENCE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"z1: order_dependence ({len(ORDER_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(ORDER_CLAIMS):
            return None
        c = ORDER_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        a, b = c["operations"]
        verb = "COMMUTE" if c["expected_commute"] else "DO NOT COMMUTE"
        canonical = (
            f"Z1_ORDER[{c['id']}] {a} and {b} {verb}: {c['claim_summary']}"
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
                "op_a": a,
                "op_b": b,
                "claim_summary": c["claim_summary"],
                "expected_commute": c["expected_commute"],
                "logical_form": "operator_commutativity",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
