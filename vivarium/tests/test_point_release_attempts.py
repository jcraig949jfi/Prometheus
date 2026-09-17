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
        # schema 9's shape (D8 cursors): a page object, never a bare list --
        # the s14 canary D found the verifiers iterating the dict's keys
        return {"observations": list(self.observations.get(wid, [])), "next_after_seq": None, "truncated": False}

    def list_experiments(self, wid):
        return {"experiments": [{"exp_id": e, "spec_hash": None} for e in self.experiments.get(wid, [])],
                "next_after_seq": None, "truncated": False}

    def events(self, wid, limit=100):
        # the base double has only OBSERVATION_RECORDED events; a completed
        # attempt with ZERO observations (budget-censored) and a boundary-
        # crossing failure both anchor on EXPERIMENT_COMMITTED, which a real
        # engine always has once experiment() returned
        base = super().events(wid, limit=limit)
        return [{"event_type": "EXPERIMENT_COMMITTED", "event_id": "evt_exp_fixed",
                 "entry_hash": "sha256:" + "b" * 64, "event_seq": 5,
                 "refs": {"exp_id": "exp_fixed"}}] + base


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
        cur.execute("SELECT step_kind, parts, status, replay_of_step, recomputed_from_step, step_key, result FROM "
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


# ------------------------------------------------------------- s14 canary finding (2026-09-17): SESSION_MISMATCH

class SessionBoundClient(VerifyingClient):
    """The production engine binds a world to the SESSION that created it and
    answers 403 SESSION_MISMATCH to every read or write from another session,
    which is what a relaunched consumer is. Mints a distinct session (and key)
    per create_session, like the engine."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.session_key = None
        self._n = 0
        self.keys = {}                 # session_id -> key
        self.world_session = {}        # world_id -> session_id

    def create_session(self, name):
        self._n += 1
        sid, key = "ses_%d" % self._n, "key_%d" % self._n
        self.keys[sid] = key
        self.session_key = key
        self._rec("create_session", name=name)
        return sid

    def _owning(self, wid):
        sid = self.world_session.get(wid)
        if sid is None or self.keys.get(sid) != self.session_key:
            raise RuntimeError("HTTP 403: SESSION_MISMATCH this session does not own that world")

    def create_world(self, sid, name, seed_root=None):
        self._n += 1
        wid = "wld_%d" % self._n
        self.world_session[wid] = sid
        self._rec("create_world", session=sid, name=name, seed_root=seed_root)
        return {"world_id": wid}

    def get_world(self, wid):
        self._owning(wid)
        return super().get_world(wid)

    def get_experiment(self, wid, exp_id):
        self._owning(wid)
        return super().get_experiment(wid, exp_id)

    def list_observations(self, wid):
        self._owning(wid)
        return super().list_observations(wid)

    def observation(self, wid, exp_id, content, outcome, **kw):
        self._owning(wid)
        return super().observation(wid, exp_id, content, outcome, **kw)


def _strand_after_first_observation(conn, schema, spec, client, worker, session_store):
    v = _viv(schema, client, spec, worker=worker)
    v._runner.session_store = session_store
    real = client.observation
    calls = {"n": 0}

    def crash_on_second(wid, exp_id, content, outcome, **kw):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("simulated worker death during observation 1")
        return real(wid, exp_id, content, outcome, **kw)
    client.observation = crash_on_second
    eid = _enqueue(conn, schema, spec)
    r1 = v.tick(conn)
    assert r1.outcome == FAILED
    client.observation = real
    atts = _attempts(conn, schema, eid)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".execution_attempt (experiment_id, attempt_number, parent_attempt_id, design_digest, worker_id) "
                    "VALUES (%s, 2, %s, %s, %s)", (eid, atts[0]["attempt_id"], _spec.spec_hash(spec), worker))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='running', claimed_by=%s, finished_at=NULL WHERE experiment_id=%s", (worker, eid))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
    conn.commit()
    _q.release_stranded(conn, eid, actor="op", reason="worker died", schema=schema, new_attempt=True)
    conn.commit()
    return eid


def _fresh_process(schema, client, spec, worker, session_store):
    """A relaunched consumer: a NEW runner (new session on first use) over the
    same engine, with whatever session keys this host holds."""
    v = _viv(schema, client, spec, worker=worker)
    v._runner.session_store = session_store
    client.session_key = None              # the new process has no key until it opens or adopts a session
    return v


def test_a_relaunched_consumer_adopts_the_prior_worlds_session_and_replays(conn, drafted, tmp_path):
    """POSITIVE: with the predecessor's session key held on this host, attempt
    2 reads the world it did not create (REPLAYED world/experiment/observe:0)
    and no second world is minted. This is the s14 canary defect: on
    production the new process opened a new session, every verifier got 403
    SESSION_MISMATCH, the world was RECOMPUTED and attempt 1's observations
    were orphaned in a world nobody could reach."""
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-ses-1", "players": []})
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    client = SessionBoundClient()
    store = tmp_path / "sessions"
    eid = _strand_after_first_observation(conn, schema, spec, client, "ses-w1", store)
    assert (store / "ses_1.key").read_text(encoding="utf-8") == "key_1"     # persisted, host-local
    v2 = _fresh_process(schema, client, spec, "ses-w2", store)
    r2 = v2.tick(conn)
    assert r2.outcome == EXECUTED, r2
    atts = _attempts(conn, schema, eid)
    steps = {(s["step_kind"], tuple(s["parts"])): s["status"] for s in _steps(conn, schema, atts[2]["attempt_id"])}
    assert steps[("world", ("plain",))] == "REPLAYED" and steps[("observe", (0,))] == "REPLAYED" and steps[("observe", (1,))] == "NEW"
    assert sum(1 for name, _ in client.calls if name == "create_world") == 1, "a second world was minted"
    assert v2._runner._session_id == "ses_1"                                  # adopted, not a new session
    # the outbox carries the stranded attempt's termination too (the other canary finding)
    with conn.cursor() as cur:
        cur.execute("SELECT event_kind, count(*) FROM " + schema + ".pew_outbox WHERE source_experiment=%s GROUP BY 1 ORDER BY 1", (eid,))
        kinds = dict(cur.fetchall())
    conn.rollback()
    assert kinds.get("ATTEMPT_TERMINATED") == 3 and kinds.get("ATTEMPT_OPENED") == 2   # FAILED, STRANDED, COMPLETED / attempts 1 and 3


def test_negative_without_the_key_the_prior_world_is_recomputed_and_says_so(conn, drafted, tmp_path):
    """NEGATIVE: a host that does not hold the key cannot reach the world; the
    step is RECOMPUTED (typed, receipted), never silently REPLAYED from a
    world it could not verify. CHEAT: a key file for the WRONG session does
    not open the world either."""
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-ses-2", "players": []})
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    client = SessionBoundClient()
    eid = _strand_after_first_observation(conn, schema, spec, client, "ses-w1", tmp_path / "gone")
    other = tmp_path / "other-host"
    other.mkdir()
    (other / "ses_1.key").write_text("key_not_the_engine_s", encoding="utf-8")   # CHEAT: wrong key
    v2 = _fresh_process(schema, client, spec, "ses-w2", other)
    r2 = v2.tick(conn)
    assert r2.outcome == EXECUTED, r2
    atts = _attempts(conn, schema, eid)
    steps = {(s["step_kind"], tuple(s["parts"])): s["status"] for s in _steps(conn, schema, atts[2]["attempt_id"])}
    assert steps[("world", ("plain",))] == "RECOMPUTED"
    assert sum(1 for name, _ in client.calls if name == "create_world") == 2


# ------------------------------------------------------------- s14 canary finding (2026-09-17): a COMPLETED work item is not claimable

class WorkItemClient(SessionBoundClient):
    """Models the engine's ONE work item per experiment: QUEUED -> CLAIMED
    (leased) -> COMPLETED; a claim on a COMPLETED item returns None (that is
    what production answered a NEW ATTEMPT: WORK_NOT_CLAIMABLE); an expired
    lease makes it RETRYABLE (claimable again)."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.items = {}            # work_id -> dict(status, exp_id, world_id)

    def experiment(self, wid, spec, **kw):
        out = super().experiment(wid, spec, **kw)
        self.items["wrk_" + out["exp_id"]] = {"status": "QUEUED", "world_id": wid, "exp_id": out["exp_id"]}
        return out

    def claim(self, worker_id, world_id=None, lease_s=None):
        self._rec("claim", worker_id=worker_id, world_id=world_id, lease_s=lease_s)
        for work_id, it in self.items.items():
            if it["world_id"] == world_id and it["status"] in ("QUEUED", "RETRYABLE"):
                it["status"] = "CLAIMED"
                return {"work_id": work_id, "claim_id": "clm_" + work_id, "kind": "noop", "payload": {}}
        return None

    def complete(self, work_id, worker_id, claim_id, result, attestation=None):
        assert self.items[work_id]["status"] == "CLAIMED", "complete on a %s item" % self.items[work_id]["status"]
        self.items[work_id]["status"] = "COMPLETED"
        return super().complete(work_id, worker_id, claim_id, result, attestation=attestation)

    def expire_leases(self):
        for it in self.items.values():
            if it["status"] == "CLAIMED":
                it["status"] = "RETRYABLE"

    def work_attestation(self, work_id):
        it = self.items[work_id]
        self._owning(it["world_id"])
        return {"work_id": work_id, "status": it["status"], "result_hash": "sha256:x" if it["status"] == "COMPLETED" else None}


def test_a_new_attempt_after_a_completed_work_item_replays_the_claim_and_completes_nothing_twice(conn, drafted, tmp_path):
    """The production shape: the runner computes every repeat under ONE
    lease, completes the item, then posts observations; the death lands
    between observation 0 and 1. Attempt 2 must not claim (nothing is
    claimable), must not complete again, and must post the missing
    observations against the completed item."""
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-wrk-1", "players": []})
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    client = WorkItemClient()
    store = tmp_path / "sessions"
    eid = _strand_after_first_observation(conn, schema, spec, client, "wrk-w1", store)
    assert [it["status"] for it in client.items.values()] == ["COMPLETED"]
    v2 = _fresh_process(schema, client, spec, "wrk-w2", store)
    r2 = v2.tick(conn)
    assert r2.outcome == EXECUTED, r2
    atts = _attempts(conn, schema, eid)
    steps = {(s["step_kind"], tuple(s["parts"])): s["status"] for s in _steps(conn, schema, atts[2]["attempt_id"])}
    assert steps[("claim", ("plain",))] == "REPLAYED"
    assert steps[("world", ("plain",))] == "REPLAYED" and steps[("observe", (0,))] == "REPLAYED" and steps[("observe", (1,))] == "NEW"
    assert sum(1 for name, _ in client.calls if name == "complete") == 1, "the work item was completed twice"
    assert sum(1 for name, _ in client.calls if name == "claim") == 1, "a completed item was claimed again"


def test_negative_a_lease_that_expired_mid_run_is_claimed_afresh_and_completed_once(conn, drafted, tmp_path):
    """The other death: the worker dies INSIDE the repeat loop (before
    complete). The lease expires -> RETRYABLE -> attempt 2's claim is
    RECOMPUTED (a fresh claim on the same item), the runs recompute and the
    item is completed exactly once, by attempt 2."""
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-wrk-2", "players": []})
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    client = WorkItemClient()
    store = tmp_path / "sessions"
    v = _viv(schema, client, spec, worker="wrk-w1")
    v._runner.session_store = store
    real_complete = client.complete

    def die_before_complete(*a, **k):
        raise RuntimeError("simulated worker death inside the repeat loop")
    client.complete = die_before_complete
    eid = _enqueue(conn, schema, spec)
    assert v.tick(conn).outcome == FAILED
    client.complete = real_complete
    atts = _attempts(conn, schema, eid)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".execution_attempt (experiment_id, attempt_number, parent_attempt_id, design_digest, worker_id) "
                    "VALUES (%s, 2, %s, %s, 'wrk-w1')", (eid, atts[0]["attempt_id"], _spec.spec_hash(spec)))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='running', claimed_by='wrk-w1', finished_at=NULL WHERE experiment_id=%s", (eid,))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
    conn.commit()
    _q.release_stranded(conn, eid, actor="op", reason="worker died", schema=schema, new_attempt=True)
    conn.commit()
    client.expire_leases()                                # the dead attempt's lease runs out
    v2 = _fresh_process(schema, client, spec, "wrk-w2", store)
    v2._runner.lease_s = 2.0                              # keep the lease wait short in the test
    r2 = v2.tick(conn)
    assert r2.outcome == EXECUTED, r2
    atts = _attempts(conn, schema, eid)
    steps = {(s["step_kind"], tuple(s["parts"])): s["status"] for s in _steps(conn, schema, atts[2]["attempt_id"])}
    assert steps[("claim", ("plain",))] == "RECOMPUTED" and steps[("world", ("plain",))] == "REPLAYED"
    assert [it["status"] for it in client.items.values()] == ["COMPLETED"]
    assert sum(1 for name, _ in client.calls if name == "complete") == 1      # attempt 1 died before its complete was recorded; attempt 2 completed once
    assert sum(1 for name, _ in client.calls if name == "claim") == 2


