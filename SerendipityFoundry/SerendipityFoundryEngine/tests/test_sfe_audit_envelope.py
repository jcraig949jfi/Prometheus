"""Third-party auditability battery (Daedalus, R2-1 / R-SFE-1 / R-SFE-2).

Harmonia R2-1: the complete sealed experiment exists in SFE, but its read
routes are client-scoped, so a third-party investigator holding a PEW fossil
gets 403 without the producing client's credential.

Mnemosyne R-SFE-1: PEW must be able to verify an (engine, event_id,
entry_hash) anchor without that credential, or "wrong real event -> rejected"
cannot be enforced. R-SFE-2: engine identity must be IN the anchor, because
build identity alone was byte-identical on M1 and M2.

The direction taken, deliberately:

    producer/arena -> SFE sealed envelope -> PEW immutable audit envelope

and NOT: arbitrary investigator bypasses SFE authorization. So the envelope is
OWNER-SCOPED like every other read -- ordinary client isolation is untouched --
and only anchor VERIFICATION (booleans, no content, no enumeration) is
available to a non-owner.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from sfe.api import create_app
from sfe.errors import AccessDenied
from sfe.ids import content_hash


def _client_session(f, name="orch"):
    c = f.create_client(name)
    return c, f.create_session(c, "s")


@pytest.fixture
def http(tmp_path):
    app = create_app(str(tmp_path / "audit_api.db"))
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _auth(c, name):
    tok = c.post("/v2/clients", json={"name": name}).json()["token"]
    h = {"authorization": "Bearer " + tok}
    s = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    return h, s["session_id"]


def _sealed_run(f, cname="producer"):
    c, s = _client_session(f, cname)
    w = f.create_world(s, "w", seed_root=424242,
                       budget={"ticks": {"limit": 9,
                                         "enforcement": "enforceable"}})["world_id"]
    f.start_world(w, c)
    h = f.propose_hypothesis(w, "H", client_id=c)
    spec = {"action": "encounter", "ticks": 32}
    e = f.create_experiment(w, spec, client_id=c, hyp_id=h, commit=True)
    o = f.record_observation(w, e["exp_id"], {"score": 0.5}, "SURVIVED",
                             client_id=c)
    return c, w, e["exp_id"], o, spec


# ===================== R2-1: THE ENVELOPE ==================================

def test_R2_1_envelope_carries_every_preserved_identity(foundry):
    """SELF-CONTAINED: an auditor reading this out of PEW, holding no SFE
    credential, must find every identity the directive says to preserve."""
    c, w, eid, o, spec = _sealed_run(foundry)
    env = foundry.audit_envelope(w, eid, client_id=c)
    # engine identity -- build AND instance (R-SFE-2)
    assert env["engine"]["engine_instance_id"].startswith("eng_")
    assert env["engine"]["engine_source_hash"]
    # world / config identity
    assert env["world"]["world_id"] == w
    assert env["world"]["seed_root"] == 424242
    assert env["world"]["sharing_policy"] == "ISOLATED"
    assert env["world"]["budget"]["ticks"]["limit"] == 9
    # exact sealed spec + hash, AND the hash the ledger committed to
    assert env["experiment"]["spec"] == spec
    assert env["sealed_spec_hash_in_ledger"] == env["experiment"]["spec_hash"]
    assert env["spec_hash_recomputed"] == env["experiment"]["spec_hash"]
    # action / input / output identity
    assert env["observations"][0]["content"] == {"score": 0.5}
    assert env["observations"][0]["outcome"] == "SURVIVED"
    assert env["observations"][0]["evidence_class"] in ("CLIENT_ASSERTED",
                                                        "ENGINE_WORK_RESULT")
    # exact causal anchor
    anchor = [a for a in env["anchors"]
              if a["event_type"] == "OBSERVATION_RECORDED"][0]
    assert anchor["event_id"] == o["event_id"]
    assert anchor["entry_hash"] == o["entry_hash"]
    assert env["ledger_head_hash"]
    assert env["envelope_hash"]


def test_R2_1_envelope_hash_seals_the_document(foundry):
    c, w, eid, o, spec = _sealed_run(foundry)
    env = foundry.audit_envelope(w, eid, client_id=c)
    again = foundry.audit_envelope(w, eid, client_id=c)
    assert env["envelope_hash"] == again["envelope_hash"], "stable"
    body = {k: v for k, v in env.items() if k != "envelope_hash"}
    assert content_hash(body) == env["envelope_hash"], "re-derivable"
    tampered = dict(body)
    tampered["experiment"] = dict(body["experiment"],
                                  spec={"action": "SOMETHING ELSE"})
    assert content_hash(tampered) != env["envelope_hash"]


def test_R2_1_envelope_is_owner_scoped_ISOLATION_UNCHANGED(foundry):
    """The point of the chosen direction: this does NOT weaken ordinary
    isolation. A non-owner still cannot pull material out of the engine; they
    read the envelope from PEW, where the producer published it."""
    c, w, eid, o, spec = _sealed_run(foundry)
    c2, _ = _client_session(foundry, "intruder")
    with pytest.raises(AccessDenied):
        foundry.audit_envelope(w, eid, client_id=c2)


# ===================== R-SFE-1: ANCHOR VERIFICATION ========================

def test_R_SFE_1_verify_works_without_the_producers_credential(foundry):
    c, w, eid, o, spec = _sealed_run(foundry)
    _client_session(foundry, "auditor")          # a different client exists
    v = foundry.verify_anchor(w, o["event_id"], o["entry_hash"],
                              exp_id=eid, obs_id=o["obs_id"])
    assert v["valid"] is True
    assert v["checks"]["event_exists"] and v["checks"]["entry_hash_matches"]
    assert v["checks"]["binds_exp_id"] and v["checks"]["binds_obs_id"]
    assert v["event_type"] == "OBSERVATION_RECORDED"
    assert v["engine"]["engine_instance_id"].startswith("eng_")


def test_R_SFE_1_wrong_but_real_event_is_REJECTED(foundry):
    """The property that makes this worth having. Harmonia D1: anchoring on
    WORLD_CREATED satisfies a pure EXISTENCE check. Binding must reject it."""
    c, w, eid, o, spec = _sealed_run(foundry)
    created = [e for e in foundry.world_events(w, client_id=c, limit=1000)
               if e["event_type"] == "WORLD_CREATED"][0]
    v = foundry.verify_anchor(w, created["event_id"], created["entry_hash"],
                              exp_id=eid, obs_id=o["obs_id"])
    assert v["checks"]["event_exists"] is True, "the pair is entirely genuine"
    assert v["checks"]["entry_hash_matches"] is True
    assert v["checks"]["binds_exp_id"] is False
    assert v["valid"] is False, "a real-but-WRONG event must not verify"


def test_R_SFE_1_tampered_entry_hash_is_rejected(foundry):
    c, w, eid, o, spec = _sealed_run(foundry)
    v = foundry.verify_anchor(w, o["event_id"], "sha256:" + "0" * 64,
                              exp_id=eid)
    assert v["valid"] is False
    assert v["checks"]["entry_hash_matches"] is False


def test_R_SFE_1_verify_discloses_nothing(foundry):
    """It must never become a content oracle or an enumeration surface."""
    c, w, eid, o, spec = _sealed_run(foundry)
    v = foundry.verify_anchor(w, o["event_id"], o["entry_hash"], exp_id=eid)
    blob = json.dumps(v)
    assert "score" not in blob, "no observation content"
    assert "encounter" not in blob, "no spec content"
    assert "refs" not in v, "no refs block"
    assert set(v) <= {"valid", "checks", "engine", "event_type", "event_seq",
                      "world_index"}
    miss = foundry.verify_anchor(w, "evt_nope", o["entry_hash"])
    assert miss["valid"] is False and miss["checks"]["event_exists"] is False


# ===================== R-SFE-2: ENGINE INSTANCE IDENTITY ===================

def test_R_SFE_2_instance_id_is_stable_across_a_reopen(foundry, db_path):
    """Build identity was byte-identical on M1 and M2 for most of 2026-09-04,
    so an anchor consumer could not tell which engine minted it."""
    from sfe.runtime import Foundry
    first = foundry.engine_instance_id()
    assert first == foundry.engine_instance_id()
    foundry.close()
    f2 = Foundry(db_path)
    try:
        assert f2.engine_instance_id() == first, "must follow the SUBSTRATE"
    finally:
        f2.close()


def test_R_SFE_2_two_engines_differ(foundry, tmp_path):
    from sfe.runtime import Foundry
    other = Foundry(str(tmp_path / "other.db"))
    try:
        assert other.engine_instance_id() != foundry.engine_instance_id()
    finally:
        other.close()


# ===================== HTTP SURFACE =======================================

def test_http_R2_1_envelope_denied_but_verify_allowed_for_a_third_party(http):
    h, sid = _auth(http, "producer")
    wid = http.post("/v2/worlds", json={"session_id": sid, "name": "w",
                                        "seed_root": 7, "budget": {}},
                    headers=h).json()["world_id"]
    http.post("/v2/worlds/%s/start" % wid, headers=h)
    hyp = http.post("/v2/worlds/%s/hypotheses" % wid, json={"statement": "H"},
                    headers=h).json()["hyp_id"]
    eid = http.post("/v2/worlds/%s/experiments" % wid,
                    json={"spec": {"a": 1}, "hyp_id": hyp},
                    headers=h).json()["exp_id"]
    o = http.post("/v2/worlds/%s/observations" % wid,
                  json={"exp_id": eid, "content": {"r": 1},
                        "outcome": "SURVIVED"}, headers=h).json()

    env = http.get("/v2/worlds/%s/experiments/%s/audit-envelope" % (wid, eid),
                   headers=h)
    assert env.status_code == 200, env.text
    assert env.json()["envelope_hash"]

    h2, _ = _auth(http, "auditor")
    denied = http.get("/v2/worlds/%s/experiments/%s/audit-envelope"
                      % (wid, eid), headers=h2)
    assert denied.status_code == 403, denied.text

    v = http.post("/v2/audit/verify-anchor",
                  json={"world_id": wid, "event_id": o["event_id"],
                        "entry_hash": o["entry_hash"], "exp_id": eid},
                  headers=h2)
    assert v.status_code == 200, v.text
    assert v.json()["valid"] is True

    # the auth wall still stands
    anon = http.post("/v2/audit/verify-anchor",
                     json={"world_id": wid, "event_id": o["event_id"],
                           "entry_hash": o["entry_hash"]})
    assert anon.status_code == 401, anon.text
