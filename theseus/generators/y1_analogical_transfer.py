"""Y1 — analogical transfer generator (REAL, Stage 32).

For each cross-domain analogy template, computes the source-side
quantity and the analogous target-side quantity from the live
catalogs. Emits a record stating whether the analogy holds at
the value level.

From Sphinx domain N.
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


# Each analogy: pair source-side population with target-side population
# and check a "should map" relation. Holds if the source-side claim
# is mirrored in target-side.
ANALOGY_TEMPLATES = [
    {
        "id": "small_knot_low_signature_matches_small_ec_low_rank",
        "source_set_label": "knots[crossings ≤ 5]",
        "target_set_label": "EC[conductor ≤ 50]",
        "source_extract": lambda o: abs(o.get("signature", 0)),
        "target_extract": lambda o: ((o.get("base") or {}).get("rank") or 0),
        "source_pred": lambda o: (o.get("crossing_number") or 99) <= 5,
        "target_pred": lambda o: ((o.get("base") or {}).get("conductor") or 1e9) <= 50,
        "claim": "max |signature| over small knots ≈ max rank over small EC",
        "tolerance": 1,
    },
    {
        "id": "knot_genus_grows_with_crossings_ec_rank_grows_with_conductor",
        "source_set_label": "knots[crossings ≤ 8]",
        "target_set_label": "EC[conductor ≤ 1000]",
        "source_extract": lambda o: o.get("three_genus", 0),
        "target_extract": lambda o: ((o.get("base") or {}).get("rank") or 0),
        "source_pred": lambda o: (o.get("crossing_number") or 99) <= 8,
        "target_pred": lambda o: ((o.get("base") or {}).get("conductor") or 1e9) <= 1000,
        "claim": "max genus over small knots ≈ max rank over small EC",
        "tolerance": 1,
    },
    {
        "id": "small_objs_have_small_invariants",
        "source_set_label": "knots[crossings ≤ 4]",
        "target_set_label": "EC[conductor ≤ 30]",
        "source_extract": lambda o: abs(o.get("determinant", 0)),
        "target_extract": lambda o: ((o.get("rich") or {}).get("tamagawa_product") or 0),
        "source_pred": lambda o: (o.get("crossing_number") or 99) <= 4,
        "target_pred": lambda o: ((o.get("base") or {}).get("conductor") or 1e9) <= 30,
        "claim": "max |det| over tiny knots ≈ max tamagawa over tiny EC",
        "tolerance": 5,
    },
]


class Y1AnalogicalTransferGenerator(Generator):
    generator_id = "y1"
    claim_kind = ClaimKind.ANALOGICAL_TRANSFER.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

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
        self._cursor = 0

    def description(self) -> str:
        return f"y1: analogical_transfer (real) — {len(ANALOGY_TEMPLATES)} cross-domain checks"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(ANALOGY_TEMPLATES):
            tpl = ANALOGY_TEMPLATES[self._cursor]
            self._cursor += 1
            self.attempts += 1
            src = [tpl["source_extract"](o) for o in self._knots if tpl["source_pred"](o)]
            tgt = [tpl["target_extract"](o) for o in self._ecs if tpl["target_pred"](o)]
            src = [v for v in src if isinstance(v, int)]
            tgt = [v for v in tgt if isinstance(v, int)]
            if not src or not tgt:
                continue
            src_max = max(src)
            tgt_max = max(tgt)
            gap = abs(src_max - tgt_max)
            holds = gap <= tpl["tolerance"]
            if holds:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = f"analogy HOLDS: |{src_max} - {tgt_max}| = {gap} ≤ {tpl['tolerance']}"
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"y1_analogy_breaks_at_gap_{gap}"
                outcome = f"analogy BREAKS: |{src_max} - {tgt_max}| = {gap} > {tpl['tolerance']}"
            canonical = (
                f"Y1_ANALOGY[{tpl['id']}] {tpl['claim']}: src_max={src_max} tgt_max={tgt_max} — {outcome}"
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
                    "analogy_id": tpl["id"],
                    "source_set_label": tpl["source_set_label"],
                    "target_set_label": tpl["target_set_label"],
                    "claim": tpl["claim"],
                    "source_max": src_max,
                    "target_max": tgt_max,
                    "gap": gap,
                    "tolerance": tpl["tolerance"],
                    "holds": holds,
                    "logical_form": "cross_domain_analogy",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
