"""K1 — typed bridge generator.

Emits claims encoding TYPED MORPHISM PATHS between mathematical
domains, not just untyped invariant pairs. Where existing generators
(a1, f2, etc.) produce records of shape:

    invariant_A(object_X) <relation> invariant_B(object_Y)

K1 produces:

    object_X --(typed_arrow_1)--> intermediate_1
            --(typed_arrow_2)--> intermediate_2 ...
            --(typed_arrow_n)--> value

with the chain of types and arrows explicit. Two records can share
both endpoints but trace different paths, which encodes mathematical
structure that flat invariant pairs cannot.

Stage 2 / Stage 1-of-implementation: STUB. Emits a small hand-coded
set of typed paths from existing catalogs to validate the SHAPE.
Iteration to a useful version is gated on Stage 8 validation fires.

Plan: pivot/techne_5gen_plan_2026-05-27.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Tuple

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


# Stub-level typed paths. Each path is a tuple of:
#   (source_domain, source_object_template, arrow_chain, expected_target_type)
# Real implementation will pull these from a typed-bridge catalog;
# this is the smallest meaningful set that exercises the SHAPE.
STUB_TYPED_PATHS: List[dict] = [
    {
        "source_domain": "knot",
        "source_object_pattern": "knot:5_2",
        "arrow_chain": [
            ("trace_field", "knot", "number_field"),
            ("class_group_order", "number_field", "Z"),
        ],
        "expected_target_type": "Z",
        "human_summary": (
            "knot:5_2 → trace_field → number_field "
            "→ class_group_order → Z"
        ),
    },
    {
        "source_domain": "ec",
        "source_object_pattern": "ec:11.a1",
        "arrow_chain": [
            ("conductor", "ec", "Z"),
            ("modulo_prime", "Z", "Z/pZ"),
        ],
        "expected_target_type": "Z/pZ",
        "human_summary": (
            "ec:11.a1 → conductor → Z → modulo_prime → Z/pZ"
        ),
    },
    {
        "source_domain": "knot",
        "source_object_pattern": "knot:7_3",
        "arrow_chain": [
            ("alexander_polynomial", "knot", "Z[t,t^-1]"),
            ("evaluate_at_minus_one", "Z[t,t^-1]", "Z"),
            ("absolute_value", "Z", "N"),
        ],
        "expected_target_type": "N",
        "human_summary": (
            "knot:7_3 → alexander_polynomial → Z[t,t^-1] "
            "→ evaluate_at_minus_one → Z → absolute_value → N "
            "(= |determinant|)"
        ),
    },
    {
        "source_domain": "ec",
        "source_object_pattern": "ec:37.a1",
        "arrow_chain": [
            ("l_function", "ec", "Dirichlet_series"),
            ("analytic_rank", "Dirichlet_series", "N"),
        ],
        "expected_target_type": "N",
        "human_summary": (
            "ec:37.a1 → l_function → Dirichlet_series "
            "→ analytic_rank → N"
        ),
    },
]


class K1TypedBridgeGenerator(Generator):
    generator_id = "k1"
    claim_kind = ClaimKind.TYPED_BRIDGE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return (
            f"k1: typed-bridge stub "
            f"({len(STUB_TYPED_PATHS)} hand-coded morphism paths)"
        )

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(STUB_TYPED_PATHS):
            return None
        path = STUB_TYPED_PATHS[self._cursor]
        self._cursor += 1
        self.attempts += 1

        canonical = (
            f"K1_TYPED_BRIDGE[{path['source_object_pattern']}] "
            f"{path['human_summary']}"
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
                "source_domain": path["source_domain"],
                "source_object": path["source_object_pattern"],
                "arrow_chain": [
                    {"arrow": a, "source_type": s, "target_type": t}
                    for (a, s, t) in path["arrow_chain"]
                ],
                "expected_target_type": path["expected_target_type"],
                "path_length": len(path["arrow_chain"]),
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
