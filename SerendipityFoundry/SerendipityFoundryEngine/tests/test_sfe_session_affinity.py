"""Session affinity (v5): an experiment must not wander between engines.

THE DEFECT: M1 and M2 run byte-identical builds over separate databases. A
client could register on one and send otherwise-valid requests to the other.
Best case a confusing 404; worst case a write into the wrong engine.

The suite is deliberately failure-first. The happy path is two tests; the rest
are the ways it must fail, because the defect was a QUIET success.

Two engines are simulated by two databases in one process -- which is exactly
what M1 and M2 are: same code, different substrate. That also covers
requirement M (no process-global affinity state): both apps live in this
interpreter at once and must not leak into each other.
"""
import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.api import create_app          # noqa: E402
from sfe.ids import engine_id_from_key, session_key_for  # noqa: E402
from sfe.runtime import Foundry         # noqa: E402

HDR = "X-SFE-Session"


def _engine(enforcement="advisory"):
    db = os.path.join(tempfile.mkdtemp(), "e.db")
    c = TestClient(create_app(db, session_enforcement=enforcement))
    tok = c.post("/v2/clients", json={"name": "t"}).json()["token"]
    return c, {"Authorization": "Bearer " + tok}, db


def _session(c, h):
    r = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    hs = dict(h)
    hs[HDR] = r["session_key"]
    return r, hs


def _world(c, hs, sid, **kw):
    body = {"session_id": sid, "name": "w"}
    body.update(kw)
    r = c.post("/v2/worlds", json=body, headers=hs)
    assert r.status_code == 200, r.text
    wid = r.json()["world_id"]
    c.post("/v2/worlds/%s/start" % wid, json={}, headers=hs)
    return wid


@pytest.fixture()
def m1():
    return _engine()


@pytest.fixture()
def m2():
    return _engine()


# ---- A/B: the happy path, on each engine ------------------------------------
def test_A_session_on_engine1_works_on_engine1(m1):
    c, h, _ = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    assert c.get("/v2/worlds/%s/status" % wid, headers=hs).status_code == 200


def test_B_session_on_engine2_works_on_engine2(m2):
    c, h, _ = m2
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    assert c.get("/v2/worlds/%s/status" % wid, headers=hs).status_code == 200


# ---- C/D: the headline defect, both directions ------------------------------
def _assert_wrong_session(r):
    assert r.status_code == 421, r.text
    d = r.json()["detail"]
    assert d["error"] == "WRONG_SESSION"
    assert d["claimed_engine_instance_id"] != d["this_engine_instance_id"]
    return d


def test_C_engine1_session_presented_to_engine2(m1, m2):
    c1, h1, _ = m1
    c2, h2, _ = m2
    s1, _ = _session(c1, h1)
    s2, hs2 = _session(c2, h2)
    wid2 = _world(c2, hs2, s2["session_id"])          # a REAL world on engine 2

    foreign = dict(h2)
    foreign[HDR] = s1["session_key"]                  # engine 1's key
    _assert_wrong_session(c2.get("/v2/worlds/%s/status" % wid2, headers=foreign))


def test_D_engine2_session_presented_to_engine1(m1, m2):
    c1, h1, _ = m1
    c2, h2, _ = m2
    s1, hs1 = _session(c1, h1)
    s2, _ = _session(c2, h2)
    wid1 = _world(c1, hs1, s1["session_id"])

    foreign = dict(h1)
    foreign[HDR] = s2["session_key"]
    _assert_wrong_session(c1.get("/v2/worlds/%s/status" % wid1, headers=foreign))


def test_C2_wrong_engine_beats_missing_resource(m1, m2):
    """ORDERING. A foreign key + a world id that does not exist here must still
    be WRONG_SESSION, never 404 -- that confusion is the whole bug."""
    c1, h1, _ = m1
    c2, h2, _ = m2
    s1, _ = _session(c1, h1)
    foreign = dict(h2)
    foreign[HDR] = s1["session_key"]
    r = c2.get("/v2/worlds/wld_000000000000000000000000/status", headers=foreign)
    assert r.status_code == 421
    assert r.json()["detail"]["error"] == "WRONG_SESSION"


