"""Planted family ps1 -- imports the shared helper on purpose."""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.contract import Family
from prometheus.cosmos.planted._shared import shared_margin, shared_rewards


class Planted(Family):
    version = "1"
    lineage = ("prometheus/cosmos/planted/ps1.py",)

    def __init__(self, scenario: str = "shared"):
        self.scenario = scenario
        self.name = "ps1:" + scenario

    def space(self):
        return {"C": list(np.round(np.geomspace(0.02, 1.2, 14), 4)), "N": [0.0, 0.2, 0.4, 0.7, 1.0, 1.5],
                "K": [0, 1, 2, 4, 8], "G": [0.5, 0.75, 0.875, 0.9375], "u": [0.0]}

    def coords(self, p, cmap="v1"):
        return {"C": float(p["C"]), "N": float(p["N"]), "K": float(p["K"]), "G": float(p["G"])}

    def units(self, p):
        return {"reward_per_success": 1.0}

    def run(self, p, mech, seed, episodes):
        prob = float(np.clip(0.5 + shared_margin(p["N"]), 0, 1)) if mech == "SEL" else 0.5
        return {"reward": shared_rewards(prob, seed + (1 if mech == "SEL" else 2 if mech == "LOG" else 3), episodes),
                "cost": np.zeros(episodes)}
