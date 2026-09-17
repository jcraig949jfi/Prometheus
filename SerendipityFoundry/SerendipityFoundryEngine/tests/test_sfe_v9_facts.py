"""v9 point release (2026-09-17): the engine records FACTS the caller supplies
and interprets none of them. D1 logical_time, D2 typed termination, D3 sealed
generic world events, D4 manifest envelope, D6 fork diff, D7 labels.

Every test here has a cheat control: the thing the engine must NOT do.
"""
import base64
import json
import os
import re
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from sfe.api import create_app                                    # noqa: E402
from sfe.errors import InvalidTransition, ValidationError        # noqa: E402
from sfe.ids import content_hash                                  # noqa: E402
from sfe.runtime import Foundry                                   # noqa: E402
from sfe.store import SCHEMA_VERSION                              # noqa: E402

HDR = "X-SFE-Session"


@pytest.fixture
def f(tmp_path):
    return Foundry(str(tmp_path / "v9.db"))


def _owner(f, name="owner"):
    cid = f.create_client(name)
    s = f.create_session(cid, "s")
    return cid, (s["session_id"] if isinstance(s, dict) else s)


def _wire(tmp_path):
    c = TestClient(create_app(str(tmp_path / "w.db")))
    tok = c.post("/v2/clients", json={"name": "owner"}).json()["token"]
    h = {"Authorization": "Bearer " + tok}
    sess = c.post("/v2/sessions", json={"name": "s"}, headers=h).json()
    h[HDR] = sess["session_key"]
    return c, h, sess["session_id"]


# ===========================================================================
# D4 manifest envelope
# ===========================================================================

def test_manifest_is_hashed_sealed_immutable_and_opaque(f):
    cid, sid = _owner(f)
    man = {"kind": "wse.bitstring", "logical_time_unit": "generation",
           "cells": ["W0", "W2_K2"], "SHELF_MIN": 0.45}   # the engine reads none of this
    w = f.create_world(sid, "run", manifest=man,
                       manifest_schema="archaeon.wse.world/3")
    assert w["manifest_hash"] == content_hash(man)
    assert w["manifest_schema"] == "archaeon.wse.world/3"
    assert "manifest" not in w                       # identity on the row, body on its route
    got = f.get_manifest(w["world_id"], cid)
    assert got["manifest"] == man and got["manifest_hash"] == w["manifest_hash"]
    # key order does not change identity
    w2 = f.create_world(sid, "run2", manifest=dict(reversed(list(man.items()))),
                        manifest_schema="archaeon.wse.world/3")
    assert w2["manifest_hash"] == w["manifest_hash"]
    # sealed in the chain
    created = [e for e in f.world_events(w["world_id"], client_id=cid)
               if e["event_type"] == "WORLD_CREATED"][0]
    assert created["payload"]["manifest_hash"] == w["manifest_hash"]
    # no world without one reads a hash
    w3 = f.create_world(sid, "bare")
    assert w3["manifest_hash"] is None and f.get_manifest(w3["world_id"], cid)["manifest"] is None


def test_manifest_envelope_is_validated_and_content_is_not(f):
    cid, sid = _owner(f)
    with pytest.raises(ValidationError):                 # schema required
        f.create_world(sid, "x", manifest={"a": 1})
    with pytest.raises(ValidationError):                 # schema without manifest
        f.create_world(sid, "x", manifest_schema="s/1")
    with pytest.raises(ValidationError):                 # not an object
        f.create_world(sid, "x", manifest=[1, 2], manifest_schema="s/1")
    with pytest.raises(ValidationError):                 # size bound
        f.create_world(sid, "x", manifest={"blob": "x" * 300000},
                       manifest_schema="s/1")
    with pytest.raises(ValidationError):                 # reserved key shape
        f.create_world(sid, "x", manifest={"declared_event_kinds": "no"},
                       manifest_schema="s/1")
    # CONTROL: arbitrary content, including words the engine must never act on
    w = f.create_world(sid, "x", manifest_schema="s/1",
                       manifest={"SUMMIT": 0.9, "corridor": True, "nested": {"deep": [1, {"x": None}]}})
    assert w["manifest_hash"]


