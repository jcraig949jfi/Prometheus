"""Family B -- RING: a delay-line network.

Physics: a ring of n nodes. A retained observation exists only as a packet in
flight. Each tick every live packet makes s hops; each hop costs `ehop`
currency and independently destroys the packet with probability `lam`. A
destroyed packet stops costing (a dead memory is free). The ring holds at most
n packets; injecting into a full ring evicts the OLDEST packet. Packets carry
their symbol exactly (loss, never corruption).

Mechanisms:
  SEL   inject the tagged input only ; at ask: emit the cue packet's symbol, 0 if gone
  LOG   inject every input ; at ask: emit the first packet's symbol, 0 if gone/evicted
  LAST  inject nothing ; at ask: emit 0

Self-contained: numpy + the contract signatures only.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.contract import Family


class Ring(Family):
    name = "ring"
    version = "1"
    lineage = ("prometheus/cosmos/substrates/ring.py",)
    cost_knob = "ehop"

    def space(self) -> Dict[str, List[Any]]:
        return {
            "V": [2, 4, 8, 16],
            "H": [6, 12, 24],
            "K": [0, 1, 2, 4, 5],
            "R": [1.0, 5.0],
            "s": [1, 3],
            "n": [3, 64],
            "ehop": [3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 6e-3, 1.2e-2, 2.4e-2, 5e-2, 0.1],
            "lam": [0.0, 0.002, 0.006, 0.02, 0.05, 0.1],
        }

    def coords(self, p: Dict[str, Any], cmap: str = "v1") -> Dict[str, float]:
        hops = p["s"] * p["H"]
        return {"C": p["ehop"] * hops / p["R"], "N": p["lam"] * hops, "K": float(p["K"]), "G": 1.0 - 1.0 / p["V"]}

    def units(self, p: Dict[str, Any]) -> Dict[str, float]:
        return {"reward_per_success": float(p["R"])}

    def run(self, p: Dict[str, Any], mech: str, seed: int, episodes: int) -> Dict[str, Any]:
        V, H, K, R, s, n, eh, lam = p["V"], p["H"], p["K"], p["R"], p["s"], p["n"], p["ehop"], p["lam"]
        E = episodes
        rs = np.random.default_rng(seed)
        cue = rs.integers(0, V, E)
        arrive = np.sort(np.argsort(rs.random((E, H - 1)), axis=1)[:, :K] + 1, axis=1) if K else np.zeros((E, 0), int)
        _ = rs.integers(0, V, (E, K))           # distractor symbols (carried exactly; only order matters here)
        target = rs.integers(0, V, E) if p.get("sham") else cue
        wear = np.random.default_rng(seed + 7919)

        hops_done = np.zeros(E)
        if mech == "LAST":
            emitted = np.zeros(E, dtype=np.int64)
        else:
            P = 1 if mech == "SEL" else 1 + K
            alive = np.zeros((E, P), dtype=bool)
            born = np.full((E, P), 10 ** 9)
            alive[:, 0] = True
            born[:, 0] = 0
            evicted0 = np.zeros(E, dtype=bool)
            for t in range(1, H + 1):
                if mech == "LOG":
                    for j in range(K):
                        inj = arrive[:, j] == t
                        if not inj.any():
                            continue
                        full = alive.sum(axis=1) >= n
                        ev = inj & full
                        if ev.any():
                            b2 = np.where(alive, born, 10 ** 9)
                            oldest = b2.argmin(axis=1)
                            rows = np.nonzero(ev)[0]
                            alive[rows, oldest[rows]] = False
                            evicted0 |= ev & (oldest == 0)
                        alive[inj, 1 + j] = True
                        born[inj, 1 + j] = t
                # every live packet attempts s hops; the hop that fails is still paid
                for _h in range(s):
                    hops_done += alive.sum(axis=1)
                    if lam > 0:
                        alive &= wear.random(alive.shape) >= lam
            emitted = np.where(alive[:, 0], cue, 0)
        reward = np.where(emitted == target, R, 0.0)
        return {"reward": reward, "cost": hops_done * eh, "hops": hops_done}

    def slots(self, p: Dict[str, Any]):
        return p["n"]

    def coord_preserving(self, p: Dict[str, Any], rng) -> List[Dict[str, Any]]:
        out = []
        for s2 in (1, 2, 3, 6):
            if s2 != p["s"]:
                f = p["s"] / s2
                out.append(dict(p, s=s2, ehop=p["ehop"] * f, lam=p["lam"] * f))
        out.append(dict(p, R=p["R"] * 10, ehop=p["ehop"] * 10))
        # capacity is NOT a declared coordinate; a variant that changes only n is coordinate-preserving
        out.append(dict(p, n=3 if p["n"] != 3 else 64))
        return out


FAMILY = Ring()
