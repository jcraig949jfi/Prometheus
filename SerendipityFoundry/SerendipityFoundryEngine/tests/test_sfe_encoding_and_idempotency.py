"""DFX-5: the artifact endpoint must FAIL CLOSED on bad encoding, and an
idempotency conflict must say what differed.

Both defects were found by reading a real client's traffic, not by a test:
URL-safe base64 was accepted with a 200 and silently stored different, shorter
bytes (24 in, 15 stored), and malformed base64 escaped as an opaque 500. Every
other field on this endpoint fails closed; these did not.
"""
import base64
import hashlib
import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.api import create_app  # noqa: E402

RAW = bytes([250, 251, 252, 253, 254, 255]) * 4      # needs + / in standard b64


@pytest.fixture()
def client():
    return TestClient(create_app(os.path.join(tempfile.mkdtemp(), "t.db")))


@pytest.fixture()
def world(client):
    tok = client.post("/v2/clients", json={"name": "t"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    sid = client.post("/v2/sessions", json={"name": "s"},
                      headers=h).json()["session_id"]
    wid = client.post("/v2/worlds", json={"session_id": sid, "name": "w"},
                      headers=h).json()["world_id"]
    client.post("/v2/worlds/%s/start" % wid, json={}, headers=h)
    return client, h, sid, wid


def test_standard_base64_round_trips_byte_exactly(world):
    c, h, _sid, wid = world
    r = c.post("/v2/worlds/%s/artifacts" % wid,
               json={"kind": "artifact",
                     "data_b64": base64.b64encode(RAW).decode()}, headers=h)
    assert r.status_code == 200
    assert r.json()["blob_hash"] == "sha256:" + hashlib.sha256(RAW).hexdigest()


def test_urlsafe_base64_is_rejected_not_silently_corrupted(world):
    """The regression that matters: this used to return 200 and store 15 bytes
    for a 24-byte payload, because b64decode(validate=False) DISCARDS '-' and
    '_' rather than rejecting them."""
    c, h, _sid, wid = world
    r = c.post("/v2/worlds/%s/artifacts" % wid,
               json={"kind": "artifact",
                     "data_b64": base64.urlsafe_b64encode(RAW).decode()},
               headers=h)
    assert r.status_code == 422
    d = r.json()["detail"]
    assert d["loc"] == ["body", "data_b64"]
    assert "standard base64" in d["message"]


def test_malformed_base64_is_422_not_500(world):
    c, h, _sid, wid = world
    r = c.post("/v2/worlds/%s/artifacts" % wid,
               json={"kind": "artifact", "data_b64": "!!!not-base64!!!"},
               headers=h)
    assert r.status_code == 422
    assert r.json()["detail"]["error"] == "validation_error"


def test_empty_payload_remains_legal(world):
    c, h, _sid, wid = world
    r = c.post("/v2/worlds/%s/artifacts" % wid,
               json={"kind": "artifact", "data_b64": ""}, headers=h)
    assert r.status_code == 200


def test_identical_replay_under_one_key_is_idempotent(world):
    c, h, _sid, wid = world
    k = dict(h, **{"Idempotency-Key": "step-1"})
    a = c.post("/v2/worlds/%s/hypotheses" % wid, json={"statement": "x"},
               headers=k)
    b = c.post("/v2/worlds/%s/hypotheses" % wid, json={"statement": "x"},
               headers=k)
    assert a.status_code == b.status_code == 200
    assert a.json() == b.json()


def test_key_reused_across_worlds_conflicts_and_says_so(world):
    """Unchanged behaviour, better message. A key unique per logical step but
    NOT per world conflicts on every world after the first, which reads as a
    random scatter of 409s until the error names the first-use world."""
    c, h, sid, wid = world
    k = dict(h, **{"Idempotency-Key": "step-1"})
    c.post("/v2/worlds/%s/hypotheses" % wid, json={"statement": "x"}, headers=k)

    wid2 = c.post("/v2/worlds", json={"session_id": sid, "name": "w2"},
                  headers=h).json()["world_id"]
    c.post("/v2/worlds/%s/start" % wid2, json={}, headers=h)
    r = c.post("/v2/worlds/%s/hypotheses" % wid2, json={"statement": "x"},
               headers=k)

    assert r.status_code == 409
    d = r.json()["detail"]
    assert d["first_used_world_id"] == wid
    assert d["first_used_route"] == "hypotheses"
    assert "unique per (world, step)" in d["message"]