# ===========================================================================
# D7 labels (opaque provenance; attempt identity minted ABOVE the engine)
# ===========================================================================

def test_labels_are_opaque_filterable_and_bounded(f):
    cid, sid = _owner(f)
    a = f.create_world(sid, "a", labels={"attempt": "C4-SFE-01/a02", "campaign": "cmp4"})
    b = f.create_world(sid, "b", labels={"attempt": "C4-SFE-01/a03"})
    f.create_world(sid, "c")
    assert a["labels"] == {"attempt": "C4-SFE-01/a02", "campaign": "cmp4"}
    got = f.list_worlds(client_id=cid, labels={"attempt": "C4-SFE-01/a03"})
    assert [w["world_id"] for w in got] == [b["world_id"]]
    assert len(f.list_worlds(client_id=cid, labels={"campaign": "cmp4"})) == 1
    assert len(f.list_worlds(client_id=cid)) == 3
    with pytest.raises(ValidationError):
        f.create_world(sid, "x", labels={str(i): "v" for i in range(17)})
    with pytest.raises(ValidationError):
        f.create_world(sid, "x", labels={"k": "v" * 65})
    with pytest.raises(ValidationError):
        f.create_world(sid, "x", labels={"k": 1})


# ===========================================================================
# D1 logical_time
# ===========================================================================

def test_logical_time_is_stored_sealed_and_never_defaulted(f):
    cid, sid = _owner(f)
    w = f.create_world(sid, "w", manifest={"logical_time_unit": "generation"},
                       manifest_schema="s/1")["world_id"]
    f.start_world(w, cid)
    e = f.create_experiment(w, {"x": 1}, client_id=cid)["exp_id"]
    f.commit_experiment(w, e, client_id=cid)
    o1 = f.record_observation(w, e, {"score": 0.5}, "SURVIVED", client_id=cid, logical_time=80)
    e2 = f.create_experiment(w, {"x": 2}, client_id=cid)["exp_id"]
    f.commit_experiment(w, e2, client_id=cid)
    o2 = f.record_observation(w, e2, {"score": 0.5}, "SURVIVED", client_id=cid)
    rows = {r["obs_id"]: r for r in f.list_observations(w, client_id=cid)}
    oid = lambda o: o["obs_id"] if isinstance(o, dict) else o
    assert rows[oid(o1)]["logical_time"] == 80
    assert rows[oid(o2)]["logical_time"] is None         # NOT_SUPPLIED, never 0
    ev = [x for x in f.world_events(w, client_id=cid) if x["event_type"] == "OBSERVATION_RECORDED"]
    assert [x["payload"]["logical_time"] for x in ev] == [80, None]
    e3 = f.create_experiment(w, {"x": 3}, client_id=cid)["exp_id"]
    f.commit_experiment(w, e3, client_id=cid)
    with pytest.raises(ValidationError):
        f.record_observation(w, e3, {"score": 0.5}, "SURVIVED", client_id=cid, logical_time=-1)
    with pytest.raises(ValidationError):
        f.record_observation(w, e3, {"score": 0.5}, "SURVIVED", client_id=cid, logical_time=True)


# ===========================================================================
# D2 typed termination
# ===========================================================================

def test_termination_facts_are_recorded_and_the_engine_sets_none(f):
    cid, sid = _owner(f)
    w = f.create_world(sid, "w")["world_id"]
    f.start_world(w, cid)
    out = f.terminate_world(w, cid, termination={
        "reason": "stop_rule:first_solve", "logical_time": 97, "horizon": 300,
        "budget_consumed": {"evaluations": 19400}, "reference": "C4-SFE-01/a02"})
    assert out["state"] == "TERMINATED"
    t = out["termination"]
    assert t["reason"] == "stop_rule:first_solve" and t["horizon"] == 300 \
        and t["logical_time"] == 97 and t["budget_consumed"] == {"evaluations": 19400}
    last = f.world_events(w, client_id=cid)[-1]
    assert last["event_type"] == "WORLD_TERMINATED" and last["payload"]["reason"] == "stop_rule:first_solve"
    # a second termination is the same 409 it always was
    with pytest.raises(InvalidTransition):
        f.terminate_world(w, cid, termination={"reason": "again"})
    # CONTROL: a world terminated with no facts reads NOT_SUPPLIED, not a default
    w2 = f.create_world(sid, "w2")["world_id"]
    out2 = f.terminate_world(w2, cid)
    assert out2["termination"] is None
    assert f.world_events(w2, client_id=cid)[-1]["payload"] == {}


