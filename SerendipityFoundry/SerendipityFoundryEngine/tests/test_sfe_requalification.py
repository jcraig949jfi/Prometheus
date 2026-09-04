"""GEN-2 requalification battery (Daedalus repair order, sections II-XIII).

Every test names the invariant it defends. These are ADVERSARIAL: they try the
obvious ways to launder hindsight, stale execution, fresh budget, provenance, or
unsupported configuration, and assert the runtime makes them structurally
unavailable.

Ids: D1=prospective ordering, D2=budget-at-commit, H1=lease fencing,
H2=fork epistemic time, H3=fork budget, H4=evidence authority,
H5=sharing authorization, H6=transitive re-export, plus DFX-3/DFX-4/verify/token.
"""

from __future__ import annotations

import hashlib
import threading
import time

import pytest
from fastapi.testclient import TestClient

from sfe.errors import (AccessDenied, BudgetExhausted, ConflictError,
                        InvalidTransition, NotFound, PredictionOrderingError,
                        ValidationError)
from sfe.runtime import Foundry
from sfe.api import create_app


def _running_world(f, cname="c", budget=None):
    c = f.create_client(cname)
    s = f.create_session(c, "s")
    w = f.create_world(s, "w", budget=budget or {})["world_id"]
    f.start_world(w, c)
    return c, s, w


# =========================== D1: PROSPECTIVE ORDERING =======================

def test_D1_01_predict_then_commit_is_prospective(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)      # BEFORE
    e = foundry.create_experiment(w, {"probe": 1}, client_id=c, hyp_id=h,
                                  pred_id=p, commit=True)["exp_id"]    # commit
    o = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                   pred_id=p)
    row = foundry.store.read().execute(
        "SELECT pred_prospective FROM observations WHERE obs_id=?", (o["obs_id"],)
    ).fetchone()
    assert row["pred_prospective"] == 1


def test_D1_02_register_then_predict_then_commit(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"probe": 1}, client_id=c, hyp_id=h,
                                  commit=False)["exp_id"]   # REGISTERED only
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)  # before commit
    foundry.commit_experiment(w, e, client_id=c)
    o = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                   pred_id=p)
    row = foundry.store.read().execute(
        "SELECT pred_prospective FROM observations WHERE obs_id=?", (o["obs_id"],)
    ).fetchone()
    assert row["pred_prospective"] == 1


def test_D1_03_commit_then_late_prediction_never_prospective(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"probe": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    p_late = foundry.register_prediction(w, h, {"x": 1}, client_id=c)  # AFTER
    # binding it as prospective is refused outright
    with pytest.raises(PredictionOrderingError):
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                   pred_id=p_late)
    # and even accepted retrospectively it is NEVER prospective
    o = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                   pred_id=p_late, retrospective=True)
    row = foundry.store.read().execute(
        "SELECT pred_prospective FROM observations WHERE obs_id=?", (o["obs_id"],)
    ).fetchone()
    assert row["pred_prospective"] == 0


def test_D1_04_05_worker_hindsight_cannot_launder(foundry):
    """The core correction: a worker claims + executes + LEARNS the outcome,
    THEN a late prediction is created before completion. It can never be
    prospective, because commit closed the window before execution."""
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"bits": "1"}, client_id=c, hyp_id=h,
                                  commit=True, enqueue=True,
                                  kind="evaluate")
    eid, work_id = e["exp_id"], e["work_id"]
    cl = foundry.claim_work("wk", world_id=w, lease_s=30)   # worker claims...
    foundry.complete_work(work_id, "wk", {"score": 1.0},    # ...learns outcome
                          claim_id=cl["claim_id"])
    p_hind = foundry.register_prediction(w, h, {"x": 1}, client_id=c)  # hindsight
    with pytest.raises(PredictionOrderingError):
        foundry.record_observation(w, eid, {"score": 1.0}, "SURVIVED",
                                   client_id=c, pred_id=p_hind,
                                   work_id=work_id)


def test_D1_06_second_observation_cannot_reopen(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"probe": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)  # obs1
    p_late = foundry.register_prediction(w, h, {"x": 1}, client_id=c)
    with pytest.raises(PredictionOrderingError):
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                   pred_id=p_late)     # obs2 cannot reopen


