"""Orchestration-safety battery (Daedalus sprint, 2026-09-04).

Every test here is an EXECUTABLE CONSTRAINT derived from a measured failure, not
from a design opinion. Each names the Harmonia boundary probe that produced it,
so a future maintainer can trace the guard back to the evidence that justified
it. These are the four "quiet success" hazards -- the engine used to accept the
call and return 200 while producing something the caller did not mean.

Ids: D-IDEM-1     create-world retry safety        (Harmonia B1 / H2)
     D-ATTEST-1   forced evidence attestation      (Harmonia C3)
     D-CIDGATE-1  organism content-identity gate   (Harmonia A3)
     D-ANCHOR-1   exact causal anchor from write   (Harmonia D1)
     D-LIFECYCLE-1 terminal-state write gate       (Harmonia B4)
     D-WORLDCFG-1 world config completeness        (Harmonia B5)
"""

from __future__ import annotations

import hashlib

import pytest

from sfe.errors import ConflictError, InvalidTransition, ValidationError
from sfe.ids import content_hash


def _client_session(f, name="orch"):
    c = f.create_client(name)
    return c, f.create_session(c, "s")


def _running_world(f, **kw):
    c, s = _client_session(f)
    w = f.create_world(s, "w", **kw)["world_id"]
    f.start_world(w, c)
    return c, s, w


def _rh(body):
    """Mirror the API layer's request hash so runtime tests exercise the same
    conflict semantics the HTTP surface produces."""
    return content_hash({"route": "worlds", "world_id": None, "body": body})


# ===================== D-IDEM-1: CREATE-WORLD RETRY SAFETY ==================

def test_D_IDEM_1_no_key_still_mints_distinct_worlds(foundry):
    """The baseline hazard, unchanged and deliberate: without a key, config is
    NOT identity, so a replicate is a genuinely new world."""
    c, s = _client_session(foundry)
    ids = {foundry.create_world(s, "w", seed_root=424242)["world_id"]
           for _ in range(3)}
    assert len(ids) == 3


def test_D_IDEM_1_same_key_same_request_replays_one_world(foundry):
    """A blind retry after a timeout must NOT create a second causal universe."""
    c, s = _client_session(foundry)
    body = {"session_id": s, "name": "w", "seed_root": 424242}
    first = foundry.create_world(s, "w", seed_root=424242,
                                 idem_key="k1", request_hash=_rh(body))
    again = foundry.create_world(s, "w", seed_root=424242,
                                 idem_key="k1", request_hash=_rh(body))
    assert first["world_id"] == again["world_id"]
    assert again["seed_root"] == 424242
    # and exactly one world exists
    assert len([w for w in foundry.list_worlds(client_id=c)]) == 1


def test_D_IDEM_1_same_key_different_request_is_a_diagnosable_conflict(foundry):
    """A key reused for materially different config must fail loudly, never
    silently return the older world (which would misreport the config in use)."""
    c, s = _client_session(foundry)
    foundry.create_world(s, "w", seed_root=424242, idem_key="k2",
                         request_hash=_rh({"seed_root": 424242}))
    with pytest.raises(ConflictError):
        foundry.create_world(s, "w", seed_root=999999, idem_key="k2",
                             request_hash=_rh({"seed_root": 999999}))


def test_D_IDEM_1_replay_is_atomic_across_a_reopen(foundry, db_path):
    """The key, the world row and WORLD_CREATED commit in ONE transaction, so a
    process that dies mid-retry leaves either both or neither."""
    from sfe.runtime import Foundry
    c, s = _client_session(foundry)
    body = {"seed_root": 7}
    w1 = foundry.create_world(s, "w", seed_root=7, idem_key="k3",
                              request_hash=_rh(body))["world_id"]
    foundry.close()
    f2 = Foundry(db_path)                      # a fresh process would do this
    try:
        w2 = f2.create_world(s, "w", seed_root=7, idem_key="k3",
                             request_hash=_rh(body))["world_id"]
        assert w1 == w2
    finally:
        f2.close()


