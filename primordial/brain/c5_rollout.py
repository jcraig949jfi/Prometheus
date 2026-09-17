"""C5: does C4's numba forward_fast speed up lane E's closed-loop rollout end to end?

Runs lane E's OWN E5 rollout (primordial/qd/e5_run, imported read-only). The only change
is its module-level `forward`, swapped IN THIS PROCESS for genomes.TTDigits.forward_fast
(tt_digits is E5's genome). Nothing in primordial/qd is edited.

Per world (1-5), P=128 genomes from E's init_brains, E's 8 seeds:
  timing    rollout wall, numpy forward vs forward_fast(parallel) vs forward_fast(serial),
            3 alternating reps each
  equality  E's logged rollout rows (obs, genome, emitted idx); forward_fast re-run on the SAME
            obs; every mismatch checked against lane C ref64_logits for a near-tie
  cheat     forward_fast(cheat=True) (skip odd cores) vs ref64 argmax on sampled clear rows
  amdahl    in-process micro speedup of the forward and the brain share of the numpy rollout

usage: python -m primordial.brain.c5_rollout [--worlds 1,2,3,4,5] [--reps 3]
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

from primordial.brain import genomes as gm
from primordial.brain.tt_policy import TTPolicy, ref64_logits

EXP_ID = "C5-fast-population-forward"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = 128
CLEAR_REL = 1e-4          # E5 brain_oracle's clear-margin rule


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def clear(ref):
    top = np.sort(ref, 1)
    return (top[:, -1] - top[:, -2]) > CLEAR_REL * np.maximum(np.abs(top[:, -1]), 1e-30)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,2,3,4,5")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    import primordial.qd.e5_run as E5                      # lane E, read-only

    numpy_forward = E5.forward
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(json.dumps(row)[:700], flush=True)

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "P": P, "reps": a.reps,
              "seeds": [int(s) for s in E5.SEEDS], "threads": os.environ.get("NUMBA_NUM_THREADS")})
        for gs in [int(x) for x in a.worlds.split(",")]:
            bs = E5.BrainSpec(gs)
            fam = gm.TTDigits(bs.D, E5.A)
            g = E5.init_brains(np.random.Generator(np.random.PCG64([77, gs])), bs, P)

            def fast_par(gg, obs, gidx, skip_odd=False):
                return fam.forward_fast(gg[:3], obs, gidx, cheat=skip_odd, parallel=True)

            def fast_ser(gg, obs, gidx, skip_odd=False):
                return fam.forward_fast(gg[:3], obs, gidx, cheat=skip_odd, parallel=False)

            forwards = {"numpy": numpy_forward, "fast_par": fast_par, "fast_ser": fast_ser}
            for f in (fast_par, fast_ser):                 # compile outside timing
                E5.forward = f
                E5.rollout(bs, g)
            walls = {k: [] for k in forwards}
            fits = {}
            for _ in range(a.reps):
                for k, f in forwards.items():
                    E5.forward = f
                    t0 = time.perf_counter()
                    fit, cells, _, _ = E5.rollout(bs, g)
                    walls[k].append(time.perf_counter() - t0)
                    fits[k] = (fit, cells)
            med = {k: float(np.median(v)) for k, v in walls.items()}

            # brain share of the numpy rollout (same loop, forward timed alone)
            spent = [0.0]

            def timed_numpy(gg, obs, gidx, skip_odd=False):
                s = time.perf_counter()
                r = numpy_forward(gg, obs, gidx, skip_odd)
                spent[0] += time.perf_counter() - s
                return r

            E5.forward = timed_numpy
            t0 = time.perf_counter()
            E5.rollout(bs, g)
            share = spent[0] / (time.perf_counter() - t0)

            # equality on identical obs: E's logged rollout with E's numpy forward
            E5.forward = numpy_forward
            _, _, _, L = E5.rollout(bs, g, log=True)
            k = len(E5.SEEDS)
            live = L["live"]
            t_i, e_i, s_i = np.nonzero(live)
            obs = L["obs"][t_i, e_i, s_i]
            gidx = e_i // k
            e_idx = L["idx"][t_i, e_i, s_i]
            s0 = time.perf_counter()
            f_idx = fam.forward_fast(g[:3], obs, gidx, parallel=True)
            t_fast_rows = time.perf_counter() - s0
            s0 = time.perf_counter()
            numpy_forward(g, obs, gidx)
            t_numpy_rows = time.perf_counter() - s0
            mism = np.flatnonzero(f_idx != e_idx)
            clear_mism = 0
            for p in np.unique(gidx[mism]):
                rows = mism[gidx[mism] == p]
                pol = TTPolicy(g[0][p].astype(np.float64), g[1][p].astype(np.float64), g[2][p].astype(np.float64))
                clear_mism += int(clear(ref64_logits(pol, obs[rows].astype(np.uint16))).sum())

            # cheat control on sampled rows
            rng = np.random.default_rng(gs)
            pick = rng.choice(len(obs), size=min(512, len(obs)), replace=False)
            bad = fam.forward_fast(g[:3], obs[pick], gidx[pick], cheat=True, parallel=True)
            cheat_clear = cheat_wrong = 0
            for p in np.unique(gidx[pick]):
                rr = np.flatnonzero(gidx[pick] == p)
                pol = TTPolicy(g[0][p].astype(np.float64), g[1][p].astype(np.float64), g[2][p].astype(np.float64))
                ref = ref64_logits(pol, obs[pick][rr].astype(np.uint16))
                c = clear(ref)
                cheat_clear += int(c.sum())
                cheat_wrong += int(((bad[rr] != ref.argmax(1)) & c).sum())

            micro = t_numpy_rows / t_fast_rows
            amdahl = 1.0 / ((1 - share) + share / micro)
            emit({"kind": "world", "gen_seed": gs, "D": bs.D, "d": bs.d, "T": bs.T, "S": bs.S, "W": bs.W,
                  "rows_per_tick": P * k * bs.S, "wall_s": walls, "wall_median_s": med,
                  "speedup_fast_par": med["numpy"] / med["fast_par"], "speedup_fast_ser": med["numpy"] / med["fast_ser"],
                  "fitness_equal_genomes_par": int((fits["numpy"][0] == fits["fast_par"][0]).sum()),
                  "cells_equal_genomes_par": int((fits["numpy"][1] == fits["fast_par"][1]).sum()),
                  "brain_share_numpy": share, "micro_forward_speedup": micro, "amdahl_predicted": amdahl,
                  "amdahl_ratio_measured_over_predicted": (med["numpy"] / med["fast_par"]) / amdahl,
                  "live_rows": int(len(obs)), "row_mismatches": int(len(mism)),
                  "row_agreement": 1.0 - len(mism) / max(len(obs), 1), "clear_row_mismatches": clear_mism,
                  "cheat_clear_rows": cheat_clear, "cheat_wrong_clear_rows": cheat_wrong,
                  "cheat_wrong_frac": cheat_wrong / max(cheat_clear, 1)})
        E5.forward = numpy_forward
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
