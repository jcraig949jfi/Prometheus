"""C7e: the single post-correction C7 run, with eligibility decided from the genome lookup alone (bus hypothesis, C7e).

Eligibility (no sampling): primordial/soup/b7/c7_fixed_eligibility.json (lane B, B7b; read-only) + B's world genomes.
A register column of the FIXED layout (charge column last, d1f73fc3c) is eligible iff
  exact_on_reachable AND identifiable_by_odd_differences AND single-source fit in both regimes AND the same source
  column in both regimes AND (a, c) differ across regimes AND predicted old-model post-flip agreement < 0.25
  AND the world has >= 1 switch in its horizon.
Predicted agreement: the old map a_n*x + c_n and the new map a_f*x + c_f agree iff delta_a * x == delta_c (mod 2^16);
under a uniform 2-adic valuation of x that happens with probability 2^-(16 - v2(delta_a)) when v2(delta_a) <= v2(delta_c)
(or delta_c == 0), else 0. lane B's regime_changes_form is NOT used (mismatched both ways for single-source fits).

Learners, probe and per-target measures are C7c/C7d's; the digit-TT chance rate is calibrated on seeds never scored.

usage: python -m primordial.brain.c7e_genome_eligible [--n 512]
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import argparse
import json
import pathlib
import time

import numpy as np

from primordial.brain import affine_plastic as ap
from primordial.brain.c7b_regime_plastic import HOT, DigitTT, drive, git_sha, score, trajectory
from primordial.brain.c7d_chance_contrast import Q, poisson_quantile, window_ticks

EXP_ID = "C7e-genome-eligible-plasticity"
LOOKUP = pathlib.Path(__file__).resolve().parents[1] / "soup" / "b7" / "c7_fixed_eligibility.json"
RECORD_SEED0 = 94000
CALIB_SEED0 = 95000
MOD = 1 << 16
AGREE_MAX = 0.25


def v2(x: int) -> int:
    x %= MOD
    if x == 0:
        return 16
    v = 0
    while x % 2 == 0:
        x //= 2
        v += 1
    return v


def predicted_agreement(fn, ff) -> float:
    da = (fn["a"] - ff["a"]) % MOD
    dc = (ff["c"] - fn["c"]) % MOD
    return 2.0 ** -(16 - v2(da)) if (dc == 0 or v2(da) <= v2(dc)) else 0.0


def eligible_targets(make_world):
    doc = json.load(open(LOOKUP, encoding="utf-8"))
    out = []
    for gs, w in doc["worlds"].items():
        m, _ = make_world(int(gs))
        T, P = m.horizon, m.regime_period
        n_sw = len(range(P, T, P)) if P else 0
        if n_sw < 1:
            continue
        for col in w["register_columns"]:
            if not (col["exact_on_reachable"] is True and col["identifiable_by_odd_differences"] is True):
                continue
            fn, ff = col["fit"].get("normal"), col["fit"].get("flip")
            if fn is None or ff is None or fn["kind"] != "single" or ff["kind"] != "single":
                continue
            if fn["source_fixed_column"] != ff["source_fixed_column"]:
                continue
            if (fn["a"] % MOD, fn["c"] % MOD) == (ff["a"] % MOD, ff["c"] % MOD):
                continue
            agree = predicted_agreement(fn, ff)
            if agree >= AGREE_MAX:
                continue
            out.append({"gen_seed": int(gs), "j": int(col["fixed_column"]), "corrupt_rate": int(w["corrupt_rate"]),
                        "switches": n_sw, "source_fixed_column": int(fn["source_fixed_column"]),
                        "normal": [int(fn["a"]), int(fn["c"])], "flip": [int(ff["a"]), int(ff["c"])],
                        "predicted_agreement": agree})
    return sorted(out, key=lambda e: (e["gen_seed"], e["j"]))


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=512)
    p.add_argument("--only", default="", help="comma list of gen_seeds (smoke only)")
    p.add_argument("--tag", default="run")
    a = p.parse_args(argv)
    from primordial.soup.b1.common import make_world            # lane B, read-only

    elig = eligible_targets(make_world)
    if a.only:
        keep = {int(x) for x in a.only.split(",")}
        elig = [e for e in elig if e["gen_seed"] in keep]
    rec_seeds = np.arange(RECORD_SEED0, RECORD_SEED0 + a.n, dtype=np.int64)
    cal_seeds = np.arange(CALIB_SEED0, CALIB_SEED0 + a.n, dtype=np.int64)
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

        emit({"kind": "header", "exp_id": EXP_ID, "git": git_sha(), "ts": stamp, "n": a.n, "record_seed0": RECORD_SEED0,
              "calibration_seed0": CALIB_SEED0, "agree_max": AGREE_MAX, "q": Q, "lookup": str(LOOKUP.name),
              "eligible_count": len(elig), "eligible_worlds": len({e["gen_seed"] for e in elig}),
              "eligible_switches": sum(e["switches"] for e in elig), "eligible": elig, "only": a.only})

        worlds = {}
        for e in elig:
            gs = e["gen_seed"]
            if gs not in worlds:
                m, wid = make_world(gs)
                worlds[gs] = (m, wid)

        # ================= phase 1: digit-TT chance rate on calibration seeds (never scored)
        tt_out = tt_ticks = 0
        for gs in sorted(worlds):
            m, wid = worlds[gs]
            T, P = m.horizon, m.regime_period
            cal = trajectory(m, wid, "", cal_seeds)
            D = cal.shape[2]
            for e in (x for x in elig if x["gen_seed"] == gs):
                j = e["j"]
                Y = cal[1:, :, j]
                sc, mu = max(float(Y.std()), 1.0), float(Y.mean())
                s_tt, u_tt, _ = drive(lambda: DigitTT(D - 1, mu, sc, a.n), cal[:-1, :, :-1], Y, T, P, 0)
                tt_out += score(s_tt, u_tt, T, P)["surprises_outside_windows"]
                tt_ticks += (T - 2) - window_ticks(T, P)
        from scipy.stats import chi2
        c_up = 0.5 * float(chi2.ppf(0.95, 2 * tt_out + 2))
        rate = c_up / max(tt_ticks, 1)
        rec_window_ticks = sum(window_ticks(worlds[e["gen_seed"]][0].horizon, worlds[e["gen_seed"]][0].regime_period)
                               for e in elig)
        lam = rate * rec_window_ticks
        q99 = poisson_quantile(lam, Q)
        emit({"kind": "h2_rule", "tt_out_surprises_calibration": tt_out, "count_upper95": c_up,
              "tt_out_ticks_calibration": tt_ticks, "rate_per_tick_upper": rate,
              "record_window_ticks": rec_window_ticks, "poisson_mean": lam, "q99_bar": q99})

        # ================= phase 2: record seeds
        for gs in sorted(worlds):
            m, wid = worlds[gs]
            T, P, r = m.horizon, m.regime_period, m.corrupt_rate
            real = trajectory(m, wid, "", rec_seeds)
            null = trajectory(m, wid, "no_regime_flip", rec_seeds)
            D = real.shape[2]
            for e in (x for x in elig if x["gen_seed"] == gs):
                j = e["j"]
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
                      "expected_support": (1.0 - 1.0 / r) ** 2 if r else 1.0,
                      "lookup_fit": {"source": e["source_fixed_column"], "normal": e["normal"], "flip": e["flip"]},
                      "final_model": list(m_aff[-1]) if m_aff[-1] else None,
                      "probe_affine": "CLEAN" if (s_aff, m_aff) == (s_aff2, m_aff2) else "LEAK",
                      "probe_leak": "CLEAN" if (s_leak, m_leak) == (s_leak2, m_leak2) else "LEAK"})

        tg = [x for x in rows if x["kind"] == "target"]
        k_in = sum(t["digit_tt"]["detected"] for t in tg)
        h1 = bool(tg) and all(t["plastic_affine"]["detected"] == t["plastic_affine"]["switches"] for t in tg)
        h2 = k_in <= q99
        h3_cells = [(t["gen_seed"], t["j"], t["plastic_affine"]["support_in_regime"], t["expected_support"]) for t in tg]
        h3 = all(s is not None and abs(s - e) <= 0.05 for _, _, s, e in h3_cells)
        h4 = all(t["null_affine"]["surprises_after_first_fit"] <= 2 for t in tg)
        probe = all(t["probe_affine"] == "CLEAN" and t["probe_leak"] == "LEAK" for t in tg)
        status = ("INDETERMINATE" if len(tg) < 12 else "KILL" if not h1
                  else "PASS" if (h2 and h3 and h4 and probe) else "FAIL")
        emit({"kind": "summary", "eligible_targets": len(tg), "eligible_worlds": len({t["gen_seed"] for t in tg}),
              "switches_total": sum(t["plastic_affine"]["switches"] for t in tg),
              "affine_detected_total": sum(t["plastic_affine"]["detected"] for t in tg),
              "digit_tt_in_window_surprises": k_in, "h2_q99_bar": q99,
              "H1": h1, "H2_chance_grounded": h2, "H3": h3,
              "H3_max_abs_deviation": max((abs(s - e) for _, _, s, e in h3_cells if s is not None), default=None),
              "H4": h4, "leak_probe": probe,
              "null_surprises_max": max((t["null_affine"]["surprises_after_first_fit"] for t in tg), default=None),
              "status_by_posted_rule": status})
    print("rows:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
