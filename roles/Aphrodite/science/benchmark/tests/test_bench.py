"""Harness, bundle and economics checks (stub only; no model, no GPU)."""
import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import economics as E  # noqa: E402


def run_stub_bench(tmp_path, label):
    out = tmp_path / f"{label}.json"
    subprocess.run([sys.executable, str(HERE / "bench.py"), "--stub", "--host-label", label, "--model", "stub-model",
                    "--out", str(out)], check=True, capture_output=True, timeout=600)
    return json.loads(out.read_text(encoding="utf-8"))


def fake_manifest(r):
    return {"canonical_sha256": "c" * 64, "files": {"bench.py": r["harness_sha256"]}}


def stamp(r):
    r = copy.deepcopy(r)
    r["bundle_manifest_sha256"], r["bundle_verified"] = "c" * 64, True
    return r


def test_stub_receipt_fields(tmp_path):
    r = run_stub_bench(tmp_path, "S1")
    for k in ("starting_accuracy", "measured", "projection_single_host", "gpu_identity", "model"):
        assert k in r
    assert r["starting_accuracy"]["n"] == 200 and len(r["starting_accuracy"]["by_family"]) == 4


def test_validity_requires_bundle_stamp_and_frozen_harness(tmp_path):
    r = run_stub_bench(tmp_path, "S2")
    m = fake_manifest(r)
    assert any("bundle manifest" in p for p in E.valid(r, m))
    assert E.valid(stamp(r), m) == []
    bad = dict(m, files={"bench.py": "0" * 64})
    assert any("harness sha256" in p for p in E.valid(stamp(r), bad))


def test_three_bounds_and_decision_is_the_larger_projection(tmp_path):
    r = run_stub_bench(tmp_path, "S3")
    r["measured"]["per_generation"] = [{"wall_s": 10, "evaluations": 80, "evals_per_s": 8.0},
                                       {"wall_s": 10, "evaluations": 80, "evals_per_s": 8.0},
                                       {"wall_s": 10, "evaluations": 80, "evals_per_s": 8.0},
                                       {"wall_s": 40, "evaluations": 80, "evals_per_s": 2.0}]   # one stall
    r["measured"]["eval_throughput_per_s"]["conservative"] = 6.5
    b = E.bounds(r)
    assert b["B_slowest_generation"] == 2.0
    assert b["DECISION"] == min(b["C_variance_aware_upper95"], 6.5)
    assert b["DECISION"] > b["B_slowest_generation"]   # one stall does not define the estimate alone


def test_sharding_uses_measured_capacity_not_2x():
    alloc, days = E.shard(64, {"M1": 3.0, "M2": 1.0})
    assert alloc == {"M1": 48, "M2": 16} and abs(days - 16.0) < 1e-9


def run_econ(tmp_path, m, receipts):
    mp = tmp_path / "man.json"
    mp.write_text(json.dumps(m), encoding="utf-8")
    ps = []
    for i, r in enumerate(receipts):
        p = tmp_path / f"r{i}.json"
        p.write_text(json.dumps(r), encoding="utf-8")
        ps.append(str(p))
    return json.loads(subprocess.run([sys.executable, str(HERE / "economics.py"), str(mp)] + ps,
                                     capture_output=True, text=True, timeout=120).stdout)


def test_anomaly_blocks_combination_and_variants_are_not_averaged(tmp_path):
    r = stamp(run_stub_bench(tmp_path, "M1"))
    r["starting_accuracy"]["accuracy"] = 0.40
    r2 = copy.deepcopy(r)
    r2["host_label"], r2["starting_accuracy"]["accuracy"] = "M2", 0.50     # same variant, 10-point gap
    out = run_econ(tmp_path, fake_manifest(r), [r, r2])
    v = list(out["variants"].values())[0]
    assert v["combined"] is None and not v["selectable"] and any("ANOMALY" in n for n in v["notes"])


def test_different_quant_is_a_different_variant(tmp_path):
    r = stamp(run_stub_bench(tmp_path, "M1"))
    r["starting_accuracy"]["accuracy"] = 0.40
    r2 = copy.deepcopy(r)
    r2["host_label"], r2["model"]["quant"] = "M2", "Q8_0"
    out = run_econ(tmp_path, fake_manifest(r), [r, r2])
    assert len(out["variants"]) == 2


def test_no_eligible_substrate(tmp_path):
    r = stamp(run_stub_bench(tmp_path, "M1"))
    r["starting_accuracy"]["accuracy"] = 0.95
    assert run_econ(tmp_path, fake_manifest(r), [r])["selection"] == "NO_ELIGIBLE_SUBSTRATE"
