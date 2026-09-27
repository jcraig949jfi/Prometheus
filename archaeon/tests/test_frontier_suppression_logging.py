"""Regression: suppression enforcement is logged per STATE TRANSITION, not per scheduler retry (operator authorization 2026-09-26).

Failure mode reproduced: one queued item + one unchanged active suppression + many scheduler ticks. Before the repair every tick wrote a
full BLOCKED_BY_SUPPRESSION event (299,991 identical rows in archaeon/frontier/registry/EVENTS.jsonl, left untouched as evidence).
Everything here runs in a temp registry/queue; nothing is executed (a lifted item hits a stubbed `execute`).
"""
from __future__ import annotations

import json

import pytest

from archaeon.frontier import scheduler as S
from archaeon.frontier import specs as SP
from archaeon.frontier import capabilities as CAP
from archaeon.frontier.registry import Registry
from archaeon.frontier.queues import Queues
from archaeon.frontier.allocation import RULES

TID = "C4-cliff.T1"
STATE0 = {"verdict": "CLIFF_SURVIVES", "falsifier_status": "FALSIFIER_FAILED", "neighbourhood_exhausted": False}


def _sup(active=True, state=STATE0, sid="PROTEUS-46"):
    return {"suppression_id": sid, "_active": active, "covers_experiments": [TID], "covers_families": [], "_source_state": dict(state)}


@pytest.fixture()
def world(tmp_path, monkeypatch):
    S._ENF.clear()
    monkeypatch.setattr(S, "pursue_table", lambda: None)
    reg = Registry(tmp_path / "registry"); q = Queues(tmp_path / "queues")
    spec = SP.make_spec(family_id="C4-cliff", experiment_id=TID, world={"kind": "c6.composed.sample", "seed": 10000, "bin": 3}, profile="v0",
                        population={"source": "c4_parents", "seed": 1, "N": 16}, E=4, generations=20, chunk=10, schedule={"kind": "unlabeled", "seed": 10000},
                        seed=10000, budget_evaluations=320, lane="PROCEDURAL", generator="test")
    lid = reg.create(originating_observation={"key": "t", "summary": "t"}, mode="BREADTH", title="t",
                     transformations=[{"id": TID, "dims": ["x"], "from": "-", "to": "-", "budget_evaluations": 320, "status": "PENDING", "spec": spec}])
    q.push("EXPLOITATION", lineage_id=lid, transformation_id=TID, priority=1.0, lane="PROCEDURAL", budget_evaluations=320)
    return reg, q, lid, CAP.present()


def _tick(reg, q, caps, sups):
    return S.step(reg, q, dict(RULES["initial"]), {}, None, None, caps, sups)


def _events(reg, kind):
    return [json.loads(l) for l in open(reg.events_path, encoding="utf-8") if json.loads(l)["kind"] == kind]


def test_many_ticks_one_transition_retries_recoverable(world):
    reg, q, lid, caps = world
    N = 500
    rs = [_tick(reg, q, caps, [_sup()]) for _ in range(N)]
    assert all(r["status"] == "BLOCKED_BY_SUPPRESSION" for r in rs)          # enforcement itself is unchanged: blocked every tick
    ev = _events(reg, "BLOCKED_BY_SUPPRESSION")
    assert len(ev) == 1 and ev[0]["payload"]["enforcement"] == "STATE_TRANSITION"
    assert ev[0]["payload"]["source_state"] == STATE0 and ev[0]["payload"]["suppression"] == "PROTEUS-46"
    assert [r["event_written"] for r in rs].count(True) == 1
    acc = json.loads((reg.root / S.ENFORCEMENT_FILE).read_text(encoding="utf-8"))           # accounting persisted, separate, flagged
    assert acc["accounting_only"] is True
    (rec,) = acc["open"].values()
    assert rec["retries"] == N and rec["first_blocked_at"] <= rec["last_blocked_at"]
    S._ENF.clear()                                                           # a NEW scheduler invocation (the historical bursts were separate runs)
    _tick(reg, q, caps, [_sup()])
    assert len(_events(reg, "BLOCKED_BY_SUPPRESSION")) == 1
    assert json.loads((reg.root / S.ENFORCEMENT_FILE).read_text(encoding="utf-8"))["open"][rec["lineage_id"] + "|" + TID]["retries"] == N + 1


def test_changed_source_state_or_suppression_emits_new_event(world):
    reg, q, lid, caps = world
    for _ in range(10): _tick(reg, q, caps, [_sup()])
    for _ in range(10): _tick(reg, q, caps, [_sup(state=dict(STATE0, neighbourhood_exhausted=None))])
    for _ in range(10): _tick(reg, q, caps, [_sup(sid="PROTEUS-99")])
    ev = _events(reg, "BLOCKED_BY_SUPPRESSION")
    assert len(ev) == 3
    assert [e["payload"]["suppression"] for e in ev] == ["PROTEUS-46", "PROTEUS-46", "PROTEUS-99"]
    acc = json.loads((reg.root / S.ENFORCEMENT_FILE).read_text(encoding="utf-8"))
    assert [c["reason"] for c in acc["closed"]] == ["SUPERSEDED", "SUPERSEDED"] and all(c["retries"] == 10 for c in acc["closed"])
    assert list(acc["open"].values())[0]["retries"] == 10


def test_lift_then_reapply_emits_lifted_and_new_blocked(world, monkeypatch):
    reg, q, lid, caps = world

    class Ran(Exception):
        pass

    def fake_execute(*a, **k):
        raise Ran()
    monkeypatch.setattr(S, "execute", fake_execute)
    for _ in range(7): _tick(reg, q, caps, [_sup()])
    with pytest.raises(Ran):                                                  # suppression lifted -> the item proceeds to execution
        _tick(reg, q, caps, [_sup(active=False)])
    lifted = _events(reg, "SUPPRESSION_LIFTED")
    assert len(lifted) == 1 and lifted[0]["payload"]["suppression"] == "PROTEUS-46"
    assert "retries" not in json.dumps(lifted[0]["payload"])                 # accounting never enters the scientific stream
    for pool in q.items:                                                      # the stubbed execution left the item CLAIMED; requeue it
        for it in list(q.items[pool].values()):
            q.set_state(pool, it["item_id"], "PENDING")
    for _ in range(5): _tick(reg, q, caps, [_sup()])                         # reapplied
    assert len(_events(reg, "BLOCKED_BY_SUPPRESSION")) == 2
    acc = json.loads((reg.root / S.ENFORCEMENT_FILE).read_text(encoding="utf-8"))
    assert [c["reason"] for c in acc["closed"]] == ["LIFTED"] and acc["closed"][0]["retries"] == 7
    assert list(acc["open"].values())[0]["retries"] == 5

