"""THESEUS-23b: the composition wall, measured inside Theseus.

Prereg: roles/Theseus/prereg/2026-10-08_composition/PREREG.md.

Hestia (comms #1735) names a program-wide wall: engines find 1-part
mechanisms but never a 2-part mechanism whose parts are each worth nothing
alone. This module measures that property directly on substrate genomes.

For a genome G with n >= 2 rules and every split point s in 1..n-1:
  A = rules[:s], B = rules[s:], EMPTY = the same genome with one no-op rule
  f(X) = seed-0 fingerprint (34 dims), d = euclid_z distance (frozen v0_1 CAL)
  A_alone_nothing  d(f(A), f(EMPTY)) <= EPS
  B_alone_nothing  d(f(B), f(EMPTY)) <= EPS
  AB_something     d(f(G), f(EMPTY)) >  TAU
G is a COMPOSITION if some split satisfies all three. EPS = the median G0
replicate distance (1.63, the noise floor: "indistinguishable from doing
nothing"); TAU = tau_rep (4.31). Both are frozen from run v0_1.
Also recorded per genome: the best split's synergy ratio
  d(G, EMPTY) / max(d(A, EMPTY), d(B, EMPTY)).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import battery as bt  # noqa: E402
from . import rulers as ru  # noqa: E402

REF = "v0_1_2026-09-30"
NOOP = {"op": "recall", "src": [], "dst": 0, "p": [0.0], "prov": "noop"}
ARMS = ("D", "E", "S", "G", "B", "C", "P", "R", "A")
N_PER_ARM = 120

_CAL = None


def _init(cald):
    global _CAL
    _CAL = ru.Cal(cald)


def _with_rules(g, rules):
    h = copy.deepcopy(g)
    h["rules"] = copy.deepcopy(rules) if rules else [dict(NOOP)]
    return h


def _fp(g):
    return bt.fingerprint(g, _CAL.desc_scales, seed=0)["fp"]


def _d(a, b):
    return float(ru.dist_matrix(np.asarray(a)[None], np.asarray(b)[None], "euclid_z", _CAL)[0, 0])


def _job(args):
    g, eps, tau = args
    t0 = time.process_time()
    rules = g["rules"]
    n = len(rules)
    fe = _fp(_with_rules(g, []))
    fg = _fp(g)
    dG = _d(fg, fe)
    splits = []
    for s in range(1, n):
        dA = _d(_fp(_with_rules(g, rules[:s])), fe)
        dB = _d(_fp(_with_rules(g, rules[s:])), fe)
        splits.append({"s": s, "dA": dA, "dB": dB})
    comp = [x for x in splits if x["dA"] <= eps and x["dB"] <= eps and dG > tau]
    best = max(splits, key=lambda x: dG / max(x["dA"], x["dB"], 1e-9)) if splits else None
    return {"n_rules": n, "d_G_empty": dG, "composition": bool(comp), "composition_splits": [x["s"] for x in comp],
            "best_split": best, "best_synergy": (dG / max(best["dA"], best["dB"], 1e-9)) if best else None,
            "cpu_s": time.process_time() - t0}


def load_arms(rng, n_per_arm=N_PER_ARM):
    arms = {a: [] for a in ARMS}
    lane_arm = {"DEEP": "D", "VERY_DEEP": "D", "DEEP_LENS": "E", "SHALLOW": "S", "G0": "G"}
    for line in open(f"theseus/entities/{REF}.jsonl", encoding="utf-8"):
        e = json.loads(line)
        if e.get("kind") == "mechanism" and e.get("origin") == "synthetic" and e.get("viable"):
            arm = lane_arm.get(e.get("lane"))
            if arm:
                arms[arm].append({"id": e["id"], "genome": e["executableRepresentation"]})
    arms_path = f"theseus/controls/arms_{REF}.jsonl"  # absent for --ecology-only runs (THESEUS-31c)
    for line in (open(arms_path, encoding="utf-8") if os.path.exists(arms_path) else []):
        r = json.loads(line)
        if r["arm"] in ("B", "C", "P", "R", "A") and r["viable"]:
            arms[r["arm"]].append({"id": r["id"], "genome": r["genome"]})
    out = {}
    for a, rows in arms.items():
        rows = [r for r in rows if len(r["genome"]["rules"]) >= 2]
        idx = rng.choice(len(rows), size=min(n_per_arm, len(rows)), replace=False) if rows else []
        out[a] = [rows[i] for i in sorted(idx)]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n", type=int, default=N_PER_ARM)
    a = ap.parse_args(argv)
    out_dir = f"theseus/runs/{a.tag}"
    os.makedirs(out_dir, exist_ok=True)
    cald = json.load(open(f"theseus/runs/{REF}/CAL.json", encoding="utf-8"))
    eps, tau = cald["g0_rep_dist_pct"][1], cald["tau_rep"]
    arms = load_arms(np.random.default_rng(20261008), a.n)
    jobs = [(arm, r) for arm in ARMS for r in arms[arm]]
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(cald,)) as pool:
        res = pool.map(_job, [(r["genome"], eps, tau) for _, r in jobs])
    rows = [{"arm": arm, "id": r["id"], **x} for (arm, r), x in zip(jobs, res)]
    summary = {"eps": eps, "tau": tau, "wall_s": round(time.time() - t0, 1),
               "cpu_s": round(sum(x["cpu_s"] for x in res), 1), "arms": {}}
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        k = sum(r["composition"] for r in rs)
        summary["arms"][arm] = {"n": len(rs), "compositions": k, "rate": (k / len(rs)) if rs else None,
                                "median_n_rules": float(np.median([r["n_rules"] for r in rs])) if rs else None,
                                "median_best_synergy": float(np.median([r["best_synergy"] for r in rs])) if rs else None}
    with open(f"{out_dir}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    with open(f"{out_dir}/SUMMARY.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
