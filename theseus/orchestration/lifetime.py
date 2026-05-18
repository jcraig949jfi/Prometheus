"""Lifetime stats — cumulative counters across batches.

Persisted to `theseus/orchestration/lifetime_stats.json`. The orchestration
layer reads these for the dashboard status (lifetime_records,
dedup_rate, etc.). The status_json field demanded by the M4 brief.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from theseus.config import THESEUS_ROOT


LIFETIME_PATH = THESEUS_ROOT / "orchestration" / "lifetime_stats.json"


def _empty_stats() -> Dict[str, Any]:
    return {
        "first_seen_at": None,
        "last_updated_at": None,
        "batches_completed": 0,
        "lifetime_records": 0,
        "lifetime_kills": 0,
        "lifetime_confirmations": 0,
        "lifetime_inconclusive": 0,
        "lifetime_errors": 0,
        "lifetime_duplicates_skipped": 0,
        "lifetime_discoveries_emitted": 0,
        # Per-generator lifetime emit counts
        "per_generator_lifetime": {},
    }


def load_lifetime_stats() -> Dict[str, Any]:
    if not LIFETIME_PATH.exists():
        return _empty_stats()
    try:
        with LIFETIME_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            base = _empty_stats()
            base.update(data)
            return base
    except (OSError, json.JSONDecodeError):
        pass
    return _empty_stats()


def save_lifetime_stats(stats: Dict[str, Any]) -> None:
    LIFETIME_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = LIFETIME_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, sort_keys=True)
    tmp.replace(LIFETIME_PATH)


def update_lifetime_after_batch(
    batch_metrics, n_discoveries_emitted: int = 0
) -> Dict[str, Any]:
    """Merge a completed BatchMetrics into the lifetime stats and persist."""
    stats = load_lifetime_stats()
    now = datetime.now(timezone.utc).isoformat()
    if stats["first_seen_at"] is None:
        stats["first_seen_at"] = now
    stats["last_updated_at"] = now
    stats["batches_completed"] += 1
    stats["lifetime_records"] += batch_metrics.total_records
    stats["lifetime_kills"] += batch_metrics.total_kills
    stats["lifetime_confirmations"] += batch_metrics.total_confirmations
    stats["lifetime_inconclusive"] += batch_metrics.total_inconclusive
    stats["lifetime_errors"] += batch_metrics.total_errors
    stats["lifetime_discoveries_emitted"] += int(n_discoveries_emitted)

    pg = stats.setdefault("per_generator_lifetime", {})
    for gid, m in batch_metrics.per_generator.items():
        pg[gid] = pg.get(gid, 0) + m.records_emitted

    save_lifetime_stats(stats)
    return stats


def dedup_rate(batch_metrics) -> float:
    """records_new / records_emitted across this batch (1.0 = all unique)."""
    total = batch_metrics.total_records
    if total <= 0:
        return 1.0
    # We don't track duplicates_skipped at BatchMetrics level today; use
    # 1.0 as a placeholder. Tier-2 refactor surfaces dedup count to here.
    return 1.0
