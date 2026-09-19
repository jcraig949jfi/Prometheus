"""Degrees of freedom the playtests found missing (overnight C12-C14): population as a sweep axis; an
objective that reads the series; a held-out split that the receipts carry mechanically."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox.ir import Experiment, IRError, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, constant_player

REG = default_registry()


def _exp(**kw):
    base = dict(family="dof", world=ref("world.integer.v1", world_seed=3, start_charge=100000, step_cost=0), substrate=ref("substrate.flat.v1"),
                players=[random_statemachine(1).manifest()], seed_policy={"base": 1, "n_seeds": 1}, budget={"episodes": 2, "horizon": 10},
                observers=[ref("observer.series.v1")])
    base.update(kw); return Experiment(**base)


# C12: "players" as a sweep root (found in C3/C11: population variation had to be a separate experiment)
def test_population_is_a_sweep_axis_and_controls_pair_per_population(tmp_path):
    A = [random_statemachine(1).manifest()]; B = [random_statemachine(2).manifest()]; C = [constant_player([1, 1]).manifest()]
    e = _exp(sweep={"players": [A, B, C]}, controls=[ref("control.replay.v1")])
    assert e.validate() == [] and len(e.sweep_points()) == 3
    low = lower(e, REG); assert low.ok and len(low.job.runs) == 6
    rep = execute(low.job, tmp_path / "p.jsonl", REG); assert rep.n_failed == 0 and rep.controls["replay"]["pairs"] == 3
    hashes = {r["components"]["players"][0]["manifest_hash"] for r in read_all(tmp_path / "p.jsonl") if r["arm"] == "primary"}
    assert len(hashes) == 3


def test_single_player_slot_and_payload_fields_are_sweepable():
    e = _exp(players=[random_statemachine(1).manifest(), random_statemachine(2).manifest()], world=ref("world.integer.v1", world_seed=3, n_players=2),
             sweep={"players.1": [random_statemachine(5).manifest(), random_statemachine(6).manifest()], "players.0.initial_state.state": [0, 1]})
    pts = e.sweep_points(); assert len(pts) == 4
    at = e.at_point(pts[3]); assert at.players[0]["initial_state"]["state"] == 1 and at.players[1]["meta"]["seed"] == 6


# C13: an objective that reads the SERIES (experience-to-competence shape): gain = yield in the last episode
# minus yield in the first; None (never a fabricated 0) when the series is absent or disabled.
def test_series_gain_objective_reads_the_series_and_refuses_to_fabricate(tmp_path):
    e = _exp(objective=ref("objective.series_gain.v1"), budget={"episodes": 3, "horizon": 10})
    execute(lower(e, REG).job, tmp_path / "g.jsonl", REG)
    r = [x for x in read_all(tmp_path / "g.jsonl") if x["arm"] == "primary"][0]
    obj = r["science"]["objective"]
    eps = r["series"]["observer.series.v1"]["inline"]
    assert obj["value"] == eps[-1][-1][2] - eps[0][-1][2] and obj["components"]["episodes"] == 3
    e2 = _exp(objective=ref("objective.series_gain.v1"), observers=[ref("observer.series.v1", enabled=False)])
    execute(lower(e2, REG).job, tmp_path / "g2.jsonl", REG)
    obj2 = [x for x in read_all(tmp_path / "g2.jsonl") if x["arm"] == "primary"][0]["science"]["objective"]
    assert obj2["value"] is None and obj2["components"]["reason"] == "SERIES_DISABLED"
    e3 = _exp(objective=ref("objective.series_gain.v1"), observers=[])
    execute(lower(e3, REG).job, tmp_path / "g3.jsonl", REG)
    obj3 = [x for x in read_all(tmp_path / "g3.jsonl") if x["arm"] == "primary"][0]["science"]["objective"]
    assert obj3["value"] is None and obj3["components"]["reason"] == "SERIES_MISSING"


# C14: held-out split carried by receipts, not by prose: seed_policy.holdout_seeds adds seeds tagged "holdout";
# the summary aggregates objectives per split; controls pair within a split.
def test_holdout_seeds_are_tagged_and_summarised_per_split(tmp_path):
    e = _exp(seed_policy={"base": 10, "n_seeds": 2, "holdout_seeds": 3}, objective=ref("objective.survival.v1"), controls=[ref("control.replay.v1")])
    low = lower(e, REG); assert low.ok and len(low.job.runs) == 10
    rep = execute(low.job, tmp_path / "h.jsonl", REG); assert rep.n_failed == 0
    rs = read_all(tmp_path / "h.jsonl"); prim = [r for r in rs if r["arm"] == "primary"]
    assert sorted(r["split"] for r in prim) == ["holdout"] * 3 + ["train"] * 2
    assert {r["seed"] for r in prim if r["split"] == "holdout"} == {12, 13, 14}
    summ = rs[-1]["science"]["splits"]
    assert summ["train"]["n"] == 2 and summ["holdout"]["n"] == 3 and "objective_mean" in summ["holdout"]
    assert rep.controls["replay"]["pairs"] == 5


def test_series_gain_objective_works_when_the_series_is_artifact_backed(tmp_path):
    """False-green guard: an objective that only read the inline series would return SERIES_EMPTY for a large run."""
    e = _exp(objective=ref("objective.series_gain.v1"), budget={"episodes": 3, "horizon": 300})
    execute(lower(e, REG).job, tmp_path / "big.jsonl", REG)
    r = [x for x in read_all(tmp_path / "big.jsonl") if x["arm"] == "primary"][0]
    assert "artifact" in r["series"]["observer.series.v1"] and r["science"]["objective"]["value"] is not None
    assert r["science"]["objective"]["components"]["episodes"] == 3 and "_series_episodes" not in r


# C19: "worlds are stationary" is not assumed (directive s8): an Intervention may carry a SCHEDULE of parameter
# changes applied at tick boundaries by the kernel; the world declares ext.world.mutable_params.v1 and emits
# TASK_CHANGE. Same designer text, no world rewrite.
def test_schedule_intervention_changes_conditions_mid_episode_and_is_recorded(tmp_path):
    sched = {"name": "task_switch", "world_params": {}, "wrappers": {}, "schedule": [{"tick": 4, "world_params": {"act_cost": 5}}, {"tick": 7, "world_params": {"yield_amt": 0}}]}
    e = _exp(interventions=[sched], observers=[ref("observer.trace.v1")], controls=[ref("control.replay.v1")], budget={"episodes": 1, "horizon": 12})
    assert "ext.intervention.schedule.v1" in e.derived_requirements()
    low = lower(e, REG); assert low.ok, low.reasons
    rep = execute(low.job, tmp_path / "s.jsonl", REG); assert rep.n_failed == 0 and rep.controls["replay"]["outcome"] == "MET"
    r = [x for x in read_all(tmp_path / "s.jsonl") if x["arm"] == "primary"][0]
    assert r["science"]["observations"]["observer.trace.v1"]["events_by_kind"].get("TASK_CHANGE") == 2
    assert r["components"]["world"]["manifest"]["schedule"] == sched["schedule"]
    e0 = _exp(observers=[ref("observer.trace.v1")], budget={"episodes": 1, "horizon": 12})
    execute(lower(e0, REG).job, tmp_path / "s0.jsonl", REG)
    r0 = [x for x in read_all(tmp_path / "s0.jsonl") if x["arm"] == "primary"][0]
    assert r0["trace_hashes"] != r["trace_hashes"]


def test_schedule_on_a_world_without_mutable_params_is_blocked_locally():
    e = _exp(world=ref("world.wforge.encounter.v0", genome_seed=1), interventions=[{"name": "s", "schedule": [{"tick": 1, "world_params": {"act_cost": 2}}]}])
    if REG.get("world.wforge.encounter.v0").state == "UNAVAILABLE":
        pytest.skip("wforge not importable")
    low = lower(e, REG)
    assert low.status == "BLOCKED_MISSING_CAPABILITY" and "ext.world.mutable_params.v1" in low.negotiation["missing"]


def test_schedule_refuses_non_mutable_params_as_a_failed_run_not_a_halt(tmp_path):
    e = _exp(interventions=[{"name": "s", "schedule": [{"tick": 1, "world_params": {"n_regs": 99}}]}], budget={"episodes": 1, "horizon": 4})
    rep = execute(lower(e, REG).job, tmp_path / "bad.jsonl", REG)
    assert rep.n_failed == 1 and "not runtime-mutable" in read_all(tmp_path / "bad.jsonl")[0]["error"]


# C23 (playtest C rows): TASK_CHANGE counts exceeded the schedule because the StateDevice reused the TASK_CHANGE
# kind for key expiry and scope discards -- two meanings under one event id. Expiry/discard get their own kinds.
def test_task_change_counts_only_schedule_changes_and_expiry_has_its_own_kind(tmp_path):
    sched = {"name": "s", "schedule": [{"tick": 2, "world_params": {"act_cost": 3}}, {"tick": 4, "world_params": {"yield_amt": 1, "step_cost": 0}}]}
    e = _exp(interventions=[sched], substrate=ref("substrate.kv.v1", scope="lifetime", ttl=1), players=[random_statemachine_v2(3).manifest()],
             observers=[ref("observer.trace.v1")], budget={"episodes": 2, "horizon": 6})
    execute(lower(e, REG).job, tmp_path / "tc.jsonl", REG)
    r = [x for x in read_all(tmp_path / "tc.jsonl") if x["arm"] == "primary"][0]
    ev = r["science"]["observations"]["observer.trace.v1"]["events_by_kind"]
    assert ev.get("TASK_CHANGE") == 2 * 3                     # 3 parameter changes per episode x 2 episodes
    assert ev.get("STATE_EXPIRE", 0) == r["accounting"]["ws_expired"] > 0
    assert ev.get("STATE_DISCARD", 0) >= 1                    # the episode-scope end at the second episode


# C40 (directive s30: persistent objects / long-lived world state; c6's "coupling"): the World contract resets per
# episode, so a world could never carry state across episodes. A world that declares ext.world.lifetime_state.v1
# accepts reset(seed, keep=True); the experiment asks for it with budget.world_state="lifetime". Episode 2 then
# begins where episode 1 ended (registers, pending actions), while charge and survival still reset.
def test_world_lifetime_state_carries_registers_across_episodes(tmp_path):
    e = _exp(budget={"episodes": 3, "horizon": 8, "world_state": "lifetime"}, observers=[ref("observer.trace.v1")],
             world=ref("world.integer.v1", world_seed=3, start_charge=100000, step_cost=0, action_delay=3))
    assert "ext.world.lifetime_state.v1" in e.derived_requirements()
    low = lower(e, REG); assert low.ok, low.reasons
    execute(low.job, tmp_path / "lt.jsonl", REG)
    r = [x for x in read_all(tmp_path / "lt.jsonl") if x["arm"] == "primary"][0]
    e0 = _exp(budget={"episodes": 3, "horizon": 8}, observers=[ref("observer.trace.v1")], world=ref("world.integer.v1", world_seed=3, start_charge=100000, step_cost=0, action_delay=3))
    execute(lower(e0, REG).job, tmp_path / "ep.jsonl", REG)
    r0 = [x for x in read_all(tmp_path / "ep.jsonl") if x["arm"] == "primary"][0]
    assert r["trace_hashes"][0] == r0["trace_hashes"][0], "episode 0 must be identical with or without persistence"
    assert r["trace_hashes"][1] != r0["trace_hashes"][1], "episode 1 must differ: the world remembered"
    assert r["components"]["world"]["manifest"]["world_state"] == "lifetime"


def test_world_lifetime_state_on_a_world_without_it_is_blocked():
    e = _exp(world=ref("world.wforge.encounter.v0", genome_seed=1), budget={"episodes": 2, "horizon": 8, "world_state": "lifetime"})
    if REG.get("world.wforge.encounter.v0").state == "UNAVAILABLE":
        pytest.skip("wforge not importable")
    low = lower(e, REG)
    assert low.status == "BLOCKED_MISSING_CAPABILITY" and "ext.world.lifetime_state.v1" in low.negotiation["missing"]


# C45 (ergonomics): a designer hands the IR PlayerSpec and Intervention OBJECTS (the natural thing to write); the
# IR is data, so it converts them at construction instead of failing later with "not a PlayerSpec manifest".
def test_ir_accepts_component_objects_and_stores_their_manifests():
    from prometheus.toolbox.contracts import Intervention
    e = Experiment(family="ergo", world=ref("world.integer.v1"), substrate=ref("substrate.flat.v1"),
                   players=[random_statemachine(1), constant_player([1, 2]).manifest()],
                   interventions=[Intervention("lag", wrappers={"observation_delay": 2}), {"name": "raw", "world_params": {"act_cost": 2}}])
    assert e.validate() == []
    assert e.players[0]["representation"] == "statemachine.v1" and isinstance(e.players[0], dict)
    assert e.interventions[0] == {"name": "lag", "world_params": {}, "wrappers": {"observation_delay": 2}}
    assert json.dumps(e.to_dict())


# C58: TRANSFER (NPE Clause B shape: candidate evolved in world A judged in world B against scratch AND sham arms)
# needs NO new abstraction: it is a sweep over `world` with sham + scratch controls. Verified rather than built.
def test_transfer_is_a_world_sweep_with_sham_and_scratch_arms(tmp_path):
    A = ref("world.integer.v1", world_seed=1, start_charge=60); B = ref("world.integer.v1", world_seed=2, start_charge=60, regime_period=4)
    e = _exp(world=A, players=[random_statemachine(7).manifest()], sweep={"world": [A, B]}, controls=[ref("control.sham.v1"), ref("control.scratch.v1")],
             objective=ref("objective.survival.v1"), seed_policy={"base": 1, "n_seeds": 2})
    low = lower(e, REG); assert low.ok and len(low.job.runs) == 12
    rep = execute(low.job, tmp_path / "tr.jsonl", REG); assert rep.n_failed == 0
    rs = read_all(tmp_path / "tr.jsonl")
    by = {}
    for r in rs:
        if r["arm"] != "SUMMARY":
            by.setdefault(r["sweep_point"]["world"]["params"]["world_seed"], {}).setdefault(r["arm"], []).append(r["science"]["objective"]["value"])
    assert set(by) == {1, 2} and all(set(v) == {"primary", "sham", "scratch"} for v in by.values())
    assert rep.controls["sham"]["pairs"] == 4 and rep.controls["scratch"]["pairs"] == 4


# C59: ablation as a control OBJECT: control.ablation.v1 removes every player's workspace (forces the flat
# substrate, keeping per-player overrides visible as ablated); expectation = the arm ran with zero workspace
# traffic while the primary had some (otherwise INDETERMINATE: nothing to ablate).
def test_ablation_control_removes_workspaces_and_reports(tmp_path):
    e = _exp(substrate=ref("substrate.kv.v1", scope="lifetime"), players=[random_statemachine_v2(1).manifest()], controls=[ref("control.ablation.v1")],
             world=ref("world.integer.v1", world_seed=3, start_charge=100000, step_cost=0))
    rep = execute(lower(e, REG).job, tmp_path / "ab.jsonl", REG)
    assert rep.controls["ablation"]["outcome"] == "MET" and rep.controls["ablation"]["details"][0]["detail"]["arm_ws_ops"] == 0
    arm = [r for r in read_all(tmp_path / "ab.jsonl") if r["arm"] == "ablation"][0]
    assert arm["components"]["substrate"]["kind"] == "substrate.flat.v1" and arm["provenance"]["ablated"] == "workspace"
    e2 = _exp(substrate=ref("substrate.flat.v1"), players=[random_statemachine(1).manifest()], controls=[ref("control.ablation.v1")])
    rep2 = execute(lower(e2, REG).job, tmp_path / "ab2.jsonl", REG)
    assert rep2.controls["ablation"]["outcome"] == "INDETERMINATE"


# C66 (mutation wave 4 survivor M37): the ablation control's tests used the EXPERIMENT substrate only; an
# ablation that left PER-PLAYER overrides in place survived. Ablation must strip every override too.
def test_ablation_strips_per_player_substrate_overrides(tmp_path):
    p_mem = dict(random_statemachine_v2(11).manifest(), substrate=ref("substrate.kv.v1", scope="lifetime"))
    e = _exp(substrate=ref("substrate.flat.v1"), players=[p_mem], controls=[ref("control.ablation.v1")],
             world=ref("world.integer.v1", world_seed=3, start_charge=100000, step_cost=0))
    rep = execute(lower(e, REG).job, tmp_path / "abo.jsonl", REG)
    assert rep.controls["ablation"]["outcome"] == "MET"
    arm = [r for r in read_all(tmp_path / "abo.jsonl") if r["arm"] == "ablation"][0]
    assert arm["components"]["player_substrates"] == ["substrate.flat.v1"] and arm["accounting"].get("ws_writes", 0) == 0 and arm["accounting"].get("ws_refused", 0) > 0


# C76: ONE designer text over EVERY registered world (worlds vary independently of players -- the whole point).
# The same players, substrate, observers, objective and controls; only the world ref changes. Each world must
# lower, run, replay MET, and the cheat control must be MET (every world has a cheat mechanism now).
import pytest as _pt


@_pt.mark.parametrize("kind", ["world.integer.v1", "world.integer_alt.v1", "world.grid.v1", "world.pendulum.v1", "world.c6.composed.v1", "world.wforge.encounter.v0"])
def test_one_experiment_text_runs_on_every_registered_world(tmp_path, kind):
    if not REG.has(kind) or REG.get(kind).state == "UNAVAILABLE":
        _pt.skip("%s not on this tree" % kind)
    probe = REG.make(kind); n = probe.n_players
    e = Experiment(family="every_world", world=ref(kind), substrate=ref("substrate.kv.v1", scope="lifetime"),
                   players=[random_statemachine_v2(100 + i, width=3).manifest() for i in range(n)],
                   observers=[ref("observer.trace.v1"), ref("observer.series.v1", per_player=True)], objective=ref("objective.series_gain.v1"),
                   controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.sham.v1")],
                   seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 2, "horizon": 16})
    low = lower(e, REG); assert low.ok, (kind, low.reasons)
    rep = execute(low.job, tmp_path / (kind + ".jsonl"), REG)
    assert rep.n_failed == 0 and rep.controls["replay"]["outcome"] == "MET" and rep.controls["cheat"]["outcome"] == "MET" and rep.controls["sham"]["outcome"] == "MET", (kind, rep.controls)
    r = [x for x in read_all(tmp_path / (kind + ".jsonl")) if x["arm"] == "primary"][0]
    assert r["series"]["observer.series.v1"]["status"] in ("PRESENT", "EMPTY") and r["replay_class"] in ("BIT", "SEMANTIC")
