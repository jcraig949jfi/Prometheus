"""THESEUS-33: is the depth advantage on the cue-recall task DEGENERACY (redundant carriers)?

Prereg: roles/Theseus/prereg/2026-10-08_degeneracy/PREREG.md.

Population: the 31b knockout set (capable genomes, J_hard >= .5, up to 40 per arm), restricted
to genomes with carrier size 0 (no single rule essential). Their genomes are rebuilt with the
identical construction as 31a/31b (task_census.controls + load_arms, seed 20261008).
For each, every PAIR of rules is knocked out (J at V 8, k 8, task seed 0):
  DEGENERATE         some pair drop >= .2 (two redundant carriers)
  DISTRIBUTED        no pair drop >= .2 (>= 3 overlapping carriers, or a diffuse carrier)
Gate (built here, 20 each):
  redundant_relay    C = 3: two separate relays ch0 -> ch1 and ch0 -> ch2 (+ saturate each):
                     single knockouts must not break it (size 0) and the relay pair must
  single_relay       C = 2: one relay ch0 -> ch1 (+ saturate): its relay is essential (size 1)
"""

from __future__ import annotations

import argparse
import json
import os
import time
from itertools import combinations
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import task_census as tc  # noqa: E402
from . import task_system as ts  # noqa: E402

V, K = 8, 8
DROP = 0.2
NOOP = {"op": "recall", "src": [], "dst": 0, "p": [0.0]}


def _J(g):
    return ts.task_J(g, V=V, k=K, seed=0)["J"]


def _without(g, drop):
    h = dict(g)
    h["rules"] = [r for i, r in enumerate(g["rules"]) if i not in drop] or [dict(NOOP)]
    return h


def job(g):
    t0 = time.process_time()
    base = _J(g)
    n = len(g["rules"])
    singles = [base - _J(_without(g, {i})) for i in range(n)]
    pairs = []
    for i, j in combinations(range(n), 2):
        d = base - _J(_without(g, {i, j}))
        if d >= DROP:
            pairs.append([i, j, d])
    return {"J0": base, "single_drops": singles, "carrier_size": sum(d >= DROP for d in singles),
            "critical_pairs": pairs, "degenerate": bool(pairs) and all(d < DROP for d in singles),
            "pair_ops": [[g["rules"][i]["op"], g["rules"][j]["op"]] for i, j, _ in pairs],
            "cpu_s": time.process_time() - t0}


def gate(rng, n=20):
    rows = []
    for i in range(n):
        base = {"topo": {"kind": "ring", "seed": int(rng.integers(1 << 16))}, "bc": "periodic",
                "init": {"kind": "random", "amp": 0.1}}
        a, b = float(rng.uniform(0.2, 0.5)), float(rng.uniform(0.2, 0.5))
        rows.append(("CTL:redundant_relay", f"rr-{i:02d}", {**base, "C": 3, "rules": [
            {"op": "diffuse", "src": [0], "dst": 1, "p": [a]}, {"op": "saturate", "src": [], "dst": 1, "p": [2.0]},
            {"op": "diffuse", "src": [0], "dst": 2, "p": [b]}, {"op": "saturate", "src": [], "dst": 2, "p": [2.0]}]}))
        rows.append(("CTL:single_relay", f"sr-{i:02d}", {**base, "C": 2, "rules": [
            {"op": "diffuse", "src": [0], "dst": 1, "p": [a]}, {"op": "saturate", "src": [], "dst": 1, "p": [2.0]}]}))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261008)
    genomes = {i: (grp, g) for grp, i, g in tc.controls(rng) + tc.load_arms(rng, 100)}  # 31a/31b construction
    ko = [json.loads(l) for l in open("theseus/runs/task_hard_2026-10-08/ROWS.jsonl", encoding="utf-8")]
    target = [r for r in ko if "knockout" in r and r["knockout"]["carrier_size"] == 0]
    jobs = gate(np.random.default_rng(33)) + [(r["group"], r["id"], genomes[r["id"]][1]) for r in target]
    p = f"{out}/ROWS.jsonl"
    done = {}
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            x = json.loads(l)
            done[x["id"]] = x
    todo = [(grp, i, g) for grp, i, g in jobs if i not in done]
    t0 = time.time()
    with Pool(a.workers) as pool, open(p, "a", encoding="utf-8") as f:
        for (grp, i, g), x in zip(todo, pool.imap(job, [g for _, _, g in todo])):
            rec = {"group": grp, "id": i, "n_rules": len(g["rules"]), **x}
            f.write(json.dumps(rec, separators=(",", ":")) + chr(10))
            f.flush()
            done[i] = rec
    rows = [done[i] for _, i, _ in jobs]
    summ = {"V": V, "k": K, "wall_s": round(time.time() - t0, 1), "groups": {},
            "ko_set_sizes": {g: sum(1 for r in ko if "knockout" in r and r["group"] == g) for g in tc.ARMS}}
    for grp in sorted({r["group"] for r in rows}):
        rs = [r for r in rows if r["group"] == grp]
        summ["groups"][grp] = {"n": len(rs), "degenerate": sum(r["degenerate"] for r in rs),
                               "carrier_size_0": sum(r["carrier_size"] == 0 for r in rs),
                               "distributed": sum((r["carrier_size"] == 0) and not r["critical_pairs"] for r in rs)}
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
