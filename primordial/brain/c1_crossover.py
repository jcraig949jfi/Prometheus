"""C1: TT-policy contraction, CPU vs GPU crossover over batch size.

Every timed cell is validated: the actions the timed call returned are compared
with argmax of the float64 per-sample oracle on up to 1024 rows (near-ties
excluded). The instrument also cross-checks each backend's per-call timer
against wall clock with a final device sync; a timer that stops before the
work finishes is FLAGGED. Controls (cheat + positive) run in the same process.

usage: python -m primordial.brain.c1_crossover [--quick] [--budget S]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import pathlib
import subprocess
import time

import numpy as np
import psutil

from primordial.brain import tt_policy as tt

EXP_ID = "C1-tt-policy-crossover"
ROOT = pathlib.Path(__file__).resolve().parents[1]
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
A_ACTIONS = 8
TIE_GAP = 2e-2
LOGIT_TOL = 5e-3
TIMER_FLAG_RATIO = 0.67


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def nvsmi() -> str:
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                               "--format=csv,noheader"], capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:
        return "unavailable"


def compare(actions: np.ndarray, ref: np.ndarray, gap: float) -> tuple[int, int, int]:
    n = len(ref)
    top2 = np.sort(ref, axis=1)[:, -2:]
    tie = (top2[:, 1] - top2[:, 0]) < gap
    mism = int(((actions[:n] != ref.argmax(1)) & ~tie).sum())
    return n, int(tie.sum()), mism


def time_cell(be, x, min_time=0.3, min_reps=2, max_reps=5000):
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


def positive_control(names, emit) -> dict:
    out = {}
    rng = np.random.default_rng(1)
    for obs_dim in (4, 16):
        f = rng.integers(-8, 9, size=(4 * obs_dim, 16, A_ACTIONS)).astype(np.float64)
        p = tt.additive_policy(f, r=16)
        obs = rng.integers(0, 65535, size=(3000, obs_dim), dtype=np.uint16, endpoint=True)
        exact = additive = tt.additive_logits(f, obs)
        for name in names:
            be = tt.make(name, p)
            try:
                a = be.to_numpy(be.run(be.prepare(obs)))
                n, ties, mism = compare(a, additive, 0.5)
                try:
                    maxdiff = float(np.abs(be.logits(obs) - exact).max())
                except NotImplementedError:
                    maxdiff = None
            finally:
                be.close()
            ok = mism == 0 and (maxdiff is None or maxdiff == 0.0)
            row = {"kind": "positive_control", "impl": name, "obs_dim": obs_dim, "r": 16,
                   "n": n, "ties": ties, "mismatch": mism, "max_abs_logit_diff": maxdiff,
                   "exact": ok}
            emit(row)
            out[f"{name}/d{4 * obs_dim}"] = ok
    return out


def sweep(names, dims, ranks, batches, budget, emit):
    for obs_dim in dims:
        for r in ranks:
            p = tt.random_policy(obs_dim, r, A_ACTIONS, seed=1000 * obs_dim + r)
            bes = {n: tt.make(n, p) for n in names}
            rng = np.random.default_rng(7 + r)
            vobs = rng.integers(0, 65535, size=(512, obs_dim), dtype=np.uint16, endpoint=True)
            vref = tt.ref64_logits(p, vobs)
            for n, be in bes.items():
                try:
                    diff = float(np.abs(be.logits(vobs) - vref).max())
                except NotImplementedError:
                    diff = None
                emit({"kind": "logit_check", "impl": n, "obs_dim": obs_dim, "d": p.d, "r": r,
                      "max_abs_logit_diff": diff,
                      "within_tol": None if diff is None else diff <= LOGIT_TOL})
            gpu_state = nvsmi()
            stopped: dict[str, float] = {}
            for B in batches:
                obs = rng.integers(0, 65535, size=(B, obs_dim), dtype=np.uint16, endpoint=True)
                nv = min(B, 1024)
                ref = tt.ref64_logits(p, obs[:nv])
                for n, be in bes.items():
                    base = {"kind": "cell", "impl": n, "device": be.device, "cheat": be.cheat,
                            "obs_dim": obs_dim, "d": p.d, "r": r, "A": A_ACTIONS, "B": B,
                            "flops_per_obs": p.d * r * r + r * A_ACTIONS, "gpu_state": gpu_state}
                    if n in stopped:
                        emit({**base, "skipped": f"budget: median {stopped[n]:.2f}s > {budget}s at smaller B"})
                        continue
                    psutil.cpu_percent(None)
                    try:
                        x = be.prepare(obs)
                        per, wall = time_cell(be, x, max_reps=30 if be.cheat else 5000)
                        a = be.to_numpy(be.run(x))
                    except (RuntimeError, MemoryError) as e:
                        emit({**base, "skipped": f"error: {type(e).__name__}: {str(e)[:200]}"})
                        stopped[n] = float("inf")
                        continue
                    host_cpu = psutil.cpu_percent(None)
                    nc, ties, mism = compare(a, ref, TIE_GAP)
                    med = float(np.median(per))
                    ratio = float(per.sum() / wall)
                    emit({**base, "reps": len(per), "t_median_s": med,
                          "t_p10_s": float(np.percentile(per, 10)),
                          "t_p90_s": float(np.percentile(per, 90)),
                          "wall_s": wall, "obs_per_s_timer": B / med,
                          "obs_per_s_wall": B * len(per) / wall,
                          "timer_wall_ratio": ratio, "timer_flag": ratio < TIMER_FLAG_RATIO,
                          "n_compared": nc, "n_ties": ties, "n_mismatch": mism,
                          "valid": mism == 0, "host_cpu_pct": host_cpu,
                          "contended": host_cpu > 60.0})
                    if med > budget:
                        stopped[n] = med
            for be in bes.values():
                be.close()


def analyse(rows) -> dict:
    cells = [r for r in rows if r["kind"] == "cell" and "skipped" not in r]
    keys = sorted({(r["obs_dim"], r["r"]) for r in cells})
    cross = {}
    for od, r in keys:
        grid = {}
        for c in cells:
            if (c["obs_dim"], c["r"]) == (od, r):
                grid.setdefault(c["B"], {})[c["impl"]] = c
        Bs = sorted(grid)
        best_cpu = {}
        for B in Bs:
            cands = [(c["obs_per_s_wall"], n) for n, c in grid[B].items()
                     if n in tt.CPU_HONEST and c["valid"] and not c["timer_flag"]]
            best_cpu[B] = max(cands) if cands else (0.0, "none(all skipped)")
        for g in tt.GPU_HONEST:
            wins = []
            for B in Bs:
                c = grid[B].get(g)
                if c is None or not c["valid"] or c["timer_flag"]:
                    wins.append(None)
                else:
                    wins.append(c["obs_per_s_wall"] > best_cpu[B][0])
            xB = None
            for i, B in enumerate(Bs):
                if all(w for w in wins[i:] if w is not None) and wins[i]:
                    xB = B
                    break
            g1 = grid[Bs[0]].get(g)
            gl = grid[Bs[-1]].get(g)
            cross[f"d{4 * od}_r{r}/{g}"] = {
                "crossover_B": xB,
                "cpu_over_gpu_at_B%d" % Bs[0]: (best_cpu[Bs[0]][0] / g1["obs_per_s_wall"]) if g1 else None,
                "best_cpu_at_B%d" % Bs[0]: best_cpu[Bs[0]][1],
                "gpu_over_cpu_at_B%d" % Bs[-1]: (gl["obs_per_s_wall"] / best_cpu[Bs[-1]][0])
                if gl and best_cpu[Bs[-1]][0] else None,
                "best_cpu_at_B%d" % Bs[-1]: best_cpu[Bs[-1]][1],
            }
    honest = [c for c in cells if not c["cheat"]]
    skip = [c for c in cells if c["impl"] == "cheat_skip_half"]
    nosync = [c for c in cells if c["impl"] == "cheat_gpu_nosync"]
    resident = {(c["obs_dim"], c["r"], c["B"]): c for c in cells if c["impl"] == "torch_gpu_resident"}
    # A FALSE speed claim: the cheat's own timer says >= 1.5x the honest resident
    # path, but wall clock (with a final sync) says it is not really >= 1.2x faster.
    # Skipping the per-call sync is a real saving and is not counted here.
    inflated = [c for c in nosync
                if (k := (c["obs_dim"], c["r"], c["B"])) in resident
                and c["obs_per_s_timer"] > 1.5 * resident[k]["obs_per_s_wall"]
                and c["obs_per_s_wall"] <= 1.2 * resident[k]["obs_per_s_wall"]]
    controls = {
        "honest_cells": len(honest),
        "honest_invalid": sum(not c["valid"] for c in honest),
        "honest_timer_flagged": sum(c["timer_flag"] for c in honest),
        "skip_half_cells": len(skip),
        "skip_half_invalid": sum(not c["valid"] for c in skip),
        "skip_half_invalid_where_compared_ge_64": (
            sum(not c["valid"] for c in skip if c["n_compared"] >= 64),
            sum(1 for c in skip if c["n_compared"] >= 64)),
        "nosync_cells": len(nosync),
        "nosync_inflated_cells": len(inflated),
        "nosync_inflated_and_flagged": sum(c["timer_flag"] for c in inflated),
        "contended_cells": sum(c["contended"] for c in cells),
    }
    return {"crossover": cross, "controls": controls}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--budget", type=float, default=4.0)
    ap.add_argument("--tag", default="run")
    ap.add_argument("--dims", default="4,16", help="obs_dim list (d = 4*obs_dim)")
    ap.add_argument("--ranks", default="4,16,64")
    a = ap.parse_args(argv)
    names = list(tt.CPU_HONEST + tt.GPU_HONEST + tt.CHEATS)
    if a.quick:
        dims, ranks, batches = [4], [16], [1, 64, 4096]
    else:
        dims = [int(x) for x in a.dims.split(",")]
        ranks = [int(x) for x in a.ranks.split(",")]
        batches = [4 ** i for i in range(10)]
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    hot = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    rows = []
    header = {"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp,
              "threads": os.environ.get("NUMBA_NUM_THREADS"), "tie_gap": TIE_GAP,
              "logit_tol": LOGIT_TOL, "timer_flag_ratio": TIMER_FLAG_RATIO,
              "dims": dims, "ranks": ranks, "batches": batches, "A": A_ACTIONS,
              "budget_s": a.budget, "cpu_count": os.cpu_count(), "gpu_start": nvsmi()}
    with open(hot, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            if row["kind"] == "cell" and "skipped" not in row:
                print(f"d{row['d']:>2} r{row['r']:>2} B{row['B']:>6} {row['impl']:<20} "
                      f"{row['obs_per_s_wall']:>12.0f}/s valid={row['valid']} "
                      f"flag={row['timer_flag']} cpu={row['host_cpu_pct']:.0f}%", flush=True)
            elif row["kind"] != "cell":
                print(json.dumps(row), flush=True)
        emit(header)
        positive = positive_control(names, emit)
        sweep(names, dims, ranks, batches, a.budget, emit)
        summary = analyse(rows)
        summary["positive_control"] = positive
        emit({"kind": "summary", **summary})
    print(f"rows: {hot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
