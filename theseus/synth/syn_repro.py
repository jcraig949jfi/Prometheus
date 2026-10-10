"""THESEUS-39 part R: known-mechanism reproduction of the admitted SYN concepts (before any claim).

Prereg: roles/Theseus/prereg/2026-10-09_syn_reinject/PREREG.md.

R1  battery fingerprint (charter mechanistic reproduction): known.reproduce against the known
    library rebuilt from the source run's frozen CAL.json (seed master + 11, 40 per family).
R2  task fingerprint: J over 8 task variants (ch0 readout V4 k2/k4/k8/k16 seed 0, V4 k8 seed 1,
    V8 k8; full-state readout V4 k8, V8 k8). Known reference = parameter sweeps of the three
    hand-built store+release mechanisms (task_comp 2-part controls): remember rate x
    inject/recall rate, and the relay-out-back diffusion rates (5 x 5 grid each, 75 genomes).
    REPRODUCED_BY_KNOWN iff some reference matches every variant within .05; PARTIAL within .15.
"""

import argparse
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import known as kn  # noqa: E402
from . import rulers as ru  # noqa: E402
from . import task_system as ts  # noqa: E402

VARIANTS = [(4, 2, 0, "ch0"), (4, 4, 0, "ch0"), (4, 8, 0, "ch0"), (4, 16, 0, "ch0"), (4, 8, 1, "ch0"),
            (8, 8, 0, "ch0"), (4, 8, 0, "all"), (8, 8, 0, "all")]
GRID = [0.2, 0.4, 0.6, 0.8, 1.0]


def task_fp(g):
    return [ts.task_J(g, V=V, k=k, seed=s, readout=ro)["J"] for V, k, s, ro in VARIANTS]


def references():
    B = {"topo": {"kind": "ring", "seed": 3}, "bc": "periodic", "init": {"kind": "random", "amp": 0.1}}
    out = []
    for a in GRID:
        for b in GRID:
            out.append((f"remember_inject:{a}:{b}", {**B, "C": 1, "rules": [
                {"op": "remember", "src": [0], "dst": 0, "p": [a]}, {"op": "inject", "src": [], "dst": 0, "p": [b]}]}))
            out.append((f"remember_recall:{a}:{b}", {**B, "C": 1, "rules": [
                {"op": "remember", "src": [0], "dst": 0, "p": [a]}, {"op": "recall", "src": [], "dst": 0, "p": [b]}]}))
            out.append((f"relay_out_back:{a}:{b}", {**B, "C": 2, "rules": [
                {"op": "diffuse", "src": [0], "dst": 1, "p": [a / 2]}, {"op": "saturate", "src": [], "dst": 1, "p": [2.0]},
                {"op": "diffuse", "src": [1], "dst": 0, "p": [b / 2]}]}))
    return out


_CAL, _LIB = None, None


def _init(cald, lib):
    global _CAL, _LIB
    _CAL = ru.Cal(cald)
    _LIB = lib and {"fam": lib["fam"], "theta": lib["theta"], "fp": np.asarray(lib["fp"])}


def _r1(args):
    g, seed = args
    return kn.reproduce(kn.fp_of(g, _CAL), _LIB, _CAL, seed=seed)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="v0_2t0_2026-10-08")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    out = f"theseus/runs/syn_repro_{a.run}"
    os.makedirs(out, exist_ok=True)
    syn = [json.loads(l) for l in open(f"theseus/archive/syn_concepts_{a.run}.jsonl", encoding="utf-8")]
    syn = [s for s in syn if s["admitted"]]
    cald = json.load(open(f"theseus/runs/{a.run}/CAL.json", encoding="utf-8"))
    master = json.load(open(f"theseus/runs/{a.run}/CONFIG.json", encoding="utf-8"))["master_seed"]
    cal = ru.Cal(cald)
    refs = references()
    with Pool(a.workers) as pool:
        lib = kn.build_library(cal, seed=master + 11, per_family=kn.LIB_PER_FAMILY, mapper=pool.map)
        lib = {"fam": lib["fam"], "theta": lib["theta"], "fp": np.asarray(lib["fp"]).tolist()}
        tf_syn = pool.map(task_fp, [s["executable_definition"] for s in syn])
        tf_ref = pool.map(task_fp, [g for _, g in refs])
    with Pool(a.workers, initializer=_init, initargs=(cald, lib)) as pool:
        r1 = pool.map(_r1, [(s["executable_definition"], 1000 + i) for i, s in enumerate(syn)])
    R = np.asarray(tf_ref)
    rows = []
    for s, tf, x in zip(syn, tf_syn, r1):
        dev = np.abs(R - np.asarray(tf)).max(axis=1)
        j = int(np.argmin(dev))
        v2 = "REPRODUCED_BY_KNOWN" if dev[j] <= 0.05 else ("PARTIALLY_REPRODUCED" if dev[j] <= 0.15 else "NOT_REPRODUCED_YET")
        rows.append({"syn_id": s["syn_id"], "R1": {k: x[k] for k in ("verdict", "best_dist", "best_family", "tau_rep")},
                     "R2": {"verdict": v2, "max_dev": float(dev[j]), "best_ref": refs[j][0], "task_fp": tf,
                            "ref_fp": tf_ref[j]}})
    with open(f"{out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    summ = {"n": len(rows), "variants": VARIANTS,
            "R1": {v: sum(r["R1"]["verdict"] == v for r in rows) for v in ("REPRODUCED_BY_KNOWN", "PARTIALLY_REPRODUCED", "NOT_REPRODUCED_YET")},
            "R2": {v: sum(r["R2"]["verdict"] == v for r in rows) for v in ("REPRODUCED_BY_KNOWN", "PARTIALLY_REPRODUCED", "NOT_REPRODUCED_YET")},
            "ref_task_fp_range": [[float(R[:, i].min()), float(R[:, i].max())] for i in range(R.shape[1])],
            "n_refs": len(refs)}
    json.dump(summ, open(f"{out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
