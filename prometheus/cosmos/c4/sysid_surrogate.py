"""LOCAL SUFFICIENCY instrument (EXP-04): a nonlinear one-step surrogate learned through LocalProbe (G7: at most one
controlled step per stationary state), composed by simulation into a predicted task accuracy. Zero label-fitted
parameters: the prediction is the surrogate actor's held-out accuracy.

numpy only (G1); every setting frozen below.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from prometheus.cosmos.c4.sysid_local import LocalProbe, _whitener

N_TRAIN = 4096
WIDTH = 512
RIDGE = 1e-2
E_SIM = 2000
SEED_NS = 0x5022_0647


def _rf(X, P, b):
    return np.hstack([np.maximum(X @ P + b, 0.0), X, np.ones((len(X), 1))])


def _ridge(Z, Y, lam=RIDGE):
    return np.linalg.solve(Z.T @ Z + lam * len(Z) * np.eye(Z.shape[1]), Z.T @ Y)


def fit_surrogate(probe: LocalProbe, n: int = N_TRAIN, seed: int = 0) -> Dict:
    rng = np.random.default_rng([SEED_NS, seed])
    n_in = probe._n_in
    s0 = probe.stationary(n)
    F0, R0 = probe.full(s0), probe.readout(s0)
    mf, Wf = _whitener(F0)
    mr, Wr = _whitener(R0)
    Z0 = (F0 - mf) @ Wf
    obs = probe.symbols(n)
    s1 = probe.step1(s0, obs, probe.noise(n))
    Z1 = (probe.full(s1) - mf) @ Wf
    X = np.hstack([Z0, np.eye(n_in)[obs]])
    P = rng.standard_normal((X.shape[1], WIDTH)) / np.sqrt(X.shape[1])
    b = rng.uniform(-1, 1, WIDTH)
    Wdyn = _ridge(_rf(X, P, b), Z1)
    res = Z1 - _rf(X, P, b) @ Wdyn
    cov = np.cov(res.T) if res.shape[1] > 1 else np.atleast_2d(res.var())
    w, U = np.linalg.eigh(np.atleast_2d(cov))
    Lc = U * np.sqrt(np.clip(w, 0, None))
    Pr = rng.standard_normal((Z0.shape[1], WIDTH)) / np.sqrt(max(Z0.shape[1], 1))
    br = rng.uniform(-1, 1, WIDTH)
    Wro = _ridge(_rf(Z0, Pr, br), (R0 - mr) @ Wr)
    return {"P": P, "b": b, "W": Wdyn, "L": Lc, "Pr": Pr, "br": br, "Wro": Wro, "Z0": Z0,
            "lo": Z0.min(0) - 1.0, "hi": Z0.max(0) + 1.0, "n_in": n_in}


def predicted_accuracy(S: Dict, V: int, k: int, E: int = E_SIM, seed: int = 0) -> float:
    """Simulate the task in the surrogate from stationary starts; ridge linear decoder of the cue; held-out acc."""
    rng = np.random.default_rng([SEED_NS, seed, 1])
    n_in = S["n_in"]
    Z = S["Z0"][rng.integers(0, len(S["Z0"]), E)]
    cues = rng.integers(0, V, E)
    seq = [cues] + [V + rng.integers(0, V, E) for _ in range(k)] + [np.full(E, 2 * V)]
    eye = np.eye(n_in)
    for o in seq:
        X = np.hstack([Z, eye[np.clip(o, 0, n_in - 1)]])
        Z = _rf(X, S["P"], S["b"]) @ S["W"] + rng.standard_normal((E, S["L"].shape[1])) @ S["L"].T
        Z = np.clip(Z, S["lo"], S["hi"])
    R = _rf(Z, S["Pr"], S["br"]) @ S["Wro"]
    h = E // 2
    Rtr, Rte = R[:h], R[h:]
    mu, sd = Rtr.mean(0), Rtr.std(0) + 1e-9
    A = np.hstack([(Rtr - mu) / sd, np.ones((h, 1))])
    W = _ridge(A, np.eye(V)[cues[:h]])
    pred = (np.hstack([(Rte - mu) / sd, np.ones((len(Rte), 1))]) @ W).argmax(1)
    return float((pred == cues[h:]).mean())
