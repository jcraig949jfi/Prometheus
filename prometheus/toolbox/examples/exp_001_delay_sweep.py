"""EXP-001: the end-to-end reference Experiment (directive s25).

Two state-machine players in the kernel's integer world, swept over observation delay (a kernel-applied
intervention wrapper) x action landing delay (a world parameter intervention), with seven controls,
two observers and one objective, 3 seeds x 2 episodes per run. The designer's text names NO library,
host, queue or transport.

    python -m prometheus.toolbox.examples.exp_001_delay_sweep [out.jsonl]
"""
from __future__ import annotations

import json
import sys

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine


def build() -> Experiment:
    return Experiment(
        family="exp001_delay_sweep",
        world=ref("world.integer.v1", n_regs=6, n_players=2, act_width=2, act_range=8, world_seed=11, start_charge=48, yield_amt=6),
        substrate=ref("substrate.flat.v1"),
        players=[random_statemachine(101, n_states=4, n_buckets=8).manifest(), random_statemachine(202, n_states=4, n_buckets=8).manifest()],
        interventions=[{"name": "conditions", "world_params": {"action_delay": 0}, "wrappers": {"observation_delay": 0}}],
        objective=ref("objective.yield_net.v1", penalties={"ops": 0.01}),
        observers=[ref("observer.trace.v1"), ref("observer.descriptor.v1")],
        controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.negative.v1"), ref("control.positive.v1"),
                  ref("control.sham.v1"), ref("control.scratch.v1"), ref("control.permutation.v1")],
        sweep={"interventions.0.wrappers.observation_delay": [0, 4], "interventions.0.world_params.action_delay": [0, 2]},
        seed_policy={"base": 1000, "n_seeds": 3},
        budget={"episodes": 2, "horizon": 64},
        required_capabilities=frozenset({"ext.events.v1", "ext.replay.bit.v1"}),
        provenance={"designer": "Bellerophon", "lane": "KERNEL_REFERENCE", "note": "EXP-001 proves the local path; it claims nothing about the world"},
    )


def main(out: str = "prometheus/toolbox/examples/receipts/exp_001.jsonl") -> dict:
    exp = build()
    assert not exp.validate(), exp.validate()
    low = exp.compile("local")
    if not low.ok:
        print(json.dumps(low.as_dict(), indent=1)); return low.as_dict()
    from prometheus.toolbox.backends.local import execute
    rep = execute(low.job, out)
    print(json.dumps({"experiment_id": rep.experiment_id, "runs": rep.n_runs, "completed": rep.n_completed, "failed": rep.n_failed,
                      "valid": rep.valid, "controls": {k: v["outcome"] for k, v in rep.controls.items()}, "receipts": rep.receipts_path}, indent=1))
    return rep.as_dict()


if __name__ == "__main__":
    main(*sys.argv[1:])
