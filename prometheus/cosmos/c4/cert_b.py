"""Certificate B for C4 v0.3 (R-MECH F2 repair), written without importing Certificate A's code.

F2 established that B-USE as specified in DESIGN v0.2 s6 tests A's causal contrast by another estimator. In a
PASSIVE world family (an externally trained readout is the actor) every behavioural certificate tests that
contrast; independence of the CONTRAST is not available there. What B can and must differ in is the
FAILURE MECHANISM. This module therefore exposes the machinery choices explicitly, and the planted
shared-failure matrix (tests/test_c4_cert_b.py) checks that B disagrees with A exactly where their machinery
differs:

  machinery            Certificate A                         Certificate B (this module)
  intervention         full-state interchange at t = k       source randomization of the cue at t = 0
  needs full_state     YES (the swap)                        NO (inputs and readout view only)
  decoder              multinomial logit (c3/probe.Logit)    ridge least squares, own code; `rf` variant adds
                                                             random ReLU features (nonlinear)
  pairing / seeds      common random numbers, A's seeds      none; own namespace
  statistic            paired effect, 3-SE                   exact binomial on held-out V-way accuracy

So B does NOT share A's dependence on full_state completeness (a mis-declared full_state makes A's swap
miss the carrier), and B-rf does not share A's linear-readout blind spot. They DO share the task, the
System interface and the readout cut. Those shared parts are declared, not hidden.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

SEED_NS = 0xB0B0_C4C4
ALPHA = 0.01
RF_WIDTH = 512


def _episodes(task, E, rng):
    """Cue randomized at the source; distractors independent; the query observation identical everywhere."""
    V, k = task.V, task.k
    cues = rng.integers(0, V, E)
    obs = np.empty((E, k + 2), dtype=np.int64)
    obs[:, 0] = cues
    obs[:, 1:k + 1] = V + rng.integers(0, V, (E, k))
    obs[:, k + 1] = 2 * V
    return cues, obs


def _run(sys_, obs, rng):
    st = sys_.init(obs.shape[0])
    for t in range(obs.shape[1]):
        st = sys_.step(st, obs[:, t], sys_.noise(obs.shape[0], rng))
    return np.asarray(sys_.readout_features(st), float)


class _Ridge:
    def __init__(self, K, lam=1e-2, rf=0, seed=0):
        self.K, self.lam, self.rf, self.seed = K, lam, rf, seed

    def _feat(self, X):
        Z = (X - self.mu) / self.sd
        if self.rf:
            Z = np.maximum(Z @ self.P + self.b, 0.0)
        return np.hstack([Z, np.ones((len(Z), 1))])

    def fit(self, X, y):
        self.mu, sd = X.mean(0), X.std(0)
        self.sd = np.where(sd > 1e-12, sd, 1.0)
        if self.rf:
            r = np.random.default_rng([SEED_NS, self.seed, 1])
            self.P = r.standard_normal((X.shape[1], self.rf)) / np.sqrt(X.shape[1])
            self.b = r.uniform(-1, 1, self.rf)
        Z = self._feat(X)
        self.W = np.linalg.solve(Z.T @ Z + self.lam * len(Z) * np.eye(Z.shape[1]), Z.T @ np.eye(self.K)[y])
        return self

    def predict(self, X):
        return (self._feat(X) @ self.W).argmax(1)


def b_use(sys_, task, decoder: str = "linear", E_train: int = 3000, E_test: int = 3000, seed: int = 0,
          alpha: float = ALPHA) -> Dict:
    from scipy.stats import binom
    rng = np.random.default_rng([SEED_NS, int(seed)])
    c_tr, o_tr = _episodes(task, E_train, rng)
    c_te, o_te = _episodes(task, E_test, rng)
    m = _Ridge(task.V, rf=RF_WIDTH if decoder == "rf" else 0, seed=seed).fit(_run(sys_, o_tr, rng), c_tr)
    acc = float((m.predict(_run(sys_, o_te, rng)) == c_te).mean())
    k = int(round(acc * E_test))
    p = float(binom.sf(k - 1, E_test, 1.0 / task.V))
    return {"decoder": decoder, "acc": acc, "p": p, "functional": bool(p < alpha)}
