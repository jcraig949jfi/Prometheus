"""EXP-05: stig ring RETURN vs ACCUMULATION (exploratory; prereg roles/Cosmos/c4/prereg/EXP-05_STIG_RETURN_VS_ACCUM.md).

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.c4.exp05 run <rundir> [workers]
    python -m prometheus.cosmos.c4.exp05 analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c4 import firewall as FW

KS = tuple(range(1, 41))
LS = (16, 24)
V = 4


def R(v: int, k: int, L: int) -> int:
    d = (v * (k + 2)) % L
    return int(min(d, L - d) <= 1)


def jobs():
    from prometheus.cosmos.c4 import exp01 as E
    out = []
    for i in range(60):
        w = E.sample_world("stig", FW.split_seed("DISCOVERY", 3, 500000 + i))
        for L in LS:
            out.append({"key": f"stig:{i}:L{L}", "family": "stig", "i": i, "knobs": w["knobs"], "L": L})
    for fam, base in (("rnn", 600000), ("phase", 700000)):
        for i in range(20):
            w = E.sample_world(fam, FW.split_seed("DISCOVERY", 3, base + i))
            out.append({"key": f"{fam}:{i}", "family": fam, "i": i, "knobs": w["knobs"], "L": None})
    return out


def one(j: dict) -> dict:
    from prometheus.cosmos.c3.substrates import Stig
    from prometheus.cosmos.c3.task import Task
    from prometheus.cosmos.c4 import exp01 as E
    from prometheus.cosmos.c4.cert_b import b_use
    from prometheus.cosmos.hashing import h
    seed = int(h({"EXP-05": j["family"], "i": j["i"]})[:8], 16)          # same seed for L16 and L24 (held)
    acc = []
    for k in KS:
        if j["family"] == "stig":
            kn = j["knobs"]
            t = Task(V, k)
            s = Stig(t, kn["delta"], kn["D"], kn["v"], kn["j"], L=j["L"])
        else:
            s, t = E.build(j["family"], j["knobs"], k)
        acc.append(float(b_use(s, t, "linear", seed=seed + k)["acc"]))
    return {**j, "acc": acc}


def run(rundir: str, workers: int = 3):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="exp05.jsonl", workers=workers, max_failures=0)


def _ex(a):
    return (np.asarray(a, float) - 1.0 / V) / (1.0 - 1.0 / V)


def _pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def analyse(rundir: str) -> dict:
    from scipy.stats import spearmanr
    rows = [json.loads(x) for x in (Path(rundir) / "exp05.jsonl").read_text().splitlines() if x.strip()]
    st = {}
    for r in rows:
        if r["family"] == "stig":
            st.setdefault(r["i"], {})[r["L"]] = r
    per = []
    for i, d in sorted(st.items()):
        kn = d[16]["knobs"]
        e16, e24 = _ex(d[16]["acc"]), _ex(d[24]["acc"])
        R16 = [R(kn["v"], k, 16) for k in KS]
        R24 = [R(kn["v"], k, 24) for k in KS]
        per.append({"i": i, "v": kn["v"], "delta": kn["delta"], "D": kn["D"], "j": kn["j"],
                    "r16": _pearson(e16, R16), "r24": _pearson(e24, R24), "r24x": _pearson(e24, R16),
                    "rho_k": float(spearmanr(KS, e16).statistic), "dL": float(np.mean(np.abs(e24 - e16))),
                    "mean16": float(e16.mean())})
    mv = [p for p in per if p["v"] >= 1]
    med = lambda x: float(np.nanmedian(x)) if len(x) else float("nan")
    m16, m24 = med([p["r16"] for p in mv]), med([p["r24"] for p in mv])
    moved = float(np.mean([p["r24"] > p["r24x"] for p in mv])) if mv else float("nan")
    mrho, mdL = med([p["rho_k"] for p in mv]), med([p["dL"] for p in mv])
    ret = m16 >= .5 and m24 >= .5 and moved >= .7
    acc = mrho >= .5 and mdL < .05
    verdict = ("H-RETURN SUPPORTED" if ret and not acc else "H-ACCUM SUPPORTED" if acc and not ret
               else "INCONCLUSIVE")
    ctrl = {}
    for fam in ("rnn", "phase"):
        rs = [float(spearmanr(KS, _ex(r["acc"])).statistic) for r in rows if r["family"] == fam]
        ctrl[fam] = {"n": len(rs), "median_spearman_k_excess": med(rs)}
    v0 = [p for p in per if p["v"] == 0]
    return {"n_stig": len(per), "n_moving": len(mv), "median_r16": m16, "median_r24": m24,
            "frac_intervention_moves_pattern": moved, "median_spearman_k": mrho, "median_abs_dL": mdL,
            "verdict": verdict, "v0": {"n": len(v0), "median_spearman_k": med([p["rho_k"] for p in v0]),
                                       "median_mean_excess": med([p["mean16"] for p in v0])},
            "controls": ctrl, "per_world": per}


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 3)
    elif a[1] == "analyse":
        out = analyse(a[2])
        print(json.dumps({k: v for k, v in out.items() if k != "per_world"}, indent=1))
