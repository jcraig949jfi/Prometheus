"""Harness and economics checks (stub only; no model, no GPU needed)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import economics as E  # noqa: E402

REQUIRED = ["harness_sha256", "harness_git_head", "host_label", "frozen_settings", "model", "gpu_identity",
            "starting_accuracy", "measured", "projection_single_host"]
MEASURED = ["tokens_in_per_task", "tokens_out_per_task", "tokens_per_task_mean", "wall_s_per_eval",
            "evaluations_per_generation", "model_calls_per_generation", "failure_rate", "retry_rate",
            "eval_throughput_per_s", "gpu"]


def run_stub(tmp_path, label):
    out = tmp_path / f"{label}.json"
    subprocess.run([sys.executable, str(HERE / "bench.py"), "--stub", "--host-label", label, "--model", "stub-model",
                    "--out", str(out)], check=True, capture_output=True, timeout=600)
    return json.loads(out.read_text(encoding="utf-8"))


def test_stub_receipt_has_every_required_field(tmp_path):
    r = run_stub(tmp_path, "STUB1")
    for k in REQUIRED:
        assert k in r, k
    for k in MEASURED:
        assert k in r["measured"], k
    assert r["starting_accuracy"]["n"] == 200
    assert {p["lineages"] for p in r["projection_single_host"]} == {32, 64}


def test_economics_shards_by_measured_capacity_not_2x():
    alloc, days = E.shard(64, {"M1": 3.0, "M2": 1.0})
    assert alloc == {"M1": 48, "M2": 16} and abs(days - 16.0) < 1e-9
    alloc1, days1 = E.shard(64, {"M1": 3.0})
    assert alloc1 == {"M1": 64} and abs(days1 - 64 / 3) < 1e-9


def test_economics_rejects_a_modified_harness(tmp_path):
    r = run_stub(tmp_path, "STUB2")
    assert E.valid(r, r["harness_sha256"]) == []
    assert "harness sha256 differs" in E.valid(r, "0" * 64)[0]


def test_no_eligible_substrate_path(tmp_path):
    r = run_stub(tmp_path, "STUB3")
    r["starting_accuracy"]["accuracy"] = 0.95
    p = tmp_path / "r.json"
    p.write_text(json.dumps(r), encoding="utf-8")
    out = subprocess.run([sys.executable, str(HERE / "economics.py"), r["harness_sha256"], str(p)],
                         capture_output=True, text=True, timeout=120).stdout
    assert json.loads(out)["selection"] == "NO_ELIGIBLE_SUBSTRATE"
