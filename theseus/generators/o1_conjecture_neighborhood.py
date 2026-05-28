"""O1 — conjecture-neighborhood generator.

Emits claims of the form:

    Theorem T with assumption A relaxed to A' ⇒ conclusion C holds/fails

Starts from a KNOWN result, perturbs ONE hypothesis, asks whether
the conclusion survives. The shape is fundamentally different from
all current generators which either sample claims or transform
existing claims by mechanical mutation; o1 transforms by HYPOTHESIS
PERTURBATION.

Example: "Mazur's torsion theorem: with the rationality hypothesis
relaxed to QQ-bar, the torsion-subgroup classification changes from
15 groups to a different countable list."

Stage 6 / Stage 1-of-implementation: STUB. Emits hand-coded
perturbation templates from a small list of theorems.

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


STUB_CONJECTURE_NEIGHBORHOODS: List[dict] = [
    {
        "source_theorem": "Mazur_torsion_theorem",
        "theorem_statement": (
            "An elliptic curve over Q has torsion subgroup isomorphic "
            "to one of 15 specific groups"
        ),
        "original_hypotheses": [
            "E defined over Q",
            "torsion subgroup considered over Q",
        ],
        "perturbed_hypothesis_index": 1,
        "perturbed_hypothesis": "torsion subgroup considered over Q-bar",
        "conjectured_conclusion_change": (
            "classification becomes countably infinite "
            "(all finite abelian groups admissible)"
        ),
        "perturbation_strength": "moderate",
        "human_summary": (
            "Mazur torsion theorem with Q → Q-bar in the torsion "
            "field: 15-group list opens to countable family"
        ),
    },
    {
        "source_theorem": "Faltings_theorem_finiteness",
        "theorem_statement": (
            "A curve of genus ≥ 2 over a number field has finitely "
            "many rational points"
        ),
        "original_hypotheses": [
            "C smooth projective curve",
            "genus(C) ≥ 2",
            "K number field",
        ],
        "perturbed_hypothesis_index": 1,
        "perturbed_hypothesis": "genus(C) = 1 with j-invariant non-CM",
        "conjectured_conclusion_change": (
            "finiteness fails: rank may be positive, rational points "
            "may be infinite (this is the EC case, by design)"
        ),
        "perturbation_strength": "destroys_conclusion",
        "human_summary": (
            "Faltings finiteness fails when genus drops from ≥2 "
            "to 1 — recovers the EC rank theory"
        ),
    },
    {
        "source_theorem": "Sato_Tate_for_non_CM_EC",
        "theorem_statement": (
            "For a non-CM elliptic curve E over Q, the normalized "
            "Frobenius angles equidistribute according to the "
            "Sato-Tate measure (sin² distribution on [0,π])"
        ),
        "original_hypotheses": [
            "E non-CM",
            "E defined over Q",
        ],
        "perturbed_hypothesis_index": 0,
        "perturbed_hypothesis": "E has complex multiplication",
        "conjectured_conclusion_change": (
            "distribution changes: equidistributes on {0,π} "
            "(degenerate two-point) plus continuous component"
        ),
        "perturbation_strength": "qualitative_change",
        "human_summary": (
            "Sato-Tate distribution changes from sin² to "
            "mixed-discrete when EC has CM"
        ),
    },
    {
        "source_theorem": "Manin_Drinfeld_theorem",
        "theorem_statement": (
            "Cusps of modular curves X_0(N) generate a finite subgroup "
            "of Jacobian when considered as degree-0 divisors"
        ),
        "original_hypotheses": [
            "X_0(N) modular curve of level N",
            "degree-0 cusp divisors",
        ],
        "perturbed_hypothesis_index": 0,
        "perturbed_hypothesis": (
            "X_0(N) replaced by X_1(N) (Γ_1(N) instead of Γ_0(N))"
        ),
        "conjectured_conclusion_change": (
            "Manin-Drinfeld may fail at level N where extra "
            "non-torsion cusp differences appear"
        ),
        "perturbation_strength": "delicate",
        "human_summary": (
            "Manin-Drinfeld for X_0(N) — does it survive when "
            "the congruence subgroup is changed Γ_0 → Γ_1?"
        ),
    },
]


class O1ConjectureNeighborhoodGenerator(Generator):
    generator_id = "o1"
    claim_kind = ClaimKind.CONJECTURE_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return (
            f"o1: conjecture-neighborhood stub "
            f"({len(STUB_CONJECTURE_NEIGHBORHOODS)} hand-coded "
            f"theorem-perturbation records)"
        )

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(STUB_CONJECTURE_NEIGHBORHOODS):
            return None
        cn = STUB_CONJECTURE_NEIGHBORHOODS[self._cursor]
        self._cursor += 1
        self.attempts += 1

        canonical = (
            f"O1_NEIGHBORHOOD[{cn['source_theorem']}] "
            f"perturb hypothesis #{cn['perturbed_hypothesis_index']}: "
            f"{cn['perturbed_hypothesis']} ⇒ "
            f"{cn['conjectured_conclusion_change']}"
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
                "source_theorem": cn["source_theorem"],
                "theorem_statement": cn["theorem_statement"],
                "original_hypotheses": cn["original_hypotheses"],
                "perturbed_hypothesis_index": cn["perturbed_hypothesis_index"],
                "perturbed_hypothesis": cn["perturbed_hypothesis"],
                "conjectured_conclusion_change": cn["conjectured_conclusion_change"],
                "perturbation_strength": cn["perturbation_strength"],
                "logical_form": "hypothesis_perturbation",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
