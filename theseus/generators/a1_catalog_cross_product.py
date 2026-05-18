"""A1 — catalog-cross-product generator.

For each pair (catalog_A, catalog_B), pick objects (a, b) and integer
invariants (i, j), emit a claim of form `i(a) RELATION j(b)` where
RELATION is one of {equal, equal_mod_2, divides, abs_diff_le_K}.

The generator is mathematically agnostic — it produces structured
cross-catalog claims at volume. Info-density scoring filters out
trivial/uninteresting pairings; bandit downweights low-yield catalog
pairs over time.

v0.1 catalogs: knots × ECs (BSD-rich) — the cleanest two pre-loaded
databases. Genus-2 + modular forms wired in Tier 1.
"""
from __future__ import annotations

import gzip
import json
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus


# Integer-valued invariants per catalog
KNOT_INTEGER_INVARIANTS = (
    "crossing_number",
    "signature",
    "determinant",
    "three_genus",
    "trace_field_class",
    "nf_class_number",
)

EC_INTEGER_INVARIANTS = (
    "rank",
    "conductor",
    "tamagawa_product",
    "torsion",
)

RELATIONS = ("equal", "equal_mod_2", "divides", "abs_diff_le_3")


def _load_catalog(path) -> List[Dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.get("entries", []))


def _get_int(obj: Dict[str, Any], key: str) -> Optional[int]:
    """Safely fetch an integer invariant; handles nested EC schema."""
    if key in obj:
        v = obj[key]
        return int(v) if isinstance(v, (int, float)) and v == int(v) else None
    # EC entries have nested base/rich
    if "base" in obj and key in obj["base"]:
        v = obj["base"][key]
        return int(v) if isinstance(v, (int, float)) and v == int(v) else None
    if "rich" in obj and key in obj["rich"]:
        v = obj["rich"][key]
        return int(v) if isinstance(v, (int, float)) and v == int(v) else None
    return None


def _evaluate_relation(a_val: int, b_val: int, relation: str) -> bool:
    if relation == "equal":
        return a_val == b_val
    if relation == "equal_mod_2":
        return (a_val % 2) == (b_val % 2)
    if relation == "divides":
        if b_val == 0:
            return False
        return (b_val % a_val) == 0 if a_val != 0 else False
    if relation == "abs_diff_le_3":
        return abs(a_val - b_val) <= 3
    return False


def _label(obj: Dict[str, Any], catalog: str) -> str:
    if catalog == "knot":
        return str(obj.get("name", "?"))
    if catalog == "ec":
        return str(obj.get("base", {}).get("label", "?"))
    return "?"


class A1CatalogCrossProductGenerator(Generator):
    generator_id = "a1"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 0,
        max_claims_per_call: int = 1,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._max_per_call = max_claims_per_call

    def description(self) -> str:
        return (
            f"a1: catalog-cross-product knot×EC integer-invariant "
            f"relations ({len(self._knots)} knots × {len(self._ecs)} ECs "
            f"× {len(KNOT_INTEGER_INVARIANTS) * len(EC_INTEGER_INVARIANTS)} "
            f"invariant pairs × {len(RELATIONS)} relations)"
        )

    def next(self) -> Optional[TheseusRecord]:
        # Sample one (knot, ec, knot_inv, ec_inv, relation) tuple
        for _ in range(20):  # retry budget on missing-value combos
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

            holds = _evaluate_relation(a_val, b_val, rel)
            self.attempts += 1

            knot_label = _label(k, "knot")
            ec_label = _label(e, "ec")
            canonical = (
                f"{ki}(knot:{knot_label}) {rel} {ei}(ec:{ec_label}) "
                f"| {a_val} vs {b_val} | holds={holds}"
            )

            verdict = (
                Verdict.SHADOW_CATALOG.value if holds else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"a1_relation_{rel}_violated"

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
                precision_dps=None,
                method="exact",
                convergence_status="exact",
            )
            self.emitted.append(record_id)
            return r

        return None  # exhausted retry budget
