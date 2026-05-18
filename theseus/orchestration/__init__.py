"""Theseus orchestration — wires the engine into the M4 orchestration layer.

Uses scripts/session_telemetry.py:
  - register_session: declare Theseus as a TOOL with operator=James
  - log_work:         per-batch work events to agora.intelligence_outputs
  - emit_discovery:   push high-training-weight records to agora:discoveries

Best-effort + fail-soft. If session_telemetry / Postgres / Redis is
unreachable, the engine continues normally; orchestration calls return
False / None silently.
"""
from theseus.orchestration.telemetry import (
    register_theseus,
    log_batch_work,
    maybe_emit_discoveries,
    DEFAULT_DISCOVERY_WEIGHT_THRESHOLD,
)
from theseus.orchestration.lifetime import (
    load_lifetime_stats,
    save_lifetime_stats,
    update_lifetime_after_batch,
)

__all__ = [
    "register_theseus",
    "log_batch_work",
    "maybe_emit_discoveries",
    "DEFAULT_DISCOVERY_WEIGHT_THRESHOLD",
    "load_lifetime_stats",
    "save_lifetime_stats",
    "update_lifetime_after_batch",
]
