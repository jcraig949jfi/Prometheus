"""NS-02 de-saturated signature: NS-01 signature + STRESS axes that separate mechanisms whose task behaviour saturates
(NS-01 defect: perfect memories collapsed to one witness). Measured at k = 8, decoder trained on unperturbed runs.

  corr[q]  readout rf excess after CORRUPTING a fraction q in {.1, .3, .5} of every state array's elements at t = 1
           (each corrupted element replaced by the same element of a random other episode): robustness profile.
  dual1 / dual2  a SECOND cue at t = 1 (distractor slot replaced by cue symbol c2): rf excess for the FIRST cue and for
           the SECOND cue (decoders trained on dual-cue runs): latch vs first-write gate vs superposition vs composition.
Equivalence (NS-02): base distance <= TAU (.05) AND stress distance (mean abs over the 5 stress values) <= TAU_S (.10).
"""
from __future__ import annotations

from typing import Callable, Dict

import numpy as np

from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4.cert_b import RF_WIDTH, _Ridge
from prometheus.cosmos.ns01 import signature as S1

QS = (0.1, 0.3, 0.5)
TAU_S = 0.10
K = 8


def _corrupt(st, q, rng):
    out = {}
    for key, v in st.items():
        v = np.asarray(v)
        if v.ndim == 0 or v.shape[0] < 2:
            out[key] = v
            continue
        E = v.shape[0]
        donor = rng.integers(0, E, E)
        flat = v.reshape(E, -1)
        mask = rng.random(flat.shape) < q
        new = np.where(mask, flat[donor], flat)
        out[key] = new.reshape(v.shape).astype(v.dtype, copy=False)
    return out


def _run(sys_, obs, rng, corrupt_q=None):
    st = sys_.init(obs.shape[0])
    for t in range(obs.shape[1]):
        st = sys_.step(st, obs[:, t], sys_.noise(obs.shape[0], rng))
        if corrupt_q is not None and t == 1:
            st = _corrupt(st, corrupt_q, rng)
    return np.asarray(sys_.readout_features(st), float)


def _fit(X, y):
    return _Ridge(S1.V, rf=RF_WIDTH, seed=1).fit(X, y) if np.all(np.isfinite(X)) else None


def _acc(m, X, y):
    if m is None or not np.all(np.isfinite(X)):
        return 0.0
    return S1.excess(float((m.predict(X) == y).mean()))


def stress(make: Callable[[Task], object], seed: int = 0) -> Dict:
    rng = np.random.default_rng([S1.SEED, 2, seed])
    t = Task(S1.V, K)
    ctr, otr = S1._episodes(K, S1.E_TR, rng)
    cte, ote = S1._episodes(K, S1.E_TE, rng)
    m = _fit(_run(make(t), otr, rng), ctr)
    out = {"corr": {q: _acc(m, _run(make(t), ote, rng, corrupt_q=q), cte) for q in QS}}
    c2tr, c2te = rng.integers(0, S1.V, S1.E_TR), rng.integers(0, S1.V, S1.E_TE)
    o2tr, o2te = otr.copy(), ote.copy()
    o2tr[:, 1], o2te[:, 1] = c2tr, c2te
    Rtr, Rte = _run(make(t), o2tr, rng), _run(make(t), o2te, rng)
    out["dual1"] = _acc(_fit(Rtr, ctr), Rte, cte)
    out["dual2"] = _acc(_fit(Rtr, c2tr), Rte, c2te)
    return out


def signature2(make, seed: int = 0) -> Dict:
    sig = S1.signature(make, seed)
    sig["stress"] = stress(make, seed)
    return sig


def svec(sig) -> np.ndarray:
    s = sig["stress"]
    return np.array([s["corr"][q] for q in QS] + [s["dual1"], s["dual2"]])


def equivalent(a, b) -> bool:
    return S1.distance(a, b) <= S1.TAU and float(np.mean(np.abs(svec(a) - svec(b)))) <= TAU_S


def distances(a, b):
    return S1.distance(a, b), float(np.mean(np.abs(svec(a) - svec(b))))
