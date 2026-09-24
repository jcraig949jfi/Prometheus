"""Canary harness regressions, isolated from repository receipts and real CUDA.

Imports and subprocesses explicitly select NumPy, even on GPU-equipped hosts.
Fake device arrays test residency and synchronization, not CUDA correctness.
"""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

_CANARY_DIR = Path(__file__).resolve().parents[1] / "runpod" / "aeth01_canary"
_SOURCE_FILES = ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py")
_CANARY_ENV = (
    "AETH01_CANARY_REQUIRE_GPU", "AETH01_RUN_ID", "AETH01_CANARY_HOURLY_RATE",
    "AETH01_CANARY_MAX_DOLLAR_BUDGET", "AETH01_CANARY_TIMEOUT_SECONDS",
)


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, _CANARY_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def rc(monkeypatch, tmp_path):
    for name in _CANARY_ENV:
        monkeypatch.delenv(name, raising=False)
    # No persistent sys.path or sys.modules changes, and no real CuPy import.
    with patch.dict(sys.modules, {"cupy": None}):
        kernel = _load_module("_canary_test_kernel", "aeth01_gpu_kernel.py")
    oracle = _load_module("_canary_test_oracle", "aeth01_cpu_oracle.py")
    with patch.dict(sys.modules, {
        "aeth01_cpu_oracle": oracle, "aeth01_gpu_kernel": kernel,
    }):
        module = _load_module("_canary_receipt_test", "run_canary.py")
    module.RECEIPT_PATH = str(tmp_path / "receipt.json")
    module.REQUIRE_GPU = False
    return module


def _receipt(rc):
    return json.loads(Path(rc.RECEIPT_PATH).read_text(encoding="utf-8"))


def _schema():
    return json.loads((_CANARY_DIR / "receipt_schema.json").read_text(encoding="utf-8"))


def _successful_corpus(rng, num_trials, num_ticks):
    return num_trials * num_ticks, [], 0.0, 0.0


def _run_canary_subprocess(tmp_path, env_overrides):
    env = {name: value for name, value in os.environ.items() if name not in _CANARY_ENV}
    env.update(env_overrides)
    # run_path executes the real __main__/sys.exit path in an isolated CWD.
    bootstrap = (
        "import os, runpy, sys; sys.modules['cupy'] = None; "
        "sys.path.insert(0, os.path.dirname(sys.argv[1])); "
        "runpy.run_path(sys.argv[1], run_name='__main__')"
    )
    return subprocess.run(
        [sys.executable, "-c", bootstrap, str(_CANARY_DIR / "run_canary.py")],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60,
    )


@pytest.mark.parametrize("require_gpu,status", [
    (None, "FAIL_ENVIRONMENT"), ("1", "FAIL_ENVIRONMENT"), ("0", "PASS"),
])
def test_subprocess_exit_status_and_schema_fields(tmp_path, require_gpu, status):
    overrides = {"AETH01_RUN_ID": "isolated-subprocess-run"}
    if require_gpu is not None:
        overrides["AETH01_CANARY_REQUIRE_GPU"] = require_gpu
    result = _run_canary_subprocess(tmp_path, overrides)
    assert result.returncode == (0 if status == "PASS" else 1), result.stderr
    receipt = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == status
    assert receipt["backend"] == "numpy_fallback"
    assert receipt["run_id"] == "isolated-subprocess-run"
    assert receipt["cases_expected"] == 300
    assert receipt["cases_run"] == receipt["cases_matched"] == (300 if status == "PASS" else 0)
    assert receipt["mismatches"] == []
    assert receipt["finished_at_utc"] is not None
    schema = _schema()
    assert set(schema["required"]) <= receipt.keys() <= schema["properties"].keys()
    for name in _SOURCE_FILES:
        assert receipt["source_hashes"][name] == hashlib.sha256((_CANARY_DIR / name).read_bytes()).hexdigest()


def test_status_vocabulary_and_strict_pass_schema(rc):
    schema = _schema()
    assert set(rc.FINAL_STATUSES) == set(schema["properties"]["status"]["enum"])
    assert schema["properties"]["cases_expected"]["const"] == 300
    gate = schema["allOf"][0]
    assert gate["if"]["properties"]["status"]["const"] == "PASS"
    for name, value in {
        "cases_run": 300, "cases_matched": 300, "single_tick_trials": 200,
        "multi_tick_trials": 20, "multi_tick_steps": 5, "rng_seed": 0,
    }.items():
        assert gate["then"]["properties"][name]["const"] == value
    assert gate["then"]["properties"]["mismatches"]["maxItems"] == 0
    assert "run_id" in schema["properties"] and "run_id" not in schema["required"]


