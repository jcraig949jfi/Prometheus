"""One eager CPU evaluation path shared by the audit rulers, certificates and tests.

c1b.evaluate / assays.evaluate semantics: mirror pairs share physics seeds (world m uses seeds[m - m % 2]);
genome [G, L, 5] is broadcast to every world; sched_fn(ep) may edit the built schedule in place (input
ablations). This replaces four private copies in the Wave-2 drafts (H-PLANT hp_common.evaluate, W2-B
w2b_common.run and rulers_c1._run, W2-S w2s_common.flip_eval's first half).

The caller owns the device policy: pass device="cpu" (the default) and hide the GPU with
CUDA_VISIBLE_DEVICES=-1 before torch is imported when a CPU-only brief applies.
"""
from __future__ import annotations

import numpy as np

from prometheus.ananke import assays, envs
from prometheus.ananke.engine import World


def mirrored(seeds) -> list:
    return [seeds[m - (m % 2)] for m in range(len(seeds))]


def run(ph, genome, env, seeds, ctrl=None, sched_fn=None, device: str = "cpu", T: int | None = None):
    """-> (pairs [M/2], per_trial [M, trials] bool, ep, trace [T, M, A] int64)."""
    M = len(seeds)
    if M % 2:
        raise ValueError("mirror design: an even number of worlds is required")
    ep = envs.build(ph, env, seeds)
    if sched_fn is not None:
        sched_fn(ep)
    g = np.repeat(np.asarray(genome)[None], M, axis=0)
    w = World(ph, g, mirrored(seeds), device=device, ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T() if T is None else T, graph=False)
    tr = w.trace.cpu().numpy()
    acc = envs.score(ep, tr)
    return acc.reshape(M // 2, 2).mean(-1), envs.per_trial(ep, tr), ep, tr


def ci(pairs) -> dict:
    m, lo, hi = assays.pair_ci(np.asarray(pairs, float))
    return {"acc": float(m), "lo99": float(lo), "hi99": float(hi)}
