"""C1b: C1's CPU vs GPU cells re-measured under CONTROLLED background CPU load.

Lane B's C1 bounty (3e7fbc89c) re-measured numba_par at 45-81k obs/s under ~30% host
load vs C's 101.5k. Load levels are separate processes started by this harness:
  idle    no load
  sham8   8 processes that only sleep (claims load, uses none)   -- control
  burn4   4 busy-spinning processes (~B's condition)
  burn8   8 busy-spinning processes
Load is MEASURED per cell (psutil host CPU%), never asserted. Rounds x loads are
interleaved in a seeded shuffled order; every timed cell is validated on C1's
float64 oracle. Imports lane B's nb_bucket kernel read-only.

usage: python -m primordial.brain.c1b_load [--rounds 3] [--quick]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import multiprocessing as mp
import random
import time

import numpy as np
import psutil

from primordial.brain import tt_policy as tt
from primordial.brain.c1_crossover import A_ACTIONS, HOT, TIE_GAP, compare, git_sha, nvsmi, time_cell

EXP_ID = "C1b-load-sensitivity"
LOADS = {"idle": (0, False), "sham8": (8, True), "burn4": (4, False), "burn8": (8, False)}
CONFIGS = [(4, 16, [256, 1024, 4096, 16384]), (16, 64, [1024, 4096, 16384])]
CPU = ["numba_1", "numba_par", "numba_par_c3", "nb_bucket_c3", "np_bucket"]
GPU = ["torch_gpu_e2e", "torch_gpu_graph_e2e"]
CHEAT = ["cheat_skip_half"]


def _burn(stop, sleepy):
    if sleepy:
        while not stop.is_set():
            time.sleep(0.05)
        return
    x = 0
    while not stop.is_set():
        for _ in range(200_000):
            x += 1


class Load:
    def __init__(self, n, sleepy):
        self.n, self.sleepy = n, sleepy

    def __enter__(self):
        self.stop = mp.Event()
        self.procs = [mp.Process(target=_burn, args=(self.stop, self.sleepy), daemon=True)
                      for _ in range(self.n)]
        for p in self.procs:
            p.start()
        time.sleep(2.0 if self.n else 0.2)
        return self

    def __exit__(self, *exc):
        self.stop.set()
        for p in self.procs:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        time.sleep(0.5)


def backend(name, p):
    if name == "nb_bucket_c3":
        from primordial.soup.bounty.c1_cpu import nb_bucket_class   # lane B, read-only
        return nb_bucket_class(3)(p)
    if name == "numba_par_c3":
        return tt.NumbaParC3(p)
    return tt.make(name, p)


def analyse(cells):
    med = {}
    for c in cells:
        med.setdefault((c["obs_dim"], c["r"], c["B"], c["impl"], c["load"]), []).append(c)
    agg = {k: {"obs_per_s": float(np.median([c["obs_per_s_wall"] for c in v])),
               "host_cpu": float(np.median([c["host_cpu_pct"] for c in v])),
               "valid": all(c["valid"] for c in v)} for k, v in med.items()}
    ratio = {}
    for (od, r, B, impl, load), a in agg.items():
        if load != "idle" and (od, r, B, impl, "idle") in agg:
            ratio[f"d{4 * od}_r{r}_B{B}/{impl}/{load}"] = a["obs_per_s"] / agg[(od, r, B, impl, "idle")]["obs_per_s"]
    cross = {}
    for od, r, Bs in CONFIGS:
        for load in LOADS:
            best = {B: max(((agg[(od, r, B, i, load)]["obs_per_s"], i) for i in CPU
                            if (od, r, B, i, load) in agg and agg[(od, r, B, i, load)]["valid"]),
                           default=(0.0, "none")) for B in Bs}
            for g in GPU:
                wins = [(od, r, B, g, load) in agg and agg[(od, r, B, g, load)]["obs_per_s"] > best[B][0] for B in Bs]
                xB = next((B for i, B in enumerate(Bs) if all(wins[i:])), None)
                cross[f"d{4 * od}_r{r}/{g}/{load}"] = {
                    "crossover_B_in_tested": xB,
                    "gpu_over_best_cpu": {B: (agg[(od, r, B, g, load)]["obs_per_s"] / best[B][0]) if best[B][0] else None
                                          for B in Bs if (od, r, B, g, load) in agg},
                    "best_cpu": {B: best[B][1] for B in Bs}}
    host = {load: float(np.median([c["host_cpu_pct"] for c in cells if c["load"] == load])) for load in LOADS}
    honest = [c for c in cells if not c["cheat"]]
    skip = [c for c in cells if c["cheat"] and c["n_compared"] >= 64]
    return {"ratio_vs_idle": ratio, "crossover": cross, "host_cpu_median_by_load": host,
            "honest_invalid": sum(not c["valid"] for c in honest), "honest_cells": len(honest),
            "skip_half_invalid_ge64": [sum(not c["valid"] for c in skip), len(skip)]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    import numba
    configs = [(4, 16, [1024])] if a.quick else CONFIGS
    rounds = 1 if a.quick else a.rounds
    names = CPU + GPU + CHEAT
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    rng = np.random.default_rng(11)
    cells = []
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
        policies = {}
        for od, r, Bs in configs:
            p = tt.random_policy(od, r, A_ACTIONS, seed=1000 * od + r)     # C1's seeds
            bes = {n: backend(n, p) for n in names}
            obs = {B: np.random.default_rng(7 + r + B).integers(0, 65535, size=(B, od), dtype=np.uint16, endpoint=True)
                   for B in Bs}
            ref = {B: tt.ref64_logits(p, obs[B][:min(B, 1024)]) for B in Bs}
            policies[(od, r)] = (Bs, bes, obs, ref)
        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "rounds": rounds,
              "loads": LOADS, "configs": configs, "names": names, "threads": os.environ.get("NUMBA_NUM_THREADS"),
              "numba_threading_layer_requested": numba.config.THREADING_LAYER, "gpu_start": nvsmi(),
              "cpu_count": os.cpu_count()})
        layer_logged = False
        for rd in range(rounds):
            order = list(LOADS)
            random.Random(rd * 31 + 5).shuffle(order)
            for load in order:
                n, sleepy = LOADS[load]
                with Load(n, sleepy):
                    for (od, r), (Bs, bes, obs, ref) in policies.items():
                        for B in Bs:
                            for name in rng.permutation(names):
                                be = bes[name]
                                psutil.cpu_percent(None)
                                x = be.prepare(obs[B])
                                per, wall = time_cell(be, x, max_reps=2000)
                                acts = be.to_numpy(be.run(x))
                                host = psutil.cpu_percent(None)
                                nc, ties, mism = compare(acts, ref[B], TIE_GAP)
                                row = {"kind": "cell", "round": rd, "load": load, "n_procs": n, "sham": sleepy,
                                       "obs_dim": od, "d": 4 * od, "r": r, "B": B, "impl": str(name),
                                       "cheat": be.cheat, "reps": len(per), "t_median_s": float(np.median(per)),
                                       "obs_per_s_wall": B * len(per) / wall, "n_compared": nc, "n_ties": ties,
                                       "n_mismatch": mism, "valid": mism == 0, "host_cpu_pct": host}
                                cells.append(row)
                                emit(row)
                                if not layer_logged and name.startswith("numba"):
                                    emit({"kind": "threading_layer", "layer": numba.threading_layer()})
                                    layer_logged = True
                    print(f"round {rd} {load}: host_cpu median "
                          f"{np.median([c['host_cpu_pct'] for c in cells if c['load'] == load and c['round'] == rd]):.0f}%",
                          flush=True)
        summary = analyse(cells)
        emit({"kind": "summary", **summary})
        for _, (_, bes, _, _) in policies.items():
            for be in bes.values():
                be.close()
    print(json.dumps({k: summary[k] for k in ("host_cpu_median_by_load", "honest_invalid", "honest_cells",
                                               "skip_half_invalid_ge64")}))
    print("rows:", out)
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
