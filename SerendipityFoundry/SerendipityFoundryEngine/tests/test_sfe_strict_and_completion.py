"""Fixes from Harmonia's M1 expanded test pass, 2026-09-05.

Three findings, all of the same family: the engine answered 200 to something it
should have refused, and the caller learned too late or not at all.

  T3 6.2  under strict, an unkeyed POST /v2/worlds CREATED A WORLD the caller
          could never touch again -- every later call answered 428. An orphan
          at birth, in a system with no GC.
  T3 6.3  "strict" silently meant "strict on {wid}-scoped routes": an unkeyed
          worker could still claim and complete work.
  T2 C3e  a completion replayed with a DIFFERENT result returned 200 and the
          ORIGINAL result. Nothing was overwritten; the DIAGNOSIS was wrong.
"""
import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.api import create_app          # noqa: E402

HDR = "X-SFE-Session"


def _engine(enforcement):
    db = os.path.join(tempfile.mkdtemp(), "e.db")
    c = TestClient(create_app(db, session_enforcement=enforcement))
    tok = c.post("/v2/clients", json={"name": "t"}).json()["token"]
    return c, {"Authorization": "Bearer " + tok}


def _session(c, h):
    r = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    hs = dict(h)
    hs[HDR] = r["session_key"]
    return r, hs


# ---- T3 6.2: refuse at creation, do not orphan ------------------------------
def test_strict_unkeyed_world_creation_is_refused_not_orphaned():
    """The whole point: fail at the point of the mistake, before state exists.

    Creating a world the caller can never touch again is strictly worse than
    refusing it -- the caller gets a 200, discovers the problem one call later,
    and leaves an unreachable world behind for ever."""
    c, h = _engine("strict")
    s, _hs = _session(c, h)

    r = c.post("/v2/worlds", json={"session_id": s["session_id"], "name": "w"},
               headers=h)                                    # NO session key
    assert r.status_code == 428, r.text
    assert r.json()["detail"]["error"] == "SESSION_REQUIRED"

    # and nothing was created
    before = c.get("/v2/worlds", headers=_session(c, h)[1]).json()
    n = len(before if isinstance(before, list) else before.get("worlds", []))
    c.post("/v2/worlds", json={"session_id": s["session_id"], "name": "w2"},
           headers=h)
    after = c.get("/v2/worlds", headers=_session(c, h)[1]).json()
    m = len(after if isinstance(after, list) else after.get("worlds", []))
    assert m == n, "a refused creation still created a world"


def test_advisory_still_allows_unkeyed_creation():
    """The migration path is untouched: advisory is why 106 legacy sessions and
    every pre-v5 client keep working."""
    c, h = _engine("advisory")
    s, _ = _session(c, h)
    r = c.post("/v2/worlds", json={"session_id": s["session_id"], "name": "w"},
               headers=h)
    assert r.status_code == 200


# ---- T3 6.3: strict means strict, including the work routes -----------------
@pytest.mark.parametrize("method,path,body", [
    ("POST", "/v2/worlds", {"session_id": "ses_x", "name": "w"}),
    ("GET", "/v2/worlds", None),
    ("POST", "/v2/work/claim", {"worker_id": "w1"}),
    ("POST", "/v2/work/wrk_000000000000000000000000/heartbeat",
     {"worker_id": "w1", "claim_id": "clm_0"}),
    ("POST", "/v2/work/wrk_000000000000000000000000/complete",
     {"worker_id": "w1", "claim_id": "clm_0", "result": {}}),
    ("POST", "/v2/work/wrk_000000000000000000000000/fail",
     {"worker_id": "w1", "claim_id": "clm_0", "error": "e"}),
])
def test_strict_gates_the_routes_that_carry_no_world_id(method, path, body):
    """These six answered 200 unkeyed under strict. An unkeyed worker could
    claim and complete work while the mode was called 'strict'."""
    c, h = _engine("strict")
    _session(c, h)
    r = (c.get(path, headers=h) if method == "GET"
         else c.post(path, json=body, headers=h))
    assert r.status_code == 428, "%s %s -> %s" % (method, path, r.status_code)
    assert r.json()["detail"]["error"] == "SESSION_REQUIRED"


def test_strict_keyed_path_is_unaffected():
    c, h = _engine("strict")
    s, hs = _session(c, h)
    w = c.post("/v2/worlds", json={"session_id": s["session_id"], "name": "w"},
               headers=hs)
    assert w.status_code == 200
    wid = w.json()["world_id"]
    assert c.post("/v2/worlds/%s/start" % wid, json={},
                  headers=hs).status_code == 200
    assert c.get("/v2/worlds/%s/status" % wid, headers=hs).status_code == 200
    assert c.post("/v2/work/claim", json={"worker_id": "w1", "world_id": wid},
                  headers=hs).status_code == 200


