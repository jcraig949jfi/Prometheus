"""Mechanism lens: between-tick interventions and recorders for PTE.

Everything here acts on World state BETWEEN ticks (after tick t, before
tick t+1), so the engine's physics is untouched. Used by the 2026-09-27
spikes (roles/Ananke/research/SPIKES_2026-09-27_PLAN.md).

Mirror-pair carrier swap: worlds 2p and 2p+1 share all exogenous
randomness and have negated cue sequences. Swapping a carrier between
partners hands each world the other's version. A carrier that holds the
bit makes the answer follow the partner (accuracy -> 1 - normal).
"""
from __future__ import annotations

import dataclasses

import numpy as np
import torch

from . import assays, envs
from .engine import Controls, World, Schedule
from .physics import Physics

SITE_ARRAYS = ("S", "E", "r", "Kp", "Acc_sum", "Acc_cnt", "w")
FLIGHT_ARRAYS = ("Msum", "Mcnt")


def partner_index(M: int, dev) -> torch.Tensor:
    return torch.arange(M, device=dev) ^ 1


def swap(w: World, names, sub=None):
    """Swap the named arrays between mirror partners. `sub` optionally
    restricts Msum to one payload component."""
    p = partner_index(w.B, w.dev)
    for n in names:
        if n == "w" and not w.R:
            continue
        a = getattr(w, n)
        if n in FLIGHT_ARRAYS:
            if sub is not None and n == "Msum":
                a[..., sub].copy_(a[:, p][..., sub])
            else:
                a.copy_(a[:, p])
        else:
            a.copy_(a[p])


def roll_slots(w: World, k: int):
    """Delay every in-flight packet by k ticks (content and recipient kept).
    Valid for k >= 1 while the ring has room: after tick t the slot t % LM
    is empty and stands for the farthest future arrival."""
    t = w.t                                       # next tick to run
    LM = w.LM
    order = [(t + j) % LM for j in range(LM)]     # arrival t, t+1, ..., t+LM-1
    ms, mc = w.Msum.clone(), w.Mcnt.clone()
    w.Msum.zero_()
    w.Mcnt.zero_()
    for j in range(LM - k):
        w.Msum[order[j + k]] += ms[order[j]]
        w.Mcnt[order[j + k]] += mc[order[j]]
    # arrivals beyond the ring's horizon would be lost; with k <= LM-1-maxdelay none exist
    lost = int(sum(mc[order[j]].sum() for j in range(LM - k, LM)))
    return lost


def roll_recipients(w: World, k: int = 1):
    w.Msum.copy_(torch.roll(w.Msum, k, dims=2))
    w.Mcnt.copy_(torch.roll(w.Mcnt, k, dims=2))


def reset_r(w: World):
    w.r.copy_(w.r0)


@dataclasses.dataclass
class Trace:
    ep: envs.Episode
    trace: np.ndarray
    per_trial: np.ndarray          # [M, trials] 0 / 0.5 / 1
    rec: dict
    stats: dict


def run(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, seeds, hooks=None, recorders=None,
        device="cuda", ctrl: Controls | None = None, schedule=None, ep=None, mirrored=True) -> Trace:
    """Eager tick loop with between-tick hooks {tick: fn(world)} (applied
    AFTER that tick) and recorders fn(world, t) called after every tick."""
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)] if mirrored else list(seeds)
    if ep is None:
        ep = envs.build(ph, env, seeds)
    sch = schedule or ep.schedule
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device=device, ctrl=ctrl or Controls(), schedule=sch)
    hooks = hooks or {}
    rec = {}
    for t in range(env.T()):
        w.step()
        if recorders:
            for name, fn in recorders.items():
                rec.setdefault(name, []).append(fn(w, t))
        if t in hooks:
            for fn in (hooks[t] if isinstance(hooks[t], list) else [hooks[t]]):
                fn(w)
    tr = w.trace.cpu().numpy()
    return Trace(ep, tr, envs.per_trial(ep, tr), rec,
                 {k: v.cpu().numpy() for k, v in w.stats.items()})


def trial_acc(tr: Trace, trials) -> np.ndarray:
    """Pair means over the chosen trials (scored ones only)."""
    sel = np.zeros_like(tr.ep.scored)
    sel[:, list(trials)] = True
    sel &= tr.ep.scored
    v = np.where(sel, tr.per_trial, np.nan)
    per_world = np.nanmean(v, 1)
    return per_world.reshape(-1, 2).mean(-1)


def ci(pairs):
    m, lo, hi = assays.pair_ci(pairs)
    return float(m), float(lo), float(hi)


def swap_verdict(normal_pairs, pairs) -> str:
    """Plan decision rule: FLIP / NO-EFFECT / CHANCE."""
    m, lo, hi = ci(pairs)
    nlo = ci(normal_pairs)[1]
    if hi < 0.40:
        return "FLIP"
    if lo >= nlo - 0.05:
        return "NO-EFFECT"
    return "CHANCE"
