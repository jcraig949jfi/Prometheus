"""D1c (ANOM-1789415790377-0): is D1's code-learner trap operator bundling, a width valley, or a rent valley?

Prospective version of D1b's unscored post hoc: the exact-cost (1+32) climber at eps=0 from FRESH run
seeds, with three mutation operators -- BUNDLED (D1's 4 enc + 2 dec moves), SINGLE (1 enc + 1 dec), and
FROZEN (0 enc, 0 dec, no width moves: the cheat, children only relabel; it must never escape).
Predicate posted on the bus before the run (contract "D1c-operator-unbundling HYPOTHESIS").

usage: python -m primordial.cohorts.d.d1c_run [--quick]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from primordial.fabric.rows import RowWriter
from primordial.lingua import signal as S

EXP = "D1c-operator-unbundling"
ROOT = pathlib.Path(__file__).resolve().parents[2]
ALPHAS, BETAS, DELTA, EPS, LAM, ESC = (0.0, 0.1, 0.3, 0.6, 1.5), (0.0, 0.01), 1.0, 0.0, 32, 0.02
OPS = {"bundled": dict(n_enc=4, n_dec=2), "single": dict(n_enc=1, n_dec=1),
       "frozen": dict(n_enc=0, n_dec=0, p_k=0.0)}
R_ALL = np.arange(S.N_R)


def exact_cost(K, E, D, a, b):
    return S.evaluate(K, E, D, R_ALL, a, b, DELTA)[0]


def climb(job):
    a, b, s, op, gens = job
    t0 = time.perf_counter()
    rng = np.random.Generator(np.random.PCG64(7919 * s + 100003))
    k, enc, dec = S.random_genomes(rng, 1)
    pc = start = float(exact_cost(k, enc, dec, a, b)[0])
    best = (pc, k, enc, dec)
    accepts = 0
    for _ in range(gens):
        ck, ce, cd = S.mutate(rng, np.repeat(k, LAM), np.repeat(enc, LAM, 0), np.repeat(dec, LAM, 0), **OPS[op])
        cc = exact_cost(ck, ce, cd, a, b)
        j = LAM - 1 - int(np.argmin(cc[::-1]))
        if cc[j] <= pc + EPS:
            accepts += cc[j] < pc - 1e-12
            k, enc, dec, pc = ck[j:j + 1], ce[j:j + 1], cd[j:j + 1], float(cc[j])
            if pc < best[0]:
                best = (pc, k, enc, dec)
    c, bk, be, bd = best
    m_opt, c_opt = S.analytic_optimum(a, b, DELTA)
    return {"alpha": a, "beta": b, "run_seed": s, "op": op, "gens": gens, "start_cost": start,
            "cost": c, "gap": c - c_opt, "escaped": bool(c - c_opt <= ESC), "opt_m": m_opt,
            "k": int(bk[0]), "entries": int(S.entries(be)[0]), "improving_accepts": int(accepts),
            "yield": float(S.evaluate(bk, be, bd, R_ALL, a, b, DELTA)[1][0]),
            "wall_s": round(time.perf_counter() - t0, 2)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    gens, seeds = (200, range(2)) if args.quick else (4000, range(10))
    tag = EXP + ("-quick" if args.quick else "")
    t0 = time.perf_counter()
    jobs = [(a, b, s, op, gens) for op in OPS for a in ALPHAS for b in BETAS for s in seeds]
    rows = []
    with RowWriter(ROOT / "ledger" / "rows" / "D" / f"{tag}.jsonl", tag) as w:
        with ProcessPoolExecutor(max_workers=2) as ex:
            for r in ex.map(climb, jobs):
                status = "cheat" if r["op"] == "frozen" else ("control" if r["alpha"] == 1.5 else
                                                               ("dev" if args.quick else "record"))
                w.write({"status": status, "kind": "climb", **r})
                rows.append(r)

        def esc(op, a, b):
            rs = [r for r in rows if r["op"] == op and r["alpha"] == a and r["beta"] == b]
            return sum(r["escaped"] for r in rs), len(rs)

        n = len(seeds)
        checks = {
            "H1_single_escapes_00": esc("single", 0.0, 0.0)[0] >= 0.8 * n,
            "H2_bundled_trapped_00": esc("bundled", 0.0, 0.0)[0] <= 0.2 * n,
            "H3_single_trapped_width_cells": all(esc("single", a, 0.0)[0] <= 0.2 * n for a in (0.1, 0.3)),
            "H4_single_trapped_rent_cells": all(esc("single", a, 0.01)[0] <= 0.2 * n for a in ALPHAS if a < 1.5),
            "C_frozen_never_escapes": all(esc("frozen", a, b)[0] == 0 for a in ALPHAS for b in BETAS),
            "C_alpha1.5_real_ops_all_escape": all(esc(op, 1.5, b)[0] == n for op in ("bundled", "single")
                                                  for b in BETAS),
        }
        summary = {"exp": tag, "checks": checks, "gens": gens, "n_seeds": n,
                   "escape_table": {f"a{a}_b{b}": {op: "%d/%d" % esc(op, a, b) for op in OPS}
                                    for a in ALPHAS for b in BETAS},
                   "median_gap": {f"a{a}_b{b}": {op: float(np.median([r["gap"] for r in rows if r["op"] == op
                                                                     and r["alpha"] == a and r["beta"] == b]))
                                                 for op in OPS} for a in ALPHAS for b in BETAS},
                   "wall_s": round(time.perf_counter() - t0, 1)}
        w.write({"status": "record", "kind": "summary", **summary})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
