"""
prometheus_data — Unified data access layer for Project Prometheus.

Provides connection management, caching, and domain loaders for all
Prometheus agents (Harmonia, Ergon, Charon). Single source of truth
for database configuration across both machines.

Usage:
    from prometheus_data import get_lmfdb, get_sci, get_fire, get_redis

    # Postgres connections (context managers, pooled)
    with get_lmfdb() as conn:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM ec_curvedata")

    with get_fire() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO results.ergon_runs ...")

    # Redis
    r = get_redis()
    r.get("tensor:slice:elliptic_curves:conductor")
"""

from prometheus_data.pool import get_lmfdb, get_sci, get_fire, get_redis, get_duckdb

__all__ = ["get_lmfdb", "get_sci", "get_fire", "get_redis", "get_duckdb"]
