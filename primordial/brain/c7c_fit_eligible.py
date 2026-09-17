"""C7c: C7b re-registered with FIT-based eligibility decided on held-out seeds (bus hypothesis, C7c claim).

C7b (02f4fa5fa) FAILED because eligibility asked only for flip sensitivity and admitted targets the single-source
affine model can never fit. C7c decides eligibility on a SEPARATE seed set (ELIG_SEED0) that is never scored:
  world:  >= 1 regime switch inside the horizon
  target: observed non-charge feature, next-obs difference vs no_regime_flip in >= 50% of post-switch (env, tick),
          AND PlasticAffine in the no_regime_flip world surprises <= 2 times after its first fit (the model FITS).
Scoring runs on fresh RECORD seeds with C7b's exact learners, probe and per-target measures.

usage: python -m primordial.brain.c7c_fit_eligible [--worlds ...] [--n 512]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import time

import numpy as np

from primordial.brain import affine_plastic as ap
from primordial.brain.c7b_regime_plastic import HOT, SENS_MIN, DigitTT, drive, git_sha, score, trajectory

EXP_ID = "C7c-fit-eligible-plasticity"
CLEAN = (30, 45, 71, 107, 173, 195, 222, 228, 233, 248, 261, 281, 359, 380)
CORRUPTED = (46, 60, 115, 168, 235, 255, 271, 300, 389, 428, 440, 494, 497, 512, 527, 532, 599, 612, 649, 678, 699, 730)
RECORD_SEED0 = 90000
ELIG_SEED0 = 91000
FIT_MAX_NULL_SURPRISES = 2


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default=",".join(str(g) for g in CLEAN + CORRUPTED))
    p.add_argument("--n", type=int, default=512)
    p.add_argument("--tag", default="run")
    a = p.parse_args(argv)
    from primordial.soup.b1.common import make_world            # lane B, read-only

    rec_seeds = np.arange(RECORD_SEED0, RECORD_SEED0 + a.n, dtype=np.int64)
    elig_seeds = np.arange(ELIG_SEED0, ELIG_SEED0 + a.n, dtype=np.int64)
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

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "n": a.n,
              "record_seed0": RECORD_SEED0, "eligibility_seed0": ELIG_SEED0, "sens_min": SENS_MIN,
              "fit_max_null_surprises": FIT_MAX_NULL_SURPRISES, "worlds": a.worlds})
        for gs in [int(x) for x in a.worlds.split(",")]:
            m, wid = make_world(gs)
            T, P, r = m.horizon, m.regime_period, m.corrupt_rate
            n_sw = len(range(P, T, P)) if P else 0
            base = {"gen_seed": gs, "T": T, "period": P, "switches": n_sw, "corrupt_rate": r,
                    "stoch_rate": m.stoch_rate, "obs_delay": m.obs_delay}
            if n_sw < 1 or T <= P + 1:
                emit({"kind": "world", **base, "eligible_targets": [], "reason": "no switch in horizon"})
                continue
            # ---------------- eligibility on ELIG seeds only
            real_e = trajectory(m, wid, "", elig_seeds)
            null_e = trajectory(m, wid, "no_regime_flip", elig_seeds)
            D = real_e.shape[2]
            sens = (real_e[P + 1:] != null_e[P + 1:]).mean(axis=(0, 1))
            sensitive = [j for j in range(D - 1) if sens[j] >= SENS_MIN]
            fit_null = {}
            for j in sensitive:
                s_n, _, _ = drive(lambda: ap.PlasticAffine(seed=gs * 101 + j), null_e[:-1, :, :-1], null_e[1:, :, j],
                                  T, P, 0)
                fit_null[j] = int(sum(s_n[1:]))
            targets = [j for j in sensitive if fit_null[j] <= FIT_MAX_NULL_SURPRISES]
            emit({"kind": "world", **base, "D": D, "eligibility_sensitivity": np.round(sens, 4).tolist(),
                  "sensitive": sensitive, "eligibility_null_surprises": fit_null, "eligible_targets": targets})
            if not targets:
                continue
            # ---------------- record on fresh seeds
            real = trajectory(m, wid, "", rec_seeds)
            null = trajectory(m, wid, "no_regime_flip", rec_seeds)
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
                emit({"kind": "target", "gen_seed": gs, "j": j, "corrupt_rate": r,
                      "plastic_affine": score(s_aff, u_aff, T, P), "digit_tt": score(s_tt, u_tt, T, P),
                      "null_affine": {"surprises_after_first_fit": int(sum(s_null[1:])),
                                      "support": float(np.mean(u_null[1:]))},
                      "expected_support_corrupted": (1.0 - 1.0 / r) ** 2 if r else None,
                      "probe_affine": "CLEAN" if (s_aff, m_aff) == (s_aff2, m_aff2) else "LEAK",
                      "probe_leak": "CLEAN" if (s_leak, m_leak) == (s_leak2, m_leak2) else "LEAK",
                      "final_model": list(m_aff[-1]) if m_aff[-1] else None})

        tg = [x for x in rows if x["kind"] == "target"]
        worlds = [x for x in rows if x["kind"] == "world"]
        h1 = bool(tg) and all(t["plastic_affine"]["detected"] == t["plastic_affine"]["switches"] for t in tg)
        h2 = all(t["digit_tt"]["detected"] == 0 for t in tg)
        h3_cells = [(t["gen_seed"], t["j"], t["plastic_affine"]["support_in_regime"], t["expected_support_corrupted"])
                    for t in tg if t["expected_support_corrupted"] is not None]
        h3 = all(s is not None and abs(s - e) <= 0.05 for _, _, s, e in h3_cells)
        h4 = all(t["null_affine"]["surprises_after_first_fit"] <= 2 for t in tg)
        probe = all(t["probe_affine"] == "CLEAN" and t["probe_leak"] == "LEAK" for t in tg)
        status = ("INDETERMINATE" if len(tg) < 12 else "KILL" if not h1
                  else "PASS" if (h2 and h3 and h4 and probe) else "FAIL")
        emit({"kind": "summary", "worlds_scanned": len(worlds),
              "eligible_worlds": sum(bool(w["eligible_targets"]) for w in worlds), "eligible_targets": len(tg),
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
