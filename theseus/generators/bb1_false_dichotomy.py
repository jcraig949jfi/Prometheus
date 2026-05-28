"""BB1 — false dichotomy generator (REAL, Stage 32).

For each "naive binary" claim, counts the ACTUAL number of
distinct categories in the catalog. Emits kill record when
the catalog reveals ≥ 3 categories where binary was assumed.

From Sphinx domain J (Common Sense).
"""
from __future__ import annotations

import gzip
import json
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


# Each probe: (id, domain, naive_binary, fine_classifier, expected_max).
# fine_classifier returns a string label per object.
DICHOTOMY_PROBES = [
    {
        "id": "ec_torsion_categories",
        "domain": "ec",
        "naive_binary": "EC torsion is trivial-or-nontrivial",
        "fine_classifier": lambda o: f"Z/{(o.get('rich') or {}).get('torsion', 0)}Z",
        "expected_binary_count": 2,
    },
    {
        "id": "knot_signature_categories",
        "domain": "knot",
        "naive_binary": "knot signature is zero-or-nonzero",
        "fine_classifier": lambda o: f"sig={o.get('signature')}",
        "expected_binary_count": 2,
    },
    {
        "id": "ec_rank_categories",
        "domain": "ec",
        "naive_binary": "EC rank is zero-or-positive",
        "fine_classifier": lambda o: f"rank={(o.get('base') or {}).get('rank')}",
        "expected_binary_count": 2,
    },
    {
        "id": "knot_three_genus_categories",
        "domain": "knot",
        "naive_binary": "knot three_genus is zero-or-positive",
        "fine_classifier": lambda o: f"g={o.get('three_genus')}",
        "expected_binary_count": 2,
    },
    {
        "id": "ec_tamagawa_categories",
        "domain": "ec",
        "naive_binary": "EC tamagawa is one-or-not",
        "fine_classifier": lambda o: f"c={(o.get('rich') or {}).get('tamagawa_product')}",
        "expected_binary_count": 2,
    },
]


class Bb1FalseDichotomyGenerator(Generator):
    generator_id = "bb1"
    claim_kind = ClaimKind.FALSE_DICHOTOMY.value
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
        return f"bb1: false_dichotomy (real) — {len(DICHOTOMY_PROBES)} catalog category counts"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(DICHOTOMY_PROBES):
            p = DICHOTOMY_PROBES[self._cursor]
            self._cursor += 1
            self.attempts += 1
            catalog = self._knots if p["domain"] == "knot" else self._ecs
            categories = Counter()
            for o in catalog:
                try:
                    cat = p["fine_classifier"](o)
                    if cat is not None and "None" not in str(cat):
                        categories[cat] += 1
                except Exception:
                    continue
            n_categories = len(categories)
            top_5 = categories.most_common(5)
            if n_categories > p["expected_binary_count"]:
                verdict = Verdict.REJECTED.value
                kill_pattern = f"bb1_false_dichotomy_revealed_{n_categories}_categories"
                outcome = (
                    f"NAIVE binary is FALSE: {n_categories} actual categories. "
                    f"Top: {top_5}"
                )
            else:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = (
                    f"binary holds: {n_categories} categories observed "
                    f"(≤ {p['expected_binary_count']})"
                )
            canonical = (
                f"BB1_FALSE_DI[{p['id']}] '{p['naive_binary']}' — {outcome}"
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
                    "probe_id": p["id"],
                    "naive_binary": p["naive_binary"],
                    "actual_category_count": n_categories,
                    "top_categories": top_5,
                    "expected_binary_count": p["expected_binary_count"],
                    "logical_form": "false_dichotomy",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
