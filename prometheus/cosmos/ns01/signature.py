"""NS-01 behavioural SIGNATURE of an executable mechanism (the measurement under the exclusion engine).

A candidate is a factory make(task) -> System (c3/system.py contract; knobs fixed inside). The signature is computed
only from executing the mechanism through its interface -- never from its name, comments or source -- so verbal
novelty cannot move it. All seeds are fixed; decoders are Certificate B's own ridge / random-feature decoders.

Measured (excess = (acc - 1/V) / (1 - 1/V); V = 4; k in KS):
  lin[k]   cue decoded from readout_features at the query, linear decoder
  rf[k]    same, random-feature (nonlinear) decoder
  full[k]  cue decoded from full_state at the query, random-feature decoder (is the cue ANYWHERE in the state?)
  own8 / donor8   TRANSPLANT intervention, k 8: after step t = 1 the state dicts of paired episodes are exchanged;
           readout decoded (decoder trained on unperturbed runs) against the episode's OWN cue and the DONOR's cue.
           The cue should travel with the declared state (donor high, own at chance); own > floor means the cue is
           carried OUTSIDE the declared state.
  dfree8   rf at k 8 when every distractor is the same symbol (distractor-free intervention).
"""
from __future__ import annotations

from typing import Callable, Dict

import numpy as np

from prometheus.cosmos.c3.system import swap_rows
from prometheus.cosmos.c3.task import Task
from prometheus.cosmos.c4.cert_b import RF_WIDTH, _Ridge

V = 4
KS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16)
E_TR, E_TE = 2000, 2000
SEED = 0x0515_0001
FLOOR = 0.10                          # A15-style minimum magnitude, fixed a priori
TAU = 0.05                            # equivalence: mean abs signature difference, fixed a priori (NS-01)


def excess(acc: float) -> float:
    return (acc - 1.0 / V) / (1.0 - 1.0 / V)


def _episodes(k, E, rng, distractor_free=False):
    cues = rng.integers(0, V, E)
    obs = np.empty((E, k + 2), dtype=np.int64)
    obs[:, 0] = cues
    obs[:, 1:k + 1] = V if distractor_free else V + rng.integers(0, V, (E, k))
    obs[:, k + 1] = 2 * V
    return cues, obs


def _run(sys_, obs, rng, swap_after=None, perm=None):
    st = sys_.init(obs.shape[0])
    for t in range(obs.shape[1]):
        st = sys_.step(st, obs[:, t], sys_.noise(obs.shape[0], rng))
        if swap_after is not None and t == swap_after:
            st = swap_rows(st, perm)
    R = np.asarray(sys_.readout_features(st), float)
    F = np.asarray(sys_.full_state(st), float)
    return R, F


def _fit_eval(Xtr, ytr, Xte, yte, rf):
    if not np.all(np.isfinite(Xtr)) or not np.all(np.isfinite(Xte)):
        return 0.0
    m = _Ridge(V, rf=RF_WIDTH if rf else 0, seed=1).fit(Xtr, ytr)
    return excess(float((m.predict(Xte) == yte).mean()))


def signature(make: Callable[[Task], object], seed: int = 0) -> Dict:
    rng = np.random.default_rng([SEED, seed])
    sig = {"lin": {}, "rf": {}, "full": {}}
    for k in KS:
        t = Task(V, k)
        sys_ = make(t)
        ctr, otr = _episodes(k, E_TR, rng)
        cte, ote = _episodes(k, E_TE, rng)
        Rtr, Ftr = _run(sys_, otr, rng)
        Rte, Fte = _run(sys_, ote, rng)
        sig["lin"][k] = _fit_eval(Rtr, ctr, Rte, cte, False)
        sig["rf"][k] = _fit_eval(Rtr, ctr, Rte, cte, True)
        sig["full"][k] = _fit_eval(Ftr, ctr, Fte, cte, True)
        if k == 8:
            m = _Ridge(V, rf=RF_WIDTH, seed=1).fit(Rtr, ctr) if np.all(np.isfinite(Rtr)) else None
            perm = np.arange(E_TE).reshape(-1, 2)[:, ::-1].reshape(-1)
            Rx, _ = _run(make(t), ote, rng, swap_after=1, perm=perm)
            if m is not None and np.all(np.isfinite(Rx)):
                p = m.predict(Rx)
                sig["own8"] = excess(float((p == cte).mean()))
                sig["donor8"] = excess(float((p == cte[perm]).mean()))
            else:
                sig["own8"] = sig["donor8"] = 0.0
            c1, o1 = _episodes(k, E_TR, rng, True)
            c2, o2 = _episodes(k, E_TE, rng, True)
            R1, _ = _run(make(t), o1, rng)
            R2, _ = _run(make(t), o2, rng)
            sig["dfree8"] = _fit_eval(R1, c1, R2, c2, True)
    return sig


def vector(sig: Dict) -> np.ndarray:
    return np.array([sig[m][k] for m in ("lin", "rf", "full") for k in KS] +
                    [sig["own8"], sig["donor8"], sig["dfree8"]])


def distance(a: Dict, b: Dict) -> float:
    return float(np.mean(np.abs(vector(a) - vector(b))))


# -- mechanism-level failure rules (frozen; thresholds = FLOOR or 2 x FLOOR) ------------------------------------
def classify(sig: Dict) -> Dict:
    lin, rf, full = sig["lin"], sig["rf"], sig["full"]
    ks = list(KS)
    fired = []
    if max(full.values()) < FLOOR:
        fired.append("DEGENERATE")                       # the cue never reaches the state at the query
    if sig["own8"] >= FLOOR:
        fired.append("M-HIDDEN")                         # cue survives transplant of the declared state
    if max(rf[k] - lin[k] for k in ks) >= 2 * FLOOR:
        fired.append("M-LINBLIND")                       # readable only nonlinearly
    if max(full[k] - rf[k] for k in ks) >= 2 * FLOOR:
        fired.append("M-UNREACHABLE")                    # in the state, not at the readout
    if any(rf[b] - rf[a] >= 2 * FLOOR or full[b] - full[a] >= 2 * FLOOR for i, a in enumerate(ks) for b in ks[i + 1:]):
        fired.append("M-NONMONOTONE")                    # usability returns / rises with k (geometry, aliasing)
    if sig["dfree8"] - rf[8] >= 2 * FLOOR:
        fired.append("M-INTERFERENCE")                   # distractors destroy what silence preserves
    if rf[ks[0]] >= FLOOR and rf[ks[-1]] < FLOOR:
        fired.append("M-DECAY")                          # usable early, lost by k 16
    viable = min(rf.values()) >= FLOOR
    return {"fired": fired, "viable": viable}
