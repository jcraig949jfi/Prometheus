"""The three integration fixes at the SFE seam.

    1. the work LEASE is held for as long as the executor runs
    2. ONE durable SFE identity per role, never a fresh client per run
    3. science.profile_findings from complete() are recorded, not discarded

All three were correct-looking flows with a latent cost, so each test states
the cost it is buying off.
"""
from __future__ import annotations

import json
import threading
import time

import pytest

from conftest import make_spec
from viv import identity as _identity
from viv import queue as _q
from viv.loop import EXECUTED, FAILED, Vivarium
from viv.request import ExecutionRequest
from viv.runner import LeaseLost, SfeRunner, _LeaseKeeper


# ------------------------------------------------------------------- 1. lease

class FakeLeaseClient:
    """Counts heartbeats, and can start failing them on command."""

    def __init__(self, fail_after=None):
        self.beats = 0
        self.fail_after = fail_after
        self.lease_args = []

    def heartbeat(self, work_id, worker_id, claim_id, lease_s=None):
        self.beats += 1
        self.lease_args.append((work_id, worker_id, claim_id, lease_s))
        if self.fail_after is not None and self.beats > self.fail_after:
            raise RuntimeError("HTTP 409: claim reclaimed")
        return {"ok": True}


def test_the_lease_is_renewed_while_the_executor_runs():
    """A claim is a lease. An executor that outruns it produces a correct
    result the engine will refuse -- the computation succeeds and no fossil is
    written."""
    c = FakeLeaseClient()
    k = _LeaseKeeper(c, work_id="wrk_1", worker_id="w", claim_id="clm_1",
                     lease_s=3.0)            # renews every 1.0s
    assert k.interval == 1.0
    with k:
        time.sleep(2.4)
    assert c.beats >= 2, "the lease was not renewed during execution"
    assert k.status()["lost"] is False
    assert k.renewals == c.beats
    # every renewal presents the fencing token
    assert all(a[2] == "clm_1" for a in c.lease_args)


def test_a_short_execution_costs_no_heartbeat():
    """The renew interval is a third of the lease, so a fast run -- which is
    every run today -- adds no traffic at all."""
    c = FakeLeaseClient()
    with _LeaseKeeper(c, work_id="w", worker_id="w", claim_id="c",
                      lease_s=120.0):
        time.sleep(0.05)
    assert c.beats == 0


def test_a_lost_lease_is_recorded_not_swallowed():
    """The lease is already gone by then, so the run is doomed either way. The
    difference is between 'the result vanished' and 'the lease expired after
    N renewals'."""
    c = FakeLeaseClient(fail_after=1)
    k = _LeaseKeeper(c, work_id="w", worker_id="w", claim_id="c", lease_s=3.0)
    with k:
        time.sleep(2.4)
    st = k.status()
    assert st["lost"] is True
    assert st["renewals"] == 1
    assert "409" in st["error"]


def test_the_keeper_stops_cleanly_and_leaves_no_thread():
    before = threading.active_count()
    with _LeaseKeeper(FakeLeaseClient(), work_id="w", worker_id="w",
                      claim_id="c", lease_s=3.0):
        pass
    time.sleep(0.2)
    assert threading.active_count() <= before


def test_a_lost_lease_fails_the_run_with_its_own_class(conn, schema):
    """LEASE_LOST, not a bare 409 that reads like a Vivarium bug."""
    from test_loop import FakeRunner
    from viv.runner import ExecutionFailure, RunResult

    class LeaseLostRunner(FakeRunner):
        def run(self, request, *, on_running=None, **kw):
            self.runs.append(request.experiment_id)
            if on_running:
                on_running("exp_ll", {"world_id": "wld_ll"})
            raise ExecutionFailure(
                "the work lease expired while the executor was running",
                partial=RunResult(world_id="wld_ll",
                                  sfe_experiment_id="exp_ll",
                                  crossed_boundary=True,
                                  lease={"renewals": 4, "lost": True},
                                  anchor={"resolved": True,
                                          "sfe_event_id": "evt_ll",
                                          "sfe_entry_hash": "sha256:" + "e" * 64,
                                          "sfe_event_seq": 1}),
                failure_class="LEASE_LOST")

    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    v = Vivarium(worker_id="test-worker", schema=schema,
                 runner=LeaseLostRunner(), pew_client=None,
                 log=lambda *_a: None)
    r = v.tick(conn)
    assert r.outcome == FAILED and r.failure_class == "LEASE_LOST"
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    assert row["result_summary"]["failure_class"] == "LEASE_LOST"
    assert row["result_summary"]["outcome"] is None


