"""C7d: C7c with the contrast bar grounded in the contrast learner's own chance rate (bus hypothesis, C7d claim).

Identical to C7c (primordial/brain/c7c_fit_eligible.py) -- worlds, learners, fit-based eligibility, leak probe -- except:
  * eligibility seeds 93000.., record seeds 92000.. (both new);
  * H2' is derived BEFORE scoring: on the eligibility seeds the digit TT runs on every eligible target and its surprises
    outside the 2-tick switch windows give a per-tick chance rate r; on the record seeds the TT's total in-window surprise
    count k must satisfy k <= Q99 = the 99th percentile of Poisson(r x record window ticks).

usage: python -m primordial.brain.c7d_chance_contrast [--worlds ...] [--n 512]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import math
import time

import numpy as np

from primordial.brain import affine_plastic as ap
from primordial.brain.c7b_regime_plastic import HOT, SENS_MIN, WINDOW, DigitTT, drive, git_sha, score, trajectory
from primordial.brain.c7c_fit_eligible import CLEAN, CORRUPTED, FIT_MAX_NULL_SURPRISES

EXP_ID = "C7d-chance-grounded-contrast"
RECORD_SEED0 = 92000
ELIG_SEED0 = 93000
Q = 0.99


def poisson_quantile(lam: float, q: float) -> int:
    k, cdf, term = 0, math.exp(-lam), math.exp(-lam)
    while cdf < q:
        k += 1
        term *= lam / k
        cdf += term
    return k


def window_ticks(T, P):
    return min(len(range(P, T, P)) * WINDOW, T - 1)


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
              "record_seed0": RECORD_SEED0, "eligibility_seed0": ELIG_SEED0, "q": Q, "worlds": a.worlds})
        elig = []                                                # (gs, j, T, P, D)
        tt_out_surprises = tt_out_ticks = 0
        # ================= phase 1: eligibility seeds only (fit rule + TT chance rate)
        for gs in [int(x) for x in a.worlds.split(",")]:
            m, wid = make_world(gs)
            T, P = m.horizon, m.regime_period
            n_sw = len(range(P, T, P)) if P else 0
            if n_sw < 1 or T <= P + 1:
                emit({"kind": "world", "gen_seed": gs, "switches": n_sw, "eligible_targets": [],
                      "reason": "no switch in horizon"})
                continue
            real_e = trajectory(m, wid, "", elig_seeds)
            null_e = trajectory(m, wid, "no_regime_flip", elig_seeds)
            D = real_e.shape[2]
            sens = (real_e[P + 1:] != null_e[P + 1:]).mean(axis=(0, 1))
            sensitive = [j for j in range(D - 1) if sens[j] >= SENS_MIN]
            fit_null, targets = {}, []
            for j in sensitive:
                s_n, _, _ = drive(lambda: ap.PlasticAffine(seed=gs * 101 + j), null_e[:-1, :, :-1], null_e[1:, :, j],
                                  T, P, 0)
                fit_null[j] = int(sum(s_n[1:]))
                if fit_null[j] <= FIT_MAX_NULL_SURPRISES:
                    targets.append(j)
            for j in targets:
                Y = real_e[1:, :, j]
                sc, mu = max(float(Y.std()), 1.0), float(Y.mean())
                s_tt, u_tt, _ = drive(lambda: DigitTT(D - 1, mu, sc, a.n), real_e[:-1, :, :-1], Y, T, P, 0)
                sc_tt = score(s_tt, u_tt, T, P)
                tt_out_surprises += sc_tt["surprises_outside_windows"]
                tt_out_ticks += (T - 2) - window_ticks(T, P)
                elig.append((gs, j, T, P, D))
            emit({"kind": "world", "gen_seed": gs, "switches": n_sw, "corrupt_rate": m.corrupt_rate, "D": D,
                  "eligibility_sensitivity": np.round(sens, 4).tolist(), "sensitive": sensitive,
                  "eligibility_null_surprises": fit_null, "eligible_targets": targets})
        # AMENDMENT (posted on the bus before any record run): a finite eligibility sample can show 0 chance surprises,
        # which would make the bar 0 again. Use the one-sided 95% upper bound of the Poisson count instead:
        # c_up = 0.5 * chi2.ppf(0.95, 2c + 2); rate = c_up / out-of-window ticks; bar = Q99 of Poisson(rate x window ticks).
        from scipy.stats import chi2
        c_up = 0.5 * float(chi2.ppf(0.95, 2 * tt_out_surprises + 2))
        rate = c_up / max(tt_out_ticks, 1)
        rec_window_ticks = sum(window_ticks(T, P) for _, _, T, P, _ in elig)
        lam = rate * rec_window_ticks
        q99 = poisson_quantile(lam, Q)
        emit({"kind": "h2_rule", "tt_out_surprises_elig": tt_out_surprises, "count_upper95": c_up,
              "tt_out_ticks_elig": tt_out_ticks, "rate_per_tick_upper": rate, "record_window_ticks": rec_window_ticks,
              "poisson_mean": lam, "q99_bar": q99, "amended": "upper-95% count bound, posted before record run"})
        # ================= phase 2: record seeds
        cache = {}
        for gs, j, T, P, D in elig:
            if gs not in cache:
                m, wid = make_world(gs)
                cache = {gs: (m, trajectory(m, wid, "", rec_seeds), trajectory(m, wid, "no_regime_flip", rec_seeds))}
            m, real, null = cache[gs]
            r = m.corrupt_rate
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
                  "probe_leak": "CLEAN" if (s_leak, m_leak) == (s_leak2, m_leak2) else "LEAK"})

        tg = [x for x in rows if x["kind"] == "target"]
        k_in = sum(t["digit_tt"]["detected"] for t in tg)
        h1 = bool(tg) and all(t["plastic_affine"]["detected"] == t["plastic_affine"]["switches"] for t in tg)
        h2 = k_in <= q99
        h3_cells = [(t["gen_seed"], t["j"], t["plastic_affine"]["support_in_regime"], t["expected_support_corrupted"])
                    for t in tg if t["expected_support_corrupted"] is not None]
        h3 = all(s is not None and abs(s - e) <= 0.05 for _, _, s, e in h3_cells)
        h4 = all(t["null_affine"]["surprises_after_first_fit"] <= 2 for t in tg)
        probe = all(t["probe_affine"] == "CLEAN" and t["probe_leak"] == "LEAK" for t in tg)
        status = ("INDETERMINATE" if len(tg) < 12 else "KILL" if not h1
                  else "PASS" if (h2 and h3 and h4 and probe) else "FAIL")
        emit({"kind": "summary", "eligible_targets": len(tg), "eligible_worlds": len({t["gen_seed"] for t in tg}),
              "switches_total": sum(t["plastic_affine"]["switches"] for t in tg),
              "affine_detected_total": sum(t["plastic_affine"]["detected"] for t in tg),
              "digit_tt_in_window_surprises": k_in, "h2_q99_bar": q99,
              "digit_tt_out_window_surprises_record": sum(t["digit_tt"]["surprises_outside_windows"] for t in tg),
              "H1": h1, "H2_chance_grounded": h2, "H3": h3,
              "H3_max_abs_deviation": max((abs(s - e) for _, _, s, e in h3_cells if s is not None), default=None),
              "H4": h4, "leak_probe": probe,
              "null_surprises_max": max((t["null_affine"]["surprises_after_first_fit"] for t in tg), default=None),
              "status_by_posted_rule": status})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
