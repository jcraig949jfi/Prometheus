"""EXP-06: surrogate underprediction diagnosis on planted systems (prereg
roles/Cosmos/c4/prereg/EXP-06_SURROGATE_UNDERPREDICTION.md).

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.c4.exp06 run <rundir> [workers]
    python -m prometheus.cosmos.c4.exp06 analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

V = 4
KS = (2, 4, 8)
VARIANTS = ("V0", "V1", "V2", "V3", "V4")


def jobs():
    out = []
    for a in (.5, .7, .85, .95):
        for s in (.1, .3):
            for w in (1, 2):
                out.append({"key": f"Res:a{a}:s{s}:w{w}", "cls": "Reservoir", "a": a, "sigma": s, "wseed": w})
    for a in (.7, .85, .95):
        for w in (1, 2):
            out.append({"key": f"Rot:a{a}:s.3:w{w}", "cls": "RotReservoir", "a": a, "sigma": .3, "wseed": w})
    return out


def one(j: dict) -> dict:
    from prometheus.cosmos.c3.task import Task
    from prometheus.cosmos.c4 import planted
    from prometheus.cosmos.c4.cert_b import b_use
    from prometheus.cosmos.c4.sysid_local import LocalProbe
    from prometheus.cosmos.c4.sysid_surrogate import fit_surrogate, predicted_accuracy
    from prometheus.cosmos.hashing import h
    cls = getattr(planted, j["cls"])
    seed = int(h({"EXP-06": j["key"]})[:8], 16)
    cells = []
    for k in KS:
        t = Task(V, k)
        sys_ = cls(t, j["a"], j["sigma"], wseed=j["wseed"])
        actual = float(b_use(sys_, t, "linear", seed=seed + k)["acc"])
        probe = lambda: LocalProbe(sys_, t.n_symbols, seed=seed)
        S0 = fit_surrogate(probe())
        S3 = fit_surrogate(probe(), ridge=1e-4)
        S4 = fit_surrogate(probe(), n=16384)
        pred = {"V0": predicted_accuracy(S0, V, k), "V1": predicted_accuracy(S0, V, k, noise_scale=0.0),
                "V2": predicted_accuracy(S0, V, k, clip=False), "V3": predicted_accuracy(S3, V, k),
                "V4": predicted_accuracy(S4, V, k)}
        cells.append({"k": k, "actual": actual, "pred": pred})
    return {**j, "cells": cells}


def run(rundir: str, workers: int = 3):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="exp06.jsonl", workers=workers, max_failures=0)


def analyse(rundir: str) -> dict:
    ex = lambda a: (a - 1.0 / V) / (1.0 - 1.0 / V)
    rows = [json.loads(x) for x in (Path(rundir) / "exp06.jsonl").read_text().splitlines() if x.strip()]
    cells = [c for r in rows for c in r["cells"]]
    act = np.array([ex(c["actual"]) for c in cells])
    out = {}
    for v in VARIANTS:
        err = np.array([ex(c["pred"][v]) for c in cells]) - act
        out[v] = {"MAE": float(np.median(np.abs(err))), "SE": float(np.median(err))}
    base = out["V0"]
    confirmed = base["SE"] < -.05
    causes = [v for v in VARIANTS[1:] if out[v]["MAE"] <= .5 * base["MAE"] and abs(out[v]["SE"]) <= .05]
    verdict = ("NOT CONFIRMED on planted systems (no cause assigned)" if not confirmed else
               ("CAUSE(S) IDENTIFIED: " + ", ".join(causes)) if causes else "INSTRUMENT_DEFECT UNEXPLAINED")
    return {"n_cells": len(cells), "variants": out, "underprediction_confirmed": confirmed, "verdict": verdict}


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 3)
    elif a[1] == "analyse":
        print(json.dumps(analyse(a[2]), indent=1))
