"""E-BEL-REPL-01 PILOT 2/3 (declared feasibility only; no event scored, no state-freedom measured on any evolved genome).

Per run it records ONLY: whether a self-replicator originated (first SR tick), extinction, SR alive at the end, SR max depth,
births and wall seconds. The purpose is to size the preregistered design (origin rate and cost under CARRIED vs ZERO; founder
establishment under CARRIED vs ZERO). Pilot seeds are 30_000_000 + s, a range the production design will not use.

Cell: grounding G1 ENDOGENOUS_PARTIAL/Z80_64 (v2, GRID LOCAL, 256 cells, lifespan 40, BYTE MED, IMPLICIT/ATOMIC/INC).
    python -I pilot_worlds.py --arm CARRIED --mode random --s0 0 --n 30 --ticks 2000
    python -I pilot_worlds.py --arm ZERO --mode founders --s0 0 --n 24 --ticks 2000     # founders: FOUNDERS_PILOT.json, cycled
Prints one JSON document on stdout (the Fabric result).
"""
import argparse, json, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from prometheus.z80atlas.world import Config, World  # noqa: E402

CELL = {"budget": 256, "cells": 256, "env_dynamics": "FIXED", "ext_mut_mult": 4.0, "init": "RANDOM", "layout": "SHARED", "ldir": "on",
        "lifespan": 40, "mutation": "BYTE", "mutation_rate": "MED", "physics": "v2", "pressure": "IMPLICIT", "read_gate": "ABR",
        "recombination": "NONE", "representation": "Z80_64", "reproduction": "ENDOGENOUS_PARTIAL", "scoring": "ATOMIC",
        "spatial": "LOCAL", "target_fill": "preserve", "task": "INC", "undefined_op": "NOP", "world": "GRID"}
PILOT_SEED0 = 30_000_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=("CARRIED", "ZERO"))
    ap.add_argument("--mode", required=True, choices=("random", "founders"))
    ap.add_argument("--zero-p", type=float, default=0.0)
    ap.add_argument("--s0", type=int, default=0); ap.add_argument("--n", type=int, default=30); ap.add_argument("--ticks", type=int, default=2000)
    a = ap.parse_args()
    founders = json.loads((pathlib.Path(__file__).resolve().parent.parent / "FOUNDERS_PILOT.json").read_text())["tapes"] if a.mode == "founders" else []
    rows = []
    for s in range(a.s0, a.s0 + a.n):
        seed = PILOT_SEED0 + (1_000_000 if a.mode == "founders" else 0) + s
        tapes = (founders[s % len(founders)],) if founders else ()
        cfg = Config(**CELL, ticks=a.ticks, init_tapes=tapes, reg_world=a.arm, reg_zero_p=a.zero_p)
        t0 = time.perf_counter()
        w = World(cfg, seed); w.run()
        sm = w.summary([o for o in w.cells if o])
        f = sm.get("first_self_replication")
        rows.append([s, f["tick"] if f else None, sm["extinct"], sm["extinct_tick"], sm["sr_alive_end"], sm["sr_max_depth"],
                     sm["endogenous_births"], round(time.perf_counter() - t0, 2)])
    print(json.dumps({"arm": a.arm, "zero_p": a.zero_p, "mode": a.mode, "ticks": a.ticks, "cols": ["s", "first_sr_tick", "extinct", "extinct_tick",
                      "sr_alive_end", "sr_max_depth", "endogenous_births", "wall_s"], "rows": rows}, separators=(",", ":")))


if __name__ == "__main__":
    main()
