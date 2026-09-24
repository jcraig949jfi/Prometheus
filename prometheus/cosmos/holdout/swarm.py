"""Family E (SEALED HOLDOUT #2) -- SWARM: collective memory in a population of agents.

Physics: a retained symbol is carried by a population of M agents, each holding a symbol.
Every tick: (1) each agent is independently CORRUPTED with probability u (its symbol replaced by
a uniform random symbol); (2) each agent samples 3 agents of its own population uniformly with
replacement and adopts the majority symbol of the sample if one exists (else keeps its own).
Readout = the population's plurality symbol (ties -> lowest symbol). Maintaining an agent costs
c_agent currency per tick. The colony has a total agent budget A_max: at most A_max // M
populations can exist at once; founding a population beyond that dissolves the OLDEST one.

Mechanisms:
  SEL   found one population on the tagged input ; readout at the ask
  LOG   found one population per observation ; readout of the cue's population (0 if dissolved)
  LAST  found nothing ; emit 0

Declared coordinates (spec only; v2 is a crude binomial approximation, deliberately):
  C  = c_agent * M * H / R
  N  v1 = u * M * H                         (raw corruption events on the population)
     v2 = H * binom(M, m) * u^m, m = (M+1)//2  (a majority corrupted within one tick)
  K, G = 1 - 1/V ; slots = A_max // M  (-> Q under coordinate map v3)

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


class Swarm(Family):
    name = "swarm"
    version = "1"
    lineage = ("prometheus/cosmos/holdout/swarm.py",)

    def space(self) -> Dict[str, List[Any]]:
        return {
            "V": [2, 4, 8],
            "H": [8, 16, 32],
            "K": [0, 1, 2, 4, 6],
            "R": [1.0, 4.0],
            "M": [1, 3, 5, 9],
            "u": [0.0, 0.002, 0.006, 0.02, 0.05],
            "c_agent": [1e-4, 3e-4, 1e-3, 2e-3, 4e-3, 8e-3, 1.6e-2, 3.2e-2, 6.4e-2],
            "A_max": [9, 27, 1000],
        }

    def coords(self, p: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        M, H, u = p["M"], p["H"], p["u"]
        if cmap == "v1":
            n = u * M * H
        else:
            m = (M + 1) // 2
            n = H * math.comb(M, m) * u ** m
        return {"C": p["c_agent"] * M * H / p["R"], "N": n, "K": float(p["K"]), "G": 1.0 - 1.0 / p["V"]}

    def slots(self, p: Dict[str, Any]):
        return p["A_max"] // p["M"]

    def units(self, p: Dict[str, Any]) -> Dict[str, float]:
        return {"reward_per_success": float(p["R"])}

    def run(self, p: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        V, H, K, R, M, u, ca, Amax = (p[k] for k in ("V", "H", "K", "R", "M", "u", "c_agent", "A_max"))
        E = episodes
        g = np.random.default_rng(seed)
        cue = g.integers(0, V, E)
        arr = np.sort(np.argsort(g.random((E, H - 1)), axis=1)[:, :K] + 1, axis=1) if K else np.zeros((E, 0), int)
        dv = g.integers(0, V, (E, K))
        target = g.integers(0, V, E) if p.get("sham") else cue
        life = np.random.default_rng(seed * 7 + 3)
        if mech == "LAST" or M > Amax:
            return {"reward": np.where(target == 0, R, 0.0), "cost": np.zeros(E), "agent_ticks": np.zeros(E)}
        P = 1 if mech == "SEL" else 1 + K
        slots = Amax // M
        S = np.zeros((E, P, M), dtype=np.int64)
        alive = np.zeros((E, P), dtype=bool)
        born = np.full((E, P), 10 ** 9)
        S[:, 0, :] = cue[:, None]
        alive[:, 0] = True
        born[:, 0] = 0
        agent_ticks = np.zeros(E)
        for t in range(1, H + 1):
            if mech == "LOG":
                for j in range(K):
                    on = arr[:, j] == t
                    if not on.any():
                        continue
                    full = alive.sum(axis=1) >= slots
                    ev = on & full
                    if ev.any():
                        b2 = np.where(alive, born, 10 ** 9)
                        old = b2.argmin(axis=1)
                        rows = np.nonzero(ev)[0]
                        alive[rows, old[rows]] = False
                    S[on, 1 + j, :] = dv[on, j][:, None]
                    alive[on, 1 + j] = True
                    born[on, 1 + j] = t
            if u > 0:
                hit = life.random((E, P, M)) < u
                S = np.where(hit, life.integers(0, V, (E, P, M)), S)
            if M > 1:
                idx = life.integers(0, M, (E, P, M, 3))
                a = np.take_along_axis(S[:, :, None, :].repeat(M, axis=2), idx[..., 0:1], axis=3)[..., 0]
                b = np.take_along_axis(S[:, :, None, :].repeat(M, axis=2), idx[..., 1:2], axis=3)[..., 0]
                c = np.take_along_axis(S[:, :, None, :].repeat(M, axis=2), idx[..., 2:3], axis=3)[..., 0]
                S = np.where((a == b) | (a == c), a, np.where(b == c, b, S))
            agent_ticks += alive.sum(axis=1) * M
        counts = (S[:, 0, :, None] == np.arange(V)[None, None, :]).sum(axis=1)
        read = np.where(alive[:, 0], counts.argmax(axis=1), 0)
        return {"reward": np.where(read == target, R, 0.0), "cost": agent_ticks * ca, "agent_ticks": agent_ticks}

    def with_cost_factor(self, p: Dict[str, Any], f: float) -> Dict[str, Any]:
        return dict(p, c_agent=p["c_agent"] * f)


FAMILY = Swarm()
