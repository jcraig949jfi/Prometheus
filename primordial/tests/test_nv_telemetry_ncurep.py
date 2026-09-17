"""Q2e: the counter-fill judge is code over a report dump (vendor pyd not needed)."""
from __future__ import annotations

from primordial.nv.telemetry.ncurep import counter_filled, judge
from primordial.nv.telemetry.smoke import probes


def _k(metrics):
    return {"range": 0, "kernel": "cutlass::Kernel2<sgemm>", "metrics": metrics}


def test_q2d_basic_set_shape_is_bound():
    ks = [_k({"launch__block_size": [1, [128.0]], "gpu__time_duration.sum": [0, []],
              "sm__cycles_elapsed.avg": [0, []], "breakdown:sm__throughput.avg.pct_of_peak_sustained_elapsed": [0, []]})]
    assert counter_filled(ks) == [] and judge(ks) == "BOUND"


def test_filled_counter_passes_and_zero_does_not():
    assert judge([_k({"gpu__time_duration.sum": [3, [0.0, 12.5, 0.0]]})]) == "PASS"
    assert counter_filled([_k({"gpu__time_duration.sum": [3, [0.0, 12.5]]})])[0][2] == 12.5
    assert judge([_k({"sm__cycles_elapsed.avg": [2, [0.0, None]]})]) == "BOUND"
    assert judge([_k({"launch__grid_size": [1, [216.0]]})]) == "BOUND"
    assert judge([]) == "NO_KERNELS"


def test_ncu_set_passthrough(tmp_path):
    assert "--set" not in probes("python", tmp_path)["ncu_torch"]
    cmd = probes("python", tmp_path, ncu_set="detailed")["ncu_torch"]
    assert cmd[1:3] == ["--set", "detailed"]