def test_write_receipt_rejects_unknown_status(rc):
    with pytest.raises(AssertionError):
        rc.write_receipt({"status": "NOT_A_REAL_STATUS"})
    assert not Path(rc.RECEIPT_PATH).exists()


def test_source_hashes_are_exact_bundled_file_hashes(rc):
    assert rc._source_hashes() == {
        name: hashlib.sha256((_CANARY_DIR / name).read_bytes()).hexdigest()
        for name in _SOURCE_FILES
    }


@pytest.mark.parametrize("run_id", [None, "", "controller-run-123"])
def test_run_binding_in_placeholder_and_final_receipt(rc, monkeypatch, run_id):
    if run_id is not None:
        monkeypatch.setenv("AETH01_RUN_ID", run_id)
    observed = []
    real_write = rc.write_receipt

    def record_write(receipt):
        real_write(receipt)
        observed.append(_receipt(rc))

    monkeypatch.setattr(rc, "write_receipt", record_write)
    monkeypatch.setattr(rc, "run_corpus", _successful_corpus)
    assert rc.main() == 0
    assert [r["status"] for r in observed] == ["FAIL_INCOMPLETE", "PASS"]
    assert all(r["run_id"] == (run_id or None) for r in observed)
    assert observed[0]["finished_at_utc"] is None
    assert observed[1]["source_hashes"] == rc._source_hashes()


@pytest.mark.parametrize("counts", [(0, 0), (200, 0), (199, 100), (201, 99), (200, 101)])
def test_empty_partial_or_wrongly_partitioned_corpus_never_passes(rc, monkeypatch, counts):
    reports = iter(counts)
    monkeypatch.setattr(rc, "run_corpus", lambda *args: (next(reports), [], 0.0, 0.0))
    assert rc.main() == 1
    receipt = _receipt(rc)
    assert receipt["status"] == "FAIL_INCOMPLETE"
    assert receipt["cases_run"] == receipt["cases_matched"] == sum(counts)
    assert receipt["finished_at_utc"] is not None


@pytest.mark.parametrize("name,value", [
    ("TRIALS", 0), ("TRIALS", 1), ("MULTI_TICK_TRIALS", 0),
    ("MULTI_TICK_STEPS", 0), ("MULTI_TICK_TRIALS", 10),
    ("MULTI_TICK_STEPS", 10), ("RNG_SEED", 1),
])
def test_non_preregistered_configuration_never_passes(rc, monkeypatch, name, value):
    monkeypatch.setattr(rc, name, value)
    monkeypatch.setattr(rc, "run_corpus", _successful_corpus)
    assert rc.main() == 1
    assert _receipt(rc)["status"] == "FAIL_INCOMPLETE"


@pytest.mark.parametrize("failure", ["corpus", "source_hashes"])
def test_exceptions_replace_placeholder_with_bound_error(rc, monkeypatch, failure):
    monkeypatch.setenv("AETH01_RUN_ID", "error-run")

    def fail(*args):
        assert _receipt(rc)["status"] == "FAIL_INCOMPLETE"
        assert _receipt(rc)["run_id"] == "error-run"
        raise RuntimeError("injected canary failure")

    monkeypatch.setattr(rc, "run_corpus" if failure == "corpus" else "_source_hashes", fail)
    assert rc.main() == 1
    receipt = _receipt(rc)
    assert receipt["status"] == "FAIL_ERROR"
    assert "injected canary failure" in receipt["error"]
    assert receipt["run_id"] == "error-run"


def test_missing_source_hash_never_passes(rc, monkeypatch, tmp_path):
    monkeypatch.setattr(rc, "_HERE", str(tmp_path))
    assert rc.main() == 1
    assert _receipt(rc)["status"] == "FAIL_ERROR"


def test_later_error_preserves_completed_corpus_evidence(rc, monkeypatch):
    real_step = rc.gpu_step
    real_corpus = rc.run_corpus

    def corrupt(*args):
        *outputs, counters = real_step(*args)
        outputs[3] = outputs[3] ^ np.uint8(1)
        return (*outputs, counters)

    def fail_second_corpus(rng, trials, ticks):
        if ticks > 1:
            raise RuntimeError("multi-tick failure")
        return real_corpus(rng, 1, ticks)

    monkeypatch.setattr(rc, "gpu_step", corrupt)
    monkeypatch.setattr(rc, "run_corpus", fail_second_corpus)
    assert rc.main() == 1
    receipt = _receipt(rc)
    assert receipt["status"] == "FAIL_ERROR"
    assert receipt["cases_run"] == 1 and receipt["cases_matched"] == 0
    assert len(receipt["mismatches"]) == 1
    assert receipt["mismatches"][0]["corpus"] == "single_tick"
    assert receipt["mismatches"][0]["output_diff"]


