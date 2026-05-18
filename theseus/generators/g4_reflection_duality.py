"""G4 — reflection-duality generator.

Tests whether a cross-catalog relation is INVARIANT under sign-reflection
of the knot-side invariant. For each (knot, EC, knot_inv, ec_inv, relation):
  rel(knot_inv(K), ec_inv(E))     -- "raw"
  rel(-knot_inv(K), ec_inv(E))    -- "reflected"

If both have the same truth value, the relation is "reflection-symmetric"
on the knot side. Many relations are reflection-symmetric (e.g.
equal_mod_2 is naturally symmetric for many invariants); others are not
(e.g. divides depends on sign).

Frontier-aligned: Information bottleneck / IRM (invariant risk
minimization) — these techniques optimize for invariances; G4 catalogs
which (relation, invariant) combinations naturally exhibit the symmetry.
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


class G4ReflectionDualityGenerator(Generator):
    generator_id = "g4"
    claim_kind = ClaimKind.SYMMETRY_TRANSFORM.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 210) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)

    def description(self) -> str:
        return (
            f"g4: reflection-duality on knot-side invariant (test "
            f"rel(v_a, v_b) == rel(-v_a, v_b))"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            k = self._rng.choice(self._knots)
            e = self._rng.choice(self._ecs)
            ki = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            ei = self._rng.choice(EC_INTEGER_INVARIANTS)
            rel = self._rng.choice(RELATIONS)

            a_val = _get_int(k, ki)
            b_val = _get_int(e, ei)
            if a_val is None or b_val is None:
                self.attempts += 1
                continue

            raw_holds = _evaluate_relation(a_val, b_val, rel)
            reflected_holds = _evaluate_relation(-a_val, b_val, rel)
            symmetric = raw_holds == reflected_holds

            verdict = (
                Verdict.SHADOW_CATALOG.value if symmetric
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if symmetric
                else f"g4_reflection_asymmetric_{ki}_{rel}_{ei}"
            )

            knot_label = _label(k, "knot")
            ec_label = _label(e, "ec")
            canonical = (
                f"G4_REFL[{ki}↔-{ki}] {ki}(knot:{knot_label}) {rel} "
                f"{ei}(ec:{ec_label}) | raw={a_val}:{raw_holds} "
                f"reflected={-a_val}:{reflected_holds} symmetric={symmetric}"
            )
            payload = {
                "catalog_a": "knot",
                "object_a": knot_label,
                "invariant_a": ki,
                "value_a": a_val,
                "reflected_value_a": -a_val,
                "catalog_b": "ec",
                "object_b": ec_label,
                "invariant_b": ei,
                "value_b": b_val,
                "relation": rel,
                "raw_holds": raw_holds,
                "reflected_holds": reflected_holds,
                "reflection_symmetric": symmetric,
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
                extras={"frontier_technique": "irm_invariance_via_reflection"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
