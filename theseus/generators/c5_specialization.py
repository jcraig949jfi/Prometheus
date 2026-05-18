"""C5 — specialization-mutation generator.

Opposite of C4 (generalization): picks a SHADOW_CATALOG parent and emits
a strictly-STRONGER variant. The stronger claim MAY or MAY NOT hold for
the same (a, b) — and that information is exactly the substrate boundary.

Logical implications used (each from-relation generates strict
strengthenings):
  equal_mod_2 ⇒  equal (stronger; often fails)
  abs_diff_le_K ⇒  abs_diff_le_{K-1} for K ≥ 1 (stronger; often fails)
  equal ⇒  (no strict strengthening; top of lattice)
  divides ⇒  equal (sometimes stronger)

Most emissions are REJECTED (strengthening fails) and that's the point:
each reject pins down the EXACT threshold of (a, b) under that relation
family. C5's kill records carry boundary information D2 also surfaces
but in a different format.

Pulls from frontier counterfactual augmentation paired with the dual
direction of C4. Together C4 + C5 sandwich the parent claim's truth
boundary.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List, Optional

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    A1CatalogCrossProductGenerator,
    _evaluate_relation,
)


def _generate_strengthenings(rel: str, rng: random.Random) -> List[str]:
    """Return strictly-stronger relations than `rel`. Empty if `rel` is
    top of its lattice."""
    if rel == "equal_mod_2":
        return ["equal"]
    if rel == "divides":
        return ["equal"]
    if rel.startswith("abs_diff_le_"):
        try:
            k = int(rel.split("_")[-1])
        except ValueError:
            return []
        if k <= 0:
            return []
        # Strictly smaller thresholds (stronger)
        cands = [k - 1]
        if k >= 2:
            cands.append(k - 2)
        if k >= 5:
            cands.append(k // 2)
        return [f"abs_diff_le_{j}" for j in cands if j >= 0]
    return []


class C5SpecializationGenerator(Generator):
    generator_id = "c5"
    claim_kind = ClaimKind.MUTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 80,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":c5seed", seed=seed + 800
        )

    def description(self) -> str:
        return "c5: specialization-mutation (strictly stronger relation)"

    def add_parent(self, record: TheseusRecord) -> None:
        if record.verdict != Verdict.SHADOW_CATALOG.value:
            return
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b",
                  "value_a", "value_b", "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            if _generate_strengthenings(p["relation"], self._rng):
                self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict != Verdict.SHADOW_CATALOG.value:
                continue
            p = r.claim_payload
            if _generate_strengthenings(p.get("relation", ""), self._rng):
                return r
        return None

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            if self._parents:
                parent = self._rng.choice(self._parents)
            else:
                parent = self._bootstrap_parent()
                if parent is None:
                    return None

            p = parent.claim_payload
            strengthenings = _generate_strengthenings(p["relation"], self._rng)
            if not strengthenings:
                self.attempts += 1
                continue
            strong_rel = self._rng.choice(strengthenings)
            a_val = p["value_a"]
            b_val = p["value_b"]
            strong_holds = _evaluate_relation(a_val, b_val, strong_rel)

            verdict = (
                Verdict.SHADOW_CATALOG.value if strong_holds
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if strong_holds
                else f"c5_strengthening_{p['relation']}_to_{strong_rel}_fails"
            )

            canonical = (
                f"C5_SPEC[{p['relation']}⇏{strong_rel}] "
                f"{p['invariant_a']}(knot:{p['object_a']}) "
                f"{p['invariant_b']}(ec:{p['object_b']}) "
                f"| {a_val} vs {b_val} | strong_holds={strong_holds}"
            )
            payload = dict(p)
            payload["original_relation"] = p["relation"]
            payload["relation"] = strong_rel
            payload["strong_holds"] = strong_holds
            payload["parent_record_id"] = parent.record_id
            payload["boundary_revealed"] = not strong_holds  # kill = boundary info

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
                extras={"role": "boundary_pinning_specialization"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
