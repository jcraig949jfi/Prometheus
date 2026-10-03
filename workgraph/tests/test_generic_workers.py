"""Generic workers, execution modes, epic priority bands, preemption and the operator priority queue
(operator directive 2026-10-03, roles/Achilles/prompts/2026-10-03_generic_workers/). Includes the directive's
completion simulations A-D, run end to end through workgraph.worker with a filesystem store."""
import datetime
import json
import shutil
import sys
from pathlib import Path

import pytest

from workgraph import core, priority as P, worker as Wk, cwo

NOW = datetime.datetime(2026, 10, 3, 12, 0, 0, tzinfo=datetime.timezone.utc)
SHA = "a" * 40


def _ops(tmp_path):
    """A copy of the real epics/threads plus empty campaigns/ and operator_queue/."""
    ops = tmp_path / "repo" / "ops"
    shutil.copytree(core.OPS / "epics", ops / "epics")
    (ops / "threads").mkdir(parents=True)
    for _, e in core.load_epics().values():
        for th in e.get("threads", []):
            shutil.copy(core.OPS / "threads" / (th + ".md"), ops / "threads")
    (ops / "campaigns").mkdir()
    (ops / "operator_queue" / "priority").mkdir(parents=True)
    return ops


def _campaign(ops, cid, thread, epic, coordinator):
    d = ops / "campaigns" / cid / "tasks"
    d.mkdir(parents=True)
    camp = {"schema": core.CAMPAIGN_SCHEMA, "campaign_id": cid, "thread_id": thread, "epic_id": epic, "title": cid,
            "objective": "o", "coordinator_role": coordinator, "authority": "test",
            "quality_classes": {"Q1": {"description": "mechanical", "rank": 1}, "Q2": {"description": "x", "rank": 2}}}
    (ops / "campaigns" / cid / "CAMPAIGN.json").write_text(json.dumps(camp))


def _generic(ops, cid, tid, owner, cmd, experiment=None, local=0, created="2026-10-03T00:00:00Z", **kw):
    t = {"schema": core.TASK_SCHEMA, "task_id": tid, "campaign_id": cid, "title": tid, "objective": "execute",
         "owner_role": owner, "quality_class": "Q1", "can_downgrade": False, "escalate_to": "Q2", "depends_on": [],
         "problem": "run the registered command unchanged", "non_goals": ["no interpretation"],
         "evidence_required": ["receipt"], "acceptance": {"condition": "exit 0"}, "deliverables": ["out/"],
         "kind": "operations", "executor_class": "GENERIC_WORKER", "execution_mode": "ATOMIC", "local_priority": local,
         "execution": {"source_sha": SHA, "command": cmd, "environment": {"vars": {}}, "inputs": [],
                       "resources": {"cpu": 1}, "timeout_s": 120, "output_dir": "out",
                       "success_criteria": {"exit_code": 0}, "cleanup": "REMOVE_WORKTREE",
                       "preemption_policy": "REPLAY_FROM_START"},
         "status": "READY", "history": [{"status": "PROPOSED", "by": owner, "at_utc": created},
                                        {"status": "READY", "by": owner, "at_utc": created}]}
    if experiment:
        t["experiment_id"] = experiment
    t.update(kw)
    d = ops / "campaigns" / cid / "tasks" / tid
    d.mkdir(parents=True)
    (d / "TASK.json").write_text(json.dumps(t))
    return d


def _named(ops, cid, tid, owner, experiment=None):
    d = _generic(ops, cid, tid, owner, [sys.executable, "-c", "pass"], experiment)
    t = json.loads((d / "TASK.json").read_text())
    t["executor_class"] = "NAMED_SEAT"; t["kind"] = "review"; t.pop("execution")
    (d / "TASK.json").write_text(json.dumps(t))
    return d


def _prq(ops, rid, requester, epic, campaign, experiment, status="REQUESTED", expires="2026-10-05T00:00:00Z", **kw):
    r = {"schema": P.PRQ_SCHEMA, "request_id": rid, "requester": requester, "epic_id": epic,
         "thread_id": "TH-P2B-ENGINE-HARDENING", "campaign_id": campaign, "experiment_id": experiment,
         "current_priority": "LOW", "requested_priority": "MEDIUM", "request_type": "PREEMPTION_PROTECTION",
         "reason": "long run worth finishing", "scientific_value": "v", "why_now": "idle window now",
         "if_delayed": "restart costs 20h", "resources": "cpu8", "expected_runtime": "20h", "restart_cost": "20h",
         "preemptible": True, "window": "next 48h", "created_at_utc": "2026-10-03T01:00:00Z",
         "expires_at_utc": expires, "status": status, "operator_decision": None, "operator_note": None,
         "decided_at_utc": None}
    r.update(kw)
    f = ops / "operator_queue" / "priority" / (rid + ".json")
    f.write_text(json.dumps(r))
    return f


