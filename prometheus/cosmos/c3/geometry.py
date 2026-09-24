"""Generic, decoder-free candidate coordinates (S1_PREREG_LAW s2). Identical protocol for every system;
uses only the System interface. No substrate declares any of these (coordinate firewall).

  d_sig(t)   distance between CRN-paired trajectories that differ only in the first observation
  d_noise(t) distance between trajectories with the same observations and independent noise
Views: F = full_state, R = readout_features; each view standardised per component by its SD over all
recorded states. Coordinates at q = k+1:
  sR = d_sig^R(q) / (d_sig^R(q) + d_noise^R(q)), sF likewise; rR = d_sig^R(q) / d_sig^R(1), rF likewise; kq = k+1
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, paired_batch

TINY = 1e-12


def _traj(sys: System, obs: np.ndarray, rng, paired: bool, times) -> Dict[int, Dict[str, np.ndarray]]:
    E, T = obs.shape
    st = sys.init(E)
    out = {}
    for t in range(T):
        n = E // 2 if paired else E
        nz = sys.noise(n, rng)
        if paired:
            nz = {k: np.repeat(v, 2, axis=0) for k, v in nz.items()}
        st = sys.step(st, obs[:, t], nz)
        if t in times:
            out[t] = {"F": np.asarray(sys.full_state(st), float), "R": np.asarray(sys.readout_features(st), float)}
    return out


def coordinates(sys: System, task: Task, n_pairs: int = 400, seed: int = 0) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    q = task.k + 1
    times = (1, q)
    # signal: pairs differ in the cue only, share everything else (CRN)
    _, obs_s = paired_batch(task, n_pairs, rng)
    sig = _traj(sys, obs_s, rng, paired=True, times=times)
    # noise: identical observation rows, independent noise
    obs_n = np.repeat(obs_s[0::2], 2, axis=0)
    noi = _traj(sys, obs_n, rng, paired=False, times=times)
    out = {"kq": float(q)}
    for view in ("F", "R"):
        allv = np.vstack([sig[t][view] for t in times] + [noi[t][view] for t in times])
        sd = allv.std(0)
        sd = np.where(sd > TINY, sd, 1.0)

        def d(block, t):
            X = block[t][view] / sd
            return float(np.linalg.norm(X[0::2] - X[1::2], axis=1).mean())

        ds_q, dn_q, ds_1 = d(sig, q), d(noi, q), d(sig, 1)
        out["s" + view] = ds_q / (ds_q + dn_q + TINY) if (ds_q + dn_q) > TINY else 0.0
        out["r" + view] = ds_q / (ds_1 + TINY) if ds_1 > TINY else 0.0
        out["dsig_" + view] = ds_q
        out["dnoise_" + view] = dn_q
    return out
