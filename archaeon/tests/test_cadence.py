"""Cadence tests against a REAL PostgreSQL database.

These do not mock the database. The whole cadence design rests on PostgreSQL
semantics -- ``SELECT ... FOR UPDATE`` serialization, a partial unique index,
and the server clock -- and a mock would test the mock. Concurrency is
exercised with genuine parallel connections.

Every test runs in its own LANE (migration 002), so it exercises the real
database mechanism without consuming or colliding with production's six
proposals for the day. Each cleans up after itself.
"""
from __future__ import annotations

import json
import os
import threading
import uuid

import os as _os

import pytest

_S = _os.environ.get("VIV_SCHEMA", "viv")
VIVQ = _S + ".research_experiment_queue"
VIVE = _S + ".research_experiment_events"

from archaeon import cadence as cad
from archaeon import config as cfg
from archaeon import queue as q
from archaeon import vivqueue as vq

psycopg2 = pytest.importorskip("psycopg2")


def _connect():
    try:
        from evidence_wiki.ew import db as ewdb
        return ewdb.connect()
    except Exception as exc:                       # pragma: no cover
        pytest.skip("PostgreSQL unavailable: {}".format(exc))


@pytest.fixture(scope="module")
def conn():
    c = _connect()
    q.apply_migrations(c)
    yield c
    c.close()


@pytest.fixture
def lane(conn):
    """A unique quota lane per test.

    Real isolation without a transaction rollback -- which would defeat the
    point, since the behaviour under test is what COMMITTED concurrent writes
    do to one another.
    """
    name = "test-{}".format(uuid.uuid4().hex[:8])
    yield name
    _cleanup(conn, name)


def _cleanup(conn, lane):
    cur = conn.cursor()
    cur.execute("DELETE FROM archaeon.cadence_log WHERE lane = %s", (lane,))
    cur.execute("DELETE FROM archaeon.experiment_queue WHERE lane = %s", (lane,))
    # the CANONICAL register: cadence counts rows HERE now (Vivarium 002)
    cur.execute("DELETE FROM " + VIVE + " e USING " + VIVQ + " q "
                "WHERE e.experiment_id = q.experiment_id "
                "  AND q.cadence_lane = %s", (lane,))
    cur.execute("DELETE FROM " + VIVQ + " WHERE cadence_lane = %s", (lane,))
    cur.execute("DELETE FROM archaeon.cadence_gate WHERE lane = %s", (lane,))
    conn.commit()


def _insert_viv(conn, lane, ordinal, offset_hours=0.0):
    """An autonomous-shaped row in the CANONICAL register, at a controlled
    time. Cadence counts rows there now, not in the retired table."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO " + VIVQ + " (created_at, created_by, source_reason, "
        "source_evidence, experiment_spec, spec_hash, status, cadence_lane, "
        "cadence_day_ordinal) VALUES "
        "(now() - (%s || ' hours')::interval, 'archaeon', "
        " 'exploration', '{}'::jsonb, '{}'::jsonb, %s, 'queued', "
        " %s, %s) RETURNING experiment_id",
        (str(offset_hours), "sha256:" + uuid.uuid4().hex * 2, lane, ordinal))
    out = cur.fetchone()[0]
    conn.commit()
    return out


def _insert(conn, lane, ordinal, offset_hours=0.0, pid=None,
            source_reason="exploration"):
    """Insert an autonomous-shaped row directly, at a controlled time."""
    pid = pid or "AX-{}".format(uuid.uuid4().hex[:12])
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO archaeon.experiment_queue
            (proposal_id, lane, created_at, day_ordinal, created_by,
             source_reason, spec, spec_hash, source_evidence)
        VALUES (%s, %s, now() - (%s || ' hours')::interval, %s, 'archaeon', %s,
                '{}'::jsonb, 'sha256:test', '{}'::jsonb)
        """, (pid, lane, str(offset_hours), ordinal, source_reason))
    conn.commit()
    return pid


