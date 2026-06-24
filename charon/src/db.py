"""Charon DB access layer — Postgres (prometheus_fire.charon_duckdb).

DuckDB is retired. All 14 `charon.duckdb` `main.*` tables were migrated VERBATIM
(row-for-row, identical column names/types) into the `charon_duckdb` schema of the
local `prometheus_fire` Postgres 17 database (Ergon, 2026-06-24; see
`roles/Ergon/DUCKDB_RETIREMENT_AUDIT_2026-06-24.md`). `charon/data/charon.duckdb`
remains on disk, frozen, as the verification oracle + fallback (no-delete doctrine).

This module is a thin **DuckDB-compatible facade over psycopg2** so the existing
call sites — `con.execute(sql, params).fetchall()` with `?` placeholders and
unqualified table names — keep working with a one-line import swap:

    import duckdb                       ->  from charon.src import db as duckdb
    duckdb.connect(str(DB_PATH), read_only=True)   # now returns a CharonConnection

`connect()` accepts (and ignores) the legacy DuckDB path argument, connects to
Postgres, and sets `search_path = charon_duckdb, public` so unqualified table names
(`FROM objects`) resolve to the migrated archive.

Credentials: reads use the read-only role `lmfdb` (same non-secret cred already in
`thesauros/prometheus_data/config.py`). The default connection target is *localhost*
(the migrated data is local; the prometheus_data config default still points at the
remote `devmirror` mirror, so we connect directly here). All of host/port/db/user/
password are overridable via CHARON_PG_* env vars. The sensitive postgres/prometheus
write cred is NOT used or hardcoded here — this layer is read-only by design.

SQL dialect note: DuckDB `?` placeholders are translated to psycopg2 `%s` (with
literal `%` escaped) only when params are supplied. The migrated tables use only
standard types (`double precision[]` arrays come back as Python lists, as in DuckDB).
The DuckDB-only DDL constructs (`DOUBLE[]` column declarations, etc.) lived only in
the retired ingest/schema writers, which are not routed through this layer.
"""
from __future__ import annotations

import os

# Connection target. Localhost is authoritative (data was migrated locally);
# overridable for other hosts via environment.
PG_CONFIG = {
    "host": os.environ.get("CHARON_PG_HOST", "localhost"),
    "port": int(os.environ.get("CHARON_PG_PORT", "5432")),
    "dbname": os.environ.get("CHARON_PG_DB", "prometheus_fire"),
    "user": os.environ.get("CHARON_PG_USER", "lmfdb"),
    "password": os.environ.get("CHARON_PG_PASSWORD", "lmfdb"),
}
SCHEMA = os.environ.get("CHARON_PG_SCHEMA", "charon_duckdb")


def _translate(sql: str, has_params: bool) -> str:
    """Translate DuckDB `?` placeholders to psycopg2 `%s`.

    Only runs when params are supplied; psycopg2 does not interpret `%` when
    execute() is called without a params argument, so a paramless query is left
    verbatim. When params ARE present, literal `%` must be escaped to `%%` first,
    then `?` becomes `%s`.
    """
    if not has_params:
        return sql
    return sql.replace("%", "%%").replace("?", "%s")


class _Result:
    """Wraps a psycopg2 cursor to expose DuckDB's fetch* API."""

    __slots__ = ("_cur",)

    def __init__(self, cur):
        self._cur = cur

    def fetchall(self):
        return self._cur.fetchall()

    def fetchone(self):
        return self._cur.fetchone()

    def fetchmany(self, size=None):
        if size is None:
            return self._cur.fetchmany()
        return self._cur.fetchmany(size)

    @property
    def description(self):
        return self._cur.description

    @property
    def rowcount(self):
        return self._cur.rowcount


class CharonConnection:
    """DuckDB-compatible facade over a psycopg2 connection (read-only by default)."""

    def __init__(self, conn, read_only: bool = True):
        self._conn = conn
        self.read_only = read_only

    def execute(self, sql: str, params=None) -> _Result:
        cur = self._conn.cursor()
        if params is not None:
            cur.execute(_translate(sql, True), list(params))
        else:
            cur.execute(sql)
        return _Result(cur)

    def executemany(self, sql: str, seq_of_params) -> _Result:
        cur = self._conn.cursor()
        cur.executemany(_translate(sql, True), [list(p) for p in seq_of_params])
        return _Result(cur)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    @property
    def raw(self):
        """Escape hatch: the underlying psycopg2 connection."""
        return self._conn

    # Context-manager parity with duckdb connections.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def connect(database=None, read_only: bool = True, **overrides) -> CharonConnection:
    """Return a DuckDB-compatible connection to Postgres `charon_duckdb`.

    `database` is the legacy DuckDB path — accepted for call-site compatibility and
    ignored. `read_only` controls the session mode. Any of host/port/dbname/user/
    password may be overridden via kwargs.
    """
    import psycopg2

    cfg = dict(PG_CONFIG)
    for k in ("host", "port", "dbname", "user", "password"):
        if k in overrides:
            cfg[k] = overrides[k]

    conn = psycopg2.connect(**cfg)
    conn.autocommit = True  # read workloads; no transaction churn
    cur = conn.cursor()
    cur.execute(f"SET search_path TO {SCHEMA}, public")
    if read_only:
        cur.execute("SET default_transaction_read_only = on")
    cur.close()
    return CharonConnection(conn, read_only=read_only)


def get_connection(read_only: bool = True) -> CharonConnection:
    """Preferred explicit entry point for new code."""
    return connect(read_only=read_only)
