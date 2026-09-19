"""Playtest H (overnight C96): a VECTOR objective above the kernel. One template, objective.multi.v1 with two
named components (net yield, survival ticks), MAP-Elites ranked by each component in turn, 5 generations x 8
proposals x 2 seeds. Asks (kernel questions only): do rows carry both components; does the rank change what the
archive keeps; does a component that is None in some seed poison the row honestly; do the per-generation
receipts' split summaries read "vector" with per-component means."""
from __future__ import annotations

import json
import shutil
import sys
import pathlib

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox import search as SR
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.ref.players import random_statemachine_v2


def template() -> Experiment:
    return Experiment(family="pt_h_multi", world=ref("world.integer.v1", world_seed=31, n_regs=6, start_charge=24, yield_amt=12, step_cost=1, regime_period=5),
                      substrate=ref("substrate.kv.v1", scope="lifetime"), players=[random_statemachine_v2(1).manifest()],
                      objective=ref("objective.multi.v1", components={"net": ref("objective.yield_net.v1", penalties={"ws_writes": 0.05}), "life": ref("objective.survival.v2")}),
                      observers=[ref("observer.descriptor.v1", action_scale=2, yield_scale=40)], seed_policy={"base": 3, "n_seeds": 2}, budget={"episodes": 2, "horizon": 40})


def main(root: str = "prometheus/toolbox/playtests/receipts/pt_h") -> dict:
    from prometheus.toolbox.registry import default_registry
    reg = default_registry().fork()
    out = {}
    for rank in ("net", "life"):
        wd = pathlib.Path(root) / rank; shutil.rmtree(wd, ignore_errors=True)
        res = SR.evolve(template(), ref("selector.map_elites.v1", n=8, representation="statemachine.v2", rank=rank), generations=5, workdir=wd, seed=27, registry=reg)
        rows = SR.committed_rows(SR.load_rows(wd / "archive.jsonl")); cells = SR.elites_by_cell(rows, rank=rank)
        shapes = set(); comp_means = []
        for f in sorted(wd.glob("gen_*_a*.jsonl")):
            for r in read_all(f):
                if r["arm"] == "SUMMARY":
                    sp = r["science"]["splits"]["train"]; shapes.add(sp["objective_shape"]); comp_means.append(sp["objective_mean"])
        out[rank] = {"gens": res["generations_done"], "elites": len(rows), "cells": len(cells),
                     "distinct_players": len({r["player_hash"] for r in rows}), "distinct_behaviour_classes": len({r["fingerprint"] for r in rows}),
                     "rows_with_both_components": sum(1 for r in rows if isinstance(r["objective"], dict) and set(r["objective"]) == {"net", "life"}),
                     "rows_with_none": sum(1 for r in rows if r["objective"] is None),
                     "best_by_rank": max((r["objective"][rank] for r in rows if r["objective"]), default=None),
                     "cell_elites": {str(k): {kk: round(vv, 2) for kk, vv in v[0]["objective"].items()} for k, v in sorted(cells.items())},
                     "summary_shapes": sorted(shapes), "gen_component_means": comp_means}
    a, b = SR.elites_by_cell(SR.committed_rows(SR.load_rows(pathlib.Path(root) / "net" / "archive.jsonl")), rank="net"), \
        SR.elites_by_cell(SR.committed_rows(SR.load_rows(pathlib.Path(root) / "life" / "archive.jsonl")), rank="life")
    out["rank_changes_the_archive"] = {str(k): (a[k][0]["fingerprint"][:8], b[k][0]["fingerprint"][:8]) for k in sorted(set(a) & set(b))}
    print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:])
