"""S1 — triangle inequality / metric structure generator (stub, Stage 20).

Emits claims testing |f(X) - f(Z)| ≤ |f(X) - f(Y)| + |f(Y) - f(Z)|
for triples of catalog objects and various invariant functions f.
Tests whether invariants induce a metric.

From Sphinx domain H (Spatial / Metric).
Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


TRIANGLE_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_conductor_metric_holds_on_3_curves",
        "invariant": "conductor",
        "objects": ["ec:11.a1", "ec:37.a1", "ec:5077.a1"],
        "expected_outcome": "triangle inequality holds (conductor is a valid pseudo-metric)",
    },
    {
        "id": "knot_three_genus_metric_holds",
        "invariant": "three_genus",
        "objects": ["knot:3_1", "knot:5_2", "knot:8_3"],
        "expected_outcome": "triangle inequality holds (genus is a valid pseudo-metric)",
    },
    {
        "id": "ec_rank_NOT_metric_fails_on_some_triple",
        "invariant": "rank",
        "objects": ["ec:11.a1", "ec:5077.a1", "ec:234446.a1"],
        "expected_outcome": "triangle inequality may fail (rank is not metric in general)",
    },
    {
        "id": "knot_signature_metric_check",
        "invariant": "abs(signature)",
        "objects": ["knot:3_1", "knot:5_1", "knot:7_3"],
        "expected_outcome": "|σ| satisfies triangle inequality (abs of integer difference)",
    },
]


class S1TriangleInequalityGenerator(Generator):
    generator_id = "s1"
    claim_kind = ClaimKind.TRIANGLE_INEQUALITY.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        self._cursor = 0

    def description(self) -> str:
        return f"s1: triangle_inequality ({len(TRIANGLE_CLAIMS)} claims)"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(TRIANGLE_CLAIMS):
            return None
        c = TRIANGLE_CLAIMS[self._cursor]
        self._cursor += 1
        self.attempts += 1
        canonical = (
            f"S1_TRIANGLE[{c['id']}] "
            f"|{c['invariant']}(A)-{c['invariant']}(C)| ≤ "
            f"|{c['invariant']}(A)-{c['invariant']}(B)| + "
            f"|{c['invariant']}(B)-{c['invariant']}(C)| "
            f"on {c['objects']}: {c['expected_outcome']}"
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
                "invariant": c["invariant"],
                "objects": c["objects"],
                "expected_outcome": c["expected_outcome"],
                "logical_form": "metric_triangle_inequality",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