# ===================== D-ATTEST-1: FORCED ATTESTATION =======================

def _attested_observation(f, c, w, require=False):
    h = f.propose_hypothesis(w, "H", client_id=c)
    e = f.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h, commit=True,
                            enqueue=True)
    eid, work_id = e["exp_id"], e["work_id"]
    cl = f.claim_work("wk", world_id=w, lease_s=30)
    f.complete_work(work_id, "wk", {"score": 1.0}, claim_id=cl["claim_id"])
    return eid, work_id


def test_D_ATTEST_1_default_world_still_allows_client_asserted(foundry):
    """Unattested observation remains LEGAL by default -- exploratory freedom is
    not the thing being closed. It is typed, and it stays typed."""
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    o = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    assert o["evidence_class"] == "CLIENT_ASSERTED"


def test_D_ATTEST_1_required_world_refuses_unattested_observation(foundry):
    """The hazard C3 measured: an orchestrator omits one identifier and silently
    produces weaker evidence. In a require_attestation world it now fails."""
    c, s = _client_session(foundry)
    w = foundry.create_world(s, "w", require_attestation=True)["world_id"]
    foundry.start_world(w, c)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    with pytest.raises(ValidationError):
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)


def test_D_ATTEST_1_required_world_accepts_attested_observation(foundry):
    """The gate must not block the legitimate path it exists to require."""
    c, s = _client_session(foundry)
    w = foundry.create_world(s, "w", require_attestation=True)["world_id"]
    foundry.start_world(w, c)
    eid, work_id = _attested_observation(foundry, c, w)
    o = foundry.record_observation(w, eid, {"score": 1.0}, "SURVIVED",
                                   client_id=c, work_id=work_id)
    assert o["evidence_class"] == "ENGINE_WORK_RESULT"


def test_D_ATTEST_1_flag_is_visible_on_the_world(foundry):
    """A consumer must be able to read the evidence regime WITHOUT running an
    observation to find out."""
    c, s = _client_session(foundry)
    w = foundry.create_world(s, "w", require_attestation=True)
    assert w["require_attestation"] is True
    assert foundry.get_world(w["world_id"], c)["require_attestation"] is True


# ===================== D-CIDGATE-1: CONTENT-IDENTITY GATE ===================

def test_D_CIDGATE_1_matching_digest_is_stored(foundry):
    c, s, w = _running_world(foundry)
    data = b"organism-bytes-v1"
    good = "sha256:" + hashlib.sha256(data).hexdigest()
    a = foundry.create_artifact(w, "organism", data, client_id=c,
                                expected_blob_hash=good)
    assert a["blob_hash"] == good


def test_D_CIDGATE_1_mismatch_fails_closed_and_stores_nothing(foundry):
    """A3: corrupted bytes used to be stored as a valid artifact with an honest
    digest of the WRONG object. Asserting the identity now refuses it."""
    c, s, w = _running_world(foundry)
    intended = b"organism-bytes-v1"
    corrupt = b"organism-bytes-v1-CORRUPTED"
    claim = "sha256:" + hashlib.sha256(intended).hexdigest()
    before = len(foundry.world_events(w, client_id=c, limit=1000))
    with pytest.raises(ValidationError):
        foundry.create_artifact(w, "organism", corrupt, client_id=c,
                                expected_blob_hash=claim)
    after = foundry.world_events(w, client_id=c, limit=1000)
    assert len(after) == before, "a rejected artifact must append NO event"


def test_D_CIDGATE_1_bare_hex_is_accepted_as_the_same_assertion(foundry):
    c, s, w = _running_world(foundry)
    data = b"organism-bytes-v1"
    bare = hashlib.sha256(data).hexdigest()          # no "sha256:" prefix
    a = foundry.create_artifact(w, "organism", data, client_id=c,
                                expected_blob_hash=bare)
    assert a["blob_hash"] == "sha256:" + bare


