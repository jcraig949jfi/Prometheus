"""Run E1-E4 exactly as preregistered; write rows to ledgers/ and verdicts to RESULTS.json.

python run_all.py [--quick]   (--quick: tiny seed counts, for smoke only; never a result)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e1_feedback as e1  # noqa: E402
import e2_self_improver as e2  # noqa: E402
import e3_memory as e3  # noqa: E402
import e4_guard as e4  # noqa: E402
from stats import bootstrap_ci, mean, median  # noqa: E402

QUICK = "--quick" in sys.argv
LEDGER = HERE / ("ledgers_quick" if QUICK else "ledgers")


def write_rows(name, rows):
    LEDGER.mkdir(exist_ok=True)
    with open(LEDGER / f"{name}.jsonl", "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
            fh.flush()


def verdict(ok, indeterminate=False):
    return "INDETERMINATE" if indeterminate else ("SUPPORTED" if ok else "REFUTED")


# ------------------------------------------------------------------ E1
def _e1(args):
    return asdict(e1.run(*args))


def run_e1(pool):
    seeds = range(20 if QUICK else 200)
    jobs = [(k, r, s) for k in (2, 4, 8, 16) for r in e1.REGIMES for s in seeds]
    rows = pool.map(_e1, jobs, chunksize=50)
    write_rows("e1_feedback", rows)
    cell = {}
    for r in rows:
        cell.setdefault((r["k"], r["regime"]), []).append(r)
    summary = {}
    for (k, reg), rs in sorted(cell.items()):
        solved = [r["evaluations"] for r in rs if r["solved"]]
        summary[f"K{k}_{reg}"] = {
            "n": len(rs), "success_rate": len(solved) / len(rs),
            "median_evals_all": median([r["evaluations"] for r in rs]),
            "median_evals_solved": median(solved) if solved else None}
    med = lambda k, reg: summary[f"K{k}_{reg}"]["median_evals_all"]
    ratios = {k: med(k, "SCALAR") / med(k, "DENSE") for k in (4, 8, 16)}
    h1a = all(med(k, "DENSE") < med(k, "SCALAR") for k in (4, 8, 16))
    h1b = ratios[4] < ratios[8] < ratios[16]
    sr = lambda k, reg: summary[f"K{k}_{reg}"]["success_rate"]
    h1c = all(sr(k, "DENSE_MISATTRIBUTED") < sr(k, "SCALAR") for k in (4, 8, 16))
    return {"cells": summary, "ratio_scalar_over_dense": ratios,
            "H1a": verdict(h1a), "H1b": verdict(h1b), "H1c": verdict(h1c)}


# ------------------------------------------------------------------ E2
def _e2_chain(args):
    seed, mode, accounting = args
    thetas = e2.chain(seed, mode, generations=2 if QUICK else 4, accounting=accounting)
    test = e2.test_tasks()[: (8 if QUICK else None)]
    out = []
    for g, th in enumerate(thetas):
        u_test, real, dec = e2.utility(th, test, "honest")
        _, real_l, dec_l = e2.utility(th, e2.train_tasks(), "leaky") if accounting == "leaky" else (None, None, None)
        out.append({"seed": seed, "mode": mode, "accounting": accounting, "gen": g, "theta": asdict(th),
                    "U_test_honest": u_test, "real_evals_test": real,
                    "leaky_train_real_over_declared": (real_l / dec_l) if dec_l else None})
    return out


def run_e2(pool):
    seeds = range(3 if QUICK else 10)
    jobs = [(s, m, "honest") for s in seeds for m in ("RECURSIVE", "FIXED-META")]
    jobs += [(s, "RECURSIVE", "leaky") for s in seeds]
    rows = [r for chain in pool.map(_e2_chain, jobs, chunksize=1) for r in chain]
    write_rows("e2_self_improver", rows)
    G = 2 if QUICK else 4
    U = {}
    for r in rows:
        U[(r["mode"], r["accounting"], r["seed"], r["gen"])] = r
    u = lambda m, a, s, g: U[(m, a, s, g)]["U_test_honest"]
    rec = [[u("RECURSIVE", "honest", s, g) for g in range(G + 1)] for s in seeds]
    fix = [[u("FIXED-META", "honest", s, g) for g in range(G + 1)] for s in seeds]
    delta = lambda chain, g: chain[g - 1] - chain[g]
    d_med = {g: median([delta(c, g) for c in rec]) for g in range(1, G + 1)}
    d_med_fixed = {g: median([delta(c, g) for c in fix]) for g in range(1, G + 1)}
    h2a = sum(c[1] < c[0] for c in rec) >= (len(rec) - 1)
    h2b = d_med[2] < d_med[1]
    diff = [r[G] - f[G] for r, f in zip(rec, fix)]  # negative = recursive better
    lo, hi = bootstrap_ci(diff)
    h2c_ok = not (hi < 0)  # CI excluding 0 on the recursive side falsifies
    leaky_final = [U[("RECURSIVE", "leaky", s, G)] for s in seeds]
    lam_ok = sum(r["theta"]["lam"] >= 8 for r in leaky_final) >= (len(leaky_final) - 2)
    ratio_ok = all((r["leaky_train_real_over_declared"] or 0) >= 4 for r in leaky_final if r["theta"]["lam"] >= 8)
    d_leak = [U[("RECURSIVE", "leaky", s, G)]["U_test_honest"] - rec[i][G] for i, s in enumerate(seeds)]
    llo, lhi = bootstrap_ci(d_leak)  # negative = leaky-trained better under honest test
    h2d = lam_ok and ratio_ok and not (lhi < 0)
    return {"median_delta_recursive": d_med, "median_delta_fixed_meta": d_med_fixed,
            "U_test_median_by_gen_recursive": [median([c[g] for c in rec]) for g in range(G + 1)],
            "U_test_median_by_gen_fixed_meta": [median([c[g] for c in fix]) for g in range(G + 1)],
            "recursive_minus_fixed_at_G": {"median": median(diff), "ci95": [lo, hi]},
            "leaky_final_lambdas": [r["theta"]["lam"] for r in leaky_final],
            "leaky_real_over_declared": [r["leaky_train_real_over_declared"] for r in leaky_final],
            "leaky_minus_honest_test_at_G": {"median": median(d_leak), "ci95": [llo, lhi]},
            "H2a": verdict(h2a), "H2b": verdict(h2b), "H2c": verdict(h2c_ok),
            "H2d": verdict(h2d), "H2d_parts": {"lambda": lam_ok, "ratio": ratio_ok, "no_honest_gain": not (lhi < 0)}}


# ------------------------------------------------------------------ E3
def _e3(args):
    return asdict(e3.run(*args))


def run_e3(pool):
    seeds = range(20 if QUICK else 200)
    mems = ("NONE", "RAW", "DISTILLED_VERIFIED", "DISTILLED_UNVERIFIED")
    jobs = [(k, m, p, s) for k in ("COLOR", "SHAPE") for m in mems for p in (False, True) for s in seeds
            if not (p and not m.startswith("DISTILLED"))]
    rows = pool.map(_e3, jobs, chunksize=100)
    write_rows("e3_memory", rows)
    cell = {}
    for r in rows:
        cell.setdefault((r["kind"], r["memory"], r["poison"]), []).append(r)
    s = {f"{k}_{m}_{'POISON' if p else 'CLEAN'}": {
        "mean_test_acc": mean([r["test_acc"] for r in rs]),
        "mean_rules_admitted": mean([r["rules_admitted"] for r in rs]),
        "mean_interactions": mean([r["interactions"] for r in rs])} for (k, m, p), rs in sorted(cell.items())}
    a = lambda key: s[key]["mean_test_acc"]
    h3a = (a("COLOR_DISTILLED_VERIFIED_CLEAN") >= 0.9 and a("COLOR_RAW_CLEAN") <= 0.4
           and a("COLOR_NONE_CLEAN") <= 0.4)
    h3b = a("COLOR_DISTILLED_VERIFIED_POISON") - a("COLOR_DISTILLED_UNVERIFIED_POISON") >= 0.25
    h3c = (s["SHAPE_DISTILLED_VERIFIED_CLEAN"]["mean_rules_admitted"] <= 0.5
           and s["SHAPE_DISTILLED_UNVERIFIED_CLEAN"]["mean_rules_admitted"] == 6
           and a("SHAPE_DISTILLED_VERIFIED_CLEAN") >= a("SHAPE_NONE_CLEAN") - 0.05)
    return {"cells": s, "H3a": verdict(h3a), "H3b": verdict(h3b), "H3c": verdict(h3c)}


# ------------------------------------------------------------------ E4
def _e4(args):
    return asdict(e4.evolve(*args))


def run_e4(pool):
    seeds = range(20 if QUICK else 200)
    jobs = [(r, s, leak) for r in e4.REGIMES for leak in (True, False) for s in seeds]
    rows = pool.map(_e4, jobs, chunksize=10)
    write_rows("e4_guard", rows)
    cell = {}
    for r in rows:
        cell.setdefault((r["regime"], r["leak"]), []).append(r)
    s = {f"{reg}_{'LEAK' if lk else 'NOLEAK'}": {
        "mean_acc_c": mean([r["acc_c"] for r in rs]),
        "flag_rate": mean([1.0 if r["flagged"] else 0.0 for r in rs]),
        "hint_weight_nonzero_rate": mean([1.0 if r["weights"][0] != 0 else 0.0 for r in rs])}
        for (reg, lk), rs in sorted(cell.items())}
    c = lambda key: s[key]["mean_acc_c"]
    h4a = c("SINGLE_LEAK") <= 0.65
    h4b = c("DISJOINT_LEAK") >= 0.80
    h4c = c("POOLED_LEAK") <= 0.65
    det = s["SINGLE_LEAK"]["flag_rate"] >= 0.9 and s["DISJOINT_LEAK"]["flag_rate"] <= 0.05
    pos = all(c(f"{r}_NOLEAK") >= 0.80 for r in e4.REGIMES)
    return {"cells": s, "H4a": verdict(h4a), "H4b": verdict(h4b), "H4c": verdict(h4c),
            "leak_detector": verdict(det), "positive_control_noleak": verdict(pos)}


def main():
    t0 = time.time()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True,
                                cwd=HERE).stdout.strip())
    out = {"quick": QUICK, "head_sha": sha, "dirty_tree": dirty, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        for name, fn in (("E1", run_e1), ("E3", run_e3), ("E4", run_e4), ("E2", run_e2)):
            t = time.time()
            out[name] = fn(pool)
            out[name]["runtime_s"] = round(time.time() - t, 1)
            print(name, "done", out[name]["runtime_s"], "s", flush=True)
    out["runtime_s"] = round(time.time() - t0, 1)
    LEDGER.mkdir(exist_ok=True)
    (LEDGER / "RESULTS.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({k: {h: v for h, v in out[k].items() if h.startswith(("H", "leak", "positive"))}
                      for k in ("E1", "E2", "E3", "E4")}, indent=1))


if __name__ == "__main__":
    main()
