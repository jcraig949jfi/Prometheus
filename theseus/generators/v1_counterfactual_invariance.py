"""V1 — counterfactual invariance generator (stub, Stage 21).

Emits claims of form "If catalog object X had attribute A = a'
instead of a, then property P(X) would still hold."

From Sphinx domain F (Causal). Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


COUNTERFACTUALS: List[Dict[str, Any]] = [
    {
        "id": "ec_rank_robust_under_conductor_perturbation",
        "object": "ec:5077.a1",
        "perturbation": "conductor → conductor + 1 (= 5078)",
        "property": "rank ≥ 3",
        "conjectured_outcome": (
            "rank likely changes — ECs of conductor 5078 may not exist at rank 3; "
            "conductor change perturbs the curve identity"
        ),
    },
    {
        "id": "knot_signature_robust_under_one_crossing_change",
        "object": "knot:8_19",
        "perturbation": "remove one crossing (resolve to lower crossing knot)",
        "property": "signature ≠ 0",
        "conjectured_outcome": (
            "signature may flip — Reidemeister-type modifications change "
            "Seifert form, hence signature"
        ),
    },
    {
        "id": "ec_l_value_robust_under_torsion_swap",
        "object": "ec:11.a1",
        "perturbation": "swap torsion subgroup Z/5 → Z/2",
        "property": "L(E, 1) > 0",
        "conjectured_outcome": (
            "L(E,1) is sensitive to torsion since BSD links L-value, "
            "regulator, Sha, and torsion — perturbing one shifts the others"
        ),
    },
]


class V1CounterfactualInvarianceGenerator(Generator):
    generator_id = "v1"
    claim_kind = ClaimKind.COUNTERFACTUAL_INVARIANCE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"v1: counterfactual_invariance ({len(COUNTERFACTUALS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(COUNTERFACTUALS):
            return None
        c = COUNTERFACTUALS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        canonical = (
            f"V1_CFAC[{c['id']}] If {c['object']} had {c['perturbation']}, "
            f"would {c['property']} still hold? — {c['conjectured_outcome']}"
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
                "object": c["object"],
                "perturbation": c["perturbation"],
                "property": c["property"],
                "conjectured_outcome": c["conjectured_outcome"],
                "logical_form": "counterfactual_invariance",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
