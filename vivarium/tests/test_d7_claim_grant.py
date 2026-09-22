"""D7 (backlog, opened 2026-09-10; closed 2026-09-16): the execution path
refuses to create a world unless it is executing a CLAIMED row.

Seven ledger commits from 2026-09-06 (+2 from a test on 09-11) carry this
seat's derived world name and match no register row; nobody can adjudicate
them. The loop now issues a ClaimGrant for the row it claimed, and the
runner refuses without one BEFORE any engine call.

    POSITIVE  the queue path (tick -> dispatch) hands the runner a grant
              naming the claimed row and this worker, and the run proceeds
    NEGATIVE  a direct runner.run with no grant is refused with
              failure_class UNCLAIMED_EXECUTION and ZERO engine calls;
              constructing the production client with require_grant=False
              is refused at construction
    CHEAT     a grant for another row, or for another worker, is refused
              the same way; a runner double built without __init__ (no
              flag at all) still requires a grant (fails closed); the
              marked test identity may waive it, and does so visibly
"""
from __future__ import annotations

import pytest

from viv import queue as _q
from viv import spec as _spec
from viv.loop import EXECUTED, Vivarium
from viv.request import ClaimGrant, ExecutionRequest
from viv.runner import ExecutionFailure, RunResult, SfeRunner
from tests.test_blinding import RecordingClient, _runner_over
from tests.test_loop import make_spec


def _fresh_runner(client, sealed):
    """A double that did NOT waive the grant (the helper's waiver removed)."""
    r = _runner_over(client, sealed)
    del r.require_grant
    return r


def _request(spec):
    sealed = _spec.spec_hash(spec)
    return ExecutionRequest(experiment_id="00000000-0000-4000-8000-0000000000d7",
                            spec_json=_spec.canonical_bytes(spec), spec_hash=sealed), sealed


# ------------------------------------------------------------- positive

def test_positive_the_queue_path_issues_a_grant_for_the_claimed_row(conn, schema):
    seen = {}

    class GrantRecorder:
        def run(self, request, *, on_running=None, grant=None, **_kw):
            seen["grant"] = grant
            seen["eid"] = request.experiment_id
            exp = "exp_d7"
            if on_running:
                on_running(exp, {"world_id": "wld_d7"})
            return RunResult(world_id="wld_d7", sfe_experiment_id=exp, work_id="w",
                             obs_id="o", run_id="r", outcome="INCONCLUSIVE",
                             anchor={"resolved": True, "sfe_event_id": "e",
                                     "sfe_entry_hash": "sha256:" + "a" * 64,
                                     "sfe_event_seq": 1},
                             work_result={}, spec_hash_hint=request.spec_hash,
                             crossed_boundary=True,
                             summary={"exp_id": exp, "outcome": "INCONCLUSIVE",
                                      "spec_hash": request.spec_hash})

    eid = _q.enqueue(conn, created_by="t", source_reason="D7", experiment_spec=make_spec(),
                     schema=schema)
    conn.commit()
    v = Vivarium(worker_id="d7-worker", schema=schema, runner=GrantRecorder(),
                 pew_client=None, log=lambda *_a: None)
    assert v.tick(conn).outcome == EXECUTED
    g = seen["grant"]
    assert isinstance(g, ClaimGrant)
    assert g.experiment_id == str(eid) == seen["eid"]
    assert g.worker_id == "d7-worker" and g.claimed_at


def test_positive_a_real_runner_accepts_a_covering_grant(conn, schema):
    spec = make_spec()
    req, sealed = _request(spec)
    client = RecordingClient()
    r = _fresh_runner(client, sealed)
    out = r.run(req, grant=ClaimGrant(experiment_id=req.experiment_id,
                                      worker_id="test-worker", claimed_at="t"))
    assert out.crossed_boundary is True
    assert client.calls, "the engine was called"


# ------------------------------------------------------------- negative

def test_negative_a_direct_run_without_a_grant_is_refused_before_any_engine_call():
    spec = make_spec()
    req, sealed = _request(spec)
    client = RecordingClient()
    r = _fresh_runner(client, sealed)
    with pytest.raises(ExecutionFailure) as exc:
        r.run(req)
    assert exc.value.failure_class == "UNCLAIMED_EXECUTION"
    assert exc.value.partial.crossed_boundary is False
    assert client.calls == [], "no engine call may precede the refusal"


def test_negative_the_production_client_cannot_waive_the_grant_at_construction():
    with pytest.raises(ValueError) as exc:
        SfeRunner(base_url="https://127.0.0.1:1", token=None,
                  client_name="vivarium", require_grant=False)
    assert "D7" in str(exc.value)
    # the marked identity gets PAST the D7 guard (construction then fails
    # on the closed port, which is the next check and not this one)
    with pytest.raises(Exception) as exc2:
        SfeRunner(base_url="https://127.0.0.1:1", token="t" * 32,
                  client_name="vivarium-test", require_grant=False, timeout=2.0)
    assert "D7" not in str(exc2.value)


# ---------------------------------------------------------------- cheat

@pytest.mark.parametrize("grant", [
    ClaimGrant(experiment_id="00000000-0000-4000-8000-00000000beef",
               worker_id="test-worker", claimed_at="t"),          # other row
    ClaimGrant(experiment_id="00000000-0000-4000-8000-0000000000d7",
               worker_id="someone-else", claimed_at="t"),         # other worker
    "not a grant",
])
def test_cheat_a_grant_that_does_not_cover_this_request_is_refused(grant):
    spec = make_spec()
    req, sealed = _request(spec)
    client = RecordingClient()
    r = _fresh_runner(client, sealed)
    with pytest.raises(ExecutionFailure) as exc:
        r.run(req, grant=grant)
    assert exc.value.failure_class == "UNCLAIMED_EXECUTION"
    assert client.calls == []


def test_cheat_a_double_with_no_flag_at_all_fails_closed():
    spec = make_spec()
    req, sealed = _request(spec)
    r = _fresh_runner(RecordingClient(), sealed)
    assert not hasattr(r, "require_grant")
    with pytest.raises(ExecutionFailure):
        r.run(req)


def test_cheat_the_grant_carries_no_provenance():
    """Three fields, none of them created_by / arm / reason; the blinding
    boundary is unchanged by D7."""
    import dataclasses
    names = {f.name for f in dataclasses.fields(ClaimGrant)}
    assert names == {"experiment_id", "worker_id", "claimed_at"}
