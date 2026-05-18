"""B4 — fixed-point hunt generator.

For each (op, v) tuple, tests whether `op(v) == v` — v is a fixed
point of op. Operator fixed-point structure:
  - identity: every v is a fixed point (trivially)
  - abs: fixed points are v ≥ 0
  - neg: fixed point is v = 0
  - sq_mod_100: v² ≡ v mod 100; many solutions (0, 1, 25, 76, etc)
  - log2_floor: only v = 0
  - mod_3: v mod 3 = v iff v ∈ {0, 1, 2}

Records map the per-operator fixed-point set. Substrate-native; no LLM
cost. Pair with B2 (commutativity) and B3 (self-inverse) to complete
operator-algebra mapping.

The records implicitly form a fixed-point catalog: aggregated over a
batch, each (op, v=fixed_point) emission is a confirmation that v ∈ Fix(op).
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


class B4FixedPointHuntGenerator(Generator):
    generator_id = "b4"
    claim_kind = ClaimKind.OPERATOR_ROTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 100) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._op_names = list(OPERATORS.keys())

    def description(self) -> str:
        return (
            f"b4: fixed-point hunt (op(v) == v?) for "
            f"{len(OPERATORS)} ops × v ∈ [-50, 50]"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            op_name = self._rng.choice(self._op_names)
            v = self._rng.randint(-50, 50)
            op = OPERATORS[op_name]
            try:
                op_v = op(v)
            except (ValueError, OverflowError):
                self.attempts += 1
                continue

            is_fixed_point = op_v == v
            # Identity trivializes; downweight by marking the kill_pattern
            non_trivial = op_name != "identity"

            verdict = (
                Verdict.SHADOW_CATALOG.value if is_fixed_point
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if is_fixed_point
                else f"b4_not_fixed_point_{op_name}_v{v}_giving_{op_v}"
            )

            canonical = (
                f"B4_FIX[{op_name}] v={v} | "
                f"{op_name}({v})={op_v} | is_fixed_point={is_fixed_point}"
                f"{' (trivial)' if not non_trivial else ''}"
            )
            payload = {
                "operator": op_name,
                "input_value": v,
                "op_v": op_v,
                "is_fixed_point": is_fixed_point,
                "non_trivial": non_trivial,
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
                extras={"role": "operator_algebra_mapping_fixedpoints"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