# ------------------------------------------------------------- s14 canary finding D (2026-09-17): the engine committed, the step result never landed

class OriginalOnceClient(WorkItemClient):
    """The engine's rule: one ORIGINAL observation per experiment; a second
    non-replication post is 409. list_observations carries exp_id and the
    posted content (repeat_index), which is what recovery-by-content reads."""

    def observation(self, wid, exp_id, content, outcome, **kw):
        self._owning(wid)
        mine = [o for o in self.observations.get(wid, []) if o.get("exp_id") == exp_id]
        if mine and not kw.get("replication"):
            raise RuntimeError("HTTP 409: this experiment (or prediction) already has an ORIGINAL observation")
        oid = RecordingClient.observation(self, wid, exp_id, content, outcome, **kw)
        self.observations.setdefault(wid, []).append({"obs_id": oid, "exp_id": exp_id, "content": content})
        return oid


def test_a_death_between_the_engines_commit_and_the_step_result_is_recovered_by_content(conn, drafted, tmp_path):
    """POSITIVE: attempt 1's observe:0 landed on the engine but its step row
    has result NULL (the worker died in between). Attempt 2 finds it by
    (exp_id, repeat_index), REPLAYS it with the recovered obs_id, and posts
    only observe:1. NEGATIVE (the pre-fix behaviour, asserted by the double):
    re-posting observe:0 would be a 409 -- so a pass here means no re-post
    happened. CHEAT: a NULL-result step whose act is NOT on the engine is
    RECOMPUTED, never invented."""
    schema = drafted
    spec = make_spec(pew={"encounter_id": "enc-rec-1", "players": []})
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    client = OriginalOnceClient()
    store = tmp_path / "sessions"
    v = _viv(schema, client, spec, worker="rec-w1")
    v._runner.session_store = store
    real = client.observation

    def commit_then_die(wid, exp_id, content, outcome, **kw):
        real(wid, exp_id, content, outcome, **kw)         # the engine has it ...
        raise RuntimeError("simulated death before the step result landed")   # ... the recorder does not
    client.observation = commit_then_die
    eid = _enqueue(conn, schema, spec)
    assert v.tick(conn).outcome == FAILED
    client.observation = real
    atts = _attempts(conn, schema, eid)
    st1 = {(s["step_kind"], tuple(s["parts"])): s for s in _steps(conn, schema, atts[0]["attempt_id"])}
    assert st1[("observe", (0,))]["result"] is None                      # the gap, as production showed it
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".execution_attempt (experiment_id, attempt_number, parent_attempt_id, design_digest, worker_id) "
                    "VALUES (%s, 2, %s, %s, 'rec-w1')", (eid, atts[0]["attempt_id"], _spec.spec_hash(spec)))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='running', claimed_by='rec-w1', finished_at=NULL WHERE experiment_id=%s", (eid,))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
    conn.commit()
    _q.release_stranded(conn, eid, actor="op", reason="worker died", schema=schema, new_attempt=True)
    conn.commit()
    v2 = _fresh_process(schema, client, spec, "rec-w2", store)
    r2 = v2.tick(conn)
    assert r2.outcome == EXECUTED, r2
    atts = _attempts(conn, schema, eid)
    st2 = {(s["step_kind"], tuple(s["parts"])): s for s in _steps(conn, schema, atts[2]["attempt_id"])}
    assert st2[("observe", (0,))]["status"] == "REPLAYED" and st2[("observe", (0,))]["result"] is not None
    assert st2[("observe", (1,))]["status"] == "NEW"
    wid = st2[("world", ("plain",))]["result"]["world_id"]
    assert len(client.observations[wid]) == 2                             # exactly two on the engine, no duplicate
    # CHEAT: a NULL-result step with nothing on the engine is recomputed, not invented
    from viv.runner import SfeRunner
    assert SfeRunner._observation_present(client, wid, None, exp_id="exp_nothing", repeat_index=7) is False


