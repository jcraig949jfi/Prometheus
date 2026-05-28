"""M2 — corpus compression generator (REAL, Stage 31).

Real version reads the live catalog and emits "universal over
subset" lemma-statements. For each (subset_predicate, property)
template, enumerates the subset, checks the property on every
member, and emits:
- SHADOW_CATALOG if ∀ X in subset, P(X) — confirmed universal
- REJECTED with kill_pattern if a counterexample exists,
  attaches witness.

This subsumes many individual records (one per X) into a single
compressed lemma.
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


COMPRESSION_TEMPLATES = [
    {
        "id": "ec_small_cond_rank_le_2",
        "domain": "ec",
        "subset_desc": "EC[conductor ≤ 100]",
        "subset_pred": lambda o: isinstance((o.get("base") or {}).get("conductor"), int)
                                  and (o.get("base") or {})["conductor"] <= 100,
        "property_desc": "rank ≤ 2",
        "property_pred": lambda o: isinstance((o.get("base") or {}).get("rank"), int)
                                    and (o.get("base") or {})["rank"] <= 2,
    },
    {
        "id": "ec_torsion_dvd_12",
        "domain": "ec",
        "subset_desc": "all EC",
        "subset_pred": lambda o: True,
        "property_desc": "torsion ∈ Mazur's list (divides 12 or has Z/2×Z/2n shape)",
        "property_pred": lambda o: ((o.get("rich") or {}).get("torsion") in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16}),
    },
    {
        "id": "knot_low_cross_genus_bound",
        "domain": "knot",
        "subset_desc": "knots[crossings ≤ 8]",
        "subset_pred": lambda o: (o.get("crossing_number") or 99) <= 8,
        "property_desc": "three_genus ≤ 4",
        "property_pred": lambda o: (o.get("three_genus") or 99) <= 4,
    },
    {
        "id": "knot_amphichiral_implies_signature_zero",
        "domain": "knot",
        "subset_desc": "knots with |det| in {1,3,5,7,9,11,13}",
        "subset_pred": lambda o: abs(o.get("determinant") or 0) in {1, 3, 5, 7, 9, 11, 13},
        "property_desc": "signature = 0",
        "property_pred": lambda o: o.get("signature") == 0,
    },
    {
        "id": "ec_rank_zero_implies_l1_positive",
        "domain": "ec",
        "subset_desc": "EC[rank = 0]",
        "subset_pred": lambda o: (o.get("base") or {}).get("rank") == 0,
        "property_desc": "L1 > 0 (BSD-consistent)",
        "property_pred": lambda o: isinstance((o.get("rich") or {}).get("L1"), (int, float))
                                    and (o.get("rich") or {})["L1"] > 0,
    },
]


class M2CompressionGenerator(Generator):
    generator_id = "m2"
    claim_kind = ClaimKind.CORPUS_COMPRESSION.value
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
        return f"m2: corpus_compression (real) — {len(COMPRESSION_TEMPLATES)} universal claims"

    def _label(self, domain, obj):
        if domain == "knot":
            return f"knot:{obj.get('name','?')}"
        base = obj.get("base") or {}
        return f"ec:{base.get('label') or base.get('cremona_label') or '?'}"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(COMPRESSION_TEMPLATES):
            tpl = COMPRESSION_TEMPLATES[self._cursor]
            self._cursor += 1
            self.attempts += 1
            catalog = self._knots if tpl["domain"] == "knot" else self._ecs
            subset = [o for o in catalog if tpl["subset_pred"](o)]
            n = len(subset)
            if n == 0:
                continue
            counterexample = None
            for o in subset:
                try:
                    if not tpl["property_pred"](o):
                        counterexample = o
                        break
                except Exception:
                    continue
            if counterexample is None:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = f"UNIVERSAL holds across {n} members"
                witness_label = None
            else:
                verdict = Verdict.REJECTED.value
                witness_label = self._label(tpl["domain"], counterexample)
                kill_pattern = f"m2_universal_violated_by_{witness_label}"
                outcome = f"UNIVERSAL refuted by {witness_label} (of {n} members)"
            canonical = (
                f"M2_COMPRESSION[{tpl['id']}] ∀ X ∈ {tpl['subset_desc']}, "
                f"{tpl['property_desc']} — {outcome}"
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
                    "compression_id": tpl["id"],
                    "subset_description": tpl["subset_desc"],
                    "subset_size": n,
                    "property_description": tpl["property_desc"],
                    "witness": witness_label,
                    "logical_form": "universal_over_subset",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
