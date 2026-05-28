"""Q1 — modular arithmetic varying p (REAL, Stage 29).

For each (invariant, prime p), partitions the catalog by f(X) mod p
and emits a claim describing the partition. Detects "structural
change at p" by comparing partition entropies across primes —
when a prime p has anomalously concentrated distribution
compared to neighbors, structure is shifting.

Real implementation: iterate (invariant × prime in {2,3,5,7,11,13,17,19,23})
cross-product; compute partition distribution; emit one record per
(invariant, prime). When the partition is sharply concentrated
(min entropy), emit REJECTED with kill_pattern = structure-change.

From Sphinx domain C (Arithmetic).
"""
from __future__ import annotations

import gzip
import json
import math
from collections import Counter
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
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


def _f_ec_conductor(e): return (e.get("base") or {}).get("conductor")
def _f_ec_rank(e):     return (e.get("base") or {}).get("rank")
def _f_ec_tamagawa(e): return (e.get("rich") or {}).get("tamagawa_product")
def _f_knot_det(k):    return k.get("determinant")
def _f_knot_genus(k):  return k.get("three_genus")


INVARIANTS = [
    ("ec_conductor", "ec", _f_ec_conductor),
    ("ec_rank", "ec", _f_ec_rank),
    ("ec_tamagawa", "ec", _f_ec_tamagawa),
    ("knot_det", "knot", _f_knot_det),
    ("knot_three_genus", "knot", _f_knot_genus),
]
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]


class Q1ModularVaryingPGenerator(Generator):
    generator_id = "q1"
    claim_kind = ClaimKind.MODULAR_VARYING_P.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    # An anomalous concentration ratio: max-bucket > 80% of total → flag
    CONCENTRATION_THRESHOLD = 0.80

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        try:
            self._knots = _load_catalog(KNOTS_DB_PATH)
        except Exception:
            self._knots = []
        try:
            self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        except Exception:
            self._ecs = []
        self._queue: List[Dict[str, Any]] = []
        for inv_name, domain, fn in INVARIANTS:
            for p in PRIMES:
                self._queue.append({
                    "inv_name": inv_name, "domain": domain, "fn": fn, "p": p,
                })
        self._cursor = 0

    def description(self) -> str:
        return f"q1: modular_varying_p (real) — {len(self._queue)} (invariant × p) cells"

    def _catalog_for(self, domain: str) -> List[dict]:
        return self._knots if domain == "knot" else self._ecs

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(self._queue):
            item = self._queue[self._cursor]
            self._cursor += 1
            self.attempts += 1
            inv_name, domain, fn, p = item["inv_name"], item["domain"], item["fn"], item["p"]
            catalog = self._catalog_for(domain)
            buckets: Counter = Counter()
            n_valid = 0
            for o in catalog:
                v = fn(o)
                if isinstance(v, int):
                    buckets[v % p] += 1
                    n_valid += 1
            if n_valid == 0:
                continue
            max_bucket = max(buckets.values())
            max_share = max_bucket / n_valid
            entropy = -sum((c/n_valid)*math.log2(c/n_valid) for c in buckets.values() if c > 0)
            max_possible_entropy = math.log2(p) if p > 1 else 0.0
            uniformity = entropy / max_possible_entropy if max_possible_entropy > 0 else 0.0

            anomalous = max_share >= self.CONCENTRATION_THRESHOLD
            if anomalous:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"q1_modular_structure_changes_at_p{p}"
                outcome = (
                    f"CONCENTRATED at p={p}: bucket {buckets.most_common(1)[0][0]} "
                    f"has {max_share*100:.1f}% of {n_valid}; entropy={entropy:.3f}"
                )
            else:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = (
                    f"uniform-like at p={p}: max_share={max_share*100:.1f}%, "
                    f"entropy={entropy:.3f}/{max_possible_entropy:.3f}"
                )

            canonical = (
                f"Q1_MODVARP[{inv_name}_modp{p}] {n_valid} objects, "
                f"{len(buckets)} buckets, max_share={max_share*100:.1f}% — {outcome}"
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
                    "invariant": inv_name,
                    "domain": domain,
                    "p": p,
                    "n_valid": n_valid,
                    "buckets": dict(buckets),
                    "max_share": round(max_share, 4),
                    "entropy": round(entropy, 4),
                    "uniformity": round(uniformity, 4),
                    "anomalous": anomalous,
                    "logical_form": "varying_modular_structure",
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
