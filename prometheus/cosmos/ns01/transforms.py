"""Disguise transformations for the exclusion-engine test (directive s8). Each wraps a System and preserves its
causal transition structure exactly, while changing names, encodings, scales or implementation."""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class _Wrap(System):
    def __init__(self, inner):
        self.i = inner

    def init(self, E):
        return self._out(self.i.init(E))

    def noise(self, n, rng):
        return self.i.noise(n, rng)

    def step(self, st, o, nz):
        return self._out(self.i.step(self._in(st), o, nz))

    def readout_features(self, st):
        return self._enc(np.asarray(self.i.readout_features(self._in(st)), float), "r")

    def full_state(self, st):
        return self._enc(np.asarray(self.i.full_state(self._in(st)), float), "f")

    def _out(self, st):
        return st

    def _in(self, st):
        return st

    def _enc(self, X, which):
        return X


class Permute(_Wrap):
    """State-variable permutation of every exposed coordinate."""
    def __init__(self, inner, seed=0):
        super().__init__(inner)
        self.seed, self.P = seed, {}

    def _enc(self, X, which):
        if which not in self.P:
            self.P[which] = np.random.default_rng([self.seed, ord(which)]).permutation(X.shape[1])
        return X[:, self.P[which]]


class LinearEncode(_Wrap):
    """Invertible linear re-encoding (orthogonal x scales in [0.5, 2]) of every exposed coordinate."""
    def __init__(self, inner, seed=0):
        super().__init__(inner)
        self.seed, self.M = seed, {}

    def _enc(self, X, which):
        if which not in self.M:
            r = np.random.default_rng([self.seed, 7, ord(which)])
            q, _ = np.linalg.qr(r.standard_normal((X.shape[1], X.shape[1])))
            self.M[which] = q * r.uniform(0.5, 2.0, X.shape[1])
        return X @ self.M[which]


class Rescale(_Wrap):
    """Unit change: every exposed coordinate x 1000."""
    def _enc(self, X, which):
        return 1000.0 * X


class RenameState(_Wrap):
    """Implementation refactor: every state key renamed (and restored for the inner mechanism)."""
    def _out(self, st):
        return {"zz_" + k[::-1]: v for k, v in st.items()}

    def _in(self, st):
        return {k[3:][::-1]: v for k, v in st.items()}


class ShiftRegisterDelay(System):
    """Hand refactor of c3/calib.DelayLine's causal content (cue copied at t 0 and held exactly, readout sees it
    with the current symbol) written as a different data structure: a FIFO of the last T inputs whose oldest
    slot is the cue. Same causal transition, different implementation."""
    def __init__(self, task: Task):
        self.t = task

    def init(self, E):
        return {"fifo": np.full((E, self.t.k + 2), -1, dtype=np.int64), "n": np.zeros(E, dtype=np.int64)}

    def step(self, st, o, nz):
        f = st["fifo"].copy()
        n = st["n"]
        f[np.arange(len(o)), np.minimum(n, f.shape[1] - 1)] = o
        return {"fifo": f, "n": n + 1}

    def _cur(self, st):
        return st["fifo"][np.arange(len(st["n"])), np.maximum(st["n"] - 1, 0)]

    def readout_features(self, st):
        return np.hstack([onehot(np.clip(st["fifo"][:, 0], 0, self.t.V - 1), self.t.V),
                          onehot(np.clip(self._cur(st), 0, self.t.n_symbols - 1), self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([onehot(np.clip(st["fifo"][:, 0], 0, self.t.V - 1), self.t.V),
                          onehot(np.clip(self._cur(st), 0, self.t.n_symbols - 1), self.t.n_symbols)])