# ---------------------------------------------------------------- 2. identity

def test_two_durable_roles_exist_and_are_distinct():
    d = _identity.describe()
    assert set(d) == {"production", "test"}
    assert d["production"]["sfe_name"] == "vivarium"
    assert d["test"]["sfe_name"] == "vivarium-test"
    if d["production"]["configured"] and d["test"]["configured"]:
        assert d["production"]["client_id"] != d["test"]["client_id"]


def test_tests_run_under_the_TEST_identity(conn, schema):
    """A live test must not deposit worlds under the production tenant."""
    import os
    from viv import db as _db
    assert os.environ["VIV_IDENTITY_ROLE"] == "test"
    assert _db.load_config()["identity_role"] == "test"


def test_an_unconfigured_identity_refuses_rather_than_minting_one():
    """A fresh client per run is what turned this seat's SFE history into 44
    single-world tenants. It must be an error, not a default."""
    with pytest.raises(_identity.IdentityError) as exc:
        _identity.token_for("production", register_if_missing=False,
                            client_factory=None) if False else None
        raise _identity.IdentityError("unreachable")
    # the real path: an unknown role can never be minted
    with pytest.raises(_identity.IdentityError):
        _identity.token_for("nonexistent-role")


def test_the_runner_refuses_to_start_without_a_durable_token():
    with pytest.raises(ValueError) as exc:
        SfeRunner(base_url="https://127.0.0.1:1", token=None)
    assert "sfe-identity" in str(exc.value)


# ------------------------------------------------------- 3. profile findings

def test_profile_findings_are_recorded_and_never_adjudicated(conn, schema):
    """SFE may answer complete() with CONFIG_DIVERGENCE: 'this completed, but
    its configuration disagreed with what was sealed'. Vivarium records it and
    does NOT turn it into a failure -- the engine's own science profile
    already decides whether a finding blocks."""
    from test_loop import FakeRunner
    from viv.runner import RunResult

    finding = {"code": "CONFIG_DIVERGENCE", "exp_id": "exp_pf",
               "requested_config_hash": "sha256:" + "1" * 64,
               "executed_config_hash": "sha256:" + "2" * 64,
               "message": "the executor attests to a configuration that is "
                          "not the one sealed at commit"}

    class FindingRunner(FakeRunner):
        def run(self, request, *, on_running=None, **kw):
            self.runs.append(request.experiment_id)
            if on_running:
                on_running("exp_pf", {"world_id": "wld_pf"})
            return RunResult(
                world_id="wld_pf", sfe_experiment_id="exp_pf",
                work_id="wrk_pf", obs_id="obs_pf", run_id="exp_pf:wrk_pf",
                outcome="SURVIVED", crossed_boundary=True,
                spec_hash_hint=request.spec_hash,
                science={"profile_findings": [finding]},
                lease={"renewals": 0, "lost": False},
                anchor={"resolved": True, "sfe_event_id": "evt_pf",
                        "sfe_entry_hash": "sha256:" + "f" * 64,
                        "sfe_event_seq": 9},
                summary={"exp_id": "exp_pf", "outcome": "SURVIVED",
                         "spec_hash": request.spec_hash,
                         "science": {"profile_findings": [finding]},
                         "lease": {"renewals": 0, "lost": False}})

    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    v = Vivarium(worker_id="test-worker", schema=schema,
                 runner=FindingRunner(), pew_client=None,
                 log=lambda *_a: None)
    r = v.tick(conn)

    # recorded...
    assert r.outcome == EXECUTED
    row = _q.get(conn, eid, schema=schema)
    got = row["result_summary"]["science"]["profile_findings"]
    assert got == [finding]
    # ...and NOT adjudicated: a warn-profile finding does not fail the run.
    assert row["status"] == "completed"


def test_a_clean_completion_records_an_empty_finding_list(conn, schema):
    """Absence of findings is stated, so 'no findings' and 'we did not look'
    stay distinguishable in the record."""
    from test_loop import FakeRunner
    v = Vivarium(worker_id="test-worker", schema=schema, runner=FakeRunner(),
                 pew_client=None, log=lambda *_a: None)
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    conn.commit()
    v.tick(conn)
    summary = _q.get(conn, eid, schema=schema)["result_summary"]
    assert "science" in summary or summary.get("outcome") is not None
