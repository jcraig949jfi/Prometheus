"""Z1 — order dependence generator (REAL, Stage 30).

For pairs of operations (f, g) and catalog objects X, computes
f(g(X)) vs g(f(X)) at the invariant-value level. Emits kill
record when the two compositions disagree.

From Sphinx domain D (Temporal / Ordering).
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


# Each pair: extractor returns numeric, then two ops applied in
# either order. If op_a ∘ op_b ≠ op_b ∘ op_a, kill.
OP_PAIRS = [
    {
        "id": "knot_det_abs_then_mod7_vs_mod7_then_abs",
        "domain": "knot",
        "extractor": lambda o: o.get("determinant"),
        "op_a": ("abs", lambda v: abs(v)),
        "op_b": ("mod7", lambda v: v % 7),
    },
    {
        "id": "ec_conductor_div2_floor_then_mod3_vs_mod3_then_div2",
        "domain": "ec",
        "extractor": lambda o: (o.get("base") or {}).get("conductor"),
        "op_a": ("div2_floor", lambda v: v // 2),
        "op_b": ("mod3", lambda v: v % 3),
    },
    {
        "id": "knot_genus_double_then_add1_vs_add1_then_double",
        "domain": "knot",
        "extractor": lambda o: o.get("three_genus"),
        "op_a": ("double", lambda v: v * 2),
        "op_b": ("add1", lambda v: v + 1),
    },
    {
        "id": "ec_rank_square_then_add5_vs_add5_then_square",
        "domain": "ec",
        "extractor": lambda o: (o.get("base") or {}).get("rank"),
        "op_a": ("square", lambda v: v * v),
        "op_b": ("add5", lambda v: v + 5),
    },
]


class Z1OrderDependenceGenerator(Generator):
    generator_id = "z1"
    claim_kind = ClaimKind.ORDER_DEPENDENCE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    MAX_PER_PAIR = 50

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
        for pair in OP_PAIRS:
            catalog = self._knots if pair["domain"] == "knot" else self._ecs
            valid = [o for o in catalog if isinstance(pair["extractor"](o), int)]
            for obj in valid[: self.MAX_PER_PAIR]:
                self._queue.append({"pair": pair, "obj": obj})
        self._cursor = 0

    def description(self) -> str:
        return f"z1: order_dependence (real) — {len(self._queue)} (op-pair, object) checks"

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
            pair, obj = item["pair"], item["obj"]
            try:
                v = pair["extractor"](obj)
                a_then_b = pair["op_b"][1](pair["op_a"][1](v))
                b_then_a = pair["op_a"][1](pair["op_b"][1](v))
            except Exception:
                continue
            label = self._label(pair["domain"], obj)
            commute = (a_then_b == b_then_a)
            if commute:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = f"commute: {pair['op_a'][0]}∘{pair['op_b'][0]}({v}) = {a_then_b}"
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"z1_operators_dont_commute_on_{label}"
                outcome = (
                    f"NO commute: {pair['op_b'][0]}∘{pair['op_a'][0]}({v}) = "
                    f"{a_then_b} ≠ {pair['op_a'][0]}∘{pair['op_b'][0]}({v}) = {b_then_a}"
                )
            canonical = f"Z1_ORDER[{pair['id']}] on {label}: {outcome}"
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)
            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "pair_id": pair["id"],
                    "object": label,
                    "input_value": v,
                    "op_a_label": pair["op_a"][0],
                    "op_b_label": pair["op_b"][0],
                    "a_then_b": a_then_b,
                    "b_then_a": b_then_a,
                    "commute": commute,
                    "logical_form": "operator_commutativity",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
