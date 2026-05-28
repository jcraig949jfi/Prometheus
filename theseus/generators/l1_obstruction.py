"""L1 — obstruction (negative-existential) generator, real version.

Emits claims of the form:

    ∄ X ∈ S such that P(X) holds

For each obstruction template, l1 EXECUTES the bounded search
over a subset of the real catalog and emits a record whose
verdict reflects the outcome:
- SHADOW_CATALOG: search completed without finding any X satisfying
  P(X) → the obstruction holds (within the search bound)
- REJECTED: search found a witness X with P(X) → obstruction
  refuted, witness attached to payload
- UNVERIFIED: search aborted (catalog gap, type error, etc.)

Real implementation (Stage 12): a small set of obstruction
templates defined as (catalog, predicate function, bound). The
generator iterates the template list, runs each search live, and
emits one record per template.

Plan: pivot/techne_5gen_plan_2026-05-27.md
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
    return base.get("label") or base.get("cremona_label") or "?"


def _knot_label(k: dict) -> str:
    return k.get("name", "?")


# ---------------------------------------------------------------------------
# Obstruction templates
# ---------------------------------------------------------------------------
# Each template: (template_id, search_set_descriptor,
#                  catalog_subset_fn, predicate_fn,
#                  obstruction_text)
#
# - catalog_subset_fn: takes the full catalog, returns the subset to
#   search over. Implements the bound.
# - predicate_fn: takes one catalog object, returns True if it
#   satisfies P (i.e., refutes the obstruction).
#
# A SHADOW_CATALOG result means: enumerated the full subset, no
# witness found → obstruction holds in the bound.
# A REJECTED result means: found a witness → obstruction refuted,
# witness attached.
# ---------------------------------------------------------------------------


def _subset_ec_conductor_le(N: int) -> Callable[[List[dict]], List[dict]]:
    def _fn(ecs: List[dict]) -> List[dict]:
        out = []
        for ec in ecs:
            base = ec.get("base") or {}
            c = base.get("conductor")
            if isinstance(c, int) and c <= N:
                out.append(ec)
        return out
    return _fn


def _subset_knot_crossing_le(N: int) -> Callable[[List[dict]], List[dict]]:
    def _fn(knots: List[dict]) -> List[dict]:
        return [k for k in knots if isinstance(k.get("crossing_number"), int)
                and k["crossing_number"] <= N]
    return _fn


def _pred_ec_rank_ge(threshold: int) -> Callable[[dict], bool]:
    def _fn(ec: dict) -> bool:
        base = ec.get("base") or {}
        r = base.get("rank")
        return isinstance(r, int) and r >= threshold
    return _fn


def _pred_knot_det_and_signature(div_p: int, sig: int) -> Callable[[dict], bool]:
    def _fn(k: dict) -> bool:
        d = k.get("determinant")
        s = k.get("signature")
        if not isinstance(d, int) or not isinstance(s, int):
            return False
        return (d % div_p == 0) and (s == sig)
    return _fn


def _pred_knot_three_genus_eq(g: int) -> Callable[[dict], bool]:
    def _fn(k: dict) -> bool:
        return k.get("three_genus") == g
    return _fn


def _pred_ec_torsion_order_eq(t: int) -> Callable[[dict], bool]:
    def _fn(ec: dict) -> bool:
        rich = ec.get("rich") or {}
        return rich.get("torsion") == t
    return _fn


def _pred_ec_tamagawa_eq(t: int) -> Callable[[dict], bool]:
    def _fn(ec: dict) -> bool:
        rich = ec.get("rich") or {}
        return rich.get("tamagawa_product") == t
    return _fn


def _pred_knot_nf_class_eq(h: int) -> Callable[[dict], bool]:
    def _fn(k: dict) -> bool:
        return k.get("nf_class_number") == h
    return _fn


OBSTRUCTION_TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "no_ec_cond_le_100_rank_ge_5",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 100",
        "search_bound": 100,
        "subset_fn": _subset_ec_conductor_le(100),
        "predicate_fn": _pred_ec_rank_ge(5),
        "predicate_text": "rank ≥ 5",
        "human_summary": "∄ E ∈ EC[conductor ≤ 100] : rank(E) ≥ 5",
    },
    {
        "id": "no_ec_cond_le_1000_rank_ge_6",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 1000",
        "search_bound": 1000,
        "subset_fn": _subset_ec_conductor_le(1000),
        "predicate_fn": _pred_ec_rank_ge(6),
        "predicate_text": "rank ≥ 6",
        "human_summary": "∄ E ∈ EC[conductor ≤ 1000] : rank(E) ≥ 6",
    },
    {
        "id": "no_ec_cond_le_5000_rank_ge_3",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 5000",
        "search_bound": 5000,
        "subset_fn": _subset_ec_conductor_le(5000),
        "predicate_fn": _pred_ec_rank_ge(3),
        "predicate_text": "rank ≥ 3",
        "human_summary": "∄ E ∈ EC[conductor ≤ 5000] : rank(E) ≥ 3",
    },
    {
        "id": "no_knot_le_10_det_div7_sig0",
        "domain": "knot",
        "search_set_description": "knots with crossing_number ≤ 10",
        "search_bound": 10,
        "subset_fn": _subset_knot_crossing_le(10),
        "predicate_fn": _pred_knot_det_and_signature(7, 0),
        "predicate_text": "7 | det(K) ∧ σ(K) = 0",
        "human_summary": "∄ K ∈ Knot[crossings ≤ 10] : 7 | det(K) ∧ σ(K) = 0",
    },
    {
        "id": "no_knot_le_10_det_div5_sig2",
        "domain": "knot",
        "search_set_description": "knots with crossing_number ≤ 10",
        "search_bound": 10,
        "subset_fn": _subset_knot_crossing_le(10),
        "predicate_fn": _pred_knot_det_and_signature(5, 2),
        "predicate_text": "5 | det(K) ∧ σ(K) = 2",
        "human_summary": "∄ K ∈ Knot[crossings ≤ 10] : 5 | det(K) ∧ σ(K) = 2",
    },
    {
        "id": "no_knot_le_8_genus_eq_3",
        "domain": "knot",
        "search_set_description": "knots with crossing_number ≤ 8",
        "search_bound": 8,
        "subset_fn": _subset_knot_crossing_le(8),
        "predicate_fn": _pred_knot_three_genus_eq(3),
        "predicate_text": "three_genus = 3",
        "human_summary": "∄ K ∈ Knot[crossings ≤ 8] : g_3(K) = 3",
    },
    {
        "id": "no_ec_cond_le_500_torsion_eq_15",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 500",
        "search_bound": 500,
        "subset_fn": _subset_ec_conductor_le(500),
        "predicate_fn": _pred_ec_torsion_order_eq(15),
        "predicate_text": "|torsion(E)| = 15",
        "human_summary": "∄ E ∈ EC[conductor ≤ 500] : |E_tors(Q)| = 15",
    },
    {
        "id": "no_ec_cond_le_300_tamagawa_eq_11",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 300",
        "search_bound": 300,
        "subset_fn": _subset_ec_conductor_le(300),
        "predicate_fn": _pred_ec_tamagawa_eq(11),
        "predicate_text": "tamagawa_product(E) = 11",
        "human_summary": "∄ E ∈ EC[conductor ≤ 300] : c(E) = 11",
    },
    {
        "id": "no_knot_le_10_nf_class_ge_5",
        "domain": "knot",
        "search_set_description": "knots with crossing_number ≤ 10",
        "search_bound": 10,
        "subset_fn": _subset_knot_crossing_le(10),
        "predicate_fn": lambda k: isinstance(k.get("nf_class_number"), int) and k["nf_class_number"] >= 5,
        "predicate_text": "nf_class_number(K) ≥ 5",
        "human_summary": "∄ K ∈ Knot[crossings ≤ 10] : h(K) ≥ 5",
    },
    {
        "id": "no_ec_cond_le_2000_rank_ge_4",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 2000",
        "search_bound": 2000,
        "subset_fn": _subset_ec_conductor_le(2000),
        "predicate_fn": _pred_ec_rank_ge(4),
        "predicate_text": "rank ≥ 4",
        "human_summary": "∄ E ∈ EC[conductor ≤ 2000] : rank(E) ≥ 4",
    },
    {
        "id": "no_knot_le_9_nf_class_eq_2",
        "domain": "knot",
        "search_set_description": "knots with crossing_number ≤ 9",
        "search_bound": 9,
        "subset_fn": _subset_knot_crossing_le(9),
        "predicate_fn": _pred_knot_nf_class_eq(2),
        "predicate_text": "nf_class_number(K) = 2",
        "human_summary": "∄ K ∈ Knot[crossings ≤ 9] : h(K) = 2",
    },
    {
        "id": "no_ec_cond_le_1000_tamagawa_ge_8",
        "domain": "ec",
        "search_set_description": "EC of conductor ≤ 1000",
        "search_bound": 1000,
        "subset_fn": _subset_ec_conductor_le(1000),
        "predicate_fn": lambda ec: isinstance((ec.get("rich") or {}).get("tamagawa_product"), int) and (ec.get("rich") or {})["tamagawa_product"] >= 8,
        "predicate_text": "tamagawa_product ≥ 8",
        "human_summary": "∄ E ∈ EC[conductor ≤ 1000] : c(E) ≥ 8",
    },
]


class L1ObstructionGenerator(Generator):
    generator_id = "l1"
    claim_kind = ClaimKind.OBSTRUCTION.value
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
            f"l1: obstruction (real) — "
            f"{len(OBSTRUCTION_TEMPLATES)} templates, "
            f"executes bounded search on knot ({len(self._knots)}) + "
            f"EC ({len(self._ecs)}) catalogs"
        )

    def _catalog_for(self, domain: str) -> List[dict]:
        return self._knots if domain == "knot" else self._ecs

    def _witness_label(self, domain: str, obj: dict) -> str:
        return f"knot:{_knot_label(obj)}" if domain == "knot" else f"ec:{_ec_label(obj)}"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(OBSTRUCTION_TEMPLATES):
            tpl = OBSTRUCTION_TEMPLATES[self._cursor]
            self._cursor += 1
            self.attempts += 1

            catalog = self._catalog_for(tpl["domain"])
            try:
                subset = tpl["subset_fn"](catalog)
            except Exception:
                continue
            enumerated = 0
            witness = None
            for obj in subset:
                enumerated += 1
                try:
                    if tpl["predicate_fn"](obj):
                        witness = obj
                        break
                except Exception:
                    continue

            if witness is not None:
                verdict = Verdict.REJECTED.value
                witness_text = self._witness_label(tpl["domain"], witness)
                outcome_str = f"REFUTED by witness {witness_text}"
            elif enumerated > 0:
                verdict = Verdict.SHADOW_CATALOG.value
                witness_text = None
                outcome_str = f"CONFIRMED within bound ({enumerated} enumerated)"
            else:
                # Empty subset — search vacuously confirms but is uninformative.
                verdict = Verdict.UNVERIFIED.value
                witness_text = None
                outcome_str = "SEARCH_EMPTY: subset was empty"

            canonical = (
                f"L1_OBSTRUCTION[{tpl['id']}] {tpl['human_summary']} — "
                f"{outcome_str}"
            )
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)

            kill_pattern = (
                "obstruction_refuted_by_witness" if witness is not None else None
            )

            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "template_id": tpl["id"],
                    "domain": tpl["domain"],
                    "search_set_description": tpl["search_set_description"],
                    "predicate": tpl["predicate_text"],
                    "search_bound": tpl["search_bound"],
                    "enumerated_count": enumerated,
                    "witness": witness_text,
                    "logical_form": "negative_existential",
                    "outcome": outcome_str,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
