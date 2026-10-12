"""THESEUS-36: composition-necessary cue recall -- does task selection make recursion build it?

Prereg: roles/Theseus/prereg/2026-10-08_composition_task/PREREG.md.

Task: c3 cue recall, V 4, k 8, readout = the SENSOR channel only after the query step
(task_system.task_J(..., readout="ch0")). Channel 0 is overwritten every step by the input, so
a solver must STORE the cue elsewhere and RELEASE it back into channel 0 at query time; every
1-part control scores at chance and every store+release 2-part control scores 1.0 (validated
before this prereg, theseus/runs/comp_task_2026-10-08/CONTROLS.json).

Per run: J (400/400 episodes, task seed 0) for up to 100 viable DEEP+VERY_DEEP children (seed
20261008); SOLVER = J >= .6; single-rule knockouts on solvers (drop >= .2 = essential).
Checkpointed (J.jsonl, KO.jsonl per run).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import sel_eval as se  # noqa: E402
from . import task_system as ts  # noqa: E402

SOLVER = 0.6
DROP = 0.2
NOOP = {"op": "recall", "src": [], "dst": 0, "p": [0.0]}


def J(g):
    return ts.task_J(g, V=4, k=8, seed=0, readout="ch0")["J"]


def ko(args):
    g, base = args
    drops = []
    for i in range(len(g["rules"])):
        h = copy.deepcopy(g)
        h["rules"] = [r for k, r in enumerate(g["rules"]) if k != i] or [dict(NOOP)]
        drops.append(base - J(h))
    ess = [i for i, d in enumerate(drops) if d >= DROP]
    return {"drops": drops, "essential": ess, "essential_ops": [g["rules"][i]["op"] for i in ess],
            "n_essential": len(ess)}


def controls():
    B = {"topo": {"kind": "ring", "seed": 3}, "bc": "periodic", "init": {"kind": "random", "amp": 0.1}}

    def R(op, src, dst, p):
        return {"op": op, "src": src, "dst": dst, "p": p}
    return {
        "1p:noop": {**B, "C": 1, "rules": [R("recall", [], 0, [0.0])]},
        "1p:relay_out": {**B, "C": 2, "rules": [R("diffuse", [0], 1, [0.4]), R("saturate", [], 1, [2.0])]},
        "1p:delay8_self": {**B, "C": 1, "rules": [R("delay", [0], 0, [8, 0.9])]},
        "1p:remember_only": {**B, "C": 1, "rules": [R("remember", [0], 0, [0.6])]},
        "1p:inject_only": {**B, "C": 1, "rules": [R("inject", [], 0, [0.4])]},
        "2p:relay_out_back": {**B, "C": 2, "rules": [R("diffuse", [0], 1, [0.4]), R("saturate", [], 1, [2.0]),
                                                      R("diffuse", [1], 0, [0.4])]},
        "2p:remember_inject": {**B, "C": 1, "rules": [R("remember", [0], 0, [0.6]), R("inject", [], 0, [0.4])]},
        "2p:remember_recall": {**B, "C": 1, "rules": [R("remember", [0], 0, [0.6]), R("recall", [], 0, [0.5])]},
    }


def _stage(pool, path, items, fn):
    done = {}
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            x = json.loads(l)
            done[x["id"]] = x
    todo = [(i, a) for i, a in items if i not in done]
    with open(path, "a", encoding="utf-8") as f:
        for (i, _), x in zip(todo, pool.imap(fn, [a for _, a in todo])):
            rec = {"id": i, "v": x}
            f.write(json.dumps(rec, separators=(",", ":")) + chr(10))
            f.flush()
            done[i] = rec
    return {i: done[i]["v"] for i in done}


def main(argv=None):
    from scipy.stats import fisher_exact
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--a", required=True, help="task0-selected run")
    ap.add_argument("--b", required=True, help="reproducibility-selected run")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--controls-only", action="store_true")
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    ctl = controls()
    with Pool(a.workers) as pool:
        cj = dict(zip(ctl, pool.map(J, list(ctl.values()))))
        json.dump(cj, open(f"{out}/CONTROLS_RUN.json", "w"), indent=1)
        if a.controls_only:
            print(json.dumps(cj, indent=1))
            return
        res = {}
        for t in (a.a, a.b):
            s = dict(se.sample(t))
            js = _stage(pool, f"{out}/J_{t}.jsonl", list(s.items()), J)
            solvers = [i for i in s if js[i] >= SOLVER]
            kos = _stage(pool, f"{out}/KO_{t}.jsonl", [(i, (s[i], js[i])) for i in solvers], ko)
            res[t] = {"n": len(s), "mean_J": float(np.mean(list(js.values()))),
                      "solvers": len(solvers),
                      "solver_essential_counts": {str(c): sum(1 for i in solvers if kos[i]["n_essential"] == c)
                                                  for c in sorted({kos[i]["n_essential"] for i in solvers})} if solvers else {},
                      "solver_essential_ops": [kos[i]["essential_ops"] for i in solvers]}
    sa, sb = res[a.a], res[a.b]
    p = fisher_exact([[sa["solvers"], sa["n"] - sa["solvers"]], [sb["solvers"], sb["n"] - sb["solvers"]]],
                     alternative="greater").pvalue
    summ = {"controls": cj, "runs": res, "H_SEL_SOLVE_fisher_p": float(p)}
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "runs"} | {"solvers": {t: res[t]["solvers"] for t in res}}, indent=1))


if __name__ == "__main__":
    main()
