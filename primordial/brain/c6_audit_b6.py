"""C6: audit lane B's B6 fused rollout (563faf437) OFF the conditions B tested.

Reference = lane E's own E5 numpy rollout (primordial/qd/e5_run.rollout, numpy forward).
Subject   = lane B's FusedRollout (primordial/soup/b6/fused.py).
Both imported read-only. E5 draws its seeds from the module constant e5_run.SEEDS; for the
held-out condition that constant is set in THIS process only (restored afterwards).

Conditions per world (1-5), compared per genome on fitness AND descriptor cell:
  a_elites_train     E5's saved evolved elites (16) on the train seeds
  b_elites_heldout   the same elites on E6's 64 held-out seeds 30000..30063
  c_p1 / c_p7        the first 1 / 7 elites on the train seeds (odd population sizes)
  c_mutated          128 E5 init genomes after 200 mutate_brains steps, train seeds
  d_ties             elites with Wo = 0 (every logit tied)                       [report-only]
  d_overflow         elites with G x 1e20 (float32 overflow -> inf/NaN)          [report-only]
Brain oracle on b: B6 recorded actions (16 envs) vs argmax lane C ref64_logits on clear rows.
Cheat control: B6 with brain_stride=2 vs honest E5 on a_elites_train.

usage: python -m primordial.brain.c6_audit_b6 [--worlds 1,2,3,4,5]
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

from primordial.brain.tt_policy import TTPolicy, ref64_logits

EXP_ID = "C6-audit-b6-fused-exactness"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
ELITES = pathlib.Path("C:/Users/jcrai/lab/pm-data/E/E5-qd-closed-loop-tt-brains")
ROOT = pathlib.Path(__file__).resolve().parents[1]
HELDOUT = np.arange(30000, 30064, dtype=np.int64)
CLEAR_REL = 1e-4


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def sub(g, n):
    return tuple(x[:n].copy() for x in g)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="1,2,3,4,5")
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    import primordial.qd.e5_run as E5                      # lane E, read-only
    from primordial.soup.b6.fused import FusedRollout      # lane B, read-only

    train = np.asarray(E5.SEEDS, np.int64).copy()
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    rows = []
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(json.dumps(row)[:400], flush=True)

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "train_seeds": train.tolist(),
              "heldout_seeds": [int(HELDOUT[0]), int(HELDOUT[-1])], "b6_commit": "563faf437"})

        def compare(bs, g, seeds, cond, stride=1, record=None):
            E5.SEEDS = seeds
            try:
                fit_e, cells_e, _, _ = E5.rollout(bs, g)
            finally:
                E5.SEEDS = train
            fr = FusedRollout(bs, len(g[0]), seeds)
            fit_b, cells_b, done_tick, logs, rec = fr.run(g, brain_stride=stride, record=record)
            fit_eq = fit_e == fit_b
            cell_eq = cells_e == cells_b
            both = fit_eq & cell_eq
            return {"condition": cond, "P": len(g[0]), "k": len(seeds), "stride": stride,
                    "genomes_exact": int(both.sum()), "fitness_equal": int(fit_eq.sum()),
                    "cells_equal": int(cell_eq.sum()),
                    "first_mismatch": (None if both.all() else
                                       {"genome": int(np.flatnonzero(~both)[0]),
                                        "fit_e5": int(fit_e[~both][0]), "fit_b6": int(fit_b[~both][0]),
                                        "cell_e5": int(cells_e[~both][0]), "cell_b6": int(cells_b[~both][0])})}, \
                (fr, logs, rec, done_tick)

        for gs in [int(x) for x in a.worlds.split(",")]:
            bs = E5.BrainSpec(gs)
            elites = bs.unpack(np.load(ELITES / f"full_w{gs}_elites.npy"))
            base = {"kind": "cell", "gen_seed": gs, "D": bs.D, "T": bs.T, "S": bs.S, "W": bs.W}

            r, _ = compare(bs, elites, train, "a_elites_train")
            emit({**base, **r})
            k_ho = len(HELDOUT)
            record = np.arange(0, 16 * k_ho, k_ho)            # env 0 of every elite (seed 30000)
            r, (fr, logs, rec, done_tick) = compare(bs, elites, HELDOUT, "b_elites_heldout", record=record)
            clear_rows = mism = 0
            for j, e in enumerate(rec):
                p = int(e) // k_ho
                pol = TTPolicy(elites[0][p].astype(np.float64), elites[1][p].astype(np.float64),
                               elites[2][p].astype(np.float64))
                t_end = int(done_tick[e])
                for s in range(bs.S):
                    obs = logs["obs"][:t_end, j, s]
                    if len(obs) == 0:
                        continue
                    ref = ref64_logits(pol, obs)
                    top = np.sort(ref, 1)
                    clear = (top[:, -1] - top[:, -2]) > CLEAR_REL * np.maximum(np.abs(top[:, -1]), 1e-30)
                    clear_rows += int(clear.sum())
                    mism += int(((ref.argmax(1) != logs["idx"][:t_end, j, s]) & clear).sum())
            emit({**base, **r, "brain_oracle_clear_rows": clear_rows, "brain_oracle_mismatches": mism})

            r, _ = compare(bs, sub(elites, 1), train, "c_p1")
            emit({**base, **r})
            r, _ = compare(bs, sub(elites, 7), train, "c_p7")
            emit({**base, **r})
            rng = np.random.Generator(np.random.PCG64([606, gs]))
            g = E5.init_brains(rng, bs, 128)
            for _ in range(200):
                g = E5.mutate_brains(rng, bs, g)
            r, _ = compare(bs, g, train, "c_mutated")
            emit({**base, **r, "max_abs_G": float(np.abs(g[1]).max())})

            ties = (elites[0].copy(), elites[1].copy(), np.zeros_like(elites[2]), elites[3].copy())
            r, _ = compare(bs, ties, train, "d_ties")
            emit({**base, **r})
            with np.errstate(over="ignore"):
                ovf = (elites[0].copy(), (elites[1].astype(np.float64) * 1e20).astype(np.float32), elites[2].copy(),
                       elites[3].copy())
            with np.errstate(all="ignore"):
                r, _ = compare(bs, ovf, train, "d_overflow")
            emit({**base, **r})

            r, _ = compare(bs, elites, train, "cheat_stride2", stride=2)
            emit({**base, **r})

        cells = [r for r in rows if r["kind"] == "cell"]
        core = [c for c in cells if c["condition"][0] in "abc"]
        core_exact = all(c["genomes_exact"] == c["P"] for c in core)
        oracle_ok = all(c["brain_oracle_mismatches"] == 0 and c["brain_oracle_clear_rows"] > 0
                        for c in cells if c["condition"] == "b_elites_heldout")
        cheat = [c for c in cells if c["condition"] == "cheat_stride2"]
        cheat_ok = all(c["P"] - c["genomes_exact"] >= 14 for c in cheat)
        d = {c["condition"] + f"_w{c['gen_seed']}": f"{c['genomes_exact']}/{c['P']}" for c in cells
             if c["condition"].startswith("d_")}
        status = ("PASS" if core_exact and oracle_ok and cheat_ok
                  else "KILL" if not core_exact else "INDETERMINATE")
        emit({"kind": "summary", "core_exact": core_exact, "oracle_ok": oracle_ok, "cheat_ok": cheat_ok,
              "cheat_mismatching_genomes": {f"w{c['gen_seed']}": c["P"] - c["genomes_exact"] for c in cheat},
              "report_only_d": d, "status_by_posted_rule": status,
              "core_cells": {f"{c['condition']}_w{c['gen_seed']}": f"{c['genomes_exact']}/{c['P']}" for c in core}})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
