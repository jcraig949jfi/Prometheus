"""A candidate set is registered ONCE; appending to it is refused -- in the
database, for every writer, under a race. (migrations/005, viv.queue.enqueue,
viv.cli enqueue; operator directive 2026-09-12 "close the residual burst path")

WHY. 85,727 phantom "alternative" experiments reached the engine because one
candidate_set_id was reused across 256 submits and the selection binding did
what the contract said. Archaeon's writer refuses reuse in Python
(6fc3ea619). This seat's writer did not, and a SELECT-then-INSERT in either
writer cannot hold under a race. 005 puts the invariant where both meet it.

  POSITIVE   one new csid, one row -> enqueued, one member, and downstream
             (the consumer's own tick, bind spied) alternatives == 0.
  REFUSAL    a second enqueue naming the same csid -> CandidateSetReused,
             typed, before any write: counts and membership unchanged; the
             CLI wrapper exits 4 with REFUSED on stderr.
  CHEAT      (a) the legal atomic shape -- N rows in ONE transaction, which
             is Archaeon's submit -- still lands and the detector sees N
             members / N-1 alternatives, so a 0 above is a measurement;
             (b) the same cross-transaction append with the trigger DISABLED
             lands, so the trigger is what stops it (the guard's absence is
             detectable, not silent).
  RACE       two connections race to register the same csid; exactly one
             lands, the other is refused by the database (SQLSTATE VIV01),
             and the refused transaction leaves nothing behind.
  ARCHAEON   Archaeon's own multi-candidate submit (one transaction) is
             still legal under the trigger.
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path

import psycopg2
import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
REPO = VIVARIUM.parent
for p in (str(VIVARIUM), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

from conftest import make_spec                                     # noqa: E402
from test_loop import FakeRunner                                   # noqa: E402
from viv import cli as _cli                                        # noqa: E402
from viv import db as _db                                          # noqa: E402
from viv import loop as _loop                                      # noqa: E402
from viv import queue as _q                                        # noqa: E402

BITS = "1010" * 6


def _enq(conn, schema, csid, seed, status="queued"):
    return _q.enqueue(conn, created_by="t", source_reason="csid test",
                      experiment_spec=make_spec(BITS, seed_root=seed,
                                                kind="evaluate_bitstring"),
                      candidate_set_id=csid, status=status, schema=schema)


@pytest.fixture
def bind_spy(monkeypatch):
    calls = []

    def fake_bind(client, *, candidate_set_id, members, selected_row,
                  selected_exp_id, world_id, log=lambda *_a: None):
        alts = [m for m in members
                if str(m["experiment_id"]) != str(selected_row["experiment_id"])]
        calls.append({"members": len(members), "alternatives": len(alts)})
        return {"family_id": "fam_spy", "complete": True, "errors": [],
                "alternatives": [], "alternatives_recorded": len(alts),
                "selection_visible": True, "candidate_set_id": candidate_set_id}

    monkeypatch.setattr(_loop._selection, "bind", fake_bind)
    return calls


def _tick(conn, schema):
    runner = FakeRunner()
    runner.c = object()
    v = _loop.Vivarium(worker_id="csid-test", schema=schema, runner=runner,
                       pew_client=None, log=lambda *_a: None)
    return v.tick(conn)


# ------------------------------------------------------------------ POSITIVE
def test_positive_one_new_csid_one_row_zero_alternatives(conn, schema, bind_spy):
    csid = "cs-new-" + schema[-8:]
    eid = _enq(conn, schema, csid, 9001)
    conn.commit()
    assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 1
    report = _tick(conn, schema)
    assert report.outcome == _loop.EXECUTED and str(report.experiment_id) == str(eid)
    assert bind_spy == [{"members": 1, "alternatives": 0}]
    assert _q.get(conn, eid, schema=schema)["result_summary"]["selection"]["alternatives"] == []


# ------------------------------------------------------------------- REFUSAL
def test_refusal_second_enqueue_with_same_csid_is_typed_and_writes_nothing(
        conn, schema):
    csid = "cs-reuse-" + schema[-8:]
    _enq(conn, schema, csid, 9002)
    conn.commit()
    before_counts = _q.counts(conn, schema=schema)
    before_members = [str(m["experiment_id"]) for m in
                      _q.candidate_set_members(conn, csid, schema=schema)]
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM %s.research_experiment_events" % schema)
        before_events = cur.fetchone()[0]

    with pytest.raises(_q.CandidateSetReused) as ei:
        _enq(conn, schema, csid, 9003)
    conn.rollback()
    assert ei.value.candidate_set_id == csid and ei.value.prior == 1

    assert _q.counts(conn, schema=schema) == before_counts
    assert [str(m["experiment_id"]) for m in
            _q.candidate_set_members(conn, csid, schema=schema)] == before_members
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM %s.research_experiment_events" % schema)
        assert cur.fetchone()[0] == before_events, "the refusal wrote an event"


def test_refusal_also_applies_to_a_cancelled_member(conn, schema):
    """Appending an unchosen member is still appending."""
    csid = "cs-reuse-cancelled-" + schema[-8:]
    _enq(conn, schema, csid, 9004)
    conn.commit()
    with pytest.raises(_q.CandidateSetReused):
        _enq(conn, schema, csid, 9005, status="cancelled")
    conn.rollback()


def test_refusal_through_the_cli_wrapper_exits_4(conn, schema, tmp_path, capsys):
    csid = "cs-cli-" + schema[-8:]
    _enq(conn, schema, csid, 9006)
    conn.commit()
    spec_path = tmp_path / "spec.json"
    import json
    spec_path.write_text(json.dumps(make_spec(BITS, seed_root=9007,
                                              kind="evaluate_bitstring")),
                         encoding="utf-8")
    rc = _cli.main(["--schema", schema, "enqueue", str(spec_path), "--by", "t",
                    "--reason", "cli", "--candidate-set", csid])
    err = capsys.readouterr().err
    assert rc == 4, err
    assert "REFUSED" in err and csid in err
    assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 1


# --------------------------------------------------------------------- CHEAT
def test_cheat_the_legal_atomic_set_lands_and_the_detector_sees_members(
        conn, schema, bind_spy):
    """N members written in ONE transaction is the real candidate-set shape
    (Archaeon's submit). It must still be legal, and the same spy that read 0
    above must read N-1 here -- otherwise the 0 measured nothing."""
    csid = "cs-atomic-" + schema[-8:]
    ids = [_enq(conn, schema, csid, 9100 + i,
                status="queued" if i == 0 else "cancelled") for i in range(4)]
    conn.commit()                                   # one transaction, four rows
    assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 4
    report = _tick(conn, schema)
    assert report.outcome == _loop.EXECUTED and str(report.experiment_id) == ids[0]
    assert bind_spy[-1] == {"members": 4, "alternatives": 3}


def test_cheat_with_the_trigger_disabled_the_append_lands(conn, schema):
    """The guard's absence is detectable: disable the trigger and the same
    cross-transaction append that 005 refuses goes through (the Python
    pre-check is bypassed with a raw INSERT, as a foreign writer might).
    Re-enabled afterwards; the test schema is throwaway either way."""
    csid = "cs-nogurad-" + schema[-8:]
    _enq(conn, schema, csid, 9200)
    conn.commit()
    q = "%s.research_experiment_queue" % schema
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE %s DISABLE TRIGGER trg_candidate_set_append_refused" % q)
        conn.commit()
        try:
            spec = make_spec(BITS, seed_root=9201, kind="evaluate_bitstring")
            import json
            cur.execute("INSERT INTO %s (created_by, source_reason, source_evidence, "
                        "experiment_spec, spec_hash, status, candidate_set_id) "
                        "VALUES ('raw','cheat','{}'::jsonb, %%s::jsonb, %%s, 'queued', %%s)" % q,
                        (json.dumps(spec), "sha256:" + "0" * 64, csid))
            conn.commit()
            assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 2, \
                "with the trigger off the append should have landed"
        finally:
            cur.execute("ALTER TABLE %s ENABLE TRIGGER trg_candidate_set_append_refused" % q)
            conn.commit()
    # and with the trigger back on, the same raw append is refused by SQLSTATE
    with pytest.raises(psycopg2.Error) as ei, conn.cursor() as cur:
        cur.execute("INSERT INTO %s (created_by, source_reason, source_evidence, "
                    "experiment_spec, spec_hash, status, candidate_set_id) "
                    "VALUES ('raw','cheat','{}'::jsonb, %%s::jsonb, %%s, 'queued', %%s)" % q,
                    (json.dumps(make_spec(BITS, seed_root=9202, kind="evaluate_bitstring")),
                     "sha256:" + "1" * 64, csid))
    conn.rollback()
    assert ei.value.pgcode == _q.CandidateSetReused.SQLSTATE
    assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 2


# ---------------------------------------------------------------------- RACE
def test_race_two_connections_same_csid_exactly_one_lands(schema):
    """Two writers, two connections, one csid, released together. The advisory
    lock in the trigger serialises them; the loser is refused by the database
    (its own Python pre-check ran before the winner committed and saw 0)."""
    csid = "cs-race-" + schema[-8:]
    barrier = threading.Barrier(2)
    results = {}

    def writer(name, seed):
        conn = _db.connect()
        try:
            # Do the pre-check ourselves BEFORE the barrier, so both writers
            # have already decided the set is unused when they insert: the
            # race the trigger must catch.
            assert _q.candidate_set_committed_rows(conn, csid, schema=schema) == 0
            barrier.wait(timeout=30)
            with conn.cursor() as cur:
                import json
                cur.execute(
                    "INSERT INTO %s.research_experiment_queue (created_by, "
                    "source_reason, source_evidence, experiment_spec, spec_hash, "
                    "status, candidate_set_id) VALUES ('race','race','{}'::jsonb, "
                    "%%s::jsonb, %%s, 'queued', %%s) RETURNING experiment_id" % schema,
                    (json.dumps(make_spec(BITS, seed_root=seed, kind="evaluate_bitstring")),
                     "sha256:%064x" % seed, csid))
                eid = cur.fetchone()[0]
            # hold the transaction open briefly so the other writer must wait
            # on the advisory lock rather than merely arriving later
            import time
            time.sleep(0.5)
            conn.commit()
            results[name] = ("LANDED", str(eid))
        except psycopg2.Error as exc:
            conn.rollback()
            results[name] = ("REFUSED", exc.pgcode)
        finally:
            conn.close()

    t1 = threading.Thread(target=writer, args=("a", 9301))
    t2 = threading.Thread(target=writer, args=("b", 9302))
    t1.start(); t2.start(); t1.join(60); t2.join(60)

    outcomes = sorted(v[0] for v in results.values())
    assert outcomes == ["LANDED", "REFUSED"], results
    refused = [v for v in results.values() if v[0] == "REFUSED"][0]
    assert refused[1] == _q.CandidateSetReused.SQLSTATE
    check = _db.connect()
    try:
        members = _q.candidate_set_members(check, csid, schema=schema)
        assert len(members) == 1
        with check.cursor() as cur:
            cur.execute("SELECT count(*) FROM %s.research_experiment_queue "
                        "WHERE created_by='race'" % schema)
            assert cur.fetchone()[0] == 1, "the refused row partially landed"
    finally:
        check.close()


# ------------------------------------------------------------------- ARCHAEON
def test_archaeons_multi_candidate_submit_is_still_legal(conn, schema, monkeypatch):
    monkeypatch.setenv("ARCHAEON_CONFORMANCE_MODE", "off")
    from archaeon import vivqueue as vq                            # noqa: PLC0415
    cands = [vq.make_candidate(make_spec(BITS, seed_root=9400 + i,
                                         kind="evaluate_bitstring"),
                               source_evidence={"policy_version": "t", "template_id": "t"})
             for i in range(3)]
    res = vq.submit(conn, candidates=cands, selected_index=1, source_reason="human")
    assert res["registered"] == 3 and len(res["cancelled_experiment_ids"]) == 2
    csid = res["candidate_set_id"]
    assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 3
    # and its own append is refused by the database too, not only by its check
    with pytest.raises(vq.CandidateSetReused):
        vq.submit(conn, candidates=cands[:1], selected_index=0,
                  source_reason="human", candidate_set_id=csid)
    conn.rollback()
