"""Lane C (BRAIN) C7b: a structure-matched plastic learner for lane B's world dynamics.

B's transition updates registers by affine maps mod M = 2^16 (a*x + b*y + c), and a regime flip negates every
multiplier (a -> M - a). C7's dev probe showed a hex-digit TT cannot learn one regime at all. This learner uses the
representation the world actually has:

    y_j(t+1) == a * x_s(t) + c   (mod 2^16)      for one observed source feature s

Fit (robust): over random sample pairs (i, k) with an ODD difference d = x_s[i] - x_s[k] (invertible mod 2^16),
a = (y[i] - y[k]) * d^{-1} mod 2^16 and c = y[i] - a * x_s[i]; the (s, a, c) with the most exact matches on the
batch wins (a vote, so corrupted observations only cost support, not correctness).

Plasticity: each tick the current model's exact-match SUPPORT on the new batch is measured before any refit.
surprise = support < SURPRISE_SUPPORT; on surprise the model is refit on this batch. No rank: the representation is
fixed and tiny (s, a, c = 1 + 2 + 2 bytes); what adapts is the program's constants.
observe_flag() exists for the leak probe; honest learners ignore it.
"""
from __future__ import annotations

import numpy as np

MOD = 1 << 16
MASK = MOD - 1
SURPRISE_SUPPORT = 0.5


def inv_odd(d: np.ndarray) -> np.ndarray:
    """Inverse of odd integers mod 2^16 by Newton iteration (x <- x * (2 - d x)); exact after 4 steps from x = d."""
    d = d.astype(np.int64) & MASK
    x = d.copy()
    for _ in range(4):
        x = (x * (2 - d * x)) & MASK
    return x


def fit_affine(X: np.ndarray, y: np.ndarray, rng, pairs: int = 256):
    """X int [n, D] current observed values, y int [n] next value of the target. Returns (s, a, c, support)."""
    n, D = X.shape
    X = X.astype(np.int64) & MASK
    y = y.astype(np.int64) & MASK
    best = (0, 0, int(np.bincount(y).argmax()) if n else 0, 0.0)
    if n < 2:
        return best
    i = rng.integers(0, n, pairs)
    k = rng.integers(0, n, pairs)
    for s in range(D):
        d = (X[i, s] - X[k, s]) & MASK
        odd = (d & 1) == 1
        if not odd.any():
            continue
        a = ((y[i[odd]] - y[k[odd]]) * inv_odd(d[odd])) & MASK
        c = (y[i[odd]] - a * X[i[odd], s]) & MASK
        cand, counts = np.unique(np.stack([a, c], 1), axis=0, return_counts=True)
        for (aa, cc) in cand[np.argsort(-counts)[:4]]:
            sup = float(np.mean(((aa * X[:, s] + cc) & MASK) == y))
            if sup > best[3]:
                best = (s, int(aa), int(cc), sup)
    return best


class PlasticAffine:
    name = "plastic_affine"

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)
        self.model = None                       # (s, a, c)
        self.surprised = False
        self.support = 0.0
        self.refits = 0

    def observe_flag(self, flag: int) -> None:
        pass

    def predict(self, X):
        if self.model is None:
            return np.zeros(len(X), np.int64)
        s, a, c = self.model
        return (a * (X[:, s].astype(np.int64) & MASK) + c) & MASK

    def _is_surprise(self, support: float) -> bool:
        return self.model is None or support < SURPRISE_SUPPORT

    def adapt_batch(self, X, y) -> None:
        y = y.astype(np.int64) & MASK
        self.support = float(np.mean(self.predict(X) == y)) if self.model is not None else 0.0
        self.surprised = self._is_surprise(self.support)
        if self.surprised:
            s, a, c, _ = fit_affine(X, y, self.rng)
            self.model = (s, a, c)
            self.refits += 1


class LeakAffine(PlasticAffine):
    """CHEAT: refits when the regime FLAG changes (and only then), instead of on low support."""
    name = "leak_affine"

    def __init__(self, seed: int = 0):
        super().__init__(seed)
        self.flag = None
        self.switched = False

    def observe_flag(self, flag: int) -> None:
        self.switched = self.flag is not None and flag != self.flag
        self.flag = flag

    def _is_surprise(self, support: float) -> bool:
        return self.model is None or self.switched
