"""Primitive demand signal logging.

Per persona_seed_prompts_2026-05-21.md Techne idea #1:
"Primitive demand sensor. Theseus often fails to compose because some
primitive is missing. Currently those failures vanish silently — log
every failed composition with the missing-primitive signature,
aggregate weekly, surface the top-N as a 'wanted primitives' board."

A "demand signal" records why a generator failed to compose a record.
Common signatures:
- ("missing_invariant", "ec", "j_invariant_log") — the catalog object
  has no value for that invariant
- ("missing_object_field", "knot", "alexander_polynomial_degree") —
  whole field absent for this object class
- ("singleton_twist_class", "g1") — Galois twist needs ≥2 ECs sharing
  j-invariant but only found one
- ("cache_exhausted", "e2") — E2's arxiv cache fully scanned, no more
  abstracts to mine
- ("parent_starvation", "c1") — C1 mutation needs parent records but
  none available

These are KINDS of missing primitives. Aggregating across batches
surfaces what the substrate WANTS but doesn't have.

Storage: one JSONL per batch at theseus/journals/demand_<batch_id>.jsonl
Aggregation: theseus.scripts.demand_report CLI walks the directory and
emits a top-N "wanted primitives" markdown report.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from theseus.config import JOURNAL_DIR


@dataclass
class DemandSignal:
    """One missing-primitive event."""
    generator_id: str
    kind: str  # e.g. "missing_invariant", "cache_exhausted"
    signature: Tuple[str, ...]  # tuple of strings identifying the gap
    count: int = 1
    example_context: Dict[str, Any] = field(default_factory=dict)


class DemandSignalLog:
    """Per-batch accumulator for primitive-demand signals.

    Generators call .record(gen_id, kind, signature) when a composition
    fails. At batch end, .flush() writes a JSONL aggregate to
    journals/demand_<batch_id>.jsonl with the aggregated counts.

    Singleton via the module-level INSTANCE. Generators access via
    `from theseus.scoring.demand_signals import INSTANCE` then call
    INSTANCE.record(...). Daemon resets per-batch via .reset(batch_id).
    """

    def __init__(self) -> None:
        self._counts: Counter = Counter()
        self._examples: Dict[Tuple, Dict[str, Any]] = {}
        self.batch_id: Optional[str] = None

    def reset(self, batch_id: str) -> None:
        self._counts.clear()
        self._examples.clear()
        self.batch_id = batch_id

    def record(
        self,
        generator_id: str,
        kind: str,
        signature: Tuple[str, ...],
        example_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a demand signal. Cheap: increments a counter and stores
        a single example context per (gen, kind, sig) tuple.
        """
        key = (generator_id, kind, signature)
        self._counts[key] += 1
        if key not in self._examples and example_context:
            # Trim large values for memory safety
            ctx = {k: (str(v)[:128] if v is not None else None)
                   for k, v in example_context.items()}
            self._examples[key] = ctx

    def summary(self) -> List[Dict[str, Any]]:
        """Return list of demand-signal records for serialization."""
        out: List[Dict[str, Any]] = []
        for (gid, kind, sig), n in self._counts.most_common():
            out.append({
                "generator_id": gid,
                "kind": kind,
                "signature": list(sig),
                "count": n,
                "example_context": self._examples.get((gid, kind, sig), {}),
            })
        return out

    def flush(self, path: Optional[Path] = None) -> Optional[Path]:
        """Write the aggregated signals to JSONL. Returns the path written.

        If path is None, derives from batch_id under JOURNAL_DIR.
        Returns None if no signals recorded (no file written).
        """
        if not self._counts:
            return None
        if path is None:
            if self.batch_id is None:
                return None
            path = JOURNAL_DIR / f"demand_{self.batch_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for rec in self.summary():
                f.write(json.dumps(rec, sort_keys=True) + "\n")
        return path

    def __len__(self) -> int:
        return sum(self._counts.values())


# Module-level singleton. Generators import this directly.
INSTANCE = DemandSignalLog()


def iter_demand_files(
    journal_dir: Optional[Path] = None,
) -> Iterator[Path]:
    """Yield all demand_*.jsonl files in the journal directory."""
    if journal_dir is None:
        journal_dir = JOURNAL_DIR
    if not journal_dir.exists():
        return
    for p in sorted(journal_dir.glob("demand_*.jsonl")):
        if p.is_file():
            yield p


def aggregate_signals(
    journal_dir: Optional[Path] = None,
) -> Dict[Tuple[str, str, Tuple[str, ...]], int]:
    """Aggregate demand-signal counts across all per-batch JSONLs.

    Returns {(generator_id, kind, signature_tuple): total_count}
    sorted descending by count when iterated.
    """
    totals: Counter = Counter()
    for p in iter_demand_files(journal_dir):
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                gid = rec.get("generator_id", "?")
                kind = rec.get("kind", "?")
                sig = tuple(rec.get("signature", []))
                count = int(rec.get("count", 0))
                totals[(gid, kind, sig)] += count
    return dict(totals.most_common())
