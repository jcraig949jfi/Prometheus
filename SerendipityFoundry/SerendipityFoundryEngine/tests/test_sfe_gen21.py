"""SFE GEN-2.1 (Crossing Hardening) gate battery + self-hostile probes.

Gates G11-G16 plus the section-VI adversarial probes. Each test names the
invariant it defends and attacks the obvious bypass.
"""

from __future__ import annotations

import base64
import hashlib

import pytest
from fastapi.testclient import TestClient

from sfe import release
from sfe.errors import (AccessDenied, ConflictError, NotFound,
                        ValidationError)
from sfe.ids import blob_hash, content_hash
from sfe.runtime import Foundry, SHARING_POLICIES, INFO_KINDS
from sfe.api import create_app


def _rw(f, name="c", budget=None, policy="ISOLATED", group=None):
    c = f.create_client(name)
    s = f.create_session(c, "s")
    w = f.create_world(s, "w", sharing_policy=policy, topology_group=group,
                       budget=budget or {})["world_id"]
    f.start_world(w, c)
    return c, s, w


# =========================== G11 CONTENT VISIBILITY ========================

def test_G11_native_content_retrievable_and_hash_verifies(foundry):
    c, s, w = _rw(foundry)
    art = foundry.create_artifact(w, "k", b"native-bytes", client_id=c,
                                  meta={"info_kind": "artifact"})["artifact_id"]
    got = foundry.get_artifact_content(w, art, client_id=c)
    assert got["origin"] == "NATIVE"
    content = base64.b64decode(got["content_b64"])
    assert content == b"native-bytes"
    assert blob_hash(content) == got["source_hash"]      # hash-verifiable


def test_G11_imported_content_retrievable_hashes_to_source(foundry):
    ca = foundry.create_client("A"); sa = foundry.create_session(ca, "sa")
    gid = foundry.create_topology_group(ca)
    wa = foundry.create_world(sa, "A", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"A-secret", client_id=ca,
                                  meta={"info_kind": "success"})["artifact_id"]
    cb = foundry.create_client("B"); sb = foundry.create_session(cb, "sb")
    wb = foundry.create_world(sb, "B", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wb, cb)
    imp = foundry.import_artifact(wb, wa, art, client_id=cb)
    got = foundry.get_artifact_content(wb, imp["artifact_id"], client_id=cb)
    assert got["origin"] == "IMPORTED" and got["source_world"] == wa
    content = base64.b64decode(got["content_b64"])
    assert content == b"A-secret"                         # the source's bytes
    assert blob_hash(content) == got["source_hash"]
    assert got["visibility_basis"]["visibility"] == "IMPORTED"


def test_G11_probe1_no_content_without_import(foundry):
    """Bilateral group membership alone does NOT confer content visibility --
    only an actual import does."""
    ca = foundry.create_client("A"); sa = foundry.create_session(ca, "sa")
    gid = foundry.create_topology_group(ca)
    wa = foundry.create_world(sa, "A", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"A-secret", client_id=ca,
                                  meta={"info_kind": "success"})["artifact_id"]
    cb = foundry.create_client("B"); sb = foundry.create_session(cb, "sb")
    wb = foundry.create_world(sb, "B", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wb, cb)
    # B is in the same group but has NOT imported -> no local row -> denied
    with pytest.raises(NotFound):
        foundry.get_artifact_content(wb, art, client_id=cb)


def test_G11_probe2_3_origin_id_and_guess_denied(foundry):
    ca = foundry.create_client("A"); sa = foundry.create_session(ca, "sa")
    wa = foundry.create_world(sa, "A")["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"A-secret", client_id=ca)[
        "artifact_id"]
    cb = foundry.create_client("B"); sb = foundry.create_session(cb, "sb")
    wb = foundry.create_world(sb, "B")["world_id"]
    foundry.start_world(wb, cb)
    # retrieve A's native artifact via its ORIGIN id, from B's world -> denied
    with pytest.raises(NotFound):
        foundry.get_artifact_content(wb, art, client_id=cb)
    # guessed id -> denied
    with pytest.raises(NotFound):
        foundry.get_artifact_content(wb, "art_deadbeef", client_id=cb)
    # B cannot even name A's WORLD (403), let alone read its content
    with pytest.raises(AccessDenied):
        foundry.get_artifact_content(wa, art, client_id=cb)