def test_D_CIDGATE_1_absent_assertion_keeps_old_behaviour(foundry):
    """The gate is opt-in: bytes with no assertion are still content-addressed
    exactly as before (this endpoint has other, non-organism callers)."""
    c, s, w = _running_world(foundry)
    a = foundry.create_artifact(w, "note", b"anything", client_id=c)
    assert a["blob_hash"] == "sha256:" + hashlib.sha256(b"anything").hexdigest()


# ===================== D-ANCHOR-1: EXACT CAUSAL ANCHOR ======================

def test_D_ANCHOR_1_observation_returns_its_own_event_identity(foundry):
    """D1: a caller that has to SEARCH the ledger for 'its' event can pick a
    wrong-but-real one and pass every downstream shape check. The write now
    hands back the exact anchor, so the search never happens."""
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    o = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    for k in ("obs_id", "event_id", "entry_hash", "event_seq", "world_index",
              "evidence_class", "evidence_role"):
        assert k in o, k
    evs = {ev["event_id"]: ev for ev in
           foundry.world_events(w, client_id=c, limit=1000)}
    anchor = evs[o["event_id"]]
    assert anchor["event_type"] == "OBSERVATION_RECORDED"
    assert anchor["entry_hash"] == o["entry_hash"]
    assert anchor["refs"]["obs_id"] == o["obs_id"]


def test_D_ANCHOR_1_anchor_is_unique_per_observation(foundry):
    """Two observations in one world must not be able to collide on an anchor --
    otherwise 'the event this run produced' is still ambiguous."""
    c, s, w = _running_world(foundry)
    anchors = []
    for i in range(3):
        h = foundry.propose_hypothesis(w, "H%d" % i, client_id=c)
        e = foundry.create_experiment(w, {"p": i}, client_id=c, hyp_id=h,
                                      commit=True)["exp_id"]
        anchors.append(foundry.record_observation(
            w, e, {"r": i}, "SURVIVED", client_id=c)["entry_hash"])
    assert len(set(anchors)) == 3


# ===================== D-LIFECYCLE-1: TERMINAL-STATE GATE ===================

def test_D_LIFECYCLE_1_terminated_world_refuses_new_science(foundry):
    """B4 measured artifact-after-terminate. When probed properly it generalized
    to hypotheses and budget debits too. TERMINATED now ends the write
    lifetime."""
    c, s, w = _running_world(foundry, budget={"ticks": {"limit": 100}})
    foundry.terminate_world(w, c)
    with pytest.raises(InvalidTransition):
        foundry.create_artifact(w, "post", b"x", client_id=c)
    with pytest.raises(InvalidTransition):
        foundry.propose_hypothesis(w, "post", client_id=c)
    with pytest.raises(InvalidTransition):
        foundry.consume_budget(w, "ticks", 1, client_id=c)


def test_D_LIFECYCLE_1_reads_still_work_after_termination(foundry):
    """A terminated world must remain fully READABLE -- it is the evidence."""
    c, s, w = _running_world(foundry)
    foundry.create_artifact(w, "pre", b"x", client_id=c)
    foundry.terminate_world(w, c)
    assert foundry.get_world(w, c)["state"] == "TERMINATED"
    assert foundry.world_events(w, client_id=c, limit=10)
    assert foundry.world_status(w, client_id=c)["ledger_integrity_ok"]


def test_D_LIFECYCLE_1_fork_of_a_terminated_world_is_permitted(foundry):
    """Explicitly permitted: replay / counterfactual / fixed-world rerun all
    need to branch from a FINISHED world. Forbidding this would break the
    experiment designs the engine exists to serve."""
    c, s, w = _running_world(foundry)
    ck = foundry.checkpoint(w, client_id=c)
    foundry.terminate_world(w, c)
    ck2 = foundry.checkpoint(w, client_id=c)       # snapshot of final state
    assert ck2["checkpoint_id"]
    kids = foundry.fork(w, ck["checkpoint_id"], [{"name": "replay"}],
                        client_id=c)
    child = kids[0]["world_id"]
    foundry.start_world(child, c)
    assert foundry.create_artifact(child, "in-child", b"y", client_id=c)


