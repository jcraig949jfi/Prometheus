"""Q3b judge: verdict from rows only; each clause can fail it."""
from __future__ import annotations

from primordial.nv.telemetry.judge_q3b import OBS_BYTES, judge


def rows(over=None, n=4):
    out = []
    for k in range(n):
        base = {"rep": k, "h2d_bytes": 1000, "d2h_bytes": 80, "lease_lost": False}
        out.append(dict(base, arm="honest", wall_s=0.0005, kernel_share=0.3))
        out.append(dict(base, arm="cheat_sleep", wall_s=0.0515, kernel_share=0.008))
        out.append(dict(base, arm="cheat_extra_copy", wall_s=0.0006, kernel_share=0.26, h2d_bytes=1000 + OBS_BYTES))
    for (k, arm), patch in (over or {}).items():
        next(r for r in out if r["rep"] == k and r["arm"] == arm).update(patch)
    return out


def test_clean_pass():
    j = judge(rows())
    assert j["verdict"] == "PASS" and j["copy_caught"] == j["sleep_caught"] == j["reps"] == 4


def test_missed_copy_fails():
    assert judge(rows({(1, "cheat_extra_copy"): {"h2d_bytes": 1000}}))["verdict"] == "FAIL"


def test_false_stall_fails():
    j = judge(rows({(0, "honest"): {"kernel_share": 0.0, "wall_s": 0.9}}))
    assert j["honest_false_stall"] == 1 and j["verdict"] == "FAIL"


def test_lost_lease_fails():
    assert judge(rows({(2, "honest"): {"lease_lost": True}}))["verdict"] == "FAIL"