PROBE = {"host": "testhost", "os": "x", "python": "3", "cpu": 4, "ram_gb_available": 4.0, "gpu": 0, "gpus": [],
         "disk_gb_free": 50.0, "caps": []}


@pytest.fixture(autouse=True)
def _fixed_probe(monkeypatch):
    monkeypatch.setattr(Wk, "probe", lambda base: dict(PROBE))


# ------------------------------------------------------------------------------------------- roles / identity

def test_generic_worker_role_is_a_shared_layer_not_a_seat():
    from comms import api
    assert "generic-worker-role" not in api.roster()
    text = (core.ROLES / "generic-worker-role" / "RESPONSIBILITIES.md").read_text(encoding="utf-8")
    assert "Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md" in text
    assert "PrometheusWorker/<hostname>/<instance>" in text and not (core.ROLES / "PrometheusWorker").exists()


def test_prometheusworker_bootstrap_identity_and_dry_run(tmp_path, capsys):
    ident = Wk.identity("abc12345", "ELSA")
    assert ident == "PrometheusWorker/elsa/abc12345" and core.is_worker(ident)
    assert not core.is_worker("Nestor") and not core.is_worker("PrometheusWorker/elsa") and not core.is_worker("Nestor[m1-x]")
    assert Wk.main(["--dry-run", "--base", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "roles/generic-worker-role/" in out and "PrometheusWorker/" in out


# ------------------------------------------------------------------------------------------- packet validation

def test_generic_packet_must_be_complete(tmp_path):
    ops = _ops(tmp_path); _campaign(ops, "C-100", "TH-P2B-ENGINE-HARDENING", "EP-PHASE2B", "Nestor")
    d = _generic(ops, "C-100", "T1", "Nestor", [sys.executable, "-c", "pass"])
    assert core.validate_all(ops / "campaigns", ops) == {}
    t = json.loads((d / "TASK.json").read_text()); del t["execution"]["timeout_s"]; t["execution"]["command"] = "run.sh"
    errs = core.validate_task(t, json.loads((ops / "campaigns" / "C-100" / "CAMPAIGN.json").read_text()))
    assert any("missing timeout_s" in e for e in errs) and any("non-empty argv list" in e for e in errs)
    t2 = dict(json.loads((d / "TASK.json").read_text()), executor_class="ROBOT")
    assert any("executor_class must be one of" in e for e in core.validate_task(t2))


def test_execution_modes_and_sharding_and_checkpoint():
    base = json.loads(json.dumps({"executor_class": "NAMED_SEAT"}))
    assert not any("execution_mode" in e for e in core.validate_task(dict(base, execution_mode="ATOMIC")))
    assert not any("execution_mode" in e for e in core.validate_task(dict(base, execution_mode="NATIVE_PARALLEL")))
    assert any("execution_mode must be one of" in e for e in core.validate_task(dict(base, execution_mode="FANOUT")))
    errs = core.validate_task(dict(base, execution_mode="SHARDABLE", sharding={"shards": 8, "unit": "seed"}))
    assert any("SHARDABLE needs registered sharding" in e for e in errs)
    ok = {"shards": 8, "unit": "seed", "aggregation": "mean over seeds", "restart": "per shard", "merge": "concat"}
    assert not any("SHARDABLE" in e for e in core.validate_task(dict(base, execution_mode="SHARDABLE", sharding=ok)))
    g = {"executor_class": "GENERIC_WORKER", "execution": {k: 1 for k in core.GENERIC_EXECUTION_REQUIRED}}
    g["execution"].update(command=["x"], preemption_policy="NATIVE_CHECKPOINT", source_sha=SHA)
    assert any("NATIVE_CHECKPOINT needs a registered" in e for e in core.validate_task(g))
    assert any("local_priority must be" in e for e in core.validate_task(dict(base, local_priority=1000)))


def test_existing_packets_default_to_named_seat_and_c004_still_valid():
    assert core.validate_all() == {}
    t = core.load_tasks()["C-004-T000"][1]
    assert core.executor_class(t) == "NAMED_SEAT"
    assert P.effective(t, core.load_campaigns(), core.OPS, [])["band"] == "HIGH"


def test_rso_builders_remain_phase3_only():
    for seat in ("Palamedes", "Pallas", "Argus", "Cadmus", "Eupalamus"):
        assert core.seat_scope(seat) == ["EP-PHASE3"]


# ------------------------------------------------------------------------------------------- priority

def test_epic_bands_inherit_and_local_priority_cannot_cross(tmp_path):
    ops = _ops(tmp_path)
    _campaign(ops, "C-100", "TH-P2B-ENGINE-HARDENING", "EP-PHASE2B", "Nestor")
    _campaign(ops, "C-101", "TH-GLOBAL-CONTROL-PLANE", "EP-GLOBAL", "Aporia")
    _campaign(ops, "C-102", "TH-RSO-BUILD", "EP-PHASE3", "Palamedes")
    lo = _generic(ops, "C-100", "LO", "Nestor", ["x"], local=99)
    md = _generic(ops, "C-101", "MD", "Aporia", ["x"], local=0)
    hi = _generic(ops, "C-102", "HI", "Palamedes", ["x"], local=0)
    camps = core.load_campaigns(ops / "campaigns")
    eff = {d.name: P.effective(json.loads((d / "TASK.json").read_text()), camps, ops, []) for d in (lo, md, hi)}
    assert (eff["LO"]["band"], eff["MD"]["band"], eff["HI"]["band"]) == ("LOW", "MEDIUM", "HIGH")
    order = sorted(eff, key=lambda k: P.sort_key(eff[k]))
    assert order == ["HI", "MD", "LO"]                      # local 99 does not lift LOW over MEDIUM
    assert eff["LO"]["preemptible"] and not eff["HI"]["preemptible"]
    assert P.may_preempt(eff["LO"], eff["HI"]) and not P.may_preempt(eff["HI"], eff["LO"])
    assert not P.may_preempt(eff["LO"], dict(eff["LO"], local=0))   # same band never preempts


def test_overrides_need_approval_propagate_to_experiment_only_and_expire(tmp_path):
    ops = _ops(tmp_path); _campaign(ops, "C-100", "TH-P2B-ENGINE-HARDENING", "EP-PHASE2B", "Aether")
    a = _generic(ops, "C-100", "A1", "Aether", ["x"], experiment="E-AE1")
    a2 = _generic(ops, "C-100", "A2", "Aether", ["x"], experiment="E-AE1")
    b = _generic(ops, "C-100", "B1", "Aether", ["x"], experiment="E-AE2")
    camps = core.load_campaigns(ops / "campaigns")
    tk = {d.name: json.loads((d / "TASK.json").read_text()) for d in (a, a2, b)}
    f = _prq(ops, "PRQ-20261003-Aether-1", "Aether", "EP-PHASE2B", "C-100", "E-AE1")
    q = ops / "operator_queue"
    assert P.active_overrides(q, NOW) == []                                           # REQUESTED: nothing
    assert P.effective(tk["A1"], camps, ops, P.active_overrides(q, NOW))["band"] == "LOW"
    forged = json.loads(f.read_text()); forged["status"] = "APPROVED"; f.write_text(json.dumps(forged))
    assert P.active_overrides(q, NOW) == []                                           # not decided by the operator
    P.decide(f, "APPROVED", "allow it to finish", now=NOW)
    ov = P.active_overrides(q, NOW)
    bands = {k: P.effective(t, camps, ops, ov)["band"] for k, t in tk.items()}
    assert bands == {"A1": "MEDIUM", "A2": "MEDIUM", "B1": "LOW"}                    # experiment only, not the seat
    late = NOW + datetime.timedelta(days=3)
    assert P.active_overrides(q, late) == []                                          # expiry removes it
    assert P.effective(tk["A1"], camps, ops, P.active_overrides(q, late))["band"] == "LOW"


def test_priority_request_schema():
    good = {k: "x" for k in P.PRQ_REQUIRED}
    good.update(schema=P.PRQ_SCHEMA, request_type="DEADLINE", status="REQUESTED", current_priority="LOW",
                requested_priority="HIGH", created_at_utc="2026-10-03T00:00:00Z", expires_at_utc="2026-10-04T00:00:00Z",
                operator_decision=None, operator_note=None, decided_at_utc=None)
    assert P.validate_request(good) == []
    assert any("needs an expiry" in e for e in P.validate_request(dict(good, expires_at_utc=None)))
    assert any("must be above" in e for e in P.validate_request(dict(good, requested_priority="LOW")))
    assert any("request_type must be" in e for e in P.validate_request(dict(good, request_type="PLEASE")))
    assert any("decided_by 'operator'" in e for e in P.validate_request(dict(good, status="APPROVED")))


def test_queue_view_and_digest_are_deterministic(tmp_path):
    ops = _ops(tmp_path)
    _prq(ops, "PRQ-20261003-Aether-1", "Aether", "EP-PHASE2B", "C-100", "E-AE1")
    f2 = _prq(ops, "PRQ-20261003-Nestor-1", "Nestor", "EP-PHASE2B", "C-100", "E-N1", created_at_utc="2026-10-03T02:00:00Z")
    P.decide(f2, "DENIED", "not now", now=NOW)
    q = ops / "operator_queue"
    md1, md2 = P.render_markdown(q), P.render_markdown(q)
    assert md1 == md2 and "## Open (1)" in md1 and "PRQ-20261003-Aether-1" in md1 and "DENIED" in md1
    dg = P.digest(q, since_utc="2026-10-03T00:00:00Z")
    assert [r["request"] for r in dg["open"]] == ["PRQ-20261003-Aether-1"] and dg["decided_since"]["denied"] == 1
    from achilles.census import render
    md, h = render.operator_queue_block(dg)
    assert md[0].startswith("**Operator Priority Requests -- 1 open**") and "denied 1" in md[0]
    assert "PRQ-20261003-Aether-1" in "".join(h) and render.operator_queue_block(dg) == (md, h)


# ------------------------------------------------------------------------------------------- simulations A-D

def _store(ops, on_sync=None):
    return Wk.FsStore(ops.parent, on_sync)


def test_case_A_low_priority_atomic_run_is_preempted_and_replays_unchanged(tmp_path):
    ops = _ops(tmp_path)
    _campaign(ops, "C-100", "TH-P2B-ENGINE-HARDENING", "EP-PHASE2B", "Nestor")
    _campaign(ops, "C-102", "TH-RSO-BUILD", "EP-PHASE3", "Palamedes")
    slow = [sys.executable, "-c", "import time,os; os.makedirs('out',exist_ok=True); time.sleep(3); open('out/r.txt','w').write('ok')"]
    nd = _generic(ops, "C-100", "NPE-REPLAY", "Nestor", slow, experiment="NPE-X")
    before = json.loads((nd / "TASK.json").read_text())
    state = {"n": 0}

    def arrive():                                  # Phase 3 work arrives while Nestor's run is going
        state["n"] += 1
        if state["n"] == 2:
            _generic(ops, "C-102", "RSO-BATTERY", "Palamedes", [sys.executable, "-c", "pass"])
    ident = "PrometheusWorker/testhost/w1"
    r1 = Wk.run_one(_store(ops, arrive), ident, tmp_path / "base", poll_s=0.2, now=NOW)
    assert r1["outcome"] == "PREEMPTED_RESOURCE" and r1["receipt"]["preempted_by"] == "RSO-BATTERY"
    after = json.loads((nd / "TASK.json").read_text())
    assert after["status"] == "READY" and not (nd / "LEASE.json").exists()
    assert after["execution"] == before["execution"] and after["experiment_id"] == "NPE-X"   # same registration
    rec = r1["receipt"]
    assert rec["result"] == "PREEMPTED_RESOURCE" and core.validate_receipt(rec) == []
    assert after["status"] not in ("FAILED_AS_DESIGNED", "ESCALATED")                     # no verdict, no defect
    r2 = Wk.run_one(_store(ops), ident, tmp_path / "base", poll_s=0.2, now=NOW)
    assert r2["task_id"] == "RSO-BATTERY" and r2["outcome"] == "DONE_CLEAN"                # HIGH runs first
    r3 = Wk.run_one(_store(ops), ident, tmp_path / "base", poll_s=0.2, now=NOW)
    assert r3["task_id"] == "NPE-REPLAY" and r3["outcome"] == "DONE_CLEAN"                 # replayed unchanged
    results = sorted(core._load(f)["result"] for f in nd.glob("attempts/*/RECEIPT.json"))
    assert results == ["DONE_CLEAN", "PREEMPTED_RESOURCE"]
    ci = cwo.inputs("EP-PHASE2B", 48, ops / "campaigns", now=NOW + datetime.timedelta(hours=1))
    assert [x["task_id"] for x in ci["replay_unchanged"]] == ["NPE-REPLAY"] and "PREEMPTED_RESOURCE" in ci["closed"]


def test_case_B_protected_run_only_after_operator_approval(tmp_path):
    ops = _ops(tmp_path)
    _campaign(ops, "C-100", "TH-P2B-ENGINE-HARDENING", "EP-PHASE2B", "Aether")
    _campaign(ops, "C-102", "TH-RSO-BUILD", "EP-PHASE3", "Palamedes")
    _campaign(ops, "C-101", "TH-GLOBAL-CONTROL-PLANE", "EP-GLOBAL", "Aporia")
    _generic(ops, "C-100", "AGE-LONG", "Aether", ["x"], experiment="AGE-E1")
    _generic(ops, "C-100", "AGE-OTHER", "Aether", ["x"], experiment="AGE-E2")
    f = _prq(ops, "PRQ-20261003-Aether-1", "Aether", "EP-PHASE2B", "C-100", "AGE-E1")
    q = ops / "operator_queue"
    assert "PRQ-20261003-Aether-1" in [r["request"] for r in P.digest(q)["open"]]      # visible to the operator
    camps = core.load_campaigns(ops / "campaigns")
    t = {k: core.load_tasks(ops / "campaigns")[k][1] for k in ("AGE-LONG", "AGE-OTHER")}
    gl = P.effective({"campaign_id": "C-101", "history": []}, camps, ops, [])
    assert P.effective(t["AGE-LONG"], camps, ops, P.active_overrides(q, NOW))["band"] == "LOW"
    P.decide(f, "APPROVED", "worth finishing", now=NOW)
    ov = P.active_overrides(q, NOW)
    long_, other = (P.effective(t[k], camps, ops, ov) for k in ("AGE-LONG", "AGE-OTHER"))
    assert long_["band"] == "MEDIUM" and long_["override"] == "PRQ-20261003-Aether-1" and other["band"] == "LOW"
    assert not P.may_preempt(long_, gl)                       # MEDIUM GLOBAL work no longer displaces it
    assert P.may_preempt(long_, P.effective({"campaign_id": "C-102", "history": []}, camps, ops, ov))  # HIGH still can


def test_case_C_phase3_generic_task_runs_on_a_worker_and_stays_argus_owned(tmp_path):
    ops = _ops(tmp_path); _campaign(ops, "C-102", "TH-RSO-BUILD", "EP-PHASE3", "Palamedes")
    d = _generic(ops, "C-102", "ARGUS-E01", "Argus",
                 [sys.executable, "-c", "import os; os.makedirs('out',exist_ok=True); open('out/res.json','w').write('{}')"])
    r = Wk.run_one(_store(ops), "PrometheusWorker/testhost/w2", tmp_path / "base", poll_s=0.1, now=NOW)
    t = json.loads((d / "TASK.json").read_text())
    assert r["outcome"] == "DONE_CLEAN" and t["status"] == "INTEGRATION_READY" and t["owner_role"] == "Argus"
    assert not (d / "LEASE.json").exists()                 # resources released after execution
    assert r["receipt"]["effective_priority"]["band"] == "HIGH" and r["receipt"]["model"].startswith("none")
    assert [o["path"] for o in r["receipt"]["outputs"]] == ["res.json"]


def test_case_D_ownership_isolation(tmp_path):
    ops = _ops(tmp_path); _campaign(ops, "C-100", "TH-P2B-ENGINE-HARDENING", "EP-PHASE2B", "Nestor")
    g = _generic(ops, "C-100", "GEN", "Nestor", ["x"])
    n = _named(ops, "C-100", "INTERPRET", "Nestor")
    with pytest.raises(ValueError, match="only PrometheusWorker"):
        core.transition(g, "CLAIMED", "Nestor[m1-x]", root=ops / "campaigns")
    with pytest.raises(ValueError, match="only PrometheusWorker"):
        core.transition(g, "CLAIMED", "Palamedes[m1-y]", root=ops / "campaigns")
    with pytest.raises(ValueError, match="a PrometheusWorker may not claim"):
        core.transition(n, "CLAIMED", "PrometheusWorker/testhost/w3", root=ops / "campaigns")
    assert [t["task_id"] for t in core.ready_for("Nestor", ops / "campaigns")] == ["INTERPRET"]
    assert [t[2]["task_id"] for t in Wk.eligible(_store(ops), dict(PROBE))] == ["GEN"]