def test_D_LIFECYCLE_1_inflight_work_can_still_settle(foundry):
    """A worker holding a lease when the world is terminated must be able to
    report what it actually did; stranding the lease would make the ledger
    misreport the run."""
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h,
                                  commit=True, enqueue=True)
    cl = foundry.claim_work("wk", world_id=w, lease_s=30)
    foundry.terminate_world(w, c)
    done = foundry.complete_work(e["work_id"], "wk", {"score": 1.0},
                                 claim_id=cl["claim_id"])
    assert done["status"] == "COMPLETED"


def test_D_LIFECYCLE_1_no_new_claim_from_a_terminated_world(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h, commit=True,
                              enqueue=True)
    foundry.terminate_world(w, c)
    assert foundry.claim_work("wk", world_id=w, lease_s=30) is None


# ===================== D-WORLDCFG-1: CONFIG COMPLETENESS ====================

def test_D_WORLDCFG_1_get_world_carries_the_replay_relevant_config(foundry):
    """B5: budget was absent from get_world, so a fossil could not record the
    enforcement regime its run happened under."""
    c, s = _client_session(foundry)
    w = foundry.create_world(s, "w", seed_root=424242,
                             budget={"ticks": {"limit": 10,
                                               "enforcement": "enforceable"}})
    got = foundry.get_world(w["world_id"], c)
    assert got["seed_root"] == 424242
    assert got["sharing_policy"] == "ISOLATED"
    assert got["budget"]["ticks"]["limit"] == 10
    assert got["budget"]["ticks"]["enforcement"] == "enforceable"
    assert got["require_attestation"] is False


def test_D_WORLDCFG_1_list_worlds_scopes_by_state_and_session(foundry):
    """Enumeration exists so an orchestrator can answer which worlds are mine /
    active / finished / cleanup candidates. It is scoping, NOT a search engine."""
    c, s = _client_session(foundry)
    s2 = foundry.create_session(c, "s2")
    a = foundry.create_world(s, "a")["world_id"]
    b = foundry.create_world(s, "b")["world_id"]
    x = foundry.create_world(s2, "x")["world_id"]
    foundry.start_world(a, c)
    foundry.terminate_world(b, c)
    assert len(foundry.list_worlds(client_id=c)) == 3
    assert [w["world_id"] for w in
            foundry.list_worlds(client_id=c, state="RUNNING")] == [a]
    assert [w["world_id"] for w in
            foundry.list_worlds(client_id=c, state="TERMINATED")] == [b]
    assert [w["world_id"] for w in
            foundry.list_worlds(client_id=c, session_id=s2)] == [x]
    with pytest.raises(ValidationError):
        foundry.list_worlds(client_id=c, state="NOT_A_STATE")


def test_D_WORLDCFG_1_enumeration_never_crosses_clients(foundry):
    """The isolation guarantee this endpoint has always had, pinned so the new
    filters cannot erode it."""
    c1, s1 = _client_session(foundry, "one")
    c2, s2 = _client_session(foundry, "two")
    foundry.create_world(s1, "mine")
    foundry.create_world(s2, "theirs")
    assert len(foundry.list_worlds(client_id=c1)) == 1
    assert len(foundry.list_worlds(client_id=c2)) == 1


# ===================== HTTP SURFACE: header + query plumbing ================
# The runtime tests above prove the SEMANTICS. These prove the wire contract --
# that the Idempotency-Key header, the filter query params, the assertion field
# and the anchor response actually reach and leave the runtime over HTTP.

import pytest as _pytest
from fastapi.testclient import TestClient

from sfe.api import create_app


@_pytest.fixture
def http(tmp_path):
    app = create_app(str(tmp_path / "orch_api.db"))
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _auth(c, name="orch"):
    r = c.post("/v2/clients", json={"name": name})
    tok = r.json()["token"]
    h = {"authorization": "Bearer " + tok}
    s = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    return h, s["session_id"]


