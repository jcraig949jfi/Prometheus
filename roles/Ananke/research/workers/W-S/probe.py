"""W-S (T-INS-11): delivery-timing probe for the mixed swap-tick phase.

Two pieces, nothing in prometheus/ananke is edited:
1. LogWorld(World): the normal run, plus a LOG of every mirror-different
   packet copy (emitter v, emit tick te, copy f, recipient, delay, latency
   jitter draw, hop distance, delivered?, payload) for mirror pair p.
   The draws are recomputed with exactly the engine's formulas, then the
   engine's own _emit runs unchanged (the log never touches state).
   Checked in KA-L: the in-flight mirror differences addressed to the readout
   site reconstructed from the log equal the real Msum/Mcnt differences.
2. fork(): W-R fork_single's structure (fork after tick k*Pd + o_min, tile
   state, swap after tick k*Pd + o, run to trial k's readout) with four
   arms: site (all SITE arrays), chan (all FLIGHT arrays) -- bit-identical to
   W-R/lens_swap (KA-F) -- plus two targeted arms: site_a (SITE arrays at the
   readout site only) and flight_a (in-flight entries addressed to the
   readout site only).
"""
from __future__ import annotations

import importlib.util
import pathlib

import numpy as np
import torch

from prometheus.ananke import envs, lens, lens_swap as LS, rng
from prometheus.ananke.engine import Controls, World

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("wr_fork", HERE.parent / "W-R" / "fork.py")
WR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WR)

NOT_RUN = LS.NOT_RUN
LOG_KEYS = ("te", "p", "v", "f", "recA", "recB", "dlA", "dlB", "delay", "delayB", "jit", "dist",
            "payA", "payB")


