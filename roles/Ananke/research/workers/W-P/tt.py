"""W-P truth-table swap runner (T-INS-8).

For one trial k and a set of swap offsets o, run the M normal worlds up to the
swap tick t_s = k*Pd + o (swap is applied AFTER tick t_s, as lens_swap.Arm),
snapshot the whole World state, then run K chimera blocks of M worlds from that
snapshot to the readout tick of trial k. Block j swaps, between mirror partners,
exactly the component set subsets[j] (a subset of `comps`). Each component is a
list of (array name, trailing-dims index) parts; the swap copies the partner's
values of those parts. Physics untouched: between-tick copies only.

Equivalence to lens_swap.run_arms (SINGLE arm, trial k): the prefix is the same
deterministic physics, the snapshot restores every state array, t and t_dev;
telemetry / stats are not read by the physics. check_vs_lens() asserts
bit-identical S0 readouts for site_all / channel_all / joint / normal blocks.
"""
from __future__ import annotations

import itertools

import numpy as np
import torch

from prometheus.ananke import envs, lens
from prometheus.ananke import lens_swap as LS
from prometheus.ananke.engine import World

ALL = (slice(None),)
STATE = ("S", "E", "r", "Kp", "Acc_sum", "Acc_cnt", "w", "Msum", "Mcnt")
FL = ("Msum", "Mcnt")


def coarse_components(ph, include_inert=True):
    """Brief's split. E only if the economy is on (else constant e_max)."""
    c = {"S": [("S", ALL)], "inbox": [("Acc_sum", ALL), ("Acc_cnt", ALL)], "Kp": [("Kp", ALL)]}
    if ph.rules > 1:
        c["r"] = [("r", ALL)]
    if include_inert or (ph.plastic_route and ph.dest_mode != "all"):
        c["w"] = [("w", ALL)]
    if ph.economy_on:
        c["E"] = [("E", ALL)]
    c["Msum"] = [("Msum", ALL)]
    c["Mcnt"] = [("Mcnt", ALL)]
    return c


SITE_NAMES = {"S", "E", "r", "Kp", "Acc_sum", "Acc_cnt", "w"}


def is_site(parts):
    return all(p[0] in SITE_NAMES for p in parts)


def all_subsets(n):
    return [tuple(b) for b in itertools.product((0, 1), repeat=n)]


def _snapshot(w: World):
    return {"t": w.t, **{n: getattr(w, n).clone() for n in STATE}}


def _swap_block(big: World, r0: int, M: int, parts):
    for name, sel in parts:
        a = getattr(big, name)
        if name == "w" and not big.R:
            continue
        v = a.transpose(0, 1) if name in FL else a          # batch first (view)
        blk = v[r0:r0 + M]
        src = blk.clone()
        src = src.reshape(M // 2, 2, *src.shape[1:]).flip(1).reshape(src.shape)
        idx = (slice(None),) + tuple(sel)       # sel indexes the dims after batch
        blk[idx] = src[idx]


def run_table(ph, genome, env, seeds, trial, offsets, comps: dict, subsets, device="cpu", chunk=None):
    """-> {o: s0 [K, M] int64} readout S0 of trial `trial` for every subset
    (tuple of 0/1 over comps order) at each offset; plus ep."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    Pd = env.period()
    t0 = trial * Pd
    ro = int(ep.ro_tick[0, trial])
    assert (ep.ro_tick[:, trial] == ro).all()
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    g = np.repeat(genome[None], M, 0)
    w = World(ph, g, ws1, device=device, schedule=ep.schedule)
    names = list(comps)
    snaps = {}
    need = sorted(t0 + o for o in offsets)
    for t in range(max(need) + 1):
        w.step()
        if t in need:
            snaps[t] = _snapshot(w)
    out = {}
    K = len(subsets)
    chunk = chunk or K
    for o in offsets:
        ts = t0 + o
        assert 0 <= ts < ro
        s0 = np.zeros((K, M), np.int64)
        for c0 in range(0, K, chunk):
            part = subsets[c0:c0 + chunk]
            Kc = len(part)
            big = World(ph, np.repeat(genome[None], M * Kc, 0), ws1 * Kc, device=device,
                        schedule=LS.tile_schedule(ep.schedule, Kc))
            sn = snaps[ts]
            for n in STATE:
                x = sn[n]
                a = getattr(big, n)
                a.copy_(x.repeat(1, Kc, *[1] * (x.dim() - 2)) if n in FL else x.repeat(Kc, *[1] * (x.dim() - 1)))
            big.t = sn["t"]
            big.t_dev.fill_(sn["t"])
            for j, z in enumerate(part):
                for bit, nm in zip(z, names):
                    if bit:
                        _swap_block(big, j * M, M, comps[nm])
            for _ in range(ts + 1, ro + 1):
                big.step()
            tr = big.trace[ro, :, 0].cpu().numpy().astype(np.int64)
            s0[c0:c0 + Kc] = tr.reshape(Kc, M)
        out[o] = s0
    return out, ep


def check_vs_lens(ph, genome, env, seeds, trial, offset, device="cpu"):
    """Bit-identity of this runner vs lens_swap.run_arms SINGLE arms."""
    comps = {"site": [(n, ALL) for n in LS.SITE], "chan": [(n, ALL) for n in LS.FLIGHT]}
    subs = [(0, 0), (1, 0), (0, 1), (1, 1)]
    mine, ep = run_table(ph, genome, env, seeds, trial, [offset], comps, subs, device)
    arms = [LS.Arm("normal"), LS.Arm("s", tuple(LS.SITE), offset, trial),
            LS.Arm("c", tuple(LS.FLIGHT), offset, trial), LS.Arm("j", tuple(LS.SITE + LS.FLIGHT), offset, trial)]
    r = LS.run_arms(ph, genome, env, seeds, arms, device=device, early_stop=False)
    ref = [r.s0["normal"][:, trial], r.s0["s"][:, trial], r.s0["c"][:, trial], r.s0["j"][:, trial]]
    return [bool(np.array_equal(mine[offset][i], ref[i])) for i in range(4)]
