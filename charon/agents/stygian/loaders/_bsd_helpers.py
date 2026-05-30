"""Shared helpers for BSD-domain composition loaders.

Loads the existing 1000-entry rich BSD database at
prometheus_math/databases/bsd_rich.json.gz. Each entry has:
  - base: {label, cremona_label, ainvs, conductor, a_p, rank}
  - rich: {regulator, real_period, L1, ...}
"""
from __future__ import annotations

import gzip
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional


BSD_DB_PATH = Path("prometheus_math/databases/bsd_rich.json.gz")
MIN_BSD_SAMPLE_SIZE = 50


@lru_cache(maxsize=1)
def load_bsd_entries() -> list[dict]:
    """Load all entries from bsd_rich.json.gz. Cached.

    Each entry has 'base' (label, ainvs, conductor, a_p, rank) and
    'rich' (regulator, real_period, L1, ...). Returns the list of
    'entries' from the top-level dict, or [] on load failure.
    """
    if not BSD_DB_PATH.exists():
        return []
    try:
        with gzip.open(BSD_DB_PATH) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    return data.get("entries", [])


def get_rank(entry: dict) -> Optional[int]:
    """Extract rank (Mordell-Weil rank) from a BSD entry."""
    base = entry.get("base") or {}
    return base.get("rank")


def get_regulator(entry: dict) -> Optional[float]:
    """Extract regulator from a BSD entry's rich payload."""
    rich = entry.get("rich") or {}
    r = rich.get("regulator")
    if r is None:
        return None
    try:
        return float(r)
    except (TypeError, ValueError):
        return None


def get_conductor(entry: dict) -> Optional[int]:
    """Extract conductor from a BSD entry."""
    base = entry.get("base") or {}
    c = base.get("conductor")
    if c is None:
        return None
    try:
        return int(c)
    except (TypeError, ValueError):
        return None


def get_label(entry: dict) -> Optional[str]:
    base = entry.get("base") or {}
    return base.get("label") or base.get("cremona_label")
