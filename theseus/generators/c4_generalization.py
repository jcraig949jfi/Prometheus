"""C4 — generalization-mutation generator.

For verified parents, emits a logically-WEAKER variant of the claim. The
weaker claim MUST hold whenever the parent does (basic propositional
implication). Any emission where the weaker form fails is a substrate
self-consistency bug — extremely high info-density signal.

Logical implications used (each from-relation generates safe weakenings):
  equal(a, b)         ⇒  equal_mod_2(a, b)
  equal(a, b)         ⇒  abs_diff_le_K(a, b) for any K ≥ 0
  abs_diff_le_K(a, b) ⇒  abs_diff_le_J(a, b) for any J ≥ K
  divides(a, b)       ⇒  (no clean weakening picked at v0.1)
  equal_mod_2(a, b)   ⇒  (no clean weakening; bottom of lattice)

C4 is structurally a SUBSTRATE SELF-TEST: it should produce ~100%
SHADOW_CATALOG emissions on healthy substrate. Any REJECTED emission
indicates a relation-evaluator bug. Bandit-yield-wise this is low-info
on the happy path and high-info when it kills.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List, Optional, Tuple

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


def _generate_weakenings(rel: str, rng: random.Random) -> List[str]:
    """Return logically-weaker relations than `rel`. Returns [] if no
    safe weakening is defined for this relation."""
    if rel == "equal":
        return ["equal_mod_2"] + [f"abs_diff_le_{k}" for k in (1, 2, 3, 5, 8)]
    if rel.startswith("abs_diff_le_"):
        try:
            k = int(rel.split("_")[-1])
        except ValueError:
            return []
        # Generate strictly larger thresholds (always weaker)
        return [f"abs_diff_le_{j}" for j in (k + 1, k + 2, k + 5, k + 13)]
    # divides and equal_mod_2 are skipped at v0.1
    return []


class C4GeneralizationGenerator(Generator):
    generator_id = "c4"
    claim_kind = ClaimKind.MUTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 13,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":c4seed", seed=seed + 500
        )

    def description(self) -> str:
        return (
            f"c4: generalization-mutation (logically-weaker relation; "
            f"substrate self-consistency probe)"
        )

    def add_parent(self, record: TheseusRecord) -> None:
        if record.verdict != Verdict.SHADOW_CATALOG.value:
            return  # Generalization is only meaningful on SURVIVING claims
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b",
                  "value_a", "value_b", "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            # Must have at least one weakening defined
            if _generate_weakenings(p["relation"], self._rng):
                self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        # Seed until we get a SURVIVING claim with a weakenable relation
        for _ in range(30):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict != Verdict.SHADOW_CATALOG.value:
                continue
            p = r.claim_payload
            if _generate_weakenings(p.get("relation", ""), self._rng):
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
            weakenings = _generate_weakenings(p["relation"], self._rng)
            if not weakenings:
                self.attempts += 1
                continue
            weak_rel = self._rng.choice(weakenings)
            a_val = p["value_a"]
            b_val = p["value_b"]
            # The parent's relation held (SHADOW_CATALOG); the weakening
            # MUST also hold by logical implication.
            weak_holds = _evaluate_relation(a_val, b_val, weak_rel)
            self_consistent = weak_holds  # expected True

            verdict = (
                Verdict.SHADOW_CATALOG.value if self_consistent
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if self_consistent
                else f"c4_self_consistency_violated_{p['relation']}_implies_{weak_rel}"
            )

            canonical = (
                f"C4_GEN[{p['relation']}⇒{weak_rel}] "
                f"{p['invariant_a']}(knot:{p['object_a']}) "
                f"{p['invariant_b']}(ec:{p['object_b']}) "
                f"| {a_val} vs {b_val} | weak_holds={weak_holds} "
                f"| self_consistent={self_consistent}"
            )
            payload = dict(p)
            payload["original_relation"] = p["relation"]
            payload["relation"] = weak_rel
            payload["weak_holds"] = weak_holds
            payload["self_consistent"] = self_consistent
            payload["parent_record_id"] = parent.record_id

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
                extras={"role": "substrate_self_consistency_probe"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
