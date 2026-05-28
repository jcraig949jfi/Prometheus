"""U1 — quantifier swap generator (REAL, Stage 31).

For each ∀∃ vs ∃∀ template, EVALUATES BOTH forms against the
real catalog. The pair of evaluations gives a paired result.
When ∀∃ holds but ∃∀ doesn't (or vice versa), substrate emits
a record demonstrating the order-sensitivity with witnesses.

From Sphinx domain A.
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


# Each template: a set X, a set Y, a relation R(x, y).
# ∀x∈X ∃y∈Y R(x,y) :: "for each x there's some y..."
# ∃y∈Y ∀x∈X R(x,y) :: "there's a y that works for all x..."
# The two are equivalent only if some y is universal.
SWAP_TEMPLATES = [
    {
        "id": "ec_x_has_good_red_at_some_prime",
        "set_x_desc": "EC of conductor ≤ 50",
        "set_y_desc": "primes p ∈ [2, 100]",
        "set_x_extract": "ecs_small",
        "set_y_extract": "primes_small",
        "relation_desc": "p ∤ conductor(E) (good reduction)",
        "relation_fn": lambda e, p: ((e.get("base") or {}).get("conductor") or 0) % p != 0,
    },
    {
        "id": "knot_x_has_invariant_value_in_set",
        "set_x_desc": "knots of crossings ≤ 7",
        "set_y_desc": "small integers Y = {-2,-1,0,1,2}",
        "set_x_extract": "knots_small",
        "set_y_extract": "small_ints",
        "relation_desc": "signature(K) = y",
        "relation_fn": lambda k, y: k.get("signature") == y,
    },
]


class U1QuantifierSwapGenerator(Generator):
    generator_id = "u1"
    claim_kind = ClaimKind.QUANTIFIER_SWAP.value
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
        return f"u1: quantifier_swap (real) — {len(SWAP_TEMPLATES)} ∀∃ vs ∃∀ checks"

    def _resolve_set(self, key):
        if key == "ecs_small":
            return [e for e in self._ecs if ((e.get("base") or {}).get("conductor") or 1e9) <= 50][:50]
        if key == "primes_small":
            return [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        if key == "knots_small":
            return [k for k in self._knots if (k.get("crossing_number") or 99) <= 7][:40]
        if key == "small_ints":
            return [-2, -1, 0, 1, 2]
        return []

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(SWAP_TEMPLATES):
            tpl = SWAP_TEMPLATES[self._cursor]
            self._cursor += 1
            self.attempts += 1
            X = self._resolve_set(tpl["set_x_extract"])
            Y = self._resolve_set(tpl["set_y_extract"])
            if not X or not Y:
                continue
            # ∀x ∃y R(x,y)
            forall_exists_holds = True
            counter_x = None
            for x in X:
                if not any(tpl["relation_fn"](x, y) for y in Y):
                    forall_exists_holds = False
                    counter_x = x
                    break
            # ∃y ∀x R(x,y)
            exists_forall_holds = False
            witness_y = None
            for y in Y:
                if all(tpl["relation_fn"](x, y) for x in X):
                    exists_forall_holds = True
                    witness_y = y
                    break

            if forall_exists_holds == exists_forall_holds:
                # Both hold or both fail — quantifier swap doesn't distinguish in this catalog
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = (
                    f"∀∃={forall_exists_holds} == ∃∀={exists_forall_holds} "
                    f"on this catalog — swap does NOT distinguish"
                )
            else:
                # Swap distinguishes — the two forms give different verdicts
                verdict = Verdict.REJECTED.value
                kill_pattern = "u1_quantifier_swap_distinguishes"
                outcome = (
                    f"∀∃={forall_exists_holds} ≠ ∃∀={exists_forall_holds} — "
                    f"quantifier order MATTERS in this catalog"
                )

            canonical = f"U1_QSWAP[{tpl['id']}] X={tpl['set_x_desc']} Y={tpl['set_y_desc']} R={tpl['relation_desc']} — {outcome}"
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
                    "set_x_desc": tpl["set_x_desc"],
                    "set_y_desc": tpl["set_y_desc"],
                    "relation_desc": tpl["relation_desc"],
                    "set_x_size": len(X),
                    "set_y_size": len(Y),
                    "forall_exists_holds": forall_exists_holds,
                    "exists_forall_holds": exists_forall_holds,
                    "witness_y": witness_y,
                    "logical_form": "quantifier_order_sensitivity",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
