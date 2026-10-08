"""C4 v0.3 planted CONTINUOUS families (R-MECH F5). Calibration only, never scored as evidence.

Reservoir: x' = a x + g W[o] + sigma n; readout = (x, onehot(current symbol)). The concept follows the R-MECH
interim harness (Bellerophon, 164df3cdd, attack_harness.py); this is a Cosmos re-implementation with its own
seeds, kept bit-compatible with that harness (same W construction for wseed) so its labels can be reused.

RotReservoir: same per-step contraction and injection as Reservoir, but the leak is a rotation-scaled
orthogonal map. Its local coordinates match a Reservoir of the same a, while information is
spread over directions differently: a planted pair for testing whether local physics composes.
"""
from __future__ import annotations

import math

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Reservoir(System):
    def __init__(self, task: Task, a: float, sigma: float, g: float = 1.0, d: int = 8, wseed: int = 0):
        self.t, self.a, self.s, self.g, self.d = task, a, sigma, g, d
        r = np.random.default_rng(wseed)
        self.W = r.standard_normal((task.n_symbols, d)) / math.sqrt(d)
        self.M = a * np.eye(d)

    def init(self, E):
        return {"x": np.zeros((E, self.d)), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"n": rng.standard_normal((n, self.d))}

    def step(self, st, o, nz):
        x = st["x"] @ self.M.T + self.g * self.W[o] + self.s * nz["n"]
        return {"x": x, "cur": np.asarray(o).copy()}

    def readout_features(self, st):
        return np.hstack([st["x"], onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([st["x"], onehot(st["cur"], self.t.n_symbols)])


class RotReservoir(Reservoir):
    def __init__(self, task: Task, a: float, sigma: float, g: float = 1.0, d: int = 8, wseed: int = 0,
                 rseed: int = 1):
        super().__init__(task, a, sigma, g, d, wseed)
        q, _ = np.linalg.qr(np.random.default_rng(rseed).standard_normal((d, d)))
        self.M = a * q


class XorCue(System):
    """Binary cue (use V = 2) stored as (r, r^c) in +-1 units, r random per episode, then held exactly. The two
    classes are the two diagonals of the square: decodable only NONLINEARLY (a linear readout sees chance).
    With V = 4 the multi-class argmax can carve the 16 patterns partially (measured: linear .378 vs .25), so
    V = 2 is required. Planted case where a nonlinear decoder must disagree with any linear-readout
    certificate."""

    def __init__(self, task: Task):
        self.t = task

    def init(self, E):
        return {"m": np.zeros((E, 2)), "cur": np.zeros(E, dtype=np.int64), "t": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"r": rng.integers(0, 2, n)}

    def step(self, st, o, nz):
        o = np.asarray(o)
        m = st["m"].copy()
        first = st["t"] == 0
        if first.any():
            c, r = np.clip(o[first], 0, 1), nz["r"][first]
            m[first] = 2.0 * np.stack([r, r ^ c], 1) - 1
        return {"m": m, "cur": o.copy(), "t": st["t"] + 1}

    def readout_features(self, st):
        return np.hstack([st["m"], onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([st["m"], onehot(st["cur"], self.t.n_symbols), st["t"][:, None]])


class HiddenCarrier(System):
    """A clean register holds the cue, but it lives on the SYSTEM OBJECT, outside the state dict (a contract
    violation: the state dict is not the whole causal state). A certificate that intervenes by exchanging the
    state dict cannot move the carrier; source randomization does not need to."""

    def __init__(self, task: Task):
        self.t = task
        self._reg = None

    def init(self, E):
        self._reg = np.zeros(E, dtype=np.int64)
        return {"cur": np.zeros(E, dtype=np.int64), "t": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {}

    def step(self, st, o, nz):
        o = np.asarray(o)
        first = st["t"] == 0
        self._reg[first] = np.clip(o[first], 0, self.t.V - 1)
        return {"cur": o.copy(), "t": st["t"] + 1}

    def readout_features(self, st):
        return np.hstack([onehot(self._reg, self.t.V), onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([onehot(self._reg, self.t.V), onehot(st["cur"], self.t.n_symbols),
                          st["t"][:, None].astype(float)])
