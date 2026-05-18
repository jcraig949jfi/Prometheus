"""D2 — margin-bracket generator.

Targets claims with actual_diff close to the relation threshold —
"barely kills" and "barely survives" — and emits explicit boundary-
crossing records.

The margin signal is what `kill_vector_navigator` exploited to gain
126,983x distinguishability in margin-mode vs categorical mode (per
KILL_VECTOR_SPEC). D2 bottles that intuition: claims at the threshold
boundary are the highest-info-density region of claim-space.

v0.1 emits abs_diff-based bracket claims. Tier 1 will generalize to
continuous-margin substrate primitives.
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
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH


# Bracket distance: a "bracket claim" is one where actual_diff is within
# `bracket_width` of the relation threshold.
DEFAULT_BRACKET_WIDTH = 2


class D2MarginBracketGenerator(Generator):
    generator_id = "d2"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 12,
        bracket_width: int = DEFAULT_BRACKET_WIDTH,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._bracket = bracket_width
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":d2seed", seed=seed + 400
        )

    def description(self) -> str:
        return (
            f"d2: margin-bracket (claims with actual_diff within "
            f"{self._bracket} of relation threshold)"
        )

    def add_parent(self, record: TheseusRecord) -> None:
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b", "value_a",
                  "value_b", "invariant_a", "invariant_b")
        if (
            p.get("relation", "").startswith("abs_diff_le_")
            and all(k in p for k in needed)
        ):
            self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
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
            rel = p.get("relation", "")
            if not rel.startswith("abs_diff_le_"):
                self.attempts += 1
                continue
            try:
                k = int(rel.split("_")[-1])
            except ValueError:
                self.attempts += 1
                continue

            a_val = p["value_a"]
            b_val = p["value_b"]
            actual_diff = abs(a_val - b_val)
            margin = k - actual_diff  # positive = survives, negative = fails

            in_bracket = abs(margin) <= self._bracket

            # Bracket claim: "this object pair has |margin| <= bracket_width"
            # Verdict: SHADOW_CATALOG if the claim itself holds (margin tight);
            # REJECTED if the parent is comfortably far from threshold.
            verdict = (
                Verdict.SHADOW_CATALOG.value if in_bracket
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None
                if in_bracket
                else f"d2_margin_outside_bracket_{abs(margin)}>{self._bracket}"
            )

            band = "barely_survives" if margin > 0 and in_bracket else (
                "barely_fails" if margin <= 0 and in_bracket else
                "comfortable_survival" if margin > 0 else "comfortable_failure"
            )

            canonical = (
                f"D2_BRACKET[K={k}, w={self._bracket}] "
                f"{p['invariant_a']}(knot:{p['object_a']}) vs "
                f"{p['invariant_b']}(ec:{p['object_b']}) "
                f"| margin={margin:+d} | band={band} | in_bracket={in_bracket}"
            )
            payload = {
                "parent_record_id": parent.record_id,
                "threshold_k": k,
                "bracket_width": self._bracket,
                "actual_diff": actual_diff,
                "margin": margin,
                "in_bracket": in_bracket,
                "band": band,
                "object_a": p["object_a"],
                "object_b": p["object_b"],
                "invariant_a": p["invariant_a"],
                "invariant_b": p["invariant_b"],
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
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
