"""Location-aware law selection (roles/Cosmos/campaigns/c2/PREREG.md).

LOLO balanced accuracy is nearly flat across near-tied candidate laws whose upper boundaries differ
by 30% in cost. Among the near-top candidates of each coordinate map's search, refit each on all
rows, measure per-family upper-flip offsets with the location attack, and keep the candidate with
the smallest worst-family |offset|. Every candidate's measurements are returned (the alternatives
are part of the record, not discarded).
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import terminals_for
from prometheus.cosmos.locate import locate
from prometheus.cosmos.miner import Miner, deser
from prometheus.cosmos.pipeline import design

WINDOW = 0.03
PER_MAP = 6
INDET_PENALTY = 0.5


def candidates(mined: Dict[str, Dict[str, Any]], maps) -> List[Dict[str, Any]]:
    out = []
    for cm in maps:
        res = mined.get(cm)
        if not res or res.get("p_null", 1) > 0.05 or not res.get("top"):
            continue
        best = max(t["score"] for t in res["top"] if t.get("passes_worst_gate"))  if any(t.get("passes_worst_gate") for t in res["top"]) else None
        if best is None:
            continue
        k = 0
        for t in res["top"]:
            if not t.get("passes_worst_gate") or t["score"] < best - WINDOW:
                continue
            out.append({"cmap": cm, "atoms": t["atoms"], "structure": t["structure"], "lolo_score": t["score"],
                        "fold_ba": t["fold_ba"], "p_null": res["p_null"]})
            k += 1
            if k >= PER_MAP:
                break
    return out


def select(cands: List[Dict[str, Any]], rows, fams, pool_rows, rng, n_bases: int = 6, episodes: int = 800) -> Dict[str, Any]:
    scored = []
    for c in cands:
        X, y, g, _ = design(rows, c["cmap"])
        M = Miner(X, y, g, terminals=terminals_for(c["cmap"]), max_size=3, conj=False)   # refit only; tiny grammar
        structure = [(deser(a), d) for a, d in c["atoms"]]
        L = M.refit(structure, X, y)
        loc = locate(L, fams, pool_rows, c["cmap"], rng, n_bases=n_bases, episodes=episodes, campaign="c2-select")
        offs = {}
        for f, r in loc["per_family"].items():
            offs[f] = abs(r["mean_delta_log2"]) if r.get("verdict") in ("LOCATION_OK", "LOCATION_BIASED") else INDET_PENALTY
        worst = max(offs.values()) if offs else INDET_PENALTY
        lj = L.to_json()
        lj["fold_ba"], lj["score"] = c["fold_ba"], c["lolo_score"]
        scored.append({**c, "law": lj, "offsets": offs, "worst_offset": worst,
                       "locate": {f: {k: v for k, v in r.items() if k != "rows"} for f, r in loc["per_family"].items()}})
    if not scored:
        return {"chosen": None, "scored": []}
    chosen = min(scored, key=lambda s: (s["worst_offset"], -s["lolo_score"]))
    return {"chosen": chosen, "scored": [{k: v for k, v in s.items() if k != "atoms"} for s in scored]}
