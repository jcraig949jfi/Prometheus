"""G5 — scale-invariance test.

For each (relation, invariant pair, scalar k), tests whether
`rel(k·a, k·b) == rel(a, b)`. Maps which (relation, k) combinations
are scale-invariant.

Math:
- equal: a==b iff k·a==k·b (k≠0) — preserves
- equal_mod_2: a≡b mod 2 iff k·a≡k·b mod 2 — preserves iff k is odd
  (for k=2, 2a==2b mod 2 always; trivially preserves)
- divides: a|b iff k·a|k·b — preserves
- abs_diff_le_K: |a-b|≤K → |k·a - k·b|≤K — FAILS for k>1 (LHS grows)

G5 catalogs these per (relation, k) combination empirically; the
substrate doesn't trust the analytic predictions.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Optional

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog,
    _get_int,
    _label,
    _evaluate_relation,
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
    RELATIONS,
)


SCALE_FACTORS = (2, 3, 5)


class G5ScaleInvarianceGenerator(Generator):
    generator_id = "g5"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 240) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)

    def description(self) -> str:
        return (
            f"g5: scale-invariance test (rel(k·a, k·b) == rel(a, b) "
            f"for k ∈ {SCALE_FACTORS})"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            k_obj = self._rng.choice(self._knots)
            e_obj = self._rng.choice(self._ecs)
            ki = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            ei = self._rng.choice(EC_INTEGER_INVARIANTS)
            rel = self._rng.choice(RELATIONS)
            scale = self._rng.choice(SCALE_FACTORS)

            a_val = _get_int(k_obj, ki)
            b_val = _get_int(e_obj, ei)
            if a_val is None or b_val is None:
                self.attempts += 1
                continue

            raw_holds = _evaluate_relation(a_val, b_val, rel)
            scaled_holds = _evaluate_relation(
                scale * a_val, scale * b_val, rel
            )
            invariant_under_scale = raw_holds == scaled_holds

            verdict = (
                Verdict.SHADOW_CATALOG.value if invariant_under_scale
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if invariant_under_scale
                else f"g5_scale_k{scale}_breaks_{rel}"
            )

            knot_label = _label(k_obj, "knot")
            ec_label = _label(e_obj, "ec")
            canonical = (
                f"G5_SCALE[k={scale}] {ki}(knot:{knot_label}) {rel} "
                f"{ei}(ec:{ec_label}) | raw={a_val},{b_val}→{raw_holds} "
                f"scaled={scale * a_val},{scale * b_val}→{scaled_holds} "
                f"| invariant={invariant_under_scale}"
            )
            payload = {
                "catalog_a": "knot",
                "object_a": knot_label,
                "invariant_a": ki,
                "value_a": a_val,
                "scaled_value_a": scale * a_val,
                "catalog_b": "ec",
                "object_b": ec_label,
                "invariant_b": ei,
                "value_b": b_val,
                "scaled_value_b": scale * b_val,
                "relation": rel,
                "scale_factor": scale,
                "raw_holds": raw_holds,
                "scaled_holds": scaled_holds,
                "scale_invariant": invariant_under_scale,
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
                extras={"frontier_technique": "scale_invariance_mapping"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
