"""W-R (T-INS-9): forked SINGLE-trial carrier-swap runner + update-clock phase
stratification of the frozen lens_swap census.

fork_single() is meant to be bit-identical to lens_swap.run_arms with SINGLE
arms (checked in KA-F): one normal run of M worlds; for each trial k the state
after tick k*Pd + o_min is tiled into one block of M worlds per arm; each arm's
swap is applied after tick k*Pd + o; the forked world runs to trial k's
readout. Nothing in prometheus/ananke is edited; lens_swap.census/classify are
used unchanged.
"""
from __future__ import annotations

import numpy as np
import torch

from prometheus.ananke import envs, lens_swap as LS
from prometheus.ananke.engine import Controls, World

NOT_RUN = LS.NOT_RUN


# ------------------------------------------------------------- bookkeeping
def phase_of(k: int, o: int, Pd: int, p: int) -> int:
    """Update-clock phase of the tick after which trial k's swap at offset o
    is applied: (t0 + o) mod p, t0 = k*Pd. 0 = the swap tick was a wake tick
    (sync physics wakes iff t mod p == 0)."""
    return (k * Pd + o) % p


def phase_table(trials, offsets, Pd: int, p: int) -> dict:
    """{offset: {trial: phase}}."""
    return {o: {k: phase_of(k, o, Pd, p) for k in trials} for o in offsets}


def strata(trials, o, Pd, p):
    """{phase: [trials]} for one offset (every phase 0..p-1 present, maybe empty)."""
    out = {q: [] for q in range(p)}
    for k in trials:
        out[phase_of(k, o, Pd, p)].append(k)
    return out


# ------------------------------------------------------------- runner
def _tile_state(src: World, dst: World, K: int):
    for n, v in src.state_arrays().items():
        d = getattr(dst, n)
        if n in ("Msum", "Mcnt"):
            d.copy_(v.repeat(1, K, *([1] * (v.dim() - 2))))
        else:
            d.copy_(v.repeat(K, *([1] * (v.dim() - 1))))
    dst.t = src.t
    dst.t_dev.fill_(src.t)