# ------------------------------------------------------------- s14 canary D (2026-09-17): a 4xx is the engine's answer, not transport

def test_an_engine_4xx_after_the_commit_is_engine_rejected_not_transport(conn, drafted):
    """POSITIVE: an EngineError with a 4xx status after the commit fails the
    row ENGINE_REJECTED (termination reason EXECUTOR_ERROR), which is NOT the
    consumer's halt class -- on production the 409 was classed
    ENGINE_TRANSPORT, the consumer parked and paged Daedalus. NEGATIVE: a
    5xx stays ENGINE_TRANSPORT (the engine is unhealthy; that IS the halt
    class); a socket error stays ENGINE_TRANSPORT."""
    from sfclient import EngineError
    schema = drafted
    for status, expect in ((409, "ENGINE_REJECTED"), (503, "ENGINE_TRANSPORT")):
        spec = make_spec(hypothesis="probe %d" % status)
        eid = _enqueue(conn, schema, spec)
        client = VerifyingClient()

        def refuse(*a, _st=status, **k):
            raise EngineError(_st, {"error": "x"})
        client.observation = refuse
        r = _viv(schema, client, spec).tick(conn)
        assert r.outcome == FAILED and r.failure_class == expect, (status, r)
        atts = _attempts(conn, schema, eid)
        assert atts[0]["termination"]["termination_reason"] == ("EXECUTOR_ERROR" if expect == "ENGINE_REJECTED" else "ENGINE_TRANSPORT")
    spec = make_spec(hypothesis="probe socket")
    eid = _enqueue(conn, schema, spec)
    client = VerifyingClient()

    def drop(*a, **k):
        raise OSError("connection reset")
    client.observation = drop
    r = _viv(schema, client, spec).tick(conn)
    assert r.outcome == FAILED and r.failure_class == "ENGINE_TRANSPORT"


