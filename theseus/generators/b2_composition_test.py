"""B2 — operator composition commutativity test.

For each (op1, op2) pair drawn from a set of integer-transform operators,
tests whether `op1(op2(v)) == op2(op1(v))` for many integer values v.
Most operator pairs don't commute; some do (identity commutes with all,
neg-and-abs commute since |-v| = |v| then negated == -|v|... no wait,
that's not quite right either).

The substrate's value here: maps the algebraic structure of the operator
set. Each emission is a single (op1, op2, v) instance; the bandit will
aggregate per-pair commutativity over a batch.

Frontier-aligned: this is a small step toward Information Bottleneck /
IRM (invariant risk minimization), where commutative structure is
exactly the kind of operator-invariance signal those frameworks
optimize for.
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


class B2CompositionTestGenerator(Generator):
    generator_id = "b2"
    claim_kind = ClaimKind.COMPOSITION_TEST.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 70) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._op_names = list(OPERATORS.keys())

    def description(self) -> str:
        return (
            f"b2: operator-composition commutativity test "
            f"({len(OPERATORS)}² = {len(OPERATORS) ** 2} pairs; "
            f"v drawn from [-50, 50])"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            f_name = self._rng.choice(self._op_names)
            g_name = self._rng.choice(self._op_names)
            v = self._rng.randint(-50, 50)

            try:
                fg = OPERATORS[f_name](OPERATORS[g_name](v))
                gf = OPERATORS[g_name](OPERATORS[f_name](v))
            except (ValueError, OverflowError):
                self.attempts += 1
                continue

            commutes = fg == gf
            verdict = (
                Verdict.SHADOW_CATALOG.value if commutes
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if commutes
                else f"b2_noncommute_{f_name}_{g_name}_v{v}"
            )

            canonical = (
                f"B2_COMM[{f_name},{g_name}] "
                f"v={v} | {f_name}({g_name}({v}))={fg} vs "
                f"{g_name}({f_name}({v}))={gf} | commutes={commutes}"
            )
            payload = {
                "operator_f": f_name,
                "operator_g": g_name,
                "input_value": v,
                "fg_result": fg,
                "gf_result": gf,
                "commutes": commutes,
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
                extras={"role": "operator_algebra_mapping"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