# ---- E: a real 404 stays a 404 ----------------------------------------------
def test_E_valid_session_missing_world_is_not_wrong_session(m1):
    c, h, _ = m1
    _s, hs = _session(c, h)
    r = c.get("/v2/worlds/wld_000000000000000000000000/status", headers=hs)
    assert r.status_code == 404
    assert r.json()["detail"]["error"] == "not_found"


# ---- F/G: missing and malformed ---------------------------------------------
def test_F_missing_session_on_strict_world():
    """Under STRICT enforcement a bound world refuses an unkeyed request."""
    c, h, _ = _engine("strict")
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    r = c.get("/v2/worlds/%s/status" % wid, headers=h)        # no session header
    assert r.status_code == 428
    assert r.json()["detail"]["error"] == "SESSION_REQUIRED"


def test_F2_advisory_allows_missing_key_but_wrong_engine_still_fatal():
    """The phased part is ONLY the requirement to send a key. Under advisory a
    missing key is allowed -- but a key from another engine is still fatal, so
    the defect is closed from the hour this ships, not at the cutover."""
    c1, h1, _ = _engine("advisory")
    c2, h2, _ = _engine("advisory")
    s1, hs1 = _session(c1, h1)
    wid = _world(c1, hs1, s1["session_id"])
    assert c1.get("/v2/worlds/%s/status" % wid, headers=h1).status_code == 200
    foreign = dict(h1)
    foreign[HDR] = _session(c2, h2)[0]["session_key"]
    r = c1.get("/v2/worlds/%s/status" % wid, headers=foreign)
    assert r.status_code == 421
    assert r.json()["detail"]["error"] == "WRONG_SESSION"


@pytest.mark.parametrize("bad", ["x", "hello world", "sfes_", "sfes_zz_abc",
                                 "sfes_" + "g" * 24 + "_abcdefghijklmnop",
                                 "gen2_looks_like_a_token",
                                 "sfes_" + "a" * 24 + "_short"])
def test_G_malformed_session(bad):
    """Anything that is not a session key is rejected as malformed, in BOTH
    modes -- a garbage value is never silently treated as 'no key'."""
    for mode in ("advisory", "strict"):
        c, h, _ = _engine(mode)
        s, hs = _session(c, h)
        wid = _world(c, hs, s["session_id"])
        hh = dict(h)
        hh[HDR] = bad
        r = c.get("/v2/worlds/%s/status" % wid, headers=hh)
        assert r.status_code == 422, (mode, bad, r.status_code, r.text)
        assert r.json()["detail"]["error"] == "SESSION_MALFORMED", (mode, bad)


def test_G3_empty_header_is_absent_not_malformed():
    """An empty header value is indistinguishable from no header at the HTTP
    layer, so it is treated as ABSENT -- allowed under advisory, 428 under
    strict. Documented because it is the one case where 'present but empty'
    does NOT mean malformed."""
    c, h, _ = _engine("advisory")
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    hh = dict(h); hh[HDR] = ""
    assert c.get("/v2/worlds/%s/status" % wid, headers=hh).status_code == 200

    c2, h2, _ = _engine("strict")
    s2, hs2 = _session(c2, h2)
    wid2 = _world(c2, hs2, s2["session_id"])
    hh2 = dict(h2); hh2[HDR] = ""
    r = c2.get("/v2/worlds/%s/status" % wid2, headers=hh2)
    assert r.status_code == 428
    assert r.json()["detail"]["error"] == "SESSION_REQUIRED"


def test_G2_wellformed_but_unknown_here(m1):
    """Names THIS engine, correct shape, never issued: a restore from a
    different backup, or a forgery. Must NOT be 404 and must NOT be
    WRONG_SESSION."""
    c, h, db = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    f = Foundry(db)
    forged = session_key_for(f.engine_instance_id())
    f.close()
    hh = dict(h)
    hh[HDR] = forged
    r = c.get("/v2/worlds/%s/status" % wid, headers=hh)
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "SESSION_UNKNOWN"


