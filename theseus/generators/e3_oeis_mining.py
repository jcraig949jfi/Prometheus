"""E3 — OEIS sequence-property mining (token-free, local dump).

Mines the local OEIS sleeping-sequence dump
(`prometheus_math/databases/oeis_sleeping.json.gz`) for testable
properties: monotonicity, sign-uniformity, growth-class consistency,
recurrence-shape, etc. Each emission tests one property per sequence.

Properties tested (v0.1):
  - monotonic_increasing: ∀i, a[i+1] >= a[i]
  - strictly_positive: ∀i, a[i] > 0
  - exponential_growth_consistent: log(a[n+1]) - log(a[n]) ≈ const
  - alternating_sign: signs alternate
  - even_at_even_index: a[2k] is even

Token-free, no LLM, no network. Reads the gzipped JSON once at init.
212 sequences × 5 properties = 1060 unique (seq, prop) regions.
"""
from __future__ import annotations

import gzip
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from theseus.config import REPO_ROOT
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus


OEIS_DB_PATH = REPO_ROOT / "prometheus_math" / "databases" / "oeis_sleeping.json.gz"


def _prop_monotonic_increasing(data: List[int]) -> Tuple[bool, str]:
    if len(data) < 2:
        return False, "len<2"
    return all(data[i + 1] >= data[i] for i in range(len(data) - 1)), ""


def _prop_strictly_positive(data: List[int]) -> Tuple[bool, str]:
    if not data:
        return False, "empty"
    return all(v > 0 for v in data), ""


def _prop_exponential_growth_consistent(
    data: List[int], tol: float = 0.5
) -> Tuple[bool, str]:
    """Check whether log-ratios are roughly constant (exponential growth)."""
    pos = [v for v in data if v > 0]
    if len(pos) < 5:
        return False, "fewer than 5 positive values"
    ratios = [math.log(pos[i + 1]) - math.log(pos[i]) for i in range(len(pos) - 1)]
    if not ratios:
        return False, "no ratios"
    mean = sum(ratios) / len(ratios)
    var = sum((r - mean) ** 2 for r in ratios) / len(ratios)
    return math.sqrt(var) < tol, f"stdev_log_ratio={math.sqrt(var):.3f}"


def _prop_alternating_sign(data: List[int]) -> Tuple[bool, str]:
    nonzero = [v for v in data if v != 0]
    if len(nonzero) < 3:
        return False, "<3 nonzero"
    return all((nonzero[i] > 0) != (nonzero[i + 1] > 0) for i in range(len(nonzero) - 1)), ""


def _prop_even_at_even_index(data: List[int]) -> Tuple[bool, str]:
    if len(data) < 4:
        return False, "<4 values"
    even_indices = [data[i] for i in range(0, len(data), 2)]
    return all(v % 2 == 0 for v in even_indices), ""


PROPERTIES: Dict[str, Callable[[List[int]], Tuple[bool, str]]] = {
    "monotonic_increasing": _prop_monotonic_increasing,
    "strictly_positive": _prop_strictly_positive,
    "exponential_growth_consistent": _prop_exponential_growth_consistent,
    "alternating_sign": _prop_alternating_sign,
    "even_at_even_index": _prop_even_at_even_index,
}


def _load_oeis(path: Path = OEIS_DB_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.get("entries", []))
    except (OSError, json.JSONDecodeError):
        return []


class E3OEISMiningGenerator(Generator):
    generator_id = "e3"
    claim_kind = ClaimKind.LITERATURE_MINED.value
    status = GeneratorStatus.ACTIVE

    def __init__(self, batch_id: str, seed: int = 50) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._entries = _load_oeis()
        self._props = list(PROPERTIES.keys())

    def description(self) -> str:
        return (
            f"e3: OEIS sequence-property mining "
            f"({len(self._entries)} sequences × {len(PROPERTIES)} properties)"
        )

    def next(self) -> Optional[TheseusRecord]:
        if not self._entries:
            return None
        for _ in range(15):
            entry = self._rng.choice(self._entries)
            prop_name = self._rng.choice(self._props)
            data = entry.get("data", [])
            if len(data) < 3:
                self.attempts += 1
                continue
            holds, detail = PROPERTIES[prop_name](data)
            self.attempts += 1

            a_number = entry.get("a_number", "?")
            seq_name = (entry.get("name") or "")[:80]
            verdict = (
                Verdict.SHADOW_CATALOG.value if holds
                else Verdict.REJECTED.value
            )
            kill_pattern = None if holds else f"e3_property_{prop_name}_violated"

            canonical = (
                f"E3_OEIS[{a_number}, {prop_name}] "
                f"name='{seq_name}' | n={len(data)} | "
                f"holds={holds} {('| ' + detail) if detail else ''}"
            )
            payload = {
                "a_number": a_number,
                "sequence_name": seq_name,
                "property": prop_name,
                "n_values": len(data),
                "first_5_values": data[:5],
                "holds": holds,
                "detail": detail,
                "growth_class": entry.get("growth_class"),
                "is_anchor": entry.get("is_anchor"),
            }
            record_id = TheseusRecord.compute_record_id(
                canonical_claim_text=canonical,
                generator_id=self.generator_id,
            )
            r = TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload=payload,
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
                method="local_dump_property_check",
                convergence_status="exact",
                extras={"source": "oeis_sleeping_local_dump"},
            )
            self.emitted.append(record_id)
            return r

        return None
