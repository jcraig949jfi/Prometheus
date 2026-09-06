"""The campaign's Vivarium row: E1, E6, E16, and the arm ruling.

    E1   policy_version + template_id into the PEW producer block
    E6   candidate sets bound to SFE `selection` families, WITH alternatives
    E16  outcome-rule aggregation over repeats (any/all/max/min)
    ARM  family + arm sealed SEPARATELY from the execution, linked in PEW,
         with the ruling's own acceptance test: the SAME execution hash under
         labels A and B.
"""
from __future__ import annotations

import copy

import pytest

from conftest import make_spec
from test_blinding import RecordingClient, _runner_over
from test_loop import FakeRunner
from test_repeat import rep
from viv import design as _design
from viv import queue as _q
from viv import selection as _selection
from viv import spec as _spec
from viv.loop import EXECUTED, Vivarium
from viv.request import ExecutionRequest


# ============================================================ E16 aggregation

def _rule(aggregate, field="score", op=">=", value=0.5):
    return {"field": field, "op": op, "value": value,
            "if_true": "SURVIVED", "if_false": "FALSIFIED",
            "if_indeterminate": "INCONCLUSIVE", "aggregate": aggregate}


def _spec_with(aggregate):
    return {**make_spec(kind="evaluate_bitstring",
                        repeat=rep(count=3)),
            "outcome_rule": _rule(aggregate)}


def test_aggregate_must_be_declared_on_a_v3_rule():
    """With repeats, 'the outcome' is ambiguous until someone says which
    reduction they meant."""
    s = _spec_with("any")
    del s["outcome_rule"]["aggregate"]
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(s)
    assert any("aggregate is required" in r for r in exc.value.reasons)


def test_a_v2_rule_may_not_carry_an_aggregate():
    s = make_spec(legacy=True)
    s["outcome_rule"] = _rule("any")
    with pytest.raises(_spec.SpecError) as exc:
        _spec.validate(s)
    assert any("v3 field" in r for r in exc.value.reasons)


@pytest.mark.parametrize("aggregate,scores,expected", [
    ("any", [0.1, 0.2, 0.9], "SURVIVED"),      # held once
    ("any", [0.1, 0.2, 0.3], "FALSIFIED"),     # never held
    ("all", [0.9, 0.8, 0.7], "SURVIVED"),      # held every time
    ("all", [0.9, 0.8, 0.1], "FALSIFIED"),     # one failure is enough
    ("first", [0.9, 0.1, 0.1], "SURVIVED"),    # repeat 0 only
    ("first", [0.1, 0.9, 0.9], "FALSIFIED"),
    ("max", [0.1, 0.2, 0.9], "SURVIVED"),      # reduce, then test once
    ("min", [0.1, 0.2, 0.9], "FALSIFIED"),
    ("min", [0.6, 0.7, 0.9], "SURVIVED"),
])
def test_each_reduction_answers_its_own_question(aggregate, scores, expected):
    s = _spec_with(aggregate)
    outcome, prov = _spec.aggregate_outcome(s, [{"score": v} for v in scores])
    assert outcome == expected
    assert prov["aggregate"] == aggregate
    assert prov["n"] == 3


def test_any_and_all_reduce_the_predicate_max_and_min_the_measurement():
    """They are different questions, which is why the spec must say which."""
    scores = [{"score": v} for v in (0.1, 0.9)]
    _, any_prov = _spec.aggregate_outcome(_spec_with("any"), scores)
    _, max_prov = _spec.aggregate_outcome(_spec_with("max"), scores)
    assert "predicate_held_per_repeat" in any_prov
    assert "reduced_value" in max_prov and max_prov["reduced_value"] == 0.9


def test_the_aggregate_never_hides_what_it_reduced():
    outcome, prov = _spec.aggregate_outcome(
        _spec_with("all"), [{"score": v} for v in (0.9, 0.1, 0.9)])
    assert outcome == "FALSIFIED"
    assert prov["per_repeat_outcomes"] == ["SURVIVED", "FALSIFIED", "SURVIVED"]
    assert len(prov["per_repeat_provenance"]) == 3


