"""Physics-preserving re-encodings of visible families (thread T-C1).

EgoStig is the C3 stig family written in the AGENT'S FRAME: the field is stored relative to the agent, so the
agent never moves and the field is transported by -(v + jitter) cells per step. The dynamics are isomorphic to
Stig with pos = 0 (an exact relabelling of state; same noise, same readout window); only the state's coordinate
frame changes. A law or coordinate that changes between Stig and EgoStig depends on representation, not physics.
"""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.c3.substrates import Stig
from prometheus.cosmos.c3.task import onehot


class EgoStig(Stig):
    family = "stig_ego"

    def init(self, E):
        return {"g": np.zeros((E, self.L, self.C)), "cur": np.zeros(E, dtype=np.int64)}

    def step(self, st, o, nz):
        g = st["g"] * (1 - self.delta)
        if self.D > 0:
            g = (1 - self.D) * g + 0.5 * self.D * (np.roll(g, 1, axis=1) + np.roll(g, -1, axis=1))
        E = len(o)
        g = g.copy()
        g[np.arange(E), 0, o] += self.w
        move = self.v + np.where(nz["jit"] < self.j, nz["dir"], 0)
        idx = (np.arange(self.L)[None, :] + move[:, None]) % self.L        # new g[i] = old g[i + move]
        g = g[np.arange(E)[:, None], idx]
        return {"g": g, "cur": o.copy()}

    def _sense(self, st):
        return np.hstack([st["g"][:, d % self.L] for d in (-1, 0, 1)])

    def full_state(self, st):
        return np.hstack([st["g"].reshape(len(st["cur"]), -1), onehot(st["cur"], self.C)])