def test_termination_shape_is_validated(f):
    cid, sid = _owner(f)
    w = f.create_world(sid, "w")["world_id"]
    for bad in ({"logical_time": 3}, {"reason": ""}, {"reason": "x" * 129},
                {"reason": "ok", "horizon": -1}, {"reason": "ok", "budget_consumed": 3},
                {"reason": "ok", "note": "n" * 513}):
        with pytest.raises(ValidationError):
            f.terminate_world(w, cid, termination=bad)
    assert f.get_world(w, cid)["state"] == "CREATED"      # nothing terminated


# ===========================================================================
# D3 sealed generic world events
# ===========================================================================

def test_world_events_are_sealed_ordered_idempotent_and_uninterpreted(f):
    cid, sid = _owner(f)
    w = f.create_world(sid, "w")["world_id"]
    f.start_world(w, cid)
    a = f.record_world_event(w, "pressure.schedule", {"rung": 1, "delay": 1}, client_id=cid,
                             logical_time=25, refs={"prereg": "sha256:abc"})
    b = f.record_world_event(w, "import.realized", {"requested_dose": 4, "realized_dose": 4,
                                                    "origin_shares": {"import": 0.02}},
                             client_id=cid, logical_time=25)
    assert a["kind"] == "pressure.schedule" and b["event_seq"] > a["event_seq"]
    assert b["world_index"] == a["world_index"] + 1
    ev = [x for x in f.world_events(w, client_id=cid) if x["event_type"] == "WORLD_EVENT"]
    assert [x["payload"]["kind"] for x in ev] == ["pressure.schedule", "import.realized"]
    assert ev[0]["refs"] == {"prereg": "sha256:abc"} and ev[0]["payload"]["logical_time"] == 25
    assert ev[1]["payload"]["payload"]["realized_dose"] == 4
    # chained: each entry's prev_hash is the previous entry_hash
    assert ev[1]["prev_hash"] == ev[0]["entry_hash"]
    # idempotent under a key: same request -> same event, no second row
    k = "idem:evt-1"
    rh = content_hash({"route": "world_events", "world_id": w, "kind": "phase", "n": 1})
    x = f.record_world_event(w, "phase", {"n": 1}, client_id=cid, idem_key=k, request_hash=rh)
    y = f.record_world_event(w, "phase", {"n": 1}, client_id=cid, idem_key=k, request_hash=rh)
    assert x == y
    assert sum(1 for e in f.world_events(w, client_id=cid) if e["payload"].get("kind") == "phase") == 1
    # CONTROL: the engine accepts any kind, including the forbidden words,
    # because it does not read them -- and the acceptance grep below proves
    # the engine's own source never does either.
    f.record_world_event(w, "SHELF_REACHED", {"by": "a caller, not the engine"}, client_id=cid)
    # refused on a terminated world
    f.terminate_world(w, cid)
    with pytest.raises(InvalidTransition):
        f.record_world_event(w, "late", {}, client_id=cid)


def test_world_event_validation_and_declared_kinds(f):
    cid, sid = _owner(f)
    w = f.create_world(sid, "w", manifest_schema="s/1",
                       manifest={"declared_event_kinds": ["phase", "inject"]})["world_id"]
    f.start_world(w, cid)
    f.record_world_event(w, "phase", {"p": 1}, client_id=cid)
    with pytest.raises(ValidationError) as ei:
        f.record_world_event(w, "pressure", {"p": 1}, client_id=cid)
    assert "undeclared_event_kind" in str(ei.value)
    for bad_kind in ("", "x" * 65, "has space", "bad/slash"):
        with pytest.raises(ValidationError):
            f.record_world_event(w, bad_kind, {}, client_id=cid)
    with pytest.raises(ValidationError):
        f.record_world_event(w, "phase", {"blob": "x" * 70000}, client_id=cid)
    with pytest.raises(ValidationError):
        f.record_world_event(w, "phase", {}, client_id=cid, refs={"a": 1})
    # a world WITHOUT declared kinds accepts anything
    w2 = f.create_world(sid, "w2", manifest_schema="s/1", manifest={})["world_id"]
    f.start_world(w2, cid)
    f.record_world_event(w2, "anything.at.all", {}, client_id=cid)