# ---- T2 C3e: a differing replay must not report success ---------------------
def _completed_work(c, hs, sid):
    wid = c.post("/v2/worlds", json={"session_id": sid, "name": "w"},
                 headers=hs).json()["world_id"]
    c.post("/v2/worlds/%s/start" % wid, json={}, headers=hs)
    hyp = c.post("/v2/worlds/%s/hypotheses" % wid, json={"statement": "h"},
                 headers=hs).json()["hyp_id"]
    c.post("/v2/worlds/%s/predictions" % wid,
           json={"hyp_id": hyp, "content": {"a": 1}}, headers=hs)
    c.post("/v2/worlds/%s/experiments" % wid,
           json={"spec": {"x": 1}, "commit": True, "enqueue": True},
           headers=hs)
    work = c.post("/v2/work/claim", json={"worker_id": "w1", "world_id": wid},
                  headers=hs).json()["work"]
    return wid, work


def test_identical_completion_replay_is_idempotent():
    c, h = _engine("advisory")
    s, hs = _session(c, h)
    _wid, work = _completed_work(c, hs, s["session_id"])
    body = {"worker_id": "w1", "claim_id": work["claim_id"],
            "result": {"ok": True}}
    a = c.post("/v2/work/%s/complete" % work["work_id"], json=body, headers=hs)
    b = c.post("/v2/work/%s/complete" % work["work_id"], json=body, headers=hs)
    assert a.status_code == 200 and b.status_code == 200
    assert a.json()["result_hash"] == b.json()["result_hash"]


def test_completion_replay_with_a_different_result_is_a_conflict():
    """It never overwrote -- but it returned 200 and the ORIGINAL result, so a
    caller that did not compare result_hash could believe its second result had
    been recorded. Silent success for a materially different request."""
    c, h = _engine("advisory")
    s, hs = _session(c, h)
    _wid, work = _completed_work(c, hs, s["session_id"])
    base = {"worker_id": "w1", "claim_id": work["claim_id"]}
    first = c.post("/v2/work/%s/complete" % work["work_id"],
                   json=dict(base, result={"ok": True}), headers=hs)
    assert first.status_code == 200
    stored = first.json()["result_hash"]

    second = c.post("/v2/work/%s/complete" % work["work_id"],
                    json=dict(base, result={"ok": False, "different": 1}),
                    headers=hs)
    assert second.status_code == 409, second.text
    d = second.json()["detail"]
    assert d["error"] == "conflict"
    assert d["stored_result_hash"] == stored
    assert d["submitted_result_hash"] != stored

    # the authoritative result is untouched
    again = c.post("/v2/work/%s/complete" % work["work_id"],
                   json=dict(base, result={"ok": True}), headers=hs)
    assert again.status_code == 200
    assert again.json()["result_hash"] == stored


# ---- session close: makes SESSION_CLOSED reachable, and the drain movable ----
def test_close_makes_session_closed_reachable():
    """HARMONIA T4 recorded this as INDETERMINATE: SESSION_CLOSED (409) was in
    the taxonomy but no route could produce it, so a documented failure could
    not be triggered or tested by any client."""
    c, h = _engine("advisory")
    s, hs = _session(c, h)
    wid = c.post("/v2/worlds", json={"session_id": s["session_id"], "name": "w"},
                 headers=hs).json()["world_id"]
    assert c.get("/v2/worlds/%s/status" % wid, headers=hs).status_code == 200

    r = c.post("/v2/sessions/%s/close" % s["session_id"], headers=h)
    assert r.status_code == 200 and r.json()["state"] == "CLOSED"
    assert r.json()["already_closed"] is False

    r = c.get("/v2/worlds/%s/status" % wid, headers=hs)   # key of a closed one
    assert r.status_code == 409
    assert r.json()["detail"]["error"] == "SESSION_CLOSED"


def test_close_is_idempotent_and_owner_only():
    c, h = _engine("advisory")
    s, _hs = _session(c, h)
    assert c.post("/v2/sessions/%s/close" % s["session_id"],
                  headers=h).json()["already_closed"] is False
    assert c.post("/v2/sessions/%s/close" % s["session_id"],
                  headers=h).json()["already_closed"] is True

    tok2 = c.post("/v2/clients", json={"name": "other"}).json()["token"]
    s2, _ = _session(c, h)
    r = c.post("/v2/sessions/%s/close" % s2["session_id"],
               headers={"Authorization": "Bearer " + tok2})
    assert r.status_code == 403


def test_close_works_on_a_keyless_legacy_session():
    """The drain depends on this. Close is gated on OWNERSHIP, not on the
    session key, because the 106 LEGACY sessions never had a key -- a key-gated
    close would leave exactly the sessions that need draining undrainable."""
    from sfe.runtime import Foundry
    c, h = _engine("advisory")
    s, _hs = _session(c, h)
    db = c.app.state.db_path
    f = Foundry(db)
    with f.store.write() as w:                     # demote to a pre-v5 row
        w.execute("UPDATE sessions SET affinity_mode='LEGACY', key_hash=NULL,"
                  " engine_instance_id=NULL WHERE session_id=?",
                  (s["session_id"],))
    before = f.affinity_census()["sessions_legacy_open"]
    f.close()

    assert c.post("/v2/sessions/%s/close" % s["session_id"],
                  headers=h).status_code == 200

    f = Foundry(db)
    after = f.affinity_census()["sessions_legacy_open"]
    f.close()
    assert after == before - 1, "closing a legacy session must move the drain"
