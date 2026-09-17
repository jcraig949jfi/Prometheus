"""B6 harness: exactness, speed, world + brain oracles, cheats for the fused closed-loop rollout.

Per world (E5 BrainSpec, E5 init_brains with the B5/B5b seed, P=128, seeds 9100..9107):
  H2 exact    fused fitness AND descriptor cells == E5.rollout (numpy, E's own code) 128/128
  H1 speed    fused kernel wall vs B5b fast path loop wall (B5 split copy + C5 forward_fast),
              median of `reps` alternating reps; both exclude setup (stream seeding)
  world orc   16 recorded envs: B1 trace hash of the fused log + final charge == wforge replay of
              the recorded actions (E4.wforge_replay, read-only)
  brain orc   recorded obs rows -> recorded action == argmax C ref_logits on clear rows (gm.clear_rows)
  cheats      skip_lin world: wforge replay must mismatch >= 14/16; brain stride 2 (C's skip-odd):
              >= 30% of clear rows mismatch ref_logits argmax

usage: python -m primordial.soup.b6.run_b6 --worlds 1,2,3,4,5 --reps 5 --out rows.jsonl
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.qd import e4_run as E4
from primordial.qd import e5_run as E5
from primordial.soup.b1.common import hash_log
from primordial.soup.b5 import split
from primordial.soup.b6.fused import FusedRollout

N_REC = 16


def world_oracle(bs, fr, done_tick, logs, rec):
    """-> number of recorded envs whose fused trace hash or final charge disagrees with wforge."""
    k, S, T = fr.k, bs.S, bs.T
    bad = 0
    for j, e in enumerate(rec):
        Te = int(done_tick[e])
        acts = np.zeros((T + 8, S, bs.W), np.int64)        # pad: a diverged (cheat) world may run longer in wforge
        acts[:Te] = logs["acts"][:Te, j]
        h_wf, ch_wf = E4.wforge_replay(bs, acts, int(fr.seeds_env[e]))
        h_fu = hash_log(logs["regs"][:Te, j], logs["charge"][:Te, j], logs["alive"][:Te, j], Te)
        ch_fu = np.clip(logs["charge"][Te - 1, j], 0, None)
        bad += (h_fu != h_wf) or not np.array_equal(ch_fu, ch_wf)
    return int(bad)


def brain_oracle(bs, fr, g, done_tick, logs, rec):
    """-> (clear rows checked, mismatches) of recorded actions vs argmax C ref_logits."""
    fam = gm.TTDigits(bs.D, E5.A)
    checked = mism = 0
    for j, e in enumerate(rec):
        Te = int(done_tick[e])
        p = int(fr.genome_of_env[e])
        obs = logs["obs"][:Te, j].reshape(-1, bs.D)
        got = logs["idx"][:Te, j].reshape(-1)
        ref = fam.ref_logits(fam.one(g[:3], p), obs)
        clear = gm.clear_rows(ref)
        checked += int(clear.sum())
        mism += int((ref.argmax(1) != got)[clear].sum())
    return checked, mism


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,2,3,4,5")
    ap.add_argument("--P", type=int, default=128)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for gs in (int(x) for x in a.worlds.split(",")):
        bs = E5.BrainSpec(gs)
        g = E5.init_brains(np.random.default_rng(1000 + gs), bs, a.P)
        ref_fit, ref_cells, _, _ = E5.rollout(bs, g)                     # E's own numpy rollout
        fr = FusedRollout(bs, a.P, E5.SEEDS)
        fr.run(g)                                                           # compile outside timing
        fit, cells, done_tick, _, _ = fr.run(g)
        exact_fit = bool(np.array_equal(fit, ref_fit))
        exact_cells = bool(np.array_equal(cells, ref_cells))
        # ---- speed: alternating reps, kernel-only vs B5b fast loop
        fwd = split.make_forward("fast", bs)
        split.timed_rollout(bs, g, fwd)                                     # compile C5 kernel
        t_fast, t_fused = [], []
        for _ in range(a.reps):
            _, loop, _, _, _, _ = split.timed_rollout(bs, g, fwd)
            t_fast.append(loop)
            t0 = time.perf_counter()
            fr.run(g)
            t_fused.append(time.perf_counter() - t0)
        med_fast, med_fused = float(np.median(t_fast)), float(np.median(t_fused))
        # ---- oracles and cheats on 16 recorded envs
        rec = np.random.default_rng(gs).choice(fr.n, size=N_REC, replace=False)
        _, _, dt_h, logs_h, _ = fr.run(g, record=rec)
        world_bad = world_oracle(bs, fr, dt_h, logs_h, rec)
        b_checked, b_mism = brain_oracle(bs, fr, g, dt_h, logs_h, rec)
        _, _, dt_c, logs_c, _ = fr.run(g, world_cheat="skip_lin", record=rec)
        cheat_world_bad = world_oracle(bs, fr, dt_c, logs_c, rec)
        _, _, dt_b, logs_b, _ = fr.run(g, brain_stride=2, record=rec)
        cb_checked, cb_mism = brain_oracle(bs, fr, g, dt_b, logs_b, rec)
        row = {"world_seed": gs, "world_id": bs.wid, "P": a.P, "envs": fr.n, "T": bs.T, "S": bs.S, "D": bs.D,
               "d_cores": bs.d, "corrupt": bs.mech.corrupt_rate, "obs_delay": bs.mech.obs_delay,
               "stoch": bs.mech.stoch_rate, "delay": bs.mech.delay,
               "exact_fitness": exact_fit, "exact_cells": exact_cells,
               "fitness_mismatch_genomes": int((fit != ref_fit).sum()),
               "cells_mismatch_genomes": int((cells != ref_cells).sum()),
               "wall_fast_loop_s": med_fast, "wall_fused_s": med_fused, "speedup_vs_fast": med_fast / med_fused,
               "reps": a.reps, "t_fast_s": t_fast, "t_fused_s": t_fused,
               "episode_steps_per_s_fused": fr.n * bs.T / med_fused,
               "world_oracle_bad": world_bad, "brain_clear_rows": b_checked, "brain_mismatch": b_mism,
               "cheat_skip_lin_world_bad": cheat_world_bad,
               "cheat_brain_clear_rows": cb_checked, "cheat_brain_mismatch": cb_mism,
               "cheat_brain_mismatch_share": (cb_mism / cb_checked) if cb_checked else None,
               "recorded_envs": N_REC}
        rows.append(row)
        print(f"w{gs} exact fit={exact_fit} cells={exact_cells} speedup={row['speedup_vs_fast']:.2f}x "
              f"(fast {med_fast * 1e3:.1f}ms fused {med_fused * 1e3:.1f}ms) world_bad={world_bad}/16 "
              f"brain_mism={b_mism}/{b_checked} | cheats: skip_lin bad={cheat_world_bad}/16 "
              f"brain={cb_mism}/{cb_checked}", flush=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