def fork_single(ph, genome, env, seeds, offsets, trials, device="cpu", ctrl=None, chunk=16,
                late=0, log=None):
    """Returns (ep, normal_per_trial [M,tr], normal_s0 [M,tr], site, chan, s0_site, s0_chan) where
    site[o] etc are [M, tr] arrays filled only at the trials in `trials` (NaN / NOT_RUN elsewhere),
    exactly as lens_swap.mixture_scan(mode='single') assembles them.
    late: MUST-FAIL knob; fork `late` ticks after the correct fork tick."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd, T = env.period(), env.T()
    ctrl = ctrl or Controls()
    offsets = sorted(offsets)
    omin = offsets[0]
    arms = [(o, nm) for o in offsets for nm in ("site", "chan")]
    names = {"site": LS.SITE, "chan": LS.FLIGHT}
    base = World(ph, np.repeat(genome[None], M, 0), ws1, device=device, ctrl=ctrl, schedule=ep.schedule)
    fork_at = {k: k * Pd + omin + late for k in trials}      # fork AFTER this tick
    nt = env.trials
    site = {o: np.full((M, nt), np.nan) for o in offsets}
    chan = {o: np.full((M, nt), np.nan) for o in offsets}
    s0s = {o: np.full((M, nt), NOT_RUN, np.int64) for o in offsets}
    s0c = {o: np.full((M, nt), NOT_RUN, np.int64) for o in offsets}
    for t in range(T):
        base.step()
        for k in [k for k, ft in fork_at.items() if ft == t]:
            ro = int(ep.ro_tick[:, k].max())
            for c0 in range(0, len(arms), chunk):
                part = arms[c0:c0 + chunk]
                K = len(part)
                w = World(ph, np.repeat(genome[None], M * K, 0), ws1 * K, device=device, ctrl=ctrl,
                          schedule=LS.tile_schedule(ep.schedule, K))
                _tile_state(base, w, K)
                hooks = {}
                for j, (o, nm) in enumerate(part):
                    rows = torch.arange(j * M, (j + 1) * M, device=w.dev)
                    hooks.setdefault(k * Pd + o, []).append((names[nm], rows))
                # swaps due at the fork tick itself (o == omin, or earlier when late > 0)
                for tt in sorted(hooks):
                    if tt <= t:
                        for nms, rows in hooks[tt]:
                            LS.swap_rows(w, nms, rows)
                for t2 in range(t + 1, ro + 1):
                    w.step()
                    for nms, rows in hooks.get(t2, ()):
                        LS.swap_rows(w, nms, rows)
                tr = w.trace.cpu().numpy()
                for j, (o, nm) in enumerate(part):
                    trj = tr[:, j * M:(j + 1) * M]
                    p = envs.per_trial(ep, trj).astype(float)[:, k]
                    s0 = trj[ep.ro_tick[:, k], np.arange(M), ep.ro_slot[:, k]].astype(np.int64)
                    p[~ep.scored[:, k]] = np.nan
                    (site if nm == "site" else chan)[o][:, k] = p
                    (s0s if nm == "site" else s0c)[o][:, k] = s0
            if log:
                log(f"trial {k} done")
    tr = base.trace.cpu().numpy()
    normal = envs.per_trial(ep, tr).astype(float)
    normal[~ep.scored] = np.nan
    ns0 = tr[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot].astype(np.int64)
    return ep, normal, ns0, site, chan, s0s, s0c


# ------------------------------------------------------------- stratified census
def phase_diff_boot(normal, site, chan, s0_site, s0_chan, tr0, tr1, n_boot=2000, seed=1, alpha=0.01):
    """dfX = fX(trials tr1) - fX(trials tr0), same resampled pairs for both strata."""
    t0 = LS.pair_trial_table(normal, site, chan, s0_site, s0_chan, tr0)
    t1 = LS.pair_trial_table(normal, site, chan, s0_site, s0_chan, tr1)
    P = normal.shape[0] // 2

    def fr(tab, pairs):
        ok = tab["ok"][pairs]
        n = ok.sum()
        if n == 0:
            return None
        pat = tab["pat"][pairs][ok]
        return {x: float(np.mean(pat == x)) for x in ("S", "C", "N")}
    a, b = fr(t0, np.arange(P)), fr(t1, np.arange(P))
    if a is None or b is None:
        return None
    res = {f"d{x}": b[x] - a[x] for x in ("S", "C", "N")}
    rng = np.random.default_rng(seed)
    bs = {x: [] for x in ("S", "C", "N")}
    for _ in range(n_boot):
        pr = rng.integers(P, size=P)
        a2, b2 = fr(t0, pr), fr(t1, pr)
        if a2 is None or b2 is None:
            continue
        for x in bs:
            bs[x].append(b2[x] - a2[x])
    res["ci99"] = {f"d{x}": (float(np.quantile(v, alpha / 2)), float(np.quantile(v, 1 - alpha / 2)))
                   for x, v in bs.items() if v}
    return res


def phase_effect(diff, n0, n1, floor=0.10) -> bool:
    """Frozen rule PLAN s2: both strata >= MIN_ELIGIBLE and some 99% CI of dfX
    excludes 0 with |dfX| >= floor."""
    if diff is None or n0 < LS.MIN_ELIGIBLE or n1 < LS.MIN_ELIGIBLE:
        return False
    for x in ("S", "C", "N"):
        lo, hi = diff["ci99"][f"d{x}"]
        if (lo > 0 or hi < 0) and abs(diff[f"d{x}"]) >= floor:
            return True
    return False


CLEAN = ("SITE", "CHANNEL")
MIXED = ("MIXTURE", "UNRESOLVED", "NEITHER")


def resolution(pooled: str, per: list) -> str | None:
    """PLAN s2 rule. per = per-phase classes (UNDEFINED allowed)."""
    if pooled not in MIXED:
        return None
    clean = [c in CLEAN for c in per]
    defined = [c != "UNDEFINED" for c in per]
    if all(clean) and all(defined):
        return "RESOLVES"
    if any(clean):
        return "PARTLY"
    return "STAYS_MIXED"


def stratified(normal, ns0, scored, site, chan, s0s, s0c, trials, offsets, Pd, p, follow=False,
               n_boot=2000, permute=None):
    """Per offset: pooled + per-phase frozen census/class, phase diff, resolution.
    permute: optional dict {trial: phase} replacing the true phase labels (MUST-FAIL)."""
    out = {}
    for o in offsets:
        st = strata(trials, o, Pd, p)
        if permute is not None:
            st = {q: [k for k in trials if permute[o][k] == q] for q in range(p)}
        args = (normal, site[o], chan[o], s0s[o], s0c[o])
        r = {"phase_trials": {str(q): v for q, v in st.items()}}
        for lab, trs in [("pooled", list(trials))] + [(f"q{q}", st[q]) for q in range(p)]:
            if not trs:
                c = {"eligible": 0, "class": "UNDEFINED"}
            else:
                c = LS.census(*args, trs, n_boot=n_boot)
                c["class"] = LS.classify(c)
                if follow:
                    f = LS.census_follow(ns0, s0s[o], s0c[o], scored, trs, n_boot=n_boot)
                    f["class"] = LS.classify(f)
                    c["follow"] = f
            r[lab] = c
        if p == 2:
            d = phase_diff_boot(*args, st[0], st[1], n_boot=n_boot) if st[0] and st[1] else None
            r["diff"] = d
            r["phase_effect"] = phase_effect(d, r["q0"]["eligible"], r["q1"]["eligible"])
            r["resolution"] = resolution(r["pooled"]["class"], [r["q0"]["class"], r["q1"]["class"]])
            if follow:
                r["resolution_follow"] = resolution(r["pooled"]["follow"]["class"],
                                                    [r[q]["follow"]["class"] if "follow" in r[q] else "UNDEFINED"
                                                     for q in ("q0", "q1")])
        out[o] = r
    return out
