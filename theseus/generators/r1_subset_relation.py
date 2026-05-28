"""R1 — subset relation generator (REAL, Stage 28).

Emits claims about set relations (⊆, ⊇, =, ∩=∅) between
computable catalog subsets. Each claim is verified by enumeration
over the live knot + EC catalogs.

Real implementation: define a registry of (set_A_predicate,
set_B_predicate, claimed_relation) triples. For each, enumerate
both subsets from the catalog, compute the actual relation, and
emit a record with verdict reflecting whether the CLAIMED relation
matches the ACTUAL relation. When the claim is REJECTED, attach
a witness element demonstrating the violation.

From Sphinx domain G (Set Theory).
Plan: pivot/techne_15gen_plan_2026-05-28.md
Discipline: pivot/techne_kill_pattern_audit_2026-05-28.md
"""
from __future__ import annotations

import gzip
import json
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


def _ec_label(ec: dict) -> str:
    base = ec.get("base") or {}
    return f"ec:{base.get('label') or base.get('cremona_label') or '?'}"


def _knot_label(k: dict) -> str:
    return f"knot:{k.get('name', '?')}"


# Predicates over catalog objects.
# Each: (descriptor_string, domain, predicate_fn)
def _p_ec_rank_ge(n: int) -> Callable[[dict], bool]:
    def fn(e):
        base = e.get("base") or {}
        r = base.get("rank")
        return isinstance(r, int) and r >= n
    return fn


def _p_ec_conductor_ge(n: int) -> Callable[[dict], bool]:
    def fn(e):
        base = e.get("base") or {}
        c = base.get("conductor")
        return isinstance(c, int) and c >= n
    return fn


def _p_ec_conductor_le(n: int) -> Callable[[dict], bool]:
    def fn(e):
        base = e.get("base") or {}
        c = base.get("conductor")
        return isinstance(c, int) and c <= n
    return fn


def _p_ec_torsion_eq(t: int) -> Callable[[dict], bool]:
    def fn(e):
        rich = e.get("rich") or {}
        return rich.get("torsion") == t
    return fn


def _p_knot_crossings_le(n: int) -> Callable[[dict], bool]:
    def fn(k):
        c = k.get("crossing_number")
        return isinstance(c, int) and c <= n
    return fn


def _p_knot_det_even(k: dict) -> bool:
    d = k.get("determinant")
    return isinstance(d, int) and d % 2 == 0


def _p_knot_signature_eq(s: int) -> Callable[[dict], bool]:
    def fn(k):
        return k.get("signature") == s
    return fn


# Subset claim templates. relation in {"subset", "equals", "disjoint"}.
SUBSET_CLAIMS: List[Dict[str, Any]] = [
    {
        "id": "ec_rank_ge3_subset_conductor_ge_5077",
        "domain": "ec",
        "set_a_desc": "EC[rank ≥ 3]",
        "set_a_pred": _p_ec_rank_ge(3),
        "set_b_desc": "EC[conductor ≥ 5077]",
        "set_b_pred": _p_ec_conductor_ge(5077),
        "relation": "subset",
        "claim_text": "Every EC with rank ≥ 3 has conductor ≥ 5077",
    },
    {
        "id": "ec_rank_ge2_subset_conductor_ge_389",
        "domain": "ec",
        "set_a_desc": "EC[rank ≥ 2]",
        "set_a_pred": _p_ec_rank_ge(2),
        "set_b_desc": "EC[conductor ≥ 389]",
        "set_b_pred": _p_ec_conductor_ge(389),
        "relation": "subset",
        "claim_text": "Every EC with rank ≥ 2 has conductor ≥ 389",
    },
    {
        "id": "ec_rank_ge4_disjoint_cond_le_1000",
        "domain": "ec",
        "set_a_desc": "EC[rank ≥ 4]",
        "set_a_pred": _p_ec_rank_ge(4),
        "set_b_desc": "EC[conductor ≤ 1000]",
        "set_b_pred": _p_ec_conductor_le(1000),
        "relation": "disjoint",
        "claim_text": "No EC with rank ≥ 4 has conductor ≤ 1000",
    },
    {
        "id": "ec_torsion_5_subset_cond_le_100",
        "domain": "ec",
        "set_a_desc": "EC[torsion = 5]",
        "set_a_pred": _p_ec_torsion_eq(5),
        "set_b_desc": "EC[conductor ≤ 100]",
        "set_b_pred": _p_ec_conductor_le(100),
        "relation": "subset",
        "claim_text": "Every EC with torsion order 5 has conductor ≤ 100",
    },
    {
        "id": "knot_det_even_subset_sig_zero",
        "domain": "knot",
        "set_a_desc": "knots with det even",
        "set_a_pred": _p_knot_det_even,
        "set_b_desc": "knots with signature = 0",
        "set_b_pred": _p_knot_signature_eq(0),
        "relation": "subset",
        "claim_text": "Every knot with even determinant has signature 0",
    },
    {
        "id": "knot_crossings_le5_subset_sig_zero",
        "domain": "knot",
        "set_a_desc": "knots with crossings ≤ 5",
        "set_a_pred": _p_knot_crossings_le(5),
        "set_b_desc": "knots with signature = 0",
        "set_b_pred": _p_knot_signature_eq(0),
        "relation": "subset",
        "claim_text": "Every knot with ≤ 5 crossings has signature 0",
    },
    {
        "id": "ec_torsion_7_disjoint_cond_le_10",
        "domain": "ec",
        "set_a_desc": "EC[torsion = 7]",
        "set_a_pred": _p_ec_torsion_eq(7),
        "set_b_desc": "EC[conductor ≤ 10]",
        "set_b_pred": _p_ec_conductor_le(10),
        "relation": "disjoint",
        "claim_text": "No EC with torsion order 7 has conductor ≤ 10",
    },
    {
        "id": "knot_crossings_le3_equals_unknot_trefoil",
        "domain": "knot",
        "set_a_desc": "knots with crossings ≤ 3",
        "set_a_pred": _p_knot_crossings_le(3),
        "set_b_desc": "knots with signature ∈ {-2, 0, 2}",
        "set_b_pred": lambda k: k.get("signature") in (-2, 0, 2),
        "relation": "subset",
        "claim_text": "Every knot with ≤ 3 crossings has signature ∈ {-2, 0, 2}",
    },
]


