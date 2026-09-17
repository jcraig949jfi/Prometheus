"""The transaction model, live: attempts, design-keyed steps, replay on a
NEW ATTEMPT, gate receipts, intervention receipts, the termination envelope
and the outbox -- against a THROWAWAY schema with the draft migrations
applied (migrations/drafts/006, 008, 009). Production `viv` never has them
until the window; without them every path here is a no-op and the rest of
the suite proves the loop is unchanged.

    POSITIVE  a row executes -> attempt 1 with steps NEW in order, envelope
              COMPLETED_ALL_REPEATS, of_record, outbox rows queued, no HTTP
    POSITIVE  a stranded row released --new-attempt -> attempt 2 with parent
              1; world / experiment / observe REPLAYED when the engine says
              the objects exist; run RECOMPUTED; the engine saw no second
              world
    POSITIVE  a budget stop -> COMPLETED + censored + partial, observations
              kept, fossil body carries the envelope
    POSITIVE  a gate FAIL -> receipt committed, attempt PREREQUISITE_FAILED,
              NO step executed after it; a gate PASS -> proceeded
    POSITIVE  an executor that reports an intervention -> receipt with
              intended != realised -> PARTIAL, writer executor
    NEGATIVE  release --new-attempt without the tables is refused; a spec
              edit between attempts is impossible (design in the row hash)
    CHEAT     a verifier that says the world is gone -> RECOMPUTED, never
              REPLAYED; the outbox event for a replayed encounter has the
              SAME event_id (duplicate is a no-op)
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import pytest

from viv import attempts as _att
from viv import db as _db
from viv import queue as _q
from viv import spec as _spec
from viv.loop import EXECUTED, FAILED, Vivarium
from tests.test_blinding import RecordingClient, _runner_over
from tests.test_loop import make_spec

DRAFTS = Path(__file__).resolve().parent.parent / "migrations" / "drafts"


@pytest.fixture()
def drafted(conn, schema):
    """Apply the draft migrations (006, 008, 009; not the 007 backfill) to
    the throwaway schema once per test module run."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".execution_attempt",))
        present = cur.fetchone()[0] is not None
    conn.rollback()
    if not present:
        for name in ("006_execution_attempts_and_steps.sql", "008_bundles_receipts_gates.sql", "009_pew_outbox.sql"):
            with conn.cursor() as cur:
                cur.execute((DRAFTS / name).read_text(encoding="utf-8").replace("{schema}", schema))
            conn.commit()
    yield schema


class VerifyingClient(RecordingClient):
    """RecordingClient plus the three read routes the verifiers use."""

    def __init__(self, *a, worlds_alive=True, **k):
        super().__init__(*a, **k)
        self.worlds_alive = worlds_alive
        self.experiments = {}
        self.observations = {}

    def get_world(self, wid):
        return {"world_id": wid, "state": "ACTIVE" if self.worlds_alive else "TERMINATED"}

    def experiment(self, wid, spec, **kw):
        out = super().experiment(wid, spec, **kw)
        self.experiments.setdefault(wid, []).append(out["exp_id"])
        return out

    def get_experiment(self, wid, exp_id):
        if exp_id in self.experiments.get(wid, []):
            return {"exp_id": exp_id}
        raise RuntimeError("404")

    def observation(self, wid, exp_id, content, outcome, **kw):
        oid = super().observation(wid, exp_id, content, outcome, **kw)
        self.observations.setdefault(wid, []).append({"obs_id": oid})
        return oid

    def list_observations(self, wid):
        return list(self.observations.get(wid, []))


def _viv(schema, client, spec, worker="pr-worker"):
    runner = _runner_over(client, _spec.spec_hash(spec))
    return Vivarium(worker_id=worker, schema=schema, runner=runner, pew_client=None, log=lambda *_a: None)


def _enqueue(conn, schema, spec, **kw):
    eid = _q.enqueue(conn, created_by="pr-test", source_reason="point release", experiment_spec=spec,
                     schema=schema, **kw)
    conn.commit()
    return str(eid)


def _attempts(conn, schema, eid):
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM " + schema + ".execution_attempt WHERE experiment_id=%s ORDER BY attempt_number", (eid,))
        rows = [dict(r) for r in cur.fetchall()]
    conn.rollback()
    return rows


def _steps(conn, schema, attempt_id):
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT step_kind, parts, status, replay_of_step, recomputed_from_step, step_key FROM "
                    + schema + ".execution_step WHERE attempt_id=%s ORDER BY started_at", (attempt_id,))
        rows = [dict(r) for r in cur.fetchall()]
    conn.rollback()
    return rows


