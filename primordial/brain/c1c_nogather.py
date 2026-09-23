"""C1c: GPU TT contraction without the r x r gather.

Compares torch_gpu_bucket_e2e (sort-by-digit, contiguous dense matmuls) with C1's
gather+bmm GPU paths and the best CPU forms, up to B = 1,048,576. Every timed
cell is validated on C1's float64 oracle; peak GPU memory is recorded per cell
(the mechanism check: gather is B*r^2 per core, bucket B*r).

usage: python -m primordial.brain.c1c_nogather [--quick]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import time

import numpy as np
import psutil

from primordial.brain import tt_policy as tt
from primordial.brain.c1_crossover import A_ACTIONS, HOT, TIE_GAP, compare, git_sha, nvsmi, time_cell

EXP_ID = "C1c-gpu-no-gather"
NAMES = ["torch_gpu_bucket_e2e", "torch_gpu_e2e", "torch_gpu_graph_e2e", "nb_bucket", "numba_par",
         "cheat_gpu_bucket_skip_half"]
GPU = ("torch_gpu_bucket_e2e", "torch_gpu_e2e", "torch_gpu_graph_e2e", "cheat_gpu_bucket_skip_half")
CPU = ("nb_bucket", "numba_par")


class CheatGpuBucketSkipHalf(tt.TorchGpuBucketE2E):
    name = "cheat_gpu_bucket_skip_half"
    cheat = True
    stride = 2


def make(name, p):
    return CheatGpuBucketSkipHalf(p) if name == "cheat_gpu_bucket_skip_half" else tt.make(name, p)


def analyse(cells):
    out = {}
    keys = sorted({(c["obs_dim"], c["r"]) for c in cells})
    for od, r in keys:
        g = {}
        for c in cells:
            if (c["obs_dim"], c["r"]) == (od, r) and "skipped" not in c:
                g.setdefault(c["B"], {})[c["impl"]] = c
        Bs = sorted(g)
        tp = lambda B, i: g[B][i]["obs_per_s_wall"] if i in g[B] and g[B][i]["valid"] else None
        bucket_vs_gather = {B: (tp(B, "torch_gpu_bucket_e2e") / tp(B, "torch_gpu_e2e"))
                            if tp(B, "torch_gpu_bucket_e2e") and tp(B, "torch_gpu_e2e") else None for B in Bs}
        best_cpu = {B: max([tp(B, i) or 0 for i in CPU]) for B in Bs}
        bucket_vs_cpu = {B: (tp(B, "torch_gpu_bucket_e2e") / best_cpu[B]) if best_cpu[B] and tp(B, "torch_gpu_bucket_e2e")
                         else None for B in Bs}
        wins = [bool(bucket_vs_gather[B] and bucket_vs_gather[B] > 1) for B in Bs]
        xB = next((B for i, B in enumerate(Bs) if all(wins[i:])), None)
        mem = {B: (g[B]["torch_gpu_e2e"]["peak_gpu_mem"] / g[B]["torch_gpu_bucket_e2e"]["peak_gpu_mem"])
               if "torch_gpu_e2e" in g[B] and "torch_gpu_bucket_e2e" in g[B] else None for B in Bs}
        sat = lambda i: (tp(1048576, i) / tp(262144, i)) if 1048576 in g and 262144 in g and tp(1048576, i) and tp(262144, i) else None
        out[f"d{4 * od}_r{r}"] = {"bucket_over_gather": bucket_vs_gather, "bucket_over_best_cpu": bucket_vs_cpu,
                                  "crossover_bucket_beats_gather_from_B": xB, "gather_over_bucket_peak_mem": mem,
                                  "tp_1M_over_262k": {"bucket": sat("torch_gpu_bucket_e2e"), "gather": sat("torch_gpu_e2e"),
                                                      "graph": sat("torch_gpu_graph_e2e")}}
    honest = [c for c in cells if "skipped" not in c and not c["cheat"]]
    cheat = [c for c in cells if "skipped" not in c and c["cheat"] and c["n_compared"] >= 64]
    return {"per_config": out, "honest_invalid": sum(not c["valid"] for c in honest), "honest_cells": len(honest),
            "cheat_invalid_ge64": [sum(not c["valid"] for c in cheat), len(cheat)]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--budget", type=float, default=4.0)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    import torch
    configs = [(16, 64)] if a.quick else [(4, 4), (4, 16), (4, 64), (16, 4), (16, 16), (16, 64)]
    batches = [16384, 262144] if a.quick else [4 ** i for i in range(5, 11)]
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    cells = []
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            fh.write(json.dumps(row) + "\n")
            fh.flush()

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "configs": configs,
              "batches": batches, "names": NAMES, "budget_s": a.budget, "gpu_start": nvsmi(),
              "threads": os.environ.get("NUMBA_NUM_THREADS")})
        for od, r in configs:
            p = tt.random_policy(od, r, A_ACTIONS, seed=1000 * od + r)
            bes = {n: make(n, p) for n in NAMES}
            stopped = {}
            for B in batches:
                obs = np.random.default_rng(7 + r + B).integers(0, 65535, size=(B, od), dtype=np.uint16, endpoint=True)
                ref = tt.ref64_logits(p, obs[:1024])
                for n, be in bes.items():
                    base = {"kind": "cell", "impl": n, "cheat": be.cheat, "obs_dim": od, "d": 4 * od, "r": r, "B": B}
                    if n in stopped:
                        cells.append({**base, "skipped": f"budget {stopped[n]:.2f}s"})
                        emit(cells[-1])
                        continue
                    if n in GPU:
                        torch.cuda.synchronize()
                        torch.cuda.reset_peak_memory_stats()
                    psutil.cpu_percent(None)
                    try:
                        x = be.prepare(obs)
                        per, wall = time_cell(be, x, max_reps=2000)
                        acts = be.to_numpy(be.run(x))
                    except (RuntimeError, MemoryError) as e:
                        cells.append({**base, "skipped": f"error {type(e).__name__}: {str(e)[:160]}"})
                        emit(cells[-1])
                        stopped[n] = float("inf")
                        continue
                    nc, ties, mism = compare(acts, ref, TIE_GAP)
                    med = float(np.median(per))
                    row = {**base, "reps": len(per), "t_median_s": med, "obs_per_s_wall": B * len(per) / wall,
                           "n_compared": nc, "n_mismatch": mism, "valid": mism == 0,
                           "peak_gpu_mem": int(torch.cuda.max_memory_allocated()) if n in GPU else None,
                           "host_cpu_pct": psutil.cpu_percent(None)}
                    cells.append(row)
                    emit(row)
                    print(f"d{4 * od} r{r} B{B} {n:<28} {row['obs_per_s_wall'] / 1e3:>10.0f}k valid={row['valid']} "
                          f"mem={row['peak_gpu_mem']}", flush=True)
                    if med > a.budget:
                        stopped[n] = med
            for be in bes.values():
                be.close()
        summary = analyse(cells)
        emit({"kind": "summary", **summary})
    print(json.dumps({k: summary[k] for k in ("honest_invalid", "honest_cells", "cheat_invalid_ge64")}))
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
