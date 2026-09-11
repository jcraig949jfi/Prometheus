"""The conformance gate, wired fail-closed before this consumer claims.

THE ROUTE DECLARATION IS TESTED IN BOTH DIRECTIONS, and that is the half most
likely to rot. A route this consumer calls but does not declare is a halt the
gate cannot see -- under INCOMPLETE the run proceeds having promised the
contract covers a call it does not describe. A route declared but never called
is a false claim about my own surface, and it makes the declaration look
complete when it has merely grown.

The operator's demonstration requirement -- "an intentionally incompatible
engine prevents actual work, and a conformant engine permits it" -- is not
satisfiable by asserting that a command can run. The tests below drive the
real decision function with real contract files and assert on the CONSEQUENCE:
whether a row could be claimed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
REPO = VIVARIUM.parent
for p in (str(VIVARIUM), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

from viv import conformance as _conf                            # noqa: E402
from viv import loop as _loop                                   # noqa: E402
from viv import queue as _q                                     # noqa: E402
from viv.loop import BLOCKED, Vivarium                          # noqa: E402

from conftest import make_spec                                  # noqa: E402

CONTRACT = REPO / "roles/Harmonia/contracts/sfe_contract.json"


# ===========================================================================
# The declaration -- both directions
# ===========================================================================

def test_every_declared_route_is_in_the_contract():
    """If this fails the gate halts under INCOMPLETE for a reason that does
    not exist: a spelling difference. The contract writes {aid} and {rid}
    where the client writes {artifact_id} and {reservation_id}."""
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    have = {"%s %s" % (r["method"], r["path"]) for r in C["routes"]}
    missing = sorted(set(_conf.CONSUMER_ROUTES) - have)
    assert not missing, "declared but absent from the contract: %s" % missing


def test_every_engine_route_viv_calls_is_declared():
    """The direction that actually protects the science. Derived from the
    CLIENT SOURCE, so adding a call without declaring it fails here rather
    than at 3am in a halt -- or worse, not at all, under INCOMPLETE."""
    import re
    client = (REPO / "SerendipityFoundry/SerendipityFoundryClient/sfclient"
                     "/client.py").read_text(encoding="utf-8", errors="replace")
    bodies = {}
    for m in re.finditer(r"\n    def (\w+)\(", client):
        nxt = client.find("\n    def ", m.end())
        bodies[m.group(1)] = client[m.end():nxt if nxt > 0 else len(client)]

    called = set()
    for f in (VIVARIUM / "viv").glob("*.py"):
        for m in re.finditer(r"\.(\w+)\(",
                             f.read_text(encoding="utf-8", errors="replace")):
            called.add(m.group(1))

    def shape(path):
        return re.sub(r"\{[^}]+\}", "{}", path.split("?")[0].rstrip("/"))

    declared = {(r.split(" ", 1)[0], shape(r.split(" ", 1)[1]))
                for r in _conf.CONSUMER_ROUTES}
    undeclared = set()
    for name, body in bodies.items():
        if name not in called or name.startswith("__"):
            continue
        for m in re.finditer(
                r"""_req\(\s*["']([A-Z]+)["']\s*,\s*f?["']([^"']+)["']""",
                body):
            if (m.group(1), shape(m.group(2))) not in declared:
                undeclared.add("%s %s  (sfclient.%s)"
                               % (m.group(1), m.group(2), name))
    assert not undeclared, ("viv calls engine routes it does not declare: %s"
                            % sorted(undeclared))


def test_the_declaration_is_not_padded():
    """A declaration that lists the whole contract would pass the test above
    and mean nothing. 24 of 67 is a claim about this consumer."""
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert len(_conf.CONSUMER_ROUTES) < len(C["routes"])
    assert len(set(_conf.CONSUMER_ROUTES)) == len(_conf.CONSUMER_ROUTES)


# ===========================================================================
# The four consequences, driven through the real decision function
# ===========================================================================

def _contract_variant(tmp_path, **engine_overrides):
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    C["engine"].update(engine_overrides)
    p = tmp_path / "contract.json"
    p.write_text(json.dumps(C), encoding="utf-8")
    return p


def test_a_wrong_engine_instance_halts_before_any_route_check(tmp_path,
                                                              monkeypatch):
    """WRONG_INSTANCE is the failure that corrupts attribution SILENTLY
    instead of halting work: the rows land in a real ledger, just not the one
    the contract describes. It never bends, in any state, and it is decided
    from the identity call alone -- no route diff, no probe client."""
    live = {"engine_instance_id": "eng_SOMETHING_ELSE",
            "engine_source_hash": "sha256:" + "0" * 64, "schema_version": 8,
            "science_profile": "x", "session_enforcement": "y"}
    monkeypatch.setattr(_conf, "identity", lambda *a, **k: dict(live))
    called = []
    monkeypatch.setattr(_conf, "full_gate",
                        lambda *a, **k: called.append(1) or {})
    rec = _conf.evaluate(_conf.Config(cache_path=str(tmp_path / "c.json")),
                         schema="viv")
    assert rec["state"] == "WRONG_INSTANCE"
    assert rec["halted"] is True
    assert not called, "the instance mismatch must decide without the full gate"


def test_an_unreachable_engine_retries_then_halts(tmp_path, monkeypatch):
    """UNREACHABLE is an inability to LOOK, not evidence of drift -- so it is
    retried before it becomes a stop, and it still becomes a stop."""
    tries = []

    def boom(*a, **k):
        tries.append(1)
        raise OSError("connection refused")

    monkeypatch.setattr(_conf, "identity", boom)
    cfg = _conf.Config(retries=2, backoff_s=0.0,
                       cache_path=str(tmp_path / "c.json"))
    rec = _conf.evaluate(cfg, schema="viv")
    assert rec["state"] == "UNREACHABLE"
    assert rec["halted"] is True
    assert len(tries) == 3, "retries+1 attempts, then halt"
    assert len(rec["attempts"]) == 3


def test_drift_halts(tmp_path, monkeypatch):
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    live = {"engine_instance_id": C["engine"]["engine_instance_id"],
            "engine_source_hash": "sha256:" + "d" * 64,
            "schema_version": C["engine"]["schema_version"],
            "science_profile": C["engine"].get("science_profile"),
            "session_enforcement": C["engine"].get("session_enforcement")}
    monkeypatch.setattr(_conf, "identity", lambda *a, **k: dict(live))
    monkeypatch.setattr(_conf, "full_gate", lambda *a, **k: {
        "exit": 1, "state": _conf.DRIFT, "at": "2026-09-11T00:00:00+00:00",
        "elapsed_s": 0.1, "stdout_tail": "DRIFT -- a route was REMOVED"})
    rec = _conf.evaluate(_conf.Config(cache_path=str(tmp_path / "c.json")),
                         schema="viv")
    assert rec["state"] == _conf.DRIFT and rec["halted"] is True


def test_incomplete_with_an_undeclared_route_halts(tmp_path, monkeypatch):
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    live = {"engine_instance_id": C["engine"]["engine_instance_id"],
            "engine_source_hash": "sha256:" + "e" * 64,
            "schema_version": C["engine"]["schema_version"],
            "science_profile": C["engine"].get("science_profile"),
            "session_enforcement": C["engine"].get("session_enforcement")}
    monkeypatch.setattr(_conf, "identity", lambda *a, **k: dict(live))
    monkeypatch.setattr(_conf, "full_gate", lambda *a, **k: {
        "exit": 3, "state": _conf.INCOMPLETE, "at": "2026-09-11T00:00:00+00:00",
        "elapsed_s": 0.1,
        "stdout_tail": "HALT: 1 route(s) you will call are NOT in the contract"})
    rec = _conf.evaluate(_conf.Config(cache_path=str(tmp_path / "c.json")),
                         schema="viv")
    assert rec["state"] == "INCOMPLETE_HALT" and rec["halted"] is True


def test_incomplete_with_every_route_covered_PROCEEDS(tmp_path, monkeypatch):
    """The state that makes the gate survivable. The build moved by ADDITION
    only; nothing the contract describes was removed; every route this
    consumer calls is still described. Halting here would be halting for no
    reason, and a gate that halts for no reason gets unwired."""
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    live = {"engine_instance_id": C["engine"]["engine_instance_id"],
            "engine_source_hash": "sha256:" + "f" * 64,
            "schema_version": C["engine"]["schema_version"],
            "science_profile": C["engine"].get("science_profile"),
            "session_enforcement": C["engine"].get("session_enforcement")}
    monkeypatch.setattr(_conf, "identity", lambda *a, **k: dict(live))
    monkeypatch.setattr(_conf, "full_gate", lambda *a, **k: {
        "exit": 0, "state": _conf.CONFORMANT, "at": "2026-09-11T00:00:00+00:00",
        "elapsed_s": 0.1,
        "stdout_tail": "Every route you declared IS in the contract, so its "
                       "claims\ncover your calls. PROCEED"})
    rec = _conf.evaluate(_conf.Config(cache_path=str(tmp_path / "c.json")),
                         schema="viv")
    assert rec["state"] == "INCOMPLETE_PROCEED"
    assert rec["halted"] is False


def test_a_conformant_engine_permits_work(tmp_path, monkeypatch):
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    live = {"engine_instance_id": C["engine"]["engine_instance_id"],
            "engine_source_hash": C["engine"]["engine_source_hash"],
            "schema_version": C["engine"]["schema_version"],
            "science_profile": C["engine"].get("science_profile"),
            "session_enforcement": C["engine"].get("session_enforcement")}
    monkeypatch.setattr(_conf, "identity", lambda *a, **k: dict(live))
    monkeypatch.setattr(_conf, "full_gate", lambda *a, **k: {
        "exit": 0, "state": _conf.CONFORMANT, "at": "2026-09-11T00:00:00+00:00",
        "elapsed_s": 0.1, "stdout_tail": "CONFORMANT -- safe to proceed"})
    rec = _conf.require(_conf.Config(cache_path=str(tmp_path / "c.json")),
                        schema="viv")
    assert rec["state"] == "CONFORMANT" and rec["halted"] is False


# ===========================================================================
# The gate cannot be switched off where it matters
# ===========================================================================

def test_the_override_is_ignored_in_the_production_schema(tmp_path,
                                                          monkeypatch):
    """The one property that decides whether any of this is real."""
    monkeypatch.setenv("VIV_CONFORMANCE_MODE", "off")
    monkeypatch.setattr(_conf, "identity",
                        lambda *a, **k: (_ for _ in ()).throw(
                            OSError("refused")))
    rec = _conf.evaluate(_conf.Config(enabled=False, retries=0, backoff_s=0.0,
                                      cache_path=str(tmp_path / "c.json")),
                         schema="viv")
    assert rec["state"] == "UNREACHABLE" and rec["halted"] is True


def test_the_override_is_honoured_outside_it(tmp_path, monkeypatch):
    monkeypatch.setenv("VIV_CONFORMANCE_MODE", "off")
    rec = _conf.evaluate(_conf.Config(cache_path=str(tmp_path / "c.json")),
                         schema="viv_test_something")
    assert rec["state"] == "DISABLED_TEST_SCHEMA" and rec["halted"] is False


def test_a_gate_that_cannot_be_read_is_not_a_gate_that_passed(tmp_path,
                                                              monkeypatch):
    monkeypatch.setattr(_conf, "_abs",
                        lambda p: tmp_path / "does-not-exist.json")
    with pytest.raises(Exception):
        _conf.evaluate(_conf.Config(), schema="viv")


# ===========================================================================
# The consequence at the boundary: NOTHING IS CLAIMED
# ===========================================================================

def test_a_halt_blocks_the_tick_and_claims_NOTHING(conn, schema, monkeypatch):
    """The reason the gate sits before `claim` and not at dispatch. A halt
    with a row already claimed would strand it, and invariant 6 forbids
    resolving a stranded row by inference -- so every halt would cost a human
    release. Here the queue is left exactly as it was."""
    _q.enqueue(conn, created_by="t", source_reason="conformance-test",
               experiment_spec=make_spec(), schema=schema)
    conn.commit()

    def halt(*a, **k):
        raise _conf.ConformanceHalt({"state": _conf.DRIFT, "halted": True,
                                     "reason": "test"})

    monkeypatch.setattr(_conf, "require", halt)
    v = Vivarium(worker_id="w-gate", schema=schema, config={},
                 conformance=None, log=lambda *a: None)
    rep = v.tick(conn)
    assert rep.outcome == BLOCKED
    assert rep.detail["conformance"]["state"] == _conf.DRIFT
    assert _q.counts(conn, schema=schema).get("queued") == 1
    assert not _q.counts(conn, schema=schema).get("claimed")
    assert _q.active(conn, schema=schema) is None


def test_an_idle_queue_does_not_call_the_engine(conn, schema, monkeypatch):
    """An idle tick is not a crossing. Gating one would put twelve identity
    calls a minute on the engine to authorise nothing, and would make the
    engine's availability a precondition for noticing the queue is empty."""
    calls = []
    monkeypatch.setattr(_conf, "require",
                        lambda *a, **k: calls.append(1) or {"state": "X"})
    v = Vivarium(worker_id="w-idle", schema=schema, config={},
                 conformance=None, log=lambda *a: None)
    v.tick(conn)
    assert calls == []


def test_a_gate_error_blocks_rather_than_proceeds(conn, schema, monkeypatch):
    _q.enqueue(conn, created_by="t", source_reason="conformance-test",
               experiment_spec=make_spec(), schema=schema)
    conn.commit()

    def boom(*a, **k):
        raise RuntimeError("the gate script is missing")

    monkeypatch.setattr(_conf, "require", boom)
    v = Vivarium(worker_id="w-err", schema=schema, config={},
                 conformance=None, log=lambda *a: None)
    rep = v.tick(conn)
    assert rep.outcome == BLOCKED
    assert rep.detail["conformance"]["halted"] is True
    assert _q.counts(conn, schema=schema).get("queued") == 1


class _NoEngine:
    """A runner that proves the tick got past the gate without letting it
    reach an engine. The first version of this test had no runner double and
    no engine config, and `config={}` is FALSY -- so it loaded the PRODUCTION
    configuration and dispatched a real run. The assertion still passed. That
    is the shape of a test that checks the thing it names and does something
    else on the way."""

    def __init__(self):
        self.dispatched = 0

    def run(self, request, on_running=None):
        self.dispatched += 1
        raise RuntimeError("no engine in this test")


def test_conformance_false_is_the_only_way_a_test_skips_the_gate(conn, schema,
                                                                 monkeypatch):
    calls = []
    monkeypatch.setattr(_conf, "require",
                        lambda *a, **k: calls.append(1) or {"state": "X"})
    _q.enqueue(conn, created_by="t", source_reason="conformance-test",
               experiment_spec=make_spec(), schema=schema)
    conn.commit()
    runner = _NoEngine()
    v = Vivarium(worker_id="w-off", schema=schema, config={},
                 conformance=False, runner=runner, log=lambda *a: None)
    v.tick(conn)
    assert calls == [], "the gate must not have run"
    assert runner.dispatched == 1, "and the tick must have got past it"


def test_compact_matches_archaeons_field_names():
    """A producer row and an executor row must join without a translation
    table. Reconciliation has already cost this campaign one false pair of
    engine defects (TRACKA-RECON-2 is the open one)."""
    pytest.importorskip("archaeon.conformance")
    from archaeon import conformance as a_conf
    rec = {"schema": "vivarium.conformance.v1", "state": "CONFORMANT",
           "halted": False, "at": "2026-09-11T00:00:00+00:00",
           "live": {}, "contract": {}, "consumer_routes": [],
           "gate": {"mode": "full", "exit": 0, "at": "x"}}
    assert set(_conf.compact(rec)) == set(a_conf.compact(rec))
