"""F3 — importance-sampling generator (active learning / uncertainty).

Same claim shape as A1 (catalog cross-product) but with biased sampling
weighted toward UNDER-EXPLORED regions. A region is the tuple
(knot_invariant, ec_invariant, relation); F3 maintains coverage counts
per region and samples regions with probability ∝ 1 / (1 + coverage).

Pulls from frontier "active learning / uncertainty sampling" (Settles
2009): when verification is expensive, prioritize the most uncertain
examples. Here, uncertain ≈ under-explored.

The point isn't to replicate A1 — it's to surface regions A1's uniform
sampling would visit too slowly. Yield improvement comes from cheaper
discovery of high-info regions.
"""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
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
    _evaluate_relation,
    KNOT_INTEGER_INVARIANTS,
    EC_INTEGER_INVARIANTS,
    RELATIONS,
)


class F3ImportanceSamplingGenerator(Generator):
    generator_id = "f3"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 30) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Per-region coverage counter. Region = (knot_inv, ec_inv, relation).
        self._coverage: Dict[Tuple[str, str, str], int] = defaultdict(int)
        # All possible regions (small enumeration: ~6 * 4 * 4 = 96).
        self._all_regions: List[Tuple[str, str, str]] = [
            (ki, ei, rel)
            for ki in KNOT_INTEGER_INVARIANTS
            for ei in EC_INTEGER_INVARIANTS
            for rel in RELATIONS
        ]

    def description(self) -> str:
        return (
            f"f3: importance-sampling biased toward under-covered regions "
            f"({len(self._all_regions)} regions; coverage-weighted)"
        )

    def _pick_region(self) -> Tuple[str, str, str]:
        """Sample region with probability ∝ 1 / (1 + coverage[region])^2.

        Squared inverse weighting (alpha=2) is empirically necessary —
        alpha=1 produced near-uniform variance (stdev 3.37 vs uniform
        Poisson 3.23 at n=1000, only ~5% reduction). With alpha=2 the
        bias toward under-explored regions is sharp enough to matter.
        """
        weights = [
            1.0 / ((1.0 + self._coverage[r]) ** 2) for r in self._all_regions
        ]
        total = sum(weights)
        pick = self._rng.random() * total
        cumsum = 0.0
        for region, w in zip(self._all_regions, weights):
            cumsum += w
            if cumsum >= pick:
                return region
        return self._all_regions[-1]

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            ki, ei, rel = self._pick_region()
            k = self._rng.choice(self._knots)
            e = self._rng.choice(self._ecs)
            a_val = _get_int(k, ki)
            b_val = _get_int(e, ei)
            if a_val is None or b_val is None:
                self.attempts += 1
                continue

            holds = _evaluate_relation(a_val, b_val, rel)
            self.attempts += 1
            self._coverage[(ki, ei, rel)] += 1

            knot_label = _label(k, "knot")
            ec_label = _label(e, "ec")
            coverage_at_emit = self._coverage[(ki, ei, rel)]
            canonical = (
                f"F3_ACT[cov={coverage_at_emit}] "
                f"{ki}(knot:{knot_label}) {rel} {ei}(ec:{ec_label}) "
                f"| {a_val} vs {b_val} | holds={holds}"
            )
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"f3_active_{rel}_violated"

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
                "region_coverage_at_emit": coverage_at_emit,
                "sampling": "importance_inverse_coverage",
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
                extras={"frontier_technique": "active_learning_uncertainty_sampling"},
            )
            self.emitted.append(record_id)
            return r

        return None
