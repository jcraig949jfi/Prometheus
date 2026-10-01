"""W-O re-run machinery (T-SWAP-AUDIT). Imports frozen engine / lens / lens_swap
read-only; never edits them.

fork_single: SINGLE-trial swaps by forking (own implementation of the idea in
W-N plants_rel.run_fork): one normal world runs the whole episode; after tick
k*Pd+offset a deep copy per arm is swapped (all mirror pairs, lens_swap.swap_rows)
and stepped to trial k's readout. Must be bit-identical, at the readout, to
lens_swap.run_arms with Arm(label, names, offset, trial=k) (selfcheck()).
every_arms: EVERY-trial swaps through lens_swap.run_arms (trial=None).
"""
from __future__ import annotations

import copy
import pathlib
import sys

import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
for p in (str(REPO), str(HERE.parent / "W-N")):
    if p not in sys.path:
        sys.path.insert(0, p)
from prometheus.ananke import assays, c1b, c1b_run, envs, lens, lens_swap  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
import swap_rel as sr  # noqa: E402  (W-N relative rule; imported, not edited)

NS = 0x600
M = 512
NOT_RUN = lens_swap.NOT_RUN
SITE = tuple(lens.SITE_ARRAYS)
FLIGHT = tuple(lens.FLIGHT_ARRAYS)
ARMS = {"site_all": SITE, "channel_all": FLIGHT, "joint": SITE + FLIGHT, "S": ("S",),
        "inbox": ("Acc_sum", "Acc_cnt"), "Kp": ("Kp",), "E": ("E",), "r": ("r",), "w": ("w",),
        "channel_content": ("Msum",), "channel_count": ("Mcnt",),
        "inflight": FLIGHT, "sitestate": SITE, "payload": ("Msum",), "counts": ("Mcnt",)}


def seeds(M_=M, ns=NS):
    return assays.world_seeds(ns, M_)


def load(loader: str, specimen: str):
    """-> (ph, env, genome)."""
    if loader == "c1_row":
        ph, env, g, _ = c1b_run.load(specimen)
        return ph, env, g
    if loader == "d_wave":
        for r in c1b_run.d_wave_cells():
            if r["extra"]["source_cell"].startswith(specimen):
                return (Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"]),
                        np.asarray(r["extra"]["genome"], dtype=np.int64))
    raise KeyError((loader, specimen))


def sct_offset(env) -> int:
    tk = c1b.ticks(env)
    if env.family == "HOLD":
        return tk["mid"][0] - tk["t0"][0]
    return max(1, env.delta // 2)


def _swap_all(w, names, arrays_sub=None):
    rows = torch.arange(w.B, device=w.dev)
    if arrays_sub is not None:          # payload component k of Msum (pay<k>)
        p = rows ^ 1
        w.Msum[:, rows, ..., arrays_sub] = w.Msum[:, p, ..., arrays_sub]
        return
    lens_swap.swap_rows(w, names, rows)


def fork_single(ph, g, env, sd, arms: dict, offset: int, trials, device="cpu"):
    """arms: {label: names tuple | ('pay', k)}. Returns (ep, normal_pt, {label: pt}, n_s0, {label: s0})."""
    Mw = len(sd)
    ep = envs.build(ph, env, sd)
    ws1 = [sd[m - (m % 2)] for m in range(Mw)]
    Pd, T = env.period(), env.T()
    w = World(ph, np.repeat(g[None], Mw, 0), ws1, device=device, ctrl=Controls(), schedule=ep.schedule)
    s0 = {k: np.full(ep.y.shape, NOT_RUN, np.int64) for k in arms}
    fork_at = {}
    for k in trials:
        t = k * Pd + offset
        if 0 <= t < T:
            fork_at.setdefault(t, []).append(k)
    bi = np.arange(Mw)
    for t in range(T):
        w.step()
        for k in fork_at.get(t, ()):
            ro = ep.ro_tick[:, k]
            for lab, names in arms.items():
                c = copy.deepcopy(w)
                if names and names[0] == "pay":
                    _swap_all(c, None, names[1])
                else:
                    _swap_all(c, names)
                for _ in range(t + 1, int(ro.max()) + 1):
                    c.step()
                tr = c.trace.cpu().numpy()
                s0[lab][:, k] = tr[ro, bi, ep.ro_slot[:, k]]
    trn = w.trace.cpu().numpy()
    n0 = trn[ep.ro_tick, bi[:, None], ep.ro_slot].astype(np.int64)

    def score(v):
        p = np.where(v == 0, 0.5, (np.sign(v) == ep.y).astype(float))
        return np.where((v != NOT_RUN) & ep.scored, p, np.nan)
    return ep, score(n0), {k: score(v) for k, v in s0.items()}, n0, s0


def every_arms(ph, g, env, sd, arms: dict, offset: int, device="cpu", chunk=8):
    """EVERY-trial swaps; payload-component arms are not supported here (none in scope
    need EVERY besides those handled by lens.swap sub)."""
    al = [lens_swap.Arm("normal")] + [lens_swap.Arm(lab, tuple(n), offset) for lab, n in arms.items()]
    r = lens_swap.run_arms(ph, g, env, sd, al, device=device, chunk=chunk, early_stop=False)
    return r


def every_pay(ph, g, env, sd, k: int, offset: int, device="cpu"):
    Pd = env.period()
    fn = lambda w: lens.swap(w, ["Msum"], sub=k)
    hooks = {j * Pd + offset: fn for j in range(env.trials) if j * Pd + offset >= 0}
    return lens.run(ph, g, env, sd, hooks=hooks, device=device)


def trial_mask(nt, trials):
    keep = np.zeros(nt, bool)
    keep[list(trials)] = True
    return keep


def verdicts(normal_pt, swap_pt, trials):
    """Absolute (lens.swap_verdict on PAIRED pair means over the design's trials),
    plus W-N relative rule ungated (secondary)."""
    keep = trial_mask(normal_pt.shape[1], trials)[None]
    n = np.where(keep, normal_pt, np.nan)
    s = np.where(keep, swap_pt, np.nan)
    both = ~np.isnan(n) & ~np.isnan(s)
    a = sr.pair_means(np.where(both, n, np.nan))
    b = sr.pair_means(np.where(both, s, np.nan))
    ok = ~np.isnan(a) & ~np.isnan(b)
    a, b = a[ok], b[ok]
    out = {"P": int(ok.sum()), "cells": int(both.sum()), "normal": lens.ci(a), "swap": lens.ci(b),
           "abs": lens.swap_verdict(a, b)}
    rel = sr.swap_verdict_rel(n, s, pmin=0.5)
    out["rel_ungated"] = rel["verdict_ungated"]
    out["z"] = rel["z"]
    return out
