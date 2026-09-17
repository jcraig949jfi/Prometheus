"""Run the lane-B C1 bounty head-to-head in ONE process with C's own instrument.

Cell: d64 (obs_dim 16), r64, A8, B4096, 3 threads. Policy and observations are drawn
exactly as C's sweep draws them (seed 1000*obs_dim + r; rng default_rng(7 + r); vobs 512,
then one obs draw per batch 1..1024 before the B4096 draw), so the cell is C's cell.

Per round, every backend (C's numba_par and np_bucket re-measured, B's candidates, the
cheat) is built, timed with C's time_cell, validated with C's compare against float64
ref64 argmax on 1024 rows, and closed. Order rotates each round to spread drift.

usage: python -m primordial.soup.bounty.run_c1 --rounds 5 --min-time 1.0 --out rows.jsonl
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

from primordial.brain import c1_crossover as c1
from primordial.brain import tt_policy as tt
from primordial.soup.bounty.c1_cpu import backends as b_backends

OBS_DIM, R, A, B = 16, 64, 8, 4096
C_BASELINES = ("numba_par", "np_bucket")


def c_cell_inputs():
    p = tt.random_policy(OBS_DIM, R, A, seed=1000 * OBS_DIM + R)
    rng = np.random.default_rng(7 + R)
    vobs = rng.integers(0, 65535, size=(512, OBS_DIM), dtype=np.uint16, endpoint=True)
    for b in (1, 4, 16, 64, 256, 1024):
        rng.integers(0, 65535, size=(b, OBS_DIM), dtype=np.uint16, endpoint=True)
    obs = rng.integers(0, 65535, size=(B, OBS_DIM), dtype=np.uint16, endpoint=True)
    return p, vobs, obs


def make(name, p, extra):
    return extra[name](p) if name in extra else tt.make(name, p)


def positive_control(names, extra, emit):
    rng = np.random.default_rng(1)
    f = rng.integers(-8, 9, size=(4 * OBS_DIM, 16, A)).astype(np.float64)
    p = tt.additive_policy(f, r=16)
    obs = rng.integers(0, 65535, size=(3000, OBS_DIM), dtype=np.uint16, endpoint=True)
    exact = tt.additive_logits(f, obs)
    for n in names:
        be = make(n, p, extra)
        try:
            a = be.to_numpy(be.run(be.prepare(obs)))
            nc, ties, mism = c1.compare(a, exact, 0.5)
            maxdiff = float(np.abs(be.logits(obs) - exact).max())
        finally:
            be.close()
        emit({"kind": "positive_control", "impl": n, "obs_dim": OBS_DIM, "r": 16, "n": nc,
              "mismatch": mism, "max_abs_logit_diff": maxdiff, "exact": mism == 0 and maxdiff == 0.0})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--min-time", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", help="comma list of impls (default: all)")
    a = ap.parse_args(argv)
    extra = b_backends()
    names = list(C_BASELINES) + [n for n in extra]
    if a.only:
        keep = a.only.split(",")
        names = [n for n in names if n in keep]
    rows = []
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            rows.append(row)
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
            if row["kind"] == "cell":
                print(f"round {row['round']} {row['impl']:<26} {row['obs_per_s_wall']:>10.0f}/s "
                      f"valid={row['valid']} flag={row['timer_flag']} cpu={row['host_cpu_pct']:.0f}%", flush=True)
            elif row["kind"] != "header":
                print(json.dumps(row), flush=True)

        emit({"kind": "header", "cell": {"obs_dim": OBS_DIM, "d": 4 * OBS_DIM, "r": R, "A": A, "B": B},
              "threads": os.environ.get("NUMBA_NUM_THREADS"), "rounds": a.rounds, "min_time_s": a.min_time,
              "tie_gap": c1.TIE_GAP, "logit_tol": c1.LOGIT_TOL, "c_source": "primordial/brain (read-only)"})
        honest = [n for n in names if not n.startswith("cheat")]
        positive_control(honest, extra, emit)
        p, vobs, obs = c_cell_inputs()
        vref = tt.ref64_logits(p, vobs)
        ref = tt.ref64_logits(p, obs[:1024])
        for n in names:
            be = make(n, p, extra)
            try:
                diff = float(np.abs(be.logits(vobs) - vref).max())
            finally:
                be.close()
            emit({"kind": "logit_check", "impl": n, "max_abs_logit_diff": diff, "within_tol": diff <= c1.LOGIT_TOL})
        for rnd in range(a.rounds):
            order = names[rnd % len(names):] + names[:rnd % len(names)]
            for n in order:
                be = make(n, p, extra)
                try:
                    x = be.prepare(obs)
                    psutil.cpu_percent(None)
                    per, wall = c1.time_cell(be, x, min_time=a.min_time)
                    host = psutil.cpu_percent(None)
                    act = be.to_numpy(be.run(x))
                finally:
                    be.close()
                nc, ties, mism = c1.compare(act, ref, c1.TIE_GAP)
                ratio = float(per.sum() / wall)
                emit({"kind": "cell", "round": rnd, "impl": n, "cheat": n.startswith("cheat"), "B": B,
                      "d": 4 * OBS_DIM, "r": R, "reps": len(per), "t_median_s": float(np.median(per)),
                      "wall_s": wall, "obs_per_s_wall": B * len(per) / wall,
                      "obs_per_s_timer": B / float(np.median(per)), "timer_wall_ratio": ratio,
                      "timer_flag": ratio < c1.TIMER_FLAG_RATIO, "n_compared": nc, "n_ties": ties,
                      "n_mismatch": mism, "valid": mism == 0, "host_cpu_pct": host, "contended": host > 60.0})
        cells = [r for r in rows if r["kind"] == "cell"]
        summ = {}
        for n in names:
            cs = [c for c in cells if c["impl"] == n]
            summ[n] = {"median_obs_per_s_wall": float(np.median([c["obs_per_s_wall"] for c in cs])),
                       "all_valid": all(c["valid"] for c in cs), "any_flag": any(c["timer_flag"] for c in cs),
                       "any_contended": any(c["contended"] for c in cs)}
        base = summ["numba_par"]["median_obs_per_s_wall"]
        for n in names:
            summ[n]["x_numba_par"] = summ[n]["median_obs_per_s_wall"] / base
        emit({"kind": "summary", "per_impl": summ,
              "c_recorded": {"numba_par": 101505.1, "np_bucket": 91777.8, "torch_gpu_e2e": 179408.3,
                             "torch_gpu_graph_e2e": 184425.2}})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
