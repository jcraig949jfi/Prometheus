"""Gen-2 REST API tests: the external capability surface, including the
isolation boundary over HTTP (knowing a world id + holding a DIFFERENT valid
token must not grant access) and machine-readable API docs."""

from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient

from sfe.api import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "api.db"))
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _register(c, name):
    r = c.post("/v2/clients", json={"name": name})
    assert r.status_code == 200, r.text
    return r.json()["token"], r.json()["client_id"]


def _h(tok):
    return {"authorization": f"Bearer {tok}"}


def test_full_flow_over_http(client):
    tok, cid = _register(client, "A")
    s = client.post("/v2/sessions", json={"name": "s"}, headers=_h(tok)).json()
    w = client.post("/v2/worlds", json={"session_id": s["session_id"],
                    "name": "w", "budget": {}}, headers=_h(tok)).json()
    wid = w["world_id"]
    assert client.post(f"/v2/worlds/{wid}/start", headers=_h(tok)).status_code == 200
    h = client.post(f"/v2/worlds/{wid}/hypotheses",
                    json={"statement": "H"}, headers=_h(tok)).json()["hyp_id"]
    p = client.post(f"/v2/worlds/{wid}/predictions",
                    json={"hyp_id": h, "content": {"e": 1}},
                    headers=_h(tok)).json()["pred_id"]
    e = client.post(f"/v2/worlds/{wid}/experiments",
                    json={"spec": {"r": 1}, "hyp_id": h, "pred_id": p},
                    headers=_h(tok)).json()["exp_id"]
    o = client.post(f"/v2/worlds/{wid}/observations",
                    json={"exp_id": e, "content": {"got": 1},
                          "outcome": "SURVIVED", "pred_id": p}, headers=_h(tok))
    assert o.status_code == 200, o.text
    st = client.get(f"/v2/worlds/{wid}/status", headers=_h(tok)).json()
    assert st["state"] == "RUNNING" and st["ledger_integrity_ok"] is True
    assert st["epistemics"]["predictions_registered"] == 1


def test_unauth_is_401(client):
    assert client.get("/v2/worlds").status_code == 401
    assert client.get("/v2/worlds",
                      headers=_h("gen2_bogus")).status_code == 401


def test_http_isolation_attack(client):
    ta, _ = _register(client, "A")
    tb, _ = _register(client, "B")
    s = client.post("/v2/sessions", json={"name": "s"}, headers=_h(ta)).json()
    wid = client.post("/v2/worlds", json={"session_id": s["session_id"],
                      "name": "w"}, headers=_h(ta)).json()["world_id"]
    # client B holds a valid token and knows wid -> still denied on every op
    assert client.get(f"/v2/worlds/{wid}", headers=_h(tb)).status_code == 403
    assert client.post(f"/v2/worlds/{wid}/start",
                       headers=_h(tb)).status_code == 403
    assert client.post(f"/v2/worlds/{wid}/hypotheses",
                       json={"statement": "x"}, headers=_h(tb)).status_code == 403
    # and B cannot create a world in A's session
    assert client.post("/v2/worlds", json={"session_id": s["session_id"],
                       "name": "w"}, headers=_h(tb)).status_code == 403


def test_work_lifecycle_over_http(client):
    tok, _ = _register(client, "A")
    s = client.post("/v2/sessions", json={"name": "s"}, headers=_h(tok)).json()
    wid = client.post("/v2/worlds", json={"session_id": s["session_id"],
                      "name": "w"}, headers=_h(tok)).json()["world_id"]
    client.post(f"/v2/worlds/{wid}/start", headers=_h(tok))
    e = client.post(f"/v2/worlds/{wid}/experiments",
                    json={"spec": {"bits": "0"}, "enqueue": True,
                          "kind": "evaluate_bitstring"}, headers=_h(tok)).json()
    claim = client.post("/v2/work/claim",
                        json={"worker_id": "wk", "world_id": wid},
                        headers=_h(tok)).json()["work"]
    assert claim is not None and claim["work_id"] == e["work_id"]
    assert claim["claim_id"]              # H1: server-issued fencing token
    hb = client.post(f"/v2/work/{claim['work_id']}/heartbeat",
                     json={"worker_id": "wk", "claim_id": claim["claim_id"]},
                     headers=_h(tok))
    assert hb.status_code == 200
    done = client.post(f"/v2/work/{claim['work_id']}/complete",
                       json={"worker_id": "wk", "claim_id": claim["claim_id"],
                             "result": {"score": 1.0}},
                       headers=_h(tok))
    assert done.status_code == 200 and done.json()["status"] == "COMPLETED"
    # a completion WITHOUT the fencing token is a validation failure
    bare = client.post(f"/v2/work/{claim['work_id']}/complete",
                       json={"worker_id": "wk", "result": {"score": 1.0}},
                       headers=_h(tok))
    assert bare.status_code == 422


