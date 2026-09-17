"""D1b: why D1's code learner got trapped -- rent valley, width valley, or sampling noise.

Exact cost (R uniform over all 256 values), an exhaustive single-move neighbourhood scan of the
D1 record elites, and an exact-cost climber with acceptance threshold eps from D1's start genomes.

usage: python -m primordial.lingua.d1b_run [--quick]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from primordial.lingua import signal as S

EXP = "D1b-code-learner-valleys"
ROOT = pathlib.Path(__file__).resolve().parents[1]
HOT = pathlib.Path(os.environ.get("PM_D_HOT", "C:/Users/jcrai/lab/pm-data/D"))
ALPHAS, BETAS, DELTA = (0.0, 0.1, 0.3, 0.6, 1.5), (0.0, 0.01), 1.0
EPS = (0.0, 0.01, 0.03, 0.1)
R_ALL = np.arange(S.N_R)


def exact_cost(K, E, D, a, b):
    return S.evaluate(K, E, D, R_ALL, a, b, DELTA)[0]


def best_single_move(k, enc, dec, a, b, cheat: str = "") -> dict:
    """Lowest exact cost over every single mutation. cheat='skip_enc' omits encoder moves."""
    k, enc, dec = int(k), np.asarray(enc, dtype=np.int64), np.asarray(dec, dtype=np.int64)
    base = float(exact_cost(np.array([k]), enc[None], dec[None], a, b)[0])
    best, move = np.inf, None
    for nk in (k - 1, k + 1):
        if 0 <= nk <= 8:
            c = float(exact_cost(np.array([nk]), (enc % (1 << nk))[None], dec[None], a, b)[0])
            if c < best:
                best, move = c, f"k->{nk}"
    ns = 1 << k
    D = np.repeat(dec[None], ns * S.N_ACT, 0)
    D[np.arange(ns * S.N_ACT), np.repeat(np.arange(ns), S.N_ACT)] = np.tile(np.arange(S.N_ACT), ns)
    c = exact_cost(np.full(len(D), k), np.repeat(enc[None], len(D), 0), D, a, b)
    j = int(np.argmin(c))
    if c[j] < best:
        best, move = float(c[j]), f"dec[{j // S.N_ACT}]={j % S.N_ACT}"
    if cheat != "skip_enc":
        for s in range(ns):
            E = np.repeat(enc[None], S.N_R, 0)
            E[R_ALL, R_ALL] = s
            c = exact_cost(np.full(S.N_R, k), E, np.repeat(dec[None], S.N_R, 0), a, b)
            j = int(np.argmin(c))
            if c[j] < best:
                best, move = float(c[j]), f"enc[{j}]={s}"
    return {"base": base, "best_neighbour": best, "improving": bool(best < base - 1e-12), "move": move}


def learn_exact(a, b, seed, gens, eps, lam=32):
    rng = np.random.Generator(np.random.PCG64(seed))
    k, enc, dec = S.random_genomes(rng, 1)          # same first draw as S.learn -> same start genome
    pc = float(exact_cost(k, enc, dec, a, b)[0])
    best = (pc, k, enc, dec)
    for _ in range(gens):
        ck, ce, cd = S.mutate(rng, np.repeat(k, lam), np.repeat(enc, lam, 0), np.repeat(dec, lam, 0))
        cc = exact_cost(ck, ce, cd, a, b)
        j = lam - 1 - int(np.argmin(cc[::-1]))
        if cc[j] <= pc + eps:
            k, enc, dec, pc = ck[j:j + 1], ce[j:j + 1], cd[j:j + 1], float(cc[j])
            if pc < best[0]:
                best = (pc, k, enc, dec)
    return best


def climb(args):
    a, b, s, eps, gens = args
    t0 = time.perf_counter()
    c, k, enc, dec = learn_exact(a, b, 1000 * s + 17, gens, eps)
    m_opt, c_opt = S.analytic_optimum(a, b, DELTA)
    return {"kind": "climb", "alpha": a, "beta": b, "run_seed": s, "eps": eps, "gens": gens,
            "cost": c, "gap": c - c_opt, "opt_m": m_opt, "k": int(k[0]), "entries": int(S.entries(enc)[0]),
            "yield": float(S.evaluate(k, enc, dec, R_ALL, a, b, DELTA)[1][0]),
            "wall_s": round(time.perf_counter() - t0, 2)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    gens, seeds = (300, (0,)) if args.quick else (4000, (0, 1, 2))
    tag = EXP + ("-quick" if args.quick else "")
    t_start = time.perf_counter()
    rows = []

    # controls: planted defects in the m=8 hand code
    k8, e8, d8 = S.hand_code(8)
    e_bad = e8.copy()
    e_bad[3 << S.SHIFT] = 0                      # one register of bucket 3 sent silent
    d_bad = d8.copy()
    d_bad[5] = 0                                 # symbol 5 decodes wrong
    for label, (e, d) in {"planted_enc": (e_bad, d8), "planted_dec": (e8, d_bad), "hand8_clean": (e8, d8)}.items():
        for cheat in ("", "skip_enc"):
            rows.append({"kind": "scan_control", "genome": label, "scanner": cheat or "full",
                         **best_single_move(k8, e, d, 0.0, 0.0, cheat)})

    # H1: scan the D1 record elites
    elites = json.loads((HOT / "D1-metered-channel.elites.json").read_text(encoding="utf-8"))
    for e in elites:
        m_opt, c_opt = S.analytic_optimum(e["alpha"], e["beta"], DELTA)
        sc = best_single_move(e["k"], e["enc"], e["dec"], e["alpha"], e["beta"])
        rows.append({"kind": "scan_elite", "alpha": e["alpha"], "beta": e["beta"], "run_seed": e["run_seed"],
                     "k": e["k"], "gap": sc["base"] - c_opt, **sc})

    jobs = [(a, b, s, eps, gens) for s in seeds for a in ALPHAS for b in BETAS for eps in EPS]
    with ProcessPoolExecutor(max_workers=3) as ex:
        rows += list(ex.map(climb, jobs))

    sc_rows = [x for x in rows if x["kind"] == "scan_elite" and x["gap"] > 0.02]
    cl = [x for x in rows if x["kind"] == "climb"]

    def esc(a, b, eps):
        rs = [x for x in cl if x["alpha"] == a and x["beta"] == b and x["eps"] == eps]
        return sum(x["gap"] <= 0.02 for x in rs), len(rs)

    ctrl = {(x["genome"], x["scanner"]): x["improving"] for x in rows if x["kind"] == "scan_control"}
    rent_cells = [(a, 0.01) for a in ALPHAS if a < 1.5]
    checks = {
        "H1_valley_elites_no_improving_single_move": all(not x["improving"] for x in sc_rows
                                                         if not (x["alpha"] == 0 and x["beta"] == 0)),
        "H1_noise_elites_have_improving_move": all(x["improving"] for x in sc_rows
                                                   if x["alpha"] == 0 and x["beta"] == 0),
        "H2_exact_eps0_escapes_00_and_0.6_0": all(esc(a, b, 0.0)[0] == esc(a, b, 0.0)[1]
                                                  for a, b in ((0.0, 0.0), (0.6, 0.0))),
        "H2_exact_eps0_trapped_rent_cells": all(esc(a, b, 0.0)[0] * 3 <= esc(a, b, 0.0)[1]
                                                for a, b in rent_cells),
        "H3_eps0.01_escapes_rent_cells": all(esc(a, b, 0.01)[0] * 3 >= 2 * esc(a, b, 0.01)[1]
                                             for a, b in rent_cells),
        "H4_width_cells_eps0_trapped": all(esc(a, 0.0, 0.0)[0] * 3 <= esc(a, 0.0, 0.0)[1] for a in (0.1, 0.3)),
        "C_planted_enc_found_full": ctrl[("planted_enc", "full")],
        "C_planted_enc_missed_by_skip_enc_cheat": not ctrl[("planted_enc", "skip_enc")],
        "C_planted_dec_found_both": ctrl[("planted_dec", "full")] and ctrl[("planted_dec", "skip_enc")],
        "C_clean_hand8_not_improvable": not ctrl[("hand8_clean", "full")],
        "C_alpha1.5_gap0_all_eps": all(x["gap"] <= 1e-9 for x in cl if x["alpha"] == 1.5),
    }
    summary = {"exp": tag, "checks": checks,
               "n_scanned_gap_gt_0.02": len(sc_rows),
               "escape_table": {f"a{a}_b{b}": {f"eps{e}": "%d/%d" % esc(a, b, e) for e in EPS}
                                for a in ALPHAS for b in BETAS},
               "wall_s": round(time.perf_counter() - t_start, 1)}
    rows_path = ROOT / "ledger" / "rows" / "D" / f"{tag}.jsonl"
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rows_path, "w", encoding="utf-8", newline="\n") as fh:
        for x in rows:
            fh.write(json.dumps(x, sort_keys=True) + "\n")
        fh.write(json.dumps({"kind": "summary", **summary}, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