def test_http_D_IDEM_1_key_header_makes_create_world_retry_safe(http):
    h, sid = _auth(http)
    body = {"session_id": sid, "name": "w", "seed_root": 424242, "budget": {}}
    k = dict(h, **{"Idempotency-Key": "orch-key-1"})
    a = http.post("/v2/worlds", json=body, headers=k)
    b = http.post("/v2/worlds", json=body, headers=k)
    assert a.status_code == b.status_code == 200, (a.text, b.text)
    assert a.json()["world_id"] == b.json()["world_id"]
    listed = http.get("/v2/worlds", headers=h).json()["worlds"]
    assert len(listed) == 1, "a retry must not leave a second world behind"


def test_http_D_IDEM_1_conflicting_body_under_one_key_is_409(http):
    h, sid = _auth(http)
    k = dict(h, **{"Idempotency-Key": "orch-key-2"})
    http.post("/v2/worlds", json={"session_id": sid, "name": "w",
                                  "seed_root": 1, "budget": {}}, headers=k)
    r = http.post("/v2/worlds", json={"session_id": sid, "name": "w",
                                      "seed_root": 2, "budget": {}}, headers=k)
    assert r.status_code == 409, r.text


def test_http_D_ANCHOR_1_observation_response_carries_the_anchor(http):
    h, sid = _auth(http)
    wid = http.post("/v2/worlds", json={"session_id": sid, "name": "w",
                                        "budget": {}},
                    headers=h).json()["world_id"]
    http.post("/v2/worlds/%s/start" % wid, headers=h)
    hyp = http.post("/v2/worlds/%s/hypotheses" % wid, json={"statement": "H"},
                    headers=h).json()["hyp_id"]
    eid = http.post("/v2/worlds/%s/experiments" % wid,
                    json={"spec": {"r": 1}, "hyp_id": hyp},
                    headers=h).json()["exp_id"]
    o = http.post("/v2/worlds/%s/observations" % wid,
                  json={"exp_id": eid, "content": {"got": 1},
                        "outcome": "SURVIVED"}, headers=h)
    assert o.status_code == 200, o.text
    body = o.json()
    for k in ("obs_id", "event_id", "entry_hash", "event_seq",
              "evidence_class"):
        assert k in body, k
    evs = http.get("/v2/worlds/%s/events?limit=100" % wid,
                   headers=h).json()["events"]
    match = [e for e in evs if e["event_id"] == body["event_id"]]
    assert len(match) == 1
    assert match[0]["event_type"] == "OBSERVATION_RECORDED"


def test_http_D_CIDGATE_1_expected_hash_is_enforced_over_the_wire(http):
    import base64
    h, sid = _auth(http)
    wid = http.post("/v2/worlds", json={"session_id": sid, "name": "w",
                                        "budget": {}},
                    headers=h).json()["world_id"]
    http.post("/v2/worlds/%s/start" % wid, headers=h)
    intended = b"organism-bytes-v1"
    good = "sha256:" + hashlib.sha256(intended).hexdigest()
    ok = http.post("/v2/worlds/%s/artifacts" % wid,
                   json={"kind": "organism",
                         "data_b64": base64.b64encode(intended).decode(),
                         "expected_blob_hash": good}, headers=h)
    assert ok.status_code == 200, ok.text
    bad = http.post("/v2/worlds/%s/artifacts" % wid,
                    json={"kind": "organism",
                          "data_b64": base64.b64encode(b"CORRUPT").decode(),
                          "expected_blob_hash": good}, headers=h)
    assert bad.status_code == 422, bad.text
    assert "content identity mismatch" in bad.text


