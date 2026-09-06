"""Non-scientific integration tests for the Archaeon -> Vivarium queue seam.

Nothing here tests science. Every assertion is about a mechanical property of
the register: does the relation survive, does cadence still hold, is the
candidate count derivable rather than attested, does the spec stay free of
provenance. Run against real PostgreSQL, in a per-test lane and candidate set.
"""
from __future__ import annotations

import json
import threading
import uuid

import os as _os

import pytest

# The schema conftest.py chose. Before 2026-09-06 these tests wrote into the
# PRODUCTION register -- 245 rows in one run, one of which a live Vivarium
# cycle claimed and tried to execute. VIV_SCHEMA now redirects both this suite
# and archaeon.vivqueue to a throwaway schema carrying the identical DDL.
_S = _os.environ.get("VIV_SCHEMA", "viv")
VIVQ = _S + ".research_experiment_queue"
VIVC = _S + ".candidate_sets"

from archaeon import cadence as cad
from archaeon import config as cfg
from archaeon import vivqueue as vq

psycopg2 = pytest.importorskip("psycopg2")

SPEC = {"executor": "bitstring", "length": 24, "seed": 7,
        "outcome_rule": {"metric": "score", "op": ">=", "value": 0.5,
                         "if_indeterminate": "fail"}}


def _connect():
    try:
        from evidence_wiki.ew import db as ewdb
        return ewdb.connect()
    except Exception as exc:                       # pragma: no cover
        pytest.skip("PostgreSQL unavailable: {}".format(exc))


@pytest.fixture(scope="module")
def conn():
    c = _connect()
    from archaeon import queue as q
    q.apply_migrations(c)
    yield c
    c.close()


@pytest.fixture
def lane(conn):
    name = "test-{}".format(uuid.uuid4().hex[:8])
    yield name
    cur = conn.cursor()
    cur.execute("DELETE FROM archaeon.cadence_log WHERE lane = %s", (name,))
    cur.execute("DELETE FROM " + VIVQ + " "
                "WHERE cadence_lane = %s OR created_by = %s",
                (name, "archaeon-test-" + name))
    cur.execute("DELETE FROM archaeon.cadence_gate WHERE lane = %s", (name,))
    conn.commit()


def _cfg(lane):
    return cfg.ArchaeonConfig(cadence=cfg.CadenceConfig(lane=lane))


def _cands(n, family=None, arms=None):
    out = []
    for i in range(n):
        out.append(vq.make_candidate(
            dict(SPEC, seed=1000 + i),
            family_id=family,
            arm_id=(arms[i % len(arms)] if arms else None),
            source_evidence={"mode": "test", "corpus": {"hash": "corpus:x"}}))
    return out


# --------------------------------------------------------------------------
# The spec stays execution-only
# --------------------------------------------------------------------------
@pytest.mark.parametrize("bad", ["notes", "experiment_kind", "family_id",
                                 "arm_id", "policy", "created_by"])
def test_provenance_in_the_spec_is_refused(bad):
    """Anything that changes spec_hash without changing execution is a channel
    for the policy to leak into the sealed record (Vivarium F2 / S14)."""
    with pytest.raises(vq.RelationContractViolation):
        vq.make_candidate(dict(SPEC, **{bad: "arm_a"}))


def test_world_name_in_the_spec_is_refused():
    with pytest.raises(vq.RelationContractViolation):
        vq.make_candidate(dict(SPEC, world={"name": "arm_a_world"}))


def test_two_arms_may_carry_byte_identical_specs():
    """The property that makes a comparison a comparison. If arm identity had
    to live in the spec, the two arms could never share a spec_hash and the
    universe would be split along the arm boundary by construction."""
    a = vq.make_candidate(SPEC, family_id="fam1", arm_id="a")
    b = vq.make_candidate(SPEC, family_id="fam1", arm_id="b")
    assert a["spec_hash"] == b["spec_hash"]
    assert a["arm_id"] != b["arm_id"]