@pytest.mark.parametrize("aggregate", ["any", "all", "first", "max", "min"])
def test_one_indeterminate_repeat_makes_the_whole_aggregate_indeterminate(
        aggregate):
    """A reduction over a set containing an unmeasured member is not a
    measurement of that set. Dropping it would turn 'one of three did not
    measure' into 'the three agreed'."""
    s = _spec_with(aggregate)
    outcome, prov = _spec.aggregate_outcome(
        s, [{"score": 0.9}, {"other": 1}, {"score": 0.9}])
    assert outcome == "INCONCLUSIVE"
    assert prov["branch"] == "if_indeterminate"
    assert prov["reason"].startswith("repeat(s) [1]")


def test_the_run_records_the_aggregate_and_the_per_repeat_outcomes():
    s = {**make_spec(kind="random_walk_v0", repeat=rep(count=3, state="persist")),
         "work": {"kind": "random_walk_v0",
                  "payload": {"steps": 2, "step_scale": 1.0}},
         "outcome_rule": _rule("all", field="steps", op="==", value=2)}
    sealed = _spec.spec_hash(s)
    client = RecordingClient()
    out = _runner_over(client, sealed).run(ExecutionRequest(
        experiment_id="e", spec_json=_spec.canonical_bytes(s),
        spec_hash=sealed))
    assert out.outcome == "SURVIVED"
    assert out.summary["aggregate"] == "all"
    assert out.summary["per_repeat_outcomes"] == ["SURVIVED"] * 3
    # each observation still carries its OWN per-repeat outcome
    obs = [c for c in client.calls if c[0] == "observation"]
    assert len(obs) == 3


# ================================================== ARM RULING + design seal

def test_the_design_is_sealed_separately_from_the_execution(conn, schema):
    spec = make_spec()
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="t",
                     experiment_spec=spec, family_id="F1", arm_id="A",
                     request_key="rk-design", schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    d = _design.design_of(row)
    assert d["family_id"] == "F1" and d["arm_id"] == "A"
    h = _design.design_hash(d)
    assert h.startswith("sha256:") and h != row["spec_hash"]
    assert _design.is_declared(d) is True


def test_the_ruling_acceptance_test_same_execution_hash_under_A_and_B(conn,
                                                                     schema):
    """The ruling's own acceptance criterion, stated as a test: two arms, one
    execution hash, two DIFFERENT design hashes."""
    spec = make_spec()
    ids = {}
    for arm in ("A", "B"):
        ids[arm] = _q.enqueue(conn, created_by="archaeon", source_reason="t",
                              experiment_spec=copy.deepcopy(spec),
                              family_id="F-ruling", arm_id=arm,
                              request_key="rk-ruling-" + arm, schema=schema)
    conn.commit()
    rows = {a: _q.get(conn, i, schema=schema) for a, i in ids.items()}

    assert rows["A"]["spec_hash"] == rows["B"]["spec_hash"], \
        "the arm label reached the execution hash"
    da, db = (_design.design_of(rows["A"]), _design.design_of(rows["B"]))
    assert _design.design_hash(da) != _design.design_hash(db), \
        "the design hash did not distinguish the arms"


def test_reassignment_after_commitment_is_refused(conn, schema):
    """Enforced by the database, so design_hash records what the assignment
    WAS and could not have moved."""
    import psycopg2
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), family_id="F", arm_id="A",
                     schema=schema)
    conn.commit()
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue SET arm_id='B' "
                    "WHERE experiment_id=%%s" % schema, (eid,))
    conn.rollback()


def test_the_design_never_reaches_the_executor(conn, schema):
    """The arm is provenance. The apparatus stays blind to it."""
    import json
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), family_id="ZZFAMZZ",
                     arm_id="ZZARMZZ", schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    req = ExecutionRequest.from_queue_row(row)
    blob = json.dumps({"spec": req.spec, "hash": req.spec_hash})
    assert "ZZARMZZ" not in blob and "ZZFAMZZ" not in blob


# ================================================== E1 + the producer block

