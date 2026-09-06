"""THE LOAD-BEARING TEST.

The claim is not "the executor currently ignores provenance" -- that is a code
review that has to be repeated forever. The claim is that **provenance cannot
reach the executor through the supported interface**, and that any change to a
real execution input DOES change execution identity.

Both halves matter. Without the first, an arm label could silently alter what
runs. Without the second, a real parameter change could silently NOT alter the
sealed identity, and two different experiments would share one hash.

If Archaeon's fossil-directed policy eventually beats random selection, this
file is what makes the difference attributable to SELECTION.
"""
from __future__ import annotations

import copy
import dataclasses
import json

import pytest

from conftest import make_spec
from viv import queue as _q
from viv import spec as _spec
from viv.loop import Vivarium
from viv.request import FIELDS, ExecutionRequest, SpecIntegrityError
from viv.runner import RunResult


class RecordingClient:
    """Records every SFE call with its arguments, in order.

    The comparison unit is this transcript. Two runs are identical executions
    iff their transcripts are equal after masking only the ids the ENGINE mints
    (world_id, exp_id, ...), which no caller controls."""

    def __init__(self):
        self.calls = []
        self.beats = 0

    def _rec(self, _call, **kw):
        self.calls.append((_call, kw))

    # -- the subset SfeRunner uses ---------------------------------------
    def create_session(self, name):
        self._rec("create_session", name=name)
        return "ses_fixed"

    def create_world(self, sid, name, seed_root=None):
        self._rec("create_world", session=sid, name=name,
                  seed_root=seed_root)
        return {"world_id": "wld_fixed"}

    def start(self, wid):
        self._rec("start", wid=wid)

    def hypothesis(self, wid, statement):
        self._rec("hypothesis", wid=wid, statement=statement)
        return "hyp_fixed"

    def prediction(self, wid, hyp_id, content):
        self._rec("prediction", wid=wid, hyp_id=hyp_id, content=content)
        return "prd_fixed"

    def experiment(self, wid, spec, **kw):
        self._rec("experiment", wid=wid, spec=spec, **kw)
        return {"exp_id": "exp_fixed"}

    def claim(self, worker_id, world_id=None, lease_s=None):
        self._rec("claim", worker_id=worker_id, world_id=world_id,
                  lease_s=lease_s)
        return {"work_id": "wrk_fixed", "claim_id": "clm_fixed",
                "kind": "noop", "payload": {}}

    def heartbeat(self, work_id, worker_id, claim_id, lease_s=None):
        # Recorded but NOT part of the compared transcript: renewals depend on
        # wall-clock, and two identical specs may legitimately differ there.
        self.beats += 1
        return {"ok": True}

    def complete(self, work_id, worker_id, claim_id, result, attestation=None):
        self._rec("complete", work_id=work_id, worker_id=worker_id,
                  claim_id=claim_id, result=result, attestation=attestation)
        return {"science": {"profile_findings": []}}

    def observation(self, wid, exp_id, content, outcome, pred_id=None,
                    work_id=None):
        self._rec("observation", wid=wid, exp_id=exp_id, content=content,
                  outcome=outcome, pred_id=pred_id, work_id=work_id)
        return "obs_fixed"

    def events(self, wid, limit=100):
        return [{"event_type": "OBSERVATION_RECORDED", "event_id": "evt_fixed",
                 "entry_hash": "sha256:" + "a" * 64, "event_seq": 1,
                 "refs": {"exp_id": "exp_fixed", "obs_id": "obs_fixed"}}]

    def _req(self, method, path, body=None):
        # the audit envelope; spec_hash is filled by the fixture below
        return {"sealed_spec_hash_in_ledger": self.sealed,
                "spec_hash_recomputed": self.sealed,
                "envelope_hash": "sha256:" + "b" * 64,
                "ledger_head_hash": "sha256:" + "c" * 64,
                "work": {"status": "COMPLETED"}}


