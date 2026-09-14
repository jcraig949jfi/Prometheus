"""ew.db refuses a store whose identity is not the expected environment
(Hermes patch, comms #69; accepted 2026-09-11).

Needs the database (it reads pg_control_system() on a live connection);
skipped when it cannot connect. The refusal is exercised by EXPECTING the
other registered environment, never by touching another store.

    positive   PROMETHEUS_ENV unset -> prometheus-canonical is what M1 is
    cheat      PROMETHEUS_ENV=m2-local-fork on the canonical store refuses
               with WrongEnvironment, on the pool AND on the direct fallback
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ew import db as ewdb  # noqa: E402


def _reachable():
    try:
        import psycopg2
        c = ewdb.load_config()
        psycopg2.connect(host=c["db_host"], dbname=c["db_name"], user=c["db_user"],
                         password=c["db_password"], connect_timeout=3).close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _reachable(), reason="no database")


@pytest.fixture(autouse=True)
def _fresh_pool(monkeypatch):
    monkeypatch.setattr(ewdb, "_POOL", None)
    monkeypatch.delenv("PROMETHEUS_ENV", raising=False)
    yield
    ewdb._POOL = None


def test_positive_canonical_expectation_connects():
    c = ewdb.connect()
    with c.cursor() as cur:
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1
    c.close()


def test_cheat_wrong_environment_refuses_pool(monkeypatch):
    monkeypatch.setenv("PROMETHEUS_ENV", "m2-local-fork")
    with pytest.raises(Exception) as e:
        ewdb.connect()
    assert type(e.value).__name__ == "WrongEnvironment"
    assert "REFUSED" in str(e.value)
    assert ewdb._POOL is None, "a refused pool must not be kept"


def test_cheat_wrong_environment_refuses_direct_fallback(monkeypatch):
    monkeypatch.setenv("PROMETHEUS_ENV", "m2-local-fork")

    class _Broken:
        def getconn(self):
            raise RuntimeError("pool exhausted")
    monkeypatch.setattr(ewdb, "_get_pool", lambda: _Broken())
    with pytest.raises(Exception) as e:
        ewdb.connect()
    assert type(e.value).__name__ == "WrongEnvironment"
