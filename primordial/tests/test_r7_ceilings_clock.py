"""F-R7-2 (D15, gate 27) and F-R7-5: round 7 ceilings in the ONE CEILINGS table and the r7 clock shape.
A non-checkpointable cpu job above 900 s is refused at admission (it cannot pause, so it would hold every lane at
a boundary); a checkpointable one keeps the 2400 s segment wall; cpu_budget_s <= 36000; gpu <= 600 per lease segment;
r7 = PRODUCTION 8 x 3600 s, drain 1800, close 1800 on pm:round:r7."""
from __future__ import annotations

import pytest

from primordial.fabric import envelope as EV
from primordial.ops import epoch as EP
from primordial.ops import round_clock as RC


def clock7(start=0.0):
    return RC.plan(start, "r7")


def env(**kw):
    return EV.example(campaign_stage="PRODUCTION", **kw)


def test_r7_production_row():
    for stage in ("PRODUCTION", "REPLICATION"):
        assert EV.CEILINGS[stage] == {"cpu_wall_s": 2400, "cpu_wall_noncheckpointable_s": 900, "gpu_wall_s": 600,
                                      "cpu_budget_s": 36000}
    for stage in EV.STAGES:                                     # SMOKE/PILOT never looser than PILOT's 900
        assert EV.CEILINGS[stage]["cpu_wall_noncheckpointable_s"] <= 900


@pytest.mark.parametrize("kw,reasons", [
    ({"checkpointable": False, "wall_budget_s": 901}, ["NONCHECKPOINTABLE_WALL_OVER_CEILING"]),
    ({"checkpointable": False, "wall_budget_s": 900}, []),
    ({"checkpointable": True, "wall_budget_s": 2400}, []),
    ({"checkpointable": True, "wall_budget_s": 2401}, ["CPU_WALL_OVER_CEILING"]),
    ({"checkpointable": False, "wall_budget_s": 2401}, ["CPU_WALL_OVER_CEILING"]),
    ({"checkpointable": True, "wall_budget_s": 600, "cpu_budget_s": 36000}, []),
    ({"checkpointable": True, "wall_budget_s": 600, "cpu_budget_s": 36001}, ["CPU_BUDGET_OVER_CEILING"]),
])
def test_r7_cpu_admission(kw, reasons):
    v = EV.admit(env(**kw), clock=clock7(), now=0.0)
    assert v["reasons"] == reasons and v["ok"] == (not reasons)
    assert v["stub"] == bool(reasons)                           # budget refusals keep their PRODUCTION_CANDIDATE stub


def test_evidence_class_values_are_validated_here():
    """A 1789504263405-0: an unknown evidence_class is a malformed envelope (validate), not a sample defect."""
    assert EV.admit(env(checkpointable=True, evidence_class="OBSERVATION"), clock=clock7(), now=0.0)["ok"]
    assert EV.admit(env(checkpointable=True, evidence_class="VERDICT"), clock=clock7(), now=0.0)["ok"]
    v = EV.admit(env(checkpointable=True, evidence_class="MAYBE"), clock=clock7(), now=0.0)
    assert v["reasons"] == ["ENVELOPE_BAD_VALUE:evidence_class"]
    assert EV.admit(env(checkpointable=True), clock=clock7(), now=0.0)["ok"]          # absent stays admissible here


def test_r7_declared_lane_repos():
    lr = RC.ROUNDS["r7"]["lane_repos"]
    assert set(lr) == {"B", "C", "D", "E", "R", "G", "gpu"} and lr["G"] == ["F:/Prometheus-worktrees/nestor-bld-g"]
    assert lr["D"] == ["F:/Prometheus-worktrees/nestor-r7-d"] and "F:/Prometheus-worktrees/nestor-r6-e" in lr["gpu"]
    assert "lane_repos" not in RC.plan(0.0, "r7")                                    # a declaration, not clock state


def test_r7_gpu_per_lease_segment():
    assert EV.admit(env(gpu_budget_s=600), kind="gpu", clock=clock7(), now=0.0)["ok"]
    assert EV.admit(env(gpu_budget_s=601), kind="gpu", clock=clock7(), now=0.0)["reasons"] == ["GPU_WALL_OVER_CEILING"]


def test_no_new_work_refusal_makes_no_stub():
    c = clock7()
    v = EV.admit(env(wall_budget_s=60), clock=c, now=c["no_new_work_ts"])
    assert v["event"] == EV.NO_NEW_WORK_REFUSAL and v["stub"] is False


def test_r7_clock_shape():
    """The `epoch round` CLI default (r7) is asserted in test_r7_f1_residue.py with the epoch.py change."""
    c = clock7()
    assert RC.DEFAULT_ROUND == "r7" and c["stage"] == "PRODUCTION" and RC.plan(0.0) == c
    assert (c["epoch_s"], c["epochs"], c["no_new_work_ts"], c["drain_ts"], c["end_ts"]) == (3600.0, 8, 28800, 30600, 32400)
    assert [RC.phase(c, t)["epoch"] for t in (0, 3599, 3600, 28799)] == [1, 1, 2, 8]
    a = EP.parser().parse_args(["round", "--lanes", "B,C,D,E,G", "--round", "r7", "--repo", "X"])
    assert RC.plan(0.0, a.round, **EP.round_shape(a)) == c
