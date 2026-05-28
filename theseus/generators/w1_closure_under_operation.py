"""W1 — closure under operation generator (REAL, Stage 29).

For each (set, operation) template: enumerate the set, apply the
operation, check whether the result stays in the set. Emit kill
record when closure breaks.

From Sphinx domains G + H.
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


# Each closure template: (set_predicate, operation_label, operation_fn,
#   would_stay_in_set_fn).
# operation_fn returns a representation of the OPERATION RESULT;
# would_stay_in_set_fn checks whether the result satisfies set_pred.
#
# These are NUMERIC operations on extracted features (since we don't
# have a way to construct new catalog objects). They simulate closure
# behavior at the invariant level.
CLOSURE_TEMPLATES = [
    {
        "id": "ec_rank_le_2_under_add_1",
        "domain": "ec",
        "set_desc": "EC[rank ≤ 2]",
        "set_pred": lambda o: isinstance((o.get("base") or {}).get("rank"), int) and (o.get("base") or {})["rank"] <= 2,
        "operation_label": "add_1_to_rank",
        "operation_fn": lambda o: ((o.get("base") or {}).get("rank") or 0) + 1,
        "stays_in_set_fn": lambda result: result <= 2,
    },
    {
        "id": "knot_crossings_le_8_under_add_1",
        "domain": "knot",
        "set_desc": "knots[crossings ≤ 8]",
        "set_pred": lambda o: isinstance(o.get("crossing_number"), int) and o["crossing_number"] <= 8,
        "operation_label": "add_1_to_crossings",
        "operation_fn": lambda o: (o.get("crossing_number") or 0) + 1,
        "stays_in_set_fn": lambda result: result <= 8,
    },
    {
        "id": "ec_conductor_le_500_under_double",
        "domain": "ec",
        "set_desc": "EC[conductor ≤ 500]",
        "set_pred": lambda o: isinstance((o.get("base") or {}).get("conductor"), int) and (o.get("base") or {})["conductor"] <= 500,
        "operation_label": "double_conductor",
        "operation_fn": lambda o: ((o.get("base") or {}).get("conductor") or 0) * 2,
        "stays_in_set_fn": lambda result: result <= 500,
    },
    {
        "id": "ec_torsion_le_4_under_double",
        "domain": "ec",
        "set_desc": "EC[torsion ≤ 4]",
        "set_pred": lambda o: isinstance((o.get("rich") or {}).get("torsion"), int) and (o.get("rich") or {})["torsion"] <= 4,
        "operation_label": "double_torsion",
        "operation_fn": lambda o: ((o.get("rich") or {}).get("torsion") or 0) * 2,
        "stays_in_set_fn": lambda result: result <= 4,
    },
]


class W1ClosureUnderOperationGenerator(Generator):
    generator_id = "w1"
    claim_kind = ClaimKind.CLOSURE_UNDER_OPERATION.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    MAX_PER_TEMPLATE = 80

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
        # Build queue: per template, sample objects in the set
        self._queue: List[Dict[str, Any]] = []
        for tpl in CLOSURE_TEMPLATES:
            catalog = self._knots if tpl["domain"] == "knot" else self._ecs
            in_set = [o for o in catalog if tpl["set_pred"](o)]
            for obj in in_set[: self.MAX_PER_TEMPLATE]:
                self._queue.append({"template": tpl, "obj": obj})
        self._cursor = 0

    def description(self) -> str:
        return f"w1: closure_under_operation (real) — {len(self._queue)} (template, object) pairs"

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
            tpl, obj = item["template"], item["obj"]
            try:
                result = tpl["operation_fn"](obj)
                stays = tpl["stays_in_set_fn"](result)
            except Exception:
                continue
            label = self._label(tpl["domain"], obj)
            if stays:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = f"closure HOLDS: {label} →({tpl['operation_label']}) {result} stays in set"
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"w1_closure_violated_by_{label}"
                outcome = f"closure VIOLATED: {label} →({tpl['operation_label']}) {result} leaves set"
            canonical = f"W1_CLOSURE[{tpl['id']}] {outcome}"
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)
            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "template_id": tpl["id"],
                    "set_description": tpl["set_desc"],
                    "operation": tpl["operation_label"],
                    "object": label,
                    "operation_result": result,
                    "stays_in_set": stays,
                    "logical_form": "closure_under_operation",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
