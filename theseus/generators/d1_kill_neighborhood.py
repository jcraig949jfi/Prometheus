"""D1 — kill-neighborhood generator.

Uses kill_vector_navigator's recommendations to emit claims about
"neighboring objects in this region should also kill on this F-gate."
v0.1: when the navigator is reachable, queries its existing recommendations;
when not, falls back to in-memory parent-driven neighborhood synthesis.

Neighborhood = "for the parent kill (object_p, F-gate F), find nearby
objects (by integer-invariant proximity) and emit a claim that F should
also kill them." Validation: cheap distance check + retesting the
relation in the parent claim.
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
)
from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH


def _knot_distance(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """Integer-invariant distance between two knots."""
    keys = ("crossing_number", "signature", "determinant", "three_genus")
    s = 0.0
    n = 0
    for k in keys:
        va = _get_int(a, k)
        vb = _get_int(b, k)
        if va is None or vb is None:
            continue
        s += (va - vb) ** 2
        n += 1
    return (s / max(n, 1)) ** 0.5


class D1KillNeighborhoodGenerator(Generator):
    generator_id = "d1"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 3,
        parent_kills: Optional[List[TheseusRecord]] = None,
        neighborhood_radius: float = 2.0,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parent_kills: List[TheseusRecord] = (
            list(parent_kills) if parent_kills else []
        )
        self._radius = neighborhood_radius
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        # Bootstrap fallback — generate one A1 kill if no parents yet
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":d1seed", seed=seed + 200
        )

    def description(self) -> str:
        return (
            f"d1: kill-neighborhood (parent_kills={len(self._parent_kills)}, "
            f"radius={self._radius})"
        )

    def add_kill(self, record: TheseusRecord) -> None:
        """Hook for daemon to feed kill records back as parent kills.

        Filters to A1-shaped payloads (must have relation, object_a,
        value_b, invariant_a/b) so next() can navigate without KeyError.
        """
        if record.verdict != Verdict.REJECTED.value:
            return
        p = record.claim_payload
        needed = ("relation", "object_a", "value_b",
                  "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            self._parent_kills.append(record)

    def _find_kill_parent(self) -> Optional[TheseusRecord]:
        if self._parent_kills:
            return self._rng.choice(self._parent_kills)
        # Bootstrap: spin A1 until we get a kill, max 10 tries
        for _ in range(10):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict == Verdict.REJECTED.value:
                return r
        return None

    def next(self) -> Optional[TheseusRecord]:
        # Internal retry budget for transient failures:
        # parent shape mismatch, missing parent_knot, empty neighborhood,
        # missing invariant on neighbor.
        for _ in range(30):
            parent = self._find_kill_parent()
            if parent is None:
                return None

            p = parent.claim_payload
            if "object_a" not in p or "invariant_a" not in p:
                self.attempts += 1
                continue

            parent_knot = next(
                (k for k in self._knots if k.get("name") == p["object_a"]),
                None,
            )
            if parent_knot is None:
                self.attempts += 1
                continue

            candidates = [
                k
                for k in self._knots
                if k.get("name") != parent_knot.get("name")
                and _knot_distance(parent_knot, k) <= self._radius
            ]
            if not candidates:
                self.attempts += 1
                continue
            neighbor = self._rng.choice(candidates)

            ki = p["invariant_a"]
            ei = p["invariant_b"]
            rel = p["relation"]
            b_val = p["value_b"]
            a_val = _get_int(neighbor, ki)
            if a_val is None:
                self.attempts += 1
                continue

            holds = _evaluate_relation(a_val, b_val, rel)
            break
        else:
            return None  # retry budget exhausted
        # The CLAIM is "neighbor also kills" — so prediction is NOT holds
        prediction_correct = not holds
        verdict = (
            Verdict.SHADOW_CATALOG.value
            if prediction_correct
            else Verdict.REJECTED.value
        )
        kill_pattern = None if prediction_correct else "d1_neighborhood_prediction_wrong"

        neighbor_label = _label(neighbor, "knot")
        canonical = (
            f"KILL_NBHD[parent={p['object_a']}->{neighbor_label}, "
            f"r={self._radius}]: predict {rel} also kills, "
            f"actual_holds={holds}, prediction_correct={prediction_correct}"
        )
        payload = {
            "parent_kill_record_id": parent.record_id,
            "parent_object": p["object_a"],
            "neighbor_object": neighbor_label,
            "neighbor_distance": _knot_distance(parent_knot, neighbor),
            "relation": rel,
            "invariant_a": ki,
            "invariant_b": ei,
            "value_a": a_val,
            "value_b": b_val,
            "predicted_also_kills": True,
            "actually_killed": not holds,
            "prediction_correct": prediction_correct,
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
