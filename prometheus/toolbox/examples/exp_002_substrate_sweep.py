"""EXP-002: the same players x {flat, kv, stream} substrates (directive s12; overnight s5).

Two statemachine.v2 players (one memory slot each, living in whatever workspace the substrate grants) in the
integer world, swept over SIX substrate configurations (flat; kv episode-scoped; kv lifetime-scoped; kv
lifetime with a 4-tick ttl; stream lag 2; stream lag 5 with a capacity of 8) x world regime period
{0, 6} x start charge {40, 80}, 3 seeds x 3 episodes x 48 ticks, with replay / cheat / negative / sham /
scratch controls, trace + series observers, and an objective that CHARGES memory (0.05 per workspace read
or write). A kernel playtest first: lifetime state, expiry, bounded capacity, reuse across episodes, series,
controls and replay all under one designer's text with no library or device named.

    python -m prometheus.toolbox.examples.exp_002_substrate_sweep [out.jsonl]
"""
from __future__ import annotations

import json
import sys

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine_v2

SUBSTRATES = [
    ref("substrate.flat.v1"),
    ref("substrate.kv.v1", scope="episode"),
    ref("substrate.kv.v1", scope="lifetime"),
    ref("substrate.kv.v1", scope="lifetime", ttl=4),
    ref("substrate.stream.v1", scope="lifetime", lag=2),
    ref("substrate.stream.v1", scope="lifetime", lag=5, maxlen=8),
]


def build() -> Experiment:
    return Experiment(
        family="exp002_substrate_sweep",
        world=ref("world.integer.v1", n_regs=6, n_players=2, act_width=2, act_range=8, world_seed=23, start_charge=40, yield_amt=10, step_cost=1),
        substrate=ref("substrate.flat.v1"),
        players=[random_statemachine_v2(21, n_states=5, n_buckets=12, mem_range=16, write_every=2).manifest(),
                 random_statemachine_v2(22, n_states=5, n_buckets=12, mem_range=16, write_every=2).manifest()],
        interventions=[{"name": "conditions", "world_params": {"regime_period": 0}, "wrappers": {}}],
        objective=ref("objective.yield_net.v1", penalties={"ws_reads": 0.05, "ws_writes": 0.05, "ws_appends": 0.05}),
        observers=[ref("observer.trace.v1"), ref("observer.series.v1")],
        controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.negative.v1"), ref("control.sham.v1"), ref("control.scratch.v1")],
        sweep={"substrate": SUBSTRATES, "interventions.0.world_params.regime_period": [0, 6], "world.params.start_charge": [40, 80]},
        seed_policy={"base": 7000, "n_seeds": 3},
        budget={"episodes": 3, "horizon": 48},
        required_capabilities=frozenset({"ext.events.v1", "ext.replay.bit.v1"}),
        provenance={"designer": "Bellerophon", "lane": "KERNEL_PLAYTEST", "note": "EXP-002: same players across workspaces; memory is charged"},
    )


def main(out: str = "prometheus/toolbox/examples/receipts/exp_002.jsonl") -> dict:
    exp = build()
    assert not exp.validate(), exp.validate()
    low = exp.compile("local")
    if not low.ok:
        print(json.dumps(low.as_dict(), indent=1)); return low.as_dict()
    from prometheus.toolbox.backends.local import execute
    rep = execute(low.job, out)
    print(json.dumps({"experiment_id": rep.experiment_id, "runs": rep.n_runs, "completed": rep.n_completed, "failed": rep.n_failed, "valid": rep.valid,
                      "controls": {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep.controls.items()}, "receipts": rep.receipts_path}, indent=1))
    return rep.as_dict()


if __name__ == "__main__":
    main(*sys.argv[1:])
