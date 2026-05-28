"""Erebos per-plugin structured logging.

Per pivot/erebos_design_philosophy_dna_2026-05-26.md P4 (structured
detailed logging): every plugin tick emits a structured JSONL row
to charon/agents/erebos/logs/g<NN>_<name>_<YYYY-MM-DD>.jsonl with
the fields defined in GeneratorTickLog.

These logs are the substrate for the continuous-review cycle (P5)
and the per-plugin telemetry that surfaces in daily stats.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from harmonia.agents._base import REPO_ROOT

EREBOS_LOGS_DIR = REPO_ROOT / "charon" / "agents" / "erebos" / "logs"


@dataclass
class GeneratorTickLog:
    """One row per plugin tick. Persists to per-plugin per-day JSONL."""
    ts: str
    plugin_id: str
    tick_id: str
    applicable: bool
    inputs_summary: dict = field(default_factory=dict)
    generated: bool = False
    composed_id: Optional[str] = None
    parent_record_ids: list = field(default_factory=list)
    transformation_path: Optional[str] = None
    expected_kill_pattern: Optional[str] = None
    falsification_route_hash: Optional[str] = None
    error: Optional[str] = None
    elapsed_ms: float = 0.0
    plugin_extras: dict = field(default_factory=dict)

    # Phase 1B ITER-37: cost-instrumentation daemon wire. Populated by
    # _cost_instrumentation.time_plugin_generate(); cross-references
    # claim.generation_cost_seconds (same value).
    generation_cost_seconds: float = 0.0


def hash_falsification_route(text: str) -> str:
    """sha256(text)[:16] for change-detection across plugin versions."""
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _log_path_for(plugin_id: str) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return EREBOS_LOGS_DIR / f"{plugin_id}_{today}.jsonl"


def emit_tick_log(row: GeneratorTickLog) -> Path:
    """Append the tick log to charon/agents/erebos/logs/<plugin>_<date>.jsonl.

    Auto-creates the logs dir. Silent on disk errors so logging
    can't crash a tick."""
    try:
        p = _log_path_for(row.plugin_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(row), ensure_ascii=False, default=str) + "\n")
        return p
    except Exception:
        return _log_path_for(row.plugin_id)


def read_plugin_log_since(plugin_id: str, days_back: int = 7) -> list[dict]:
    """Read recent tick log rows for a plugin across the last N daily
    files. Used by the per-plugin review cycle (P5)."""
    from datetime import timedelta
    rows: list[dict] = []
    today = datetime.now(timezone.utc).date()
    for offset in range(days_back + 1):
        date = today - timedelta(days=offset)
        p = EREBOS_LOGS_DIR / f"{plugin_id}_{date.isoformat()}.jsonl"
        if not p.exists():
            continue
        try:
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue
    return rows