# --------------------------------------------------------------------------
# The database-level cap
# --------------------------------------------------------------------------
def test_seventh_autonomous_proposal_in_a_day_is_impossible(conn, lane):
    """Six ordinals exist. There is no seventh, at the DATABASE level."""
    for i in range(6):
        _insert(conn, lane, i, offset_hours=0.1 * i)
    with pytest.raises(psycopg2.Error):
        _insert(conn, lane, 6)          # CHECK ordinal_range rejects it
    conn.rollback()


def test_duplicate_ordinal_in_one_day_is_rejected(conn, lane):
    """Two instances cannot both take ordinal 0 -- the unique index decides."""
    _insert(conn, lane, 0)
    with pytest.raises(psycopg2.Error):
        _insert(conn, lane, 0)
    conn.rollback()


def test_autonomous_row_must_carry_an_ordinal(conn):
    """Otherwise an instance could evade the cap by leaving it NULL."""
    cur = conn.cursor()
    with pytest.raises(psycopg2.Error):
        cur.execute(
            """
            INSERT INTO archaeon.experiment_queue
                (proposal_id, day_ordinal, created_by, source_reason,
                 spec, spec_hash, source_evidence)
            VALUES (%s, NULL, 'archaeon', 'exploration',
                    '{}'::jsonb, 'x', '{}'::jsonb)
            """, ("AX-" + uuid.uuid4().hex[:12],))
    conn.rollback()


def test_renaming_the_actor_does_not_escape_the_quota(conn, lane):
    """Migration 001 keyed autonomy on the literal created_by 'archaeon', so a
    second instance under any other handle escaped the cap entirely. Autonomy
    is now keyed on source_reason, which no rename can change."""
    cur = conn.cursor()
    _insert(conn, lane, 0, offset_hours=0.1)
    cur.execute(
        """
        INSERT INTO archaeon.experiment_queue
            (proposal_id, lane, day_ordinal, created_by, source_reason,
             spec, spec_hash, source_evidence)
        VALUES (%s, %s, 1, 'archaeon-on-some-other-host', 'exploration',
                '{}'::jsonb, 'x', '{}'::jsonb)
        """, ("AX-" + uuid.uuid4().hex[:12], lane))
    conn.commit()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert d.detail["autonomous_today"] == 2, (
        "a renamed instance escaped the quota count")


def test_human_row_must_not_carry_an_ordinal(conn):
    """Human rows are outside the quota by construction, not by convention."""
    cur = conn.cursor()
    with pytest.raises(psycopg2.Error):
        cur.execute(
            """
            INSERT INTO archaeon.experiment_queue
                (proposal_id, day_ordinal, created_by, source_reason,
                 spec, spec_hash, source_evidence)
            VALUES (%s, 0, 'james', 'human', '{}'::jsonb, 'x', '{}'::jsonb)
            """, ("AX-" + uuid.uuid4().hex[:12],))
    conn.rollback()


# --------------------------------------------------------------------------
# The evaluator
# --------------------------------------------------------------------------
def _ccfg(lane):
    return cfg.CadenceConfig(lane=lane)


def test_admits_when_the_day_is_empty(conn, lane):
    cur = conn.cursor()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert d.admitted and d.day_ordinal == 0


def test_refuses_before_four_hours_have_passed(conn, lane):
    _insert(conn, lane, 0, offset_hours=3.5)
    cur = conn.cursor()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert not d.admitted
    assert d.decision == "REFUSED_MIN_SEPARATION"
    assert d.detail["next_eligible_in_seconds"] > 0


def test_admits_after_four_hours(conn, lane):
    """A proposal 4.5h old satisfies the separation.

    The ordinal is asserted against the DAY COUNT rather than hard-coded to 1.
    Near UTC midnight a row 4.5 hours old falls on the PREVIOUS UTC day, so it
    satisfies the separation (which is day-independent) while contributing
    nothing to today's count. Hard-coding 1 made this test fail for ~4.5 hours
    out of every 24 -- a latent flake that only surfaced when a run happened to
    cross 00:00 UTC.
    """
    _insert(conn, lane, 0, offset_hours=4.5)
    cur = conn.cursor()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert d.admitted, "4.5h separation should admit: {}".format(d.detail)
    assert d.day_ordinal == d.detail["autonomous_today"],         "ordinal must be the count of autonomous rows on the CURRENT UTC day"


