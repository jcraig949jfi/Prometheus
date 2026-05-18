"""C2 — threshold-mutation generator (counterfactual upgrade, Fire #3).

Targets parent claims using the `abs_diff_le_K` relation and mutates K
to boundary-adjacent values rather than random ladder picks. Each
mutation pins down the exact threshold flip-point for the parent's
(value_a, value_b) pair.

Pulls from frontier "counterfactual augmentation" (Pearl, Kaushik et al.
2020): instead of random perturbation, intervene on the threshold to
land AT the relation boundary. Boundary records are exactly the
high-info-density population D2 already prioritizes.

Strategy:
  Pick from {actual_diff, actual_diff - 1, actual_diff + 1, midpoint,
            random_ladder_fallback}.
  This gives 80%+ boundary-flavored mutations vs the previous random
  Fibonacci ladder.
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
    _load_catalog,
    _get_int,
    _label,
    _evaluate_relation,
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH


# Random-ladder fallback (used when counterfactual candidates collide)
THRESHOLD_LADDER = (0, 1, 2, 3, 5, 8, 13, 21)


def _counterfactual_thresholds(orig_k: int, actual_diff: int) -> list[int]:
    """Boundary-adjacent threshold candidates for counterfactual mutation.

    Returns thresholds that PROBE THE BOUNDARY of the parent's
    (value_a, value_b) pair:
      - actual_diff (exact boundary: claim becomes just-barely-true)
      - actual_diff - 1 (one-step inside: claim flips to false)
      - actual_diff + 1 (one-step outside: claim stays comfortably true)
      - midpoint between orig_k and actual_diff (half-step)
    Filters non-negative and != orig_k.
    """
    candidates = {
        actual_diff,
        actual_diff - 1,
        actual_diff + 1,
        (orig_k + actual_diff) // 2,
    }
    return [k for k in candidates if k >= 0 and k != orig_k]


class C2ThresholdMutationGenerator(Generator):
    generator_id = "c2"
    claim_kind = ClaimKind.MUTATION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 11,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":c2seed", seed=seed + 300
        )

    def description(self) -> str:
        return (
            f"c2: threshold-mutation on abs_diff_le_K claims "
            f"(ladder={THRESHOLD_LADDER})"
        )

    def add_parent(self, record: TheseusRecord) -> None:
        # Only accept abs_diff_le_K parents with full A1-shape payload
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b",
                  "value_a", "value_b", "invariant_a", "invariant_b")
        if (
            p.get("relation", "").startswith("abs_diff_le_")
            and all(k in p for k in needed)
        ):
            self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        # Spin A1 until we get an abs_diff parent
        for _ in range(20):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.claim_payload.get("relation", "").startswith("abs_diff_le_"):
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
            if not p.get("relation", "").startswith("abs_diff_le_"):
                self.attempts += 1
                continue

            # Parse original threshold from relation name (e.g. "abs_diff_le_3" → 3)
            try:
                orig_k = int(p["relation"].split("_")[-1])
            except (ValueError, KeyError):
                self.attempts += 1
                continue

            a_val = p["value_a"]
            b_val = p["value_b"]
            actual_diff = abs(a_val - b_val)

            # Counterfactual: pick from boundary-adjacent candidates first;
            # fall back to ladder if all boundary candidates collide with
            # orig_k (e.g., already AT the boundary).
            cf_candidates = _counterfactual_thresholds(orig_k, actual_diff)
            if cf_candidates:
                new_k = self._rng.choice(cf_candidates)
                mutation_kind = "counterfactual_boundary"
            else:
                ladder = [k for k in THRESHOLD_LADDER if k != orig_k]
                if not ladder:
                    self.attempts += 1
                    continue
                new_k = self._rng.choice(ladder)
                mutation_kind = "ladder_fallback"
            new_rel = f"abs_diff_le_{new_k}"

            new_holds = _evaluate_relation(a_val, b_val, new_rel)
            old_holds = _evaluate_relation(a_val, b_val, p["relation"])

            # If mutation flips truth, this is a margin-revealing mutation.
            # Information value: discover the exact threshold.
            flipped = old_holds != new_holds

            verdict = (
                Verdict.SHADOW_CATALOG.value
                if new_holds
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None
                if new_holds
                else f"c2_threshold_K{new_k}_violated_actual_diff_{actual_diff}"
            )

            canonical = (
                f"C2_THRESH[K:{orig_k}→{new_k},{mutation_kind}] "
                f"{p['invariant_a']}(knot:{p['object_a']}) {new_rel} "
                f"{p['invariant_b']}(ec:{p['object_b']}) "
                f"| actual_diff={actual_diff} | holds={new_holds} "
                f"| flipped={flipped}"
            )
            payload = dict(p)
            payload["original_threshold"] = orig_k
            payload["new_threshold"] = new_k
            payload["relation"] = new_rel
            payload["actual_diff"] = actual_diff
            payload["old_holds"] = old_holds
            payload["new_holds"] = new_holds
            payload["truth_flipped"] = flipped
            payload["mutation_kind"] = mutation_kind
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
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
