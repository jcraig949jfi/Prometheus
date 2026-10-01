"""W2-B proposed rulers (drafts; not frozen semantics):

per_sensor_pivotality  the per-sensor cue-twin census: for sensor column j and trial k, a twin world equal
                       to the normal one except that ONLY column j's cue in trial k is negated. Pivotality
                       p_j = P(decision at trial k's readout differs), decision = sign(S0) in {-1, 0, +1}.
                       Known answers (proved in REPORT): XOR parity (1, 1); any non-parity 2-input readout
                       min_j p_j <= .5 (AND/OR types (.5, .5)); single-input (1, 0); 5-sensor majority with
                       flip .3: .2646 each; single-sensor MAJ reader (1, 0, 0, 0, 0).
"""
from __future__ import annotations

import numpy as np
import torch

from prometheus.ananke import envs
from prometheus.ananke.engine import Schedule, World


def per_sensor_pivotality(ph, genome, env, seeds, trials, device="cpu"):
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    K = ep.schedule.sense_idx.shape[1]
    Pd = env.period()
    cols = [j for j in range(K) if (ep.schedule.sense_val[:, :, j] != 0).any()]
    if env.family == "FLIP":
        cols = [0]                                     # column 1 is the teacher, not a cue
    arms = [(None, None)] + [(j, k) for j in cols for k in trials]
    A = len(arms)
    sv = ep.schedule.sense_val.repeat(1, A, 1).clone()
    for a, (j, k) in enumerate(arms):
        if j is None:
            continue
        t0 = k * Pd
        sv[t0:t0 + env.cue_len, a * M:(a + 1) * M, j] *= -1
    sch = Schedule(ep.schedule.sense_idx.repeat(A, 1), sv, ep.schedule.read_idx.repeat(A, 1))
    ws = [seeds[m - (m % 2)] for m in range(M)] * A
    w = World(ph, np.repeat(genome[None], M * A, 0), ws, device=device, schedule=sch)
    T = int(ep.ro_tick[:, max(trials)].max()) + 1
    w.run(T, graph=False)
    tr = w.trace.cpu().numpy()[:, :, 0]
    base = np.sign(tr[:, :M])
    out = {}
    for a, (j, k) in enumerate(arms):
        if j is None:
            continue
        rt = ep.ro_tick[:, k]
        d = np.sign(tr[rt, np.arange(M) + a * M]) != base[rt, np.arange(M)]
        out.setdefault(j, []).append(d.astype(float))
    return {j: float(np.mean(v)) for j, v in out.items()}, {j: np.stack(v, 1) for j, v in out.items()}