def test_G11_probe14_terminated_world_no_side_effect_leak(foundry):
    c, s, w = _rw(foundry)
    art = foundry.create_artifact(w, "k", b"x", client_id=c)["artifact_id"]
    n_events_before = len(foundry.world_events(w, client_id=c, limit=1000))
    foundry.get_artifact_content(w, art, client_id=c)   # a read
    n_events_after = len(foundry.world_events(w, client_id=c, limit=1000))
    assert n_events_after == n_events_before             # read did not append


# =========================== G12 POLICY COHERENCE =========================

def test_G12_every_policy_maps_onto_ontology():
    for pol, kinds in SHARING_POLICIES.items():
        assert kinds <= INFO_KINDS, (pol, kinds - INFO_KINDS)
    assert "success" in INFO_KINDS
    assert SHARING_POLICIES["SUCCESSES_ONLY"] == frozenset({"success"})


def test_G12_info_kind_fails_closed(foundry):
    c, s, w = _rw(foundry)
    with pytest.raises(ValidationError):
        foundry.create_artifact(w, "k", b"x", client_id=c,
                                meta={"info_kind": "triumph"})


# =========================== G13 BINDING UNIQUENESS =======================

def _committed_exp(f, w, c, hyp=None):
    return f.create_experiment(w, {"i": 1}, client_id=c, hyp_id=hyp,
                               commit=True)["exp_id"]


def test_G13_probe8_duplicate_binding_rejected_without_replication(foundry):
    c, s, w = _rw(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)
    e1 = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e1, {"r": 1}, "SURVIVED", client_id=c,
                               pred_id=p)                 # ORIGINAL
    e2 = _committed_exp(foundry, w, c, h)
    with pytest.raises(ConflictError):                   # silent duplicate -> no
        foundry.record_observation(w, e2, {"r": 1}, "SURVIVED", client_id=c,
                                   pred_id=p)
    # explicit replication is accepted and TYPED
    o3 = foundry.record_observation(w, e2, {"r": 1}, "SURVIVED", client_id=c,
                                    pred_id=p, replication=True)
    role = foundry.store.read().execute(
        "SELECT evidence_role FROM observations WHERE obs_id=?", (o3["obs_id"],)
    ).fetchone()["evidence_role"]
    assert role == "REPLICATION"


def test_G13_probe9_replication_cannot_improve_original(foundry):
    """FALSIFIED original, then a 'successful' replication -- the hypothesis must
    stay FALSIFIED; a retest never re-adjudicates."""
    c, s, w = _rw(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)
    e1 = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e1, {"r": 0}, "FALSIFIED", client_id=c,
                               pred_id=p)
    assert foundry.store.read().execute(
        "SELECT state FROM hypotheses WHERE hyp_id=?", (h,)
    ).fetchone()["state"] == "FALSIFIED"
    e2 = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e2, {"r": 1}, "SURVIVED", client_id=c,
                               pred_id=p, replication=True)
    # unchanged: the replication did not flip the original adjudication
    assert foundry.store.read().execute(
        "SELECT state FROM hypotheses WHERE hyp_id=?", (h,)
    ).fetchone()["state"] == "FALSIFIED"
    # and no second CLAIM_* event was emitted by the replication
    claims = [e for e in foundry.world_events(w, client_id=c, limit=1000)
              if e["event_type"] in ("CLAIM_SURVIVED", "CLAIM_FALSIFIED")]
    assert len(claims) == 1 and claims[0]["event_type"] == "CLAIM_FALSIFIED"


# =========================== G14 RELEASE CONTINUITY =======================