def test_refuses_at_the_daily_cap(conn, lane):
    """The cap is evaluated BEFORE the separation, so it reports DAILY_CAP.

    All six rows are placed inside the CURRENT UTC day. Spreading them over
    5-10 hours (the original) pushes them onto the previous UTC day whenever a
    run happens within ~10h of 00:00 UTC, at which point today's count is 0 and
    no cap can fire. The property under test -- cap precedence over separation
    -- is time-independent when the rows are anchored to today.
    """
    for i in range(6):
        _insert(conn, lane, i, offset_hours=0.01 * (i + 1))
    cur = conn.cursor()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert d.detail["autonomous_today"] == 6
    assert not d.admitted
    assert d.decision == "REFUSED_DAILY_CAP",         "cap must take precedence over separation, got {}".format(d.decision)


def test_separation_is_checked_across_the_utc_day_boundary(conn, lane):
    """A proposal at 23:50 and one at 00:10 are 20 minutes apart, even though a
    day-scoped query would not see the earlier one."""
    cur = conn.cursor()
    # Place a row 1 hour ago but on the PREVIOUS utc day, if we are early in
    # the UTC day; otherwise the test still asserts the global check is used.
    _insert(conn, lane, 0, offset_hours=1.0)
    cur.execute("UPDATE archaeon.experiment_queue "
                "SET created_at = now() - interval '1 hour' "
                "WHERE lane = %s", (lane,))
    conn.commit()
    cur = conn.cursor()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert not d.admitted
    assert d.detail["last_autonomous_at_any_day"] is not None


