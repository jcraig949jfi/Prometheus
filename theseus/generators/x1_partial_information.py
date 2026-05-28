"""X1 — partial information / closed-world fragility (REAL, Stage 31).

For each (property, view_bound) template: compute the property's
extremal value (max/min/distribution) on the bounded view of the
catalog, then compare to the value computed on the full catalog.
When the bounded view "lies" (underestimates max, overestimates
min, etc.), emit a record showing the inflation.

From Sphinx domain L.
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


# Each template: (id, domain, view_predicate, extract_property, aggregate_fn, agg_label)
PROBES = [
    {
        "id": "ec_rank_max_under_cond_le",
        "domain": "ec",
        "extract": lambda o: (o.get("base") or {}).get("rank"),
        "aggregate": max,
        "agg_label": "max rank",
        "view_bounds": [(50, "conductor ≤ 50"), (100, "conductor ≤ 100"),
                        (500, "conductor ≤ 500"), (1000, "conductor ≤ 1000")],
        "view_pred_for": lambda N: lambda o: ((o.get("base") or {}).get("conductor") or 1e9) <= N,
    },
    {
        "id": "ec_tamagawa_max_under_cond_le",
        "domain": "ec",
        "extract": lambda o: (o.get("rich") or {}).get("tamagawa_product"),
        "aggregate": max,
        "agg_label": "max tamagawa",
        "view_bounds": [(100, "conductor ≤ 100"), (500, "conductor ≤ 500"),
                        (2000, "conductor ≤ 2000")],
        "view_pred_for": lambda N: lambda o: ((o.get("base") or {}).get("conductor") or 1e9) <= N,
    },
    {
        "id": "knot_genus_max_under_crossings_le",
        "domain": "knot",
        "extract": lambda o: o.get("three_genus"),
        "aggregate": max,
        "agg_label": "max three_genus",
        "view_bounds": [(5, "crossings ≤ 5"), (7, "crossings ≤ 7"), (9, "crossings ≤ 9")],
        "view_pred_for": lambda N: lambda o: (o.get("crossing_number") or 99) <= N,
    },
]


class X1PartialInformationGenerator(Generator):
    generator_id = "x1"
    claim_kind = ClaimKind.PARTIAL_INFORMATION.value
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
        self._queue: List[Dict[str, Any]] = []
        for probe in PROBES:
            for N, view_label in probe["view_bounds"]:
                self._queue.append({"probe": probe, "N": N, "view_label": view_label})
        self._cursor = 0

    def description(self) -> str:
        return f"x1: partial_information (real) — {len(self._queue)} (probe, view) checks"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(self._queue):
            item = self._queue[self._cursor]
            self._cursor += 1
            self.attempts += 1
            probe, N, view_label = item["probe"], item["N"], item["view_label"]
            catalog = self._knots if probe["domain"] == "knot" else self._ecs
            view_pred = probe["view_pred_for"](N)
            view_vals = [probe["extract"](o) for o in catalog if view_pred(o)]
            view_vals = [v for v in view_vals if isinstance(v, int)]
            full_vals = [probe["extract"](o) for o in catalog]
            full_vals = [v for v in full_vals if isinstance(v, int)]
            if not view_vals or not full_vals:
                continue
            view_agg = probe["aggregate"](view_vals)
            full_agg = probe["aggregate"](full_vals)
            inflation = full_agg - view_agg  # how much the partial underestimates
            label = f"x1_partial_view_inflation_under_{view_label.replace(' ', '_')}"
            if inflation > 0:
                # the partial view said "max is X", full view shows "max is X+inflation"
                verdict = Verdict.REJECTED.value
                kill_pattern = label
                outcome = (
                    f"PARTIAL view ({view_label}) {probe['agg_label']}={view_agg}; "
                    f"FULL catalog reveals {probe['agg_label']}={full_agg} "
                    f"(under-estimate by {inflation})"
                )
            else:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = (
                    f"partial = full ({view_agg}); no inflation for "
                    f"{probe['agg_label']} under {view_label}"
                )
            canonical = f"X1_PARTIAL[{probe['id']}_under_{view_label}] {outcome}"
            record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
            self.emitted.append(record_id)
            return TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload={
                    "probe_id": probe["id"],
                    "view_label": view_label,
                    "view_bound": N,
                    "view_aggregate": view_agg,
                    "full_aggregate": full_agg,
                    "inflation": inflation,
                    "n_view": len(view_vals),
                    "n_full": len(full_vals),
                    "logical_form": "partial_information_fragility",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