def test_interruption_leaves_bound_incomplete_receipt(rc, monkeypatch):
    monkeypatch.setenv("AETH01_RUN_ID", "interrupted-run")
    rc.write_receipt({"status": "PASS", "run_id": "old-run"})

    def interrupt(*args):
        raise KeyboardInterrupt

    monkeypatch.setattr(rc, "run_corpus", interrupt)
    with pytest.raises(KeyboardInterrupt):
        rc.main()
    receipt = _receipt(rc)
    assert receipt["status"] == "FAIL_INCOMPLETE"
    assert receipt["run_id"] == "interrupted-run"
    assert receipt["finished_at_utc"] is None


def test_gpu_outputs_remain_on_device_and_timing_is_synchronized(rc, monkeypatch):
    events = []
    real_step = rc.gpu_step
    previous = None
    steps = 0

    class DeviceArray:
        def __init__(self, values):
            self.values = values

        def get(self):
            events.append("download")
            return self.values.copy()

    def upload(array):
        events.append("upload")
        return DeviceArray(array.copy())

    def device_step(*args):
        nonlocal previous, steps
        events.append("step")
        inputs = args[9:]
        assert all(isinstance(a, DeviceArray) for a in inputs)
        if steps % 5:
            assert all(a is b for a, b in zip(inputs, previous))
        elif previous is not None:
            assert all(a is not b for a, b in zip(inputs, previous))
        *outputs, counters = real_step(*args[:9], *(a.values for a in inputs))
        previous = tuple(DeviceArray(a) for a in outputs)
        steps += 1
        return (*previous, counters)

    def clock():
        events.append("clock")
        return float(events.count("clock"))

    stream = SimpleNamespace(synchronize=lambda: events.append("sync"))
    backend = SimpleNamespace(asarray=upload, cuda=SimpleNamespace(get_current_stream=lambda: stream))
    monkeypatch.setattr(rc, "gpu_np", backend)
    monkeypatch.setattr(rc, "BACKEND", "cupy")
    monkeypatch.setattr(rc, "gpu_step", device_step)
    monkeypatch.setattr(rc.time, "perf_counter", clock)
    cases, mismatches, cpu_seconds, gpu_seconds = rc.run_corpus(random.Random(0), 2, 5)
    assert cases == steps == 10 and mismatches == []
    assert cpu_seconds == gpu_seconds == 10.0
    tick_events = ["clock", "clock", "sync", "clock", "step", "sync", "clock"] + ["download"] * 5
    assert events == (["upload"] * 5 + tick_events * 5) * 2


def test_mismatch_receipt_includes_full_outputs_and_every_difference(rc, monkeypatch):
    real_step = rc.gpu_step
    real_corpus = rc.run_corpus

    def corrupt_all_fields(*args):
        *outputs, counters = real_step(*args)
        return (*(a ^ np.uint8(1) for a in outputs), counters)

    monkeypatch.setattr(rc, "gpu_step", corrupt_all_fields)
    monkeypatch.setattr(rc, "run_corpus", lambda rng, n, t: real_corpus(rng, 1, t))
    assert rc.main() == 1
    receipt = _receipt(rc)
    assert receipt["status"] == "FAIL_MISMATCH"
    assert receipt["cases_run"] == 2 and receipt["cases_matched"] == 0
    assert [m["corpus"] for m in receipt["mismatches"]] == ["single_tick", "multi_tick"]
    required = _schema()["properties"]["mismatches"]["items"]["required"]
    for mismatch in receipt["mismatches"]:
        assert set(required) <= mismatch.keys()
        assert set(mismatch["cpu_output"]) == set(mismatch["gpu_output"]) == set(rc._FIELDS)
        assert len(mismatch["output_diff"]) == mismatch["H"] * mismatch["W"] * 5
        for diff in mismatch["output_diff"]:
            field, row, col = diff["field"], diff["row"], diff["col"]
            assert diff["cpu"] == mismatch["cpu_output"][field][row][col]
            assert diff["gpu"] == mismatch["gpu_output"][field][row][col]
            assert diff["cpu"] ^ diff["gpu"] == 1