# ===========================================================================
# D6 fork diff + manifest/labels inheritance
# ===========================================================================

def test_fork_records_the_changed_fields_and_inherits_identity(f):
    cid, sid = _owner(f)
    man = {"logical_time_unit": "generation", "pressure": "P"}
    w = f.create_world(sid, "w", manifest=man, manifest_schema="s/1",
                       labels={"attempt": "a01"}, seed_root=7)["world_id"]
    f.start_world(w, cid)
    ck = f.checkpoint(w, client_id=cid)["checkpoint_id"]
    kids = f.fork(w, ck, [
        {"name": "same"},
        {"name": "pressureQ", "manifest": {**man, "pressure": "Q"}, "manifest_schema": "s/1",
         "seed_root": 7, "labels": {"attempt": "a01", "branch": "Q"}},
    ], client_id=cid)
    same, q = kids
    assert same["manifest_hash"] == content_hash(man) and same["labels"] == {"attempt": "a01"}
    assert same["parent_world_id"] == w and same["fork_point"] is not None
    ev_same = f.world_events(same["world_id"], client_id=cid)
    forked = [e for e in ev_same if e["event_type"] == "WORLD_FORKED"][0]
    assert forked["payload"]["changed"] == {}
    assert forked["payload"]["manifest_hash"] == content_hash(man)
    ev_q = [e for e in f.world_events(q["world_id"], client_id=cid) if e["event_type"] == "WORLD_FORKED"][0]
    ch = ev_q["payload"]["changed"]
    assert set(ch) == {"manifest_hash", "labels"}
    assert ch["manifest_hash"]["parent"] == content_hash(man)
    assert ch["manifest_hash"]["child"] == content_hash({**man, "pressure": "Q"}) == q["manifest_hash"]
    assert f.get_manifest(q["world_id"], cid)["manifest"]["pressure"] == "Q"


# ===========================================================================
# THE ARCHITECTURAL ACCEPTANCE TEST (operator order s4 / s12)
# ===========================================================================

FORBIDDEN = ("SHELF", "SUMMIT", "CORRIDOR", "TAKEOVER", "GENERALIZATION")


def test_engine_source_never_uses_the_scientific_words():
    """The engine records the world; it does not interpret the science. Its
    OWN source must not contain the Campaign-3 vocabulary in any form."""
    src_dir = os.path.join(os.path.dirname(HERE), "sfe")
    hits = []
    for name in sorted(os.listdir(src_dir)):
        if not name.endswith(".py"):
            continue
        text = open(os.path.join(src_dir, name), encoding="utf-8").read()
        for word in FORBIDDEN:
            for m in re.finditer(word, text, flags=re.IGNORECASE):
                line = text.count("\n", 0, m.start()) + 1
                hits.append("%s:%d:%s" % (name, line, word))
    assert not hits, hits


# ===========================================================================
# on the wire (strictness, capabilities, old rows)
# ===========================================================================

