"""B5 — conservation-law generator.

For (catalog, invariant, operator) triples, test whether the invariant
is preserved when the operator is applied. v0.1 operators are
catalog-native transformations (e.g. for knots: mirror reflection,
which negates signature; for ECs: quadratic twist, which can change
rank but should preserve conductor's radical).

Conservation-law claims naturally produce KILLS when the operator
does change the invariant, and SURVIVALS when it doesn't. Both are
informative.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

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
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH


# Operators: name -> (catalog, fn:obj->modified_invariant_values_dict)
# v0.1 operators are stubs that simulate known structural effects.
# Real operators wired in Tier 1 once we have catalog-native primitives.


def _knot_mirror_op(obj: Dict[str, Any]) -> Dict[str, Optional[int]]:
    """Mirror reflection: negates signature, preserves others."""
    sig = _get_int(obj, "signature")
    return {
        "crossing_number": _get_int(obj, "crossing_number"),
        "signature": -sig if sig is not None else None,
        "determinant": _get_int(obj, "determinant"),
        "three_genus": _get_int(obj, "three_genus"),
    }


def _ec_quadratic_twist_op_modeled(obj: Dict[str, Any]) -> Dict[str, Optional[int]]:
    """Quadratic twist (modeled): preserves conductor's radical structure
    but can flip parity of rank. v0.1 model: rank stays, conductor stays,
    tamagawa product may change. Real implementation in Tier 1."""
    return {
        "rank": _get_int(obj, "rank"),
        "conductor": _get_int(obj, "conductor"),
        "tamagawa_product": _get_int(obj, "tamagawa_product"),
        "torsion": _get_int(obj, "torsion"),
    }


OPERATORS = (
    ("knot_mirror", "knot", _knot_mirror_op,
     ("signature",), ("crossing_number", "determinant", "three_genus")),
    ("ec_quad_twist_modeled", "ec", _ec_quadratic_twist_op_modeled,
     (), ("rank", "conductor", "tamagawa_product", "torsion")),
)


class B5ConservationLawGenerator(Generator):
    generator_id = "b5"
    claim_kind = ClaimKind.CONSERVATION_LAW.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 1) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)

    def description(self) -> str:
        return (
            f"b5: conservation-law ({len(OPERATORS)} operators × "
            f"per-catalog invariants × catalog size)"
        )

    def _pick_object(self, catalog: str) -> Dict[str, Any]:
        if catalog == "knot":
            return self._rng.choice(self._knots)
        return self._rng.choice(self._ecs)

    def next(self) -> Optional[TheseusRecord]:
        op_name, catalog, op_fn, expected_change, expected_preserve = (
            self._rng.choice(OPERATORS)
        )
        obj = self._pick_object(catalog)

        # Apply operator; check which invariants change
        pre = {
            inv: _get_int(obj, inv)
            for inv in (expected_change + expected_preserve)
        }
        post = op_fn(obj)

        actually_changed: List[str] = []
        actually_preserved: List[str] = []
        for inv, pre_v in pre.items():
            post_v = post.get(inv)
            if pre_v is None or post_v is None:
                continue
            if pre_v == post_v:
                actually_preserved.append(inv)
            else:
                actually_changed.append(inv)

        # Conservation claim: "all of expected_preserve are preserved AND
        # all of expected_change are changed" — the predicted operator
        # behavior.
        holds = (
            all(inv in actually_preserved for inv in expected_preserve)
            and all(inv in actually_changed for inv in expected_change)
        )

        verdict = (
            Verdict.SHADOW_CATALOG.value if holds else Verdict.REJECTED.value
        )
        kill_pattern = None if holds else f"b5_conservation_violated_{op_name}"

        obj_label = _label(obj, catalog)
        canonical = (
            f"operator={op_name} object={catalog}:{obj_label} "
            f"changed={actually_changed} preserved={actually_preserved} "
            f"expected_change={list(expected_change)} "
            f"expected_preserve={list(expected_preserve)} holds={holds}"
        )

        payload = {
            "operator": op_name,
            "catalog": catalog,
            "object": obj_label,
            "expected_change": list(expected_change),
            "expected_preserve": list(expected_preserve),
            "actually_changed": actually_changed,
            "actually_preserved": actually_preserved,
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
        self.attempts += 1
        self.emitted.append(record_id)
        return r