def test_extra_field_rejected(client):
    tok, _ = _register(client, "A")
    r = client.post("/v2/sessions", json={"name": "s", "bogus": 1},
                    headers=_h(tok))
    assert r.status_code == 422       # scientific requests fail closed


def test_openapi_is_generated(client):
    r = client.get("/v2/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec["info"]["version"] == "2.2.0"
    assert "/v2/worlds/{wid}/fork" in spec["paths"]
    assert "/v2/work/claim" in spec["paths"]
    assert "/v2/worlds/{wid}/experiments/{eid}/commit" in spec["paths"]


def test_work_claim_is_client_scoped(client):
    """Experimenter isolation on the work queue: an UNSCOPED claim by client B
    must never be handed client A's queued work item -- B cannot even observe
    its payload, let alone hold a lease on A's queue (I5, cross-tenant claim)."""
    ta, _ = _register(client, "A")
    tb, _ = _register(client, "B")
    s = client.post("/v2/sessions", json={"name": "sa"}, headers=_h(ta)).json()
    wa = client.post("/v2/worlds", json={"session_id": s["session_id"],
                     "name": "wa"}, headers=_h(ta)).json()["world_id"]
    client.post(f"/v2/worlds/{wa}/start", headers=_h(ta))
    # A enqueues a work item on A's world
    client.post(f"/v2/worlds/{wa}/experiments",
                json={"spec": {"bits": "0"}, "enqueue": True,
                      "kind": "evaluate"}, headers=_h(ta))
    # B, unscoped, claims -> must get nothing (A's item is not in B's queue)
    rb = client.post("/v2/work/claim",
                     json={"worker_id": "wb"}, headers=_h(tb))
    assert rb.status_code == 200 and rb.json()["work"] is None
    # B, naming A's world explicitly -> 403 (ownership)
    assert client.post("/v2/work/claim",
                       json={"worker_id": "wb", "world_id": wa},
                       headers=_h(tb)).status_code == 403
    # A, unscoped, DOES get its own item
    ra = client.post("/v2/work/claim",
                     json={"worker_id": "wa"}, headers=_h(ta)).json()["work"]
    assert ra is not None and ra["world_id"] == wa


def test_import_artifact_is_cross_client_isolated(client):
    """Experimenter B cannot pull experimenter A's artifact by id: a cross-world
    import requires a bilateral topology share, and A's ISOLATED source never
    consents. B also learns nothing about which artifact ids exist in A's world
    (shared-substrate confidentiality + existence oracle, I5)."""
    import base64
    ta, _ = _register(client, "A")
    tb, _ = _register(client, "B")
    sa = client.post("/v2/sessions", json={"name": "sa"},
                     headers=_h(ta)).json()["session_id"]
    wa = client.post("/v2/worlds", json={"session_id": sa, "name": "wa"},
                     headers=_h(ta)).json()["world_id"]
    client.post(f"/v2/worlds/{wa}/start", headers=_h(ta))
    art = client.post(f"/v2/worlds/{wa}/artifacts",
                      json={"kind": "secret",
                            "data_b64": base64.b64encode(b"A-only").decode(),
                            "meta": {"info_kind": "artifact"}},
                      headers=_h(ta)).json()["artifact_id"]
    # B builds a FULLY_SHARED destination and tries to pull A's artifact by id
    sb = client.post("/v2/sessions", json={"name": "sb"},
                     headers=_h(tb)).json()["session_id"]
    wb = client.post("/v2/worlds", json={"session_id": sb, "name": "exfil",
                     "sharing_policy": "FULLY_SHARED"},
                     headers=_h(tb)).json()["world_id"]
    client.post(f"/v2/worlds/{wb}/start", headers=_h(tb))
    r = client.post(f"/v2/worlds/{wb}/import",
                    json={"source_world": wa, "source_artifact": art},
                    headers=_h(tb))
    assert r.status_code == 403, r.text
    # GUESSING a fake artifact id gives the SAME denial -> no existence oracle
    r2 = client.post(f"/v2/worlds/{wb}/import",
                     json={"source_world": wa, "source_artifact": "art_deadbeef"},
                     headers=_h(tb))
    assert r2.status_code == 403
    assert r2.json()["detail"]["error"] == "access_denied"
