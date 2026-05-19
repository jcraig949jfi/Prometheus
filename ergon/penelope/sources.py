"""Upstream-source scanners for Penelope.

Each `Source` declares:
  * a `name` (logged in ledger + telemetry)
  * a `scanner` that returns candidate input paths
  * a `runner_type` (decides which downstream script the daemon dispatches to:
      - "training_anchor" → ergon/learner/scripts/ingest_training_anchors.py
      - "claim_batch"     → prometheus_math.substrate_generation.tier_1_claim_runner

The dispatcher in daemon.py reads `runner_type` and invokes the matching
script with appropriate flags. Output paths land under
`corpus/v1_0_tier_pending/by_file/<source>/<discriminator>/<batch_date>/`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Tuple

from ergon.penelope.config import (
    APORIA_STAGED_ROOT,
    TECHNE_MINED_ROOT,
    THESEUS_OUTBOX,
)


@dataclass(frozen=True)
class Source:
    name: str
    scanner: Callable[[], List[Path]]
    runner_type: str  # "training_anchor" | "claim_batch"


def scan_theseus_outbox() -> List[Path]:
    """Theseus handoff bundles: theseus/handoff/ergon_outbox/*.jsonl.

    Excludes _combined_*.jsonl intermediates (Theseus-internal
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
    """Aporia hand-staged blocks: aporia/docs/staged_substrate_blocks/<date>/*.jsonl.

    Picks training_anchor / validated / validated_reauthored files. The
    ingester filters non-training_anchor block_types internally.
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


def scan_techne_mined() -> List[Path]:
    """Techne mining-pipeline output: aporia/docs/mined_substrate_blocks/<date>/<extractor>/{boundary,frontier_survey,substrate_self}.jsonl.

    These are CLAIM-shaped records, not training_anchor blocks — dispatched
    to tier_1_claim_runner.py. The runner emits LearnerRecord output.
    Skips empty files and the per-extractor `_summary.json` sidecars.
    """
    if not TECHNE_MINED_ROOT.exists():
        return []
    out: List[Path] = []
    for date_dir in sorted(TECHNE_MINED_ROOT.iterdir()):
        if not date_dir.is_dir():
            continue
        for extractor_dir in sorted(date_dir.iterdir()):
            if not extractor_dir.is_dir():
                continue
            for category in ("boundary", "frontier_survey", "substrate_self"):
                p = extractor_dir / f"{category}.jsonl"
                if p.exists() and p.stat().st_size > 0:
                    out.append(p)
    out.sort(key=lambda p: p.stat().st_mtime)
    return out


REGISTERED_SOURCES: List[Source] = [
    Source(name="theseus", scanner=scan_theseus_outbox, runner_type="training_anchor"),
    Source(name="aporia_staged", scanner=scan_aporia_staged, runner_type="training_anchor"),
    Source(name="techne_mined", scanner=scan_techne_mined, runner_type="claim_batch"),
]


def discover_candidates() -> List[Tuple[str, Path, str]]:
    """Return list of (source_name, path, runner_type) tuples across all sources."""
    out: List[Tuple[str, Path, str]] = []
    for src in REGISTERED_SOURCES:
        for p in src.scanner():
            out.append((src.name, p, src.runner_type))
    return out
