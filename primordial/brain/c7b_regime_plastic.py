"""C7b: does a structure-matched plastic learner track regime flips in lane B's world? (bus hypothesis, C7b claim)

B world (primordial/soup/b1/np_world.NpEncounter, read-only), zero actions, n envs with record seeds, and the same
world with cheat="no_regime_flip" as the null. Target selection is an instrument step (never shown to a learner):
observed non-charge feature j is ELIGIBLE iff its next value differs from the null world in >= 50% of post-switch
(env, tick) on the record seeds, in a world with >= 1 switch inside the horizon.

Learners, one batch = all envs at one tick: (obs_t[:, :-1], obs_{t+1}[:, j]):
  plastic_affine  affine_plastic.PlasticAffine (refit when exact-match support < 0.5)
  leak_affine     affine_plastic.LeakAffine (CHEAT: refits on regime-flag change)
  digit_tt        C2 plastic.PlasticTTBrain on hex digits of obs_t (surprise from C2's own rule)
LEAK PROBE: the regime flag (tick // period) is fed through observe_flag() true and shifted by period/2; a learner is
CLEAN iff its surprise/model traces are identical under both, LEAK otherwise.

usage: python -m primordial.brain.c7b_regime_plastic [--worlds ...] [--n 512]
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

from primordial.brain import affine_plastic as ap
from primordial.brain import plastic as pl
from primordial.brain.tt_policy import digits

EXP_ID = "C7b-structure-matched-plasticity"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C")
ROOT = pathlib.Path(__file__).resolve().parents[1]
CLEAN = (30, 107, 173, 195, 222, 228, 248, 261, 281)
CORRUPTED = (46, 60, 115, 168, 235, 255, 271, 440, 532)
SEED0 = 80000
WINDOW = 2
SENS_MIN = 0.5


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def trajectory(m, wid, cheat, seeds):
    from primordial.soup.b1.np_world import NpEncounter        # lane B, read-only
    w = NpEncounter(m, wid, cheat=cheat, with_obs=True)
    o = [w.reset(seeds)[:, 0].astype(np.int64)]
    a = np.zeros((len(seeds), m.n_slots, m.act_width), np.int32)
    for _ in range(m.horizon - 1):
        o.append(w.step(a)[0][:, 0].astype(np.int64))
    return np.stack(o)                                          # [T, n, D]


class DigitTT:
    """C2's plastic TT on hex digits behind the same batch interface."""

    def __init__(self, D, mean, scale, n):
        self.b = pl.PlasticTTBrain(d=4 * D, seed=0, window=8 * n)
        self.mean, self.scale = mean, scale
        self.surprised, self.support, self.model = False, 0.0, None

    def observe_flag(self, flag):
        pass

    def adapt_batch(self, X, y):
        Xd = digits(X.astype(np.uint16)).astype(np.uint8)
        yy = (y - self.mean) / self.scale
        pred = self.b.predict(Xd)
        self.support = 1.0 - float(np.mean((pred - yy) ** 2))
        self.b.adapt_batch(Xd, yy, pred)
        self.surprised = self.b.surprised
        self.model = tuple(pl.ranks(self.b.cores))


