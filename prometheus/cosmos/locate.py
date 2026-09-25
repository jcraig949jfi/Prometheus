"""Boundary-LOCATION attack: where is the transition, versus where the law says it is?

The confident-contradiction adversary cannot see a law whose boundary is shifted by less than
its own transition band: every world near the true boundary is "uncertain" to the law. This
attack measures the location directly (charter s XI: characterise transition location, then
attack the estimate):

  for n_bases confidently-PAYS pool worlds per family, along do(cost_knob: a -> a f):
    f_pred  = the law's upper flip (broker.two_sided_flips on the world's coordinates)
    ladder  = f_pred * linspace(0.6, 1.4, 33), 1600 episodes, common random numbers (seed key =
              the base world id)
    f_obs   = maximum-likelihood logistic location of PAYS along the ladder
    delta   = log2(f_obs / f_pred)
  summary per family and pooled: mean delta, its standard error, and the verdict
    LOCATION_BIASED  if |mean delta| > max(2 SE, TOL)       (TOL = 0.05 in log2, ~3.5%)
    LOCATION_OK      otherwise
    INDETERMINATE    if fewer than 4 bases yielded a flip inside the ladder
The ladder resolution (0.025 of f_pred, ~0.035 log2) is below TOL, so the verdict is attainable.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.boundary import _fit
from prometheus.cosmos.broker import two_sided_flips
from prometheus.cosmos.contract import coords_of
from prometheus.cosmos.world import evaluate, world_id

TOL = 0.05


def locate(law, fams: Dict[str, Any], pools: Dict[str, List[Dict[str, Any]]], cmap: str, rng, n_bases: int = 8,
           episodes: int = 1600, campaign: str = "locate") -> Dict[str, Any]:
    CK = {"v1": "coords", "v2": "coords_v2", "v3": "coords_v3", "v4": "coords_v4"}[cmap]
    per_fam: Dict[str, Any] = {}
    all_d: List[float] = []
    for f, P in pools.items():
        fam = fams[f]
        X = {k: np.array([r[CK][k] for r in P]) for k in P[0][CK]}
        pp = law.prob(X)
        conf = np.nonzero(pp >= 0.9)[0]
        rng.shuffle(conf)
        rows = []
        for i in conf:
            if len(rows) >= n_bases:
                break
            base = P[i]["params"]
            fl = two_sided_flips(law, P[i][CK])
            if fl["f_hi"] is None or fl["f_hi"] > 30:
                continue
            fs = fl["f_hi"] * np.linspace(0.6, 1.4, 33)
            key = world_id(fam, base)
            ys = []
            for fct in fs:
                p = dict(base, **{fam.cost_knob: base[fam.cost_knob] * float(fct)})
                ys.append(int(evaluate(fam, p, episodes=episodes, campaign=campaign, seed_key=key)["verdict"] == "PAYS"))
            ys = np.array(ys)
            if ys.min() == ys.max():
                rows.append({"base": base, "f_pred": fl["f_hi"], "f_obs": None, "note": "no flip inside the ladder",
                             "all_pays": bool(ys.max() == 1)})
                continue
            fit = _fit(np.log(fs), ys)
            d = float(np.log2(fit["x0"] / fl["f_hi"]))
            rows.append({"base": base, "coords": P[i][CK], "f_pred": fl["f_hi"], "f_obs": fit["x0"], "delta_log2": d})
            all_d.append(d)
        ds = [r["delta_log2"] for r in rows if r.get("f_obs")]
        per_fam[f] = _summ(ds)
        per_fam[f]["rows"] = rows
    pooled = _summ(all_d)
    return {"per_family": per_fam, "pooled": pooled, "tol_log2": TOL}


def _summ(ds: List[float]) -> Dict[str, Any]:
    if len(ds) < 4:
        return {"n": len(ds), "verdict": "INDETERMINATE"}
    m = float(np.mean(ds))
    se = float(np.std(ds, ddof=1) / np.sqrt(len(ds)))
    v = "LOCATION_BIASED" if abs(m) > max(2 * se, TOL) else "LOCATION_OK"
    return {"n": len(ds), "mean_delta_log2": m, "se": se, "verdict": v}
