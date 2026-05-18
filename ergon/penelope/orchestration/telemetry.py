"""Telemetry wiring for Penelope → M4 orchestration layer.

Calls into scripts/session_telemetry.py (agora.agent_heartbeats +
agora.intelligence_outputs). All calls fail-soft: if Postgres/Redis is
unreachable, the loop continues normally.

Adapted from theseus/orchestration/telemetry.py.
"""
from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ergon.penelope.config import PENELOPE_AGENT_NAME, REPO_ROOT
from ergon.penelope.orchestration.lifetime import load_lifetime_stats

_SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    import session_telemetry  # type: ignore
    HAS_TELEMETRY = True
except Exception:
    session_telemetry = None  # type: ignore
    HAS_TELEMETRY = False


PENELOPE_OPERATOR = os.environ.get("PENELOPE_OPERATOR", "Ergon")
PENELOPE_MACHINE = os.environ.get("PENELOPE_MACHINE", "M2")


def _build_status_json(
    sources_scanned: Optional[List[str]] = None,
    triggered_by: str = "schedule",
    last_cycle_id: Optional[str] = None,
    next_cycle_at: Optional[str] = None,
    errors_this_cycle: Optional[List[str]] = None,
) -> Dict[str, Any]:
    stats = load_lifetime_stats()
    return {
        "operator": PENELOPE_OPERATOR,
        "tool_kind": "substrate_ingest_loop",
        "sources_scanned": list(sources_scanned or []),
        "lifetime_files_ingested": stats["lifetime_files_ingested"],
        "lifetime_records_ingested": stats["lifetime_records_ingested"],
        "lifetime_batches": stats["batches_completed"],
        "lifetime_validation_failures": stats["lifetime_validation_failures"],
        "per_source_lifetime": stats.get("per_source_lifetime", {}),
        "per_domain_lifetime": stats.get("per_domain_lifetime", {}),
        "errors_this_cycle": errors_this_cycle or [],
        "last_cycle_id": last_cycle_id,
        "next_cycle_at": next_cycle_at,
        "triggered_by": triggered_by,
        "first_seen_at": stats["first_seen_at"],
    }


def register_penelope(
    sources_scanned: Optional[List[str]] = None,
    triggered_by: str = "schedule",
    last_cycle_id: Optional[str] = None,
    next_cycle_at: Optional[str] = None,
    errors_this_cycle: Optional[List[str]] = None,
) -> bool:
    """Declare Penelope's identity + refresh status_json on the heartbeat.

    Call at daemon startup AND after each batch.
    """
    if not HAS_TELEMETRY:
        return False
    try:
        return bool(session_telemetry.register_session(
            agent_name=PENELOPE_AGENT_NAME,
            machine=PENELOPE_MACHINE,
            role=(
                "substrate ingest loop (Ergon's Learner-corpus consumer): "
                "scans Theseus handoffs + Aporia hand-staged blocks + mining-pipeline "
                "outputs, ingests via ingest_training_anchors.py, tracks processed "
                "files in an idempotent ledger, emits per-batch telemetry"
            ),
            kind="tool",
            status="online",
            status_json=_build_status_json(
                sources_scanned=sources_scanned,
                triggered_by=triggered_by,
                last_cycle_id=last_cycle_id,
                next_cycle_at=next_cycle_at,
                errors_this_cycle=errors_this_cycle,
            ),
            tools_operated=None,
        ))
    except Exception as e:
        print(f"[penelope.orchestration] register_penelope failed (non-fatal): {e}",
              file=sys.stderr)
        return False


def log_batch_work(
    batch_id: str,
    batch_summary: Dict[str, Any],
    started_at: Optional[datetime] = None,
) -> bool:
    """Log one Penelope batch to agora.intelligence_outputs."""
    if not HAS_TELEMETRY:
        return False
    try:
        files_in = batch_summary.get("files_ingested", 0)
        files_dup = batch_summary.get("files_skipped_duplicate", 0)
        files_fail = batch_summary.get("files_failed", 0)
        records = batch_summary.get("records_ingested", 0)
        drops = batch_summary.get("records_dropped", 0)
        vfails = batch_summary.get("validation_failures", 0)
        sources = ",".join(sorted(batch_summary.get("per_source", {}).keys())) or "none"
        domains = ",".join(sorted(batch_summary.get("per_domain", {}).keys())) or "none"
        summary = (
            f"[{batch_id}] files: {files_in} ingested, {files_dup} dup-skip, "
            f"{files_fail} failed. records: {records} ingested, {drops} dropped, "
            f"{vfails} validation_failures. sources: {sources}. domains: {domains}."
        )
        cycle_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, batch_id))
        return bool(session_telemetry.log_work(
            stage="penelope_batch_complete",
            summary=summary,
            agent=PENELOPE_AGENT_NAME,
            success=(files_fail == 0 and vfails == 0),
            cycle_id=cycle_uuid,
            started_at=started_at,
        ))
    except Exception as e:
        print(f"[penelope.orchestration] log_batch_work failed (non-fatal): {e}",
              file=sys.stderr)
        return False
