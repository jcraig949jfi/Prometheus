"""Q4: refusal re-filing and the B6 judge work from rows only."""
from __future__ import annotations

from primordial.nv.telemetry.q4_b6 import judge_b6, refusal_rows


def test_refusals_are_aborted_and_reclassified():
    rows = {"Q2.jsonl": [
        {"probe": "control_torch", "rc": 0, "stdout": "cc", "stderr": "", "verdict": "ok"},
        {"probe": "ncu_torch", "rc": 1, "stdout": "", "verdict": "failed", "host": {"ncu": "Version 2025.2.1.0"},
         "stderr": "==PROF== Connected\n==ERROR== ERR_NVGPUCTRPERM - The user does not have permission\n"},
    ]}
    out = refusal_rows(rows)
    assert len(out) == 1
    r = out[0]
    assert r["status"] == "aborted" and r["tool"] == "ncu" and r["verdict"] == "perm_gpu_counters"
    assert r["verdict_recorded"] == "failed" and r["stderr_first"].startswith("==ERROR== ERR_NVGPUCTRPERM")


def _b6(**h):
    base = dict(h2d_bytes=0, d2h_bytes=0, n_cuda_ops=0, peak_mem_bytes=0, exact_fitness=True, exact_cells=True)
    return [dict(base, arm="honest", wall_s=0.01, **h), dict(base, arm="cheat_sleep", wall_s=0.061)]


def test_b6_judge():
    assert judge_b6(_b6()) == "PASS"
    assert judge_b6(_b6(h2d_bytes=8)) == "FAIL"
    assert judge_b6(_b6(exact_cells=False)) == "FAIL"
