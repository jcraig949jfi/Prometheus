"""K1 — typed bridge generator (real version, Stage 11).

Emits claims encoding TYPED MORPHISM PATHS between mathematical domains:

    object --(typed_arrow_1)--> intermediate_1
            --(typed_arrow_2)--> intermediate_2 ...
            --(typed_arrow_n)--> target_value

Where existing generators (a1, f2, etc.) produce records of shape
"invariant_A(object_X) <relation> invariant_B(object_Y)" — flat
invariant pairs — k1 produces the full morphism chain.

Real implementation (Stage 11): defines an ARROW_REGISTRY mapping
(source_type, arrow_name) → callable that computes the target value
from a catalog object. Iterates (object, path) cross-product over
the knot + EC catalogs, emitting one record per (object, path) pair
with the computed target value attached.

Plan: pivot/techne_5gen_plan_2026-05-27.md
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable, Tuple

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


# ---------------------------------------------------------------------------
# Arrow registry
# ---------------------------------------------------------------------------
# Each arrow: (source_type, arrow_name) -> (target_type, callable(input)).
# Callable signature: takes an object dict and returns the target value
# or None if the arrow is not applicable (e.g., field missing).
# ---------------------------------------------------------------------------


def _arrow_knot_determinant(knot: dict) -> Optional[int]:
    return knot.get("determinant")


def _arrow_knot_signature(knot: dict) -> Optional[int]:
    return knot.get("signature")


def _arrow_knot_three_genus(knot: dict) -> Optional[int]:
    return knot.get("three_genus")


def _arrow_knot_hyperbolic_volume(knot: dict) -> Optional[float]:
    v = knot.get("hyperbolic_volume")
    return v if isinstance(v, (int, float)) and v > 0 else None


def _arrow_knot_to_nf_class_number(knot: dict) -> Optional[int]:
    return knot.get("nf_class_number")


def _arrow_knot_trace_field_class(knot: dict) -> Optional[int]:
    return knot.get("trace_field_class")


def _arrow_ec_conductor(ec: dict) -> Optional[int]:
    base = ec.get("base") or {}
    return base.get("conductor")


def _arrow_ec_rank(ec: dict) -> Optional[int]:
    base = ec.get("base") or {}
    return base.get("rank")


def _arrow_ec_torsion_order(ec: dict) -> Optional[int]:
    rich = ec.get("rich") or {}
    return rich.get("torsion")


def _arrow_ec_tamagawa(ec: dict) -> Optional[int]:
    rich = ec.get("rich") or {}
    return rich.get("tamagawa_product")


def _arrow_ec_real_period(ec: dict) -> Optional[float]:
    rich = ec.get("rich") or {}
    return rich.get("real_period")


def _arrow_abs(x: Any) -> Optional[int]:
    try:
        return abs(int(x))
    except (TypeError, ValueError):
        return None


def _arrow_mod_2(x: Any) -> Optional[int]:
    try:
        return int(x) % 2
    except (TypeError, ValueError):
        return None


def _arrow_mod_3(x: Any) -> Optional[int]:
    try:
        return int(x) % 3
    except (TypeError, ValueError):
        return None


# Each path is: [(arrow_name, source_type, target_type, callable), ...]
# When a path has multiple steps, the output of step n feeds into step n+1.
# First arrow takes the full object dict; subsequent arrows take a scalar.
TYPED_PATHS: List[Tuple[str, str, str, List[Tuple[str, str, str, Callable]]]] = [
    # (path_id, source_domain, source_object_key, [arrow chain])
    (
        "knot_det_abs",
        "knot",
        "knot",
        [
            ("determinant", "knot", "Z", _arrow_knot_determinant),
            ("absolute_value", "Z", "N", _arrow_abs),
        ],
    ),
    (
        "knot_sig_mod2",
        "knot",
        "knot",
        [
            ("signature", "knot", "Z", _arrow_knot_signature),
            ("mod_2", "Z", "Z/2Z", _arrow_mod_2),
        ],
    ),
    (
        "knot_three_genus_direct",
        "knot",
        "knot",
        [
            ("three_genus", "knot", "Z", _arrow_knot_three_genus),
        ],
    ),
    (
        "knot_hyperbolic_volume_direct",
        "knot",
        "knot",
        [
            ("hyperbolic_volume", "knot", "R", _arrow_knot_hyperbolic_volume),
        ],
    ),
    (
        "knot_nf_class_number",
        "knot",
        "knot",
        [
            ("nf_class_number", "knot", "N", _arrow_knot_to_nf_class_number),
        ],
    ),
    (
        "knot_trace_field_class_mod2",
        "knot",
        "knot",
        [
            ("trace_field_class", "knot", "Z", _arrow_knot_trace_field_class),
            ("mod_2", "Z", "Z/2Z", _arrow_mod_2),
        ],
    ),
    (
        "ec_conductor_mod3",
        "ec",
        "ec",
        [
            ("conductor", "ec", "Z", _arrow_ec_conductor),
            ("mod_3", "Z", "Z/3Z", _arrow_mod_3),
        ],
    ),
    (
        "ec_rank_direct",
        "ec",
        "ec",
        [
            ("rank", "ec", "Z", _arrow_ec_rank),
        ],
    ),
    (
        "ec_torsion_order_direct",
        "ec",
        "ec",
        [
            ("torsion_order", "ec", "N", _arrow_ec_torsion_order),
        ],
    ),
    (
        "ec_tamagawa_mod2",
        "ec",
        "ec",
        [
            ("tamagawa_product", "ec", "N", _arrow_ec_tamagawa),
            ("mod_2", "N", "Z/2Z", _arrow_mod_2),
        ],
    ),
    (
        "ec_real_period_direct",
        "ec",
        "ec",
        [
            ("real_period", "ec", "R", _arrow_ec_real_period),
        ],
    ),
]


def _load_catalog(path) -> List[dict]:
    p = str(path)
    if p.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    return data.get("entries", []) if isinstance(data, dict) else data


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


class K1TypedBridgeGenerator(Generator):
    generator_id = "k1"
    claim_kind = ClaimKind.TYPED_BRIDGE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    # Bound iteration so daemon doesn't enumerate every (knot × path)
    # combo forever on first .next(). Caller can override.
    MAX_RECORDS_PER_BATCH = 5000

    def __init__(
        self,
        batch_id: str,
        max_records: Optional[int] = None,
    ) -> None:
        super().__init__(batch_id)
        self._max = max_records if max_records is not None else self.MAX_RECORDS_PER_BATCH
        try:
            self._knots = _load_catalog(KNOTS_DB_PATH)
        except Exception:
            self._knots = []
        try:
            self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        except Exception:
            self._ecs = []
        # Pre-compute the (path, object) iteration order
        self._queue: List[Tuple[str, str, str, List[Tuple], dict]] = []
        for path_id, source_domain, source_object_key, arrows in TYPED_PATHS:
            objects = self._knots if source_domain == "knot" else self._ecs
            for obj in objects:
                self._queue.append((path_id, source_domain, source_object_key, arrows, obj))
        self._cursor = 0

    def description(self) -> str:
        return (
            f"k1: typed-bridge (real) — {len(TYPED_PATHS)} paths × "
            f"{len(self._knots)} knots + {len(self._ecs)} ECs "
            f"= {len(self._queue)} candidate emissions"
        )

    def _object_label(self, source_domain: str, obj: dict) -> str:
        if source_domain == "knot":
            return f"knot:{obj.get('name', '?')}"
        base = obj.get("base") or {}
        return f"ec:{base.get('label', base.get('cremona_label', '?'))}"

    def _evaluate_path(
        self, obj: dict, arrows: List[Tuple]
    ) -> Tuple[Optional[Any], int]:
        """Evaluate the arrow chain. Returns (final_value, steps_completed)."""
        value: Any = obj
        steps = 0
        for arrow_name, source_type, target_type, fn in arrows:
            try:
                value = fn(value)
            except Exception:
                return (None, steps)
            steps += 1
            if value is None:
                return (None, steps)
        return (value, steps)

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(self._queue) and self.attempts < self._max:
            path_id, source_domain, _src_obj_key, arrows, obj = self._queue[self._cursor]
            self._cursor += 1
            self.attempts += 1

            target_value, steps_completed = self._evaluate_path(obj, arrows)
            # Skip records whose arrow chain couldn't compute (catalog gap).
            if target_value is None:
                continue
            obj_label = self._object_label(source_domain, obj)

            human_chain = " → ".join(
                f"{a[0]} ({a[1]}→{a[2]})" for a in arrows
            )
            canonical = (
                f"K1_TYPED_BRIDGE[{path_id}] {obj_label} "
                f"⟶ {human_chain} = {target_value}"
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
                    "path_id": path_id,
                    "source_domain": source_domain,
                    "source_object": obj_label,
                    "arrow_chain": [
                        {"arrow": a[0], "source_type": a[1], "target_type": a[2]}
                        for a in arrows
                    ],
                    "expected_target_type": arrows[-1][2],
                    "target_value": target_value,
                    "path_length": len(arrows),
                    "steps_completed": steps_completed,
                },
                canonical_claim_text=canonical,
                verdict=Verdict.UNVERIFIED.value,
            )
        return None