# --------------------------------------------------------------------------
# Registration and selection
# --------------------------------------------------------------------------
def test_candidate_set_is_registered_and_unchosen_are_cancelled(conn, lane):
    r = vq.submit(conn, candidates=_cands(5), selected_index=2,
                  source_reason="exploration", config=_cfg(lane))
    assert r["registered"] == 5
    assert len(r["cancelled_experiment_ids"]) == 4
    cur = conn.cursor()
    cur.execute("SELECT status, cadence_day_ordinal FROM "
                "" + VIVQ + " WHERE candidate_set_id = %s "
                "ORDER BY status", (r["candidate_set_id"],))
    rows = cur.fetchall()
    assert sum(1 for s, _ in rows if s == "cancelled") == 4
    assert sum(1 for s, _ in rows if s == "queued") == 1
    # only the selected row consumed quota
    assert sum(1 for _, o in rows if o is not None) == 1


def test_cancelled_candidates_are_retained_not_deleted(conn, lane):
    """A cancelled row is the only class-A trace of a selection decision."""
    r = vq.submit(conn, candidates=_cands(4), selected_index=0,
                  source_reason="exploration", config=_cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM " + VIVQ + " "
                "WHERE candidate_set_id = %s", (r["candidate_set_id"],))
    assert int(cur.fetchone()[0]) == 4


def test_candidate_count_is_derived_not_attested(conn, lane):
    r = vq.submit(conn, candidates=_cands(6), selected_index=1,
                  source_reason="exploration", config=_cfg(lane))
    cs = vq.candidate_set(conn, r["candidate_set_id"])
    assert cs["registered"] == 6 and cs["cancelled"] == 5 and cs["retained"] == 1
    assert cs["count_source"].startswith("DERIVED")
    # there must be no column that could carry a fabricated count
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='viv' AND table_name='research_experiment_queue'")
    cols = {c[0] for c in cur.fetchall()}
    assert "candidate_set_size" not in cols, \
        "an attested count column exists; the count must be derived"


def test_registration_is_atomic(conn, lane):
    """A partially registered set must not exist. If any insert fails the whole
    set rolls back, so 'registered before selection' is a property rather than
    a claim."""
    cands = _cands(3)
    cands[2]["spec_hash"] = "not-a-valid-hash"      # violates req_spec_hash_ck
    csid = "cs-atomic-" + uuid.uuid4().hex[:8]
    with pytest.raises(Exception):
        vq.submit(conn, candidates=cands, selected_index=0,
                  source_reason="exploration", config=_cfg(lane),
                  candidate_set_id=csid)
    assert vq.candidate_set(conn, csid) is None


def test_single_candidate_is_an_honest_set_of_one(conn, lane):
    r = vq.submit(conn, candidates=_cands(1), selected_index=0,
                  source_reason="exploration", config=_cfg(lane))
    cs = vq.candidate_set(conn, r["candidate_set_id"])
    assert cs["registered"] == 1 and cs["cancelled"] == 0


# --------------------------------------------------------------------------
# The relation survives, and is frozen
# --------------------------------------------------------------------------
def test_family_and_arm_are_recorded(conn, lane):
    r = vq.submit(conn, candidates=_cands(4, family="fam-x", arms=["a", "b"]),
                  selected_index=0, source_reason="exploration",
                  config=_cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT family_id, arm_id FROM " + VIVQ + " "
                "WHERE candidate_set_id = %s", (r["candidate_set_id"],))
    rows = cur.fetchall()
    assert all(f == "fam-x" for f, _ in rows)
    assert {a for _, a in rows} == {"a", "b"}


def test_relation_is_immutable_after_acceptance(conn, lane):
    """A comparison must not be re-drawn after its outcomes are visible."""
    r = vq.submit(conn, candidates=_cands(2, family="fam-y", arms=["a", "b"]),
                  selected_index=0, source_reason="exploration",
                  config=_cfg(lane))
    cur = conn.cursor()
    with pytest.raises(psycopg2.Error):
        cur.execute("UPDATE " + VIVQ + " SET family_id='other' "
                    "WHERE experiment_id = %s", (r["selected_experiment_id"],))
    conn.rollback()


