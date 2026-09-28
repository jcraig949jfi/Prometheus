"""W-H harness: copy of lens.run semantics with pre-tick and post-tick hooks.
Between-tick only; physics untouched."""
from __future__ import annotations
import pathlib, sys
REPO = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO))
import numpy as np
import torch
from prometheus.ananke import assays, envs, lens
from prometheus.ananke.engine import Controls, World

AN = assays.world_seeds(0x5ED, 64)


def run(ph, genome, env, seeds=AN, pre=None, post=None, init=None, ctrl=None, device="cpu", ep=None):
    """pre(w, t): before tick t; post(w, t): after tick t; init(w): before tick 0."""
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = ep or envs.build(ph, env, seeds)
    g = np.repeat(np.asarray(genome)[None], M, axis=0)
    w = World(ph, g, ws, device=device, ctrl=ctrl or Controls(), schedule=ep.schedule)
    if init:
        init(w)
    for t in range(env.T()):
        if pre:
            pre(w, t)
        w.step()
        if post:
            post(w, t)
    tr = w.trace.cpu().numpy()
    out = lens.Trace(ep, tr, envs.per_trial(ep, tr), {}, {k: v.cpu().numpy() for k, v in w.stats.items()})
    out.world = w
    return out


def acc(tr, trials=None, mask=None):
    """pair means; mask [B, trials] bool restricts scored trials."""
    sc = tr.ep.scored.copy()
    if trials is not None:
        s2 = np.zeros_like(sc); s2[:, list(trials)] = True; sc &= s2
    if mask is not None:
        sc &= mask
    v = np.where(sc, tr.per_trial, np.nan)
    pw = np.nanmean(v, 1)
    return np.nanmean(pw.reshape(-1, 2), -1)


def paired(arm, normal):
    d = arm - normal
    m, lo, hi = lens.ci(d)
    return {"arm": lens.ci(arm), "normal": lens.ci(normal), "d": [m, lo, hi]}


def seen_inbox(w):
    """[B,N,C] counts and [B,N,C,P] sums the program will see at the NEXT tick
    (accumulated inbox + arrivals in the slot about to be delivered;
    ignores collision saturation)."""
    slot = w.t % w.LM
    return (w.Acc_cnt + w.Mcnt[slot]).cpu().numpy().copy(), (w.Acc_sum + w.Msum[slot]).cpu().numpy().copy()
