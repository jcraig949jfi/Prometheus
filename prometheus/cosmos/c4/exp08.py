"""EXP-08: surrogate one-step gain vs truth (prereg roles/Cosmos/c4/prereg/EXP-08_SURROGATE_GAIN.md).

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.c4.exp08 run <rundir> [workers]
    python -m prometheus.cosmos.c4.exp08 analyse <rundir> <exp07.jsonl>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c4 import exp07 as X7

V = 4
N_PTS = 256
EPS = 1e-3


def jobs():
    return X7.jobs()


def _step(S, Z, o):
    from prometheus.cosmos.c4.sysid_surrogate import _rf
    X = np.hstack([Z, np.eye(S["n_in"])[np.full(len(Z), o)]])
    return _rf(X, S["P"], S["b"]) @ S["W"]


def one(j: dict) -> dict:
    from prometheus.cosmos.c3.task import Task
    from prometheus.cosmos.c4 import planted
    from prometheus.cosmos.c4.sysid_local import LocalProbe
    from prometheus.cosmos.c4.sysid_surrogate import fit_surrogate
    from prometheus.cosmos.hashing import h
    cls = getattr(planted, j["cls"])
    seed = int(h({"EXP-06": j["key"]})[:8], 16) if j["grid"] == "G1" else int(h({"EXP-07": j["key"]})[:8], 16)
    rhos = []
    for k in X7.KS:                                    # EXP-07 fitted one surrogate per k (same seed); match it
        t = Task(V, k)
        S = fit_surrogate(LocalProbe(cls(t, j["a"], j["sigma"], wseed=j["wseed"]), t.n_symbols, seed=seed))
        Zs = S["Z0"][np.random.default_rng(0).integers(0, len(S["Z0"]), N_PTS)]
        d = Zs.shape[1]
        r = []
        for z in Zs:
            base = _step(S, z[None], V)[0]
            J = np.stack([(_step(S, (z + EPS * np.eye(d)[i])[None], V)[0] - base) / EPS for i in range(d)], 1)
            r.append(float(np.max(np.abs(np.linalg.eigvals(J)))))
        rhos.append({"k": k, "rho_fit": float(np.median(r))})
    return {**j, "rho": rhos}


def run(rundir: str, workers: int = 3):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="exp08.jsonl", workers=workers, max_failures=0)


def analyse(rundir: str, exp07: str) -> dict:
    from scipy.stats import spearmanr
    ex = lambda a: (a - 1.0 / V) / (1.0 - 1.0 / V)
    g = {json.loads(x)["key"]: json.loads(x) for x in Path(rundir, "exp08.jsonl").read_text().splitlines() if x.strip()}
    e7 = {json.loads(x)["key"]: json.loads(x) for x in Path(exp07).read_text().splitlines() if x.strip()}
    gap95, s, err = [], [], []
    by_a = {}
    for key, r in g.items():
        for rr, c in zip(r["rho"], e7[key]["cells"]):
            assert rr["k"] == c["k"]
            by_a.setdefault(r["a"], []).append(rr["rho_fit"] - r["a"])
            if r["a"] == .95:
                gap95.append(rr["rho_fit"] - r["a"])
            if r["a"] >= .85:
                s.append((rr["rho_fit"] / r["a"]) ** (c["k"] + 2) - 1)
                err.append(ex(c["pred"]["O1"]) - ex(c["actual"]))
    m95 = float(np.median(gap95))
    rho = float(spearmanr(s, err).statistic)
    ok = m95 <= -.01 and rho >= .5
    return {"median_gap_a95": m95, "spearman_shortfall_vs_O1_error": rho, "n_cells_a_ge_85": len(s),
            "median_gap_by_a": {str(a): float(np.median(v)) for a, v in sorted(by_a.items())},
            "verdict": "H-GAIN SUPPORTED" if ok else "H-GAIN REJECTED"}


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 3)
    elif a[1] == "analyse":
        print(json.dumps(analyse(a[2], a[3]), indent=1))