def test_arm_without_family_is_refused(conn, lane):
    cur = conn.cursor()
    with pytest.raises(psycopg2.Error):
        cur.execute(
            "INSERT INTO " + VIVQ + " "
            "(created_by, source_reason, experiment_spec, spec_hash, arm_id) "
            "VALUES ('t','exploration','{}'::jsonb, %s, 'a')",
            ("sha256:" + "0" * 64,))
    conn.rollback()


def test_request_key_refuses_a_double_submission(conn, lane):
    key = "rk-" + uuid.uuid4().hex[:12]
    c1 = vq.make_candidate(SPEC, request_key=key)
    vq.submit(conn, candidates=[c1], selected_index=0,
              source_reason="exploration", config=_cfg(lane))
    c2 = vq.make_candidate(SPEC, request_key=key)
    with pytest.raises(Exception):
        vq.submit(conn, candidates=[c2], selected_index=0,
                  source_reason="human", config=_cfg(lane))
    conn.rollback()


def test_replication_must_declare_itself(conn, lane):
    r = vq.submit(conn, candidates=_cands(1), selected_index=0,
                  source_reason="exploration", config=_cfg(lane))
    rep = vq.make_candidate(SPEC, replication_of=r["selected_experiment_id"])
    r2 = vq.submit(conn, candidates=[rep], selected_index=0,
                   source_reason="human", config=_cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT replication_of FROM " + VIVQ + " "
                "WHERE experiment_id = %s", (r2["selected_experiment_id"],))
    assert str(cur.fetchone()[0]) == r["selected_experiment_id"]


# --------------------------------------------------------------------------
# Cadence is preserved on the new table
# --------------------------------------------------------------------------
def test_cadence_still_refuses_inside_four_hours(conn, lane):
    vq.submit(conn, candidates=_cands(1), selected_index=0,
              source_reason="exploration", config=_cfg(lane))
    with pytest.raises(cad.CadenceRefused) as ei:
        vq.submit(conn, candidates=_cands(1), selected_index=0,
                  source_reason="exploration", config=_cfg(lane))
    assert ei.value.decision.decision == "REFUSED_MIN_SEPARATION"


def test_registering_many_candidates_does_not_consume_the_daily_cap(conn, lane):
    """The interaction that makes candidate registration affordable.

    Twenty registered candidates must consume ONE of the six daily slots, not
    twenty -- otherwise the class-B -> class-A conversion is priced out of
    existence and would never be used.
    """
    r = vq.submit(conn, candidates=_cands(20), selected_index=7,
                  source_reason="exploration", config=_cfg(lane))
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM " + VIVQ + " "
                "WHERE cadence_lane = %s AND cadence_day_ordinal IS NOT NULL",
                (lane,))
    assert int(cur.fetchone()[0]) == 1
    assert vq.candidate_set(conn, r["candidate_set_id"])["registered"] == 20


def test_database_caps_the_day_at_six(conn, lane):
    """Application-independent: the unique index is the backstop."""
    cur = conn.cursor()
    for i in range(6):
        cur.execute(
            "INSERT INTO " + VIVQ + " "
            "(created_by, source_reason, experiment_spec, spec_hash, "
            " cadence_lane, cadence_day_ordinal) "
            "VALUES ('archaeon','exploration','{}'::jsonb,%s,%s,%s)",
            ("sha256:" + "%064x" % i, lane, i))
    conn.commit()
    with pytest.raises(psycopg2.Error):        # ordinal 6 violates the CHECK
        cur.execute(
            "INSERT INTO " + VIVQ + " "
            "(created_by, source_reason, experiment_spec, spec_hash, "
            " cadence_lane, cadence_day_ordinal) "
            "VALUES ('archaeon','exploration','{}'::jsonb,%s,%s,6)",
            ("sha256:" + "f" * 64, lane))
    conn.rollback()


def test_duplicate_ordinal_is_refused(conn, lane):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO " + VIVQ + " "
        "(created_by, source_reason, experiment_spec, spec_hash, "
        " cadence_lane, cadence_day_ordinal) "
        "VALUES ('archaeon','exploration','{}'::jsonb,%s,%s,0)",
        ("sha256:" + "a" * 64, lane))
    conn.commit()
    with pytest.raises(psycopg2.Error):
        cur.execute(
            "INSERT INTO " + VIVQ + " "
            "(created_by, source_reason, experiment_spec, spec_hash, "
            " cadence_lane, cadence_day_ordinal) "
            "VALUES ('archaeon','exploration','{}'::jsonb,%s,%s,0)",
            ("sha256:" + "b" * 64, lane))
    conn.rollback()