def test_idle_vivarium_is_not_a_reason_to_relax():
    """Nothing in the cadence DECISION PATH may consult runner state.

    Scanned over executable code only, with docstrings and comments stripped:
    the module's prose necessarily mentions the very things it must not read,
    so a raw substring scan would fail on its own explanation.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(cad))
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)                 and isinstance(node.value.value, str):
            node.value.value = ""           # blank every docstring
    code = ast.unparse(tree)

    for forbidden in ("status", "QUEUED", "CLAIMED", "RUNNING",
                      "claimed_by", "idle", "queue_depth"):
        assert forbidden not in code, (
            "cadence consults runner state via {!r}; queue depth is not a "
            "reason to relax the four-hour boundary".format(forbidden))


# --------------------------------------------------------------------------
# Concurrency: the real test
# --------------------------------------------------------------------------
def test_concurrent_instances_cannot_exceed_the_quota(lane):
    """Eight threads, eight real connections, one empty day, one lane.

    Exactly ONE may be admitted: the first writes ordinal 0 and every other is
    then inside the four-hour window. This is the property the whole design
    exists for.
    """
    results = []
    lock = threading.Lock()
    barrier = threading.Barrier(8)

    def worker():
        c = _connect()
        try:
            barrier.wait(timeout=30)
            spec = {"procedure": "archaeon.explore.v0", "spec_hash": "sha256:x",
                    "worlds": ["w0"], "players": []}
            ev = {"schema": "archaeon.provenance.v0", "mode": "exploration",
                  "corpus": {"hash": "corpus:test"},
                  "rules": {"config_fingerprint": "cfg:test"}}
            try:
                out = vq.submit(
                    c, candidates=[vq.make_candidate(
                        {k: v for k, v in spec.items() if k != "spec_hash"},
                        source_evidence=ev)],
                    selected_index=0, source_reason="exploration",
                    config=cfg.ArchaeonConfig(cadence=_ccfg(lane)))
                with lock:
                    results.append(("ADMITTED",
                                    out["selected_experiment_id"]))
            except cad.CadenceRefused as exc:
                with lock:
                    results.append(("REFUSED", exc.decision.decision))
            except Exception as exc:                # pragma: no cover
                with lock:
                    results.append(("ERROR", str(exc)[:200]))
        finally:
            c.close()

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    admitted = [r for r in results if r[0] == "ADMITTED"]
    errors = [r for r in results if r[0] == "ERROR"]
    assert not errors, "unexpected errors: {}".format(errors)
    assert len(results) == 8
    assert len(admitted) == 1, \
        "{} concurrent instances were admitted; quota was evaded".format(
            len(admitted))

    c = _connect()
    _cleanup(c, lane)
    c.close()


def test_refusals_are_logged(conn, lane):
    """A refusal that leaves no trace is indistinguishable from a cycle that
    never ran."""
    _insert_viv(conn, lane, 0, offset_hours=0.5)
    spec = {"procedure": "archaeon.explore.v0", "spec_hash": "sha256:y",
            "worlds": ["w0"], "players": []}
    ev = {"schema": "archaeon.provenance.v0", "mode": "exploration",
          "corpus": {"hash": "corpus:test"},
          "rules": {"config_fingerprint": "cfg:test"}}
    before = _log_count(conn)
    with pytest.raises(cad.CadenceRefused):
        vq.submit(conn, candidates=[vq.make_candidate(
                      {k: v for k, v in spec.items() if k != "spec_hash"},
                      source_evidence=ev)],
                  selected_index=0, source_reason="exploration",
                  config=cfg.ArchaeonConfig(cadence=_ccfg(lane)))
    assert _log_count(conn) > before


def _log_count(conn) -> int:
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM archaeon.cadence_log")
    return int(cur.fetchone()[0])


# --------------------------------------------------------------------------
# Human rows do not consume the autonomous quota
# --------------------------------------------------------------------------
def test_human_rows_do_not_consume_the_quota(conn, lane):
    cur = conn.cursor()
    for _ in range(10):
        cur.execute(
            """
            INSERT INTO archaeon.experiment_queue
                (proposal_id, lane, day_ordinal, created_by, source_reason,
                 spec, spec_hash, source_evidence)
            VALUES (%s, %s, NULL, 'james', 'human',
                    '{}'::jsonb, 'x', '{}'::jsonb)
            """, ("AX-" + uuid.uuid4().hex[:12], lane))
    conn.commit()
    cad.take_gate(cur, lane)
    d = cad.evaluate(cur, _ccfg(lane))
    conn.commit()
    assert d.admitted, "human rows consumed the autonomous quota"
    assert d.day_ordinal == 0


# --------------------------------------------------------------------------
# The write path refuses a record carrying a verdict
# --------------------------------------------------------------------------
def test_negative_authority_blocks_the_write(conn, lane):
    spec = {"procedure": "archaeon.explore.v0", "spec_hash": "sha256:z",
            "note": "this lineage is exhausted", "worlds": ["w0"]}
    ev = {"schema": "archaeon.provenance.v0", "mode": "exploration",
          "corpus": {"hash": "corpus:test"},
          "rules": {"config_fingerprint": "cfg:test"}}
    with pytest.raises(q.NegativeAuthorityViolation):
        vq.submit(conn, candidates=[vq.make_candidate(
                      {k: v for k, v in spec.items() if k != "spec_hash"},
                      source_evidence=ev)],
                  selected_index=0, source_reason="exploration",
                  config=cfg.ArchaeonConfig(cadence=_ccfg(lane)))
    conn.rollback()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM " + VIVQ + " WHERE cadence_lane = %s",
                (lane,))
    assert int(cur.fetchone()[0]) == 0, "a forbidden record reached the queue"


def test_the_retired_writer_refuses(conn, lane):
    """archaeon.experiment_queue is retired. The old writer must not remain a
    second live path into a second table -- that seam is what made Archaeon's
    proposals go nowhere."""
    with pytest.raises(q.QueueRetired) as exc:
        q.enqueue(conn, spec={"procedure": "x"}, source_reason="exploration",
                  source_evidence={})
    assert "vivqueue.submit" in str(exc.value)
