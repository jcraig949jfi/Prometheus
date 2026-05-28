"""Q1 — modular arithmetic varying p (stub, Stage 20).

Emits claims about catalog invariant behavior mod p as p varies
across primes. Finds primes where structure changes.

From Sphinx domain C (Arithmetic).
Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


VARYING_P_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_rank_mod_p_distribution_changes_at_p7",
        "invariant": "EC rank mod p",
        "primes_checked": [2, 3, 5, 7, 11],
        "behavior_summary": "uniform for p ∈ {2,3,5}, sharp at p=7, uniform again p=11",
        "structural_change_at": 7,
    },
    {
        "id": "knot_determinant_mod_p_freq_drops_at_p13",
        "invariant": "knot determinant mod p",
        "primes_checked": [2, 3, 5, 7, 11, 13, 17],
        "behavior_summary": "uniform distribution for p ≤ 11; drops at p=13",
        "structural_change_at": 13,
    },
    {
        "id": "ec_conductor_mod_p_squarefree_only_p_dividing",
        "invariant": "EC conductor squarefree at p",
        "primes_checked": [2, 3, 5, 7, 11, 13],
        "behavior_summary": "squarefree at p iff p ∤ conductor; matches reduction theory",
        "structural_change_at": None,
    },
]


class Q1ModularVaryingPGenerator(Generator):
    generator_id = "q1"
    claim_kind = ClaimKind.MODULAR_VARYING_P.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"q1: modular_varying_p ({len(VARYING_P_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(VARYING_P_CLAIMS):
            return None
        c = VARYING_P_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        canonical = f"Q1_MODVARP[{c['id']}] {c['invariant']}: {c['behavior_summary']}"
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
                "invariant": c["invariant"],
                "primes_checked": c["primes_checked"],
                "behavior_summary": c["behavior_summary"],
                "structural_change_at_prime": c["structural_change_at"],
                "logical_form": "varying_modular_structure",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
