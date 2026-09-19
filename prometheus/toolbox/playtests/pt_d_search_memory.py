"""Playtest D (overnight C27): MAP-Elites above the kernel, same template on flat vs kv-lifetime substrates,
statemachine.v2 players, regime-switching world, 6 generations x 8 proposals x 2 seeds. Asks: does the
archive stay honest (rows, markers, resume), do descriptor cells fill, do silent players pollute the archive,
does the substrate change what search finds (a kernel question only: no claim about the world)."""
from __future__ import annotations

import json
import shutil
import sys
import pathlib

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox import search as SR
from prometheus.toolbox.ref.players import random_statemachine_v2


def template(sub) -> Experiment:
    return Experiment(family="pt_d_search", world=ref("world.integer.v1", world_seed=19, n_regs=6, start_charge=40, yield_amt=10, regime_period=6),
                      substrate=sub, players=[random_statemachine_v2(1).manifest()], objective=ref("objective.yield_net.v1", penalties={"ws_reads": 0.02, "ws_writes": 0.02}),
                      observers=[ref("observer.descriptor.v1", action_scale=2, yield_scale=40)], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 2, "horizon": 32})


class V2Selector(SR.MapElitesSelector):
    """gen-0 proposals as statemachine.v2 (the reference selector seeds v1); everything else inherited."""
    def propose(self, rows, rng_seed, n):
        if not any(r["kind"] == "elite" for r in rows):
            return [random_statemachine_v2(rng_seed * 131 + i, meta={"gen0": True}) for i in range(n)]
        return super().propose(rows, rng_seed, n)


def main(root: str = "prometheus/toolbox/playtests/receipts/pt_d") -> dict:
    from prometheus.toolbox.registry import default_registry, ComponentRecord
    reg = default_registry()
    if not reg.has("selector.map_elites_v2.playtest"):
        reg.register(ComponentRecord("selector.map_elites_v2.playtest", "selector", V2Selector, frozenset(), route="write", provenance={"author": "Bellerophon", "playtest": "D"}, license="repository"))
    out = {}
    for name, sub in (("flat", ref("substrate.flat.v1")), ("kv", ref("substrate.kv.v1", scope="lifetime"))):
        wd = pathlib.Path(root) / name; shutil.rmtree(wd, ignore_errors=True)
        res = SR.evolve(template(sub), ref("selector.map_elites_v2.playtest", n=8), generations=6, workdir=wd, seed=21)
        rows = SR.committed_rows(SR.load_rows(wd / "archive.jsonl")); cells = SR.elites_by_cell(rows)
        best = max((r["objective"] for r in rows if r["objective"] is not None), default=None)
        out[name] = {"elites": len(rows), "cells": len(cells), "best": best, "gens": res["generations_done"],
                     "cell_best": {str(k): round(v[0]["objective"], 2) for k, v in sorted(cells.items())}}
    print(json.dumps(out, indent=1)); return out


if __name__ == "__main__":
    main(*sys.argv[1:])