def test_the_producer_block_carries_the_design_and_the_policy(conn, schema):
    evidence = {"schema": "archaeon.tick.v0", "mode": "weak_signal",
                "policy_version": "random.v0/3", "template_id":
                "bitstring.uniform.v0", "template_version": "1",
                "policy": {"name": "random.v0", "seed": 42, "attempt": 0}}
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="weak_signal",
                     source_evidence=evidence, experiment_spec=make_spec(),
                     family_id="F1", arm_id="C", candidate_set_id="cs-1",
                     request_key="rk-e1", schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    block = _design.producer_block(
        row, engine={"engine_source_hash": "sha256:fake"},
        producer_version="0.1.0", spec_hash=row["spec_hash"])

    assert block["policy"]["policy_version"] == "random.v0/3"
    assert block["policy"]["template_id"] == "bitstring.uniform.v0"
    assert block["policy"]["policy"]["name"] == "random.v0"
    assert block["design"]["arm_id"] == "C"
    assert block["design_hash"].startswith("sha256:")
    assert block["queue"]["candidate_set_id"] == "cs-1"


def test_an_undeclared_policy_version_is_recorded_as_absent(conn, schema):
    """`policy_version: null` says the producer did not declare one. Leaving
    the key out would make 'not declared' and 'not carried' the same."""
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="t",
                     source_evidence={"policy": {"name": "random.v0"}},
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    block = _design.producer_block(
        _q.get(conn, eid, schema=schema),
        engine={}, producer_version="0.1.0", spec_hash="sha256:" + "0" * 64)
    assert "policy_version" in block["policy"]
    assert block["policy"]["policy_version"] is None
    assert block["policy"]["template_id"] is None
    assert block["design_declared"] is False


def test_the_producer_block_reaches_pew(conn, schema):
    bodies = {}

    class FakePew:
        namespace = "test"

        def _req(self, method, path, body=None):
            bodies.setdefault(path, []).append(body)
            if path.startswith("/fossil/encounters/"):
                return 200, {"encounter_id": "enc_e1"}
            return 200, {"status": "inserted"}

    spec = make_spec(pew={"encounter_id": "enc_e1", "players": []})
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="t",
                     source_evidence={"policy_version": "v9",
                                      "template_id": "tmpl.x"},
                     experiment_spec=spec, family_id="F", arm_id="A",
                     request_key="rk-pew-e1", schema=schema)
    conn.commit()
    v = Vivarium(worker_id="test-worker", schema=schema, runner=FakeRunner(),
                 pew_client=FakePew(), log=lambda *_a: None)
    assert v.tick(conn).outcome == EXECUTED
    producer = bodies["/fossil/encounters"][0]["producer"]
    assert producer["policy"]["policy_version"] == "v9"
    assert producer["policy"]["template_id"] == "tmpl.x"
    assert producer["design"]["arm_id"] == "A"
    assert producer["design_hash"].startswith("sha256:")


# ==================================================== E6 selection families

class FamilyClient:
    """Records the SFE family calls a selection binding makes."""

    def __init__(self, fail_alternatives=False):
        self.families, self.members, self.registered = [], [], []
        self.fail_alternatives = fail_alternatives

    def family(self, kind, manifest=None, name=None):
        # The REAL EngineClient.family() returns the whole family dict, not
        # the id. The fake returned a bare string, so it could not catch the
        # bug that a live run found immediately.
        self.families.append({"kind": kind, "manifest": manifest,
                              "name": name})
        return {"family_id": "fam_1", "kind": kind, "state": "OPEN",
                "manifest_hash": "sha256:" + "9" * 64}

    def family_member(self, fid, member_kind, member_id, role=None):
        self.members.append({"fid": fid, "member_kind": member_kind,
                             "member_id": member_id, "role": role})

    def experiment(self, wid, spec, commit=True, enqueue=False, kind=None):
        if self.fail_alternatives:
            raise RuntimeError("engine refused the plan")
        self.registered.append({"wid": wid, "commit": commit,
                                "enqueue": enqueue, "kind": kind})
        return {"exp_id": "exp_alt_%d" % len(self.registered)}


def _candidate_set(conn, schema, n=4, selected=1):
    ids = []
    for i in range(n):
        ids.append(_q.enqueue(
            conn, created_by="archaeon", source_reason="exploration-like",
            experiment_spec=make_spec(seed_root=3000 + i),
            candidate_set_id="cs-e6", request_key="e6-%d" % i,
            status="queued" if i == selected else "cancelled", schema=schema))
    conn.commit()
    return ids


