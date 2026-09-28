"""Designed echoes as calibration (ARC3 Block E).

Stage 'predict' (run and COMMITTED before any engine run): W-A's
zero-parameter echo model (workers/W-A/echo_model.py) predicts accuracy vs
gap for each hand-designed echo genome. Stage 'engine' runs the genomes
in PTE. Stage 'instruments' checks the carrier swap and reach instruments
against designed carrier trajectories. A hand-designed echo is a
POSITIVE CONTROL for the model and the instruments, NOT evidence of
emergence.

    python design.py predict | engine | instruments | compare
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import pathlib
import sys

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "roles/Ananke/research/workers/W-A"))
from prometheus.ananke import assays, c1b, c1b_run, lens, plants  # noqa: E402
import echo_model as em  # noqa: E402

torch.set_num_threads(2)
GAPS = list(range(2, 17))
SEEDS = assays.world_seeds(0x5F1, 64)
PH0, ENV0, _, _ = c1b_run.load("4ab2ba014aac967e")


def genome(ph, k: int, route: str):
    """Canonical echo with pipeline depth k: EMIT const; PAY0 := SENSE;
    PAY1 := IN0_0; S0 := S1; ...; S_{k-1} := S_k; S_k := IN0_1.
    route 'specimen' adds W-A's routing lines (RPORT -7168, RVAL -1)."""
    lines = [("CONST", "EMIT", 0, 1, 62), ("MOV", "PAY0", "SENSE", 0, 0), ("MOV", "PAY1", "IN0_0", 0, 0)]
    for i in range(k):
        lines.append(("MOV", f"S{i}", f"S{i + 1}", 0, 0))
    lines.append(("MOV", f"S{k}", "IN0_1", 0, 0))
    if route == "specimen":
        lines += [("CONST", "RPORT", 0, 6, -112), ("CONST", "RVAL", 0, 0, -1)]
    return plants.assemble(ph, lines)[None]


# name -> (physics overrides, pipeline k, route)
DESIGNS = {
    "E1_canon": ({"plastic_route": 0}, 0, "uniform"),
    "E1s_canon_specroute": ({}, 0, "specimen"),
    "E2_pipe2": ({"plastic_route": 0, "state_dim": 3}, 2, "uniform"),
    "E3_pipe2_lb0": ({"plastic_route": 0, "state_dim": 3, "lat_base": 0}, 2, "uniform"),
    "E4_pipe4_mistimed": ({"plastic_route": 0, "state_dim": 5}, 4, "uniform"),
    "E5_pipe1_up3": ({"plastic_route": 0, "update_period": 3}, 1, "uniform"),
    "E6_specroute_lh2": ({"lat_hop": 2}, 0, "specimen"),
}


def build(name):
    kw, k, route = DESIGNS[name]
    ph = PH0.replace(**kw)
    return ph, genome(ph, k, route), em.Prog(shift=0, route=route, pipeline=k)


def stage_predict():
    out = {}
    for name in DESIGNS:
        ph, g, prog = build(name)
        out[name] = {str(gp): em.predict(ph, dataclasses.replace(ENV0, gap=gp), prog, nw=4000, seed=gp)
                     for gp in GAPS}
        out[name]["_kernel"] = {str(k): v for k, v in em.kernel(ph, prog).items()}
        print(name, " ".join(f"{gp}:{out[name][str(gp)]:.2f}" for gp in GAPS), flush=True)
    blob = json.dumps(out, indent=1, sort_keys=True)
    (HERE / "predictions.json").write_text(blob)
    print("sha256", hashlib.sha256(blob.encode()).hexdigest())


def stage_engine():
    res = {}
    for name in DESIGNS:
        ph, g, _ = build(name)
        res[name] = {}
        for gp in GAPS:
            e = dataclasses.replace(ENV0, gap=gp)
            tr = lens.run(ph, g, e, SEEDS, device="cpu")
            res[name][str(gp)] = lens.ci(lens.trial_acc(tr, range(e.trials)))
        print(name, " ".join(f"{gp}:{res[name][str(gp)][0]:.2f}" for gp in GAPS), flush=True)
    (HERE / "engine.json").write_text(json.dumps(res, indent=1))


def stage_instruments():
    """Designed carrier trajectory: E2 (pipeline 2) at its best predicted
    gap. The bit should ride the CHANNEL (pay1) mid-gap and sit in SITE state
    (the pipeline registers) in the last wakes before the readout."""
    pred = json.loads((HERE / "predictions.json").read_text())
    out = {}
    for name in ("E1_canon", "E2_pipe2"):
        ph, g, _ = build(name)
        best = max(GAPS, key=lambda gp: pred[name][str(gp)])
        env = dataclasses.replace(ENV0, gap=best)
        tk = c1b.ticks(env)
        rows = {}
        for off in (-6, -4, -3, -2, -1):
            ticks = [ro + off for ro in tk["ro"]]
            t = lens.carrier_table(ph, g, env, SEEDS, ticks, names=["site_all", "channel_all", "pay1"])
            rows[str(off)] = {k: (v["verdict"] if isinstance(v, dict) else v) for k, v in t.items()}
        prof = lens.cue_arrival_profile(ph, g[0] if g.ndim == 4 else g, env, M=64)
        out[name] = {"gap": best, "swaps_by_lag_before_readout": rows,
                     "cue_arrival_lags": prof["lags"]}
        print(name, best, json.dumps(rows), prof["lags"], flush=True)
    (HERE / "instruments.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"predict": stage_predict, "engine": stage_engine, "instruments": stage_instruments}[sys.argv[1]]()
