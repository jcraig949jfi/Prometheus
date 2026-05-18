"""F4 — frontier-pursuit sampler.

Samples from the COVERAGE FRONTIER: regions that are partially explored
but not heavily covered. Distinct from F2 (strict min-coverage) and F3
(soft inverse-coverage): F4 picks from the middle band.

Definition of frontier: regions with coverage in
[min_cov + 1, min_cov + 3]. After cold-start (everyone at 0), F4
behaves like F2 (picking unvisited). Once coverage spreads, F4
concentrates on the "interesting" mid-band — neither trivially-
unexplored nor saturated.

This is the substrate-frontier analog of curriculum learning: don't
sample what's settled, don't sample what's untouched, sample the
boundary where the substrate's understanding is being actively built.
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


FRONTIER_BAND_LO = 1
FRONTIER_BAND_HI = 3


class F4FrontierPursuitGenerator(Generator):
    generator_id = "f4"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 230) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._coverage: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self._all_regions: List[Tuple[str, str, str]] = [
            (ki, ei, rel)
            for ki in KNOT_INTEGER_INVARIANTS
            for ei in EC_INTEGER_INVARIANTS
            for rel in RELATIONS
        ]

    def description(self) -> str:
        return (
            f"f4: frontier-pursuit (mid-coverage band: "
            f"min+{FRONTIER_BAND_LO}..min+{FRONTIER_BAND_HI})"
        )

    def _pick_frontier(self) -> Tuple[str, str, str]:
        """Pick from regions whose coverage is in the frontier band."""
        min_cov = min(self._coverage[r] for r in self._all_regions)
        frontier_lo = min_cov + FRONTIER_BAND_LO
        frontier_hi = min_cov + FRONTIER_BAND_HI
        frontier_regions = [
            r for r in self._all_regions
            if frontier_lo <= self._coverage[r] <= frontier_hi
        ]
        if not frontier_regions:
            # Fall back to min-coverage if frontier is empty
            frontier_regions = [
                r for r in self._all_regions
                if self._coverage[r] == min_cov
            ]
        return self._rng.choice(frontier_regions)

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            ki, ei, rel = self._pick_frontier()
            k = self._rng.choice(self._knots)
            e = self._rng.choice(self._ecs)
            a_val = _get_int(k, ki)
            b_val = _get_int(e, ei)
            if a_val is None or b_val is None:
                self.attempts += 1
                continue

            self._coverage[(ki, ei, rel)] += 1
            holds = _evaluate_relation(a_val, b_val, rel)
            self.attempts += 1

            knot_label = _label(k, "knot")
            ec_label = _label(e, "ec")
            cov = self._coverage[(ki, ei, rel)]
            min_cov_at_pick = min(self._coverage[r] for r in self._all_regions)
            canonical = (
                f"F4_FRONT[cov={cov}, min={min_cov_at_pick}] "
                f"{ki}(knot:{knot_label}) {rel} {ei}(ec:{ec_label}) "
                f"| {a_val} vs {b_val} | holds={holds}"
            )
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"f4_frontier_{rel}_violated"

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
                "region_coverage_at_emit": cov,
                "min_coverage_at_pick": min_cov_at_pick,
                "sampling": "frontier_band_pursuit",
                "frontier_band": (FRONTIER_BAND_LO, FRONTIER_BAND_HI),
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
                extras={"frontier_technique": "active_learning_frontier_band"},
            )
            self.emitted.append(record_id)
            return r

        return None
