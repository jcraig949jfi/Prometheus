"""
prometheus_data — Unified data access layer for Project Prometheus.

Provides connection management, caching, and domain loaders for all
Prometheus agents (Harmonia, Ergon, Charon). Single source of truth
for database configuration across both machines.

Three tiers:
    Postgres = truth    (queryable, joinable, indexed, durable)
    Redis    = speed    (cached state, coordination, hot lookups)
    Files    = archive  (static reference, model weights, backups)

Usage:
    from prometheus_data import get_lmfdb, get_sci, get_fire, get_redis

    # Postgres connections (context managers, pooled)
    with get_lmfdb() as conn:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM ec_curvedata")
        cur.execute("SELECT * FROM bsd_joined WHERE rank >= 2 LIMIT 10")

    with get_fire() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM zeros.object_zeros LIMIT 10")
        cur.execute("SELECT * FROM xref.object_registry LIMIT 10")

    # Redis
    r = get_redis()
    r.smembers("graph:neighbors:42")
    r.zrevrange("landscape:by_curvature", 0, 50)
"""

from prometheus_data.pool import get_lmfdb, get_sci, get_fire, get_redis, get_duckdb

__all__ = ["get_lmfdb", "get_sci", "get_fire", "get_redis", "get_duckdb"]