def test_late_divergence_records_intermediate_input_and_stops(rc, monkeypatch):
    trial = rc.make_trial(random.Random(7))
    H, W, seed, tick, wc, mc, rn, ra, mn, grid = trial
    world = rc.Aeth01World(H, W, seed, wc, mc, rn, ra, mn, tick=tick, grid=grid)
    monkeypatch.setattr(rc, "make_trial", lambda rng: trial)
    real_step = rc.gpu_step
    steps = 0

    def diverge(*args):
        nonlocal steps
        *outputs, counters = real_step(*args)
        steps += 1
        if steps == 2:
            outputs[3] = outputs[3] ^ np.uint8(1)
        return (*outputs, counters)

    monkeypatch.setattr(rc, "gpu_step", diverge)
    cases, mismatches, _, _ = rc.run_corpus(random.Random(0), 1, 5)
    assert cases == steps == 2
    assert len(mismatches) == 1
    mismatch = mismatches[0]
    assert mismatch["tick_index"] == 1 and mismatch["tick"] == tick + 1
    assert mismatch["grid"] == world.step().grid
    assert {d["field"] for d in mismatch["output_diff"]} == {"payload"}


def test_bad_output_shape_is_preserved_as_mismatch(rc, monkeypatch):
    real_step = rc.gpu_step

    def wrong_shape(*args):
        *outputs, counters = real_step(*args)
        outputs[4] = outputs[4].ravel()
        return (*outputs, counters)

    monkeypatch.setattr(rc, "gpu_step", wrong_shape)
    cases, mismatches, _, _ = rc.run_corpus(random.Random(0), 1, 5)
    assert cases == 1 and len(mismatches) == 1
    mismatch = mismatches[0]
    assert mismatch["output_diff"] == [{
        "field": "energy", "cpu_shape": [mismatch["H"], mismatch["W"]],
        "gpu_shape": [mismatch["H"] * mismatch["W"]],
    }]


def test_atomic_write_flushes_before_replace_and_keeps_old_file_until_then(rc, monkeypatch, tmp_path):
    old = {"status": "FAIL_INCOMPLETE"}
    new = {"status": "FAIL_ERROR", "error": "injected"}
    rc.write_receipt(old)
    real_replace, real_fsync = rc.os.replace, rc.os.fsync
    events = []

    def fsync(fd):
        real_fsync(fd)
        events.append("fsync")

    def replace(source, target):
        assert events == ["fsync"]
        assert Path(source).parent == Path(target).parent == tmp_path
        assert _receipt(rc) == old
        assert json.loads(Path(source).read_text(encoding="utf-8")) == new
        real_replace(source, target)
        events.append("replace")

    monkeypatch.setattr(rc.os, "fsync", fsync)
    monkeypatch.setattr(rc.os, "replace", replace)
    rc.write_receipt(new)
    assert events == ["fsync", "replace"] and _receipt(rc) == new
    assert list(tmp_path.iterdir()) == [Path(rc.RECEIPT_PATH)]


@pytest.mark.parametrize("operation", ["fsync", "replace"])
def test_failed_atomic_write_preserves_placeholder_and_cleans_temp(rc, monkeypatch, tmp_path, operation):
    old = {"status": "FAIL_INCOMPLETE"}
    rc.write_receipt(old)

    def fail(*args):
        raise OSError("injected persistence failure")

    monkeypatch.setattr(rc.os, operation, fail)
    with pytest.raises(OSError, match="injected persistence failure"):
        rc.write_receipt({"status": "PASS"})
    assert _receipt(rc) == old
    assert list(tmp_path.iterdir()) == [Path(rc.RECEIPT_PATH)]


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), object()])
def test_invalid_json_never_replaces_existing_receipt(rc, tmp_path, invalid):
    old = {"status": "FAIL_INCOMPLETE"}
    rc.write_receipt(old)
    with pytest.raises((ValueError, TypeError)):
        rc.write_receipt({"status": "PASS", "invalid": invalid})
    assert _receipt(rc) == old
    assert list(tmp_path.iterdir()) == [Path(rc.RECEIPT_PATH)]


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "not-a-number"])
def test_nonfinite_cost_context_is_null(rc, monkeypatch, value):
    monkeypatch.setenv("AETH01_CANARY_HOURLY_RATE", value)
    assert rc._cost_context()["hourly_rate_usd"] is None
