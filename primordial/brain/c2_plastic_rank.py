"""C2: does a plastic TT rank track regime change?

World: batches of uniform base-16 digits (d=4); a fresh target function per
regime, plus noise. Worlds:
  real  targets exactly rank r* (orthogonal cores), r* cycling [1,4,2,8]
  soft  targets NOT exactly low rank: 8 separable terms weighted decay**c,
        decay cycling [0.3,0.8,0.5,0.95]; scored against the ORACLE rank = what the
        same memory charge keeps when rounding the true function
  null  every target rank 4, fake labels cycling [1,4,2,8] (rank must not follow labels)
The regime flag is exposed to every brain through observe_flag().

LEAK PROBE (scores C2): every brain runs (a) with the true flag, (b) the true
flag again (determinism floor) and (c) the flag shifted by half a period. An
honest brain's rank and error trajectories are bit-identical in (a),(b),(c);
any difference (a) vs (c) with (a) == (b) = LEAK. Tracking is scored on (c) only.
One-sided: invariance proves the brain ignores THIS channel, nothing more.

usage: python -m primordial.brain.c2_plastic_rank [--dev] [--seeds 0,1,2]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import pathlib
import subprocess
import time

import numpy as np
from scipy.stats import spearmanr

from primordial.brain import plastic as pl

EXP_ID = "C2-plastic-rank"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
ROOT = pathlib.Path(__file__).resolve().parents[1]
D = 4
NOISE = 0.1
RESPONSE_STEPS = 5
LAM, RMAX = 1e-4, 12          # must equal PlasticTTBrain defaults (asserted below)


class RegimeWorld:
    def __init__(self, specs, period, batch, seed, labels=None):
        self.period, self.batch, self.seed = period, batch, seed
        rng = np.random.default_rng([seed, 991])
        self.specs = specs
        self.targets = [pl.random_target(D, v, rng) if kind == "orth"
                        else pl.decaying_target(D, 8, v, rng) for kind, v in specs]
        self.oracle = [max(pl.oracle_ranks(t, LAM, RMAX)) for t in self.targets]
        self.label = labels or self.oracle
        self.T = len(specs) * period

    def regime(self, t: int) -> int:
        return min(max(t, 0) // self.period, len(self.specs) - 1)

    def step(self, t: int):
        rng = np.random.default_rng([self.seed, t])
        X = rng.integers(0, 16, size=(self.batch, D), dtype=np.uint8)
        y = pl.tt_eval(self.targets[self.regime(t)], X) + NOISE * rng.standard_normal(self.batch)
        return X, y


def make_world(name, seed, P, batch):
    if name == "real":
        return RegimeWorld([("orth", r) for r in [1, 4, 2, 8] * 2], P, batch, seed)
    if name == "soft":
        return RegimeWorld([("decay", v) for v in [0.3, 0.8, 0.5, 0.95] * 2], P, batch, seed + 3000)
    if name == "null":
        return RegimeWorld([("orth", 4)] * 8, P, batch, seed + 5000, labels=[1, 4, 2, 8] * 2)
    raise ValueError(name)


def run(make_brain, world: RegimeWorld, flag_shift: int) -> dict:
    b = make_brain()
    assert (b.lam, b.rmax) == (LAM, RMAX) or not b.plastic
    R = np.zeros((world.T, D - 1), np.int16)
    E = np.zeros(world.T)
    S = np.zeros(world.T, bool)
    for t in range(world.T):
        X, y = world.step(t)
        b.observe_flag(world.regime(t + flag_shift))
        pred = b.predict(X)
        E[t] = np.mean((pred - y) ** 2)
        b.adapt_batch(X, y, pred)
        S[t] = b.surprised
        R[t] = pl.ranks(b.cores)
    return {"ranks": R, "mse": E, "surprise": S, "name": b.name}


def _rho(a, b):
    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return float(spearmanr(a, b).statistic)


def score(tr: dict, world: RegimeWorld) -> dict:
    P = world.period
    steady_mean, steady_max, excess = [], [], []
    for i in range(len(world.specs)):
        sl = slice(i * P + P // 2, (i + 1) * P)
        steady_mean.append(float(tr["ranks"][sl].mean()))
        steady_max.append(float(np.median(tr["ranks"][sl].max(axis=1))))
        excess.append(float(tr["mse"][sl].mean() - NOISE ** 2))
    starts = [i * P for i in range(1, len(world.specs))]
    responded = [bool(tr["surprise"][s:s + RESPONSE_STEPS].any()) for s in starts]
    near = np.zeros(world.T, bool)
    for s in starts:
        near[s:s + RESPONSE_STEPS] = True
    return {"rho_oracle": _rho(world.oracle, steady_mean),
            "rho_label": _rho(world.label, steady_mean),
            "steady_rank_spread": float(np.ptp(steady_mean)),
            "steady_mean_rank": steady_mean, "steady_max_rank": steady_max,
            "within1_of_oracle": float(np.mean([abs(m - r) <= 1 for m, r in zip(steady_max, world.oracle)])),
            "switch_response": float(np.mean(responded)),
            "false_surprises": int((tr["surprise"] & ~near).sum()),
            "steady_excess_mse": excess,
            "steady_excess_mse_mean": float(np.mean(excess))}


def same(a, b) -> bool:
    return (np.array_equal(a["ranks"], b["ranks"]) and np.array_equal(a["mse"], b["mse"])
            and np.array_equal(a["surprise"], b["surprise"]))


def params_of(ranks_row) -> int:
    dims = [1] + list(ranks_row) + [1]
    return sum(dims[k] * 16 * dims[k + 1] for k in range(D))


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


BRAINS = {
    "plastic": lambda s: (lambda: pl.PlasticTTBrain(d=D, seed=s)),
    "fixed8": lambda s: (lambda: pl.FixedTTBrain(rank0=8, d=D, seed=s)),
    "fixed2": lambda s: (lambda: pl.FixedTTBrain(rank0=2, d=D, seed=s)),
    "leak_flag": lambda s: (lambda: pl.LeakTTBrain(d=D, seed=s)),
}
PLAN = {"real": ["plastic", "fixed8", "fixed2", "leak_flag"],
        "soft": ["plastic", "fixed8", "leak_flag"],
        "null": ["plastic", "leak_flag"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--worlds", default="real,soft,null")
    ap.add_argument("--brains", default="")
    ap.add_argument("--period", type=int, default=120)
    ap.add_argument("--batch", type=int, default=512)
    ap.add_argument("--tag", default="run")
    a = ap.parse_args(argv)
    seeds = [100] if a.dev else [int(s) for s in a.seeds.split(",")]
    only = set(a.brains.split(",")) if a.brains else None
    P = a.period
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            if row["kind"] == "run":
                s = row["score_flag_shifted"]
                print(f"s{row['seed']} {row['world']:<4} {row['brain']:<9} {row['probe']:<6} "
                      f"oracle={row['oracle']} steady_max={s['steady_max_rank']} "
                      f"rho_o={s['rho_oracle']} rho_l={s['rho_label']} spread={s['steady_rank_spread']:.2f} "
                      f"resp={s['switch_response']:.2f} false={s['false_surprises']} "
                      f"exc={s['steady_excess_mse_mean']:.4f} params={row['steady_params_mean']:.0f} "
                      f"{row['wall_s']}s", flush=True)

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "seeds": seeds,
              "plan": PLAN, "period": P, "batch": a.batch, "d": D, "noise": NOISE, "lam": LAM,
              "rmax": RMAX, "dev": a.dev})
        for s in seeds:
            for wname in a.worlds.split(","):
                w = make_world(wname, s, P, a.batch)
                for bname in PLAN[wname]:
                    if only and bname not in only:
                        continue
                    t0 = time.perf_counter()
                    mk = BRAINS[bname](s)
                    tr_a = run(mk, w, 0)
                    tr_b = run(mk, w, 0)
                    tr_c = run(mk, w, P // 2)
                    deterministic = same(tr_a, tr_b)
                    invariant = same(tr_a, tr_c)
                    steady_params = float(np.mean([params_of(r) for i in range(len(w.specs))
                                                   for r in tr_c["ranks"][i * P + P // 2:(i + 1) * P]]))
                    emit({"kind": "trajectory", "seed": s, "world": wname, "brain": bname,
                          "condition": "flag_shifted", "ranks": tr_c["ranks"].tolist(),
                          "mse": [round(float(x), 6) for x in tr_c["mse"]],
                          "surprise": np.flatnonzero(tr_c["surprise"]).tolist()})
                    emit({"kind": "run", "seed": s, "world": wname, "brain": bname,
                          "specs": w.specs, "oracle": w.oracle, "label": w.label,
                          "deterministic": deterministic, "flag_invariant": invariant,
                          "probe": ("INDETERMINATE" if not deterministic
                                    else "CLEAN" if invariant else "LEAK"),
                          "score_flag_shifted": score(tr_c, w), "score_true_flag": score(tr_a, w),
                          "steady_params_mean": steady_params,
                          "wall_s": round(time.perf_counter() - t0, 2)})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
