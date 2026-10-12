"""THESEUS-30a: can the 23b composition detector fire at all? Constructive controls.

Prereg: roles/Theseus/prereg/2026-10-08_comp_control/PREREG.md.

PLANTED (should be compositions): genomes whose rules split into a WRITER block
(only "remember" rules: they write the memory field, never the state) followed or
preceded by a READER block (only "inject"/"modulate": they read memory, so they are
inert while memory is empty). Each block alone leaves the state untouched by
construction; together they act.
NEGATIVE (should not be compositions):
  N-active : two blocks that each act alone (diffuse + decay style)
  N-recall : writer + "recall" (recall pulls the state toward memory, active alone)
  N-inert  : writer-only genomes (inert as a whole)
Detector: theseus.synth.composition._job with the frozen v0_1 EPS/TAU.
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

from . import composition as cp  # noqa: E402
from . import substrate as sb  # noqa: E402

REF = "v0_1_2026-09-30"


def _base(rng, C):
    return {"C": C, "topo": {"kind": str(rng.choice(["ring", "line", "rrg"])), "seed": int(rng.integers(1 << 16))},
            "bc": "periodic", "init": {"kind": str(rng.choice(["spike", "random", "gradient", "blocks"])), "amp": 1.0}}


def writer(rng, C):
    return {"op": "remember", "src": [int(rng.integers(C))], "dst": int(rng.integers(C)),
            "p": [float(rng.uniform(0.05, 0.9))], "prov": "ctl"}


def reader(rng, C, dsts):
    d = int(rng.choice(dsts))
    if rng.random() < 0.5:
        return {"op": "inject", "src": [], "dst": d, "p": [float(rng.choice([-1, 1]) * rng.uniform(0.05, 0.5))], "prov": "ctl"}
    return {"op": "modulate", "src": [int(rng.integers(C))], "dst": d,
            "p": [float(rng.choice([-1, 1]) * rng.uniform(0.1, 1.0))], "prov": "ctl"}


def planted(rng):
    C = int(rng.integers(1, 4))
    W = [writer(rng, C) for _ in range(int(rng.integers(1, 3)))]
    R = [reader(rng, C, [w["dst"] for w in W]) for _ in range(int(rng.integers(1, 3)))]
    rules = W + R if rng.random() < 0.7 else R + W
    return {**_base(rng, C), "rules": rules}


def neg_active(rng):
    C = 1
    ops = [sb.rand_rule(rng, C, op=o, prov="ctl") for o in rng.choice(["diffuse", "decay", "advect", "mirror", "rank"], size=2, replace=False)]
    return {**_base(rng, C), "rules": ops}


def neg_recall(rng):
    C = int(rng.integers(1, 3))
    W = writer(rng, C)
    return {**_base(rng, C), "rules": [W, {"op": "recall", "src": [], "dst": W["dst"], "p": [float(rng.uniform(0.2, 0.9))], "prov": "ctl"}]}


def neg_inert(rng):
    C = int(rng.integers(1, 3))
    return {**_base(rng, C), "rules": [writer(rng, C) for _ in range(int(rng.integers(2, 4)))]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    cald = json.load(open(f"theseus/runs/{REF}/CAL.json", encoding="utf-8"))
    eps, tau = cald["g0_rep_dist_pct"][1], cald["tau_rep"]
    rng = np.random.default_rng(20261008)
    rows = []
    for cls, fn in (("planted", planted), ("neg_active", neg_active), ("neg_recall", neg_recall), ("neg_inert", neg_inert)):
        for i in range(a.n):
            g = fn(rng)
            assert not sb.validate(g), (cls, sb.validate(g))
            rows.append({"id": f"{cls}-{i:03d}", "class": cls, "genome": g})
    t0 = time.time()
    with Pool(a.workers, initializer=cp._init, initargs=(cald,)) as pool:
        res = pool.map(cp._job, [(r["genome"], eps, tau) for r in rows])
    for r, x in zip(rows, res):
        r.update(x)
    summ = {"eps": eps, "tau": tau, "wall_s": round(time.time() - t0, 1), "classes": {}}
    for cls in ("planted", "neg_active", "neg_recall", "neg_inert"):
        rs = [r for r in rows if r["class"] == cls]
        summ["classes"][cls] = {"n": len(rs), "flagged": sum(r["composition"] for r in rs),
                                "median_d_whole": float(np.median([r["d_G_empty"] for r in rs]))}
    with open(f"{out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
