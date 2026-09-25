"""Q1: the capture-smoke classifier reads exit codes and tool text only (strings captured on SKULLPORT)."""
from __future__ import annotations

from primordial.nv.telemetry.smoke import VERDICTS, classify, judge_capture, probes, report_ok


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


def test_ncu_2026_2_driver_too_old():
    err = ("==ERROR== Cuda driver is not compatible with Nsight Compute.\n"
           "==ERROR== The application returned an error code (3221225477).\n")
    assert classify("ncu_torch", 3221225477, "", err) == "driver_incompatible"


def test_ncu_2025_2_counter_permission():
    err = ("==ERROR== ERR_NVGPUCTRPERM - The user does not have permission to access NVIDIA GPU Performance "
           "Counters on the target device 0.\n")
    assert classify("ncu_torch", 1, "cc (12, 0) 1.0", err) == "perm_gpu_counters"


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


def test_report_ok_accepts_2025_ncu_rep_extension():
    assert report_ok(["ncu_torch.ncu-rep"]) and report_ok(["ncu_torch.ncu"])
    assert not report_ok([]) and not report_ok(["ncu_torch.qdstrm"])


def _row(probe, rc, out="", err="", files=()):
    return {"probe": probe, "rc": rc, "stdout": out, "stderr": err, "report_files": list(files)}


def test_judge_capture_q2d_strings():
    out = ("==PROF== Connected to process 13320\n==PROF== Profiling \"Kernel2\" - 1: 0%....50%....100% - 9 passes\n"
           "cc (12, 0) 4368.2\n==PROF== Report: ncu_torch.ncu-rep\n")
    ctl = _row("control_torch", 0, "cc (12, 0) 1.0")
    assert judge_capture([ctl, _row("ncu_torch", 0, out, "", ["ncu_torch.ncu-rep"])]) == "PASS"
    assert judge_capture([ctl, _row("ncu_torch", 0, out, "", [])]) == "REFUSAL:ok"
    perm = "==ERROR== ERR_NVGPUCTRPERM - The user does not have permission"
    assert judge_capture([ctl, _row("ncu_torch", 1, "", perm)]) == "REFUSAL:perm_gpu_counters"
    assert judge_capture([_row("control_torch", 2, "", "boom"), _row("ncu_torch", 0, out, "", ["a.ncu-rep"])]) == "INVALID"
