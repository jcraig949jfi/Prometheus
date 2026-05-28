"""AA1 — confidence calibration generator (REAL, Stage 32).

For each (claim, declared_confidence) template, computes the
ACTUAL outcome from the catalog and compares to the declared
confidence. Emits meta-record flagging miscalibration (stated
confidence >> actual rate, or stated << actual).

From Sphinx domain I (Meta-Reasoning).
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


# Each calibration check: (claim_label, predicate, stated_confidence).
# The "stated_confidence" is what the substrate would have stated;
# the "actual_rate" is computed from real catalog.
CALIBRATION_PROBES = [
    {
        "id": "knot_signature_zero_assumed_common",
        "domain": "knot",
        "claim_label": "knot has signature = 0",
        "predicate": lambda o: o.get("signature") == 0,
        "stated_confidence": 0.50,
    },
    {
        "id": "ec_torsion_trivial_assumed_majority",
        "domain": "ec",
        "claim_label": "EC has trivial torsion (T(E) = {0})",
        "predicate": lambda o: (o.get("rich") or {}).get("torsion") == 1,
        "stated_confidence": 0.60,
    },
    {
        "id": "ec_rank_zero_assumed_majority",
        "domain": "ec",
        "claim_label": "EC has rank = 0",
        "predicate": lambda o: (o.get("base") or {}).get("rank") == 0,
        "stated_confidence": 0.50,
    },
    {
        "id": "knot_amphichiral_assumed_rare",
        "domain": "knot",
        "claim_label": "knot is amphichiral (sig=0 AND |det| odd)",
        "predicate": lambda o: o.get("signature") == 0
                                 and abs(o.get("determinant") or 0) % 2 == 1,
        "stated_confidence": 0.10,
    },
    {
        "id": "ec_high_tamagawa_assumed_rare",
        "domain": "ec",
        "claim_label": "EC has tamagawa_product ≥ 4",
        "predicate": lambda o: ((o.get("rich") or {}).get("tamagawa_product") or 0) >= 4,
        "stated_confidence": 0.05,
    },
]

# Miscalibration tolerance: difference between stated and actual > this triggers REJECTED
MISCALIBRATION_THRESHOLD = 0.15


class Aa1ConfidenceCalibrationGenerator(Generator):
    generator_id = "aa1"
    claim_kind = ClaimKind.CONFIDENCE_CALIBRATION.value
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
        return f"aa1: confidence_calibration (real) — {len(CALIBRATION_PROBES)} checks"

    def next(self) -> Optional[TheseusRecord]:
        while self._cursor < len(CALIBRATION_PROBES):
            p = CALIBRATION_PROBES[self._cursor]
            self._cursor += 1
            self.attempts += 1
            catalog = self._knots if p["domain"] == "knot" else self._ecs
            if not catalog:
                continue
            n_total = len(catalog)
            n_holds = sum(1 for o in catalog if p["predicate"](o))
            actual_rate = n_holds / n_total
            stated = p["stated_confidence"]
            delta = stated - actual_rate
            if abs(delta) > MISCALIBRATION_THRESHOLD:
                direction = "OVERCONFIDENT" if delta > 0 else "UNDERCONFIDENT"
                verdict = Verdict.REJECTED.value
                kill_pattern = f"aa1_confidence_miscalibrated_{direction.lower()}"
                outcome = (
                    f"{direction}: stated={stated:.2f}, actual={actual_rate:.3f}, "
                    f"|delta|={abs(delta):.3f} > {MISCALIBRATION_THRESHOLD}"
                )
            else:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
                outcome = (
                    f"calibrated: stated={stated:.2f}, actual={actual_rate:.3f}, "
                    f"|delta|={abs(delta):.3f} ≤ {MISCALIBRATION_THRESHOLD}"
                )
            canonical = (
                f"AA1_CALIB[{p['id']}] claim='{p['claim_label']}': {outcome}"
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
                    "claim_id": p["id"],
                    "claim_label": p["claim_label"],
                    "stated_confidence": stated,
                    "actual_rate": round(actual_rate, 4),
                    "delta": round(delta, 4),
                    "n_total": n_total,
                    "n_holds": n_holds,
                    "logical_form": "confidence_vs_precision_meta_claim",
                    "outcome": outcome,
                },
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
            )
        return None