def test_G14_probe11_identity_header_on_every_response_and_discontinuity(db_path,
                                                                         monkeypatch):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        r1 = cl.get("/v2/version")
        assert r1.headers["X-SFE-Engine-Source-Hash"] == release.ENGINE_SOURCE_HASH
        # a NON-version endpoint also carries the header
        tok = cl.post("/v2/clients", json={"name": "x"}).json()["token"]
        r2 = cl.post("/v2/sessions", json={"name": "s"},
                     headers={"authorization": f"Bearer {tok}"})
        assert r2.headers["X-SFE-Engine-Source-Hash"] == release.ENGINE_SOURCE_HASH
        # simulate the loaded build changing between two calls
        monkeypatch.setattr(release, "ENGINE_SOURCE_HASH", "sha256:DIFFERENT")
        r3 = cl.get("/v2/version")
        assert r3.headers["X-SFE-Engine-Source-Hash"] == "sha256:DIFFERENT"
        assert r3.headers["X-SFE-Engine-Source-Hash"] != \
            r1.headers["X-SFE-Engine-Source-Hash"]        # discontinuity visible


# =========================== G15 RETRY EXACTNESS =========================

def test_G15_retry_same_key_one_object(db_path):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        tok = cl.post("/v2/clients", json={"name": "x"}).json()["token"]
        hdr = {"authorization": f"Bearer {tok}"}
        sid = cl.post("/v2/sessions", json={"name": "s"},
                      headers=hdr).json()["session_id"]
        wid = cl.post("/v2/worlds", json={"session_id": sid, "name": "w"},
                      headers=hdr).json()["world_id"]
        cl.post(f"/v2/worlds/{wid}/start", headers=hdr)
        h = dict(hdr, **{"Idempotency-Key": "k1"})
        r1 = cl.post(f"/v2/worlds/{wid}/hypotheses",
                     json={"statement": "H"}, headers=h).json()
        r2 = cl.post(f"/v2/worlds/{wid}/hypotheses",       # transport retry
                     json={"statement": "H"}, headers=h).json()
        assert r1["hyp_id"] == r2["hyp_id"]                # one logical act
        n = cl.get(f"/v2/worlds/{wid}/status", headers=hdr).json()[
            "epistemics"]["hypotheses_proposed"]
        assert n == 1                                      # exactly one object


def test_G15_probe6_same_key_different_payload_conflicts(db_path):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        tok = cl.post("/v2/clients", json={"name": "x"}).json()["token"]
        hdr = {"authorization": f"Bearer {tok}"}
        sid = cl.post("/v2/sessions", json={"name": "s"},
                      headers=hdr).json()["session_id"]
        wid = cl.post("/v2/worlds", json={"session_id": sid, "name": "w"},
                      headers=hdr).json()["world_id"]
        cl.post(f"/v2/worlds/{wid}/start", headers=hdr)
        h = dict(hdr, **{"Idempotency-Key": "k9"})
        cl.post(f"/v2/worlds/{wid}/hypotheses", json={"statement": "H1"},
                headers=h)
        r = cl.post(f"/v2/worlds/{wid}/hypotheses", json={"statement": "H2"},
                    headers=h)                             # same key, diff body
        assert r.status_code == 409


def test_G15_probe7_same_key_across_worlds_conflicts(db_path):
    app = create_app(db_path)
    with TestClient(app, raise_server_exceptions=False) as cl:
        tok = cl.post("/v2/clients", json={"name": "x"}).json()["token"]
        hdr = {"authorization": f"Bearer {tok}"}
        sid = cl.post("/v2/sessions", json={"name": "s"},
                      headers=hdr).json()["session_id"]
        w1 = cl.post("/v2/worlds", json={"session_id": sid, "name": "w1"},
                     headers=hdr).json()["world_id"]
        w2 = cl.post("/v2/worlds", json={"session_id": sid, "name": "w2"},
                     headers=hdr).json()["world_id"]
        cl.post(f"/v2/worlds/{w1}/start", headers=hdr)
        cl.post(f"/v2/worlds/{w2}/start", headers=hdr)
        h = dict(hdr, **{"Idempotency-Key": "shared"})
        cl.post(f"/v2/worlds/{w1}/hypotheses", json={"statement": "H"},
                headers=h)
        # same key in a DIFFERENT world is a materially different request -> 409
        r = cl.post(f"/v2/worlds/{w2}/hypotheses", json={"statement": "H"},
                    headers=h)
        assert r.status_code == 409


