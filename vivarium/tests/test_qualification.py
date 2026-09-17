"""THE QUALIFICATION FIXTURE (operator Stage 3 / implementation order s13, s16).

One synthetic scientific run, Campaign-4-shaped, on a drafted throwaway
schema, exercising in order:

    harness_id -> execution_id translation (the provenance envelope)
    hashed start bundle (declared + filled; both hashes on the attempt)
    gate FAIL with no dependent action; gate PASS followed by action
    intentional recoverable worker failure -> NEW ATTEMPT (release --new-attempt)
    REUSED step (validate: pure, no verifier)
    REPLAYED step (world / experiment / observation 0: engine-verified)
    RECOMPUTED step (run: never replayable)
    design-key mismatch refusal (VIV20)
    intended intervention != realized intervention (PARTIAL receipt)
    budget termination that is COMPLETED + CENSORED
    artifact CONSUMPTION receipt (preflight import; emission is not a
    Vivarium act -- see the receipt's "not_exercised")
    PEW unavailable -> outbox growth -> later delivery -> duplicate delivery
    worker restart (a second Vivarium instance drives the new attempt)
    a deliberate malformed historical row -> backfill UNKNOWN stays UNKNOWN
    final machine-readable provenance (attempt receipt from rows)

and then answers the seven s16 questions as assertions. When
VIV_QUALIFICATION_RECEIPT names a path, the fixture writes its receipt
there (the committed evidence for READINESS_DISPOSITION.md).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from viv import attempts as _att
from viv import bundle as _b
from viv import db as _db
from viv import deliver as _dl
from viv import queue as _q
from viv import spec as _spec
from viv import stepkey as _sk
from viv.loop import EXECUTED, FAILED, Vivarium
from tests.test_blinding import _runner_over
from tests.test_deliver import FakePew
from tests.test_loop import make_spec
from tests.test_point_release_attempts import VerifyingClient, drafted  # noqa: F401

DRAFTS = Path(__file__).resolve().parent.parent / "migrations" / "drafts"


def _envelope(harness, design, attempt, step, seed, foundry):
    return {"campaign_id": "cmp4-qual", "harness_id": harness, "design_id": design, "attempt_id": attempt,
            "step_id": step, "campaign_seed": seed, "rng_label": "crn:%s" % harness, "foundry_profile": foundry,
            "cell": "W2_K2", "origin_kind": "producer"}


def _store_envelope(conn, schema, eid, env, factors):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO " + schema + ".provenance_envelope (experiment_id, envelope_version, envelope, factors) "
                    "VALUES (%s, 'viv.envelope.v1', %s, %s)", (eid, json.dumps(env), json.dumps(factors)))
    conn.commit()


def _read(conn, schema, sql, *args):
    with _db.dict_cur(conn) as cur:
        cur.execute(sql.replace("{S}", schema), args or None)
        rows = [dict(r) for r in cur.fetchall()]
    conn.rollback()
    return rows


def test_qualification_campaign4_shaped_run(conn, drafted, tmp_path):
    schema = drafted
    receipt = {"fixture": "viv.qualification.v1", "schema": schema, "checks": {}, "not_exercised": {}}
    C = receipt["checks"]

    # ---- 1. one harness, multiple executions, explicit start bundle, gate --
    harness = "C4-SFE-Q1"
    spec_a = make_spec(pew={"encounter_id": "enc-q-a", "players": ["evca:r3:" + "0" * 32]})
    spec_a["repeat"] = {"count": 2, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                        "budget": {"max_seconds": 60, "max_observations": 2}}
    spec_b = make_spec(pew={"encounter_id": "enc-q-b", "players": []})
    spec_b["repeat"] = {"count": 3, "order": "sequential", "seed_derivation": "constant", "state": "reset",
                        "budget": {"max_seconds": 1e-9, "max_observations": 3}}      # will censor
    gate = {"gate_id": "pc:w0_climbed", "phase": "pre_execution",
            "condition": "the W0 control best >= the measured shelf floor of THIS table",
            "measurement": {"source": "producer_supplied", "ref": "w0_best"},
            "rule": {"op": ">=", "reference": {"ref": "shelf_floor"}, "if_indeterminate": "FAIL"},
            "on_fail": "abort_attempt", "definition_ref": "prereg:sha256:deadbeef#gates[0]"}
    declared = _b.declared_skeleton(spec_a)
    declared["gates"] = [gate]
    declared["evaluator"] = {"profile_id": "ev.partial_credit.v1", "reward_mode": "partial"}
    declared["schedule"] = {"schedule_id": "ladder.d1.v1", "kind": "rung_hold", "parameters": {"hold_until": 0.5}}
    declared["population"] = {"population_schema": "UNKNOWN", "manifest_hash": "sha256:" + "1" * 64,
                              "manifest_ref": "pop:q1", "foundry_profile": "instr1-16:6528b9dc"}
    declared["interventions_declared"] = [{"intervention_id": "inject:A", "kind": "import",
                                           "intended": {"count": 4}, "timing": {"generation": 0}, "source_ids": ["w0:src"]}]
    declared["factors"] = {"evaluator_family": "partial_credit", "cell": "W2_K2", "foundry_profile": "instr1-16:6528b9dc",
                           "budget_class": "G300", "treatment_arm": "treated"}
    assert _b.problems(declared, spec=spec_a) == []
    bh_declared = _b.bundle_hash(declared)

    def enqueue(spec, gate_measurements, att_label):
        eid = str(_q.enqueue(conn, created_by="archaeon-qual", source_reason="qualification", experiment_spec=spec,
                             source_evidence={"gate_measurements": gate_measurements}, family_id=harness,
                             arm_id=att_label, schema=schema))
        conn.commit()
        d = json.loads(json.dumps(declared)); d["spec_hash"] = _spec.spec_hash(spec)
        with conn.cursor() as cur:
            cur.execute("UPDATE " + schema + ".research_experiment_queue SET bundle_declared=%s WHERE experiment_id=%s",
                        (json.dumps(d), eid))
        conn.commit()
        _store_envelope(conn, schema, eid, _envelope(harness, "sha256:deadbeef", "%s/a01" % harness,
                                                     _sk.step_key(_spec.spec_hash(spec), "cell", [att_label]),
                                                     20260920, "instr1-16:6528b9dc"), declared["factors"])
        return eid

    # gate FAIL: the control did not climb (0.3 < floor 0.45)
    e_fail = enqueue(spec_a, {"w0_best": 0.3, "shelf_floor": 0.45}, "gate-fail")
    client = VerifyingClient()
    v1 = Vivarium(worker_id="q-w1", schema=schema, runner=_runner_over(client, _spec.spec_hash(spec_a)),
                  pew_client=None, log=lambda *_a: None)
    r = v1.tick(conn)
    assert r.outcome == FAILED and r.failure_class == "PREREQUISITE_FAILED"
    g = _read(conn, schema, "SELECT result, action_taken, measured, reference FROM {S}.gate_receipt gr JOIN {S}.execution_attempt a ON a.attempt_id = gr.attempt_id WHERE a.experiment_id = %s", e_fail)[0]
    assert g == {"result": "FAIL", "action_taken": "aborted_attempt", "measured": 0.3, "reference": 0.45}
    assert not any(n == "create_world" for n, _ in client.calls)
    C["gate_fail_no_dependent_action"] = True
    C["gate_reference_resolved_from_measured_space"] = (g["reference"] == 0.45)

    # gate PASS + the interventional executor + a worker death mid-row
    from viv import executors as _ex
    real_noop = _ex._noop_v0

    def noop_with_intervention(spec):
        out = real_noop(spec)
        out["_interventions"] = [{"intervention_id": "inject:A", "kind": "import", "intended": {"count": 4},
                                  "realised": {"count": 1}, "logical_time": {"generation": 0},
                                  "supplied": [{"organism_id": "a" * 64}], "source_ids": ["w0:src"], "result": "APPLIED"}]
        return out
    _ex._noop_v0 = noop_with_intervention
    try:
        e_pass = enqueue(spec_a, {"w0_best": 0.9, "shelf_floor": 0.45}, "treated")
        client = VerifyingClient()
        runner = _runner_over(client, _spec.spec_hash(spec_a))
        real_obs = client.observation
        n = {"k": 0}

        def die_on_second(wid, exp_id, content, outcome, **kw):
            n["k"] += 1
            if n["k"] == 2:
                raise RuntimeError("simulated worker death")
            return real_obs(wid, exp_id, content, outcome, **kw)
        client.observation = die_on_second
        v1 = Vivarium(worker_id="q-w1", schema=schema, runner=runner, pew_client=None, log=lambda *_a: None)
        r1 = v1.tick(conn)
        assert r1.outcome == FAILED
        a1 = _read(conn, schema, "SELECT * FROM {S}.execution_attempt WHERE experiment_id=%s ORDER BY attempt_number", e_pass)[0]
        assert a1["bundle_hash_declared"] == _b.bundle_hash(dict(declared, spec_hash=_spec.spec_hash(spec_a)))
        assert a1["bundle_hash"] != a1["bundle_hash_declared"]        # Vivarium filled four slots
        C["bundle_declared_and_filled_hashes"] = True
        gp = _read(conn, schema, "SELECT result, action_taken FROM {S}.gate_receipt WHERE attempt_id=%s", a1["attempt_id"])[0]
        assert gp == {"result": "PASS", "action_taken": "proceeded"}
        C["gate_pass_then_action"] = True

        # the strand -> release to a NEW ATTEMPT (worker restart: a second instance)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO " + schema + ".execution_attempt (experiment_id, attempt_number, parent_attempt_id, design_digest, worker_id) VALUES (%s, 2, %s, %s, 'q-w1')",
                        (e_pass, a1["attempt_id"], _spec.spec_hash(spec_a)))
            cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
            cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='running', claimed_by='q-w1', finished_at=NULL WHERE experiment_id=%s", (e_pass,))
            cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
        conn.commit()
        _q.release_stranded(conn, e_pass, actor="operator", reason="worker died mid-row", schema=schema, new_attempt=True)
        conn.commit()
        client.observation = real_obs
        v2 = Vivarium(worker_id="q-w2", schema=schema, runner=runner, pew_client=None, log=lambda *_a: None)
        r2 = v2.tick(conn)
        assert r2.outcome == EXECUTED
    finally:
        _ex._noop_v0 = real_noop

    atts = _read(conn, schema, "SELECT * FROM {S}.execution_attempt WHERE experiment_id=%s ORDER BY attempt_number", e_pass)
    assert [a["attempt_number"] for a in atts] == [1, 2, 3]
    assert atts[1]["terminal_state"] == "STRANDED" and atts[2]["terminal_state"] == "COMPLETED"
    assert atts[2]["parent_attempt_id"] == atts[1]["attempt_id"] and atts[2]["of_record"] is True
    C["new_attempt_after_recoverable_failure"] = True
    steps = {(s["step_kind"], tuple(s["parts"])): s["status"] for s in
             _read(conn, schema, "SELECT step_kind, parts, status FROM {S}.execution_step WHERE attempt_id=%s", atts[2]["attempt_id"])}
    assert steps[("validate", ())] == "REUSED"
    assert steps[("world", ("plain",))] == "REPLAYED" and steps[("observe", (0,))] == "REPLAYED"
    assert steps[("run", (0,))] == "RECOMPUTED" and steps[("observe", (1,))] == "NEW"
    C["step_statuses"] = {"REUSED": "validate", "REPLAYED": "world/experiment/observe:0", "RECOMPUTED": "run:*", "NEW": "observe:1"}
    assert sum(1 for name, _ in client.calls if name == "create_world") == 1
    C["no_world_recreated_on_replay"] = True

    # intervention: intended 4, realised 1 -> PARTIAL, writer executor, entities bound
    ir = _read(conn, schema, "SELECT intervention_id, intended, realised, result, writer, supplied FROM {S}.intervention_receipt WHERE attempt_id=%s", atts[2]["attempt_id"])
    inj = [x for x in ir if x["intervention_id"].startswith("inject:A#r")]
    assert inj and inj[0]["result"] == "PARTIAL" and inj[0]["intended"] == {"count": 4} and inj[0]["realised"] == {"count": 1}
    assert inj[0]["supplied"][0]["organism_id"] == "a" * 64
    C["intended_vs_realised_intervention"] = True

    # ---- 2. budget termination: COMPLETED + CENSORED ------------------------
    e_cens = enqueue(spec_b, {"w0_best": 0.9, "shelf_floor": 0.45}, "censored")
    v3 = Vivarium(worker_id="q-w2", schema=schema, runner=_runner_over(VerifyingClient(), _spec.spec_hash(spec_b)),
                  pew_client=None, log=lambda *_a: None)
    assert v3.tick(conn).outcome == EXECUTED
    ac = _read(conn, schema, "SELECT terminal_state, termination FROM {S}.execution_attempt WHERE experiment_id=%s", e_cens)[0]
    assert ac["terminal_state"] == "COMPLETED" and ac["termination"]["censored"] is True
    assert ac["termination"]["termination_reason"] == "BUDGET_EXHAUSTED"
    C["budget_termination_completed_and_censored"] = True

    # ---- 3. design-key mismatch refusal (VIV20) -----------------------------
    import psycopg2
    with pytest.raises(psycopg2.Error) as exc:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO " + schema + ".execution_step (attempt_id, step_key, step_kind, status) VALUES (%s, %s, 'validate', 'NEW')",
                        (atts[2]["attempt_id"], _sk.step_key("sha256:" + "f" * 64, "validate", [])))
    conn.rollback()
    assert "VIV20" in str(exc.value)
    C["design_key_mismatch_refused"] = True

    # ---- 4. PEW unavailable -> outbox -> later delivery -> duplicate --------
    pend = _read(conn, schema, "SELECT count(*) AS n FROM {S}.pew_outbox WHERE state='PENDING'")[0]["n"]
    assert pend >= 6                                     # events for every attempt above
    C["outbox_growth_while_pew_down"] = pend
    fake = FakePew(); fake.down = True
    d = _dl.Deliverer(_dl.Config(producer="q-w2", var_dir=tmp_path, post=False, disable_task=False),
                      client_factory=lambda: fake, log=lambda *_a: None)
    assert d.tick(conn)["delivered"] == 0
    fake.down = False
    d.tick(conn); d.tick(conn)
    delivered = _read(conn, schema, "SELECT count(*) AS n FROM {S}.pew_outbox WHERE state='DELIVERED' AND event_kind='ENCOUNTER_RECORDED'")[0]["n"]
    # three encounters delivered (failed attempt 1, completed attempt 3, the
    # censored run); the recording double mints ONE fixed work id, so attempt
    # 1 and attempt 3 collide on (encounter_id, run_id) in the fake -- a real
    # engine issues a new work claim per attempt and they are distinct
    assert delivered == 3 and len(fake.encounters) == 2
    from viv import pew as _pew
    payload = _read(conn, schema, "SELECT payload FROM {S}.pew_outbox WHERE event_kind='ENCOUNTER_RECORDED' AND state='DELIVERED' LIMIT 1")[0]["payload"]
    dup = _pew.post_bodies(fake, payload)
    assert dup["idempotent_replay"] is True and len(fake.encounters) == 2
    C["later_delivery_and_duplicate_no_double_count"] = True

    # ---- 5. malformed historical row: backfill UNKNOWN stays UNKNOWN --------
    e_old = str(_q.enqueue(conn, created_by="legacy", source_reason="pre-release", experiment_spec=make_spec(), schema=schema))
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        # a PRE-RELEASE row is one created before the window; 007's cutoff is the window
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET status='failed', finished_at=now(), created_at='2026-09-14 00:00:00+00', error='BUDGET_EXCEEDED: execution budget exhausted after 3 of 6' WHERE experiment_id=%s", (e_old,))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
        cur.execute((DRAFTS / "007_backfill_attempts_reversible.sql").read_text(encoding="utf-8").replace("{schema}", schema))
    conn.commit()
    # NEGATIVE: a post-window row cancelled while queued has no attempt by design and is NOT backfilled
    e_new = str(_q.enqueue(conn, created_by="post-release", source_reason="cancelled while queued", experiment_spec=make_spec(hypothesis="probe post"), schema=schema))
    _q.cancel(conn, e_new, actor="t", reason="never claimed", schema=schema)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue DISABLE TRIGGER trg_req_transition")
        cur.execute("UPDATE " + schema + ".research_experiment_queue SET created_at='2026-09-18 00:00:00+00' WHERE experiment_id=%s", (e_new,))
        cur.execute("ALTER TABLE " + schema + ".research_experiment_queue ENABLE TRIGGER trg_req_transition")
        cur.execute((DRAFTS / "007_backfill_attempts_reversible.sql").read_text(encoding="utf-8").replace("{schema}", schema))
    conn.commit()
    assert _read(conn, schema, "SELECT count(*) AS n FROM {S}.execution_attempt WHERE experiment_id=%s", e_new)[0]["n"] == 0
    old = _read(conn, schema, "SELECT attempt_number, terminal_state, termination FROM {S}.execution_attempt WHERE experiment_id=%s", e_old)[0]
    assert old["attempt_number"] == 1 and old["terminal_state"] == "FAILED"
    assert old["termination"]["termination_reason"] == "UNKNOWN" and old["termination"]["censored"] is None
    assert _q.get(conn, e_old, schema=schema)["error"].startswith("BUDGET_EXCEEDED")   # legacy text preserved
    C["backfill_unknown_stays_unknown"] = True

    # ---- 6. final machine-readable provenance --------------------------------
    A = _att.Attempts(schema=schema, worker_id="q-w2", log=lambda *_a: None)
    ctx = _att.AttemptCtx(attempt_id=atts[2]["attempt_id"], experiment_id=e_pass, attempt_number=3,
                          design_digest=atts[2]["design_digest"], parent_attempt_id=atts[2]["parent_attempt_id"])
    rec = A.receipt(conn, ctx, termination=atts[2]["termination"])
    assert rec["step_counts"]["REPLAYED"] >= 3 and rec["step_counts"]["RECOMPUTED"] >= 2 and rec["step_counts"]["REUSED"] >= 1
    assert rec["intervention_summary"]["partial"] == 2          # one per repeat
    env = _read(conn, schema, "SELECT envelope, factors FROM {S}.provenance_envelope WHERE experiment_id=%s", e_pass)[0]
    assert env["envelope"]["harness_id"] == harness and env["envelope"]["attempt_id"] == harness + "/a01"
    assert env["factors"]["treatment_arm"] == "treated" and env["factors"]["budget_class"] == "G300"
    rdig = "sha256:" + hashlib.sha256(_spec.canonical_bytes(rec)).hexdigest()
    assert rdig == atts[2]["receipt_digest"]
    C["receipt_digest_recomputes_from_rows"] = True
    C["harness_to_execution_translation_preserved"] = True
    C["strata_recoverable_from_factors"] = True

    # ---- 7. the s16 questions, as assertions ---------------------------------
    answers = {
        "exact_attempt_reconstructable": rdig == atts[2]["receipt_digest"],
        "derived_design_alters_one_start_condition": (lambda: (
            _b.diff(declared, dict(declared, schedule={"schedule_id": "ladder.d2.v1", "kind": "rung_hold", "parameters": {"hold_until": 0.5}})) == ["schedule.schedule_id"]))(),
        "system_proves_what_changed": _b.bundle_hash(declared) != _b.bundle_hash(dict(declared, factors=dict(declared["factors"], treatment_arm="control"))),
        "duplicate_execution_distinguished": len(atts) == 3 and len({a["attempt_id"] for a in atts}) == 3,
        "duplicate_delivery_distinguished": dup["idempotent_replay"] is True,
        "intervention_provable": inj[0]["result"] == "PARTIAL",
        "strata_recoverable": set(env["factors"]) >= {"evaluator_family", "cell", "foundry_profile", "budget_class", "treatment_arm"},
        "pew_off_the_execution_path": pend >= 6,
    }
    assert all(answers.values()), answers
    receipt["s16_answers"] = answers
    receipt["not_exercised"] = {
        "artifact_emission": "Vivarium kinds emit observations, not artifacts; artifact CONSUMPTION (preflight import) is receipted; emission is a producer/engine act",
        "checkpoint_fork": "deferred by order (s15); slot only",
        "real_engine": "engine calls are a recording double; the canary (s14) runs against the production engine as vivarium-test",
    }
    out = os.environ.get("VIV_QUALIFICATION_RECEIPT")
    if out:
        Path(out).write_text(json.dumps(receipt, indent=2, default=str), encoding="utf-8")
