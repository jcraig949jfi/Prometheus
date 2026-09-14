"""N4 timing: cuTensorNet (plan once, execute many) vs C1c torch_gpu_bucket_e2e, same policies and obs.

Two sides, one GPU:
  --side cutn   WSL ~/lab/nv-venv-t. Obs (uint16) go host->device, digits and one-hots are built on the
                device, reset_operands, contract, argmax on device, int32 actions device->host (e2e, like C1c).
                Planning (Network + contract_path) is timed separately per (obs_dim, r, B) shape.
  --side torch  Windows gw-venv. primordial.brain.tt_policy.TorchGpuBucketE2E, unchanged (read-only import).
  --side combine  joins the two JSONL files: exec ratio and planning break-even per shape.

Policies and obs are C1c's (tt.random_policy(od, r, 8, 1000*od + r); obs rng 7 + r + B), float32 on both
sides. Exactness before speed: every cell is compared with tt.ref64_logits on its first 1024 rows (C1
tie gap 2e-2); an invalid cell carries no speed claim. The cuTN stride-2 cheat runs at the first B.
Speed status: rows are "record" only with --lease (the O5 lease id); otherwise "dev" and speed is
INDETERMINATE.

usage: python -m primordial.nv.tensornet.n4_timing --side cutn|torch --out PATH [--quick] [--lease ID] [--git SHA]
       python -m primordial.nv.tensornet.n4_timing --side combine --cutn A.jsonl --torch B.jsonl [--out C.json]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import json
import pathlib
import subprocess
import time

import numpy as np

from primordial.brain import tt_policy as tt

EXP_ID = "N4-cutensornet-vs-torch-bucket-timing"
A_ACTIONS = 8
TIE_GAP = 2e-2          # primordial.brain.c1_crossover.TIE_GAP (not imported: that module is Windows-side)


def compare(actions, ref, gap=TIE_GAP):
    """C1's compare: (n compared, ties, mismatches outside ties)."""
    n = len(ref)
    top2 = np.sort(ref, axis=1)[:, -2:]
    tie = (top2[:, 1] - top2[:, 0]) < gap
    return n, int(tie.sum()), int(((actions[:n] != ref.argmax(1)) & ~tie).sum())


def time_cell(be, x, min_time=0.3, min_reps=2, max_reps=2000):
    """C1's time_cell: two warm runs, then reps until min_time."""
    for _ in range(2):
        be.run(x)
    be.sync()
    per = []
    t0 = time.perf_counter()
    while True:
        s = time.perf_counter()
        be.run(x)
        per.append(time.perf_counter() - s)
        if len(per) >= max_reps or (len(per) >= min_reps and time.perf_counter() - t0 >= min_time):
            break
    be.sync()
    return np.array(per), time.perf_counter() - t0


def nvsmi():
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader"],
                              capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:  # pragma: no cover
        return f"error {e}"


