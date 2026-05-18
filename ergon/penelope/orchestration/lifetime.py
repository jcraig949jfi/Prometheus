"""Lifetime stats — cumulative counters across Penelope batches.

Persisted to `ergon/penelope/orchestration/lifetime_stats.json`. The
orchestration layer reads these for the agora dashboard status_json.
Adapted from theseus/orchestration/lifetime.py.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from ergon.penelope.config import PENELOPE_ROOT

LIFETIME_PATH = PENELOPE_ROOT / "orchestration" / "lifetime_stats.json"


def _empty_stats() -> Dict[str, Any]:
    return {
        "first_seen_at": None,
        "last_updated_at": None,
        "batches_completed": 0,
        "lifetime_files_ingested": 0,
        "lifetime_files_skipped_duplicate": 0,
        "lifetime_files_failed": 0,
        "lifetime_records_ingested": 0,
        "lifetime_records_dropped": 0,
        "lifetime_validation_failures": 0,
        "per_source_lifetime": {},
        "per_domain_lifetime": {},
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


def update_lifetime_after_batch(batch_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a completed batch summary into lifetime stats and persist.

    batch_summary fields consumed:
      files_ingested, files_skipped_duplicate, files_failed,
      records_ingested, records_dropped, validation_failures,
      per_source (dict), per_domain (dict).
    """
    stats = load_lifetime_stats()
    now = datetime.now(timezone.utc).isoformat()
    if stats["first_seen_at"] is None:
        stats["first_seen_at"] = now
    stats["last_updated_at"] = now
    stats["batches_completed"] += 1
    stats["lifetime_files_ingested"] += batch_summary.get("files_ingested", 0)
    stats["lifetime_files_skipped_duplicate"] += batch_summary.get("files_skipped_duplicate", 0)
    stats["lifetime_files_failed"] += batch_summary.get("files_failed", 0)
    stats["lifetime_records_ingested"] += batch_summary.get("records_ingested", 0)
    stats["lifetime_records_dropped"] += batch_summary.get("records_dropped", 0)
    stats["lifetime_validation_failures"] += batch_summary.get("validation_failures", 0)

    ps = stats.setdefault("per_source_lifetime", {})
    for src, n in batch_summary.get("per_source", {}).items():
        ps[src] = ps.get(src, 0) + int(n)

    pd = stats.setdefault("per_domain_lifetime", {})
    for dom, n in batch_summary.get("per_domain", {}).items():
        pd[dom] = pd.get(dom, 0) + int(n)

    save_lifetime_stats(stats)
    return stats