# ---- H: right engine, wrong experiment --------------------------------------
def test_H_session_from_another_experiment_same_engine(m1):
    c, h, _ = m1
    sA, hsA = _session(c, h)
    sB, _hsB = _session(c, h)
    widA = _world(c, hsA, sA["session_id"])
    cross = dict(h)
    cross[HDR] = sB["session_key"]           # valid here, but not this world's
    r = c.get("/v2/worlds/%s/status" % widA, headers=cross)
    assert r.status_code == 403
    assert r.json()["detail"]["error"] == "SESSION_MISMATCH"


# ---- I: unrelated semantics unchanged ---------------------------------------
def test_I_terminated_semantics_unchanged_under_valid_session(m1):
    c, h, _ = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    c.post("/v2/worlds/%s/terminate" % wid, json={}, headers=hs)
    import base64
    r = c.post("/v2/worlds/%s/artifacts" % wid,
               json={"kind": "artifact",
                     "data_b64": base64.b64encode(b"x").decode()}, headers=hs)
    assert r.status_code == 409          # the v4 terminal-write gate, untouched
    assert c.get("/v2/worlds/%s/status" % wid, headers=hs).status_code == 200


# ---- J: restart preserves binding -------------------------------------------
def test_J_binding_survives_restart(m1):
    """A restart is a new process over the SAME substrate. The session, its
    key and its engine binding must all survive -- otherwise every restart
    would strand every in-flight experiment."""
    c, h, db = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    c2 = TestClient(create_app(db))                   # "restart"
    r = c2.get("/v2/worlds/%s/status" % wid, headers=hs)
    assert r.status_code == 200, r.text


# ---- K: backup/restore ------------------------------------------------------
def test_K_restore_keeps_identity_and_keys(m1):
    """Restoring the substrate elsewhere KEEPS the engine identity, so keys
    issued before the backup still work. That is the documented invariant:
    identity follows the data, not the host."""
    import shutil
    c, h, db = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    restored = os.path.join(tempfile.mkdtemp(), "restored.db")
    shutil.copy(db, restored)
    c3 = TestClient(create_app(restored))
    assert c3.get("/v2/worlds/%s/status" % wid, headers=hs).status_code == 200
    # ...and the restored copy reports the SAME instance id (the clone hazard,
    # made explicit rather than hidden: a copied substrate is the same engine).
    f1, f3 = Foundry(db), Foundry(restored)
    assert f1.engine_instance_id() == f3.engine_instance_id()
    f1.close(); f3.close()


# ---- L: provenance ----------------------------------------------------------
def test_L_historical_rows_do_not_acquire_session_identity(m1):
    """A pre-affinity session must not be back-dated into a bound one. LEGACY
    means 'we do not know', and that is recorded as NULL, not invented."""
    c, h, db = m1
    s, hs = _session(c, h)
    _world(c, hs, s["session_id"])
    f = Foundry(db)
    cx = f.store.write().__enter__() if False else f.store.read()
    # simulate a row that predates the feature
    with f.store.write() as w:
        w.execute("INSERT INTO sessions(session_id,client_id,name,created_ts,"
                  "key_hash,engine_instance_id,affinity_mode) "
                  "SELECT 'ses_legacyrow', client_id, 'old', created_ts, "
                  "NULL, NULL, 'LEGACY' FROM sessions LIMIT 1")
    row = f.store.read().execute(
        "SELECT key_hash, engine_instance_id, affinity_mode FROM sessions "
        "WHERE session_id='ses_legacyrow'").fetchone()
    assert row["affinity_mode"] == "LEGACY"
    assert row["key_hash"] is None and row["engine_instance_id"] is None
    census = f.affinity_census()
    assert census["sessions_legacy"] >= 1
    f.close()


def test_L2_legacy_world_still_reachable_without_a_key(m1):
    """The migration promise: 106 sessions and 346 worlds keep working."""
    c, h, db = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    f = Foundry(db)
    with f.store.write() as w:                        # demote to pre-v5 state
        w.execute("UPDATE sessions SET affinity_mode='LEGACY', key_hash=NULL,"
                  " engine_instance_id=NULL WHERE session_id=?",
                  (s["session_id"],))
    f.close()
    assert c.get("/v2/worlds/%s/status" % wid, headers=h).status_code == 200


