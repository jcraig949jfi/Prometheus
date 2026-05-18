"""Telemetry wiring for Theseus → M4 orchestration layer.

Calls into scripts/session_telemetry.py. All calls are best-effort and
fail-soft: if Postgres/Redis is unreachable, the engine continues normally.
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from theseus.emit.record_schema import TheseusRecord, Verdict
from theseus.orchestration.lifetime import (
    load_lifetime_stats,
    update_lifetime_after_batch,
    dedup_rate,
)
from theseus.scoring.training_weight import training_weight


# Add scripts/ to sys.path so session_telemetry imports work.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    import session_telemetry  # type: ignore
    HAS_TELEMETRY = True
except Exception:
    session_telemetry = None  # type: ignore
    HAS_TELEMETRY = False


DEFAULT_DISCOVERY_WEIGHT_THRESHOLD = 0.6  # high-value records to surface
THESEUS_AGENT_NAME = "Theseus"
THESEUS_OPERATOR = os.environ.get("THESEUS_OPERATOR", "James")
THESEUS_MACHINE = os.environ.get("THESEUS_MACHINE", "M1")


def _build_status_json(
    target_generators: Optional[List[str]] = None,
    triggered_by: str = "schedule",
    last_cycle_id: Optional[str] = None,
    next_cycle_at: Optional[str] = None,
    last_dedup_rate: Optional[float] = None,
    errors_this_cycle: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build the status_json blob the M4 dashboard reads."""
    stats = load_lifetime_stats()
    return {
        "operator": THESEUS_OPERATOR,
        "tool_kind": "substrate_generation_engine",
        "target_generators": list(target_generators or []),
        "sources": ["knots_local", "bsd_rich_local", "oeis_sleeping_local"],
        "lifetime_records": stats["lifetime_records"],
        "lifetime_batches": stats["batches_completed"],
        "lifetime_discoveries_emitted": stats["lifetime_discoveries_emitted"],
        "dedup_rate": last_dedup_rate,
        "errors_this_cycle": errors_this_cycle or [],
        "last_cycle_id": last_cycle_id,
        "next_cycle_at": next_cycle_at,
        "triggered_by": triggered_by,
        "first_seen_at": stats["first_seen_at"],
    }


def register_theseus(
    target_generators: Optional[List[str]] = None,
    triggered_by: str = "schedule",
    last_cycle_id: Optional[str] = None,
    next_cycle_at: Optional[str] = None,
    last_dedup_rate: Optional[float] = None,
    errors_this_cycle: Optional[List[str]] = None,
) -> bool:
    """Declare Theseus's identity to the orchestration layer.

    Should be called at daemon startup AND after each batch (to refresh
    status_json with the latest stats).
    """
    if not HAS_TELEMETRY:
        return False
    try:
        return bool(session_telemetry.register_session(
            agent_name=THESEUS_AGENT_NAME,
            machine=THESEUS_MACHINE,
            role=(
                "substrate generation engine (catalog-cross-product, mutation, "
                "triangulation, self-play, symbolic regression) with bayesian "
                "hyperparameter tuning + per-record training-value annotation"
            ),
            kind="tool",
            status="online",
            status_json=_build_status_json(
                target_generators=target_generators,
                triggered_by=triggered_by,
                last_cycle_id=last_cycle_id,
                next_cycle_at=next_cycle_at,
                last_dedup_rate=last_dedup_rate,
                errors_this_cycle=errors_this_cycle,
            ),
            tools_operated=None,  # Theseus is itself a tool
        ))
    except Exception as e:
        print(f"[theseus.orchestration] register_theseus failed (non-fatal): {e}",
              file=sys.stderr)
        return False


def log_batch_work(
    batch_metrics,
    requested_generators: List[str],
    n_discoveries_emitted: int = 0,
    started_at: Optional[datetime] = None,
) -> bool:
    """Log one batch's work event to agora.intelligence_outputs.

    Wraps session_telemetry.log_work. Includes summary stats matching
    the format Aporia/Clio uses for the dashboard.
    """
    if not HAS_TELEMETRY:
        return False
    try:
        active = list(batch_metrics.per_generator.keys())
        summary = (
            f"{batch_metrics.total_records} records "
            f"({batch_metrics.total_kills} kills, "
            f"{batch_metrics.total_confirmations} confirms, "
            f"{batch_metrics.total_inconclusive} inconclusive, "
            f"{batch_metrics.total_errors} errors), "
            f"{batch_metrics.duration_hours * 3600:.0f}s duration. "
            f"Active generators: {','.join(active)}. "
            f"Discoveries emitted: {n_discoveries_emitted}."
        )
        # agora.intelligence_outputs requires UUID cycle_id; Theseus's
        # batch_id is a free-form string. Derive deterministic UUIDv5 so
        # the cycle is stable while satisfying the schema.
        cycle_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, batch_metrics.batch_id))
        summary = f"[{batch_metrics.batch_id}] {summary}"
        return bool(session_telemetry.log_work(
            stage="theseus_batch_complete",
            summary=summary,
            agent=THESEUS_AGENT_NAME,
            success=(batch_metrics.total_errors == 0),
            cycle_id=cycle_uuid,
            started_at=started_at,
        ))
    except Exception as e:
        print(f"[theseus.orchestration] log_batch_work failed (non-fatal): {e}",
              file=sys.stderr)
        return False


def maybe_emit_discoveries(
    records: List[TheseusRecord],
    weight_threshold: float = DEFAULT_DISCOVERY_WEIGHT_THRESHOLD,
    max_per_batch: int = 20,
) -> int:
    """For each record with training_weight ≥ threshold, push a discovery
    event to agora:discoveries. Returns count of records actually emitted.

    Caps at max_per_batch to avoid swamping the stream when a batch has
    thousands of high-weight records.
    """
    if not HAS_TELEMETRY:
        return 0
    n_emitted = 0
    # Score + sort by weight descending; take top-K above threshold
    weighted: List = []
    for r in records:
        try:
            w = training_weight(r)
        except Exception:
            continue
        if w >= weight_threshold:
            weighted.append((w, r))
    weighted.sort(key=lambda x: -x[0])
    for w, r in weighted[:max_per_batch]:
        try:
            session_telemetry.emit_discovery(
                sender=THESEUS_AGENT_NAME,
                machine=THESEUS_MACHINE,
                type_="share",
                subject=f"High-value substrate record ({w:.3f}): {r.generator_id} {r.verdict}",
                body=r.canonical_claim_text[:1500],
                confidence=w,
                extras={
                    "record_id": r.record_id,
                    "batch_id": r.batch_id,
                    "generator_id": r.generator_id,
                    "claim_kind": r.claim_kind,
                    "verdict": r.verdict,
                    "kill_pattern": r.kill_pattern,
                    "training_weight": round(w, 4),
                },
            )
            n_emitted += 1
        except Exception as e:
            print(f"[theseus.orchestration] emit_discovery failed (non-fatal): {e}",
                  file=sys.stderr)
            continue
    return n_emitted