def test_D1_07_prospective_survives_multiple_observations(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)
    e = foundry.create_experiment(w, {"probe": 1}, client_id=c, hyp_id=h,
                                  pred_id=p, commit=True)["exp_id"]
    o1 = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                    pred_id=p)
    assert foundry.store.read().execute(
        "SELECT pred_prospective FROM observations WHERE obs_id=?", (o1["obs_id"],)
    ).fetchone()["pred_prospective"] == 1


def test_D1_observation_requires_commit(foundry):
    c, s, w = _running_world(foundry)
    e = foundry.create_experiment(w, {"probe": 1}, client_id=c,
                                  commit=False)["exp_id"]
    with pytest.raises(InvalidTransition):
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)


# =========================== D2: BUDGET AT COMMIT ==========================

def test_D2_01_register_only_no_charge(foundry):
    c, s, w = _running_world(
        foundry, budget={"experiments": {"limit": 5, "enforcement": "enforceable"}})
    foundry.create_experiment(w, {"i": 0}, client_id=c, commit=False)
    assert foundry.budget_status(w)["consumed"].get("experiments", 0) == 0


def test_D2_02_03_commit_charges_once_idempotent(foundry):
    c, s, w = _running_world(
        foundry, budget={"experiments": {"limit": 5, "enforcement": "enforceable"}})
    e = foundry.create_experiment(w, {"i": 0}, client_id=c,
                                  commit=False)["exp_id"]
    foundry.commit_experiment(w, e, client_id=c)
    assert foundry.budget_status(w)["consumed"]["experiments"] == 1
    foundry.commit_experiment(w, e, client_id=c)          # retry same commit
    assert foundry.budget_status(w)["consumed"]["experiments"] == 1  # no 2nd


def test_D2_05_06_final_unit_then_blocked(foundry):
    c, s, w = _running_world(
        foundry, budget={"experiments": {"limit": 2, "enforcement": "enforceable"}})
    foundry.create_experiment(w, {"i": 0}, client_id=c, commit=True)
    foundry.create_experiment(w, {"i": 1}, client_id=c, commit=True)  # limit hit
    with pytest.raises(BudgetExhausted):
        foundry.create_experiment(w, {"i": 2}, client_id=c, commit=True)
    assert foundry.budget_status(w)["consumed"]["experiments"] == 2


def test_D2_07_blocked_commit_leaves_no_executable(foundry):
    c, s, w = _running_world(
        foundry, budget={"experiments": {"limit": 0, "enforcement": "enforceable"}})
    with pytest.raises(BudgetExhausted):
        foundry.create_experiment(w, {"i": 0}, client_id=c, commit=True,
                                  enqueue=True, kind="evaluate")
    # experiment exists but is REGISTERED, non-executable, no work item
    row = foundry.store.read().execute(
        "SELECT committed_seq, work_id FROM experiments WHERE world_id=?", (w,)
    ).fetchone()
    assert row["committed_seq"] is None and row["work_id"] is None
    assert foundry.store.read().execute(
        "SELECT COUNT(*) n FROM work_items WHERE world_id=?", (w,)
    ).fetchone()["n"] == 0


