"""Adversarial tests for the database-identity guard (Hermes, 2026-09-11).

The guard is only worth anything if it rejects targets that are wrong but
plausible. These tests run against REAL targets in this fleet plus a
deliberately constructed one, and cover the three control classes the base
role requires:

  POSITIVE  the canonical store is ACCEPTED            (can it detect real success)
  NEGATIVE  the live M2 fork is REJECTED               (does it hallucinate a match)
  CHEAT     a freshly built database carrying a PERFECT comms schema, on the
            wrong cluster, is REJECTED                 (can the channel actually
            observe the thing it claims to measure, when success is injected)

The cheat control is the load-bearing one. Its fixture satisfies every
structural check a naive guard would make -- database reachable, schema
present, all four comms tables present with the right columns, queries
succeed -- and differs from the canonical store in exactly one respect:
identity. If the guard passes it, the guard is measuring structure and
calling it identity, which is the defect being fixed.

Run:  python -m pytest roles/Hermes/science/test_db_identity.py -v
Tests that need a cluster skip (never pass) when it is unreachable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import db_identity as G                                          # noqa: E402

psycopg2 = pytest.importorskip("psycopg2")

CANONICAL_HOST = "192.168.1.202"
FORK_HOST = "localhost"
FIXTURE_DB = "hermes_guard_fixture"
REG = G.load_registry(Path(__file__).resolve().parent / "ENVIRONMENTS.json")


def _cfg():
    from evidence_wiki.ew import db as ewdb
    return ewdb.load_config()


def _connect(host, dbname=None):
    """Connect or skip. Never prints or returns the credential."""
    c = _cfg()
    try:
        return psycopg2.connect(host=host, dbname=dbname or c["db_name"],
                                user=c["db_user"], password=c["db_password"],
                                connect_timeout=8)
    except Exception as e:                                       # noqa: BLE001
        pytest.skip("{} unreachable: {}".format(host, type(e).__name__))


# --------------------------------------------------------------- POSITIVE ---
def test_positive_canonical_store_is_accepted():
    conn = _connect(CANONICAL_HOST)
    try:
        v = G.require(conn, "prometheus-canonical", registry=REG)
        assert v["ok"] and v["reason"] == "MATCH"
        assert v["observed"]["db_system_id"] == REG["prometheus-canonical"]["db_system_id"]
    finally:
        conn.close()


# --------------------------------------------------------------- NEGATIVE ---
def test_negative_the_live_m2_fork_is_rejected():
    """The exact target five seats reached on 2026-09-11."""
    conn = _connect(FORK_HOST)
    try:
        with pytest.raises(G.WrongEnvironment) as ei:
            G.require(conn, "prometheus-canonical", registry=REG)
        assert "db_system_id" in ei.value.args[0]
        assert ei.value.observed["db_system_id"] == REG["m2-local-fork"]["db_system_id"]
    finally:
        conn.close()


def test_the_fork_is_only_wrong_relative_to_an_expectation():
    """Naming the fork deliberately is allowed; getting it by default is not.
    This is what keeps the guard from being a ban on local work."""
    conn = _connect(FORK_HOST)
    try:
        assert G.check(conn, "m2-local-fork", registry=REG)["ok"] is True
    finally:
        conn.close()


def test_schema_presence_cannot_be_the_check_because_both_stores_have_ew():
    """The measurement that kills the obvious cheaper guard."""
    seen = {}
    for label, host in (("canonical", CANONICAL_HOST), ("fork", FORK_HOST)):
        conn = _connect(host)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM information_schema.tables "
                            "WHERE table_schema='ew'")
                seen[label] = cur.fetchone()[0]
        finally:
            conn.close()
    assert seen["canonical"] > 0 and seen["fork"] > 0, seen
    assert seen["canonical"] != seen["fork"], (
        "fork and canonical happen to have equal table counts; the point stands "
        "either way, but update the note in db_identity.py")


# ------------------------------------------------------------------ CHEAT ---
@pytest.fixture(scope="module")
def cheat_target():
    """A database that passes every structural test and is still the wrong one.

    Built on the M2 cluster, given the real comms schema from comms/schema.sql,
    dropped afterwards. Never touches the canonical store, and never touches
    the fork's own schemas.
    """
    c = _cfg()
    try:
        admin = psycopg2.connect(host=FORK_HOST, dbname="postgres", user=c["db_user"],
                                 password=c["db_password"], connect_timeout=8)
    except Exception as e:                                       # noqa: BLE001
        pytest.skip("cannot reach the M2 cluster to build the cheat fixture: {}"
                    .format(type(e).__name__))
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute('DROP DATABASE IF EXISTS "{}"'.format(FIXTURE_DB))
        cur.execute('CREATE DATABASE "{}"'.format(FIXTURE_DB))
    ddl = (ROOT / "comms" / "schema.sql").read_text(encoding="utf-8").replace("{schema}", "comms")
    victim = psycopg2.connect(host=FORK_HOST, dbname=FIXTURE_DB, user=c["db_user"],
                              password=c["db_password"], connect_timeout=8)
    victim.autocommit = True
    with victim.cursor() as cur:
        cur.execute(ddl)
    yield victim
    victim.close()
    with admin.cursor() as cur:
        cur.execute('DROP DATABASE IF EXISTS "{}"'.format(FIXTURE_DB))
    admin.close()


def test_cheat_fixture_really_does_satisfy_every_structural_check(cheat_target):
    """Prove the cheat is a cheat before proving the guard survives it."""
    with cheat_target.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='comms' ORDER BY 1")
        tables = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT count(*) FROM comms.agents")        # the query that failed on M2
        agents = cur.fetchone()[0]
    assert {"agents", "messages", "receipts", "task_queue"} <= tables, tables
    assert agents == 0
    # i.e. `comms sync` would have found its table here and proceeded happily.


def test_cheat_a_perfect_comms_schema_on_the_wrong_cluster_is_rejected(cheat_target):
    with pytest.raises(G.WrongEnvironment) as ei:
        G.require(cheat_target, "prometheus-canonical", registry=REG)
    assert ei.value.observed["db_name"] == FIXTURE_DB
    assert "db_name" in ei.value.args[0]


# ------------------------------------------------------- FAIL-CLOSED PATHS ---
def test_unknown_environment_refuses_rather_than_passes():
    conn = _connect(CANONICAL_HOST)
    try:
        v = G.check(conn, "no-such-environment", registry=REG)
        assert v["ok"] is False and v["reason"] == "NO_EXPECTATION"
    finally:
        conn.close()


class _BrokenConn:
    """A connection whose identity cannot be read. An instrument that cannot
    see must say so, not assume."""

    def cursor(self):
        raise RuntimeError("identity query refused")

    def rollback(self):
        pass


def test_unreadable_identity_refuses():
    v = G.check(_BrokenConn(), "prometheus-canonical", registry=REG)
    assert v["ok"] is False and v["reason"] == "IDENTITY_UNREADABLE"
    assert v["signature"]


def test_an_empty_registry_refuses_everything():
    conn = _connect(CANONICAL_HOST)
    try:
        assert G.check(conn, "prometheus-canonical", registry={})["ok"] is False
    finally:
        conn.close()


# -------------------------------------------------------------- SIGNATURE ---
def test_the_same_wrong_target_produces_one_signature_for_every_seat():
    """Five seats, one incident. This is the dedup mechanism's only moving part."""
    exp = REG["prometheus-canonical"]
    obs = {"db_system_id": REG["m2-local-fork"]["db_system_id"],
           "db_name": "prometheus_fire", "read_error": None}
    sigs = {G.signature("prometheus-canonical", dict(obs), dict(exp)) for _ in range(5)}
    assert len(sigs) == 1


