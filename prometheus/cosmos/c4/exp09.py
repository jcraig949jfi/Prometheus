"""EXP-09: stig H-SPREAD on fresh worlds (prereg roles/Cosmos/c4/prereg/EXP-09_STIG_SPREAD.md).

Zero-parameter predictor (mechanistic, from the declared stig knobs; NOT a LOCAL law): expected cue-trace mass inside
the sensor window (+-1 cell) at query time. Field: unit deposit at cell 0 at t = 0, then per step decay (1 - delta)
and nearest-neighbour diffusion D (Stig.step order). Sensor: position distribution, deterministic shift v per step
plus jitter j (+-1 with prob j / 2 each). Expectation over sensor position; the field is deterministic.

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.c4.exp09 run <rundir> [workers]
    python -m prometheus.cosmos.c4.exp09 analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c4 import firewall as FW
from prometheus.cosmos.c4.exp05 import KS, R

V = 4
L = 16


def spread_score(delta: float, D: float, v: int, j: float, k: int, L: int = L) -> float:
    T = k + 2
    f = np.zeros(L)
    p = np.zeros(L)
    p[0] = 1.0
    for t in range(T):
        f = f * (1 - delta)
        if D > 0:
            f = (1 - D) * f + 0.5 * D * (np.roll(f, 1) + np.roll(f, -1))
        if t == 0:
            f[0] += 1.0                                   # the cue write (sensor at cell 0 at t = 0)
        p = np.roll(p, v)
        p = (1 - j) * p + 0.5 * j * (np.roll(p, 1) + np.roll(p, -1))
    window = np.roll(f, 1) + f + np.roll(f, -1)           # window[x] = f[x-1] + f[x] + f[x+1]
    return float(p @ window)


def jobs():
    from prometheus.cosmos.c4 import exp01 as E
    return [{"key": f"stig:{i}", "i": i, "knobs": E.sample_world("stig", FW.split_seed("DISCOVERY", 4, 800000 + i))["knobs"]}
            for i in range(60)]


def one(j: dict) -> dict:
    from prometheus.cosmos.c3.substrates import Stig
    from prometheus.cosmos.c3.task import Task
    from prometheus.cosmos.c4.cert_b import b_use
    from prometheus.cosmos.hashing import h
    kn = j["knobs"]
    seed = int(h({"EXP-09": j["i"]})[:8], 16)
    acc = []
    for k in KS:
        t = Task(V, k)
        acc.append(float(b_use(Stig(t, kn["delta"], kn["D"], kn["v"], kn["j"], L=L), t, "linear", seed=seed + k)["acc"]))
    return {**j, "acc": acc}


def run(rundir: str, workers: int = 3):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="exp09.jsonl", workers=workers, max_failures=0)


def analyse(rundir: str) -> dict:
    from scipy.stats import spearmanr
    rows = [json.loads(x) for x in (Path(rundir) / "exp09.jsonl").read_text().splitlines() if x.strip()]
    per = []
    for r in rows:
        kn = r["knobs"]
        if kn["v"] < 1:
            continue
        ex = (np.asarray(r["acc"]) - .25) / .75
        sc = [spread_score(kn["delta"], kn["D"], kn["v"], kn["j"], k) for k in KS]
        rr = [R(kn["v"], k, L) for k in KS]
        s_sp = spearmanr(sc, ex).statistic
        s_r = spearmanr(rr, ex).statistic
        per.append({"i": r["i"], "D": kn["D"], "s_spread": float(s_sp), "s_return": float(s_r)})
    def med(x):
        return float(np.nanmedian(x)) if len(x) else float("nan")
    out = {}
    for name, sub in (("all", per), ("D>=.1", [p for p in per if p["D"] >= .1])):
        a, b = med([p["s_spread"] for p in sub]), med([p["s_return"] for p in sub])
        out[name] = {"n": len(sub), "median_spearman_spread": a, "median_spearman_return": b,
                     "passes": a >= .5 and a - b >= .1}
    out["verdict"] = "H-SPREAD SUPPORTED" if out["all"]["passes"] and out["D>=.1"]["passes"] else "H-SPREAD REJECTED"
    return out


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 3)
    elif a[1] == "analyse":
        print(json.dumps(analyse(a[2]), indent=1))