def test_alternatives_are_registered_as_uncommitted_plans(conn, schema):
    """A cancelled candidate has no SFE object. commit=False is SFE's word for
    a plan -- no budget, non-executable -- which is what it actually was."""
    ids = _candidate_set(conn, schema, n=4, selected=1)
    members = _q.candidate_set_members(conn, "cs-e6", schema=schema)
    chosen = _q.get(conn, ids[1], schema=schema)
    client = FamilyClient()

    bound = _selection.bind(client, candidate_set_id="cs-e6", members=members,
                            selected_row=chosen, selected_exp_id="exp_sel",
                            world_id="wld_1")

    assert bound["planned_members"] == 4
    assert bound["alternatives_recorded"] == 3
    assert bound["selection_visible"] is True and bound["complete"] is True
    assert all(r["commit"] is False for r in client.registered)
    roles = [m["role"] for m in client.members]
    assert roles.count("selected") == 1 and roles.count("alternative") == 3


def test_the_family_manifest_seals_the_whole_candidate_set(conn, schema):
    ids = _candidate_set(conn, schema, n=3, selected=0)
    members = _q.candidate_set_members(conn, "cs-e6", schema=schema)
    client = FamilyClient()
    _selection.bind(client, candidate_set_id="cs-e6", members=members,
                    selected_row=_q.get(conn, ids[0], schema=schema),
                    selected_exp_id="exp_sel", world_id="wld_1")
    fam = client.families[0]
    assert fam["kind"] == "selection"
    assert fam["manifest"]["planned_members"] == 3
    assert len(fam["manifest"]["candidates"]) == 3
    assert sum(1 for c in fam["manifest"]["candidates"]
               if c["role"] == "selected") == 1
    # identities are fixed in the sealed manifest, not asserted later
    assert all(c["spec_hash"].startswith("sha256:")
               for c in fam["manifest"]["candidates"])


def test_an_unrecordable_alternative_is_reported_not_swallowed(conn, schema):
    ids = _candidate_set(conn, schema, n=3, selected=0)
    members = _q.candidate_set_members(conn, "cs-e6", schema=schema)
    client = FamilyClient(fail_alternatives=True)
    bound = _selection.bind(client, candidate_set_id="cs-e6", members=members,
                            selected_row=_q.get(conn, ids[0], schema=schema),
                            selected_exp_id="exp_sel", world_id="wld_1",
                            log=lambda *_a: None)
    assert bound["complete"] is False
    assert bound["alternatives_recorded"] == 0
    assert len(bound["errors"]) == 2
    assert bound["selection_visible"] is False


def test_a_row_with_no_candidate_set_binds_nothing(conn, schema):
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    v = Vivarium(worker_id="test-worker", schema=schema, runner=FakeRunner(),
                 pew_client=None, log=lambda *_a: None)
    assert v.tick(conn).outcome == EXECUTED
    events = [e["event_type"] for e in _q.events(conn, eid, schema=schema)]
    assert "selection_bound" not in events


def test_a_failed_binding_never_fails_the_experiment(conn, schema):
    """A missing binding is a weaker provenance claim, not a wrong result."""
    _candidate_set(conn, schema, n=2, selected=0)
    ids = [str(r["experiment_id"])
           for r in _q.candidate_set_members(conn, "cs-e6", schema=schema)]

    class BrokenRunner(FakeRunner):
        pass

    v = Vivarium(worker_id="test-worker", schema=schema, runner=BrokenRunner(),
                 pew_client=None, log=lambda *_a: None)
    # the injected FakeRunner has no `.c`, so bind_selection raises internally
    r = v.tick(conn)
    assert r.outcome == EXECUTED
    row = _q.get(conn, r.experiment_id, schema=schema)
    assert row["status"] == "completed"
    events = [e["event_type"] for e in _q.events(conn, r.experiment_id,
                                                 schema=schema)]
    assert "selection_bind_failed" in events


# ======================= post-commit failures stay inside the boundary

