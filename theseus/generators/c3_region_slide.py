"""C3 — region-slide mutation generator.

Picks a verified parent claim and slides the INVARIANT SLOT (one of
knot_invariant or ec_invariant) to a different choice in the same
catalog, keeping objects + relation fixed. This is orthogonal to C1
(swap OBJECT) and C2 (swap THRESHOLD) — C3 perturbs along the
INVARIANT axis.

For example: parent claims `signature(3_1) abs_diff_le_3 rank(11a1)`.
C3 slides invariant_a to `crossing_number`: `crossing_number(3_1)
abs_diff_le_3 rank(11a1)`. Retests with new value_a.

Each emission maps how much the relation depends on the specific
invariant choice. Records with SHADOW_CATALOG verdict reveal
invariant-substitutable relations; REJECTED records pin the relation
to the specific invariants.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List, Optional

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    A1CatalogCrossProductGenerator,
    _load_catalog,
    _get_int,
    _evaluate_relation,
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
)


class C3RegionSlideGenerator(Generator):
    generator_id = "c3"
    claim_kind = ClaimKind.MUTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 120,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":c3seed", seed=seed + 900
        )

    def description(self) -> str:
        return "c3: invariant-slot slide (different invariant, same objects)"

    def add_parent(self, record: TheseusRecord) -> None:
        if record.verdict != Verdict.SHADOW_CATALOG.value:
            return
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b",
                  "value_a", "value_b", "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict == Verdict.SHADOW_CATALOG.value:
                return r
        return None

    def _find_knot(self, label: str):
        return next((k for k in self._knots if k.get("name") == label), None)

    def _find_ec(self, label: str):
        return next(
            (e for e in self._ecs if e.get("base", {}).get("label") == label),
            None,
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            if self._parents:
                parent = self._rng.choice(self._parents)
            else:
                parent = self._bootstrap_parent()
                if parent is None:
                    return None

            p = parent.claim_payload
            slide_side = self._rng.choice(("a", "b"))
            if slide_side == "a":
                new_inv = self._rng.choice(
                    [i for i in KNOT_INTEGER_INVARIANTS if i != p["invariant_a"]]
                )
                k = self._find_knot(p["object_a"])
                if k is None:
                    self.attempts += 1
                    continue
                new_val = _get_int(k, new_inv)
                if new_val is None:
                    self.attempts += 1
                    continue
                a_val, b_val = new_val, p["value_b"]
                inv_a, inv_b = new_inv, p["invariant_b"]
            else:
                new_inv = self._rng.choice(
                    [i for i in EC_INTEGER_INVARIANTS if i != p["invariant_b"]]
                )
                e = self._find_ec(p["object_b"])
                if e is None:
                    self.attempts += 1
                    continue
                new_val = _get_int(e, new_inv)
                if new_val is None:
                    self.attempts += 1
                    continue
                a_val, b_val = p["value_a"], new_val
                inv_a, inv_b = p["invariant_a"], new_inv

            rel = p["relation"]
            new_holds = _evaluate_relation(a_val, b_val, rel)

            verdict = (
                Verdict.SHADOW_CATALOG.value if new_holds
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if new_holds
                else f"c3_slide_{slide_side}_inv_breaks_{rel}"
            )

            canonical = (
                f"C3_SLIDE[{slide_side}:{p[f'invariant_{slide_side}']}"
                f"→{inv_a if slide_side == 'a' else inv_b}] "
                f"{inv_a}(knot:{p['object_a']}) {rel} "
                f"{inv_b}(ec:{p['object_b']}) | "
                f"{a_val} vs {b_val} | holds={new_holds}"
            )
            payload = {
                "parent_record_id": parent.record_id,
                "slide_side": slide_side,
                "original_invariant_a": p["invariant_a"],
                "original_invariant_b": p["invariant_b"],
                "invariant_a": inv_a,
                "invariant_b": inv_b,
                "object_a": p["object_a"],
                "object_b": p["object_b"],
                "value_a": a_val,
                "value_b": b_val,
                "relation": rel,
                "holds": new_holds,
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
                parent_record_id=parent.record_id,
                method="exact",
                convergence_status="exact",
                extras={"mutation_axis": "invariant_slot"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
