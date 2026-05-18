"""C1 — claim-mutation generator.

Mutates an existing TheseusRecord by swapping the object variable in
its payload, then retests. The parent_record_id field carries lineage.

C1 needs a *source* of parent claims — for v0.1, it can either:
- accept an in-memory list of recent records (default), or
- replay records from a prior batch's corpus JSONL file.

If no parent claims exist, C1 falls back to seeding from A1 internally
to bootstrap. This avoids the "C1 starves on cold start" problem.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
    _label,
    _evaluate_relation,
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH


class C1ClaimMutationGenerator(Generator):
    generator_id = "c1"
    claim_kind = ClaimKind.MUTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 2,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Fallback seed source if no parents yet
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":c1seed", seed=seed + 100
        )

    def description(self) -> str:
        return (
            f"c1: claim-mutation (variable-swap, parents={len(self._parents)}, "
            f"fallback=A1 seed)"
        )

    def add_parent(self, record: TheseusRecord) -> None:
        """Hook for daemon to feed verified records back as parent claims.

        Filters to A1-shaped payloads (must have relation, object_a/b,
        value_a/b, invariant_a/b) so next() can mutate without KeyError.
        """
        if record.verdict not in (
            Verdict.SHADOW_CATALOG.value,
            Verdict.REJECTED.value,
        ):
            return
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b",
                  "value_a", "value_b", "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        return self._seed_gen.next()

    def next(self) -> Optional[TheseusRecord]:
        # Internal retry budget for transient mutation failures
        # (parent payload shape mismatch, missing invariant on new object,
        # picked-same-object collisions).
        for _ in range(30):
            if self._parents:
                parent = self._rng.choice(self._parents)
            else:
                parent = self._bootstrap_parent()
                if parent is None:
                    return None

            p = parent.claim_payload
            if (
                "relation" not in p
                or "object_a" not in p
                or "object_b" not in p
            ):
                self.attempts += 1
                continue

            mutate_side = self._rng.choice(("a", "b"))
            if mutate_side == "a":
                new_obj = self._rng.choice(self._knots)
                new_label = _label(new_obj, "knot")
                new_val = _get_int(new_obj, p["invariant_a"])
                if new_val is None or new_label == p["object_a"]:
                    self.attempts += 1
                    continue
                a_val = new_val
                b_val = p["value_b"]
                object_a = new_label
                object_b = p["object_b"]
            else:
                new_obj = self._rng.choice(self._ecs)
                new_label = _label(new_obj, "ec")
                new_val = _get_int(new_obj, p["invariant_b"])
                if new_val is None or new_label == p["object_b"]:
                    self.attempts += 1
                    continue
                a_val = p["value_a"]
                b_val = new_val
                object_a = p["object_a"]
                object_b = new_label

            rel = p["relation"]
            holds = _evaluate_relation(a_val, b_val, rel)
            break
        else:
            return None  # retry budget exhausted

        canonical = (
            f"MUT[{mutate_side}]:{p['invariant_a']}(knot:{object_a}) "
            f"{rel} {p['invariant_b']}(ec:{object_b}) "
            f"| {a_val} vs {b_val} | holds={holds}"
        )
        verdict = (
            Verdict.SHADOW_CATALOG.value if holds else Verdict.REJECTED.value
        )
        kill_pattern = None if holds else f"c1_mut_{rel}_violated"

        payload = dict(p)
        payload["object_a"] = object_a
        payload["object_b"] = object_b
        payload["value_a"] = a_val
        payload["value_b"] = b_val
        payload["mutation_side"] = mutate_side
        payload["parent_record_id"] = parent.record_id
        payload["holds"] = holds

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
        )
        self.attempts += 1
        self.emitted.append(record_id)
        return r