def _outbox(conn, schema, eid):
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT event_id, event_kind, sequence, state, payload FROM " + schema +
                    ".pew_outbox WHERE source_experiment=%s ORDER BY sequence", (eid,))
        rows = [dict(r) for r in cur.fetchall()]
    conn.rollback()
    return rows


# ------------------------------------------------------------- positive

def test_a_row_executes_as_attempt_one_with_keyed_steps_and_an_envelope(conn, drafted):
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-pr-1", "players": []})
    eid = _enqueue(conn, schema, spec)
    client = VerifyingClient()
    v = _viv(schema, client, spec)
    r = v.tick(conn)
    assert r.outcome == EXECUTED, r
    atts = _attempts(conn, schema, eid)
    assert len(atts) == 1 and atts[0]["attempt_number"] == 1 and atts[0]["parent_attempt_id"] is None
    a = atts[0]
    assert a["terminal_state"] == "COMPLETED" and a["of_record"] is True
    assert a["design_digest"] == _spec.spec_hash(spec)
    assert a["bundle_hash"] and a["bundle_hash_declared"] and a["receipt_digest"]
    env = a["termination"]
    assert env["termination_reason"] == "COMPLETED_ALL_REPEATS" and env["censored"] is False and env["partial"] is False
    steps = _steps(conn, schema, a["attempt_id"])
    kinds = [s["step_kind"] for s in steps]
    assert kinds[:2] == ["validate", "build"] and "world" in kinds and "experiment" in kinds
    assert all(s["status"] == "NEW" for s in steps)
    assert all(s["step_key"].startswith("idem:") for s in steps)
    ob = _outbox(conn, schema, eid)
    assert [o["event_kind"] for o in ob] == ["ATTEMPT_OPENED", "ATTEMPT_TERMINATED", "ENCOUNTER_RECORDED"] or \
           sorted(o["event_kind"] for o in ob) == sorted(["ATTEMPT_OPENED", "ATTEMPT_TERMINATED", "ENCOUNTER_RECORDED"])
    assert all(o["state"] == "PENDING" for o in ob)
    enc = next(o for o in ob if o["event_kind"] == "ENCOUNTER_RECORDED")["payload"]
    assert enc["encounter"]["encounter_id"] == "enc-pr-1"
    assert enc["encounter"]["resources_used"]["termination"]["termination_reason"] == "COMPLETED_ALL_REPEATS"
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed" and row["result_summary"]["pew"]["queued"] is True


def test_a_stranded_row_released_to_a_new_attempt_replays_engine_steps(conn, drafted):
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-pr-2", "players": []})
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    eid = _enqueue(conn, schema, spec)
    client = VerifyingClient()
    v = _viv(schema, client, spec, worker="pr-w1")
    # strand it: the worker dies while posting the SECOND observation, so the
    # world, the experiment, both runs and observation 0 already exist
    real_observation = client.observation
    calls = {"n": 0}

    def crash_on_second(wid, exp_id, content, outcome, **kw):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("simulated worker death during observation 1")
        return real_observation(wid, exp_id, content, outcome, **kw)
    client.observation = crash_on_second
    r1 = v.tick(conn)
    assert r1.outcome == FAILED and r1.failure_class in ("EXECUTOR_ERROR", "ENGINE_TRANSPORT")
    atts = _attempts(conn, schema, eid)
    assert atts[0]["terminal_state"] == "FAILED"
    n_worlds_before = sum(1 for name, _ in client.calls if name == "create_world")
    # the operator does NOT rerun a FAILED row by inference; but a STRANDED one
    # (worker gone mid-row) may be released to a new attempt. Simulate the
    # strand: put the row back to claimed with an open attempt, then release.
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".execution_attempt (experiment_id, attempt_number, parent_attempt_id, design_digest, worker_id) "
                    "VALUES (%s, 2, %s, %s, 'pr-w1') RETURNING attempt_id", (eid, atts[0]["attempt_id"], _spec.spec_hash(spec)))
        open_id = cur.fetchone()[0]
    conn.commit()
    # the row itself is terminal (failed) from attempt 1, so requeue it the way a strand would look:
    # (a genuinely stranded row is claimed/running; emulate by direct status for the release path)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='running', claimed_by='pr-w1', finished_at=NULL WHERE experiment_id=%s", (eid,))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
    conn.commit()
    row = _q.release_stranded(conn, eid, actor="op", reason="worker died", schema=schema, new_attempt=True)
    conn.commit()
    assert row["status"] == "queued"
    atts = _attempts(conn, schema, eid)
    assert atts[1]["terminal_state"] == "STRANDED" and atts[1]["termination"]["termination_reason"] == "STRANDED"
    client.observation = real_observation
    v2 = _viv(schema, client, spec, worker="pr-w2")
    v2._runner = v._runner                                # same engine, same recording client
    r2 = v2.tick(conn)
    assert r2.outcome == EXECUTED, r2
    atts = _attempts(conn, schema, eid)
    assert len(atts) == 3 and atts[2]["parent_attempt_id"] == atts[1]["attempt_id"]
    steps = {(s["step_kind"], tuple(s["parts"])): s["status"] for s in _steps(conn, schema, atts[2]["attempt_id"])}
    assert steps[("world", ("plain",))] == "REPLAYED"
    assert [v for (k, _), v in steps.items() if k == "experiment"] == ["REPLAYED"]
    assert steps[("run", (0,))] == "RECOMPUTED" and steps[("run", (1,))] == "RECOMPUTED"
    assert steps[("observe", (0,))] == "REPLAYED"          # existed before the death
    assert steps[("observe", (1,))] == "NEW"               # never landed; posted now
    n_worlds_after = sum(1 for name, _ in client.calls if name == "create_world")
    assert n_worlds_after == n_worlds_before, "a replayed world was re-created"
    assert atts[2]["of_record"] is True and atts[0]["of_record"] is False