# ---- M: no shared affinity through process state ----------------------------
def test_M_two_engines_in_one_process_do_not_share_affinity(m1, m2):
    c1, h1, db1 = m1
    c2, h2, db2 = m2
    f1, f2 = Foundry(db1), Foundry(db2)
    assert f1.engine_instance_id() != f2.engine_instance_id()
    f1.close(); f2.close()
    s1, hs1 = _session(c1, h1)
    s2, hs2 = _session(c2, h2)
    assert engine_id_from_key(s1["session_key"]) != \
        engine_id_from_key(s2["session_key"])
    w1 = _world(c1, hs1, s1["session_id"])
    w2 = _world(c2, hs2, s2["session_id"])
    assert c1.get("/v2/worlds/%s/status" % w1, headers=hs1).status_code == 200
    assert c2.get("/v2/worlds/%s/status" % w2, headers=hs2).status_code == 200


# ---- N: existing negative probes still behave -------------------------------
def test_N_existing_negatives_survive_session_validation(m1):
    c, h, _ = m1
    s, hs = _session(c, h)
    wid = _world(c, hs, s["session_id"])
    # 422 unknown field
    import base64
    r = c.post("/v2/worlds/%s/artifacts" % wid,
               json={"kind": "a", "data_b64": base64.b64encode(b"x").decode(),
                     "nope": 1}, headers=hs)
    assert r.status_code == 422
    # 401 unauthenticated (no bearer at all)
    assert c.get("/v2/worlds/%s/status" % wid).status_code == 401
    # 403 foreign client, even holding a valid session key of its own
    tok2 = c.post("/v2/clients", json={"name": "other"}).json()["token"]
    h2 = {"Authorization": "Bearer " + tok2}
    s2, hs2 = _session(c, h2)
    r = c.get("/v2/worlds/%s/status" % wid, headers=hs2)
    assert r.status_code in (403,), r.text


# ---- THE PRIMARY ACCEPTANCE TEST --------------------------------------------
def test_PRIMARY_base_url_flipped_mid_experiment(m1, m2):
    """Reproduce the original bad configuration exactly.

    Point a client at engine 1, create a session, do real work, then flip to
    engine 2 mid-experiment. The VERY NEXT experiment-scoped request must fail
    WRONG_SESSION -- before any state is read or mutated.
    """
    c1, h1, _ = m1
    c2, h2, _ = m2
    s1, hs1 = _session(c1, h1)
    wid = _world(c1, hs1, s1["session_id"])
    assert c1.get("/v2/worlds/%s/status" % wid, headers=hs1).status_code == 200

    flipped = dict(h2)                       # engine 2's bearer...
    flipped[HDR] = s1["session_key"]         # ...engine 1's session

    import base64
    probes = [
        ("GET  status", lambda: c2.get("/v2/worlds/%s/status" % wid, headers=flipped)),
        ("GET  events", lambda: c2.get("/v2/worlds/%s/events" % wid, headers=flipped)),
        ("POST artifact", lambda: c2.post(
            "/v2/worlds/%s/artifacts" % wid,
            json={"kind": "artifact", "data_b64": base64.b64encode(b"x").decode()},
            headers=flipped)),
        ("POST hypothesis", lambda: c2.post(
            "/v2/worlds/%s/hypotheses" % wid, json={"statement": "h"},
            headers=flipped)),
        ("POST terminate", lambda: c2.post(
            "/v2/worlds/%s/terminate" % wid, json={}, headers=flipped)),
    ]
    for label, call in probes:
        r = call()
        assert r.status_code == 421, "%s -> %s %s" % (label, r.status_code, r.text)
        assert r.json()["detail"]["error"] == "WRONG_SESSION", label

    # and engine 2 wrote NOTHING: it has no such world at all
    f2 = Foundry(_engine_db(c2))
    assert f2.store.read().execute(
        "SELECT COUNT(*) c FROM worlds WHERE world_id=?", (wid,)).fetchone()["c"] == 0
    f2.close()


def _engine_db(client) -> str:
    return client.app.state.db_path


