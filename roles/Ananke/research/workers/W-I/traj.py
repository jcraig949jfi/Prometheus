"""W-I two-axis carrier-trajectory helper (does NOT edit lens.py / engine).

Axis (b) READER: mirror-pair carrier swaps at EVERY tick offset of the
cue->readout interval, many arms batched into ONE World (each arm owns a
block of 64 worlds = 32 mirror pairs; swaps act only inside the block, so
blocks are independent; bit-identity with lens.run is checked by
selfcheck()).
Axis (a) PHYSICAL: single-cue twins (worlds identical except for one
trial's cue sign), recording per tick which state differs between twins.
All interventions act between ticks; physics untouched.
"""
from __future__ import annotations

import numpy as np
import torch

from prometheus.ananke import assays, envs, lens
from prometheus.ananke.engine import Controls, Schedule, World

SITE = list(lens.SITE_ARRAYS)
FLIGHT = list(lens.FLIGHT_ARRAYS)
ARMS = {
    "site_all": SITE,
    "channel_all": FLIGHT,
    "joint": SITE + FLIGHT,
    "S": ["S"],
    "inbox": ["Acc_sum", "Acc_cnt"],
    "Kp": ["Kp"],
    "E": ["E"],
    "r": ["r"],
    "w": ["w"],
    "channel_content": ["Msum"],
    "channel_count": ["Mcnt"],
}


def arm_names(ph):
    a = ["site_all", "channel_all", "joint", "S", "inbox", "channel_content", "channel_count"]
    if ph.wimm or ph.mut_site > 0:
        a.append("Kp")
    if ph.rules > 1 and ph.setrule:
        a.append("r")
    if ph.plastic_route and ph.table_width() > 0:
        a.append("w")
    if ph.economy_on:
        a.append("E")
    return a


def swap_rows(w: World, names, rows: torch.Tensor):
    p = rows ^ 1
    for n in names:
        if n == "w" and not w.R:
            continue
        a = getattr(w, n)
        if n in lens.FLIGHT_ARRAYS:
            a[:, rows] = a[:, p]
        else:
            a[rows] = a[p]


def tile_schedule(sch: Schedule, K: int) -> Schedule:
    return Schedule(sch.sense_idx.repeat(K, 1), sch.sense_val.repeat(1, K, 1), sch.read_idx.repeat(K, 1))


