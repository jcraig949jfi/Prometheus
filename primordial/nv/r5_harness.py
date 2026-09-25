"""E-R5-3: GPU-1..3 harness wiring over the W (nv/warp), U (nv/cudagraph) and P (nv/precision) MVP code (SWARM_R5 s3,
operator 19 s6). Each function is a job for primordial.nv.gpuq and runs in its nv venv (gw-venv is never a GPU venv).
Exactness first: every job emits its oracle row, and timing rows only when the oracle is exact. The arbiter holds the O5
lease for the whole child and stamps host fields (device, driver, VRAM before/peak, CPU load); each timing row here
carries the measurement fields (batch_size, transfer_included, warm_state, comparison_backend, exactness).

  GPU-1  venv w  lane B's world step: numba (prange over envs) at 1/2/4/8 threads vs Warp CUDA,
                 via nv.warp.crossover.bench_cell. Gate = W2's (sampled env trace hashes == wforge, done ticks, charge).
                 Warp's wall INCLUDES the host->device action copy (h2d_s): state is not resident across calls here.
  GPU-2  venv u  the closed loop (brain forward -> action decode -> world update) on the GPU, via
                 nv.cudagraph.bench.throughput_cell: exactness of torch eager / graph K=1 / graph K=T vs B6 fused numba
                 first; torch walls include the initial-state copy to the device and fitness/cells back to the host;
                 B6 numba at 1/2/4/8 threads is the fair CPU comparator.
  GPU-3  venv p  fp32 vs fp16 via nv.precision.p4_cost: the fp64 oracle (clear-row agreement + skip-odd cheat) then timing.
                 The P MVP has NO resident fp16 closed loop: this path is the isolated end-to-end forward (host weights +
                 obs in, logits out), labelled resident=False. The resident canary is a PRODUCTION_CANDIDATE.

P-BUILD runs a 1-cell smoke of each through the queue; the real GPU-1..3 runs are pilot jobs (each <= 600 s leased).
No numba/torch/warp import happens at module import: thread counts must be set before numba loads.
"""
from __future__ import annotations

import os

MEASURE = ("batch_size", "transfer_included", "warm_state", "comparison_backend", "exactness")
THREADS = (1, 2, 4, 8)


def timing_row(question: str, backend: str, wall_s: float, batch_size: int, transfer_included: bool, warm_state: str,
               comparison_backend: str, exactness: str, **extra) -> dict:
    return {"kind": "timing", "question": question, "backend": backend, "wall_s": float(wall_s),
            "batch_size": int(batch_size), "transfer_included": bool(transfer_included), "warm_state": warm_state,
            "comparison_backend": comparison_backend, "exactness": exactness, **extra}


def _threads_env(threads) -> int:
    k = int(max(threads))
    os.environ["NUMBA_NUM_THREADS"] = str(k)                 # before numba loads (W's crossover defaults it to 1)
    os.environ["OMP_NUM_THREADS"] = str(k)
    return k


def gpu1_cell(emit, g: int = 4, n: int = 1024, threads=THREADS, reps: int = 3, checkpoint_path=None):
    kmax = _threads_env(threads)
    import numba
    from primordial.nv.warp import crossover as X
    gate = X.bench_cell(g, n, reps=1, devices=("cuda:0",))
    exact = "PASS" if gate["gate_ok"] else "FAIL"
    emit({"kind": "oracle", "question": "GPU-1", "world_seed": g, "batch_size": n, "gate": gate["gate"],
          "exactness": exact, "numba_threads_max": kmax})
    if exact != "PASS":
        return
    walls, last = {}, None
    for k in threads:
        if k > numba.config.NUMBA_NUM_THREADS:
            emit({"kind": "skip", "question": "GPU-1", "threads": k, "reason": "above NUMBA_NUM_THREADS"})
            continue
        numba.set_num_threads(k)
        row = X.bench_cell(g, n, reps=reps, devices=("cuda:0",))
        if not row["gate_ok"]:
            emit({"kind": "oracle", "question": "GPU-1", "threads": k, "gate": row["gate"], "exactness": "FAIL"})
            return
        walls[k], last = row["median_s"]["numba"], row
        emit(timing_row("GPU-1", f"numba_t{k}", walls[k], n, False, "warm", "warp_cuda", exact, threads=k,
                        world_seed=g, reps=reps, slot_steps=row["slot_steps"]))
    best = min(walls, key=walls.get)
    h2d = float(last["h2d_s"] or 0.0)
    warp = float(last["median_s"]["warp_cuda"]) + h2d
    emit(timing_row("GPU-1", "warp_cuda", warp, n, True, "warm", f"numba_t{best}", exact, kernel_s=warp - h2d,
                    h2d_s=h2d, world_seed=g, reps=reps, speedup_vs_best_numba=walls[best] / warp if warp > 0 else None))


