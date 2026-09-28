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


# ------------------------------------------------------------------ instruments
# INSTRUMENT 1: mirror-pair carrier swap (roles/Ananke/research/instruments/
# INSTRUMENT_CARRIER_SWAP.md). Swaps answer "does X CARRY the bit at t?";
# perturbations (delay, recipient roll) answer "is the mechanism sensitive
# to X?" and can never FLIP.

def _swap_fn(names, sub=None):
    return lambda w: swap(w, names, sub=sub)


def carriers(ph: Physics) -> dict:
    """name -> (kind, between-tick fn). kind 'swap' or 'perturb'."""
    c = {
        "site_all": ("swap", _swap_fn(SITE_ARRAYS)),
        "S": ("swap", _swap_fn(["S"])),
        "Kp": ("swap", _swap_fn(["Kp"])),
        "inbox": ("swap", _swap_fn(["Acc_sum", "Acc_cnt"])),
        "E": ("swap", _swap_fn(["E"])),
        "r": ("swap", _swap_fn(["r"])),
        "w": ("swap", _swap_fn(["w"])),
        "channel_all": ("swap", _swap_fn(FLIGHT_ARRAYS)),
        "channel_content": ("swap", _swap_fn(["Msum"])),
        "channel_count": ("swap", _swap_fn(["Mcnt"])),
        "delay+1": ("perturb", lambda w: roll_slots(w, 1)),
        "delay+2": ("perturb", lambda w: roll_slots(w, 2)),
        "recipient_roll": ("perturb", lambda w: roll_recipients(w, 1)),
    }
    for k in range(ph.payload_width):
        c[f"pay{k}"] = ("swap", _swap_fn(["Msum"], k))
    return c


def carrier_table(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, seeds, ticks,
                  names=None, device="cpu") -> dict:
    """Run each named carrier intervention at every tick in `ticks` (after
    that tick). Returns {'normal': ci, name: {'kind', 'acc': ci, 'verdict'}}.
    Verdict rule (swap_verdict): FLIP hi99 < .40; NO-EFFECT lo99 >= normal
    lo99 - .05; CHANCE otherwise. A 'perturb' FLIP is impossible by design;
    CHANCE there means 'sensitive'. arm_identical=True means the readout trace
    is bit-identical to normal in every world: the intervention never took
    effect (e.g. X is identical in both partners), so NO-EFFECT is trivial,
    not informative (W-D T-D3)."""
    base = run(ph, genome, env, seeds, device=device)
    nrm = trial_acc(base, range(env.trials))
    out = {"normal": ci(nrm)}
    cs = carriers(ph)
    for n in (names or cs):
        kind, fn = cs[n]
        tr = run(ph, genome, env, seeds, hooks={t: fn for t in ticks}, device=device)
        p = trial_acc(tr, range(env.trials))
        identical = bool(np.array_equal(tr.trace, base.trace))
        out[n] = {"kind": kind, "acc": ci(p), "verdict": swap_verdict(nrm, p),
                  "arm_identical": identical}
    return out


# INSTRUMENT 2: temporal reach (INSTRUMENT_TEMPORAL_REACH.md). Single-cue
# twins: pairs of worlds identical except for ONE trial's cue sign. The
# profile records, per tick, whether the delivery about to reach the
# actuator differs between twins (cue-bearing arrivals).

def cue_arrival_profile(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, trial: int = 5,
                        M: int = 64, ns: int = 0x5E1F, device="cpu") -> dict:
    seeds = assays.world_seeds(ns, M)
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.clone()
    tk0 = trial * env.period()
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
    sidx, ridx = ep.schedule.sense_idx.clone(), ep.schedule.read_idx.clone()
    for b in range(1, M, 2):
        sidx[b], ridx[b] = sidx[b - 1], ridx[b - 1]
    ws = [seeds[m - (m % 2)] for m in range(M)]
    w = World(ph, np.repeat(genome[None], M, 0), ws, device=device,
              schedule=Schedule(sidx, sv, ridx))
    a = w.read_idx[:, 0]
    bi = torch.arange(M, device=w.dev)
    ro = int(ep.ro_tick[0, trial])
    lags = {}
    for t in range(env.T()):
        slot = t % w.LM
        d, c = w.Msum[slot][bi, a], w.Mcnt[slot][bi, a]
        diff = (d[0::2] != d[1::2]).flatten(1).any(1) | (c[0::2] != c[1::2]).flatten(1).any(1)
        n = int(diff.sum())
        if n:
            lags[t - ro] = lags.get(t - ro, 0) + n
        w.step()
    return {"trial": trial, "cue_onset_lag": tk0 - ro, "lags": lags, "pairs": M // 2}


def reach(profile: dict, window_lags) -> float | None:
    """Fraction of the cue-bearing actuator arrivals (cue onset .. readout,
    inclusive) that fall inside window_lags (lags relative to the readout
    tick; 0 = the readout tick). None when there are no arrivals at all
    (reach is undefined, NOT zero)."""
    lo = profile["cue_onset_lag"]
    tot = {l: n for l, n in profile["lags"].items() if lo <= l <= 0}
    s = sum(tot.values())
    if s == 0:
        return None
    win = set(window_lags)
    return sum(n for l, n in tot.items() if l in win) / s