# ------------------------------------------------------------- Daedalus #354: Idempotency-Key = the step key on the id-minting posts

def test_the_step_key_travels_as_the_idempotency_key_when_the_client_accepts_it(conn, drafted):
    from viv import stepkey as _sk
    schema = drafted

    class KeyedClient(VerifyingClient):
        def __init__(self):
            super().__init__(); self.keys = {}

        def observation(self, wid, exp_id, content, outcome, pred_id=None, work_id=None, replication=False, idem_key=None):
            self.keys[("observe", content["repeat_index"])] = idem_key
            return super().observation(wid, exp_id, content, outcome, pred_id=pred_id, work_id=work_id, replication=replication)

        def experiment(self, wid, spec, idem_key=None, **kw):
            self.keys[("experiment", wid)] = idem_key
            return super().experiment(wid, spec, **kw)

    spec = make_spec(hypothesis="probe keys")
    spec["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                      "budget": {"max_seconds": 60, "max_observations": 2}}
    eid = _enqueue(conn, schema, spec)
    client = KeyedClient()
    assert _viv(schema, client, spec).tick(conn).outcome == EXECUTED
    design = _spec.spec_hash(spec)
    assert client.keys[("observe", 0)] == _sk.step_key(design, "observe", [0])
    assert client.keys[("observe", 1)] == _sk.step_key(design, "observe", [1])
    wid = next(k for k in client.keys if k[0] == "experiment")[1]
    assert client.keys[("experiment", wid)] == _sk.step_key(design, "experiment", [wid])
    # NEGATIVE: a client without the parameter is called without it (the recording doubles above)


def test_the_verifiers_read_schema_9_page_objects_and_refuse_a_truncated_page():
    """POSITIVE: {observations: [...], truncated: False} is read as the list.
    NEGATIVE: a truncated page never proves absence (None -> not present ->
    the caller recomputes rather than trusting an incomplete answer)."""
    from viv.runner import SfeRunner

    class C:
        def list_observations(self, wid):
            return {"observations": [{"obs_id": "obs_1", "exp_id": "e", "content": {"repeat_index": 0}}],
                    "next_after_seq": 9, "truncated": False}
    assert SfeRunner._observation_present(C(), "w", "obs_1") is True
    assert SfeRunner._observation_present(C(), "w", None, exp_id="e", repeat_index=0) == "obs_1"
    assert SfeRunner._items({"observations": [1], "truncated": True}, "observations") is None
    assert SfeRunner._items([1, 2], "observations") == [1, 2]
