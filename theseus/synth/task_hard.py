"""THESEUS-31b: harder task replication + knockout attribution of the cue carrier.

Prereg: roles/Theseus/prereg/2026-10-08_task_hard/PREREG.md.

Part 1: J at V = 8, k = 8 (chance .125), mean over task seeds 0 and 1, for the same arm
        sample construction as 31a (seed 20261008, 100 per arm) plus the 31a gate controls.
Part 2: for genomes with J_hard >= .5 (up to 40 per arm, seeded), single-rule knockouts:
        J (seed 0) with rule i removed; rule i is ESSENTIAL if J drops by >= .2.
        Carrier size = number of essential rules (0 = redundant carriers, 1 = one-part,
        >= 2 = multi-part carrier).
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

from . import task_census as tc  # noqa: E402
from . import task_system as ts  # noqa: E402

V, K = 8, 8
ESSENTIAL_DROP = 0.2
J_MIN_FOR_KO = 0.5
KO_PER_ARM = 40


def _j2(g):
    t0 = time.process_time()
    js = [ts.task_J(g, V=V, k=K, seed=s)["J"] for s in (0, 1)]
    return {"J_hard": float(np.mean(js)), "J_seeds": js, "cpu_s": time.process_time() - t0}


def _ko(args):
    g, base = args
    t0 = time.process_time()
    drops = []
    for i in range(len(g["rules"])):
        h = copy.deepcopy(g)
        h["rules"] = [r for k, r in enumerate(g["rules"]) if k != i] or [{"op": "recall", "src": [], "dst": 0, "p": [0.0]}]
        drops.append(base - ts.task_J(h, V=V, k=K, seed=0)["J"])
    ess = [i for i, d in enumerate(drops) if d >= ESSENTIAL_DROP]
    return {"drops": drops, "essential": ess, "essential_ops": [g["rules"][i]["op"] for i in ess],
            "carrier_size": len(ess), "cpu_s": time.process_time() - t0}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261008)
    jobs = tc.controls(rng) + tc.load_arms(rng, 100)  # identical construction to 31a
    t0 = time.time()
    # Amendment 1 (checkpointing only, no scientific change): results are appended to
    # PART1.jsonl / PART2.jsonl as they complete, and a restart skips ids already done.
    p1 = f"{out}/PART1.jsonl"
    done1 = {}
    if os.path.exists(p1):
        for l in open(p1, encoding="utf-8"):
            x = json.loads(l)
            done1[x["id"]] = x
    todo = [(grp, i, g) for grp, i, g in jobs if i not in done1]
    with Pool(a.workers) as pool:
        with open(p1, "a", encoding="utf-8") as f1:
            for (grp, i, g), x in zip(todo, pool.imap(_j2, [g for _, _, g in todo])):
                rec = {"group": grp, "id": i, **x}
                f1.write(json.dumps(rec, separators=(",", ":")) + chr(10))
                f1.flush()
                done1[i] = rec
        res = [done1[i] for _, i, _ in jobs]
        rows = [{"group": grp, "id": i, "genome": g, **{k: v for k, v in done1[i].items() if k not in ("group", "id")}}
                for (grp, i, g) in jobs]
        krng = np.random.default_rng(7)
        ko_rows = []
        for grp in tc.ARMS:
            cand = [r for r in rows if r["group"] == grp and r["J_hard"] >= J_MIN_FOR_KO]
            idx = sorted(krng.choice(len(cand), size=min(KO_PER_ARM, len(cand)), replace=False)) if cand else []
            ko_rows += [cand[i] for i in idx]
        # knockout baseline = J at seed 0 (same seed as the knockouts)
        p2 = f"{out}/PART2.jsonl"
        done2 = {}
        if os.path.exists(p2):
            for l in open(p2, encoding="utf-8"):
                x = json.loads(l)
                done2[x["id"]] = x
        todo2 = [r for r in ko_rows if r["id"] not in done2]
        with open(p2, "a", encoding="utf-8") as f2:
            for r, x in zip(todo2, pool.imap(_ko, [(r["genome"], r["J_seeds"][0]) for r in todo2])):
                f2.write(json.dumps({"id": r["id"], **x}, separators=(",", ":")) + chr(10))
                f2.flush()
                done2[r["id"]] = x
        ko_res = [{k: v for k, v in done2[r["id"]].items() if k != "id"} for r in ko_rows]
    for r, x in zip(ko_rows, ko_res):
        r["knockout"] = x
    summ = {"V": V, "k": K, "chance": 1.0 / V, "wall_s": round(time.time() - t0, 1),
            "cpu_s": round(sum(x.get("cpu_s", 0) for x in res) + sum(x.get("cpu_s", 0) for x in ko_res), 1), "groups": {}}
    for grp in sorted({r["group"] for r in rows}):
        J = np.array([r["J_hard"] for r in rows if r["group"] == grp])
        ks = [r["knockout"]["carrier_size"] for r in ko_rows if r["group"] == grp]
        summ["groups"][grp] = {"n": len(J), "mean_J": float(J.mean()), "median_J": float(np.median(J)),
                               "share_J_ge_.5": float((J >= 0.5).mean()),
                               "ko_n": len(ks),
                               "carrier_size_counts": {str(c): ks.count(c) for c in sorted(set(ks))} if ks else {}}
    with open(f"{out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if k != "genome"}, separators=(",", ":")) + "\n")
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