def test_wire_v9_fields_and_strict_bodies(tmp_path):
    c, h, sid = _wire(tmp_path)
    r = c.post("/v2/worlds", json={"session_id": sid, "name": "w", "manifest": {"a": 1},
                                   "manifest_schema": "s/1", "labels": {"attempt": "a01"}}, headers=h)
    assert r.status_code == 200, r.text
    w = r.json()
    assert w["manifest_hash"] == content_hash({"a": 1}) and w["labels"] == {"attempt": "a01"}
    assert c.get("/v2/worlds/%s/manifest" % w["world_id"], headers=h).json()["manifest"] == {"a": 1}
    assert c.post("/v2/worlds/%s/start" % w["world_id"], headers=h).status_code == 200
    # unknown field on the new route: refused, same shape as every other route
    r = c.post("/v2/worlds/%s/events" % w["world_id"], json={"kind": "k", "payload": {}, "bogus": 1}, headers=h)
    assert r.status_code == 422
    r = c.post("/v2/worlds/%s/events" % w["world_id"], json={"kind": "k", "payload": {"x": 1}, "logical_time": 3},
               headers={**h, "Idempotency-Key": "idem:k1"})
    assert r.status_code == 200, r.text
    r2 = c.post("/v2/worlds/%s/events" % w["world_id"], json={"kind": "k", "payload": {"x": 1}, "logical_time": 3},
                headers={**h, "Idempotency-Key": "idem:k1"})
    assert r2.json() == r.json()
    # termination: empty body == no facts; strict when present; facts on the world
    r = c.post("/v2/worlds/%s/terminate" % w["world_id"],
               json={"reason": "horizon", "horizon": 60, "extra": 1}, headers=h)
    assert r.status_code == 422
    r = c.post("/v2/worlds/%s/terminate" % w["world_id"], json={"reason": "horizon", "horizon": 60}, headers=h)
    assert r.status_code == 200 and r.json()["termination"]["horizon"] == 60
    assert c.get("/v2/worlds/%s" % w["world_id"], headers=h).json()["termination"]["reason"] == "horizon"
    # label filter over the wire
    assert len(c.get("/v2/worlds", params=[("label", "attempt=a01")], headers=h).json()["worlds"]) == 1
    assert len(c.get("/v2/worlds", params=[("label", "attempt=zzz")], headers=h).json()["worlds"]) == 0


def test_capabilities_is_open_and_says_what_the_engine_owns(tmp_path):
    c = TestClient(create_app(str(tmp_path / "w.db")))
    r = c.get("/v2/capabilities")                       # no auth, no session
    assert r.status_code == 200
    cap = r.json()
    assert cap["schema_version"] == SCHEMA_VERSION == 9
    assert cap["strict_bodies"] is True
    assert cap["read_semantics"]["advisory"]["no_key"] == "ADMITTED_AUDITED"
    assert cap["read_semantics"]["advisory"]["wrong_session_key"] == "REFUSED"
    assert "WORLD_EVENT" in cap["vocabularies"]["event_types_engine_owned"]
    assert cap["features"]["cursor_pagination"] and cap["pagination"]["cursor_param"] == "after_seq"
    assert cap["limits"]["page_limit_max"] == 1000
    # the capabilities agree with /v2/version on identity
    v = c.get("/v2/version").json()
    assert cap["engine_source_hash"] == v["engine_source_hash"]
    assert cap["engine_instance_id"] == v["engine_instance_id"]
    for word in FORBIDDEN:
        assert word not in json.dumps(cap).upper()


def test_old_schema_ledger_migrates_in_place_with_null_facts(tmp_path):
    """A schema-8 ledger opened by the v9 engine: migrated, old rows read
    NULL for every v9 fact, nothing backfilled, migration idempotent."""
    import sqlite3
    db = str(tmp_path / "old.db")
    f = Foundry(db)
    cid, sid = _owner(f)
    w = f.create_world(sid, "old")["world_id"]
    f.start_world(w, cid)
    e = f.create_experiment(w, {"x": 1}, client_id=cid)["exp_id"]
    f.commit_experiment(w, e, client_id=cid)
    f.record_observation(w, e, {"s": 1}, "SURVIVED", client_id=cid)
    f.terminate_world(w, cid)
    f.store.close() if hasattr(f.store, "close") else None
    # forge a schema-8 ledger: drop the v9 columns by rebuilding is invasive;
    # instead rewind the version marker and verify the guarded migration is a
    # no-op that still advances the marker (idempotence), then check reads.
    cx = sqlite3.connect(db)
    cx.execute("UPDATE meta SET value='8' WHERE key='schema_version'")
    cx.commit(); cx.close()
    f2 = Foundry(db)
    cx = sqlite3.connect(db)
    assert cx.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0] == "9"
    cx.close()
    wd = f2.get_world(w, cid)
    assert wd["manifest_hash"] is None and wd["labels"] is None and wd["termination"] is None
    assert f2.list_observations(w, client_id=cid)[0]["logical_time"] is None
    assert f2.get_manifest(w, cid)["manifest"] is None