def test_a_different_wrong_target_produces_a_different_signature():
    exp = REG["prometheus-canonical"]
    a = G.signature("prometheus-canonical",
                    {"db_system_id": "1", "db_name": "prometheus_fire", "read_error": None}, exp)
    b = G.signature("prometheus-canonical",
                    {"db_system_id": "2", "db_name": "prometheus_fire", "read_error": None}, exp)
    c = G.signature("prometheus-canonical",
                    {"db_system_id": None, "db_name": None, "read_error": "boom"}, exp)
    assert len({a, b, c}) == 3


def test_registry_is_pure_data_and_carries_no_credential():
    raw = (Path(__file__).resolve().parent / "ENVIRONMENTS.json").read_text(encoding="utf-8")
    low = raw.lower()
    for bad in ("password", "passwd", "token", "secret", "bearer"):
        assert bad not in low, bad
    json.loads(raw)


# ------------------- WHAT THE GUARD ADDS OVER THE DEPLOYED STRUCTURAL CHECK ---
# comms.connect() was hardened on 2026-09-11 (5f9d8ea7e, Archaeon, on Atalanta
# #47 / Eos #55): it refuses a database with no <schema>.messages table. That is
# correct and it closes the fork-the-queue path. These two tests measure what it
# can and cannot discriminate, and stay true whether or not the identity guard
# is ever adopted -- they are statements about the two predicates, not about a
# version of the code.

def test_comms_structural_predicate_admits_the_cheat_fixture_but_identity_does_not(cheat_target):
    """The deployed check asks "is there a comms schema here". The cheat
    fixture answers yes. It is still the wrong cluster.

    This is not a defect report against 5f9d8ea7e: the structural check fails
    closed TODAY because M2's fork happens to carry no comms schema. It stops
    doing so the moment anyone runs `comms init` on the fork -- a path the code
    deliberately keeps open (require_schema=False) -- or restores a copy that
    includes comms.
    """
    with cheat_target.cursor() as cur:
        cur.execute("select to_regclass('comms.messages')")     # comms/api.py's own predicate
        structural_ok = cur.fetchone()[0] is not None
    identity_ok = G.check(cheat_target, "prometheus-canonical", registry=REG)["ok"]
    assert structural_ok is True, "the fixture is supposed to satisfy the structural check"
    assert identity_ok is False
    assert structural_ok is not identity_ok                     # the discriminating power added


def test_the_evidence_wiki_path_has_no_such_check_and_its_schema_is_in_both_stores():
    """Where silent acceptance actually lives. `ew.claims` answers on the fork
    exactly as it answers on the canonical store, so an Evidence Wiki write
    resolved to localhost on M2 proceeds with no error at all -- unlike comms,
    which at least raised UndefinedTable."""
    results = {}
    for label, host in (("canonical", CANONICAL_HOST), ("fork", FORK_HOST)):
        conn = _connect(host)
        try:
            with conn.cursor() as cur:
                cur.execute("select to_regclass('ew.claims')")
                results[label] = {"claims_table_present": cur.fetchone()[0] is not None}
            results[label]["identity_is_canonical"] = G.check(
                conn, "prometheus-canonical", registry=REG)["ok"]
        finally:
            conn.close()
    assert results["canonical"]["claims_table_present"] is True
    assert results["fork"]["claims_table_present"] is True      # the structural check cannot help
    assert results["canonical"]["identity_is_canonical"] is True
    assert results["fork"]["identity_is_canonical"] is False    # the identity check can