class LogWorld(World):
    """Normal physics + a sparse log of mirror-different packet copies."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        ph, c = self.ph, self.ctrl
        assert ph.topology != "global" and ph.dup == 0 and ph.noise == 0
        assert not (c.shuffle_dest or c.shuffle_time or c.randomize_payload or c.zero_comm)
        assert self.B % 2 == 0
        self.log = {k: [] for k in LOG_KEYS}

    def _emit(self, want, chan, pay):
        ph = self.ph
        B, N, F = self.B, self.N, ph.copies()
        dev, t = self.dev, self.t_dev
        fidx = torch.arange(F, device=dev, dtype=torch.int64)

        def draws(stream, extra=0):
            return rng.chain(rng.site_base(self.ws, stream, t, self.sites)[..., None], fidx + extra)

        if ph.dest_mode == "all":
            rec = self.nbr[None].expand(B, N, F)
            dist = self.dist[None].expand(B, N, F)
        else:
            h = draws(rng.ROUTE)
            w = self.w.to(torch.int64)
            W = w.sum(-1, keepdim=True)
            cs = torch.cumsum(w, -1)
            u = torch.remainder(h, W.clamp(min=1))
            j_w = (cs[:, :, None, :] <= u[..., None]).sum(-1)
            j = torch.where(W > 0, j_w, torch.remainder(h, self.R))
            rec = torch.gather(self.nbr[None].expand(B, N, self.R), 2, j)
            dist = torch.gather(self.dist[None].expand(B, N, self.R), 2, j)
        surv = self.surv16[dist]
        alive = (draws(rng.LOSS) & 0xFFFF) < surv
        jit = torch.remainder(draws(rng.LAT), ph.lat_jitter + 1)
        delay = (ph.lat_base + ph.lat_hop * dist + jit).clamp(1, self.LM - 1)
        dl = want[..., None] & alive                                   # delivered copy [B,N,F]
        A, Bq = slice(0, None, 2), slice(1, None, 2)
        payd = (pay[A] != pay[Bq]).any(-1)[..., None]                  # [P,N,1]
        md = (dl[A] != dl[Bq]) | (dl[A] & dl[Bq] & ((rec[A] != rec[Bq]) | (delay[A] != delay[Bq]) | payd))
        # a copy is also mirror-different if the channel differs (C>1 physics)
        if ph.channels > 1:
            md |= dl[A] & dl[Bq] & (chan[A] != chan[Bq])[..., None]
        idx = md.nonzero(as_tuple=False)
        if idx.numel():
            p, v, f = idx[:, 0], idx[:, 1], idx[:, 2]
            a, b = 2 * p, 2 * p + 1
            L = self.log
            L["te"].append(np.full(len(p), self.t, np.int32))
            for k, x in (("p", p), ("v", v), ("f", f), ("recA", rec[a, v, f]), ("recB", rec[b, v, f]),
                         ("dlA", dl[a, v, f]), ("dlB", dl[b, v, f]), ("delay", delay[a, v, f]),
                         ("delayB", delay[b, v, f]), ("jit", jit[a, v, f]), ("dist", dist[a, v, f]),
                         ("payA", pay[a, v, 0]), ("payB", pay[b, v, 0])):
                L[k].append(x.cpu().numpy().astype(np.int32))
        super()._emit(want, chan, pay)

    def log_arrays(self) -> dict:
        return {k: (np.concatenate(v) if v else np.zeros(0, np.int32)) for k, v in self.log.items()}


def swap_targeted(w: World, kind: str, rows: torch.Tensor, ai: torch.Tensor):
    """site_a: every SITE array at the readout site only; flight_a: the in-flight
    slots addressed to the readout site only (all channels)."""
    p = rows ^ 1
    if kind == "site_a":
        for n in lens.SITE_ARRAYS:
            if n == "w" and not w.R:
                continue
            a = getattr(w, n)
            a[rows, ai] = a[p, ai]
    elif kind == "flight_a":
        for n in lens.FLIGHT_ARRAYS:
            a = getattr(w, n)
            a[:, rows, ai] = a[:, p, ai]
    else:
        raise ValueError(kind)


ARM_KINDS = ("site", "chan", "site_a", "flight_a")


def _apply(w, kind, rows, ai):
    if kind == "site":
        LS.swap_rows(w, LS.SITE, rows)
    elif kind == "chan":
        LS.swap_rows(w, LS.FLIGHT, rows)
    else:
        swap_targeted(w, kind, rows, ai)


def cue_flip_run(ph, genome, env, ep, base: World, k: int, ws1, device="cpu"):
    """Cue-bearing packets of trial k. From the normal state after tick t0-1, run 2M interleaved rows:
    row 2m = world m (normal), row 2m+1 = world m with trial k's cue sign flipped (same world seed, so
    every route/loss/latency draw is shared). The LogWorld pair log then lists exactly the packet copies
    that change when trial k's cue changes (log 'p' = world index m). Runs to trial k's readout.
    Returns (log arrays, readout_differs [M] bool)."""
    M = base.B
    t0 = k * env.period()
    ro = int(ep.ro_tick[:, k].max())
    sch = ep.schedule
    sv = sch.sense_val.repeat_interleave(2, 1).clone()
    sv[t0:t0 + env.cue_len, 1::2, :] *= -1
    s2 = type(sch)(sch.sense_idx.repeat_interleave(2, 0), sv, sch.read_idx.repeat_interleave(2, 0))
    w = LogWorld(ph, np.repeat(genome[None], 2 * M, 0), [x for x in ws1 for _ in (0, 1)], device=device,
                 ctrl=Controls(), schedule=s2)
    for n, v in base.state_arrays().items():
        getattr(w, n).copy_(v.repeat_interleave(2, 1 if n in ("Msum", "Mcnt") else 0))
    w.t = base.t
    w.t_dev.fill_(base.t)
    assert w.t == t0
    for _ in range(t0, ro + 1):
        w.step()
    tr = w.trace.cpu().numpy()
    rt = ep.ro_tick[:, k]
    diff = tr[rt, 2 * np.arange(M), 0] != tr[rt, 2 * np.arange(M) + 1, 0]
    return w.log_arrays(), diff


def fork(ph, genome, env, seeds, offsets, trials, kinds=ARM_KINDS, device="cpu", chunk=16, log=None,
         snap_offsets=(), cue=True):
    """Returns dict(ep, normal, ns0, res={kind: {o: (per [M,nt], s0 [M,nt])}}, elog, snaps).
    snaps[(k, o)] = (Msum, Mcnt) of the normal run after tick k*Pd+o (for KA-L), only for o in snap_offsets."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd, T = env.period(), env.T()
    offsets = sorted(offsets)
    omin = offsets[0]
    arms = [(o, kd) for o in offsets for kd in kinds]
    base = LogWorld(ph, np.repeat(genome[None], M, 0), ws1, device=device, ctrl=Controls(),
                    schedule=ep.schedule)
    ro_site = torch.as_tensor(ep.schedule.read_idx[:, 0], dtype=torch.int64)
    fork_at = {k: k * Pd + omin for k in trials}
    snap_at = {k * Pd + o: (k, o) for k in trials for o in snap_offsets}
    nt = env.trials
    res = {kd: {o: (np.full((M, nt), np.nan), np.full((M, nt), NOT_RUN, np.int64)) for o in offsets}
           for kd in kinds}
    snaps = {}
    cue_logs, cue_diff = {}, {}
    cue_at = {k * Pd - 1: k for k in trials} if cue else {}
    for t in range(T):
        base.step()
        if t in cue_at:
            kk = cue_at[t]
            cue_logs[kk], cue_diff[kk] = cue_flip_run(ph, genome, env, ep, base, kk, ws1, device)
        if t in snap_at:
            snaps[snap_at[t]] = (base.Msum.clone(), base.Mcnt.clone())
        for k in [k for k, ft in fork_at.items() if ft == t]:
            ro = int(ep.ro_tick[:, k].max())
            for c0 in range(0, len(arms), chunk):
                part = arms[c0:c0 + chunk]
                K = len(part)
                w = World(ph, np.repeat(genome[None], M * K, 0), ws1 * K, device=device, ctrl=Controls(),
                          schedule=LS.tile_schedule(ep.schedule, K))
                WR._tile_state(base, w, K)
                hooks = {}
                for j, (o, kd) in enumerate(part):
                    rows = torch.arange(j * M, (j + 1) * M, device=w.dev)
                    hooks.setdefault(k * Pd + o, []).append((kd, rows))
                for kd, rows in hooks.get(t, ()):
                    _apply(w, kd, rows, ro_site)
                for t2 in range(t + 1, ro + 1):
                    w.step()
                    for kd, rows in hooks.get(t2, ()):
                        _apply(w, kd, rows, ro_site)
                tr = w.trace.cpu().numpy()
                for j, (o, kd) in enumerate(part):
                    trj = tr[:, j * M:(j + 1) * M]
                    pp = envs.per_trial(ep, trj).astype(float)[:, k]
                    s0 = trj[ep.ro_tick[:, k], np.arange(M), ep.ro_slot[:, k]].astype(np.int64)
                    pp[~ep.scored[:, k]] = np.nan
                    res[kd][o][0][:, k] = pp
                    res[kd][o][1][:, k] = s0
            if log:
                log(f"trial {k} done")
    tr = base.trace.cpu().numpy()
    normal = envs.per_trial(ep, tr).astype(float)
    normal[~ep.scored] = np.nan
    ns0 = tr[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot].astype(np.int64)
    return {"ep": ep, "normal": normal, "ns0": ns0, "res": res, "elog": base.log_arrays(), "snaps": snaps, "cue_logs": cue_logs, "cue_diff": cue_diff,
            "ro_site": ep.schedule.read_idx[:, 0].numpy().copy(), "LM": base.LM}
