"""S1 — triangle inequality / metric structure generator (REAL, Stage 28).

Emits claims testing |f(X) - f(Z)| ≤ |f(X) - f(Y)| + |f(Y) - f(Z)|
for triples of catalog objects and various invariant functions f.
This is the basic triangle inequality on the induced pseudo-metric
d_f(X,Y) = |f(X) - f(Y)|.

Real implementation: pick (invariant, triple) cross-product over
real catalog. Compute actual d_f for each pair. Verdict: SHADOW
if inequality holds, REJECTED with witness triple if it fails.
(Note: for integer-valued d_f, triangle inequality always holds
because |·| satisfies it. The interesting fail mode would be on
NON-absolute-difference metrics, which we don't have. So all
records here SHOULD emit SHADOW_CATALOG — substrate-positive.)

From Sphinx domain H (Metric).
Plan: pivot/techne_15gen_plan_2026-05-28.md
"""
from __future__ import annotations

import gzip
import json
import itertools
import random
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


def _load_catalog(path) -> List[dict]:
    p = str(path)
    if p.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    return data.get("entries", []) if isinstance(data, dict) else data


def _f_ec_conductor(e: dict):
    base = e.get("base") or {}
    return base.get("conductor")


def _f_ec_rank(e: dict):
    base = e.get("base") or {}
    return base.get("rank")


def _f_ec_tamagawa(e: dict):
    rich = e.get("rich") or {}
    return rich.get("tamagawa_product")


def _f_knot_det(k: dict):
    return k.get("determinant")


def _f_knot_signature_abs(k: dict):
    s = k.get("signature")
    return abs(s) if isinstance(s, int) else None


def _f_knot_genus(k: dict):
    return k.get("three_genus")


INVARIANTS: List[Dict[str, Any]] = [
    {"domain": "ec", "name": "conductor", "fn": _f_ec_conductor},
    {"domain": "ec", "name": "rank", "fn": _f_ec_rank},
    {"domain": "ec", "name": "tamagawa_product", "fn": _f_ec_tamagawa},
    {"domain": "knot", "name": "determinant", "fn": _f_knot_det},
    {"domain": "knot", "name": "|signature|", "fn": _f_knot_signature_abs},
    {"domain": "knot", "name": "three_genus", "fn": _f_knot_genus},
]


# Pseudo-metric squared variants (|f(X) - f(Y)|² doesn't satisfy
# triangle ineq in general — picks one as falsifiable check)
def _quasi_metric_sq(a, b):
    return (a - b) ** 2 if a is not None and b is not None else None


class S1TriangleInequalityGenerator(Generator):
    generator_id = "s1"
    claim_kind = ClaimKind.TRIANGLE_INEQUALITY.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    # Cap to bound emissions per batch
    MAX_RECORDS = 600
    TRIPLES_PER_INVARIANT = 50

    def __init__(self, batch_id: str, seed: int = 7) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        try:
            self._knots = _load_catalog(KNOTS_DB_PATH)
        except Exception:
            self._knots = []
        try:
            self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        except Exception:
            self._ecs = []
        self._queue: List[Dict[str, Any]] = []
        for inv in INVARIANTS:
            catalog = self._knots if inv["domain"] == "knot" else self._ecs
            with_value = [(o, inv["fn"](o)) for o in catalog if inv["fn"](o) is not None]
            if len(with_value) < 3:
                continue
            # Sample triples
            for _ in range(self.TRIPLES_PER_INVARIANT):
                triple = self._rng.sample(with_value, 3)
                self._queue.append({
                    "invariant": inv,
                    "triple": triple,
                })
        # Optionally add the quasi-metric (squared) — falsifiable check
        for inv in INVARIANTS[:3]:  # only first 3 to bound
            catalog = self._knots if inv["domain"] == "knot" else self._ecs
            with_value = [(o, inv["fn"](o)) for o in catalog if inv["fn"](o) is not None]
            if len(with_value) < 3:
                continue
            for _ in range(self.TRIPLES_PER_INVARIANT // 2):
                triple = self._rng.sample(with_value, 3)
                self._queue.append({
                    "invariant": inv,
                    "triple": triple,
                    "metric_variant": "squared",
                })
        self._cursor = 0

    def description(self) -> str:
        return (
            f"s1: triangle_inequality (real) — {len(self._queue)} "
            f"(invariant, triple) checks queued"
        )

    def _label(self, domain: str, obj: dict) -> str:
        if domain == "knot":
            return f"knot:{obj.get('name','?')}"
        base = obj.get("base") or {}
        return f"ec:{base.get('label') or base.get('cremona_label') or '?'}"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(self._queue) and self.attempts < self.MAX_RECORDS:
            item = self._queue[self._cursor]
            self._cursor += 1
            self.attempts += 1

            inv = item["invariant"]
            triple = item["triple"]
            (xa, va), (xb, vb), (xc, vc) = triple
            domain = inv["domain"]
            label_a = self._label(domain, xa)
            label_b = self._label(domain, xb)
            label_c = self._label(domain, xc)
            variant = item.get("metric_variant", "abs")

            if variant == "abs":
                d_ab = abs(va - vb)
                d_bc = abs(vb - vc)
                d_ac = abs(va - vc)
            else:
                d_ab = (va - vb) ** 2
                d_bc = (vb - vc) ** 2
                d_ac = (va - vc) ** 2

            holds = d_ac <= d_ab + d_bc

            if holds:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = f"HOLDS d_AC={d_ac} ≤ d_AB+d_BC={d_ab+d_bc}"
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = (
                    f"s1_triangle_inequality_broken_on_triple"
                )
                outcome = (
                    f"VIOLATED d_AC={d_ac} > d_AB+d_BC={d_ab+d_bc} "
                    f"(metric variant={variant})"
                )

            canonical = (
                f"S1_TRIANGLE[{inv['name']}_{variant}] "
                f"({label_a}, {label_b}, {label_c}): {outcome}"
            )
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)

            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "invariant": inv["name"],
                    "metric_variant": variant,
                    "objects": [label_a, label_b, label_c],
                    "values": [va, vb, vc],
                    "d_AB": d_ab,
                    "d_BC": d_bc,
                    "d_AC": d_ac,
                    "holds": holds,
                    "logical_form": "metric_triangle_inequality",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