class CutnE2E:
    """One planned cuTensorNet network per (policy, B); run() is end to end like TorchGpuBucketE2E."""

    def __init__(self, p: tt.TTPolicy, B: int, stride: int = 1):
        import cupy as cp
        from primordial.nv.tensornet.tt_cutn import _cq, build_operands
        Network, _ = _cq()
        self.cp, self.p, self.stride, self.build = cp, p, stride, build_operands
        self.name = "cutn_e2e" if stride == 1 else "cheat_cutn_skip_half"
        self.cheat = stride != 1
        self.kept = list(range(0, p.d, stride))
        self.sh = cp.asarray([12, 8, 4, 0], dtype=cp.int32)
        self.eye = cp.eye(16, dtype=cp.float32)
        self.al, self.W = cp.asarray(p.alpha), cp.asarray(p.W)
        self.G = [cp.asarray(p.G[c]) for c in self.kept]
        t0 = time.perf_counter()
        self.net = Network(*self._ops(cp.zeros((B, p.obs_dim), dtype=cp.uint16)))
        self.path, info = self.net.contract_path()
        cp.cuda.Stream.null.synchronize()
        self.plan_s = time.perf_counter() - t0
        self.plan = {"opt_cost": float(info.opt_cost), "num_slices": int(info.num_slices),
                     "largest_intermediate": float(info.largest_intermediate)}

    def _ops(self, xdev):
        cp = self.cp
        dig = ((xdev.astype(cp.int32)[:, :, None] >> self.sh) & 15).reshape(xdev.shape[0], -1)
        return self.build(self.al, self.G, [self.eye[dig[:, c]] for c in self.kept], self.W)

    def prepare(self, obs):
        return np.ascontiguousarray(obs, dtype=np.uint16)

    def run(self, x):
        cp = self.cp
        self.net.reset_operands(*self._ops(cp.asarray(x))[:-1:2])     # tensors only, labels are fixed
        return cp.asnumpy(self.net.contract().argmax(1).astype(cp.int32))

    def to_numpy(self, a):
        return np.asarray(a, dtype=np.int32)

    def sync(self):
        self.cp.cuda.Stream.null.synchronize()

    def peak_mem(self):
        return int(self.cp.get_default_memory_pool().total_bytes())

    def close(self):
        self.net.free()
        self.cp.get_default_memory_pool().free_all_blocks()


class TorchBucket:
    def __init__(self, p, B):
        import torch
        torch.set_num_threads(1)
        self.torch = torch
        self.be = tt.TorchGpuBucketE2E(p)
        self.name, self.cheat, self.plan_s, self.plan = self.be.name, False, 0.0, None

    def prepare(self, obs):
        return self.be.prepare(obs)

    def run(self, x):
        return self.be.run(x)

    def to_numpy(self, a):
        return self.be.to_numpy(a)

    def sync(self):
        self.be.sync()

    def peak_mem(self):
        return int(self.torch.cuda.max_memory_allocated())

    def close(self):
        self.be.close()


def sweep(side: str, quick: bool, budget: float, emit) -> list[dict]:
    configs = [(4, 4)] if quick else [(4, 4), (4, 16), (4, 64), (16, 4), (16, 16), (16, 64)]
    batches = [1024, 4096] if quick else [4 ** i for i in range(5, 11)]
    cells = []
    for od, r in configs:
        p = tt.random_policy(od, r, A_ACTIONS, seed=1000 * od + r)
        stopped = False
        for bi, B in enumerate(batches):
            obs = np.random.default_rng(7 + r + B).integers(0, 65535, size=(B, od), dtype=np.uint16, endpoint=True)
            ref = tt.ref64_logits(p, obs[:1024])
            variants = [1] + ([2] if side == "cutn" and bi == 0 else [])
            for stride in variants:
                base = {"kind": "cell", "side": side, "obs_dim": od, "d": 4 * od, "r": r, "B": B, "stride": stride}
                if stopped and stride == 1:
                    cells.append({**base, "skipped": "budget"})
                    emit(cells[-1])
                    continue
                try:
                    if side == "torch":
                        import torch
                        torch.cuda.synchronize()
                        torch.cuda.reset_peak_memory_stats()
                    be = CutnE2E(p, B, stride) if side == "cutn" else TorchBucket(p, B)
                    x = be.prepare(obs)
                    per, wall = time_cell(be, x, min_time=0.1 if stride == 2 else 0.3)
                    acts = be.to_numpy(be.run(x))
                    mem = be.peak_mem()
                    be.close()
                except Exception as e:  # OOM / cuTensorNet errors end this impl for this config
                    cells.append({**base, "skipped": f"error {type(e).__name__}: {str(e)[:160]}"})
                    emit(cells[-1])
                    stopped = stopped or stride == 1
                    continue
                nc, ties, mism = compare(acts, ref)
                med = float(np.median(per))
                row = {**base, "impl": be.name, "cheat": be.cheat, "reps": len(per), "t_median_s": med,
                       "t_min_s": float(per.min()), "obs_per_s_wall": B * len(per) / wall,
                       "plan_s": be.plan_s, "plan": be.plan, "n_compared": nc, "n_ties": ties,
                       "n_mismatch": mism, "valid": mism == 0, "peak_mem_bytes": mem}
                cells.append(row)
                emit(row)
                print(f"{side} d{4 * od} r{r} B{B} s{stride} {row['obs_per_s_wall'] / 1e3:>9.0f}k obs/s "
                      f"plan {be.plan_s:.3f}s valid={row['valid']}", flush=True)
                if stride == 1 and med > budget:
                    stopped = True
    return cells


