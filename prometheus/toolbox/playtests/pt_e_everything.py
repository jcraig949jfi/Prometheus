"""Playtest E (overnight C35): everything tonight built, in one designer text, run twice with an interruption and
a forensic replay in between. Heterogeneous machines in one world (a memory state machine on kv-lifetime, a
rewrite system on a stream workspace, a Proteus tape on flat), a task schedule, a population sweep, holdout
seeds, series-gain objective, six controls; interrupted after 20 runs and resumed; then replay_file() over the
resumed receipts must report zero divergence."""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine_v2, random_rewrite_system, random_proteus_player, proteus_available, random_statemachine


def build() -> Experiment:
    pop_a = [dict(random_statemachine_v2(501, n_states=6, n_buckets=10).manifest(), substrate=ref("substrate.kv.v1", scope="lifetime", ttl=8)),
             dict(random_rewrite_system(502, n_rules=8, alphabet=8, tape_len=10).manifest(), substrate=ref("substrate.stream.v1", scope="lifetime", lag=2)),
             (random_proteus_player(17) if proteus_available() else random_statemachine(503)).manifest()]
    pop_b = [dict(random_statemachine_v2(511, n_states=6, n_buckets=10).manifest(), substrate=ref("substrate.kv.v1", scope="episode")),
             dict(random_rewrite_system(512, n_rules=8, alphabet=8, tape_len=10).manifest(), substrate=ref("substrate.stream.v1", scope="episode", lag=4)),
             (random_proteus_player(56) if proteus_available() else random_statemachine(513)).manifest()]
    return Experiment(
        family="pt_e_everything",
        world=ref("world.integer.v1", n_regs=8, n_players=3, act_width=2, world_seed=88, start_charge=90, yield_amt=9, regime_period=5),
        substrate=ref("substrate.flat.v1"),
        players=pop_a,
        interventions=[{"name": "lag", "wrappers": {"observation_delay": 1}},
                       {"name": "tasks", "schedule": [{"tick": 12, "world_params": {"act_cost": 3}}, {"tick": 24, "world_params": {"yield_amt": 15, "act_cost": 1}}]}],
        objective=ref("objective.series_gain.v1"),
        observers=[ref("observer.trace.v1"), ref("observer.descriptor.v1", action_scale=2, yield_scale=20), ref("observer.series.v1")],
        controls=[ref("control.replay.v1"), ref("control.cheat.v1"), ref("control.negative.v1"), ref("control.positive.v1"), ref("control.sham.v1"), ref("control.permutation.v1")],
        sweep={"players": [pop_a, pop_b], "world.params.start_charge": [60, 90]},
        seed_policy={"base": 9000, "n_seeds": 2, "holdout_seeds": 1},
        budget={"episodes": 3, "horizon": 36},
        provenance={"designer": "Bellerophon", "lane": "KERNEL_PLAYTEST", "note": "playtest E: everything at once + interruption + forensic replay"},
    )


def main(root: str = "prometheus/toolbox/playtests/receipts/pt_e") -> dict:
    from prometheus.toolbox.backends import local as L
    from prometheus.toolbox.receipt import read_all, scan
    wd = pathlib.Path(root); shutil.rmtree(wd, ignore_errors=True); wd.mkdir(parents=True)
    exp = build(); assert not exp.validate(), exp.validate()
    low = exp.compile("local"); assert low.ok, low.reasons
    real = L.run_one; calls = {"n": 0}

    def interrupt(spec, registry, receipt_dir=None):
        calls["n"] += 1
        if calls["n"] == 21:
            raise KeyboardInterrupt("simulated interruption after 20 runs")
        return real(spec, registry, receipt_dir)
    L.run_one = interrupt
    try:
        try:
            L.execute(low.job, wd / "receipts.jsonl")
        except KeyboardInterrupt:
            pass
    finally:
        L.run_one = real
    partial = scan(wd / "receipts.jsonl")
    rep = L.execute(low.job, wd / "receipts.jsonl", resume=True)
    rp = L.replay_file(wd / "receipts.jsonl", wd / "replay.jsonl")
    rs = read_all(wd / "receipts.jsonl")
    out = {"runs": rep.n_runs, "resumed": rep.resumed_runs, "failed": rep.n_failed, "valid": rep.valid,
           "controls": {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep.controls.items()},
           "partial_valid_before_resume": partial["valid"], "partial_defects": partial["defects"],
           "replay": {k: rp[k] for k in ("runs_compared", "divergent", "kernel_hash_equal")},
           "splits": rs[-1]["science"]["splits"], "receipts": len(rs)}
    print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:])
