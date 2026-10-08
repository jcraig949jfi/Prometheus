"""THESEUS-30c: composition detector v3 -- in-context pairwise epistasis (bitwise traces).

Prereg: roles/Theseus/prereg/2026-10-08_composition_v3/PREREG.md.

For genome G (rules r_0..r_{n-1}) and a rule set S, G-S is G with the rules in S removed
(one no-op rule if nothing is left). Traces are compared bitwise at IC seeds 0 and 1.
A pair (i, j), i < j, is an IN-CONTEXT COMPOSITION iff
    trace(G - {j})   == trace(G - {i, j})     (i alone, in this context, does nothing)
    trace(G - {i})   == trace(G - {i, j})     (j alone, in this context, does nothing)
    trace(G)         != trace(G - {i, j})     (together they act)
This is the two-part mechanism "whose parts are each worth nothing alone", measured inside
the rest of the genome rather than requiring the whole genome to be the two parts (v2).

Validity gate inside the same job (built here, seed 20261008):
  planted       an active background (4-8 rules from ops that never touch memory) with a
                writer ("remember" into memory channel m) and a reader ("inject"/"modulate"
                reading m) inserted at random positions -- the planted pair must be found
  neg_bg        the same backgrounds alone -- no pair may be found
  neg_recall    background + writer + "recall" (active alone) -- the writer/recall pair
                must not be found
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import time
from itertools import combinations
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import composition as cp  # noqa: E402
from . import substrate as sb  # noqa: E402

SEEDS = (0, 1)
BG_OPS = ["diffuse", "advect", "react", "saturate", "conserve", "decay", "threshold", "replicate", "select",
          "mirror", "coarse", "delay", "wrap", "rank", "drive", "gate"]  # never read or write memory


def _without(g, drop):
    keep = [r for k, r in enumerate(g["rules"]) if k not in drop]
    return cp._with_rules(g, keep)


def _tr(g):
    return [sb.run(g, seed=s)[0] for s in SEEDS]


def _eq(a, b):
    return all(np.array_equal(x, y) for x, y in zip(a, b))


def job(g):
    t0 = time.process_time()
    n = len(g["rules"])
    full = _tr(g)
    minus1 = {i: _tr(_without(g, {i})) for i in range(n)}
    pairs = []
    redundant = [i for i in range(n) if _eq(minus1[i], full)]
    for i, j in combinations(range(n), 2):
        m2 = _tr(_without(g, {i, j}))
        if _eq(minus1[j], m2) and _eq(minus1[i], m2) and not _eq(full, m2):
            pairs.append([i, j])
    return {"n_rules": n, "pairs": pairs, "has_composition": bool(pairs), "redundant_rules": redundant,
            "pair_ops": [[g["rules"][i]["op"], g["rules"][j]["op"]] for i, j in pairs],
            "cpu_s": time.process_time() - t0}


def _background(rng, C, n):
    return [sb.rand_rule(rng, C, op=str(rng.choice(BG_OPS)), prov="bg", arity=int(rng.integers(1, 3))) for _ in range(n)]


def controls(rng, n_each=40):
    rows = []
    for i in range(n_each):
        C = int(rng.integers(1, 4))
        base = {"C": C, "topo": {"kind": str(rng.choice(["ring", "line", "rrg"])), "seed": int(rng.integers(1 << 16))},
                "bc": "periodic", "init": {"kind": str(rng.choice(["spike", "random", "gradient", "blocks"])), "amp": 1.0}}
        bg = _background(rng, C, int(rng.integers(4, 9)))
        m = int(rng.integers(C))
        w = {"op": "remember", "src": [int(rng.integers(C))], "dst": m, "p": [float(rng.uniform(0.1, 0.9))], "prov": "ctl_w"}
        if rng.random() < 0.5:
            rd = {"op": "inject", "src": [], "dst": m, "p": [float(rng.choice([-1, 1]) * rng.uniform(0.05, 0.5))], "prov": "ctl_r"}
        else:
            rd = {"op": "modulate", "src": [int(rng.integers(C))], "dst": m,
                  "p": [float(rng.choice([-1, 1]) * rng.uniform(0.1, 1.0))], "prov": "ctl_r"}
        rc = {"op": "recall", "src": [], "dst": m, "p": [float(rng.uniform(0.2, 0.9))], "prov": "ctl_rc"}
        pw, pr = sorted(rng.choice(len(bg) + 2, size=2, replace=False).tolist())
        planted = copy.deepcopy(bg)
        planted.insert(pw, w)
        planted.insert(pr, rd)
        negrc = copy.deepcopy(bg)
        negrc.insert(pw, copy.deepcopy(w))
        negrc.insert(pr, rc)
        rows.append({"class": "planted", "id": f"planted-{i:03d}", "genome": {**base, "rules": planted}, "planted_pair": [pw, pr]})
        rows.append({"class": "neg_bg", "id": f"neg_bg-{i:03d}", "genome": {**base, "rules": copy.deepcopy(bg)}})
        rows.append({"class": "neg_recall", "id": f"neg_recall-{i:03d}", "genome": {**base, "rules": negrc}, "wr_pair": [pw, pr]})
    for r in rows:
        assert not sb.validate(r["genome"]), (r["id"], sb.validate(r["genome"]))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--controls-only", action="store_true")
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    ctl = controls(np.random.default_rng(20261008))
    jobs = [("CTL:" + r["class"], r["id"], r["genome"], r) for r in ctl]
    if not a.controls_only:
        arms = cp.load_arms(np.random.default_rng(20261008), a.n)  # identical sample to 23b / 30b
        jobs += [(arm, r["id"], r["genome"], None) for arm in cp.ARMS for r in arms[arm]]
    t0 = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(job, [g for _, _, g, _ in jobs])
    rows = []
    for (grp, i, g, meta), x in zip(jobs, res):
        row = {"group": grp, "id": i, **x}
        if meta and meta["class"] == "planted":
            row["planted_pair_found"] = meta["planted_pair"] in x["pairs"]
        if meta and meta["class"] == "neg_recall":
            row["writer_recall_pair_found"] = meta["wr_pair"] in x["pairs"]
        rows.append(row)
    summ = {"wall_s": round(time.time() - t0, 1), "cpu_s": round(sum(x["cpu_s"] for x in res), 1), "groups": {}}
    for grp in sorted({r["group"] for r in rows}):
        rs = [r for r in rows if r["group"] == grp]
        s = {"n": len(rs), "with_composition": sum(r["has_composition"] for r in rs),
             "pairs_total": sum(len(r["pairs"]) for r in rs),
             "median_redundant_rules": float(np.median([len(r["redundant_rules"]) for r in rs]))}
        if grp == "CTL:planted":
            s["planted_pair_found"] = sum(r["planted_pair_found"] for r in rs)
        if grp == "CTL:neg_recall":
            s["writer_recall_pair_found"] = sum(r["writer_recall_pair_found"] for r in rs)
        summ["groups"][grp] = s
    with open(f"{out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