class R1SubsetRelationGenerator(Generator):
    generator_id = "r1"
    claim_kind = ClaimKind.SUBSET_RELATION.value
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
        return (
            f"r1: subset_relation (real) — {len(SUBSET_CLAIMS)} templates "
            f"verified against knot ({len(self._knots)}) + "
            f"EC ({len(self._ecs)}) catalogs"
        )

    def _catalog_for(self, domain: str) -> List[dict]:
        return self._knots if domain == "knot" else self._ecs

    def _label_for(self, domain: str, obj: dict) -> str:
        return _knot_label(obj) if domain == "knot" else _ec_label(obj)

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(SUBSET_CLAIMS):
            c = SUBSET_CLAIMS[self._cursor]
            self._cursor += 1
            self.attempts += 1

            catalog = self._catalog_for(c["domain"])
            set_a = [o for o in catalog if c["set_a_pred"](o)]
            set_b = [o for o in catalog if c["set_b_pred"](o)]

            witness = None
            actual_relation = None
            if c["relation"] == "subset":
                # claim: A ⊆ B; witness = X ∈ A but X ∉ B
                witness_obj = next((o for o in set_a if not c["set_b_pred"](o)), None)
                if witness_obj is None:
                    actual_relation = "subset_holds"
                else:
                    witness = self._label_for(c["domain"], witness_obj)
                    actual_relation = f"counterexample_in_A_not_B"
            elif c["relation"] == "disjoint":
                # claim: A ∩ B = ∅; witness = X ∈ A ∩ B
                witness_obj = next((o for o in set_a if c["set_b_pred"](o)), None)
                if witness_obj is None:
                    actual_relation = "disjoint_holds"
                else:
                    witness = self._label_for(c["domain"], witness_obj)
                    actual_relation = "intersection_nonempty"
            elif c["relation"] == "equals":
                # claim: A = B; witness = X ∈ A△B (symmetric difference)
                in_a_not_b = next((o for o in set_a if not c["set_b_pred"](o)), None)
                if in_a_not_b is not None:
                    witness = self._label_for(c["domain"], in_a_not_b)
                    actual_relation = "in_A_not_B"
                else:
                    in_b_not_a = next((o for o in set_b if not c["set_a_pred"](o)), None)
                    if in_b_not_a is not None:
                        witness = self._label_for(c["domain"], in_b_not_a)
                        actual_relation = "in_B_not_A"
                    else:
                        actual_relation = "equality_holds"

            if witness is not None:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"r1_subset_relation_violated_at_{witness}"
                outcome_str = f"REFUTED by {witness}; actual: {actual_relation}"
            else:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome_str = (
                    f"HOLDS within catalog "
                    f"(|A|={len(set_a)}, |B|={len(set_b)})"
                )

            canonical = (
                f"R1_SUBSET[{c['id']}] {c['set_a_desc']} "
                f"{('⊆' if c['relation']=='subset' else '∩=∅' if c['relation']=='disjoint' else '=')} "
                f"{c['set_b_desc']} — {outcome_str}"
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
                    "claim_id": c["id"],
                    "set_a_description": c["set_a_desc"],
                    "set_b_description": c["set_b_desc"],
                    "claimed_relation": c["relation"],
                    "claim_text": c["claim_text"],
                    "set_a_size": len(set_a),
                    "set_b_size": len(set_b),
                    "witness": witness,
                    "actual_relation": actual_relation,
                    "logical_form": "set_relation",
                    "outcome": outcome_str,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
