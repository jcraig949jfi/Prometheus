"""EXP-07: surrogate start-state test (prereg roles/Cosmos/c4/prereg/EXP-07_SURROGATE_START_STATE.md).

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.c4.exp07 run <rundir> [workers]
    python -m prometheus.cosmos.c4.exp07 analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c4 import exp06 as X6

V = 4
KS = (2, 4, 8)


def jobs():
    out = [{**j, "grid": "G1"} for j in X6.jobs()]
    for a in (.5, .7, .85, .95):
        for s in (.1, .3):
            for w in (3, 4):
                out.append({"key": f"G2:Res:a{a}:s{s}:w{w}", "cls": "Reservoir", "a": a, "sigma": s, "wseed": w,
                            "grid": "G2"})
    return out


def one(j: dict) -> dict:
    from prometheus.cosmos.c3.task import Task
    from prometheus.cosmos.c4 import planted
    from prometheus.cosmos.c4.cert_b import b_use
    from prometheus.cosmos.c4.sysid_local import LocalProbe
    from prometheus.cosmos.c4.sysid_surrogate import E_SIM, fit_surrogate, predicted_accuracy
    from prometheus.cosmos.hashing import h
    cls = getattr(planted, j["cls"])
    seed = int(h({"EXP-06": j["key"]})[:8], 16) if j["grid"] == "G1" else int(h({"EXP-07": j["key"]})[:8], 16)
    cells = []
    for k in KS:
        t = Task(V, k)
        sys_ = cls(t, j["a"], j["sigma"], wseed=j["wseed"])
        actual = float(b_use(sys_, t, "linear", seed=seed + k)["acc"])
        S = fit_surrogate(LocalProbe(sys_, t.n_symbols, seed=seed))
        z_init = np.asarray(sys_.full_state(sys_.init(E_SIM)), float)
        cells.append({"k": k, "actual": actual, "pred": {"O0": predicted_accuracy(S, V, k),
                                                         "O1": predicted_accuracy(S, V, k, start=z_init)}})
    return {**j, "cells": cells}


def run(rundir: str, workers: int = 3):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="exp07.jsonl", workers=workers, max_failures=0)


def analyse(rundir: str) -> dict:
    ex = lambda a: (a - 1.0 / V) / (1.0 - 1.0 / V)
    rows = [json.loads(x) for x in (Path(rundir) / "exp07.jsonl").read_text().splitlines() if x.strip()]
    out, ok = {}, []
    for g in ("G1", "G2"):
        cells = [c for r in rows if r["grid"] == g for c in r["cells"]]
        act = np.array([ex(c["actual"]) for c in cells])
        m = {}
        for v in ("O0", "O1"):
            err = np.array([ex(c["pred"][v]) for c in cells]) - act
            m[v] = {"MAE": float(np.median(np.abs(err))), "SE": float(np.median(err))}
        m["n_cells"] = len(cells)
        m["passes"] = m["O1"]["MAE"] <= .5 * m["O0"]["MAE"] and abs(m["O1"]["SE"]) <= .05
        ok.append(m["passes"])
        out[g] = m
    out["verdict"] = "H-START SUPPORTED" if all(ok) else "H-START REJECTED"
    return out


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 3)
    elif a[1] == "analyse":
        print(json.dumps(analyse(a[2]), indent=1))
