"""eta2: budget-matched RANDOM vs COST-LINES sampling (roles/Cosmos/campaigns/eta2/PREREG.md).

  python -m prometheus.cosmos.eta2 <out_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.campaign0 import build_pools
from prometheus.cosmos.contract import terminals_for
from prometheus.cosmos.locate import locate
from prometheus.cosmos.miner import Miner
from prometheus.cosmos.pipeline import Chamber, design
from prometheus.cosmos.sampler import costlines
from prometheus.cosmos.stress import pool_rows
from prometheus.cosmos.substrates import visible

CMAP = "v4"


def _ba(p, y):
    p, y = np.asarray(p, bool), np.asarray(y)
    return float(0.5 * ((p & (y == 1)).sum() / max(1, (y == 1).sum()) + (~p & (y == 0)).sum() / max(1, (y == 0).sum())))


def _law(rows):
    X, y, g, _ = design(rows, CMAP)
    M = Miner(X, y, g, terminals=terminals_for(CMAP))
    best, _ = M.search(y)
    if best is None:
        return None
    return M.refit(best.structure(), X, y)


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    fams = visible()
    pools = pool_rows(fams, build_pools(fams, 600, 20260930))
    orc = Chamber(list(fams.values()), campaign="eta2-oracle")
    oracle = {f: [orc.observe(f, r["params"], keep=False) for r in P] for f, P in pools.items()}
    Xo, yo, _, _ = design([r for f in oracle for r in oracle[f]], CMAP)
    res = []
    for seed in (1, 2, 3):
        rng = np.random.default_rng(seed)
        arms = {}
        lines_ch = Chamber(list(fams.values()), campaign="eta2")
        rand_ch = Chamber(list(fams.values()), campaign="eta2")
        for f, P in pools.items():
            idx = rng.permutation(len(P))
            bases = [P[i]["params"] for i in idx[:3]]
            for b in bases:
                lines_ch.observe(f, b)
            costlines(lines_ch, f, bases)
            q = sum(1 for r in lines_ch.rows if r["family"] == f)
            for i in idx[3:3 + q]:
                rand_ch.observe(f, P[i]["params"])
        for name, ch in (("RANDOM", rand_ch), ("LINES", lines_ch)):
            L = _law(ch.rows)
            if L is None:
                arms[name] = {"law": None}
                continue
            loc = locate(L, fams, pools, CMAP, np.random.default_rng(100 + seed), n_bases=4, episodes=800, campaign="eta2-loc")
            offs = {f: (abs(r["mean_delta_log2"]) if r.get("verdict") in ("LOCATION_OK", "LOCATION_BIASED") else 0.5)
                    for f, r in loc["per_family"].items()}
            arms[name] = {"n_rows": len(ch.rows), "law": L.show(), "oracle_ba": _ba(L.predict(Xo), yo),
                          "worst_offset": max(offs.values()), "offsets": offs}
        res.append({"seed": seed, **arms})
        print(json.dumps(res[-1]), flush=True)
    summ = {}
    for arm in ("RANDOM", "LINES"):
        v = [r[arm] for r in res if r[arm].get("law")]
        summ[arm] = {"mean_oracle_ba": float(np.mean([x["oracle_ba"] for x in v])) if v else None,
                     "mean_worst_offset": float(np.mean([x["worst_offset"] for x in v])) if v else None, "n": len(v)}
    d_ba = summ["LINES"]["mean_oracle_ba"] - summ["RANDOM"]["mean_oracle_ba"]
    d_off = summ["RANDOM"]["mean_worst_offset"] - summ["LINES"]["mean_worst_offset"]
    summ["prediction_held"] = bool(d_ba >= 0.02 or d_off >= 0.05)
    summ["delta_ba"], summ["delta_worst_offset"] = d_ba, d_off
    (out / "ETA2.json").write_text(json.dumps({"runs": res, "summary": summ}, indent=1), encoding="utf-8")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
