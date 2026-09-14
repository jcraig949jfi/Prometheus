"""Q1: the capture-smoke classifier reads exit codes and tool text only (strings captured on SKULLPORT)."""
from __future__ import annotations

from primordial.nv.telemetry.smoke import VERDICTS, classify, probes


def test_nsys_non_admin_refusal():
    err = "ReflexStatsTraceLoggingProvider provider requires administrator privileges\n"
    assert classify("nsys_trivial", 1, "", err) == "refused_admin"


def test_admin_warning_on_success_is_not_a_refusal():
    err = "WARNING: CPU sampling requires administrative privileges, disabling.\n"
    assert classify("nsys_cuda_torch", 0, "", err) == "ok"


def test_ncu_2024_3_on_blackwell():
    err = ("==WARNING== An error was reported by the driver:\n==WARNING== Failed to load Nsight Compute CUDA "
           "modules.\n==ERROR== The application returned an error code (3221225477).\n")
    assert classify("ncu_torch", 139, "", err) == "cuda_modules_failed"


def test_crash_without_ncu_text():
    assert classify("ncu_torch", 3221225477, "", "") == "target_crashed"


def test_cupti_invalid_device_and_empty_events():
    err = "function cbapi->getCuptiStatus() failed with error CUPTI_ERROR_INVALID_DEVICE (2)"
    assert classify("cupti_torch", 0, "cuda_events 0\n", err) == "cupti_invalid_device"
    assert classify("cupti_torch", 0, "cuda_events 0\n", "") == "failed"
    assert classify("cupti_torch", 0, "cuda_events 12\n", "") == "ok"


def test_timeout_missing_and_plain():
    assert classify("control_torch", None, "", "") == "timeout"
    assert classify("ncu_torch", 127, "", "tool_missing: x") == "tool_missing"
    assert classify("control_torch", 0, "cc (12, 0) 1.0", "") == "ok"
    assert classify("control_torch", 2, "", "boom") == "failed"


def test_probe_set_and_verdict_vocabulary(tmp_path):
    p = probes("python", tmp_path)
    assert set(p) == {"control_torch", "nsys_trivial", "nsys_cuda_torch", "ncu_torch", "cupti_torch"}
    for name, cmd in p.items():
        assert classify(name, 0, "cuda_events 1", "") in VERDICTS
