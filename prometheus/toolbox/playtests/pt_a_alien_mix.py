"""Playtest A (overnight C3): an experiment deliberately unlike EXP-001.

Three players of THREE representations (state machine, constant, Proteus tape VM) in one non-stationary
integer world (regime switch every 8 ticks, 1-in-5 stochastic register kick), observation delay + a
seeded channel permutation as interventions, a sweep over the WORLD STRUCTURE itself (world_seed) and
the regime period, all seven controls, three observers including the series, survival objective.

Questions this playtest asks the kernel (directive s2): mixed representations in one experiment; worlds
varying independently of players; interventions without world edits; controls on players the control
does not know; series under non-stationarity; unexpected events retained.
"""
from __future__ import annotations

import json
import sys

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine, constant_player, random_proteus_player, proteus_available


def build() -> Experiment:
    players = [random_statemachine(31, n_states=6, n_buckets=16, width=3).manifest(), constant_player([3, 0, 5]).manifest()]
    players.append(random_proteus_player(77).manifest() if proteus_available() else random_statemachine(32, width=3).manifest())
    return Experiment(
        family="pt_a_alien_mix",
        world=ref("world.integer.v1", n_regs=8, n_players=3, act_width=3, act_range=8, n_ops=6, regime_period=8, stoch_rate=5, world_seed=1, start_charge=60, yield_amt=9),
        substrate=ref("substrate.flat.v1"),
        players=players,
        interventions=[{"name": "lag", "world_params": {}, "wrappers": {"observation_delay": 2}},
                       {"name": "scramble", "world_params": {}, "wrappers": {"observation_permute": 4242}}],
        objective=ref("objective.survival.v1"),
        observers=[ref("observer.trace.v1"), ref("observer.descriptor.v1"), ref("observer.series.v1")],
        controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.negative.v1"), ref("control.positive.v1"),
                  ref("control.sham.v1"), ref("control.scratch.v1"), ref("control.permutation.v1")],
        sweep={"world.params.world_seed": [1, 2, 3], "world.params.regime_period": [0, 8]},
        seed_policy={"base": 500, "n_seeds": 2},
        budget={"episodes": 2, "horizon": 40},
        provenance={"designer": "Bellerophon", "lane": "KERNEL_PLAYTEST", "note": "playtest A: alien mix"},
    )


def main(out: str = "prometheus/toolbox/playtests/receipts/pt_a.jsonl") -> dict:
    exp = build()
    assert not exp.validate(), exp.validate()
    low = exp.compile("local")
    if not low.ok:
        print(json.dumps(low.as_dict(), indent=1)); return low.as_dict()
    from prometheus.toolbox.backends.local import execute
    rep = execute(low.job, out)
    print(json.dumps({"experiment_id": rep.experiment_id, "runs": rep.n_runs, "failed": rep.n_failed, "valid": rep.valid,
                      "controls": {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep.controls.items()}}, indent=1))
    return rep.as_dict()


if __name__ == "__main__":
    main(*sys.argv[1:])
