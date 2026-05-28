"""V1 — counterfactual invariance generator (REAL, Stage 30).

For each catalog object, perturb ONE attribute by a small amount,
re-check whether a stated property still holds on the perturbed
view. Emit kill record when perturbation breaks the property.

This is a "what if attribute X were slightly different" probe —
the substrate's first counterfactual reasoning.

From Sphinx domain F (Causal).
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


# Each perturbation: (id, domain, attribute, delta, property_fn, property_label).
# property_fn takes (attribute_value) → bool (does property P hold).
PERTURBATIONS = [
    {
        "id": "ec_rank_lt_3_under_rank_plus_1",
        "domain": "ec",
        "attribute": "rank",
        "delta": 1,
        "property_fn": lambda v: v < 3,
        "property_label": "rank < 3",
        "extractor": lambda o: (o.get("base") or {}).get("rank"),
    },
    {
        "id": "knot_genus_le_2_under_genus_plus_1",
        "domain": "knot",
        "attribute": "three_genus",
        "delta": 1,
        "property_fn": lambda v: v <= 2,
        "property_label": "three_genus ≤ 2",
        "extractor": lambda o: o.get("three_genus"),
    },
    {
        "id": "ec_cond_lt_1000_under_cond_double",
        "domain": "ec",
        "attribute": "conductor",
        "delta_fn": lambda v: v * 2,
        "property_fn": lambda v: v < 1000,
        "property_label": "conductor < 1000",
        "extractor": lambda o: (o.get("base") or {}).get("conductor"),
    },
    {
        "id": "knot_det_le_20_under_det_plus_5",
        "domain": "knot",
        "attribute": "determinant",
        "delta": 5,
        "property_fn": lambda v: abs(v) <= 20,
        "property_label": "|det| ≤ 20",
        "extractor": lambda o: o.get("determinant"),
    },
]


class V1CounterfactualInvarianceGenerator(Generator):
    generator_id = "v1"
    claim_kind = ClaimKind.COUNTERFACTUAL_INVARIANCE.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    MAX_PER_PERTURBATION = 60

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
        for pert in PERTURBATIONS:
            catalog = self._knots if pert["domain"] == "knot" else self._ecs
            # filter to objects where property holds AND attribute is present
            valid = []
            for o in catalog:
                v = pert["extractor"](o)
                if v is None:
                    continue
                if pert["property_fn"](v):
                    valid.append(o)
            for obj in valid[: self.MAX_PER_PERTURBATION]:
                self._queue.append({"pert": pert, "obj": obj})
        self._cursor = 0

    def description(self) -> str:
        return f"v1: counterfactual_invariance (real) — {len(self._queue)} probes"

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
            pert, obj = item["pert"], item["obj"]
            orig_value = pert["extractor"](obj)
            if "delta_fn" in pert:
                perturbed_value = pert["delta_fn"](orig_value)
            else:
                perturbed_value = orig_value + pert["delta"]
            label = self._label(pert["domain"], obj)
            survives = pert["property_fn"](perturbed_value)
            if survives:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = (
                    f"property '{pert['property_label']}' SURVIVES "
                    f"perturbing {pert['attribute']} {orig_value} → {perturbed_value}"
                )
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = (
                    f"v1_perturbation_breaks_property_{pert['property_label'].replace(' ','_')}"
                )
                outcome = (
                    f"property '{pert['property_label']}' BREAKS when "
                    f"{pert['attribute']} perturbed {orig_value} → {perturbed_value}"
                )
            canonical = f"V1_CFAC[{pert['id']}] on {label}: {outcome}"
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)
            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "perturbation_id": pert["id"],
                    "object": label,
                    "attribute": pert["attribute"],
                    "original_value": orig_value,
                    "perturbed_value": perturbed_value,
                    "property": pert["property_label"],
                    "survives": survives,
                    "logical_form": "counterfactual_invariance",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
