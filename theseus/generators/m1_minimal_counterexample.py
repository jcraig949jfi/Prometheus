"""M1 — minimal counterexample generator.

Emits claims of the form:

    Conjecture C fails at minimum object M ∈ {P-objects ordered by size}

Where the minimality is certified by enumerating all P-objects of
size < size(M) and verifying that C holds on each.

Different from d-family (kill_neighborhood) which catalogs near-kills:
m1 finds EXTREMAL violators with proof of minimality.

Example: "Mazur's torsion theorem fails for groups Z/N with N > 12;
minimal counterexample certificate enumerates all groups Z/N with
N ≤ 12 and verifies each occurs as a torsion subgroup of some EC/Q."

Stage 4 / Stage 1-of-implementation: STUB. Emits hand-coded
minimal-counterexample claims with synthetic enumeration receipts.

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


STUB_MINIMAL_COUNTEREXAMPLES: List[dict] = [
    {
        "conjecture_name": "stub_conjecture_torsion_groups_finite",
        "conjecture_statement": (
            "Every finite abelian group is the torsion subgroup "
            "of some elliptic curve over Q"
        ),
        "ordering": "group_order",
        "minimal_violator": "Z/11Z",
        "minimal_violator_size": 11,
        "minimality_certificate": {
            "method": "exhaustive_enumeration_of_smaller",
            "enumerated_count": 10,
            "smaller_objects_passing": [
                "Z/1Z", "Z/2Z", "Z/3Z", "Z/4Z", "Z/5Z", "Z/6Z",
                "Z/7Z", "Z/8Z", "Z/9Z", "Z/10Z",
            ],
        },
        "human_summary": (
            "Minimal violator of 'every Z/nZ is EC/Q torsion' is "
            "Z/11Z; all Z/nZ for n ∈ {1..10} occur"
        ),
    },
    {
        "conjecture_name": "stub_conjecture_knot_determinant_parity",
        "conjecture_statement": (
            "For every prime p, there exists a knot K with crossings "
            "≤ 10 and determinant ≡ 1 (mod p)"
        ),
        "ordering": "prime",
        "minimal_violator": "p=23",
        "minimal_violator_size": 23,
        "minimality_certificate": {
            "method": "enumerate_primes_with_witness",
            "enumerated_count": 8,
            "smaller_primes_passing": [2, 3, 5, 7, 11, 13, 17, 19],
        },
        "human_summary": (
            "Smallest prime p with no knot ≤10 crossings having "
            "det ≡ 1 (mod p) is p=23"
        ),
    },
    {
        "conjecture_name": "stub_conjecture_ec_rank_one_density",
        "conjecture_statement": (
            "Every conductor-class C contains an elliptic curve of "
            "analytic rank exactly 1"
        ),
        "ordering": "conductor",
        "minimal_violator": "conductor=37",
        "minimal_violator_size": 37,
        "minimality_certificate": {
            "method": "lmfdb_conductor_class_lookup",
            "enumerated_count": 36,
            "note": (
                "conductors 1..36 each contain rank-1 isogeny class; "
                "conductor 37 violates"
            ),
        },
        "human_summary": (
            "Stub: smallest conductor without a rank-1 EC is N=37 "
            "(STUB CLAIM — would be wrong; real m1 must verify)"
        ),
    },
]


class M1MinimalCounterexampleGenerator(Generator):
    generator_id = "m1"
    claim_kind = ClaimKind.MINIMAL_COUNTEREXAMPLE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return (
            f"m1: minimal-counterexample stub "
            f"({len(STUB_MINIMAL_COUNTEREXAMPLES)} hand-coded extremal claims)"
        )

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(STUB_MINIMAL_COUNTEREXAMPLES):
            return None
        mc = STUB_MINIMAL_COUNTEREXAMPLES[self._cursor]
        self._cursor += 1
        self.attempts += 1

        canonical = (
            f"M1_MINCOUNTER[{mc['conjecture_name']}] "
            f"{mc['human_summary']} "
            f"(minimality_method={mc['minimality_certificate']['method']})"
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
                "conjecture_name": mc["conjecture_name"],
                "conjecture_statement": mc["conjecture_statement"],
                "ordering": mc["ordering"],
                "minimal_violator": mc["minimal_violator"],
                "minimal_violator_size": mc["minimal_violator_size"],
                "minimality_certificate": mc["minimality_certificate"],
                "logical_form": "extremal_violation_with_certificate",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
