"""U1 — quantifier swap generator (stub, Stage 21).

Emits paired claims where ∀X∃Y vs ∃Y∀X order matters. Pure-shape
records exposing the substrate's sensitivity to quantifier order.

From Sphinx domain A (Formal Logic). Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


QUANTIFIER_PAIRS: List[Dict[str, Any]] = [
    {
        "id": "ec_prime_with_quadratic_twist",
        "claim_forall_exists": (
            "∀ EC E, ∃ prime p such that E has good reduction at p"
        ),
        "claim_exists_forall": (
            "∃ prime p such that ∀ EC E, E has good reduction at p"
        ),
        "swap_distinguishes": (
            "first is TRUE (each E has some good-reduction prime); "
            "second is FALSE (no prime is good for ALL ECs — pick p=conductor(E))"
        ),
    },
    {
        "id": "knot_invariant_separability",
        "claim_forall_exists": (
            "∀ pairs of distinct knots (K1, K2), ∃ invariant I separating them"
        ),
        "claim_exists_forall": (
            "∃ invariant I such that ∀ pairs (K1, K2), I separates them"
        ),
        "swap_distinguishes": (
            "first is true if knot invariants are complete; "
            "second false (no single classical invariant separates all knots)"
        ),
    },
    {
        "id": "modular_form_level_realization",
        "claim_forall_exists": (
            "∀ newform f, ∃ EC E with conductor(E) = level(f) and L(E,s) = L(f,s)"
        ),
        "claim_exists_forall": (
            "∃ EC E such that ∀ newform f at level N, L(E,s) = L(f,s)"
        ),
        "swap_distinguishes": (
            "first is modularity (TRUE post-Wiles); "
            "second is FALSE (newform-EC correspondence is per-form)"
        ),
    },
]


class U1QuantifierSwapGenerator(Generator):
    generator_id = "u1"
    claim_kind = ClaimKind.QUANTIFIER_SWAP.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"u1: quantifier_swap ({len(QUANTIFIER_PAIRS)} paired claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(QUANTIFIER_PAIRS):
            return None
        q = QUANTIFIER_PAIRS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        canonical = (
            f"U1_QSWAP[{q['id']}] '{q['claim_forall_exists']}' ≢ "
            f"'{q['claim_exists_forall']}' — {q['swap_distinguishes']}"
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
                "claim_id": q["id"],
                "claim_forall_exists": q["claim_forall_exists"],
                "claim_exists_forall": q["claim_exists_forall"],
                "swap_distinguishes": q["swap_distinguishes"],
                "logical_form": "quantifier_order_sensitivity",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
