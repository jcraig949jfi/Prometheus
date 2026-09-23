"""Playtest G (overnight C60): transfer + communication + ablation + per-player series, on the grid world.

Three statemachine.v2 players sharing a MAILBOX (their memory slot is a channel) in the Ludus-shaped grid
world, TRANSFERRED across two worlds (a world sweep: the source grid and a scarcer variant) with sham /
scratch / ablation (mailbox removed) / replay controls, per-player series, series-gain objective, holdout
seeds. Asks: does a channel change anything measurable vs its ablation (kernel question: is the
difference VISIBLE in the rows, not whether it is good); do per-player columns and the objective agree;
do transfer arms pair per world."""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine_v2

SRC = ref("world.grid.v1", n_nodes=6, n_players=3, world_seed=41, start_charge=50, pool_max=3, regen_every=3, read_gain=6)
DST = ref("world.grid.v1", n_nodes=6, n_players=3, world_seed=42, start_charge=50, pool_max=1, regen_every=9, read_gain=6)


def build() -> Experiment:
    return Experiment(
        family="pt_g_transfer_comms",
        world=SRC, substrate=ref("substrate.mailbox.v1", scope="lifetime", capacity=16),
        players=[random_statemachine_v2(s, n_states=6, n_buckets=12, width=3, mem_range=8).manifest() for s in (601, 602, 603)],
        objective=ref("objective.series_gain.v1"),
        observers=[ref("observer.trace.v1"), ref("observer.series.v1", per_player=True)],
        controls=[ref("control.replay.v1"), ref("control.sham.v1"), ref("control.scratch.v1"), ref("control.ablation.v1")],
        sweep={"world": [SRC, DST]},
        seed_policy={"base": 8100, "n_seeds": 3, "holdout_seeds": 2},
        budget={"episodes": 3, "horizon": 40, "world_state": "lifetime"},
        provenance={"designer": "Bellerophon", "lane": "KERNEL_PLAYTEST", "note": "playtest G: transfer + mailbox + ablation + per-player series"},
    )


def main(root: str = "prometheus/toolbox/playtests/receipts/pt_g") -> dict:
    from prometheus.toolbox.backends.local import execute
    from prometheus.toolbox.receipt import read_all
    from prometheus.toolbox import series as S
    wd = pathlib.Path(root); shutil.rmtree(wd, ignore_errors=True); wd.mkdir(parents=True)
    exp = build(); assert not exp.validate(), exp.validate()
    low = exp.compile("local"); assert low.ok, low.reasons
    rep = execute(low.job, wd / "receipts.jsonl")
    rs = read_all(wd / "receipts.jsonl")
    by = {}
    for r in rs:
        if r["arm"] == "SUMMARY":
            continue
        w = r["sweep_point"]["world"]["params"]["world_seed"]
        d = by.setdefault(w, {}).setdefault(r["arm"], {"n": 0, "obj": [], "msgs": 0, "ws": 0})
        d["n"] += 1; d["obj"].append(r["science"]["objective"]["value"]); d["msgs"] += r["science"]["observations"]["observer.trace.v1"]["events_by_kind"].get("MESSAGE", 0)
        d["ws"] += r["accounting"].get("ws_reads", 0) + r["accounting"].get("ws_writes", 0)
    for w in by:
        for arm in by[w]:
            o = [x for x in by[w][arm]["obj"] if x is not None]; by[w][arm]["obj"] = round(sum(o) / len(o), 2) if o else None
    prim = [r for r in rs if r["arm"] == "primary"][0]
    eps = S.recover(prim, wd)["observer.series.v1"]
    out = {"runs": rep.n_runs, "failed": rep.n_failed, "valid": rep.valid, "controls": {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep.controls.items()},
           "by_world_arm": by, "splits": rs[-1]["science"]["splits"], "series_columns": prim["series"]["observer.series.v1"]["columns"],
           "sample_last_record": eps[-1][-1] if eps and eps[-1] else None}
    print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:])
