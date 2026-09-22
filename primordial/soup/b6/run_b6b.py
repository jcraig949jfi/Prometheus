"""B6b harness: the fused rollout for lane C's linear and tt_feat families, judged against lane E7.

Per world in E's order (4, 1, 3) and family (linear, tt_feat), genomes = E7.G7 init + 50 mutations, P=128:
  H2 exact    fused fitness AND descriptor cells == E7.rollout (E's own numpy path) 128/128, on the
              train seeds (E7.TRAIN) AND on E6's 64 held-out seeds (E7.HELD64, what E8 uses)
  H1 speed    fused wall vs E7.rollout wall (the path E uses for these families), alternating reps,
              host CPU recorded (E8 runs on this host: speed is reported, not barred)
  world orc   16 recorded envs: B1 trace hash + final charge == wforge replay of the recorded actions
  brain orc   recorded action == argmax C fam.ref_logits on clear rows, 0 mismatches
  cheats      skip_lin world fails wforge replay >= 14/16; brain stride 2 mismatches >= 30% of clear rows
Regression: tt_digits through the OLD E5 tuple API still == E5.rollout (E8 is running on it).

usage: python -m primordial.soup.b6.run_b6b --worlds 4,1,3 --reps 3 --out rows.jsonl
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
from primordial.qd import e7_run as E7
from primordial.soup.b1.common import hash_log
from primordial.soup.b6.fused import FusedRollout

N_REC = 16


def host_cpu():
    try:
        import psutil
        return psutil.cpu_percent(interval=0.3)
    except Exception:
        return None


def world_oracle(spec, fr, done_tick, logs, rec):
    S, T, W = spec.mech.n_slots, spec.mech.horizon, spec.mech.act_width
    bad = 0
    for j, e in enumerate(rec):
        Te = int(done_tick[e])
        acts = np.zeros((T + 8, S, W), np.int64)
        acts[:Te] = logs["acts"][:Te, j]
        h_wf, ch_wf = E4.wforge_replay(spec, acts, int(fr.seeds_env[e]))
        h_fu = hash_log(logs["regs"][:Te, j], logs["charge"][:Te, j], logs["alive"][:Te, j], Te)
        ch_fu = np.clip(logs["charge"][Te - 1, j], 0, None)
        bad += (h_fu != h_wf) or not np.array_equal(ch_fu, ch_wf)
    return int(bad)


def brain_oracle(g7, fr, params, done_tick, logs, rec):
    checked = mism = 0
    for j, e in enumerate(rec):
        Te = int(done_tick[e])
        p = int(fr.genome_of_env[e])
        obs = logs["obs"][:Te, j].reshape(-1, g7.D)
        got = logs["idx"][:Te, j].reshape(-1)
        live = logs["alive"][:Te, j].reshape(-1)          # alive AFTER the step; rows of a slot that just died still count
        ref = g7.fam.ref_logits(g7.fam.one(params, p), obs)
        clear = gm.clear_rows(ref)
        checked += int(clear.sum())
        mism += int((ref.argmax(1) != got)[clear].sum())
    return checked, mism


def one(gs, fam_name, P, reps):
    g7 = E7.G7(gs, fam_name)
    rng = np.random.default_rng([6262, gs, list(gm.FAMILIES).index(fam_name)])
    g = g7.init(rng, P)
    for _ in range(50):
        g = g7.mutate(rng, g)
    out = {"world_seed": gs, "family": fam_name, "P": P, "D": g7.D, "T": g7.T, "S": g7.S, "W": g7.W,
           "genome_bytes": g7.fam.nbytes}
    for tag, seeds in (("train", E7.TRAIN), ("held64", E7.HELD64)):
        ref_fit, ref_cells, _, _ = E7.rollout(g7, g, seeds)
        fr = FusedRollout(g7.spec, P, seeds, family=fam_name)
        fr.run(g)                                                   # compile outside timing
        fit, cells, _, _, _ = fr.run(g)
        out[f"exact_fitness_{tag}"] = bool(np.array_equal(fit, ref_fit))
        out[f"exact_cells_{tag}"] = bool(np.array_equal(cells, ref_cells))
        out[f"fitness_mismatch_{tag}"] = int((fit != ref_fit).sum())
        out[f"cells_mismatch_{tag}"] = int((cells != ref_cells).sum())
        if tag == "train":
            cpu = host_cpu()
            t_np, t_fu = [], []
            for _ in range(reps):
                t0 = time.perf_counter(); E7.rollout(g7, g, seeds); t_np.append(time.perf_counter() - t0)
                t0 = time.perf_counter(); fr.run(g); t_fu.append(time.perf_counter() - t0)
            out.update({"host_cpu_pct_before": cpu, "reps": reps, "wall_e7_numpy_s": float(np.median(t_np)),
                        "wall_fused_s": float(np.median(t_fu)),
                        "speedup_vs_e7": float(np.median(t_np) / np.median(t_fu)),
                        "t_e7_numpy_s": t_np, "t_fused_s": t_fu})
            rec = np.random.default_rng(gs + 17).choice(fr.n, size=N_REC, replace=False)
            _, _, dt, lg, _ = fr.run(g, record=rec)
            out["world_oracle_bad"] = world_oracle(g7.spec, fr, dt, lg, rec)
            out["brain_clear_rows"], out["brain_mismatch"] = brain_oracle(g7, fr, g[0], dt, lg, rec)
            _, _, dtc, lgc, _ = fr.run(g, world_cheat="skip_lin", record=rec)
            out["cheat_skip_lin_world_bad"] = world_oracle(g7.spec, fr, dtc, lgc, rec)
            _, _, dtb, lgb, _ = fr.run(g, brain_stride=2, record=rec)
            cb, cm = brain_oracle(g7, fr, g[0], dtb, lgb, rec)
            out["cheat_brain_clear_rows"], out["cheat_brain_mismatch"] = cb, cm
            out["cheat_brain_mismatch_share"] = (cm / cb) if cb else None
    return out


def regression_tt_digits(gs=3, P=128):
    bs = E5.BrainSpec(gs)
    g = E5.init_brains(np.random.default_rng(1000 + gs), bs, P)
    ref_fit, ref_cells, _, _ = E5.rollout(bs, g)
    fr = FusedRollout(bs, P, E5.SEEDS)                              # default family, OLD 4-tuple API
    fit, cells, _, _, _ = fr.run(g)
    return {"world_seed": gs, "family": "tt_digits", "api": "E5 4-tuple (B6 contract)",
            "exact_fitness": bool(np.array_equal(fit, ref_fit)), "exact_cells": bool(np.array_equal(cells, ref_cells))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="4,1,3")
    ap.add_argument("--families", default="linear,tt_feat")
    ap.add_argument("--P", type=int, default=128)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    reg = regression_tt_digits()
    print("regression:", json.dumps(reg), flush=True)
    rows.append({"kind": "regression", **reg})
    for gs in (int(x) for x in a.worlds.split(",")):
        for fam in a.families.split(","):
            r = one(gs, fam, a.P, a.reps)
            rows.append({"kind": "cell", **r})
            print(f"w{gs} {fam:<8} exact train fit/cells={r['exact_fitness_train']}/{r['exact_cells_train']} "
                  f"held64={r['exact_fitness_held64']}/{r['exact_cells_held64']} "
                  f"speed={r['speedup_vs_e7']:.1f}x (cpu {r['host_cpu_pct_before']}%) "
                  f"world_bad={r['world_oracle_bad']}/16 brain={r['brain_mismatch']}/{r['brain_clear_rows']} | "
                  f"cheats skip_lin={r['cheat_skip_lin_world_bad']}/16 brain={r['cheat_brain_mismatch']}/"
                  f"{r['cheat_brain_clear_rows']}", flush=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