def test_G15_probe10_idempotency_durable_across_restart(db_path):
    """The key + object commit atomically, so a retry after a process restart
    replays the SAME result and creates no duplicate."""
    f1 = Foundry(db_path)
    c = f1.create_client("c"); s = f1.create_session(c, "s")
    w = f1.create_world(s, "w")["world_id"]; f1.start_world(w, c)
    rh = content_hash({"route": "hypotheses", "world_id": w,
                       "body": {"statement": "H"}})
    hid1 = f1.propose_hypothesis(w, "H", client_id=c, idem_key="kk",
                                 request_hash=rh)
    f1.close()
    f2 = Foundry(db_path)                                 # process restart
    try:
        hid2 = f2.propose_hypothesis(w, "H", client_id=c, idem_key="kk",
                                     request_hash=rh)     # retry
        assert hid2 == hid1                               # replay, same id
        n = f2.store.read().execute(
            "SELECT COUNT(*) n FROM hypotheses WHERE world_id=?", (w,)
        ).fetchone()["n"]
        assert n == 1                                     # no duplicate
    finally:
        f2.close()


# =========================== G16 KNOWLEDGE FRONTIER =======================

def test_G16_probe12_13_frontier_reconstruct_and_monotone(foundry):
    c, s, w = _rw(foundry)
    a1 = foundry.create_artifact(w, "k", b"one", client_id=c)["artifact_id"]
    ks1 = foundry.knowledge_set(w, client_id=c)
    seq_a1 = [x for x in ks1["available"] if x["artifact_id"] == a1][0][
        "first_available_seq"]
    a2 = foundry.create_artifact(w, "k", b"two", client_id=c)["artifact_id"]
    # at seq_a1, only a1 is available; a2 is future information
    ks_before = foundry.knowledge_set(w, seq=seq_a1, client_id=c)
    ids_before = {x["artifact_id"] for x in ks_before["available"]}
    assert a1 in ids_before and a2 not in ids_before
    # now, both are available
    ks_now = foundry.knowledge_set(w, client_id=c)
    ids_now = {x["artifact_id"] for x in ks_now["available"]}
    assert a1 in ids_now and a2 in ids_now


def _hstate(f, w, h):
    return f.store.read().execute(
        "SELECT state FROM hypotheses WHERE hyp_id=?", (h,)).fetchone()["state"]


def _claims(f, w, c):
    return [e["event_type"] for e in f.world_events(w, client_id=c, limit=2000)
            if e["event_type"] in ("CLAIM_SURVIVED", "CLAIM_FALSIFIED")]


def test_F3fix_unbound_observation_cannot_readjudicate(foundry):
    """Regression (adversarial CRITICAL): a second, UNBOUND observation on a
    committed experiment must not launder FALSIFIED -> SURVIVED."""
    c, s, w = _rw(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p = foundry.register_prediction(w, h, {"x": 1}, client_id=c)
    e = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e, {"r": 0}, "FALSIFIED", client_id=c,
                               pred_id=p)                 # H FALSIFIED
    assert _hstate(foundry, w, h) == "FALSIFIED"
    # a second observation on the SAME experiment (unbound) is a repeat
    with pytest.raises(ConflictError):
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    # even as an explicit replication it never re-adjudicates
    foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                               replication=True)
    assert _hstate(foundry, w, h) == "FALSIFIED"
    assert _claims(foundry, w, c) == ["CLAIM_FALSIFIED"]   # no second CLAIM_*


def test_F3fix_cross_prediction_falsification_is_monotone(foundry):
    """Regression (adversarial CRITICAL): different predictions on the same
    hypothesis cannot flip a FALSIFIED hypothesis back to SURVIVED. A later
    experiment CAN falsify a survived hypothesis (survived->falsified only)."""
    c, s, w = _rw(foundry)
    h = foundry.propose_hypothesis(w, "H", client_id=c)
    p1 = foundry.register_prediction(w, h, {"a": 1}, client_id=c)
    p2 = foundry.register_prediction(w, h, {"b": 1}, client_id=c)
    p3 = foundry.register_prediction(w, h, {"c": 1}, client_id=c)
    e1 = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e1, {}, "SURVIVED", client_id=c, pred_id=p1)
    assert _hstate(foundry, w, h) == "SURVIVED"
    e2 = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e2, {}, "FALSIFIED", client_id=c, pred_id=p2)
    assert _hstate(foundry, w, h) == "FALSIFIED"           # legit falsification
    e3 = _committed_exp(foundry, w, c, h)
    foundry.record_observation(w, e3, {}, "SURVIVED", client_id=c, pred_id=p3)
    assert _hstate(foundry, w, h) == "FALSIFIED"           # cannot un-falsify
    # exactly two real transitions occurred: SURVIVED then FALSIFIED
    assert _claims(foundry, w, c) == ["CLAIM_SURVIVED", "CLAIM_FALSIFIED"]


