"""R1 — subset relation generator (stub, Stage 20).

Emits claims about set relations (⊆, ⊇, =, ∩, ∪, ∅) between
computable catalog subsets. Substrate had pairwise-claim records
but no set-relation claims.

From Sphinx domain G (Set Theory).
Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


SUBSET_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_rank_ge3_subset_conductor_ge_5077",
        "subset_a": "EC[rank ≥ 3]",
        "subset_b": "EC[conductor ≥ 5077]",
        "relation": "⊆",
        "human_summary": (
            "Every EC with rank ≥ 3 has conductor ≥ 5077 "
            "(known smallest rank-3 conductor)"
        ),
    },
    {
        "id": "alternating_knots_subset_signature_le_genus",
        "subset_a": "alternating knots",
        "subset_b": "knots with |signature(K)| ≤ 2·genus(K)",
        "relation": "⊆",
        "human_summary": (
            "Alternating knots satisfy |σ(K)| ≤ 2g(K) "
            "(known classical bound)"
        ),
    },
    {
        "id": "ec_cm_intersect_high_rank_empty_for_small_cond",
        "subset_a": "EC[CM]",
        "subset_b": "EC[rank ≥ 2, conductor ≤ 100]",
        "relation": "∩ = ∅",
        "human_summary": (
            "No CM EC with conductor ≤ 100 has rank ≥ 2"
        ),
    },
    {
        "id": "ec_squarefree_disc_eq_semistable",
        "subset_a": "EC[squarefree discriminant]",
        "subset_b": "EC[semistable]",
        "relation": "=",
        "human_summary": (
            "EC has squarefree discriminant ⟺ all reduction "
            "types multiplicative ⟺ E semistable"
        ),
    },
]


class R1SubsetRelationGenerator(Generator):
    generator_id = "r1"
    claim_kind = ClaimKind.SUBSET_RELATION.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"r1: subset_relation ({len(SUBSET_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(SUBSET_CLAIMS):
            return None
        c = SUBSET_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        canonical = (
            f"R1_SUBSET[{c['id']}] {c['subset_a']} {c['relation']} "
            f"{c['subset_b']}: {c['human_summary']}"
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
                "subset_a": c["subset_a"],
                "subset_b": c["subset_b"],
                "relation": c["relation"],
                "logical_form": "set_relation",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