def gpu2_cell(emit, fam: str = "linear", n_envs: int = 1024, threads=THREADS, reps: int = 3, checkpoint_path=None):
    _threads_env(threads)
    import numba
    from primordial.nv.cudagraph import bench as UB
    rows = {}
    for k in threads:
        numba.set_num_threads(k)
        row = UB.throughput_cell(fam, n_envs, reps, b6=True)
        exact = "PASS" if row.get("exact") and all(row["exact"].values()) else "FAIL"
        if not rows:
            emit({"kind": "oracle", "question": "GPU-2", "family": fam, "batch_size": row["n_envs"],
                  "exact": row.get("exact"), "exactness": exact})
        if exact != "PASS":
            return
        rows[k] = row
        emit(timing_row("GPU-2", "b6_numba", row["wall_s"]["b6_numba"], row["n_envs"], False, "warm", "graph_kT",
                        exact, threads=k, family=fam, reps=reps))
    best = min(rows, key=lambda k: rows[k]["wall_s"]["b6_numba"])
    r = rows[best]
    for path in ("torch_eager", "graph_k1", "graph_kT"):
        emit(timing_row("GPU-2", path, r["wall_s"][path], r["n_envs"], True, "warm", f"b6_numba_t{best}", "PASS",
                        family=fam, reps=reps, resident_closed_loop=True, capture_k1_s=r.get("capture_k1_s"),
                        capture_kT_s=r.get("capture_kT_s"),
                        speedup_vs_best_numba=r["wall_s"]["b6_numba"] / r["wall_s"][path] if r["wall_s"][path] else None))


def gpu3_cell(emit, family: str = "linear", n: int = 4096, precisions=("fp32", "fp16"), reps: int = 5,
              checkpoint_path=None):
    import numpy as np
    import torch
    torch.set_num_threads(1)
    from primordial.nv.precision import p4_cost as P4
    orc = {p: P4.oracle(family, p) for p in precisions}
    exact = {p: "PASS" if orc[p]["oracle_ok"] else "FAIL" for p in precisions}
    emit({"kind": "oracle", "question": "GPU-3", "family": family, "oracles": orc,
          "exactness": "PASS" if all(v == "PASS" for v in exact.values()) else "FAIL"})
    res = P4.time_cells((family,), tuple(precisions), n, reps)
    for p in precisions:
        ts = res["t_s"][(family, p)]
        other = "torch_fp32" if p != "fp32" else "torch_fp16"
        emit(timing_row("GPU-3", f"torch_{p}", float(np.median(ts)), n, True, "warm", other, exact[p], family=family,
                        precision=p, path="e2e_host", resident=False, reps=reps,
                        vram_peak_bytes=res["vram_peak_bytes"][(family, p)]))
    emit({"kind": "note", "question": "GPU-3", "resident_path": "NOT_IN_MVP",
          "detail": "the P MVP has no resident fp16 closed loop; timing is the isolated end-to-end forward; "
                    "the resident canary is a PRODUCTION_CANDIDATE"})
