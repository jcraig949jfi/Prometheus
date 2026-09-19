"""Playtest I (overnight C108): the night's late surface used together on the GRID world -- structured
observations (obs_mode="structured"), a vector objective (net yield + survival.v2), per-player series, a
mailbox substrate, batch policy requested (the grid has no batch implementation: the fallback reason must be
on every receipt), MAP-Elites ranked by each component, a permutation control (must be REFUSED at lowering
for a structured world, so it is run separately and its refusal recorded). Kernel questions only."""
from __future__ import annotations

import json
import shutil
import sys
import pathlib

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox import search as SR
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import lower, execute
from prometheus.toolbox.ref.players import random_statemachine_v2


def template(obs_mode="structured") -> Experiment:
    return Experiment(family="pt_i_grid", world=ref("world.grid.v1", world_seed=5, n_nodes=7, n_players=2, start_charge=30, regen_every=3, pool_max=3, obs_mode=obs_mode),
                      substrate=ref("substrate.mailbox.v1", scope="episode", capacity=4),
                      players=[random_statemachine_v2(1, width=3).manifest(), random_statemachine_v2(2, width=3).manifest()],
                      objective=ref("objective.multi.v1", components={"net": ref("objective.yield_net.v1", penalties={"ws_writes": 0.05}), "life": ref("objective.survival.v2")}),
                      observers=[ref("observer.descriptor.v1", action_scale=3, yield_scale=20), ref("observer.series.v1", per_player=True)],
                      controls=[ref("control.replay.v1"), ref("control.sham.v1")], seed_policy={"base": 11, "n_seeds": 2}, budget={"episodes": 2, "horizon": 30, "batch": 4})


def main(root: str = "prometheus/toolbox/playtests/receipts/pt_i") -> dict:
    from prometheus.toolbox.registry import default_registry
    reg = default_registry().fork(); out = {}
    wd = pathlib.Path(root); shutil.rmtree(wd, ignore_errors=True); wd.mkdir(parents=True)
    # 1. one plain execution: rows first
    e = template(); low = lower(e, reg); assert low.ok, low.as_dict()
    rep = execute(low.job, wd / "plain.jsonl", reg)
    rows = [r for r in read_all(wd / "plain.jsonl") if r["arm"] != "SUMMARY"]; summ = [r for r in read_all(wd / "plain.jsonl") if r["arm"] == "SUMMARY"][0]
    out["plain"] = {"runs": rep.n_runs, "failed": rep.n_failed, "valid": rep.valid, "controls": {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep.controls.items()},
                    "execution_reasons": sorted({r["execution"]["reason"] for r in rows}), "objective_shape": summ["science"]["splits"]["train"]["objective_shape"],
                    "objective_mean": summ["science"]["splits"]["train"]["objective_mean"],
                    "series_status": sorted({r["series"]["observer.series.v1"]["status"] for r in rows if "series" in r}),
                    "series_columns": rows[0]["series"]["observer.series.v1"].get("columns"),
                    "mailbox": {k: rows[0]["accounting"].get(k) for k in ("ws_writes", "ws_reads", "ws_discarded", "ws_keys")}, "spec_hashes_distinct": len({r["science"]["player_fingerprints"]["0"]["spec_hash"] for r in rows})}
    # 2. a permutation control must be refused at lowering (structured observations), not silently flattened
    e2 = template(); e2.controls = [ref("control.permutation.v1")]; low2 = lower(e2, reg)
    out["permutation_on_structured"] = {"status": low2.status, "reasons": low2.reasons}
    e3 = template(obs_mode="flat"); e3.controls = [ref("control.permutation.v1")]; low3 = lower(e3, reg)
    rep3 = execute(low3.job, wd / "flat_perm.jsonl", reg)
    out["permutation_on_flat"] = {k: (v["outcome"], v["met"], v["not_met"], v["indeterminate"]) for k, v in rep3.controls.items()}
    # 3. search ranked by each component
    for rank in ("net", "life"):
        t = template(); t.players = []; t.world["params"]["n_players"] = 1; t.controls = []
        res = SR.evolve(t, ref("selector.map_elites.v1", n=6, representation="statemachine.v2", rank=rank), generations=4, workdir=wd / rank, seed=9, registry=reg)
        rows = SR.committed_rows(SR.load_rows(wd / rank / "archive.jsonl")); cells = SR.elites_by_cell(rows, rank=rank)
        out["search_" + rank] = {"gens": res["generations_done"], "elites": len(rows), "distinct_players": len({r["player_hash"] for r in rows}), "cells": len(cells),
                                 "best": max((r["objective"][rank] for r in rows if r["objective"]), default=None),
                                 "none_rows": sum(1 for r in rows if r["objective"] is None)}
    print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:])
