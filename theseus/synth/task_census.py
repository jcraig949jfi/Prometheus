"""THESEUS-31a: task census -- do any existing Theseus programs carry a cue through distractors?

Prereg: roles/Theseus/prereg/2026-10-08_task_census/PREREG.md.

Every program is run as a task organism (theseus.synth.task_system: channel 0 is a transient
sensor overwritten each step; readout = ridge on the state at the query). J = held-out
cue-recall accuracy at V = 4, k = 4 (chance .25). No selection: this is a census of what the
committed v0_1 arms already do.

Gate (built here, seed 20261008, 20 each):
  noop      one no-op rule, varied C/topology/init       -> J must be at chance
  relay     C = 2, diffuse ch0 -> ch1 (+ saturate)       -> positive control (1-part)
  memcomp   C = 2, remember ch0 -> M[1], inject M[1] -> ch1 (+ saturate): a writer/reader
            composition                                  -> positive control (2-part)
"""

from __future__ import annotations

import argparse
import json
import os
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import task_system as ts  # noqa: E402

REF = "v0_1_2026-09-30"
ARMS = ("D", "E", "B", "C", "P", "R", "A", "G0")


def _base(rng, C):
    return {"C": C, "topo": {"kind": str(rng.choice(["ring", "line", "rrg"])), "seed": int(rng.integers(1 << 16))},
            "bc": "periodic", "init": {"kind": str(rng.choice(["spike", "random", "gradient", "blocks"])), "amp": 0.1}}


def controls(rng, n=20):
    rows = []
    for i in range(n):
        C = int(rng.integers(1, 4))
        rows.append(("CTL:noop", f"noop-{i:02d}", {**_base(rng, C), "rules": [{"op": "recall", "src": [], "dst": 0, "p": [0.0]}]}))
        rows.append(("CTL:relay", f"relay-{i:02d}", {**_base(rng, 2), "rules": [
            {"op": "diffuse", "src": [0], "dst": 1, "p": [float(rng.uniform(0.2, 0.5))]},
            {"op": "saturate", "src": [], "dst": 1, "p": [float(rng.uniform(1.0, 3.0))]}]}))
        rows.append(("CTL:memcomp", f"memcomp-{i:02d}", {**_base(rng, 2), "rules": [
            {"op": "remember", "src": [0], "dst": 1, "p": [float(rng.uniform(0.3, 0.9))]},
            {"op": "inject", "src": [], "dst": 1, "p": [float(rng.uniform(0.2, 0.5))]},
            {"op": "saturate", "src": [], "dst": 1, "p": [float(rng.uniform(1.0, 3.0))]}]}))
    return rows


def load_arms(rng, n):
    lane_arm = {"DEEP": "D", "VERY_DEEP": "D", "DEEP_LENS": "E"}
    arms = {a: [] for a in ARMS}
    for l in open(f"theseus/entities/{REF}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("viable") and e.get("kind") == "mechanism" and e.get("lane") in lane_arm:
            arms[lane_arm[e["lane"]]].append((e["id"], e["executableRepresentation"]))
        if e.get("viable") and e.get("origin") == "human":
            arms["G0"].append((e["id"], e["executableRepresentation"]))
    for l in open(f"theseus/controls/arms_{REF}.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["viable"] and r["arm"] in ("B", "C", "P", "R", "A"):
            arms[r["arm"]].append((r["id"], r["genome"]))
    out = []
    for a in ARMS:
        rows = arms[a]
        idx = sorted(rng.choice(len(rows), size=min(n, len(rows)), replace=False)) if rows else []
        out += [(a, rows[i][0], rows[i][1]) for i in idx]
    return out


def _job(g):
    t0 = time.process_time()
    r = ts.task_J(g, V=4, k=4, seed=0)
    r["cpu_s"] = time.process_time() - t0
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20261008)
    jobs = controls(rng) + load_arms(rng, a.n)
    t0 = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(_job, [g for _, _, g in jobs])
    rows = [{"group": grp, "id": i, **x} for (grp, i, _), x in zip(jobs, res)]
    summ = {"wall_s": round(time.time() - t0, 1), "cpu_s": round(sum(x["cpu_s"] for x in res), 1), "groups": {}}
    for grp in sorted({r["group"] for r in rows}):
        J = np.array([r["J"] for r in rows if r["group"] == grp])
        summ["groups"][grp] = {"n": len(J), "median_J": float(np.median(J)), "mean_J": float(J.mean()),
                               "share_above_chance_plus_.10": float((J > 0.35).mean()), "max_J": float(J.max())}
    with open(f"{out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