# ---- route coverage (R-G: enumerate everything, exempt explicitly) ---------
#
# HARMONIA, 2026-09-05, finding 3: the previous version of this test scoped its
# probe with the SAME PREDICATE that created the gap it was meant to catch --
#     if not (path.startswith("/v2/worlds/{wid}") or path.startswith("/v2/work/"))
# so POST/GET /v2/worlds were outside the population the completeness claim was
# measured over, and "coverage complete" was true only of a FILTERED route
# table. Widening the prefix closed that instance and left the general defect:
# any hand-drawn boundary can be drawn wrong, and had been, twice.
#
# The probe is now INVERTED. Every route on the live app must be either covered
# or on the named exemption list below. Adding a route forces a decision
# instead of defaulting to unprotected.

# Routes that must NOT require a session key, each with the reason. Changing
# this list is a deliberate act that shows up in review.
EXEMPT = {
    ("GET", "/v2/version"):        "liveness/identity; no auth, no resource",
    ("GET", "/v2/openapi.json"):   "the contract itself; must be readable to "
                                   "discover how to send a session at all",
    ("GET", "/v2/docs"):           "human documentation UI",
    ("POST", "/v2/clients"):       "bootstrap: mints the bearer token you need "
                                   "before a session can exist",
    ("POST", "/v2/sessions"):      "bootstrap: this is where a key is MINTED, "
                                   "so it cannot require one",
    ("POST", "/v2/audit/verify-anchor"):
        "deliberately credential-free and CROSS-ENGINE by design (R-SFE-1): "
        "PEW verifies an anchor it did not produce and holds no session. "
        "Requiring affinity here would break third-party attestation.",
    ("POST", "/v2/sessions/{sid}/close"):
        "gated on OWNERSHIP, not on the session key: the 106 LEGACY sessions "
        "never had a key, so a key-gated close would leave exactly the "
        "sessions that need draining permanently undrainable",
    ("POST", "/v2/topology-groups"):
        "client-level capability, not experiment-scoped: it mints a sharing "
        "group id bound to the CLIENT, touches no world and names no session. "
        "Exempted deliberately after the R-G census surfaced it -- previously "
        "it was unprotected by accident rather than by decision.",
}


def _live_routes(client):
    out = set()
    for r in client.app.routes:
        path = getattr(r, "path", "")
        if not path.startswith("/v2"):
            continue
        for m in (getattr(r, "methods", None) or set()):
            if m in ("GET", "POST"):
                out.add((m, path))
    return out


def test_exemption_list_has_no_stale_entries(m1):
    """An exemption for a route that no longer exists is a rule nobody is
    enforcing. It must be deleted, not left to rot."""
    live = _live_routes(m1[0])
    stale = sorted(set(EXEMPT) - live)
    assert not stale, "exemptions for routes that do not exist: %r" % stale


def test_route_coverage_is_complete(m1, m2):
    """EVERY live route is covered or explicitly exempt -- no prefix filter.

    A foreign session key must be refused by every non-exempt route BEFORE the
    resource is touched. 421 is required; 422 is tolerated only where body
    validation fires first, and 404/200 never are.
    """
    c1, h1, _ = m1
    c2, h2, _ = m2
    s1, hs1 = _session(c1, h1)
    wid = _world(c1, hs1, s1["session_id"])
    foreign = dict(h2)
    foreign[HDR] = s1["session_key"]

    live = _live_routes(c2)
    assert live, "no routes found -- the probe is broken"

    unprotected = []
    for method, path in sorted(live):
        if (method, path) in EXEMPT:
            continue
        url = (path.replace("{wid}", wid)
                   .replace("{aid}", "sha256:" + "0" * 64)
                   .replace("{eid}", "exp_000000000000000000000000")
                   .replace("{work_id}", "wrk_000000000000000000000000"))
        body = {"session_id": s1["session_id"], "name": "w"}             if path == "/v2/worlds" else {}
        r = (c2.get(url, headers=foreign) if method == "GET"
             else c2.post(url, json=body, headers=foreign))
        if r.status_code not in (421, 422):
            unprotected.append((method, path, r.status_code))

    assert not unprotected, (
        "routes that did not fail closed on a foreign session key "
        "(neither covered nor exempt): %r" % unprotected)
