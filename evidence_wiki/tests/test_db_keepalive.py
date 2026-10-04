"""Every ew.db connection carries TCP keepalive + tcp_user_timeout (Aporia
#1148; the half-open hang of Odysseus #1115 / DEF-ODY-019).

    offline    the pool AND the direct fallback pass KEEPALIVE_KWARGS to
               libpq (constructors captured, no database needed)
    libpq      the local libpq accepts every option (a bad option is a
               ProgrammingError at parse time; an unreachable port is not)
    live       a real pooled connection reports the options in its DSN
               parameters (skipped when the database is unreachable)
"""
import sys
from pathlib import Path

import psycopg2
import psycopg2.pool
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ew import db as ewdb  # noqa: E402

WANT = {"keepalives": 1, "keepalives_idle": 30, "keepalives_interval": 10,
        "keepalives_count": 3, "tcp_user_timeout": 60000}
_CFG = {"db_host": "h", "db_name": "d", "db_user": "u", "db_password": "p"}


class _Stop(Exception):
    pass


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(ewdb, "_POOL", None)
    monkeypatch.setattr(ewdb, "load_config", lambda: dict(_CFG))
    monkeypatch.setattr(ewdb, "_require_environment", lambda conn: None)
    seen = {}
    yield seen, monkeypatch
    ewdb._POOL = None


def _has_keepalives(kw):
    for k, v in WANT.items():
        assert kw.get(k) == v, (k, kw.get(k))


def test_pool_passes_keepalives(offline):
    seen, mp = offline

    def fake_pool(minconn, maxconn, **kw):
        seen.update(kw)
        raise _Stop

    mp.setattr(psycopg2.pool, "ThreadedConnectionPool", fake_pool)
    with pytest.raises(_Stop):
        ewdb._get_pool()
    _has_keepalives(seen)
    assert seen["host"] == "h" and seen["dbname"] == "d"


def test_direct_fallback_passes_keepalives(offline):
    seen, mp = offline

    def broken_pool(*a, **kw):
        raise RuntimeError("pool broken")

    def fake_connect(**kw):
        seen.update(kw)
        return object()

    mp.setattr(psycopg2.pool, "ThreadedConnectionPool", broken_pool)
    mp.setattr(ewdb.psycopg2, "connect", fake_connect)
    ewdb.connect()
    _has_keepalives(seen)


def test_local_libpq_accepts_options():
    with pytest.raises(psycopg2.ProgrammingError):  # control: parse-time reject
        psycopg2.connect(host="127.0.0.1", port=1, dbname="x", user="x", bogus_opt=1)
    with pytest.raises(psycopg2.OperationalError):  # parsed, then refused/timed out
        psycopg2.connect(host="127.0.0.1", port=1, dbname="x", user="x",
                         connect_timeout=2, **ewdb.KEEPALIVE_KWARGS)


def _reachable():
    try:
        c = ewdb.load_config()
        psycopg2.connect(host=c["db_host"], dbname=c["db_name"], user=c["db_user"],
                         password=c["db_password"], connect_timeout=3).close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _reachable(), reason="no database")
def test_live_pooled_connection_negotiates_keepalives(monkeypatch):
    monkeypatch.setattr(ewdb, "_POOL", None)
    monkeypatch.delenv("PROMETHEUS_ENV", raising=False)
    conn = ewdb.connect()
    try:
        params = conn.get_dsn_parameters()
        for k, v in WANT.items():
            assert params.get(k) == str(v), (k, params.get(k))
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            assert cur.fetchone() == (1,)
    finally:
        conn.close()
        ewdb._POOL = None