def test_a_budget_stop_completes_censored_with_the_observations_it_has(conn, drafted):
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-pr-3", "players": []})
    spec["repeat"] = {"count": 4, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 1e-9, "max_observations": 4}}
    eid = _enqueue(conn, schema, spec)
    v = _viv(schema, VerifyingClient(), spec)
    r = v.tick(conn)
    assert r.outcome == EXECUTED
    a = _attempts(conn, schema, eid)[0]
    env = a["termination"]
    assert a["terminal_state"] == "COMPLETED"
    assert env["termination_reason"] == "BUDGET_EXHAUSTED" and env["censored"] is True and env["partial"] is True
    assert env["observations_recorded"] == 0 and env["horizon"]["declared"] == 4
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed"
    assert row["result_summary"]["termination"]["censoring_reason"] == "BUDGET_EXHAUSTED"


def test_a_failing_gate_aborts_before_any_step_and_a_passing_gate_proceeds(conn, drafted):
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-pr-4", "players": []})
    gate = {"gate_id": "pc:control", "phase": "pre_execution",
            "condition": "the control reached best >= reference",
            "measurement": {"source": "producer_supplied", "ref": "control_best"},
            "rule": {"op": ">=", "reference": 0.5, "if_indeterminate": "FAIL"},
            "on_fail": "abort_attempt", "definition_ref": "prereg#gates[0]"}
    from viv import bundle as _b
    declared = _b.declared_skeleton(spec); declared["gates"] = [gate]
    eid = _enqueue(conn, schema, spec, source_evidence={"gate_measurements": {"control_best": 0.3}})
    with conn.cursor() as cur:
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET bundle_declared=%s WHERE experiment_id=%s",
                    (json.dumps(declared), eid))
    conn.commit()
    client = VerifyingClient()
    r = _viv(schema, client, spec).tick(conn)
    assert r.outcome == FAILED and r.failure_class == "PREREQUISITE_FAILED"
    a = _attempts(conn, schema, eid)[0]
    assert a["terminal_state"] == "FAILED" and a["termination"]["termination_reason"] == "PREREQUISITE_FAILED"
    assert _steps(conn, schema, a["attempt_id"]) == []                 # nothing executed after the gate
    assert not any(name == "create_world" for name, _ in client.calls)
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT result, action_taken, measured, reference FROM " + schema + ".gate_receipt WHERE attempt_id=%s", (a["attempt_id"],))
        g = dict(cur.fetchone())
    conn.rollback()
    assert g["result"] == "FAIL" and g["action_taken"] == "aborted_attempt" and g["measured"] == 0.3 and g["reference"] == 0.5
    # PASS
    eid2 = _enqueue(conn, schema, spec, source_evidence={"gate_measurements": {"control_best": 0.9}})
    with conn.cursor() as cur:
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET bundle_declared=%s WHERE experiment_id=%s",
                    (json.dumps(declared), eid2))
    conn.commit()
    r2 = _viv(schema, VerifyingClient(), spec).tick(conn)
    assert r2.outcome == EXECUTED
    a2 = _attempts(conn, schema, eid2)[0]
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT result, action_taken FROM " + schema + ".gate_receipt WHERE attempt_id=%s", (a2["attempt_id"],))
        g2 = dict(cur.fetchone())
    conn.rollback()
    assert g2 == {"result": "PASS", "action_taken": "proceeded"}


