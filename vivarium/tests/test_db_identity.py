"""connect() must PROVE which cluster it reached (2026-09-16).

Motivation, measured on the 09-16 boot on M2: with no VIV_DB_HOST the tracked
default db_host="localhost" reached the quarantined M2 fork, and only the
fork's missing viv schema made `status` fail; `run` would have created the
schema and ticked green on an empty queue. Three controls, per base rule 3:

    POSITIVE  the default connection reaches the canonical store and the
              verdict names it
    NEGATIVE  a throwaway schema naming an environment whose registered
              identity is wrong is REFUSED, the connection closed, and the
              refusal carries the incident signature
    CHEAT     the production schema with the same wrong environment exported
              is NOT re-aimed: the pin is decided by the schema, so the
              connection succeeds against the canonical store while the
              identical variable makes a non-production connection fail

These tests need the canonical server (conftest sets VIV_SCHEMA to a
throwaway schema on it). On M2 export VIV_DB_HOST=192.168.1.202 first; a run
that reaches the fork now fails in the fixture, which is the point.
"""
from __future__ import annotations

import json
import os

import psycopg2
import pytest

from viv import db as _db


def _registry_with_wrong_id(tmp_path):
    identity = _db._identity_module()
    envs = identity.load_registry()
    bogus = dict(envs[_db.CANONICAL_ENVIRONMENT])
    bogus["db_system_id"] = "1"                       # no cluster has this id
    bogus["description"] = "test-only expectation with an impossible identity"
    envs["viv-test-wrong-store"] = bogus
    path = tmp_path / "environments.json"
    path.write_text(json.dumps({"environments": envs}), encoding="utf-8")
    return path


def test_positive_default_connection_proves_canonical():
    conn = _db.connect()
    try:
        identity = _db._identity_module()
        v = identity.check(conn, _db.CANONICAL_ENVIRONMENT)
        assert v["ok"], v
        assert v["observed"]["db_system_id"] == v["expected"]["db_system_id"]
        with conn.cursor() as cur:                    # still usable afterwards
            cur.execute("SELECT 1")
            assert cur.fetchone()[0] == 1
    finally:
        conn.close()


def test_negative_wrong_environment_is_refused_and_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMETHEUS_ENVIRONMENTS", str(_registry_with_wrong_id(tmp_path)))
    monkeypatch.setenv("VIV_DB_ENVIRONMENT", "viv-test-wrong-store")
    assert _db.load_config()["schema"] != _db.PRODUCTION_SCHEMA   # conftest
    assert _db.db_environment() == "viv-test-wrong-store"
    with pytest.raises(_db.WrongStore) as ei:
        _db.connect()
    msg = str(ei.value)
    assert "WRONG_ENVIRONMENT" in msg
    assert "incident signature" in msg


def test_negative_closes_the_connection(tmp_path, monkeypatch):
    monkeypatch.setenv("PROMETHEUS_ENVIRONMENTS", str(_registry_with_wrong_id(tmp_path)))
    cfg = _db.load_config()
    conn = psycopg2.connect(host=cfg["db_host"], dbname=cfg["db_name"],
                            user=cfg["db_user"], password=cfg["db_password"])
    with pytest.raises(_db.WrongStore):
        _db.require_environment(conn, "viv-test-wrong-store")
    assert conn.closed


def test_negative_unknown_environment_is_refused(monkeypatch):
    monkeypatch.setenv("VIV_DB_ENVIRONMENT", "no-such-environment")
    with pytest.raises(_db.WrongStore) as ei:
        _db.connect()
    assert "NO_EXPECTATION" in str(ei.value)


def test_cheat_production_schema_ignores_the_environment_override(tmp_path, monkeypatch):
    """The variable that makes a test connection FAIL leaves a production
    connection pinned to the canonical store. Only the pin is under test: the
    production schema is never migrated, written or read here."""
    monkeypatch.setenv("PROMETHEUS_ENVIRONMENTS", str(_registry_with_wrong_id(tmp_path)))
    monkeypatch.setenv("VIV_DB_ENVIRONMENT", "viv-test-wrong-store")
    monkeypatch.setenv("VIV_SCHEMA", _db.PRODUCTION_SCHEMA)
    assert _db.load_config()["schema"] == _db.PRODUCTION_SCHEMA
    assert _db.db_environment() == _db.CANONICAL_ENVIRONMENT
    conn = _db.connect()                                 # pinned: succeeds
    conn.close()
    monkeypatch.delenv("VIV_SCHEMA")
    os.environ.setdefault("VIV_SCHEMA", "viv_test_cheat_ctrl")
    assert _db.db_environment() == "viv-test-wrong-store"
    with pytest.raises(_db.WrongStore):                  # same variable, no pin
        _db.connect()


def test_cheat_config_key_cannot_reaim_production(monkeypatch):
    cfg = {"schema": _db.PRODUCTION_SCHEMA, "db_environment": "m2-local-fork"}
    assert _db.db_environment(cfg) == _db.CANONICAL_ENVIRONMENT
    cfg["schema"] = "viv_test_x"
    assert _db.db_environment(cfg) == "m2-local-fork"


def test_guard_import_failure_refuses(monkeypatch):
    """No guard, no proof, no connection (fail closed)."""
    import builtins
    real_import = builtins.__import__

    def broken(name, *a, **kw):
        if name == "comms" or name.startswith("comms."):
            raise ImportError("simulated: comms unavailable")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", broken)
    with pytest.raises(_db.WrongStore) as ei:
        _db.connect()
    assert "cannot be imported" in str(ei.value)
