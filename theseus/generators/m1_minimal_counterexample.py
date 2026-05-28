"""M1 — minimal counterexample generator (real, Stage 13).

Emits claims of the form:

    Conjecture C fails at minimum object M ∈ {P-objects ordered by size},
    certified by enumerating all P-objects of size < size(M) and
    verifying C holds on each.

Real implementation (Stage 13): a small set of stub-conjectures
defined as (conjecture statement, ordering function, predicate
"conjecture-holds-on-this-object"). The generator enumerates the
catalog in ordering order, finds the first violator (or none), and
emits a record with the actual minimality certificate.

Distinguished from l1:
- l1 emits "∄ X ∈ S : P(X)" with binary outcome
- m1 emits "smallest X ∈ S where P fails", plus enumeration receipt
  proving minimality. The certificate IS the artifact.

Plan: pivot/techne_5gen_plan_2026-05-27.md
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


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
# Conjecture templates
# ---------------------------------------------------------------------------
# Each template defines a (small) conjecture and:
#   - which catalog to enumerate
#   - the size/order key for "smallest"
#   - the predicate "C holds on this object" (True = C holds; False = violator)
# The generator finds the minimum violator and certifies minimality by
# logging all smaller objects that passed C.
# ---------------------------------------------------------------------------


def _size_ec_conductor(ec: dict) -> Optional[int]:
    base = ec.get("base") or {}
    return base.get("conductor")


def _size_knot_crossings(k: dict) -> Optional[int]:
    return k.get("crossing_number")


def _label_ec(ec: dict) -> str:
    base = ec.get("base") or {}
    return f"ec:{base.get('label') or base.get('cremona_label') or '?'}"


def _label_knot(k: dict) -> str:
    return f"knot:{k.get('name', '?')}"


# Each conjecture: returns True if C HOLDS on the object (so violators
# return False). We want the SMALLEST violator.
def _conj_ec_rank_le_2(ec: dict) -> bool:
    base = ec.get("base") or {}
    r = base.get("rank")
    return isinstance(r, int) and r <= 2


def _conj_ec_rank_le_3(ec: dict) -> bool:
    base = ec.get("base") or {}
    r = base.get("rank")
    return isinstance(r, int) and r <= 3


def _conj_ec_torsion_le_8(ec: dict) -> bool:
    rich = ec.get("rich") or {}
    t = rich.get("torsion")
    return isinstance(t, int) and t <= 8


def _conj_ec_tamagawa_le_4(ec: dict) -> bool:
    rich = ec.get("rich") or {}
    t = rich.get("tamagawa_product")
    return isinstance(t, int) and t <= 4


def _conj_knot_det_le_15(k: dict) -> bool:
    d = k.get("determinant")
    return isinstance(d, int) and d <= 15


def _conj_knot_signature_in_minus2_to_2(k: dict) -> bool:
    s = k.get("signature")
    return isinstance(s, int) and -2 <= s <= 2


def _conj_knot_three_genus_le_2(k: dict) -> bool:
    g = k.get("three_genus")
    return isinstance(g, int) and g <= 2


def _conj_knot_nf_class_eq_1(k: dict) -> bool:
    return k.get("nf_class_number") == 1


def _conj_ec_real_period_lt_5(ec: dict) -> bool:
    rich = ec.get("rich") or {}
    rp = rich.get("real_period")
    return isinstance(rp, (int, float)) and rp < 5.0


CONJECTURE_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "ec_rank_le_2",
        "domain": "ec",
        "conjecture_statement": "Every EC has analytic rank ≤ 2",
        "ordering_name": "conductor",
        "size_fn": _size_ec_conductor,
        "label_fn": _label_ec,
        "conjecture_fn": _conj_ec_rank_le_2,
        "human_summary": "Smallest EC (by conductor) with rank > 2",
    },
    {
        "id": "ec_rank_le_3",
        "domain": "ec",
        "conjecture_statement": "Every EC has analytic rank ≤ 3",
        "ordering_name": "conductor",
        "size_fn": _size_ec_conductor,
        "label_fn": _label_ec,
        "conjecture_fn": _conj_ec_rank_le_3,
        "human_summary": "Smallest EC (by conductor) with rank > 3",
    },
    {
        "id": "ec_torsion_le_8",
        "domain": "ec",
        "conjecture_statement": "Every EC torsion subgroup has |T| ≤ 8",
        "ordering_name": "conductor",
        "size_fn": _size_ec_conductor,
        "label_fn": _label_ec,
        "conjecture_fn": _conj_ec_torsion_le_8,
        "human_summary": "Smallest EC (by conductor) with |torsion| > 8",
    },
    {
        "id": "ec_tamagawa_le_4",
        "domain": "ec",
        "conjecture_statement": "Every EC has tamagawa_product ≤ 4",
        "ordering_name": "conductor",
        "size_fn": _size_ec_conductor,
        "label_fn": _label_ec,
        "conjecture_fn": _conj_ec_tamagawa_le_4,
        "human_summary": "Smallest EC (by conductor) with tamagawa_product > 4",
    },
    {
        "id": "knot_det_le_15",
        "domain": "knot",
        "conjecture_statement": "Every knot with crossing_number ≤ 10 has |det(K)| ≤ 15",
        "ordering_name": "crossing_number",
        "size_fn": _size_knot_crossings,
        "label_fn": _label_knot,
        "conjecture_fn": _conj_knot_det_le_15,
        "human_summary": "Smallest knot (by crossings) with |det| > 15",
    },
    {
        "id": "knot_signature_in_minus2_to_2",
        "domain": "knot",
        "conjecture_statement": "Every knot has signature ∈ [-2, 2]",
        "ordering_name": "crossing_number",
        "size_fn": _size_knot_crossings,
        "label_fn": _label_knot,
        "conjecture_fn": _conj_knot_signature_in_minus2_to_2,
        "human_summary": "Smallest knot (by crossings) with σ ∉ [-2, 2]",
    },
    {
        "id": "knot_three_genus_le_2",
        "domain": "knot",
        "conjecture_statement": "Every knot has three_genus ≤ 2",
        "ordering_name": "crossing_number",
        "size_fn": _size_knot_crossings,
        "label_fn": _label_knot,
        "conjecture_fn": _conj_knot_three_genus_le_2,
        "human_summary": "Smallest knot (by crossings) with g_3 > 2",
    },
    {
        "id": "knot_nf_class_eq_1",
        "domain": "knot",
        "conjecture_statement": "Every knot has nf_class_number = 1",
        "ordering_name": "crossing_number",
        "size_fn": _size_knot_crossings,
        "label_fn": _label_knot,
        "conjecture_fn": _conj_knot_nf_class_eq_1,
        "human_summary": "Smallest knot (by crossings) with h(K) ≠ 1",
    },
    {
        "id": "ec_real_period_lt_5",
        "domain": "ec",
        "conjecture_statement": "Every EC has real_period < 5",
        "ordering_name": "conductor",
        "size_fn": _size_ec_conductor,
        "label_fn": _label_ec,
        "conjecture_fn": _conj_ec_real_period_lt_5,
        "human_summary": "Smallest EC (by conductor) with real_period ≥ 5",
    },
]


class M1MinimalCounterexampleGenerator(Generator):
    generator_id = "m1"
    claim_kind = ClaimKind.MINIMAL_COUNTEREXAMPLE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        try:
            self._knots = _load_catalog(KNOTS_DB_PATH)
        except Exception:
            self._knots = []
        try:
            self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        except Exception:
            self._ecs = []
        self._cursor = 0

    def description(self) -> str:
        return (
            f"m1: minimal-counterexample (real) — {len(CONJECTURE_TEMPLATES)} "
            f"conjectures over {len(self._knots)} knots + {len(self._ecs)} ECs"
        )

    def _catalog_for(self, domain: str) -> List[dict]:
        return self._knots if domain == "knot" else self._ecs

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(CONJECTURE_TEMPLATES):
            tpl = CONJECTURE_TEMPLATES[self._cursor]
            self._cursor += 1
            self.attempts += 1

            catalog = self._catalog_for(tpl["domain"])
            # Filter to objects with a defined size, then sort
            with_size = [
                (tpl["size_fn"](o), o) for o in catalog
                if tpl["size_fn"](o) is not None
            ]
            with_size.sort(key=lambda x: x[0])

            minimal_violator = None
            minimal_size = None
            smaller_passing_sizes: List[int] = []
            smaller_passing_labels: List[str] = []
            enumerated = 0

            for size, obj in with_size:
                enumerated += 1
                try:
                    holds = tpl["conjecture_fn"](obj)
                except Exception:
                    continue
                if holds:
                    smaller_passing_sizes.append(size)
                    if len(smaller_passing_labels) < 50:
                        smaller_passing_labels.append(tpl["label_fn"](obj))
                else:
                    minimal_violator = obj
                    minimal_size = size
                    break

            if minimal_violator is not None:
                # Certificate should only contain STRICTLY smaller passing
                # objects (size ties at the violator's size don't certify
                # minimality at this size and confuse the schema).
                strict_smaller_sizes = [
                    s for s in smaller_passing_sizes if s < minimal_size
                ]
                same_size_passing_count = (
                    len(smaller_passing_sizes) - len(strict_smaller_sizes)
                )
                # Replace the accumulator with the filtered version.
                smaller_passing_sizes = strict_smaller_sizes
                verdict = Verdict.REJECTED.value
                violator_label = tpl["label_fn"](minimal_violator)
                outcome_str = (
                    f"FOUND minimal violator {violator_label} "
                    f"(size={minimal_size}); certified by enumerating "
                    f"{len(smaller_passing_sizes)} strictly-smaller "
                    f"objects (all passing); {same_size_passing_count} "
                    f"additional objects of the same size also passed"
                )
                kill_pattern = "minimal_counterexample_found"
            elif enumerated > 0:
                # No violator within the catalog → conjecture holds on
                # all enumerated objects.
                verdict = Verdict.SHADOW_CATALOG.value
                violator_label = None
                outcome_str = (
                    f"NO violator found across {enumerated} enumerated "
                    f"objects; conjecture holds within bound"
                )
                kill_pattern = None
            else:
                verdict = Verdict.UNVERIFIED.value
                violator_label = None
                outcome_str = "ENUMERATION_EMPTY"
                kill_pattern = None

            canonical = (
                f"M1_MINCOUNTER[{tpl['id']}] {tpl['human_summary']} — "
                f"{outcome_str}"
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
                    "conjecture_name": tpl["id"],
                    "conjecture_statement": tpl["conjecture_statement"],
                    "ordering": tpl["ordering_name"],
                    "minimal_violator": violator_label,
                    "minimal_violator_size": minimal_size,
                    "minimality_certificate": {
                        "method": "exhaustive_enumeration_by_size",
                        "enumerated_count": enumerated,
                        "smaller_passing_sizes": smaller_passing_sizes[:200],
                        "smaller_passing_labels_sample": smaller_passing_labels[:20],
                    },
                    "logical_form": "extremal_violation_with_certificate",
                    "outcome": outcome_str,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
