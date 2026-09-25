"""Family F (SEALED HOLDOUT #3) -- CLONE: memory carried by a stochastic birth-death clone.

Physics: a retained symbol is carried by a clone of cells founded with n0 cells. Each tick every
living cell independently divides with probability b and dies with probability d (discrete-time
linear birth-death; b + d <= 1). All cells of a clone carry the symbol exactly (no mutation). A
clone that goes extinct loses the symbol and STOPS COSTING. Every living cell costs c_cell per
tick. Readout: the cue's clone symbol if the clone is alive, else 0. No capacity limit.

Mechanisms:
  SEL   found one clone (n0 cells) on the tagged input
  LOG   found one clone per observation
  LAST  found nothing ; emit 0

Declared coordinates (spec only; exact for the discrete linear birth-death chain):
  m = 1 + b - d (mean offspring factor per tick); per-cell extinction by tick t, q_t, obeys
  q_{t+1} = d + (1 - b - d) q_t + b q_t^2,  q_0 = 0 ; clone survival S = 1 - q_H^n0
  C  v1-v3 = c_cell * n0 * H / R                       (the cost if the clone stayed at n0)
     v4    = c_cell * n0 * (sum_{t=1..H} m^t) / R       (the EXPECTED cost: E[cells at t] = n0 m^t)
  N  = -ln S   (all maps)
  K, G = 1 - 1/V ; slots None (Q = 1)

Import only inside the broker subprocess (COSMOS_BROKER=1).
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import Family

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("the sealed holdout family is reachable only through the broker subprocess")


class Clone(Family):
    name = "clone"
    version = "1"
    lineage = ("prometheus/cosmos/holdout/clone.py",)
    cost_knob = "c_cell"

    def space(self) -> Dict[str, List[Any]]:
        return {
            "V": [2, 4, 8],
            "H": [8, 16, 24],
            "K": [0, 1, 2, 4, 6],
            "R": [1.0, 3.0],
            "n0": [1, 2, 4, 8],
            "b": [0.0, 0.02, 0.05, 0.1],
            "d": [0.0, 0.02, 0.05, 0.1, 0.2],
            "c_cell": [1e-4, 3e-4, 1e-3, 2e-3, 4e-3, 8e-3, 1.6e-2, 3.2e-2, 6.4e-2],
        }

    @staticmethod
    def _survival(p) -> float:
        b, d, H, n0 = p["b"], p["d"], p["H"], p["n0"]
        q = 0.0
        for _ in range(H):
            q = d + (1 - b - d) * q + b * q * q
        return 1.0 - q ** n0

    def coords(self, p: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        S = self._survival(p)
        N = -math.log(S) if S > 0 else float("inf")
        m = 1 + p["b"] - p["d"]
        if cmap == "v4":
            cost_units = p["n0"] * sum(m ** t for t in range(1, p["H"] + 1))
        else:
            cost_units = p["n0"] * p["H"]
        return {"C": p["c_cell"] * cost_units / p["R"], "N": N, "K": float(p["K"]), "G": 1.0 - 1.0 / p["V"]}

    def units(self, p: Dict[str, Any]) -> Dict[str, float]:
        return {"reward_per_success": float(p["R"])}

    def run(self, p: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        V, H, K, R, n0, b, d, cc = (p[k] for k in ("V", "H", "K", "R", "n0", "b", "d", "c_cell"))
        E = episodes
        g = np.random.default_rng(seed)
        cue = g.integers(0, V, E)
        arr = np.sort(np.argsort(g.random((E, H - 1)), axis=1)[:, :K] + 1, axis=1) if K else np.zeros((E, 0), int)
        _ = g.integers(0, V, (E, K))
        target = g.integers(0, V, E) if p.get("sham") else cue
        dyn = np.random.default_rng(seed * 13 + 5)
        if mech == "LAST":
            return {"reward": np.where(target == 0, R, 0.0), "cost": np.zeros(E), "cell_ticks": np.zeros(E)}
        P = 1 if mech == "SEL" else 1 + K
        n = np.zeros((E, P), dtype=np.int64)
        n[:, 0] = n0
        cell_ticks = np.zeros(E)
        for t in range(1, H + 1):
            if mech == "LOG":
                for j in range(K):
                    on = arr[:, j] == t
                    n[on, 1 + j] = n0
            # each living cell: divide w.p. b, die w.p. d (exclusive), else persist
            births = dyn.binomial(n, b)
            deaths = dyn.binomial(n - births, d / (1 - b)) if b < 1 else np.zeros_like(n)
            n = n + births - deaths
            cell_ticks += n.sum(axis=1)
        out = np.where(n[:, 0] > 0, cue, 0)
        return {"reward": np.where(out == target, R, 0.0), "cost": cell_ticks * cc, "cell_ticks": cell_ticks}

    def with_cost_factor(self, p: Dict[str, Any], f: float) -> Dict[str, Any]:
        return dict(p, c_cell=p["c_cell"] * f)


FAMILY = Clone()
