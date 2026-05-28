"""P1 — modus ponens chain generator (REAL, Stage 30).

Walks a chain of P → Q → R implications grounded in catalog
computations. Each link must hold on the same catalog object;
when any link fails, emit kill record naming the broken hop.

From Sphinx domain A (Formal Logic).
"""
from __future__ import annotations

import gzip
import json
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


# Each chain: list of (predicate_label, predicate_fn) links.
# The chain "holds" if ALL predicates evaluate to True on the same object.
# If link i fails, kill_pattern records link i.
CHAIN_TEMPLATES = [
    {
        "id": "ec_high_rank_implies_complex_l_function",
        "domain": "ec",
        "links": [
            ("rank ≥ 2", lambda o: ((o.get("base") or {}).get("rank") or 0) >= 2),
            ("conductor ≥ 100", lambda o: ((o.get("base") or {}).get("conductor") or 0) >= 100),
            ("L1 < 1.0", lambda o: ((o.get("rich") or {}).get("L1") or 1e9) < 1.0),
        ],
    },
    {
        "id": "knot_low_crossings_implies_simple_invariants",
        "domain": "knot",
        "links": [
            ("crossing_number ≤ 5", lambda o: (o.get("crossing_number") or 99) <= 5),
            ("|signature| ≤ 4", lambda o: abs(o.get("signature") or 99) <= 4),
            ("three_genus ≤ 2", lambda o: (o.get("three_genus") or 99) <= 2),
        ],
    },
    {
        "id": "ec_torsion_large_implies_small_conductor",
        "domain": "ec",
        "links": [
            ("torsion ≥ 8", lambda o: ((o.get("rich") or {}).get("torsion") or 0) >= 8),
            ("conductor ≤ 200", lambda o: ((o.get("base") or {}).get("conductor") or 1e9) <= 200),
        ],
    },
    {
        "id": "knot_amphichiral_implies_signature_zero",
        "domain": "knot",
        "links": [
            ("crossing_number ≤ 10", lambda o: (o.get("crossing_number") or 99) <= 10),
            ("|determinant| ∈ {1,3,5,7,9,11,13,15}", lambda o: abs(o.get("determinant") or 0) in {1,3,5,7,9,11,13,15}),
            ("signature = 0", lambda o: o.get("signature") == 0),
        ],
    },
]


class P1ModusPonensChainGenerator(Generator):
    generator_id = "p1"
    claim_kind = ClaimKind.MODUS_PONENS_CHAIN.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    MAX_PER_CHAIN = 80

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
        for tpl in CHAIN_TEMPLATES:
            catalog = self._knots if tpl["domain"] == "knot" else self._ecs
            # filter to objects satisfying link 0 (premise)
            valid = []
            for o in catalog:
                try:
                    if tpl["links"][0][1](o):
                        valid.append(o)
                except Exception:
                    continue
            for obj in valid[: self.MAX_PER_CHAIN]:
                self._queue.append({"chain": tpl, "obj": obj})
        self._cursor = 0

    def description(self) -> str:
        return f"p1: modus_ponens_chain (real) — {len(self._queue)} (chain, premise-obj) pairs"

    def _label(self, domain, obj):
        if domain == "knot":
            return f"knot:{obj.get('name','?')}"
        base = obj.get("base") or {}
        return f"ec:{base.get('label') or base.get('cremona_label') or '?'}"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(self._queue):
            item = self._queue[self._cursor]
            self._cursor += 1
            self.attempts += 1
            tpl, obj = item["chain"], item["obj"]
            link_results: List[Dict[str, Any]] = []
            broken_at = None
            for idx, (label, fn) in enumerate(tpl["links"]):
                try:
                    val = bool(fn(obj))
                except Exception:
                    val = None
                link_results.append({"index": idx, "label": label, "holds": val})
                if val is not True and broken_at is None:
                    broken_at = idx
                    break
            obj_label = self._label(tpl["domain"], obj)
            if broken_at is None:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = f"all {len(tpl['links'])} links hold on {obj_label}"
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"p1_multi_hop_break_at_step_{broken_at}"
                outcome = (
                    f"chain breaks at link {broken_at} "
                    f"('{tpl['links'][broken_at][0]}') on {obj_label}"
                )
            canonical = f"P1_MP_CHAIN[{tpl['id']}] {outcome}"
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)
            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "chain_id": tpl["id"],
                    "object": obj_label,
                    "links": link_results,
                    "broken_at_link": broken_at,
                    "logical_form": "modus_ponens_chain",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
