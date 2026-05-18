"""Upstream-source scanners for Penelope.

A `Source` is a named producer of training_anchor JSONL files. Each scanner
returns candidate input paths sorted oldest-first so older files ingest
before newer ones.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from ergon.penelope.config import APORIA_STAGED_ROOT, THESEUS_OUTBOX


@dataclass(frozen=True)
class Source:
    name: str
    scanner: Callable[[], List[Path]]


def scan_theseus_outbox() -> List[Path]:
    """Theseus handoff bundles: theseus/handoff/ergon_outbox/*.jsonl.

    Excludes _combined_*.jsonl intermediates (those are Theseus-internal
    concatenations that duplicate the per-bundle files).
    """
    if not THESEUS_OUTBOX.exists():
        return []
    out: List[Path] = []
    for p in THESEUS_OUTBOX.glob("*.jsonl"):
        if p.name.startswith("_combined_"):
            continue
        out.append(p)
    out.sort(key=lambda p: p.stat().st_mtime)
    return out


def scan_aporia_staged() -> List[Path]:
    """Aporia hand-staged blocks: aporia/docs/staged_substrate_blocks/<date>/validated.jsonl.

    Only files whose name suggests training_anchor content; the ingester
    is robust to non-training-anchor blocks (filters internally) but we
    skip obviously-empty cases.
    """
    if not APORIA_STAGED_ROOT.exists():
        return []
    out: List[Path] = []
    for date_dir in sorted(APORIA_STAGED_ROOT.iterdir()):
        if not date_dir.is_dir():
            continue
        for name in ("validated.jsonl", "validated_reauthored.jsonl", "training_anchor.jsonl"):
            p = date_dir / name
            if p.exists() and p.stat().st_size > 0:
                out.append(p)
    out.sort(key=lambda p: p.stat().st_mtime)
    return out


REGISTERED_SOURCES: List[Source] = [
    Source(name="theseus", scanner=scan_theseus_outbox),
    Source(name="aporia_staged", scanner=scan_aporia_staged),
]


def discover_candidates() -> List[tuple]:
    """Return list of (source_name, path) tuples across all sources."""
    out: List[tuple] = []
    for src in REGISTERED_SOURCES:
        for p in src.scanner():
            out.append((src.name, p))
    return out
