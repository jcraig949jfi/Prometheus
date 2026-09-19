"""Playtest C (overnight C20): changing tasks, held-out qualification, memory across episodes, series objective.

Two memory-bearing players (statemachine.v2 on a lifetime-scoped kv workspace with a 6-tick ttl) in a world
whose economics CHANGE mid-episode on a schedule (action cost x5 at tick 10, yield removed at tick 20,
restored at tick 30), swept over two populations and two schedules, 2 train seeds + 2 held-out seeds,
objective = series gain (last episode yield - first), controls replay / cheat / sham / negative.
Asks: can a task sequence be stated without a world rewrite; do TASK_CHANGE events reach the record; does the
holdout split aggregate mechanically; does memory ttl interact with the schedule visibly in the rows.
"""
from __future__ import annotations

import json
import sys

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine_v2

POP_A = [random_statemachine_v2(301, n_states=6, n_buckets=12).manifest(), random_statemachine_v2(302, n_states=6, n_buckets=12).manifest()]
POP_B = [random_statemachine_v2(303, n_states=6, n_buckets=12).manifest(), random_statemachine_v2(304, n_states=6, n_buckets=12).manifest()]
SCHED_1 = [{"tick": 10, "world_params": {"act_cost": 5}}, {"tick": 20, "world_params": {"yield_amt": 0}}, {"tick": 30, "world_params": {"yield_amt": 12, "act_cost": 1}}]
SCHED_2 = [{"tick": 5, "world_params": {"regime_period": 3}}, {"tick": 25, "world_params": {"regime_period": 0, "stoch_rate": 4}}]


def build() -> Experiment:
    return Experiment(
        family="pt_c_changing_tasks",
        world=ref("world.integer.v1", n_regs=7, n_players=2, act_width=2, world_seed=77, start_charge=70, yield_amt=12),
        substrate=ref("substrate.kv.v1", scope="lifetime", ttl=6),
        players=POP_A,
        interventions=[{"name": "tasks", "world_params": {}, "wrappers": {}, "schedule": SCHED_1}],
        objective=ref("objective.series_gain.v1"),
        observers=[ref("observer.trace.v1"), ref("observer.series.v1")],
        controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.sham.v1"), ref("control.negative.v1")],
        sweep={"players": [POP_A, POP_B], "interventions.0.schedule": [SCHED_1, SCHED_2]},
        seed_policy={"base": 4000, "n_seeds": 2, "holdout_seeds": 2},
        budget={"episodes": 3, "horizon": 40},
        provenance={"designer": "Bellerophon", "lane": "KERNEL_PLAYTEST", "note": "playtest C: changing tasks + holdout + memory ttl"},
    )


def main(out: str = "prometheus/toolbox/playtests/receipts/pt_c.jsonl") -> dict:
    exp = build(); assert not exp.validate(), exp.validate()
    low = exp.compile("local")
    if not low.ok:
        print(json.dumps(low.as_dict(), indent=1)); return low.as_dict()
    from prometheus.toolbox.backends.local import execute
    rep = execute(low.job, out)
    print(json.dumps({"runs": rep.n_runs, "failed": rep.n_failed, "valid": rep.valid, "controls": {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep.controls.items()}}))
    return rep.as_dict()


if __name__ == "__main__":
    main(*sys.argv[1:])