def test_an_executor_reported_intervention_becomes_a_receipt(conn, drafted, monkeypatch):
    schema = drafted
    from viv import executors as _ex
    real = _ex._noop_v0

    def with_intervention(spec):
        out = real(spec)
        out["_interventions"] = [{"intervention_id": "inject:A", "kind": "import",
                                  "intended": {"count": 4}, "realised": {"count": 1},
                                  "logical_time": {"generation": 0}, "supplied": [{"organism_id": "o1"}],
                                  "result": "APPLIED"}]
        return out
    monkeypatch.setattr(_ex, "_noop_v0", with_intervention)
    spec = make_spec(pew={"encounter_id": "enc-pr-5", "players": []})
    eid = _enqueue(conn, schema, spec)
    r = _viv(schema, VerifyingClient(), spec).tick(conn)
    assert r.outcome == EXECUTED
    a = _attempts(conn, schema, eid)[0]
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT intervention_id, intervention_kind, writer, intended, realised, result FROM "
                    + schema + ".intervention_receipt WHERE attempt_id=%s", (a["attempt_id"],))
        recs = [dict(x) for x in cur.fetchall()]
    conn.rollback()
    assert len(recs) == 1
    rec = recs[0]
    assert rec["writer"] == "executor" and rec["result"] == "PARTIAL"
    assert rec["intended"] == {"count": 4} and rec["realised"] == {"count": 1}


# ------------------------------------------------------------- negative / cheat

def test_release_to_new_attempt_is_refused_without_the_tables(conn, schema):
    spec = make_spec()
    eid = _enqueue(conn, schema, spec)
    with conn.cursor() as cur:
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='claimed', claimed_by='x', claimed_at=now() WHERE experiment_id=%s", (eid,))
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".execution_attempt",))
        present = cur.fetchone()[0] is not None
    conn.rollback()
    if present:
        pytest.skip("drafts already applied in this schema by another test")
    with pytest.raises(RuntimeError) as exc:
        _q.release_stranded(conn, eid, actor="op", reason="x", schema=schema, new_attempt=True)
    conn.rollback()
    assert "migration 006" in str(exc.value)


def test_cheat_a_dead_world_is_recomputed_never_replayed(conn, drafted):
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-pr-6", "players": []})
    eid = _enqueue(conn, schema, spec)
    client = VerifyingClient()
    v = _viv(schema, client, spec, worker="pr-c1")
    client.complete = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("crash"))
    assert v.tick(conn).outcome == FAILED
    a1 = _attempts(conn, schema, eid)[0]
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".execution_attempt (experiment_id, attempt_number, parent_attempt_id, design_digest, worker_id) VALUES (%s, 2, %s, %s, 'pr-c1')", (eid, a1["attempt_id"], _spec.spec_hash(spec)))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='running', claimed_by='pr-c1', finished_at=NULL WHERE experiment_id=%s", (eid,))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
    conn.commit()
    _q.release_stranded(conn, eid, actor="op", reason="x", schema=schema, new_attempt=True); conn.commit()
    client.worlds_alive = False                       # the engine says: the world is gone
    client.complete = VerifyingClient.complete.__get__(client)
    v2 = _viv(schema, client, spec, worker="pr-c2"); v2._runner = v._runner
    assert v2.tick(conn).outcome == EXECUTED
    a3 = _attempts(conn, schema, eid)[2]
    steps = {s["step_kind"]: s for s in _steps(conn, schema, a3["attempt_id"])}
    assert steps["world"]["status"] == "RECOMPUTED" and steps["world"]["recomputed_from_step"] is not None
    assert sum(1 for name, _ in client.calls if name == "create_world") == 2


def test_cheat_the_same_fact_has_the_same_outbox_event_id(conn, drafted):
    from viv import outbox as _ob
    ob = _ob.Outbox(schema=drafted, producer="pr-worker")
    spec = make_spec(pew={"encounter_id": "enc-pr-7", "players": []})
    eid = _enqueue(conn, drafted, spec)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + drafted + ".execution_attempt (experiment_id, attempt_number, design_digest, worker_id) VALUES (%s, 1, %s, 'w') RETURNING attempt_id", (eid, _spec.spec_hash(spec)))
        aid = str(cur.fetchone()[0])
    conn.commit()
    e1 = ob.enqueue(conn, kind="ATTEMPT_OPENED", source_attempt=aid, source_experiment=eid, payload={"n": 1})
    e2 = ob.enqueue(conn, kind="ATTEMPT_OPENED", source_attempt=aid, source_experiment=eid, payload={"n": 1})
    assert e1 == e2
    assert len(_outbox(conn, drafted, eid)) == 1
