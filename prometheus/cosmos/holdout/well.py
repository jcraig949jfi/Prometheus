"""Family D (SEALED HOLDOUT) -- WELL: continuous overdamped Langevin multi-well attractor.

Physics: a phase variable theta on the circle in the potential
    U(theta) = -(A / V^2) cos(V theta)
with V minima at theta_c = 2 pi c / V (one per symbol), curvature A at the minima
and barrier 2A / V^2. Dynamics (Euler-Maruyama, dt = DT):
    d theta = -(A / V) sin(V theta) dt + sigma dW
Holding a basin open costs power kappa * A per unit time (the barrier is actively
maintained). A retained symbol is lost by thermal escape to a neighbouring basin;
there is no register, no packet, no cell. Readout = nearest minimum.

Mechanisms:
  SEL   one well-system seeded at the cue's minimum ; readout at the ask
  LOG   one well-system per observation (K + 1), each from its arrival ; readout of the cue's
  LAST  no well-system ; emit symbol 0

Declared coordinates (spec only; the Kramers formula is an APPROXIMATION, which is part
of the test: the visible families declare exact hazards):
  C = kappa * A * T / R
  N = 2 * T * (A / 2 pi) * exp(-4 A / (V^2 sigma^2))     (expected escapes, both directions)
  K, G = 1 - 1/V ; v2 == v1 (no repair)

This module must only ever be imported inside the broker's subprocess
(COSMOS_BROKER=1). Importing it anywhere else raises.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import Family

if os.environ.get("COSMOS_BROKER") != "1":
    raise ImportError("the sealed holdout family is reachable only through the broker subprocess")

DT = 0.05


class Well(Family):
    name = "well"
    version = "1"
    lineage = ("prometheus/cosmos/holdout/well.py",)

    def space(self) -> Dict[str, List[Any]]:
        return {
            "V": [2, 4, 8],
            "T": [2.0, 5.0, 10.0],
            "K": [0, 1, 2, 4, 6],
            "R": [1.0, 3.0],
            "A": [1.0, 2.0, 4.0, 8.0],
            "sigma": [0.1, 0.2, 0.3, 0.5, 0.8, 1.2, 1.8, 2.5],
            "kappa": [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 2e-2, 4e-2, 8e-2, 0.16],
        }

    def coords(self, p: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        V, T, A, s = p["V"], p["T"], p["A"], p["sigma"]
        rate = (A / (2 * math.pi)) * math.exp(-4 * A / (V * V * s * s))
        return {"C": p["kappa"] * A * T / p["R"], "N": 2 * T * rate, "K": float(p["K"]), "G": 1.0 - 1.0 / V}

    def units(self, p: Dict[str, Any]) -> Dict[str, float]:
        return {"reward_per_success": float(p["R"])}

    def run(self, p: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        V, T, K, R, A, sg, kp = (p[k] for k in ("V", "T", "K", "R", "A", "sigma", "kappa"))
        E = episodes
        steps = int(round(T / DT))
        env = np.random.default_rng(seed)
        cue = env.integers(0, V, E)
        arr = np.sort(np.argsort(env.random((E, steps - 1)), axis=1)[:, :K] + 1, axis=1) if K else np.zeros((E, 0), int)
        _ = env.integers(0, V, (E, K))
        target = env.integers(0, V, E) if p.get("sham") else cue
        bath = np.random.default_rng(seed + 104729)
        if mech == "LAST":
            return {"reward": np.where(target == 0, R, 0.0), "cost": np.zeros(E), "well_time": np.zeros(E)}
        n = 1 if mech == "SEL" else 1 + K
        theta = np.zeros((E, n))
        active = np.zeros((E, n), dtype=bool)
        theta[:, 0] = 2 * math.pi * cue / V
        active[:, 0] = True
        well_time = np.zeros(E)
        amp = sg * math.sqrt(DT)
        for t in range(1, steps + 1):
            if mech == "LOG":
                for j in range(K):
                    on = arr[:, j] == t
                    active[on, 1 + j] = True           # symbol value irrelevant to the cue's readout
            drift = -(A / V) * np.sin(V * theta)
            theta = np.where(active, theta + drift * DT + amp * bath.standard_normal((E, n)), theta)
            well_time += active.sum(axis=1) * DT
        read = np.mod(np.round(theta[:, 0] * V / (2 * math.pi)).astype(np.int64), V)
        return {"reward": np.where(read == target, R, 0.0), "cost": well_time * kp * A, "well_time": well_time}

    def with_cost_factor(self, p: Dict[str, Any], f: float) -> Dict[str, Any]:
        return dict(p, kappa=p["kappa"] * f)


FAMILY = Well()