def combine(cutn_rows: list[dict], torch_rows: list[dict]) -> dict:
    """Per shape: exec ratio bucket/cutn (>1 = cuTN faster), plan break-even executions, validity."""
    key = lambda c: (c["d"], c["r"], c["B"])
    cu = {key(c): c for c in cutn_rows if c.get("kind") == "cell" and c.get("stride") == 1 and "skipped" not in c}
    to = {key(c): c for c in torch_rows if c.get("kind") == "cell" and "skipped" not in c}
    shapes = []
    for k in sorted(set(cu) & set(to)):
        c, t = cu[k], to[k]
        both = c["valid"] and t["valid"]
        gain = t["t_median_s"] - c["t_median_s"]
        shapes.append({"d": k[0], "r": k[1], "B": k[2], "valid_both": both,
                       "cutn_s": c["t_median_s"], "bucket_s": t["t_median_s"], "plan_s": c["plan_s"],
                       "bucket_over_cutn": t["t_median_s"] / c["t_median_s"] if both else None,
                       "breakeven_execs": (c["plan_s"] / gain) if both and gain > 0 else None})
    cheats = [c for c in cutn_rows if c.get("kind") == "cell" and c.get("stride") == 2 and "skipped" not in c]
    return {"shapes": shapes, "n_shapes": len(shapes),
            "cutn_faster_shapes": sum(bool(s["bucket_over_cutn"] and s["bucket_over_cutn"] > 1) for s in shapes),
            "invalid_honest": sum(not s["valid_both"] for s in shapes),
            "cheat_caught": [sum(not c["valid"] for c in cheats), len(cheats)]}


def _read(path):
    return [json.loads(x) for x in pathlib.Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--side", required=True, choices=["cutn", "torch", "combine"])
    ap.add_argument("--out")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--budget", type=float, default=4.0)
    ap.add_argument("--lease", default="")
    ap.add_argument("--git", default="")
    ap.add_argument("--cutn")
    ap.add_argument("--torch")
    a = ap.parse_args(argv)
    if a.side == "combine":
        res = {"exp_id": EXP_ID, "kind": "combine", **combine(_read(a.cutn), _read(a.torch))}
        text = json.dumps(res, indent=1)
        if a.out:
            pathlib.Path(a.out).write_text(text + "\n", encoding="utf-8", newline="\n")
        print(text)
        return 0
    status = "record" if a.lease else "dev"
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            fh.write(json.dumps({"exp_id": EXP_ID, "status": status, **row}) + "\n")
            fh.flush()

        emit({"kind": "header", "side": a.side, "git": a.git, "lease": a.lease or None,
              "speed": "LEASED" if a.lease else "INDETERMINATE", "ts": time.strftime("%Y%m%dT%H%M%S"),
              "gpu_start": nvsmi(), "pm_tag": os.environ.get("PM_TAG"), "threads": os.environ.get("OMP_NUM_THREADS")})
        cells = sweep(a.side, a.quick, a.budget, emit)
        emit({"kind": "footer", "gpu_end": nvsmi(), "cells": len(cells),
              "honest_invalid": sum(1 for c in cells if "skipped" not in c and not c["cheat"] and not c["valid"]),
              "cheat_invalid": [sum(1 for c in cells if "skipped" not in c and c["cheat"] and not c["valid"]),
                                sum(1 for c in cells if "skipped" not in c and c["cheat"])]})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
