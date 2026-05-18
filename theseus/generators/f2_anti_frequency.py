"""F2 — strict anti-frequency stratified sampling.

Complement to F3 (importance-weighted): F2 picks the LEAST-COVERED
region every emission, breaking ties uniformly at random. Strict
round-robin-over-tiers rather than smooth probabilistic bias.

Why both F2 and F3?
- F3 uses soft inverse-coverage weighting (∝ 1/(1+c)^2) — produces
  ~18% bias toward under-explored.
- F2 uses hard min-coverage selection — produces near-uniform coverage
  with explicit tie-breaking.

Together they bracket the active-learning spectrum. F2 is the
extreme-bias anchor; F3 the soft-bias anchor. The bandit will
empirically reveal which gives better yield in this substrate.
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


class F2AntiFrequencyGenerator(Generator):
    generator_id = "f2"
    claim_kind = ClaimKind.INVARIANT_EQUALITY.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 200) -> None:
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
            f"f2: strict anti-frequency sampling "
            f"({len(self._all_regions)} regions; pick min-coverage, "
            f"uniform tie-break)"
        )

    def _pick_least_covered(self) -> Tuple[str, str, str]:
        """Pick region with minimum coverage; ties broken uniformly."""
        min_cov = min(self._coverage[r] for r in self._all_regions)
        candidates = [r for r in self._all_regions if self._coverage[r] == min_cov]
        return self._rng.choice(candidates)

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            ki, ei, rel = self._pick_least_covered()
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
            canonical = (
                f"F2_AFS[cov={cov}] "
                f"{ki}(knot:{knot_label}) {rel} {ei}(ec:{ec_label}) "
                f"| {a_val} vs {b_val} | holds={holds}"
            )
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"f2_anti_freq_{rel}_violated"

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
                "sampling": "strict_anti_frequency",
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
                extras={"frontier_technique": "active_learning_strict_anti_frequency"},
            )
            self.emitted.append(record_id)
            return r

        return None