def test_F3fix_repeat_observation_of_experiment_needs_replication(foundry):
    c, s, w = _rw(foundry)
    e = _committed_exp(foundry, w, c)         # no hyp
    foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    with pytest.raises(ConflictError):        # second obs of same exp
        foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c)
    foundry.record_observation(w, e, {"r": 1}, "SURVIVED", client_id=c,
                               replication=True)          # explicit retest ok


def test_F5fix_create_experiment_idempotent(db_path):
    """Regression (adversarial LOW): a retry of create_experiment(commit=True)
    with the same idem key must not duplicate the experiment or double-debit."""
    f = Foundry(db_path)
    c, s, w = _rw(f, budget={"experiments": {"limit": 5,
                                             "enforcement": "enforceable"}})
    rh = content_hash({"route": "experiments", "world_id": w,
                       "body": {"spec": {"i": 1}}})
    o1 = f.create_experiment(w, {"i": 1}, client_id=c, idem_key="ek",
                             request_hash=rh)
    o2 = f.create_experiment(w, {"i": 1}, client_id=c, idem_key="ek",
                             request_hash=rh)              # retry
    assert o1["exp_id"] == o2["exp_id"]
    assert f.budget_status(w)["consumed"]["experiments"] == 1  # one debit
    assert f.store.read().execute(
        "SELECT COUNT(*) n FROM experiments WHERE world_id=?", (w,)
    ).fetchone()["n"] == 1
    f.close()


def test_F10fix_multilevel_fork_inherits_grandparent(foundry):
    """Regression (adversarial MEDIUM): a grandchild's KnowledgeSet must include
    a grandparent artifact inherited transitively through the parent."""
    c, s, w = _rw(foundry)
    x = foundry.create_artifact(w, "k", b"grandparent-X", client_id=c)
    xhash = x["blob_hash"]
    ck = foundry.checkpoint(w, client_id=c)["checkpoint_id"]
    b = foundry.fork(w, ck, [{"name": "B"}], client_id=c)[0]["world_id"]
    foundry.start_world(b, c)
    ckb = foundry.checkpoint(b, client_id=c)["checkpoint_id"]
    cc = foundry.fork(b, ckb, [{"name": "C"}], client_id=c)[0]["world_id"]
    ks_b = foundry.knowledge_set(b, client_id=c)
    ks_c = foundry.knowledge_set(cc, client_id=c)
    assert any(i["content_hash"] == xhash for i in ks_b["available"])   # child
    assert any(i["content_hash"] == xhash for i in ks_c["available"])   # grandchild
    got = [i for i in ks_c["available"] if i["content_hash"] == xhash][0]
    assert got["basis"] == "fork_inheritance"


def test_G16_import_adds_to_frontier_at_import_seq(foundry):
    ca = foundry.create_client("A"); sa = foundry.create_session(ca, "sa")
    gid = foundry.create_topology_group(ca)
    wa = foundry.create_world(sa, "A", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wa, ca)
    art = foundry.create_artifact(wa, "k", b"payload", client_id=ca,
                                  meta={"info_kind": "success"})["artifact_id"]
    cb = foundry.create_client("B"); sb = foundry.create_session(cb, "sb")
    wb = foundry.create_world(sb, "B", sharing_policy="FULLY_SHARED",
                              topology_group=gid)["world_id"]
    foundry.start_world(wb, cb)
    ks0 = foundry.knowledge_set(wb, client_id=cb)
    assert ks0["available_count"] == 0                    # nothing yet
    imp = foundry.import_artifact(wb, wa, art, client_id=cb)
    ks1 = foundry.knowledge_set(wb, client_id=cb)
    got = [x for x in ks1["available"]
           if x["artifact_id"] == imp["artifact_id"]]
    assert got and got[0]["basis"] == "legal_import"
    assert got[0]["source_world"] == wa
