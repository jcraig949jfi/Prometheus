"""B3 — inverse / self-inverse property test.

For each (op, v) tuple, tests whether `op(op(v)) == v` — the self-
inverse property of the operator at the value v. Some operators are
self-inverse globally (identity, neg); some are self-inverse only on
a subdomain (abs is self-inverse for v ≥ 0); some are never self-
inverse beyond trivial fixed points (sq_mod_100, log2_floor, mod_3).

Records carry the test outcome; verdict-distribution per operator
maps the algebraic subdomain on which each operator is self-inverse.
Substrate-native; no LLM cost.

Pair with B2 (commutativity) and B4 (fixed points) to fully map the
local algebraic structure of the integer-transform operator set.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List, Optional

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a3_functional_identity import OPERATORS


class B3InverseTestGenerator(Generator):
    generator_id = "b3"
    claim_kind = ClaimKind.COMPOSITION_TEST.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 90) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._op_names = list(OPERATORS.keys())

    def description(self) -> str:
        return (
            f"b3: self-inverse-at-v test (op(op(v)) == v) for "
            f"{len(OPERATORS)} ops × v ∈ [-50, 50]"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            op_name = self._rng.choice(self._op_names)
            v = self._rng.randint(-50, 50)
            op = OPERATORS[op_name]
            try:
                op_v = op(v)
                op_op_v = op(op_v)
            except (ValueError, OverflowError):
                self.attempts += 1
                continue

            self_inverse_at_v = op_op_v == v
            verdict = (
                Verdict.SHADOW_CATALOG.value if self_inverse_at_v
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if self_inverse_at_v
                else f"b3_not_self_inverse_{op_name}_v{v}_giving_{op_op_v}"
            )

            canonical = (
                f"B3_INV[{op_name}] v={v} | "
                f"{op_name}({v})={op_v}, {op_name}({op_name}({v}))={op_op_v} "
                f"| self_inverse={self_inverse_at_v}"
            )
            payload = {
                "operator": op_name,
                "input_value": v,
                "op_v": op_v,
                "op_op_v": op_op_v,
                "self_inverse_at_v": self_inverse_at_v,
            }
            record_id = TheseusRecord.compute_record_id(
                canonical_claim_text=canonical,
                generator_id=self.generator_id,
            )
            r = TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload=payload,
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
                method="exact",
                convergence_status="exact",
                extras={"role": "operator_algebra_mapping_inverse"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
