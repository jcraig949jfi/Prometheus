"""F1 — Monte Carlo uniform random catalog pairs.

The null baseline for Family F. Uniformly samples (catalog_A_object,
catalog_B_object, invariant_A, invariant_B, relation) WITHOUT the
integer-only filter A1 applies and WITHOUT the coverage-aware weighting
that F2/F3/F4 apply. Anti-recommended in inventory.md for low info
density; ships as a calibration anchor — any F2/F3/F4 yield that fails
to beat F1's yield isn't earning its sampling sophistication.

The yield-score gap (F2/F3/F4 vs F1) is the empirical evidence that
coverage-aware sampling actually helps. If they don't beat F1, they
should be downweighted.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog,
    _evaluate_relation,
    _label,
    RELATIONS,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


# Wider net than A1: includes non-integer fields. F1 will skip non-numeric
# at evaluation time but record the attempt as INCONCLUSIVE.
KNOT_ANY_INVARIANTS = (
    "crossing_number",
    "signature",
    "determinant",
    "three_genus",
    "trace_field_class",
    "nf_class_number",
    "hyperbolic_volume",
    "alexander_polynomial_degree",
)

EC_ANY_INVARIANTS = (
    "rank",
    "conductor",
    "tamagawa_product",
    "torsion",
    "regulator",
    "discriminant",
    "j_invariant",
)


def _get_any(obj: Dict[str, Any], key: str) -> Optional[Any]:
    """Fetch any value from a possibly-nested catalog object."""
    if key in obj:
        return obj[key]
    if "base" in obj and isinstance(obj["base"], dict) and key in obj["base"]:
        return obj["base"][key]
    if "rich" in obj and isinstance(obj["rich"], dict) and key in obj["rich"]:
        return obj["rich"][key]
    return None


class F1MonteCarloRandomPairsGenerator(Generator):
    generator_id = "f1"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    status = GeneratorStatus.ACTIVE
    # Per advisory board Fire #53: f1 IS the null baseline by design.
    # Its yield curve calibrates what F2/F3/F4 sophistication adds.
    # Emissions are uniform-random claims with no sampling intelligence;
    # excluded from substrate discovery stats but kept active as the
    # calibration anchor.
    role = GeneratorRole.NULL_BASELINE

    def __init__(self, batch_id: str, seed: int = 1024) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)

    def description(self) -> str:
        return (
            f"f1: uniform-random catalog-pair sampling (NULL BASELINE; "
            f"{len(self._knots)} knots × {len(self._ecs)} ECs × "
            f"{len(KNOT_ANY_INVARIANTS) * len(EC_ANY_INVARIANTS)} "
            f"invariant pairs × {len(RELATIONS)} relations)"
        )

    def next(self) -> Optional[TheseusRecord]:
        # Uniform sample, NO retry budget for missing values. This is the
        # null baseline; we DO emit INCONCLUSIVE records when values are
        # missing or non-comparable. That's the whole point — the yield
        # score should reflect the cost of unbiased sampling.
        k = self._rng.choice(self._knots)
        e = self._rng.choice(self._ecs)
        ki = self._rng.choice(KNOT_ANY_INVARIANTS)
        ei = self._rng.choice(EC_ANY_INVARIANTS)
        rel = self._rng.choice(RELATIONS)

        a_raw = _get_any(k, ki)
        b_raw = _get_any(e, ei)
        a_val = self._to_int(a_raw)
        b_val = self._to_int(b_raw)

        knot_label = _label(k, "knot")
        ec_label = _label(e, "ec")

        self.attempts += 1

        if a_val is None or b_val is None:
            # Log demand signal: which catalog field was missing.
            try:
                from theseus.scoring.demand_signals import INSTANCE
                if a_val is None:
                    INSTANCE.record(
                        generator_id="f1", kind="missing_int_field",
                        signature=("knot", ki),
                    )
                if b_val is None:
                    INSTANCE.record(
                        generator_id="f1", kind="missing_int_field",
                        signature=("ec", ei),
                    )
            except Exception:
                pass
            # INCONCLUSIVE: value missing or non-numeric. Still emit so the
            # yield score reflects the cost of uniform sampling.
            canonical = (
                f"F1[uniform] {ki}(knot:{knot_label}) {rel} "
                f"{ei}(ec:{ec_label}) | values_unavailable"
            )
            payload = {
                "catalog_a": "knot",
                "object_a": knot_label,
                "invariant_a": ki,
                "value_a_raw": str(a_raw)[:64] if a_raw is not None else None,
                "catalog_b": "ec",
                "object_b": ec_label,
                "invariant_b": ei,
                "value_b_raw": str(b_raw)[:64] if b_raw is not None else None,
                "relation": rel,
                "holds": None,
            }
            verdict = Verdict.INCONCLUSIVE.value
            kill_pattern = None
        else:
            holds = _evaluate_relation(a_val, b_val, rel)
            canonical = (
                f"F1[uniform] {ki}(knot:{knot_label}) {rel} "
                f"{ei}(ec:{ec_label}) | {a_val} vs {b_val} | holds={holds}"
            )
            payload = {
                "catalog_a": "knot",
                "object_a": knot_label,
                "invariant_a": ki,
                "value_a": a_val,
                "catalog_b": "ec",
                "object_b": ec_label,
                "invariant_b": ei,
                "value_b": b_val,
                "relation": rel,
                "holds": holds,
            }
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"f1_relation_{rel}_violated"

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
            method="uniform_random_sampling",
            convergence_status="n/a",
            extras={"role": "null_baseline_uniform_sampling"},
        )
        self.emitted.append(record_id)
        return r

    @staticmethod
    def _to_int(v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            if v == int(v):
                return int(v)
            return None
        return None
