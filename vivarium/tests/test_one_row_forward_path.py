"""One Archaeon-shaped row through queue -> claim -> execute -> result, and
the end of the alternative burst.

THE QUESTION (operator, 2026-09-11 evening): after Archaeon's candidate-set
fix (6fc3ea619), does ONE newly submitted Archaeon row traverse the path
without registering hundreds of phantom "alternative" experiments in the
engine? On 09-10/11 a campaign reused one candidate_set_id across 256
submits, and viv/selection.py -- doing what the contract said -- registered
~255 UNCOMMITTED experiments per row: 85,727 phantoms in this seat's worlds.

Three tests, in the test schema, with Archaeon's REAL writer
(archaeon.vivqueue.submit) and Vivarium's real claim/tick; the engine is a
FakeRunner and the selection binding is spied, so nothing reaches SFE.

  POSITIVE  one Archaeon row -> claimed by the consumer's own claim
            statement -> EXECUTED -> bind sees a set of ONE, 0 alternatives.
  FORWARD FIX  the old shape (reusing the csid on a second submit) is
            REFUSED before anything is written (CandidateSetReused).
  CHEAT   three rows sharing one csid through Vivarium's OWN enqueue (which
            has no such refusal) -> the spy sees 2 alternatives. This is
            what makes the 0 above a measurement: the channel can see a
            burst when one exists. It also records a fact: the forward fix
            lives in Archaeon's writer only; viv.cli enqueue would still
            reproduce the burst if handed a reused csid.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
REPO = VIVARIUM.parent
for p in (str(VIVARIUM), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

from conftest import make_spec                                     # noqa: E402
from test_loop import FakeRunner                                   # noqa: E402
from viv import loop as _loop                                      # noqa: E402
from viv import queue as _q                                        # noqa: E402

BITS = "0110" * 6


def _archaeon_candidate(vq, seed):
    """Built by Archaeon's own make_candidate, as its producers do."""
    return vq.make_candidate(
        make_spec(BITS, seed_root=seed, kind="evaluate_bitstring"),
        source_evidence=vq.campaign_set_key(
            {"policy_version": "test.forward_path.v0",
             "template_id": "bitstring.uniform.v0"}, "cs-test-forward-path"))


@pytest.fixture
def archaeon_writer(monkeypatch):
    # Archaeon's gate honours this ONLY outside the production schema
    # (archaeon/conformance.py evaluate); conftest already points VIV_SCHEMA
    # at a throwaway schema. Archaeon's writer resolves the schema through
    # Vivarium's own resolver, so it lands in the same test schema.
    monkeypatch.setenv("ARCHAEON_CONFORMANCE_MODE", "off")
    from archaeon import vivqueue as vq                            # noqa: PLC0415
    return vq


@pytest.fixture
def bind_spy(monkeypatch):
    calls = []

    def fake_bind(client, *, candidate_set_id, members, selected_row,
                  selected_exp_id, world_id, log=lambda *_a: None):
        alts = [m for m in members
                if str(m["experiment_id"]) != str(selected_row["experiment_id"])]
        rec = {"candidate_set_id": candidate_set_id, "members": len(members),
               "alternatives": len(alts), "selected": selected_exp_id}
        calls.append(rec)
        return {**rec, "family_id": "fam_spy", "complete": True, "errors": [],
                "alternatives_recorded": len(alts), "selection_visible": True}

    monkeypatch.setattr(_loop._selection, "bind", fake_bind)
    return calls


def _consumer(schema, runner):
    v = _loop.Vivarium(worker_id="viv-forward-test", schema=schema,
                       runner=runner, pew_client=None, log=lambda *_a: None)
    # bind_selection reaches for runner().c; the spy never touches it, but
    # the attribute must exist so the real code path is the one exercised.
    runner.c = object()
    return v


def test_one_archaeon_row_traverses_with_zero_alternatives(conn, schema,
                                                            archaeon_writer,
                                                            bind_spy):
    vq = archaeon_writer
    res = vq.submit(conn, candidates=[_archaeon_candidate(vq, 7001)],
                    selected_index=0, source_reason="human",
                    created_by="archaeon")
    eid = res["selected_experiment_id"]
    assert res["registered"] == 1 and res["cancelled_experiment_ids"] == []
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "queued" and row["candidate_set_id"]
    assert _q.next_eligible(conn, schema=schema)["experiment_id"] == row["experiment_id"]

    runner = FakeRunner()
    v = _consumer(schema, runner)
    report = v.tick(conn)                       # the consumer's own claim + run
    assert report.outcome == _loop.EXECUTED, report.as_dict()
    assert str(report.experiment_id) == str(eid)
    assert runner.runs == [str(eid)]
    after = _q.get(conn, eid, schema=schema)
    assert after["status"] == "completed"
    assert after["sfe_experiment_id"] == report.sfe_experiment_id
    assert after["result_summary"]["selection"]["alternatives"] == 0

    assert len(bind_spy) == 1
    assert bind_spy[0]["members"] == 1 and bind_spy[0]["alternatives"] == 0, \
        "a single Archaeon row still registers alternatives"
    assert _q.counts(conn, schema=schema).get("queued", 0) == 0


def test_the_old_burst_shape_is_refused_before_anything_is_written(
        conn, schema, archaeon_writer):
    vq = archaeon_writer
    first = vq.submit(conn, candidates=[_archaeon_candidate(vq, 7002)],
                      selected_index=0, source_reason="human")
    csid = first["candidate_set_id"]
    before = _q.counts(conn, schema=schema)
    with pytest.raises(vq.CandidateSetReused):
        vq.submit(conn, candidates=[_archaeon_candidate(vq, 7003)],
                  selected_index=0, source_reason="human",
                  candidate_set_id=csid)
    conn.rollback()
    assert _q.counts(conn, schema=schema) == before
    assert len(_q.candidate_set_members(conn, csid, schema=schema)) == 1


def test_cheat_a_shared_csid_through_vivariums_own_enqueue_still_bursts(
        conn, schema, bind_spy):
    """The channel sees a burst when there is one -- and Vivarium's own
    writer does not refuse the shape. Recorded, not fixed here."""
    csid = "cs-test-reused-shape"
    ids = []
    for i in range(3):
        ids.append(_q.enqueue(conn, created_by="t", source_reason="cheat",
                              experiment_spec=make_spec(BITS, seed_root=7100 + i,
                                                        kind="evaluate_bitstring"),
                              priority=100 + i, candidate_set_id=csid,
                              schema=schema))
    conn.commit()
    runner = FakeRunner()
    v = _consumer(schema, runner)
    report = v.tick(conn)
    assert report.outcome == _loop.EXECUTED
    assert bind_spy[-1]["members"] == 3 and bind_spy[-1]["alternatives"] == 2
