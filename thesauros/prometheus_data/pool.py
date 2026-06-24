"""
Connection pool management for Prometheus databases.

Provides context-managed connections from thread-safe pools.
Pools are module-level singletons, created on first use, closed at exit.
"""
import atexit
import os
from contextlib import contextmanager
from .config import get_pg_dsn, get_redis_config

# ============================================================
# Postgres Pools
# ============================================================

_pools = {}


def _get_pool(db_name, minconn=1, maxconn=5):
    """Get or create a connection pool for a database."""
    if db_name not in _pools:
        import psycopg2.pool
        dsn = get_pg_dsn(db_name)
        try:
            _pools[db_name] = psycopg2.pool.ThreadedConnectionPool(
                minconn, maxconn, **dsn
            )
        except Exception as e:
            # Pool creation failed (database doesn't exist yet, network down, etc.)
            # Return None — callers should handle gracefully
            return None
    return _pools[db_name]


def _close_pools():
    """Close all connection pools. Called at process exit."""
    for name, pool in _pools.items():
        try:
            pool.closeall()
        except Exception:
            pass
    _pools.clear()


atexit.register(_close_pools)


@contextmanager
def _pg_connection(db_name, readonly=False):
    """Context manager that gets a connection from the pool and returns it after use."""
    pool = _get_pool(db_name)
    if pool is None:
        raise ConnectionError(
            f"Cannot connect to {db_name}. Check ~/.prometheus/db.toml and credentials.toml"
        )
    conn = pool.getconn()
    try:
        if readonly:
            conn.set_session(readonly=True, autocommit=True)
        yield conn
        if not readonly:
            conn.commit()
    except Exception:
        if not readonly:
            conn.rollback()
        raise
    finally:
        pool.putconn(conn)


# ============================================================
# Public API: Postgres
# ============================================================

def get_lmfdb():
    """Get a read-only connection to the LMFDB mirror.

    Usage:
        with get_lmfdb() as conn:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM ec_curvedata")
    """
    return _pg_connection("lmfdb", readonly=True)


def get_sci():
    """Get a read-only connection to PrometheusSci.

    Usage:
        with get_sci() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM topology.knots LIMIT 10")
    """
    return _pg_connection("sci", readonly=True)


def get_fire():
    """Get a read-write connection to PrometheusFire.

    Usage:
        with get_fire() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO results.ergon_runs ...")
    """
    return _pg_connection("fire", readonly=False)


# ============================================================
# Public API: Redis
# ============================================================

_redis_client = None


def get_redis():
    """Get a bus client (drop-in for the redis-py subset the substrate uses).

    Postgres-backed by default since 2026-06-24: real Redis under WSL kept needing
    manual restarts, so the bus now lives in prometheus_fire (schema `bus`) via
    PgRedis. Set env PROMETHEUS_USE_REDIS=1 to use a real Redis if one is running.
    Returns None only if even the Postgres bus is unreachable (graceful degradation;
    callers already guard `if r:`).

    Usage:
        r = get_redis()
        if r:
            cached = r.get("tensor:slice:ec:conductor")
    """
    global _redis_client
    if _redis_client is None:
        if os.environ.get("PROMETHEUS_USE_REDIS") == "1":
            try:
                import redis
                config = get_redis_config()
                _redis_client = redis.Redis(
                    **config,
                    decode_responses=False,  # we store raw bytes for tensors
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                _redis_client.ping()
                return _redis_client
            except Exception:
                _redis_client = None
        # Default: Postgres-backed bus.
        try:
            from .pg_redis import PgRedis
            client = PgRedis(decode_responses=False)
            client.ping()
            _redis_client = client
        except Exception:
            _redis_client = None
    return _redis_client


def get_bus(decode_responses=False):
    """Postgres-backed bus client (PgRedis), with the decode mode you ask for.

    Use this in code that previously made its OWN `redis.Redis(decode_responses=...)`
    connection instead of calling get_redis(). It is the migration target for those
    direct-connect callers (e.g. modules that treat stream fields as str).
    """
    from .pg_redis import PgRedis
    return PgRedis(decode_responses=decode_responses)


# ============================================================
# Public API: DuckDB (DEPRECATED — use Postgres instead)
# ============================================================

def get_duckdb(read_only=True):
    """DEPRECATED: DuckDB data has been migrated to Postgres.

    All charon.duckdb data is now in:
      - prometheus_fire.xref.object_registry (134K objects)
      - prometheus_fire.xref.bridges (17K bridges)
      - prometheus_fire.zeros.* (322K zeros)
      - prometheus_fire.analysis.disagreement_atlas (119K rows)
      - Redis: graph:neighbors:*, landscape:*, bridge:*, hypothesis:queue

    Use get_fire() or get_lmfdb() instead. This function still works
    but will be removed in a future cleanup.
    """
    import warnings
    warnings.warn(
        "get_duckdb() is deprecated. DuckDB data has been migrated to Postgres "
        "(prometheus_fire) and Redis. Use get_fire() or get_lmfdb() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    import duckdb
    from .config import get_config
    config = get_config("local")
    return duckdb.connect(config["duckdb_path"], read_only=read_only)