def test_http_D_WORLDCFG_1_filters_and_budget_over_the_wire(http):
    h, sid = _auth(http)
    mk = lambda n: http.post("/v2/worlds",
                             json={"session_id": sid, "name": n,
                                   "budget": {"ticks": {"limit": 5,
                                                        "enforcement":
                                                        "enforceable"}}},
                             headers=h).json()["world_id"]
    a, b = mk("a"), mk("b")
    http.post("/v2/worlds/%s/start" % a, headers=h)
    http.post("/v2/worlds/%s/terminate" % b, headers=h)
    run = http.get("/v2/worlds?state=RUNNING", headers=h).json()["worlds"]
    assert [w["world_id"] for w in run] == [a]
    term = http.get("/v2/worlds?state=TERMINATED", headers=h).json()["worlds"]
    assert [w["world_id"] for w in term] == [b]
    bad = http.get("/v2/worlds?state=NOPE", headers=h)
    assert bad.status_code == 422, bad.text
    got = http.get("/v2/worlds/%s" % a, headers=h).json()
    assert got["budget"]["ticks"]["limit"] == 5
    assert got["require_attestation"] is False


def test_http_D_LIFECYCLE_1_terminated_world_refuses_writes_over_the_wire(http):
    import base64
    h, sid = _auth(http)
    wid = http.post("/v2/worlds", json={"session_id": sid, "name": "w",
                                        "budget": {}},
                    headers=h).json()["world_id"]
    http.post("/v2/worlds/%s/start" % wid, headers=h)
    http.post("/v2/worlds/%s/terminate" % wid, headers=h)
    r = http.post("/v2/worlds/%s/artifacts" % wid,
                  json={"kind": "post",
                        "data_b64": base64.b64encode(b"x").decode()}, headers=h)
    assert r.status_code == 409, r.text
    assert "TERMINATED" in r.text
    # reads still answer
    assert http.get("/v2/worlds/%s/events?limit=5" % wid,
                    headers=h).status_code == 200


# ===================== D-REPLAY-1: THE ACTION IS RECOVERABLE ================

def test_D_REPLAY_1_frozen_spec_is_readable_and_matches_the_sealed_hash(foundry):
    """Harmonia scored exact_action MISSING and concluded replay needs the repo
    checkout. The action was never missing from the ENGINE -- spec_hash is
    sealed in EXPERIMENT_COMMITTED -- it was unreachable from outside. Recover
    the spec and re-derive the hash the ledger committed to."""
    c, s, w = _running_world(foundry)
    spec = {"action": "encounter", "ticks": 32, "seed": 424242}
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, spec, client_id=c, hyp_id=h, commit=True)
    got = foundry.get_experiment(w, e["exp_id"], client_id=c)
    assert got["spec"] == spec, "the exact action must come back byte-equal"
    assert got["spec_hash"] == content_hash(spec)
    committed = [ev for ev in foundry.world_events(w, client_id=c, limit=1000)
                 if ev["event_type"] == "EXPERIMENT_COMMITTED"]
    assert len(committed) == 1
    sealed = committed[0]["payload"]["spec_hash"]
    assert sealed == got["spec_hash"], "recovered spec must hash to the sealed value"
    assert committed[0]["payload"]["engine_source_hash"]


def test_D_REPLAY_1_observations_are_recoverable_for_comparison(foundry):
    """A replay is only meaningful against the outcome it replays."""
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"a": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    o = foundry.record_observation(w, e, {"score": 0.5}, "SURVIVED",
                                   client_id=c)
    got = foundry.list_observations(w, client_id=c, exp_id=e)
    assert len(got) == 1
    assert got[0]["obs_id"] == o["obs_id"]
    assert got[0]["content"] == {"score": 0.5}
    assert got[0]["evidence_class"] == "CLIENT_ASSERTED"


def test_D_REPLAY_1_experiment_read_is_client_scoped(foundry):
    """The new read path must not become a cross-experimenter oracle."""
    from sfe.errors import AccessDenied
    c1, s1 = _client_session(foundry, "one")
    c2, s2 = _client_session(foundry, "two")
    w = foundry.create_world(s1, "w")["world_id"]
    foundry.start_world(w, c1)
    e = foundry.create_experiment(w, {"secret": 1}, client_id=c1,
                                  commit=True)["exp_id"]
    with pytest.raises(AccessDenied):
        foundry.get_experiment(w, e, client_id=c2)
    with pytest.raises(AccessDenied):
        foundry.list_experiments(w, client_id=c2)