def test_any_post_commit_failure_reaches_the_loop_as_an_ExecutionFailure():
    """Found live on 2026-09-06: SFE went down mid-run, the transport error
    escaped as a bare exception, and the row recorded crossed=True with no
    fossil. Everything after the irreversible commit is inside the execution
    boundary and must arrive classified, carrying what was observed."""
    from viv.runner import ExecutionFailure

    class DropsAfterCommit(RecordingClient):
        def claim(self, worker_id, world_id=None, lease_s=None):
            raise ConnectionError("Remote end closed connection without "
                                  "response")

    spec = make_spec()
    sealed = _spec.spec_hash(spec)
    client = DropsAfterCommit()
    runner = _runner_over(client, sealed)
    with pytest.raises(ExecutionFailure) as exc:
        runner.run(ExecutionRequest(experiment_id="e",
                                    spec_json=_spec.canonical_bytes(spec),
                                    spec_hash=sealed))
    assert exc.value.failure_class == "ENGINE_TRANSPORT"
    partial = exc.value.partial
    assert partial.crossed_boundary is True
    assert partial.sfe_experiment_id == "exp_fixed"
    assert "ConnectionError" in str(exc.value)


def test_a_post_commit_transport_failure_is_fossilized(conn, schema):
    """crossed=True must imply a fossil attempt, whatever broke."""
    from viv.runner import ExecutionFailure, RunResult
    bodies = {}

    class FakePew:
        namespace = "test"

        def _req(self, method, path, body=None):
            bodies.setdefault(path, []).append(body)
            if path.startswith("/fossil/encounters/"):
                return 200, {"encounter_id": "enc_drop"}
            return 200, {"status": "inserted"}

    class Dropping(FakeRunner):
        def run(self, request, *, on_running=None, **kw):
            self.runs.append(request.experiment_id)
            if on_running:
                on_running("exp_drop", {"world_id": "wld_drop"})
            raise ExecutionFailure(
                "ConnectionError after the experiment was committed",
                partial=RunResult(world_id="wld_drop",
                                  sfe_experiment_id="exp_drop",
                                  run_id="exp_drop", crossed_boundary=True,
                                  spec_hash_hint=request.spec_hash,
                                  anchor={"resolved": True,
                                          "sfe_event_id": "evt_drop",
                                          "sfe_entry_hash": "sha256:" + "c" * 64,
                                          "sfe_event_seq": 2}),
                failure_class="ENGINE_TRANSPORT")

    spec = make_spec(pew={"encounter_id": "enc_drop", "players": []})
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=spec, schema=schema)
    conn.commit()
    v = Vivarium(worker_id="test-worker", schema=schema, runner=Dropping(),
                 pew_client=FakePew(), log=lambda *_a: None)
    r = v.tick(conn)
    assert r.failure_class == "ENGINE_TRANSPORT"
    row = _q.get(conn, eid, schema=schema)
    assert row["started_at"] is not None      # crossed
    assert row["pew_reference"] is not None   # and fossilized
    enc = bodies["/fossil/encounters"][0]
    assert enc["failure_class"] == "ENGINE_TRANSPORT"
    assert "outcome" not in enc


def test_the_family_id_is_taken_from_the_engines_response_shape(conn, schema):
    """EngineClient.family() returns a DICT. Passing it straight into the
    members URL is what broke the first live E6 binding."""
    ids = _candidate_set(conn, schema, n=2, selected=0)
    members = _q.candidate_set_members(conn, "cs-e6", schema=schema)
    client = FamilyClient()
    bound = _selection.bind(client, candidate_set_id="cs-e6", members=members,
                            selected_row=_q.get(conn, ids[0], schema=schema),
                            selected_exp_id="exp_sel", world_id="wld_1")
    assert bound["family_id"] == "fam_1"
    assert all(isinstance(m["fid"], str) for m in client.members)


def test_a_family_response_without_an_id_is_refused(conn, schema):
    ids = _candidate_set(conn, schema, n=2, selected=0)
    members = _q.candidate_set_members(conn, "cs-e6", schema=schema)

    class NoId(FamilyClient):
        def family(self, kind, manifest=None, name=None):
            return {"kind": kind, "state": "OPEN"}

    with pytest.raises(_selection.SelectionBindError) as exc:
        _selection.bind(NoId(), candidate_set_id="cs-e6", members=members,
                        selected_row=_q.get(conn, ids[0], schema=schema),
                        selected_exp_id="exp_sel", world_id="wld_1")
    assert "no usable family_id" in str(exc.value)