def run_arms(ph, genome, env, seeds, arms, device="cuda", ctrl=None, chunk=48):
    """arms: list of (label, names or None, offset). offset = ticks after
    trial onset t0 at which the swap is applied (after that tick), in every
    trial where t0+offset >= 0. names None = normal arm.
    Returns {label: per_trial [M, trials]} and {label: arm_identical} vs the
    first None arm (which must be present)."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd = env.period()
    out, trs = {}, {}
    for c0 in range(0, len(arms), chunk):
        part = arms[c0:c0 + chunk]
        K = len(part)
        sch = tile_schedule(ep.schedule, K)
        g = np.repeat(genome[None], M * K, 0)
        w = World(ph, g, ws1 * K, device=device, ctrl=ctrl or Controls(), schedule=sch)
        hooks = {}
        for j, (lab, names, off) in enumerate(part):
            if names is None:
                continue
            rows = torch.arange(j * M, (j + 1) * M, device=w.dev)
            for k in range(env.trials):
                t = k * Pd + off
                if t >= 0:
                    hooks.setdefault(t, []).append((names, rows))
        for t in range(env.T()):
            w.step()
            for names, rows in hooks.get(t, ()):
                swap_rows(w, names, rows)
        tr = w.trace.cpu().numpy()
        for j, (lab, names, off) in enumerate(part):
            trj = tr[:, j * M:(j + 1) * M]
            trs[lab] = trj
            out[lab] = envs.per_trial(ep, trj)
    return ep, out, trs


def pair_acc(per_trial, ep, trials):
    sel = np.zeros_like(ep.scored)
    sel[:, list(trials)] = True
    sel &= ep.scored
    v = np.where(sel, per_trial, np.nan)
    return np.nanmean(v, 1).reshape(-1, 2).mean(-1)


def selfcheck(ph, genome, env, seeds, device="cuda"):
    """Batched arms must be bit-identical to lens.run with the same hooks."""
    off = 3
    arms = [("normal", None, 0), ("site_all@3", SITE, off), ("channel_all@3", FLIGHT, off)]
    ep, pt, trs = run_arms(ph, genome, env, seeds, arms, device=device)
    Pd = env.period()
    ok = {}
    for lab, names, _ in arms:
        if names is None:
            ref = lens.run(ph, genome, env, seeds, device=device)
        else:
            fn = (lambda nm: (lambda w: lens.swap(w, nm)))(names)
            ref = lens.run(ph, genome, env, seeds, device=device,
                           hooks={k * Pd + off: fn for k in range(env.trials)})
        ok[lab] = bool(np.array_equal(ref.trace, trs[lab]))
    return ok


# ------------------------------------------------------------------ axis (a)
def twin_profile(ph, genome, env, ns, trials=(3, 5, 7), M=64, device="cuda"):
    """Per tick of [t0-1, ro] (offsets relative to t0) for each twin trial:
    fraction of twin pairs in which each state class differs, plus spatial
    stats. Twins: world 2p+1 = world 2p with ONLY trial k's cue negated."""
    seeds = assays.world_seeds(ns, M)
    ep0 = envs.build(ph, env, seeds)
    K = len(trials)
    Pd = env.period()
    sv = ep0.schedule.sense_val.clone().repeat(1, K, 1)
    sidx = ep0.schedule.sense_idx.clone().repeat(K, 1)
    ridx = ep0.schedule.read_idx.clone().repeat(K, 1)
    for j, k in enumerate(trials):
        tk0 = k * Pd
        for b in range(1, M, 2):
            B, A = j * M + b, j * M + b - 1
            sv[:, B] = sv[:, A]
            sv[tk0:tk0 + env.cue_len, B] = -sv[tk0:tk0 + env.cue_len, A]
            sidx[B], ridx[B] = sidx[A], ridx[A]
    ws = [seeds[m - (m % 2)] for m in range(M)] * K
    w = World(ph, np.repeat(genome[None], M * K, 0), ws, device=device, schedule=Schedule(sidx, sv, ridx))
    Dm = torch.as_tensor(envs.dist_matrix(ph), device=w.dev).clamp(max=10 ** 3)
    src = sidx[:, 0].to(w.dev)             # first sensor site
    act = ridx[:, 0].to(w.dev)
    dsrc = Dm[src]                          # [B, N]
    dact = Dm[act]
    ev = w.dev
    offs = {}
    tmin = min(k * Pd - 1 for k in trials)
    tmax = max(int(ep0.ro_tick[0, k]) for k in trials)
    rec = {j: {} for j in range(K)}
    for t in range(tmax + 1):
        w.step()
        if t < tmin:
            continue
        E0, E1 = slice(0, None, 2), slice(1, None, 2)

        def d_site(x):                      # [B/2, N] any-diff per site
            dd = x[E0] != x[E1]
            return dd.flatten(2).any(-1) if dd.dim() > 2 else dd
        S = d_site(w.S)
        inbox = d_site(w.Acc_sum) | d_site(w.Acc_cnt)
        Kp = d_site(w.Kp)
        En = d_site(w.E)
        r = d_site(w.r)
        wd = d_site(w.w) if w.R else torch.zeros_like(S)
        mc = w.Mcnt[:, E0] != w.Mcnt[:, E1]                     # [LM,P2,N,C]
        ms = (w.Msum[:, E0] != w.Msum[:, E1]).any(-1)
        cnt_site = mc.any(0).any(-1)                            # [P2,N] recipients w/ count diff
        pay_site = (ms & ~mc).any(0).any(-1)                    # payload-only diff
        e = w.last_emit
        fire = e[E0] != e[E1]
        both = e[E0] & e[E1]
        epay = both & (w.last_pay[E0] != w.last_pay[E1]).any(-1)
        echan = both & (w.last_chan[E0] != w.last_chan[E1])
        ds, da = dsrc[E0].float(), dact[E0].float()
        for j, k in enumerate(trials):
            t0 = k * Pd
            ro = int(ep0.ro_tick[0, k])
            if not (t0 - 1 <= t <= ro):
                continue
            sl = slice(j * M // 2, (j + 1) * M // 2)
            o = t - t0

            def frac(x):
                return float(x[sl].any(-1).float().mean())

            def mean_n(x):
                return float(x[sl].sum(-1).float().mean())

            def mdist(x, dd):
                m = x[sl].float()
                n = m.sum()
                return float((m * dd[sl]).sum() / n) if n > 0 else None
            rec[j][o] = {
                "S": frac(S), "S_act": float(S[sl][torch.arange(M // 2, device=ev), act[E0][sl]].float().mean()),
                "nS": mean_n(S), "S_dsrc": mdist(S, ds), "S_dact": mdist(S, da),
                "inbox": frac(inbox), "Kp": frac(Kp), "E": frac(En), "r": frac(r), "w": frac(wd),
                "fl_cnt": frac(cnt_site), "fl_pay": frac(pay_site), "n_fl": mean_n(cnt_site | pay_site),
                "fl_dact": mdist(cnt_site | pay_site, da),
                "fire": frac(fire), "n_fire": mean_n(fire), "fire_dsrc": mdist(fire, ds),
                "fire_at_src": float(fire[sl][torch.arange(M // 2, device=ev), src[E0][sl]].float().mean()),
                "emit_pay": frac(epay), "emit_chan": frac(echan),
                "ro_offset": ro - t0,
            }
    # average over twin trials per offset
    all_o = sorted(set().union(*[set(v) for v in rec.values()]))
    avg = {}
    for o in all_o:
        rows = [rec[j][o] for j in rec if o in rec[j]]
        a = {}
        for key in rows[0]:
            vals = [x[key] for x in rows if x[key] is not None]
            a[key] = float(np.mean(vals)) if vals else None
        avg[o] = a
    return {"per_trial": {str(trials[j]): rec[j] for j in rec}, "avg": avg}


PHYS_KEYS = ("S", "inbox", "Kp", "r", "w", "E", "fl_cnt", "fl_pay", "fire", "emit_pay", "emit_chan")
PHYS_CODE = {"S": "s", "inbox": "i", "Kp": "k", "r": "r", "w": "w", "E": "e",
             "fl_cnt": "N", "fl_pay": "V", "fire": "F", "emit_pay": "P", "emit_chan": "H"}


def phys_label(row, thr=0.5):
    return "".join(PHYS_CODE[k] for k in PHYS_KEYS if (row.get(k) or 0) >= thr) or "-"
