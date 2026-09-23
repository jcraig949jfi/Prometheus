"""Planted family pb (self-contained)."""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.contract import Family


def _margin(scenario, c, n, k, g, u):
    if scenario == "positive":
        return 0.1 + (0.30 - c) * 1.5
    if scenario == "interaction":
        return 0.1 + (c * k - 0.50) * 0.6
    if scenario == "artifact":
        return 0.1 + (0.30 - c) * 1.5
    if scenario == "broken":
        return {"pa": 0.1 + (0.2 - c) * 1.5, "pb": 0.1 + (c - 0.5) * 1.5, "pc": 0.1 + (0.3 - n) * 1.5}["pb"]
    if scenario == "null":
        return 0.3 if u < 0.5 else -0.1
    if scenario == "shared":
        return 0.1 + (0.30 - c) * 1.5
    raise ValueError(scenario)


class Planted(Family):
    version = "1"
    lineage = ("prometheus/cosmos/planted/pb.py",)

    def __init__(self, scenario: str):
        self.scenario = scenario
        self.name = "pb:" + scenario

    def space(self):
        if self.scenario == "artifact":
            lo, hi = 0.1, 0.6
            nlo, nhi = 0.5, 1.0
            return {"C": list(np.round(np.linspace(lo, hi, 12), 4)), "N": list(np.round(np.linspace(nlo, nhi, 6), 4)),
                    "K": [0, 1, 2, 4, 8], "G": [0.5, 0.75, 0.875, 0.9375], "u": [0.0]}
        return {"C": list(np.round(np.geomspace(0.02, 1.2, 14), 4)), "N": [0.0, 0.2, 0.4, 0.7, 1.0, 1.5],
                "K": [0, 1, 2, 4, 8], "G": [0.5, 0.75, 0.875, 0.9375], "u": list(np.round(np.linspace(0, 1, 7), 4))}

    def coords(self, p, cmap="v1"):
        return {"C": float(p["C"]), "N": float(p["N"]), "K": float(p["K"]), "G": float(p["G"])}

    def units(self, p):
        return {"reward_per_success": 1.0}

    def run(self, p, mech, seed, episodes):
        rng = np.random.default_rng(seed + 23)
        if mech == "SEL":
            m = _margin(self.scenario, p["C"], p["N"], p["K"], p["G"], p["u"])
            prob = float(np.clip(0.5 + m, 0.0, 1.0))
        else:
            prob = 0.5
        r = (rng.random(episodes) < prob).astype(float)
        return {"reward": r, "cost": np.zeros(episodes)}