def test_concurrent_instances_cannot_exceed_the_quota(lane):
    """Same guarantee as before the migration, now on the canonical queue."""
    results, lk, bar = [], threading.Lock(), threading.Barrier(6)

    def worker():
        c = _connect()
        try:
            bar.wait(timeout=30)
            try:
                vq.submit(c, candidates=_cands(1), selected_index=0,
                          source_reason="exploration", config=_cfg(lane))
                with lk:
                    results.append("ADMITTED")
            except cad.CadenceRefused as exc:
                with lk:
                    results.append(exc.decision.decision)
            except Exception as exc:            # pragma: no cover
                with lk:
                    results.append("ERROR:" + str(exc)[:120])
        finally:
            c.close()

    ts = [threading.Thread(target=worker) for _ in range(6)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=60)
    assert not [r for r in results if r.startswith("ERROR")], results
    assert results.count("ADMITTED") == 1, results

    c = _connect()
    cur = c.cursor()
    cur.execute("DELETE FROM archaeon.cadence_log WHERE lane = %s", (lane,))
    cur.execute("DELETE FROM " + VIVQ + " "
                "WHERE cadence_lane = %s", (lane,))
    cur.execute("DELETE FROM archaeon.cadence_gate WHERE lane = %s", (lane,))
    c.commit()
    c.close()


# --------------------------------------------------------------------------
# The retired queue
# --------------------------------------------------------------------------
def test_archaeon_queue_is_retired_but_readable(conn):
    cur = conn.cursor()
    cur.execute("SELECT obj_description('archaeon.experiment_queue'::regclass)")
    d = cur.fetchone()[0] or ""
    assert "RETIRED" in d
    cur.execute("SELECT count(*) FROM archaeon.experiment_queue")
    assert int(cur.fetchone()[0]) >= 1, "the retired register lost its rows"


def test_archaeon_no_longer_writes_to_its_own_queue():
    """Scanned over EXECUTABLE code, docstrings stripped.

    A raw substring scan fails on the module's own docstring, which says it
    does not write to the retired table -- the same trap as the cadence
    idle-check test. Prose that names a thing is not a use of it.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(vq))
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)                 and isinstance(node.value.value, str):
            node.value.value = ""
    code = ast.unparse(tree)
    assert "archaeon.experiment_queue" not in code,         "Archaeon still writes to the retired register"
    assert "research_experiment_queue" in code


# --------------------------------------------------------------------------
# Archaeon does not create Vivarium's schema
# --------------------------------------------------------------------------
def test_queue_contract_precondition_passes_when_migration_applied(conn):
    vq.assert_queue_ready(conn)          # must not raise


def test_archaeon_never_alters_vivariums_table():
    """A consumer that silently ALTERs a producer's schema is how one contract
    becomes two divergent definitions. That already happened once here and was
    caught only because a view refused to drop a column."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(vq))
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            node.value.value = ""
    code = ast.unparse(tree).upper()
    for banned in ("ALTER TABLE", "CREATE TABLE", "CREATE OR REPLACE VIEW",
                   "DROP VIEW", "CREATE INDEX"):
        assert banned not in code, \
            "vivqueue performs DDL ({!r}); Vivarium owns that table".format(banned)


def test_missing_contract_fails_loudly(conn):
    """A missing Vivarium migration must be a visible error, never a silent
    divergence that Archaeon papers over by creating the columns itself."""
    real = vq.REQUIRED_COLUMNS
    try:
        vq.REQUIRED_COLUMNS = real + ("a_column_vivarium_never_made",)
        with pytest.raises(vq.QueueContractMissing) as ei:
            vq.assert_queue_ready(conn)
        assert "002_relations_cadence_idempotency" in str(ei.value)
    finally:
        vq.REQUIRED_COLUMNS = real