def drive(make, X, Y, T, P, shift):
    b = make()
    surp, sup, model = [], [], []
    for t in range(T - 1):
        b.observe_flag((t + 1 + shift) // P)                    # flag of the tick being predicted
        b.adapt_batch(X[t], Y[t])
        surp.append(bool(b.surprised))
        sup.append(float(b.support))
        model.append(b.model)
    return surp, sup, model


def score(surp, sup, T, P):
    switches = list(range(P, T, P))                              # pair (t -> t+1) crosses switch s when t+1 == s
    win = set()
    for s in switches:
        win.update(range(s - 1, s - 1 + WINDOW))
    detected = [any(surp[t] for t in range(s - 1, min(s - 1 + WINDOW, T - 1))) for s in switches]
    after = [t for t in range(1, T - 1) if surp[t] and t not in win]
    steady = [sup[t] for t in range(1, T - 1) if t not in win and not surp[t]]
    return {"switches": len(switches), "detected": int(sum(detected)),
            "surprises_outside_windows": len(after),
            "support_in_regime": float(np.mean(steady)) if steady else None}


def main(argv=None) -> int:
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--worlds", default=",".join(str(g) for g in CLEAN + CORRUPTED))
    ap_.add_argument("--n", type=int, default=512)
    ap_.add_argument("--tag", default="run")
    a = ap_.parse_args(argv)
    from primordial.soup.b1.common import make_world            # lane B, read-only

    seeds = np.arange(SEED0, SEED0 + a.n, dtype=np.int64)
    HOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    out = HOT / f"{EXP_ID}_{a.tag}_{stamp}.jsonl"
    rows = []
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        def emit(row):
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(json.dumps(row)[:360], flush=True)

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "n": a.n, "seed0": SEED0,
              "clean": CLEAN, "corrupted": CORRUPTED, "window": WINDOW, "sens_min": SENS_MIN,
              "surprise_support": ap.SURPRISE_SUPPORT})
        for gs in [int(x) for x in a.worlds.split(",")]:
            m, wid = make_world(gs)
            T, P, r = m.horizon, m.regime_period, m.corrupt_rate
            real = trajectory(m, wid, "", seeds)
            null = trajectory(m, wid, "no_regime_flip", seeds)
            D = real.shape[2]
            n_sw = len(range(P, T, P)) if P else 0
            sens = (real[P + 1:] != null[P + 1:]).mean(axis=(0, 1)) if P and T > P + 1 else np.zeros(D)
            targets = [j for j in range(D - 1) if n_sw >= 1 and sens[j] >= SENS_MIN]
            emit({"kind": "world", "gen_seed": gs, "T": T, "period": P, "switches": n_sw, "D": D, "corrupt_rate": r,
                  "stoch_rate": m.stoch_rate, "obs_delay": m.obs_delay, "sensitivity": np.round(sens, 4).tolist(),
                  "eligible_targets": targets})
            for j in targets:
                X, Y = real[:-1, :, :-1], real[1:, :, j]
                Xn, Yn = null[:-1, :, :-1], null[1:, :, j]
                mk_aff = lambda: ap.PlasticAffine(seed=gs * 101 + j)
                mk_leak = lambda: ap.LeakAffine(seed=gs * 101 + j)
                sc, mu = max(float(Y.std()), 1.0), float(Y.mean())
                mk_tt = lambda: DigitTT(D - 1, mu, sc, a.n)

                s_aff, u_aff, m_aff = drive(mk_aff, X, Y, T, P, 0)
                s_aff2, _, m_aff2 = drive(mk_aff, X, Y, T, P, P // 2)
                s_leak, _, m_leak = drive(mk_leak, X, Y, T, P, 0)
                s_leak2, _, m_leak2 = drive(mk_leak, X, Y, T, P, P // 2)
                s_tt, u_tt, _ = drive(mk_tt, X, Y, T, P, 0)
                s_null, u_null, _ = drive(mk_aff, Xn, Yn, T, P, 0)
                expected_support = (1.0 - 1.0 / r) ** 2 if r else None
                emit({"kind": "target", "gen_seed": gs, "j": j, "corrupt_rate": r,
                      "plastic_affine": score(s_aff, u_aff, T, P),
                      "digit_tt": score(s_tt, u_tt, T, P),
                      "null_affine": {"surprises_after_first_fit": int(sum(s_null[1:])),
                                      "support": float(np.mean(u_null[1:]))},
                      "expected_support_corrupted": expected_support,
                      "probe_affine": "CLEAN" if (s_aff, m_aff) == (s_aff2, m_aff2) else "LEAK",
                      "probe_leak": "CLEAN" if (s_leak, m_leak) == (s_leak2, m_leak2) else "LEAK",
                      "final_model": list(m_aff[-1]) if m_aff[-1] else None})

        tg = [r for r in rows if r["kind"] == "target"]
        worlds = [r for r in rows if r["kind"] == "world"]
        h1 = all(t["plastic_affine"]["detected"] == t["plastic_affine"]["switches"] for t in tg)
        h2 = all(t["digit_tt"]["detected"] == 0 for t in tg)
        h3_cells = [(t["gen_seed"], t["j"], t["plastic_affine"]["support_in_regime"], t["expected_support_corrupted"])
                    for t in tg if t["expected_support_corrupted"] is not None]
        h3 = all(s is not None and abs(s - e) <= 0.05 for _, _, s, e in h3_cells)
        h4 = all(t["null_affine"]["surprises_after_first_fit"] <= 2 for t in tg)
        probe = all(t["probe_affine"] == "CLEAN" and t["probe_leak"] == "LEAK" for t in tg)
        eligible = len(tg)
        status = ("INDETERMINATE" if eligible < 12 else "KILL" if not h1
                  else "PASS" if (h2 and h3 and h4 and probe) else "FAIL")
        emit({"kind": "summary", "eligible_targets": eligible,
              "eligible_worlds": sum(bool(w["eligible_targets"]) for w in worlds), "worlds_scanned": len(worlds),
              "switches_total": sum(t["plastic_affine"]["switches"] for t in tg),
              "affine_detected_total": sum(t["plastic_affine"]["detected"] for t in tg),
              "digit_tt_detected_total": sum(t["digit_tt"]["detected"] for t in tg),
              "H1": h1, "H2": h2, "H3": h3, "H3_cells": h3_cells, "H4": h4, "leak_probe": probe,
              "null_surprises_max": max((t["null_affine"]["surprises_after_first_fit"] for t in tg), default=None),
              "post_switch_refits_total": sum(t["plastic_affine"]["surprises_outside_windows"] for t in tg),
              "status_by_posted_rule": status})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
