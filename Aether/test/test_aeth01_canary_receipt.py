"""
AETH-01 RunPod canary package -- executable tests for run_canary.py's
pass/fail semantics (closure-patch item 2). These exercise the on-pod
entry point ITSELF (imported directly, not re-implemented), against the
NumPy-fallback backend actually available in this workspace -- there is
no CuPy/GPU here, so these tests validate the closed status vocabulary,
fail-closed behavior, and receipt shape, not real-hardware execution
(that remains RunPod's job, README.md).
"""

import json
import os
import subprocess
import sys

import pytest

_CANARY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "runpod", "aeth01_canary",
)
sys.path.insert(0, _CANARY_DIR)

import run_canary as rc  # noqa: E402 -- must follow sys.path setup above.


@pytest.fixture(autouse=True)
def _clean_receipt():
    receipt_path = os.path.join(_CANARY_DIR, rc.RECEIPT_PATH)
    if os.path.exists(receipt_path):
        os.remove(receipt_path)
    yield
    if os.path.exists(receipt_path):
        os.remove(receipt_path)


def _run_canary_subprocess(env_overrides):
    """Runs run_canary.py as a real subprocess (not an in-process import
    call) so its `sys.exit(main())` / process exit code is genuinely
    exercised, matching how `watchdog.sh` observes it."""
    env = dict(os.environ)
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "run_canary.py"],
        cwd=_CANARY_DIR, env=env, capture_output=True, text=True, timeout=60,
    )


def test_backend_is_numpy_fallback_in_this_workspace():
    # Sanity check the premise of every test below: no CuPy/GPU here.
    assert rc.BACKEND == "numpy_fallback"


def test_require_gpu_default_fails_closed_on_numpy_fallback():
    result = _run_canary_subprocess({})  # AETH01_CANARY_REQUIRE_GPU unset -> defaults to required.
    assert result.returncode != 0
    receipt = json.load(open(os.path.join(_CANARY_DIR, rc.RECEIPT_PATH)))
    assert receipt["status"] == rc.STATUS_FAIL_ENVIRONMENT
    assert receipt["backend"] == "numpy_fallback"
    # FAIL_ENVIRONMENT means the corpus never ran -- 0 cases, not a
    # vacuous "0 matched of 0 run" pass.
    assert receipt["cases_run"] == 0


def test_require_gpu_explicit_zero_allows_local_smoke_test_to_pass():
    result = _run_canary_subprocess({"AETH01_CANARY_REQUIRE_GPU": "0"})
    assert result.returncode == 0
    receipt = json.load(open(os.path.join(_CANARY_DIR, rc.RECEIPT_PATH)))
    assert receipt["status"] == rc.STATUS_PASS
    assert receipt["cases_run"] == receipt["cases_matched"]
    assert receipt["cases_run"] > 0
    assert receipt["mismatches"] == []


def test_exit_code_matches_status_pass_iff_zero():
    result = _run_canary_subprocess({"AETH01_CANARY_REQUIRE_GPU": "0"})
    receipt = json.load(open(os.path.join(_CANARY_DIR, rc.RECEIPT_PATH)))
    assert (result.returncode == 0) == (receipt["status"] == rc.STATUS_PASS)


def test_receipt_has_all_schema_required_fields():
    _run_canary_subprocess({"AETH01_CANARY_REQUIRE_GPU": "0"})
    receipt = json.load(open(os.path.join(_CANARY_DIR, rc.RECEIPT_PATH)))
    schema = json.load(open(os.path.join(_CANARY_DIR, "receipt_schema.json")))
    missing = [k for k in schema["required"] if k not in receipt]
    assert missing == []
    extra = [k for k in receipt if k not in schema["properties"]]
    assert extra == []


def test_status_vocabulary_is_closed_and_matches_schema_enum():
    schema = json.load(open(os.path.join(_CANARY_DIR, "receipt_schema.json")))
    assert set(rc.FINAL_STATUSES) == set(schema["properties"]["status"]["enum"])


def test_write_receipt_rejects_unknown_status():
    with pytest.raises(AssertionError):
        rc.write_receipt({"status": "NOT_A_REAL_STATUS"})


def test_source_hashes_present_for_bundled_files():
    hashes = rc._source_hashes()
    for name in ("aeth01_cpu_oracle.py", "aeth01_gpu_kernel.py", "run_canary.py"):
        assert name in hashes
        assert hashes[name] is not None and len(hashes[name]) == 64  # sha256 hex digest length.


def test_mismatch_forced_reports_fail_mismatch_and_nonzero_exit(monkeypatch):
    # Force a mismatch deterministically by corrupting the GPU path's
    # output, so FAIL_MISMATCH (as opposed to FAIL_ERROR) is actually
    # reachable without needing a real hardware disagreement.
    import numpy as np

    real_gpu_step = rc.gpu_step

    def _broken_gpu_step(*args, **kwargs):
        no_, na0, na1, npl, ne, counters = real_gpu_step(*args, **kwargs)
        return (no_, na0, na1, npl.copy() ^ np.uint8(1), ne, counters)

    monkeypatch.setattr(rc, "gpu_step", _broken_gpu_step)
    # REQUIRE_GPU is resolved once at module-import time from the env
    # var; patch the resolved module attribute directly rather than the
    # env var (which would have no effect on an already-imported module).
    monkeypatch.setattr(rc, "REQUIRE_GPU", False)
    receipt_path = os.path.join(_CANARY_DIR, rc.RECEIPT_PATH)
    cwd = os.getcwd()
    os.chdir(_CANARY_DIR)
    try:
        exit_code = rc.main()
    finally:
        os.chdir(cwd)
    assert exit_code != 0
    receipt = json.load(open(receipt_path))
    assert receipt["status"] == rc.STATUS_FAIL_MISMATCH
    assert len(receipt["mismatches"]) > 0
