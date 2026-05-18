"""A3 — functional-identity generator.

For each (catalog_A, invariant_i, catalog_B, invariant_j) pair, test
whether `f(i(a)) RELATION g(j(b))` holds for some operator pair
(f, g) drawn from a small set of integer-valued unary transformations.

Extension of A1: instead of testing raw invariants directly, A3 applies
transformations (abs, neg, square_mod_small, identity, etc.) before
the relation check. This explores a larger claim space cheaply.

Frontier-aligned: this is the first step toward symbolic regression
(`docs/frontier_techniques_analysis.md` #2). A4 (next fire) will let
PySR-style search discover the (f, g) pair automatically.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

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


def _square_mod_small(v: int) -> int:
    """v^2 mod 100 — keeps values in a small range for tractable comparison."""
    return (v * v) % 100


def _log_floor(v: int) -> int:
    """⌊log_2|v|⌋ for nonzero, else 0."""
    if v == 0:
        return 0
    a = abs(v)
    out = 0
    while a > 1:
        a //= 2
        out += 1
    return out


OPERATORS: Dict[str, Callable[[int], int]] = {
    "identity": lambda v: v,
    "abs": abs,
    "neg": lambda v: -v,
    "sq_mod_100": _square_mod_small,
    "log2_floor": _log_floor,
    "mod_3": lambda v: v % 3,
}


class A3FunctionalIdentityGenerator(Generator):
    generator_id = "a3"
    claim_kind = ClaimKind.FUNCTIONAL_IDENTITY.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 31) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._op_names = list(OPERATORS.keys())

    def description(self) -> str:
        return (
            f"a3: functional-identity f(i(a)) RELATION g(j(b)) for "
            f"(f,g) ∈ ({len(OPERATORS)} ops)^2 × "
            f"({len(KNOT_INTEGER_INVARIANTS)} knot inv) × "
            f"({len(EC_INTEGER_INVARIANTS)} ec inv) × "
            f"({len(RELATIONS)} relations)"
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            k = self._rng.choice(self._knots)
            e = self._rng.choice(self._ecs)
            ki = self._rng.choice(KNOT_INTEGER_INVARIANTS)
            ei = self._rng.choice(EC_INTEGER_INVARIANTS)
            rel = self._rng.choice(RELATIONS)
            f_name = self._rng.choice(self._op_names)
            g_name = self._rng.choice(self._op_names)

            a_raw = _get_int(k, ki)
            b_raw = _get_int(e, ei)
            if a_raw is None or b_raw is None:
                self.attempts += 1
                continue

            try:
                fa = OPERATORS[f_name](a_raw)
                gb = OPERATORS[g_name](b_raw)
            except (ValueError, OverflowError):
                self.attempts += 1
                continue

            holds = _evaluate_relation(fa, gb, rel)
            self.attempts += 1

            knot_label = _label(k, "knot")
            ec_label = _label(e, "ec")
            canonical = (
                f"A3_FUNC[{f_name},{g_name}] "
                f"{f_name}({ki}(knot:{knot_label})) {rel} "
                f"{g_name}({ei}(ec:{ec_label})) "
                f"| {a_raw}→{fa} vs {b_raw}→{gb} | holds={holds}"
            )
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"a3_func_id_{f_name}_{g_name}_{rel}_violated"

            payload = {
                "catalog_a": "knot",
                "object_a": knot_label,
                "invariant_a": ki,
                "value_a_raw": a_raw,
                "value_a_transformed": fa,
                "operator_f": f_name,
                "catalog_b": "ec",
                "object_b": ec_label,
                "invariant_b": ei,
                "value_b_raw": b_raw,
                "value_b_transformed": gb,
                "operator_g": g_name,
                "relation": rel,
                "holds": holds,
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
            )
            self.emitted.append(record_id)
            return r

        return None
