"""Penelope orchestration — agora heartbeat, log_work, lifetime stats.

Mirrors theseus/orchestration/ pattern. All telemetry calls are best-effort
and fail-soft: if Postgres/Redis is unreachable the loop continues normally.
"""
from ergon.penelope.orchestration.telemetry import (
    register_penelope,
    log_batch_work,
)
from ergon.penelope.orchestration.lifetime import (
    load_lifetime_stats,
    save_lifetime_stats,
    update_lifetime_after_batch,
)

__all__ = [
    "register_penelope",
    "log_batch_work",
    "load_lifetime_stats",
    "save_lifetime_stats",
    "update_lifetime_after_batch",
]
