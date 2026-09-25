"""U5 VRAM budget table and U6 throughput vs B6 fused numba, for the CUDA-graph closed loop.

  python -m primordial.nv.cudagraph.bench vram       [--fams linear,tt_digits] [--envs 4096,...]
  python -m primordial.nv.cudagraph.bench throughput [--fams ...] [--envs ...] [--reps 5]
  add --dry to print rows without the GPU lease or the rows file

World 4 (lane E's first world), E6's 8 train seeds, P = n_envs / 8 genomes (init + 3 mutations).

vram: per (family, n_envs, ticks_per_graph K in {1, T}) the peak torch allocation of one
  captured-graph rollout (torch.cuda.max_memory_allocated, reset before the build). Per-env
  bytes are fitted from the two largest points that fit; the envs that fit in 16 GiB (and in
  the free memory at measure time) are a LINEAR EXTRAPOLATION, labelled as such. OOM is a row.
throughput: exactness first -- every torch path's fitness and cells must equal B6's
  FusedRollout on the same genomes, else the cell has no speed. Then median wall of `reps`
  whole rollouts (host->device load and device->host result included) for B6 numba (thread
  count recorded), torch eager, graph K=1 and graph K=T; graph capture time separately.
  Every timing is taken inside bus.gpu_lease; a lost lease marks the cell INDETERMINATE.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

import numpy as np
import torch

from .graph import GraphRollout
from .rollout import TorchRollout, genomes

WORLD, K_SEEDS = 4, 8
GIB = 1 << 30
ROWS_DIR = "primordial/ledger/rows/U"


def _setup(fam: str, n_envs: int):
    from primordial.qd import e6_run as E6
    from primordial.qd import e7_run as E7
    g7 = E7.G7(WORLD, fam)
    P = max(1, n_envs // K_SEEDS)
    return g7, genomes(g7, P, seed=0), E6.TRAIN.copy(), P


def _sync():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def vram_cell(fam: str, n_envs: int, K: int | None) -> dict:
    g7, g, seeds, P = _setup(fam, n_envs)
    K = g7.T if K is None else K
    row = {"kind": "vram", "family": fam, "world": WORLD, "n_envs": P * K_SEEDS, "genomes": P,
           "ticks_per_graph": K, "T": g7.T, "device": torch.cuda.get_device_name()}
    torch.cuda.empty_cache()
    free0, total = torch.cuda.mem_get_info()
    torch.cuda.reset_peak_memory_stats()
    try:
        GraphRollout(g7, "cuda", ticks_per_graph=K).run(g, seeds)
        _sync()
        row.update(status="record", fits=True, peak_alloc_bytes=int(torch.cuda.max_memory_allocated()),
                   peak_reserved_bytes=int(torch.cuda.max_memory_reserved()))
    except torch.OutOfMemoryError as e:
        row.update(status="record", fits=False, error=str(e).splitlines()[0][:200])
    row.update(free_before_bytes=int(free0), total_bytes=int(total))
    torch.cuda.empty_cache()
    return row


def budget(rows: list[dict]) -> list[dict]:
    """Per (family, K): bytes/env from the two largest fitting points -> envs in 16 GiB and in free memory."""
    out = []
    for key in sorted({(r["family"], r["ticks_per_graph"]) for r in rows}):
        pts = sorted((r["n_envs"], r["peak_alloc_bytes"], r["free_before_bytes"]) for r in rows
                     if (r["family"], r["ticks_per_graph"]) == key and r.get("fits"))
        if len(pts) < 2:
            continue
        (n1, b1, _), (n2, b2, free) = pts[-2], pts[-1]
        per_env = (b2 - b1) / (n2 - n1)
        fixed = b2 - per_env * n2
        out.append({"kind": "vram_budget", "status": "record", "family": key[0], "ticks_per_graph": key[1],
                    "bytes_per_env": round(per_env, 1), "fixed_bytes": int(fixed),
                    "fit_from_envs": [n1, n2], "method": "linear extrapolation from two measured points",
                    "envs_in_16GiB_pred": int((16 * GIB - fixed) // per_env) if per_env > 0 else None,
                    "envs_in_free_pred": int((free - fixed) // per_env) if per_env > 0 else None})
    return out


def _median_wall(fn, reps: int) -> float:
    walls = []
    for _ in range(reps):
        _sync()
        t0 = time.perf_counter()
        fn()
        _sync()
        walls.append(time.perf_counter() - t0)
    return statistics.median(walls)


def throughput_cell(fam: str, n_envs: int, reps: int, b6: bool = True) -> dict:
    from primordial.soup.b6.fused import FusedRollout
    g7, g, seeds, P = _setup(fam, n_envs)
    n = P * K_SEEDS
    row = {"kind": "throughput", "family": fam, "world": WORLD, "n_envs": n, "genomes": P, "T": g7.T, "reps": reps,
           "numba_threads": int(os.environ.get("NUMBA_NUM_THREADS", "0")) or None,
           "torch_threads": torch.get_num_threads(), "device": torch.cuda.get_device_name()}
    eager = TorchRollout(g7, "cuda")
    ref_fit, ref_cells = eager.run(g, seeds)
    t0 = time.perf_counter()
    snap = eager.snapshot(g, seeds)
    _sync()
    row["torch_host_init_s"] = round(time.perf_counter() - t0, 4)        # untimed below, like B6's constructor
    t0 = time.perf_counter()
    gr1 = GraphRollout(g7, "cuda", ticks_per_graph=1)
    f1, c1 = gr1.run(g, seeds)
    row["capture_k1_s"] = round(time.perf_counter() - t0, 3)
    t0 = time.perf_counter()
    grT = GraphRollout(g7, "cuda", ticks_per_graph=g7.T)
    fT, cT = grT.run(g, seeds)
    row["capture_kT_s"] = round(time.perf_counter() - t0, 3)
    # timed unit: device copy of the initial state + T ticks + fitness/cells to host
    paths = {"torch_eager": lambda: (eager.restore(snap), eager.replay()),
             "graph_k1": lambda: (gr1.restore(snap), gr1.replay()),
             "graph_kT": lambda: (grT.restore(snap), grT.replay())}
    gr1.restore(snap)
    f1b, c1b = gr1.replay()
    exact = {"graph_k1": bool(np.array_equal(f1, ref_fit) and np.array_equal(c1, ref_cells)),
             "graph_kT": bool(np.array_equal(fT, ref_fit) and np.array_equal(cT, ref_cells)),
             "graph_k1_restore_path": bool(np.array_equal(f1b, ref_fit) and np.array_equal(c1b, ref_cells))}
    if b6:
        t0 = time.perf_counter()
        fr = FusedRollout(g7.spec, P, seeds, family=fam)
        row["b6_host_init_s"] = round(time.perf_counter() - t0, 4)
        row["b6_note"] = "B6 stops each env at its done tick; torch paths step all envs for T ticks"
        bf, bc = fr.run(g)[:2]
        exact["torch_eager_vs_b6"] = bool(np.array_equal(bf, ref_fit) and np.array_equal(bc, ref_cells))
        paths["b6_numba"] = lambda: fr.run(g)
    row["exact"] = exact
    if not all(exact.values()):
        row.update(status="record", speed_verdict="NO_SPEED_INEXACT")
        return row
    walls = {k: _median_wall(fn, reps) for k, fn in paths.items()}
    row["wall_s"] = {k: round(v, 5) for k, v in walls.items()}
    row["env_steps_per_s"] = {k: round(n * g7.T / v, 1) for k, v in walls.items()}
    if "b6_numba" in walls:
        row["speedup_vs_b6"] = {k: round(walls["b6_numba"] / v, 3) for k, v in walls.items() if k != "b6_numba"}
    row["status"] = "record"
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["vram", "throughput"])
    ap.add_argument("--fams", default="linear,tt_digits")
    ap.add_argument("--envs", default="")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--no-b6", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "1")))
    fams = a.fams.split(",")
    default = "4096,16384,65536,262144" if a.mode == "vram" else "1024,8192,65536"
    envs = [int(x) for x in (a.envs or default).split(",")]
    exp = "U5-vram-budget" if a.mode == "vram" else "U6-throughput-vs-b6"

    def cells(lease):
        rows = []
        for fam in fams:
            for n in envs:
                if a.mode == "vram":
                    for K in (1, None):
                        rows.append(vram_cell(fam, n, K))
                        print(json.dumps(rows[-1]), flush=True)
                else:
                    rows.append(throughput_cell(fam, n, a.reps, b6=not a.no_b6))
                    print(json.dumps(rows[-1]), flush=True)
                if lease is not None:
                    rows[-1]["gpu_lease_lost"] = bool(lease.get("lost"))
                    if lease.get("lost") and a.mode == "throughput":
                        rows[-1]["speed_verdict"] = "INDETERMINATE_LEASE_LOST"
        if a.mode == "vram":
            rows += budget(rows)
            for r in rows[-len(fams) * 2:]:
                if r["kind"] == "vram_budget":
                    print(json.dumps(r), flush=True)
        return rows

    if a.dry:
        for r in cells(None):
            r["status"] = "dev"
        return 0
    from primordial.bus import bus
    from primordial.fabric.rows import RowWriter
    with bus.gpu_lease(f"U {exp} {a.fams} envs={envs}", ttl_s=600, wait_s=900) as lease:
        load = bus.host_load() if hasattr(bus, "host_load") else None
        rows = cells(lease)
    os.makedirs(ROWS_DIR, exist_ok=True)
    with RowWriter(f"{ROWS_DIR}/{exp}.jsonl", exp, commit_every_s=10**9) as w:
        for r in rows:
            w.write({"exp_id": exp, "host_load_at_start": load, **r})
    return 0


if __name__ == "__main__":
    sys.exit(main())
