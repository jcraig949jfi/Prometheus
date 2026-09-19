"""Bridges (overnight C43; directive s10): honest classification, no distortion of the kernel."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox.backends import sfe_executor as SX


def _exp():
    return Experiment(family="bridge", world=ref("world.integer.v1", world_seed=1), substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()],
                      seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 8}, controls=[ref("control.replay.v1")], objective=ref("objective.survival.v1"))


def test_kernel_payload_runs_and_reports_repro_in_sfe_vocabulary(tmp_path):
    r = SX.run_payload({"experiment": _exp().to_dict()}, seed_root=42, workdir=tmp_path)
    assert r["status"] == "COMPLETED" and r["reproducibility"] == "BIT_DETERMINISTIC" and r["n_runs"] == 4 and r["valid"]
    assert r["receipts_bytes"] and r["summary"]["arm"] == "SUMMARY" and "seed_root 42" in r["note"]


def test_bad_payload_is_a_failed_result_not_an_exception(tmp_path):
    r = SX.run_payload({"experiment": {"family": "x"}}, seed_root=1, workdir=tmp_path)
    assert r["status"] == "FAILED" and r["error"] and not r["receipts_bytes"]
    e = _exp(); e.required_capabilities = frozenset({"ext.physics2d.v1"})
    r2 = SX.run_payload({"experiment": e.to_dict()}, seed_root=1, workdir=tmp_path / "b")
    assert r2["status"] == "BLOCKED_MISSING_CAPABILITY"


def test_kernel_executor_satisfies_the_sfe_executor_contract(tmp_path):
    if not SX.available():
        pytest.skip("sfe not importable on this tree")
    X = SX._sfe()
    ex = SX.KernelExecutor()
    assert ex.kind == "kernel.run_ir"
    wp = X.WorkPackage(work_id="w1", world_id="world-1", kind="kernel.run_ir", payload={"experiment": _exp().to_dict()}, seed_root=7)
    res = ex.execute(wp)
    assert isinstance(res, X.ExecutorResult) and res.status == "COMPLETED" and res.reproducibility in X.REPRO and len(res.artifacts) == 1
    assert json.loads(res.artifacts[0].decode().splitlines()[-1])["receipt_id"] == res.result["summary_receipt_id"]


def test_frontier_mismatches_are_classified():
    from prometheus.toolbox.backends.sfe import mismatches, CLASSIFICATION
    reasons = mismatches(_exp())
    assert reasons and set(CLASSIFICATION.values()) <= {"kernel_defect", "adapter_defect", "target_runtime_limitation", "target_schema_limitation", "unsupported_semantic", "unknown_interface_unavailable"}
    assert CLASSIFICATION["M1"] == "target_schema_limitation" and CLASSIFICATION["M2"] == "target_schema_limitation"


def test_execution_policy_and_vector_objectives_pass_through_the_sfe_executor(tmp_path):
    """C103: the night's IR additions (budget.batch policy, objective.multi.v1) ride through kernel.run_ir unchanged."""
    from prometheus.toolbox.receipt import read_all
    e = _exp(); e.budget = dict(e.budget, batch=4)
    r = SX.run_payload({"experiment": e.to_dict()}, seed_root=42, workdir=tmp_path / "b")
    assert r["status"] == "COMPLETED" and r["valid"] and r["reproducibility"] == "BIT_DETERMINISTIC"
    rows = [x for p in (tmp_path / "b").rglob("*.jsonl") for x in read_all(p) if x["arm"] != "SUMMARY"]
    assert rows and all(x["execution"]["batched"] for x in rows)
    e2 = _exp(); e2.objective = ref("objective.multi.v1", components={"a": ref("objective.survival.v2"), "b": ref("objective.yield_net.v1")})
    r2 = SX.run_payload({"experiment": e2.to_dict()}, seed_root=42, workdir=tmp_path / "v")
    sp = r2["summary"]["science"]["splits"]["train"]
    assert r2["status"] == "COMPLETED" and sp["objective_shape"] == "vector" and set(sp["objective_mean"]) == {"a", "b"}
