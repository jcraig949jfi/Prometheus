"""B1 — operator-rotation generator (composition-cycle test).

For object O, operator OP, integer n, predicts the n-fold composition
OP^n's effect on an integer invariant I, then verifies:

  predicted(I, OP, n) == I(OP^n(O))

For knot mirror: OP^2 = identity → signature(mirror^2(K)) == signature(K),
                                    crossing_number unchanged for all n.
For mirror^n in general: signature flips iff n is odd; other invariants
preserved.

B1 is a substrate self-test like C4: predicted == actual is a mathematical
fact on healthy operator implementations. Any REJECTED emission signals
a bug in the operator model.

v0.1 supports knot_mirror only. Tier 1 adds ec_quadratic_twist composition
properties (twist^2 = trivial-twist for many discriminants).
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Dict, List, Optional

from theseus.config import KNOTS_DB_PATH
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
    KNOT_INTEGER_INVARIANTS,
)


KNOT_MIRROR_INVARIANT_SIGN_FLIPS = {
    "signature": True,  # signature negates under mirror
    "crossing_number": False,
    "determinant": False,
    "three_genus": False,
    "trace_field_class": False,
    "nf_class_number": False,
}


def _predicted_after_mirror_n(invariant: str, original: int, n: int) -> Optional[int]:
    """Predict invariant value after n-fold mirror application.

    Returns None if the invariant isn't in the model (no prediction
    possible)."""
    if invariant not in KNOT_MIRROR_INVARIANT_SIGN_FLIPS:
        return None
    flips = KNOT_MIRROR_INVARIANT_SIGN_FLIPS[invariant]
    if not flips:
        return original  # preserved for all n
    # Sign flips: returns to original on even n, negates on odd n
    return original if n % 2 == 0 else -original


def _actual_after_mirror_n(obj: Dict, invariant: str, n: int) -> Optional[int]:
    """Simulate n-fold mirror application by repeated single-step mirror.

    The single-step mirror is the modeled operator from B5: signature
    flips, others preserve.
    """
    val = _get_int(obj, invariant)
    if val is None:
        return None
    if invariant not in KNOT_MIRROR_INVARIANT_SIGN_FLIPS:
        return None
    flips = KNOT_MIRROR_INVARIANT_SIGN_FLIPS[invariant]
    for _ in range(n):
        if flips:
            val = -val
        # preserved otherwise
    return val


class B1OperatorRotationGenerator(Generator):
    generator_id = "b1"
    claim_kind = ClaimKind.OPERATOR_ROTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 32) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        # n values to test: 2 (identity composition), 3 (odd flip), 4 (even),
        # 5 (odd), 8 (even). Cycle structure is exercised.
        self._n_values = (2, 3, 4, 5, 8)

    def description(self) -> str:
        return (
            f"b1: operator-rotation composition-cycle test "
            f"(knot_mirror^n for n ∈ {self._n_values}; substrate self-test)"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            k = self._rng.choice(self._knots)
            invariant = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            n = self._rng.choice(self._n_values)

            original = _get_int(k, invariant)
            if original is None:
                self.attempts += 1
                continue

            predicted = _predicted_after_mirror_n(invariant, original, n)
            actual = _actual_after_mirror_n(k, invariant, n)
            if predicted is None or actual is None:
                self.attempts += 1
                continue

            matches = predicted == actual
            verdict = (
                Verdict.SHADOW_CATALOG.value if matches
                else Verdict.REJECTED.value
            )
            kill_pattern = None if matches else (
                f"b1_mirror_n{n}_{invariant}_prediction_mismatch_"
                f"pred{predicted}_actual{actual}"
            )

            knot_label = _label(k, "knot")
            canonical = (
                f"B1_OPROT[mirror^{n}] {invariant}(knot:{knot_label}) "
                f"| original={original} predicted={predicted} actual={actual} "
                f"| matches={matches}"
            )
            payload = {
                "operator": "knot_mirror",
                "n_applications": n,
                "catalog": "knot",
                "object": knot_label,
                "invariant": invariant,
                "original_value": original,
                "predicted_value": predicted,
                "actual_value": actual,
                "matches": matches,
                "expected_sign_flip": KNOT_MIRROR_INVARIANT_SIGN_FLIPS.get(invariant),
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
                extras={"role": "operator_model_self_consistency_probe"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