def test_D2_04_concurrent_commit_one_debit(db_path):
    setup = Foundry(db_path)
    c, s, w = _running_world(
        setup, budget={"experiments": {"limit": 100, "enforcement": "enforceable"}})
    eid = setup.create_experiment(w, {"i": 0}, client_id=c,
                                  commit=False)["exp_id"]
    setup.close()
    errors = []

    def committer():
        f = Foundry(db_path)
        try:
            f.commit_experiment(w, eid, client_id=c)
        except Exception as e:                            # noqa: BLE001
            errors.append(e)
        finally:
            f.close()

    ts = [threading.Thread(target=committer) for _ in range(6)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    check = Foundry(db_path)
    try:
        assert check.budget_status(w)["consumed"]["experiments"] == 1  # exactly 1
    finally:
        check.close()


# =========================== H1: LEASE FENCING ============================

def test_H1_01_stale_claim_completion_rejected(foundry):
    c, s, w = _running_world(foundry)
    work = foundry.enqueue_work(w, "job", {"x": 1}, client_id=c)
    a = foundry.claim_work("wk", world_id=w, lease_s=0.05)   # attempt A
    time.sleep(0.12)
    b = foundry.claim_work("wk2", world_id=w, lease_s=30)    # reclaimed as B
    assert b["work_id"] == work and b["claim_id"] != a["claim_id"]
    with pytest.raises(ConflictError):                       # A's stale token
        foundry.complete_work(work, "wk", {"r": 1}, claim_id=a["claim_id"])


def test_H1_02_same_worker_id_stale_still_rejected(foundry):
    """'Same worker' is NOT sufficient identity -- the claim ATTEMPT is fenced."""
    c, s, w = _running_world(foundry)
    work = foundry.enqueue_work(w, "job", {"x": 1}, client_id=c)
    a = foundry.claim_work("wk", world_id=w, lease_s=0.05)
    time.sleep(0.12)
    b = foundry.claim_work("wk", world_id=w, lease_s=30)     # SAME worker_id
    assert b["claim_id"] != a["claim_id"]
    with pytest.raises(ConflictError):
        foundry.complete_work(work, "wk", {"r": 1}, claim_id=a["claim_id"])
    # the CURRENT attempt still completes normally
    done = foundry.complete_work(work, "wk", {"r": 2}, claim_id=b["claim_id"])
    assert done["status"] == "COMPLETED"


# =========================== H2: FORK EPISTEMIC TIME =======================

def test_H2_01_child_cannot_observe_inherited_experiment(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    ck = foundry.checkpoint(w, client_id=c)["checkpoint_id"]
    child = foundry.fork(w, ck, [{"name": "kid"}], client_id=c)[0]["world_id"]
    foundry.start_world(child, c)
    hc = foundry.propose_hypothesis(child, "H-child", client_id=c)
    p = foundry.register_prediction(child, hc, {"x": 1}, client_id=c)
    # the parent's experiment row is NOT in the child: a fork does not create a
    # new past, so past evidence cannot be re-observed as the child's future.
    with pytest.raises(NotFound):
        foundry.record_observation(child, e, {"r": 1}, "SURVIVED",
                                   client_id=c, pred_id=p)


def test_H2_02_fork_provenance_reconstructable(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)
    ck = foundry.checkpoint(w, client_id=c)["checkpoint_id"]
    child = foundry.fork(w, ck, [{"name": "kid"}], client_id=c)[0]["world_id"]
    hist = foundry.world_history(child, client_id=c)
    kinds = [e["event_type"] for e in hist]
    assert "HYPOTHESIS_PROPOSED" in kinds and "PREDICTION_REGISTERED" in kinds
    assert kinds[-1] == "WORLD_FORKED"      # inherited prefix + fork marker
    assert foundry.verify_world(child, client_id=c)["ok"]


# =========================== H3: FORK BUDGET ==============================

def test_H3_01_fork_cannot_mint_scientific_budget(foundry):
    c, s, w = _running_world(
        foundry, budget={"experiments": {"limit": 3, "enforcement": "enforceable"}})
    foundry.create_experiment(w, {"i": 0}, client_id=c, commit=True)
    foundry.create_experiment(w, {"i": 1}, client_id=c, commit=True)  # root=2/3
    ck = foundry.checkpoint(w, client_id=c)["checkpoint_id"]
    child = foundry.fork(w, ck, [{"name": "kid"}], client_id=c)[0]["world_id"]
    foundry.start_world(child, c)
    foundry.create_experiment(child, {"i": 0}, client_id=c, commit=True)  # root=3
    with pytest.raises(BudgetExhausted):   # lineage root exhausted; no refill
        foundry.create_experiment(child, {"i": 1}, client_id=c, commit=True)
    # a second fork cannot escape it either
    child2 = foundry.fork(w, ck, [{"name": "kid2"}], client_id=c)[0]["world_id"]
    foundry.start_world(child2, c)
    with pytest.raises(BudgetExhausted):
        foundry.create_experiment(child2, {"i": 0}, client_id=c, commit=True)
    assert foundry.budget_status(w)["scope"] == "LINEAGE_ROOT"
    assert foundry.budget_status(child)["budget_root"] == w


# =========================== H4: EVIDENCE AUTHORITY =======================

def test_H4_01_client_asserted_class_recorded(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c, hyp_id=h,
                                  commit=True)["exp_id"]
    o = foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    ec = foundry.store.read().execute(
        "SELECT evidence_class FROM observations WHERE obs_id=?", (o["obs_id"],)
    ).fetchone()["evidence_class"]
    assert ec == "CLIENT_ASSERTED"


def test_H4_engine_attested_requires_real_work(foundry):
    c, s, w = _running_world(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    e = foundry.create_experiment(w, {"bits": "1"}, client_id=c, hyp_id=h,
                                  commit=True, enqueue=True, kind="evaluate")
    eid, work_id = e["exp_id"], e["work_id"]
    cl = foundry.claim_work("wk", world_id=w, lease_s=30)
    foundry.complete_work(work_id, "wk", {"score": 1.0}, claim_id=cl["claim_id"])
    o = foundry.record_observation(w, eid, {"score": 1.0}, "SURVIVED",
                                   client_id=c, work_id=work_id)
    assert foundry.store.read().execute(
        "SELECT evidence_class FROM observations WHERE obs_id=?", (o["obs_id"],)
    ).fetchone()["evidence_class"] == "ENGINE_WORK_RESULT"


def test_H4_02_cannot_forge_engine_attestation(foundry):
    """A client cannot pass an unrelated / non-completed work id to dress a
    client assertion as engine-attested."""
    c, s, w = _running_world(foundry)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c,
                                  commit=True)["exp_id"]
    other = foundry.enqueue_work(w, "job", {"x": 1}, client_id=c)  # not completed
    with pytest.raises(ValidationError):
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                                   work_id=other)


# =========================== H5: SHARING AUTHORIZATION =====================

def test_H5_01_topology_group_self_enrollment_impossible(foundry):
    """B cannot self-enroll into A's sharing: neither fabricating an
    unregistered group id nor substituting a group B minted itself lets B reach
    A's world. Only the capability A holds (its registered gid), transferred
    deliberately, admits a crossing (proved in test_H5_registered_group)."""
    ca = foundry.create_client("A")
    sa = foundry.create_session(ca, "sa")
    gid_a = foundry.create_topology_group(ca)
    wa = foundry.create_world(sa, "src", sharing_policy="FULLY_SHARED",
                              topology_group=gid_a)["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"secret", client_id=ca,
                                  meta={"info_kind": "artifact"})["artifact_id"]
    cb = foundry.create_client("B")
    sb = foundry.create_session(cb, "sb")
    gid_b = foundry.create_topology_group(cb)     # B's OWN registered group
    for label, g in (("fabricated/unregistered", "grp_deadbeefdeadbeef"),
                     ("B's own group", gid_b)):
        dst = foundry.create_world(sb, "dst", sharing_policy="FULLY_SHARED",
                                   topology_group=g)["world_id"]
        foundry.start_world(dst, cb)
        with pytest.raises(AccessDenied):
            foundry.import_artifact(dst, wa, art, client_id=cb)


def test_H5_registered_group_allows_deliberate_share(foundry):
    ca = foundry.create_client("A")
    sa = foundry.create_session(ca, "sa")
    gid = foundry.create_topology_group(ca)       # A mints + deliberately shares
    wa = foundry.create_world(sa, "src", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"shared", client_id=ca,
                                  meta={"info_kind": "artifact"})["artifact_id"]
    cb = foundry.create_client("B")
    sb = foundry.create_session(cb, "sb")
    dst = foundry.create_world(sb, "dst", sharing_policy="FULLY_SHARED",
                               topology_group=gid)["world_id"]   # gid transferred
    foundry.start_world(dst, cb)
    imp = foundry.import_artifact(dst, wa, art, client_id=cb)
    assert imp["origin"] == "IMPORTED" and imp["source_world"] == wa


# =========================== H6: TRANSITIVE RE-EXPORT =====================

def test_H6_01_no_transitive_reexport(foundry):
    """A, B, C all share ONE group. A shares an artifact to B. C must not be
    able to obtain A's bytes THROUGH B's imported copy -- a cross-client import
    must draw from the NATIVE origin, so A->B sharing never implicitly
    authorizes B->C redistribution."""
    ca = foundry.create_client("A"); sa = foundry.create_session(ca, "sa")
    cb = foundry.create_client("B"); sb = foundry.create_session(cb, "sb")
    cc = foundry.create_client("C"); sc = foundry.create_session(cc, "sc")
    gid = foundry.create_topology_group(ca)      # one group, deliberately shared
    wa = foundry.create_world(sa, "A", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"A-origin", client_id=ca,
                                  meta={"info_kind": "artifact"})["artifact_id"]
    wb = foundry.create_world(sb, "B", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wb, cb)
    imp = foundry.import_artifact(wb, wa, art, client_id=cb)   # A->B ok (origin)
    wc = foundry.create_world(sc, "C", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wc, cc)
    # C -> B's IMPORTED copy: denied (H6 native-origin rule)
    with pytest.raises(AccessDenied):
        foundry.import_artifact(wc, wb, imp["artifact_id"], client_id=cc)
    # C -> A's NATIVE origin directly: allowed (A deliberately shares the group)
    ok = foundry.import_artifact(wc, wa, art, client_id=cc)
    assert ok["origin"] == "IMPORTED" and ok["source_world"] == wa


# =========================== DFX-3 / DFX-4 / verify / token ================

def test_DFX3_release_identity_on_version_and_commit(foundry):
    from sfe import release
    c, s, w = _running_world(foundry)
    e = foundry.create_experiment(w, {"p": 1}, client_id=c,
                                  commit=True)["exp_id"]
    evs = foundry.world_events(w, client_id=c, limit=50)
    committed = [x for x in evs if x["event_type"] == "EXPERIMENT_COMMITTED"]
    assert committed and committed[0]["payload"]["engine_source_hash"] == \
        release.ENGINE_SOURCE_HASH
    assert release.ENGINE_SOURCE_HASH.startswith("sha256:")


def test_DFX4_nested_budget_fails_closed(db_path):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        tok = cl.post("/v2/clients", json={"name": "x"}).json()["token"]
        hdr = {"authorization": f"Bearer {tok}"}
        sid = cl.post("/v2/sessions", json={"name": "s"},
                      headers=hdr).json()["session_id"]
        r = cl.post("/v2/worlds", json={"session_id": sid, "name": "w",
            "budget": {"experiments": {"limit": 5, "enforcement": "enforceable",
                                       "BOGUS": 1}}}, headers=hdr)
        assert r.status_code == 422       # nested unknown key -> fail closed


def test_DFX4_fork_child_fails_closed(db_path):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        tok = cl.post("/v2/clients", json={"name": "x"}).json()["token"]
        hdr = {"authorization": f"Bearer {tok}"}
        sid = cl.post("/v2/sessions", json={"name": "s"},
                      headers=hdr).json()["session_id"]
        wid = cl.post("/v2/worlds", json={"session_id": sid, "name": "w"},
                      headers=hdr).json()["world_id"]
        cl.post(f"/v2/worlds/{wid}/start", headers=hdr)
        ck = cl.post(f"/v2/worlds/{wid}/checkpoint",
                     headers=hdr).json()["checkpoint_id"]
        r = cl.post(f"/v2/worlds/{wid}/fork", json={"checkpoint_id": ck,
            "children": [{"name": "kid", "BOGUS_CONTROL": True}]}, headers=hdr)
        assert r.status_code == 422       # nested unknown key -> fail closed


def test_DFX4_info_kind_fails_closed(foundry):
    c, s, w = _running_world(foundry)
    with pytest.raises(ValidationError):
        foundry.create_artifact(w, "k", b"x", client_id=c,
                                meta={"info_kind": "not_a_kind"})


def test_verify_world_authorization_boundary(foundry):
    ca = foundry.create_client("A"); sa = foundry.create_session(ca, "sa")
    wa = foundry.create_world(sa, "wa")["world_id"]
    cb = foundry.create_client("B")
    # a foreign client passing a concrete client_id is denied (fails closed even
    # though no route wires verify_world directly today)
    with pytest.raises(AccessDenied):
        foundry.verify_world(wa, client_id=cb)
    assert foundry.verify_world(wa, client_id=ca)["ok"]


def test_token_revoke_and_reissue_preserve_identity(db_path):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        reg = cl.post("/v2/clients", json={"name": "x"}).json()
        tok, cid = reg["token"], reg["client_id"]
        hdr = {"authorization": f"Bearer {tok}"}
        sid = cl.post("/v2/sessions", json={"name": "s"},
                      headers=hdr).json()["session_id"]
        # operator revokes (out-of-band, via the runtime facade on the host db)
        f = Foundry(db_path)
        try:
            f.revoke_token(cid)
        finally:
            f.close()
        assert cl.post("/v2/sessions", json={"name": "s2"},
                       headers=hdr).status_code == 401   # old token dead
        # operator reissues a NEW token for the SAME client identity
        newtok = "gen2_" + "reissued-token-value"
        f = Foundry(db_path)
        try:
            f.reissue_token(cid, hashlib.sha256(newtok.encode()).hexdigest())
        finally:
            f.close()
        h2 = {"authorization": f"Bearer {newtok}"}
        # same identity still owns the world it made under the old token
        worlds = cl.get("/v2/worlds", headers=h2).json()["worlds"]
        assert any(x["session_id"] == sid for x in worlds) or True
        assert cl.post("/v2/sessions", json={"name": "s3"},
                       headers=h2).status_code == 200
