"""Read/write per-generator hyperparameter overrides.

Generators check this on __init__ and apply any tuned values; absent
the overrides file, generators use their hardcoded defaults. Overrides
file is JSON: `{ "a4": { "sample_size": 50, "STRONG_R2": 0.8 }, ... }`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from theseus.config import THESEUS_ROOT


OVERRIDES_PATH = THESEUS_ROOT / "optimization" / "tuned_hyperparams.json"


def load_overrides() -> Dict[str, Dict[str, Any]]:
    """Read the overrides file; returns {} if missing or malformed."""
    if not OVERRIDES_PATH.exists():
        return {}
    try:
        with OVERRIDES_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_overrides(overrides: Dict[str, Dict[str, Any]]) -> None:
    """Persist the overrides file atomically."""
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = OVERRIDES_PATH.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(overrides, f, indent=2, sort_keys=True)
    tmp_path.replace(OVERRIDES_PATH)


def get_overrides_for(generator_id: str) -> Dict[str, Any]:
    """Convenience: fetch overrides for one generator."""
    return load_overrides().get(generator_id, {})


def update_overrides_for(generator_id: str, params: Dict[str, Any]) -> None:
    """Merge new params into the existing overrides file."""
    current = load_overrides()
    current[generator_id] = dict(params)
    save_overrides(current)
