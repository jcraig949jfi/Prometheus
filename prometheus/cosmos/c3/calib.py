"""Planted calibration systems for the P1/P2 hard gate (S1 PREREG s3). Expected classes:
  N0 NONE, PV PASSIVE, FX FUNCTIONAL, FD FUNCTIONAL, MC NONE (task.h = 0.5), NZ FUNCTIONAL (weak).
"""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class NoMemory(System):
    """State = the current observation only."""
    name = "N0"

    def __init__(self, task: Task):
        self.t = task

    def init(self, E):
        return {"cur": np.zeros(E, dtype=np.int64)}

    def step(self, st, o, nz):
        return {"cur": o.copy()}

    def readout_features(self, st):
        return onehot(st["cur"], self.t.n_symbols)

    def full_state(self, st):
        return onehot(st["cur"], self.t.n_symbols)


class Register(System):
    """A register copies the cue at t = 0 and holds it (optionally corrupted each step).
    read_register=False -> PASSIVE (the policy reads only the current observation)."""

    def __init__(self, task: Task, read_register: bool, corrupt: float = 0.0, name: str = "FX"):
        self.t, self.read, self.p = task, read_register, corrupt
        self.name = name

    def init(self, E):
        return {"reg": np.full(E, -1, dtype=np.int64), "cur": np.zeros(E, dtype=np.int64), "t": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"u": rng.random(n), "r": rng.integers(0, self.t.V, n)}

    def step(self, st, o, nz):
        reg = st["reg"].copy()
        first = st["t"] == 0
        reg[first] = o[first]
        if self.p > 0:
            hit = (~first) & (nz["u"] < self.p)
            reg[hit] = nz["r"][hit]
        return {"reg": reg, "cur": o.copy(), "t": st["t"] + 1}

    def _reg1h(self, st):
        r = st["reg"]
        return onehot(np.where(r < 0, self.t.V, r), self.t.V + 1)

    def readout_features(self, st):
        cur = onehot(st["cur"], self.t.n_symbols)
        return np.hstack([self._reg1h(st), cur]) if self.read else cur

    def full_state(self, st):
        return np.hstack([self._reg1h(st), onehot(st["cur"], self.t.n_symbols)])


class DelayLine(System):
    """The cue enters unit 0 and moves one unit per step along a chain; only the last unit is read.
    History is held in PROPAGATING state, never in a fixed register."""
    name = "FD"

    def __init__(self, task: Task):
        self.t = task
        self.L = task.k + 2

    def init(self, E):
        return {"chain": np.full((E, self.L), self.t.V, dtype=np.int64), "cur": np.zeros(E, dtype=np.int64)}

    def step(self, st, o, nz):
        ch = np.full_like(st["chain"], self.t.V)
        ch[:, 1:] = st["chain"][:, :-1]
        ch[:, 0] = np.where(o < self.t.V, o, self.t.V)      # only cue symbols enter the line
        return {"chain": ch, "cur": o.copy()}

    def readout_features(self, st):
        return np.hstack([onehot(st["chain"][:, -1], self.t.V + 1), onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([onehot(st["chain"][:, j], self.t.V + 1) for j in range(self.L)] +
                         [onehot(st["cur"], self.t.n_symbols)])


def planted(task_mc: Task, task: Task):
    return [(NoMemory(task), task, "NONE"),
            (Register(task, read_register=False, name="PV"), task, "PASSIVE"),
            (Register(task, read_register=True, name="FX"), task, "FUNCTIONAL"),
            (DelayLine(task), task, "FUNCTIONAL"),
            (type("MC", (NoMemory,), {"name": "MC"})(task_mc), task_mc, "NONE"),
            (Register(task, read_register=True, corrupt=0.3, name="NZ"), task, "FUNCTIONAL")]
