"""F15 capacity scaling (prereg roles/Cosmos/campaigns/NS-01_2026-10-11/PREREG_F15_CAPACITY.md)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

WIDTHS = (128, 256, 512, 1024, 2048, 4096)
MS = (1, 2, 4, 8, 16, 32, 64)


def one(j):
    from prometheus.cosmos.c3.task import Task
    from prometheus.cosmos.c4.cert_b import _Ridge
    from prometheus.cosmos.ns01.f15 import RelationalWitness
    from prometheus.cosmos.ns01.signature import _episodes, excess
    rng = np.random.default_rng([0xCA9, j["M"], j["n_train"]])
    k, t = 4, Task(4, 4)
    s = RelationalWitness(t, M=j["M"])

    def run(obs):
        st = s.init(obs.shape[0])
        for i in range(obs.shape[1]):
            st = s.step(st, obs[:, i], s.noise(obs.shape[0], rng))
        F = np.asarray(s.full_state(st), float)[:, :-1]
        return np.hstack([np.eye(4)[np.rint(F[:, c]).astype(int) % 4] for c in range(F.shape[1])])

    ctr, otr = _episodes(k, j["n_train"], rng)
    cte, ote = _episodes(k, 2000, rng)
    Xtr, Xte = run(otr), run(ote)
    out = {}
    for w in j["widths"]:
        m = _Ridge(4, rf=w, seed=1).fit(Xtr, ctr)
        out[str(w)] = excess(float((m.predict(Xte) == cte).mean()))
    return {"key": j["key"], "M": j["M"], "n_train": j["n_train"], "excess_by_width": out}


def run(rundir):
    from prometheus.cosmos import supervise as SV
    jobs = [{"key": f"M{M}:n4000", "M": M, "n_train": 4000, "widths": list(WIDTHS)} for M in MS]
    jobs += [{"key": f"M{M}:n16000", "M": M, "n_train": 16000, "widths": [512]} for M in MS]
    return SV.run_jobs(one, jobs, rundir, key="key", out="capacity.jsonl", workers=2, max_failures=0)


def analyse(rundir):
    rows = [json.loads(x) for x in Path(rundir, "capacity.jsonl").read_text().splitlines() if x.strip()]
    base = {r["M"]: r for r in rows if r["n_train"] == 4000}
    big = {r["M"]: r for r in rows if r["n_train"] == 16000}
    wstar = {}
    for M in MS:
        ok = [w for w in WIDTHS if base[M]["excess_by_width"][str(w)] >= .90]
        wstar[M] = min(ok) if ok else None
    pts = [(np.log2(M), np.log2(wstar[M])) for M in MS if M >= 4 and wstar[M]]
    slope = float(np.polyfit(*zip(*pts), 1)[0]) if len(pts) >= 2 else None
    censored = [M for M in MS if wstar[M] is None]
    rescued = all(big[M]["excess_by_width"]["512"] >= .90 for M in censored) if censored else None
    if not censored and slope is not None and slope <= 1.0:
        v = "MERGE (F15 -> KNOWN decoder-capacity dependence)"
    elif (slope is not None and slope > 1.0) or (censored and not rescued):
        v = "KEEP_DISTINCT (relational dilution)"
    else:
        v = "INCONCLUSIVE"
    return {"wstar": wstar, "slope_log2w_vs_log2M_(M>=4)": slope, "censored_M": censored,
            "n16000_w512": {M: big[M]["excess_by_width"]["512"] for M in MS},
            "table_n4000": {M: base[M]["excess_by_width"] for M in MS}, "verdict": v}


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2])
    else:
        print(json.dumps(analyse(a[2]), indent=1))