def _runner_over(client, sealed):
    from viv.runner import SfeRunner
    r = SfeRunner.__new__(SfeRunner)          # no network in __init__
    r.worker_id = "test-worker"
    r.c = client
    r.lease_s = 120.0
    r.log = lambda *_a: None
    client.sealed = sealed
    r.version = {"engine_source_hash": "sha256:fake", "source_commit": "0" * 40,
                 "schema_version": 6, "engine_instance_id": "eng_fake"}
    r._session_id = None
    return r


def _transcript(spec):
    """The exact SFE call sequence a spec produces."""
    sealed = _spec.spec_hash(spec)
    client = RecordingClient()
    runner = _runner_over(client, sealed)
    req = ExecutionRequest(experiment_id="ignored",
                           spec_json=_spec.canonical_bytes(spec),
                           spec_hash=sealed)
    runner.run(req)
    return client.calls


# ---------------------------------------------------------------------------
# Half 1: provenance CANNOT cross the boundary
# ---------------------------------------------------------------------------

def test_the_request_has_exactly_three_fields():
    """Widening this is a deliberate, visible act, not a drift."""
    names = tuple(f.name for f in dataclasses.fields(ExecutionRequest))
    assert names == FIELDS == ("experiment_id", "spec_json", "spec_hash")


def test_from_queue_row_projects_only_those_three(conn, schema):
    """Every other column on the row is unreachable from the request."""
    eid = _q.enqueue(conn, created_by="archaeon:C_frozen_S17",
                     source_reason="weak_signal-lookalike",
                     source_evidence={"detector": "D1", "policy": "fossil"},
                     experiment_spec=make_spec(), family_id="F1",
                     arm_id="C_frozen_S17", schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    req = ExecutionRequest.from_queue_row(row)

    blob = json.dumps({"fields": {f.name: str(getattr(req, f.name))
                                  for f in dataclasses.fields(req)},
                       "spec": req.spec})
    for leaked in ("archaeon", "C_frozen_S17", "D1", "fossil", "F1",
                   "weak_signal"):
        assert leaked not in blob, "provenance %r reached the request" % leaked


def test_the_runner_refuses_anything_but_a_request(conn, schema):
    """A queue row passed to run() would carry provenance across the boundary.
    It is refused loudly rather than duck-typed into working."""
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    runner = _runner_over(RecordingClient(), row["spec_hash"])
    for bad in (dict(row), {"experiment_spec": {}, "spec_hash": "x"}, None, 7):
        with pytest.raises(TypeError) as exc:
            runner.run(bad)
        assert "ExecutionRequest" in str(exc.value)


def test_a_tampered_spec_cannot_even_be_packaged():
    """Self-verifying: the request checks the spec against its sealed hash at
    construction, so a corrupted spec fails before any engine call exists."""
    spec = make_spec()
    sealed = _spec.spec_hash(spec)
    tampered = copy.deepcopy(spec)
    tampered["world"]["seed_root"] = 999
    with pytest.raises(SpecIntegrityError):
        ExecutionRequest(experiment_id="e", spec_hash=sealed,
                         spec_json=_spec.canonical_bytes(tampered))


def test_identical_specs_with_opposite_provenance_execute_identically(conn,
                                                                      schema):
    """THE CLAIM. Two arms of one comparison, byte-identical specs, arbitrarily
    different provenance -- one SFE call sequence."""
    spec = make_spec(seed_root=424242)
    arms = [
        dict(created_by="archaeon:A_random", source_reason="exploration-like",
             source_evidence={"policy": "A_random", "seed": 7},
             family_id="S18-live", arm_id="A_random",
             candidate_set_id="cs-1", request_key="rk-a"),
        dict(created_by="archaeon:C_frozen_S17", source_reason="weak-signal-like",
             source_evidence={"policy": "C_frozen_S17", "detector": "D3",
                              "fossil_rank": 1},
             family_id="S18-live", arm_id="C_frozen_S17",
             candidate_set_id="cs-2", request_key="rk-c"),
    ]
    ids = []
    for a in arms:
        ids.append(_q.enqueue(conn, experiment_spec=copy.deepcopy(spec),
                              priority=100, schema=schema, **a))
    conn.commit()

    rows = [_q.get(conn, i, schema=schema) for i in ids]
    assert rows[0]["spec_hash"] == rows[1]["spec_hash"], \
        "the arm label leaked into the sealed hash"

    transcripts = []
    for row in rows:
        client = RecordingClient()
        runner = _runner_over(client, row["spec_hash"])
        runner.run(ExecutionRequest.from_queue_row(row))
        transcripts.append(client.calls)

    assert transcripts[0] == transcripts[1]
    # and the world name is derived, so it is the same in both arms
    world_calls = [c for c in transcripts[0] if c[0] == "create_world"]
    assert world_calls[0][1]["name"] == _spec.world_name(rows[0]["spec_hash"])


def test_no_field_of_the_row_appears_anywhere_in_the_sfe_traffic(conn, schema):
    """Stronger than equality of two transcripts: the provenance strings are
    absent from the bytes that reach the engine at all."""
    marker = "ZZPOLICYMARKERZZ"
    eid = _q.enqueue(conn, created_by=marker, source_reason=marker,
                     source_evidence={"policy": marker},
                     family_id=marker, arm_id=marker,
                     candidate_set_id=marker, request_key=marker,
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    client = RecordingClient()
    runner = _runner_over(client, row["spec_hash"])
    runner.run(ExecutionRequest.from_queue_row(row))
    assert marker not in json.dumps(client.calls, default=str)


# ---------------------------------------------------------------------------
# Half 2: a real execution input MUST change execution identity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("mutate,label", [
    (lambda s: s["world"].__setitem__("seed_root", 424243), "seed_root"),
    (lambda s: s["work"]["payload"].__setitem__("bits", "1" * 24), "bits"),
    (lambda s: s["work"]["payload"].__setitem__("length", 16), "length"),
    (lambda s: s.__setitem__("hypothesis", "a different claim"), "hypothesis"),
    (lambda s: s["outcome_rule"].__setitem__("value", 0.5), "outcome_rule"),
    (lambda s: s.__setitem__("prediction", {"expect": "other"}), "prediction"),
    (lambda s: s["work"].__setitem__("kind", "noop_v0"), "work.kind"),
])
def test_changing_an_execution_input_changes_execution_identity(mutate, label):
    base = make_spec(kind="evaluate_bitstring")
    other = copy.deepcopy(base)
    mutate(other)
    if label == "work.kind":
        other["work"]["payload"] = {}
    assert base != other
    assert _spec.spec_hash(base) != _spec.spec_hash(other), \
        "%s changed the experiment without changing spec_hash" % label
    assert _spec.world_name(_spec.spec_hash(base)) != \
        _spec.world_name(_spec.spec_hash(other))


def test_changing_an_execution_input_changes_the_transcript():
    """Not only the hash: the engine really is asked for something else."""
    a = make_spec(kind="evaluate_bitstring", bits="0" * 24)
    b = copy.deepcopy(a)
    b["work"]["payload"]["bits"] = "1" * 24
    assert _transcript(a) != _transcript(b)


def test_provenance_reaches_pew_even_though_it_never_reaches_sfe(conn, schema):
    """The relation must be recorded SOMEWHERE, or the fossil cannot say which
    policy proposed it. It goes to the notebook, not the apparatus."""
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="exploration-x",
                     experiment_spec=make_spec(), family_id="F9",
                     arm_id="C_frozen_S17", candidate_set_id="cs-9",
                     request_key="rk-9", schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    rel = Vivarium._relation(row)
    assert rel["arm_id"] == "C_frozen_S17"
    assert rel["family_id"] == "F9"
    assert rel["request_key"] == "rk-9"
    assert rel["experiment_id"] == eid
