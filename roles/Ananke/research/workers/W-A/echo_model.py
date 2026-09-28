"""W-A reduced model of the M2 HOLD mechanism: a two-hop ECHO particle model.

Derived from the decompiled programs (decompile.py) and the PTE physics
(engine._tick/_emit), NOT fitted to any measured accuracy curve.

Reduced program (all 4 champions, see PLAN.md s2):
  actuator a (the only site with SENSE != 0) emits its SENSE on component c
  every site relays v = f(IN_c)  (sum of c received since its last wake) on c'
  S0 := IN_c'  (sum of c' received since the last wake; OVERWRITTEN every wake)
  everyone emits every wake, fanout copies, no recirculation (c' is never relayed).

Physics that enter: ring offsets and hop distances, routing weights,
fanout, loss, delay = clamp(lat_base + lat_hop*h + U{0..jitter}, 1, LM-1),
sync wake every update_period ticks (SENSE only seen on a wake tick;
arrivals are read at the first wake >= arrival tick), cap/saturate
(optional, background traffic approximated as Poisson).

Knobs describing a program:
  shift     : relay scale, v = IN >> shift (floor), 0 = identity
  route     : "uniform" or "specimen" (every site's table index 2, i.e.
              offset -1, decays 16 -> 0 by one per wake: RVAL = -1 each wake)
  pipeline  : extra wakes between echo arrival and S0 (S0 := S1; S1 := echo)
"""
from __future__ import annotations

import dataclasses
import math

import numpy as np

from prometheus.ananke import envs
from prometheus.ananke.physics import Physics


@dataclasses.dataclass(frozen=True)
class Prog:
    shift: int = 0
    route: str = "uniform"
    pipeline: int = 0


PROGS = {
    "4ab2ba01": Prog(shift=0, route="specimen"),
    "fresh1": Prog(shift=4, route="uniform"),
    "fresh2": Prog(shift=2, route="uniform"),
    "fresh3": Prog(shift=0, route="uniform"),
}


def _sense(env: envs.EnvSpec, nw: int, g) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """[nw, T] actuator sense values, readout ticks [trials], targets [nw, trials]."""
    T, Pd = env.T(), env.period()
    x = np.zeros((nw, T), dtype=np.int64)
    y = np.where(g.random((nw, env.trials)) < 0.5, 1, -1)
    ro = np.zeros(env.trials, dtype=np.int64)
    for k in range(env.trials):
        t0 = k * Pd
        x[:, t0:t0 + env.cue_len] = env.amp * y[:, k:k + 1]
        ds = np.where(g.random((nw, env.gap)) < 0.5, 1, -1)
        x[:, t0 + env.cue_len:t0 + env.cue_len + env.gap] = env.amp_dist * ds
        ro[k] = t0 + env.cue_len + env.gap
    return x, ro, y


def _ceil_wake(t, P):
    return ((t + P - 1) // P) * P


def predict(ph: Physics, env: envs.EnvSpec, prog: Prog, nw: int = 4000, seed: int = 0,
            sat: bool = True, return_kernel: bool = False):
    assert ph.topology == "ring" and ph.update_mode == "sync" and ph.dest_mode == "sample"
    g = np.random.default_rng(seed)
    P = ph.update_period
    offs = np.array(list(range(-ph.radius, 0)) + list(range(1, ph.radius + 1)))
    R = len(offs)
    hop = np.abs(offs)
    back = np.array([int(np.flatnonzero(offs == -o)[0]) for o in offs])   # index of a in n's table
    LM = ph.lm()
    F = ph.fanout
    T = env.T()
    pad = 4 * (LM + P) + 4
    TT = T + pad
    x, ro, y = _sense(env, nw, g)
    wake = np.arange(TT) % P == 0

    def weights(t):
        """routing weights of every site's table at wake t (same for all sites)."""
        w = np.full(R, 16.0)
        if prog.route == "specimen":
            k = t // P
            w[(-7168) % R] = max(0, 15 - k)
        return w / w.sum()

    def delay(h, size):
        j = g.integers(0, ph.lat_jitter + 1, size=size)
        return np.clip(ph.lat_base + ph.lat_hop * h + j, 1, LM - 1)

    surv = (1.0 - ph.loss)
    # expected packet arrivals per site per tick (for saturation), by tick phase
    lam = np.zeros(TT)
    if sat and ph.cap > 0:
        for t in range(TT):
            s = 0.0
            for te in range(max(0, t - LM), t):
                if not wake[te]:
                    continue
                p = weights(te)
                for i in range(R):          # each neighbour of the receiver sends F copies
                    h = hop[i]
                    for jj in range(ph.lat_jitter + 1):
                        d = min(max(ph.lat_base + ph.lat_hop * h + jj, 1), LM - 1)
                        if te + d == t:
                            s += F * surv * p[back[i]] / (ph.lat_jitter + 1)
            lam[t] = s * (R - 1) / R

    def saturate(vals, cnt, t_arr):
        """vals, cnt: [nw, K, TT] sums and signal-copy counts per (site, arrival tick)."""
        if not (sat and ph.cap > 0):
            return vals
        tot = cnt + g.poisson(lam[None, None, :], size=cnt.shape)
        over = tot > ph.cap
        scaled = np.floor_divide(vals * ph.cap, np.maximum(tot, 1))
        return np.where(over, scaled, vals)

    # ---- stage 1: actuator -> neighbours (per neighbour index i, per arrival tick)
    V1 = np.zeros((nw, R, TT), dtype=np.int64)
    C1 = np.zeros((nw, R, TT), dtype=np.int64)
    for te in range(T):
        if not wake[te]:
            continue
        xv = x[:, te]
        if not np.any(xv):
            continue
        p = weights(te)
        i = g.choice(R, size=(nw, F), p=p)
        alive = g.random((nw, F)) < surv
        d = delay(hop[i], (nw, F))
        ta = te + d
        for f in range(F):
            m = alive[:, f]
            np.add.at(V1, (np.flatnonzero(m), i[m, f], ta[m, f]), xv[m])
            np.add.at(C1, (np.flatnonzero(m), i[m, f], ta[m, f]), 1)
    V1 = saturate(V1, C1, None)
    # accumulate into the neighbour's inbox until its next wake
    W1 = np.zeros_like(V1)
    for t in range(TT):
        tw = min(_ceil_wake(t, P), TT - 1)
        W1[:, :, tw] += V1[:, :, t]
    IN1 = np.clip(W1, -32767, 32767)
    # ---- stage 2: relay neighbours -> actuator
    V2 = np.zeros((nw, TT), dtype=np.int64)
    C2 = np.zeros((nw, TT), dtype=np.int64)
    for t in range(TT):
        if not wake[t]:
            continue
        v = IN1[:, :, t] >> prog.shift if prog.shift else IN1[:, :, t]
        if not np.any(v):
            continue
        p = weights(t)
        for i in range(R):
            vi = v[:, i]
            nz = vi != 0
            if not nz.any():
                continue
            k = g.binomial(F, p[back[i]], size=nw)                  # copies addressed to a
            k = g.binomial(k, surv)
            for c in range(k.max()):
                m = nz & (k > c)
                d = delay(np.full(m.sum(), hop[i]), m.sum())
                ta = np.minimum(t + d, TT - 1)
                rows = np.flatnonzero(m)
                np.add.at(V2, (rows, ta), vi[m])
                np.add.at(C2, (rows, ta), 1)
    V2 = saturate(V2[:, None, :], C2[:, None, :], None)[:, 0]
    ECHO = np.zeros_like(V2)
    for t in range(TT):
        tw = min(_ceil_wake(t, P), TT - 1)
        ECHO[:, tw] += V2[:, t]
    ECHO = np.clip(ECHO, -32767, 32767)
    # S0 at wake W = echo read pipeline wakes earlier; readout = last wake <= ro
    S0 = np.zeros((nw, TT), dtype=np.int64)
    cur = np.zeros(nw, dtype=np.int64)
    hist = []
    for t in range(TT):
        if wake[t]:
            hist.append(ECHO[:, t])
            cur = hist[-1 - prog.pipeline] if len(hist) > prog.pipeline else np.zeros(nw, dtype=np.int64)
        S0[:, t] = cur
    s = S0[:, ro]
    corr = np.where(s == 0, 0.5, (np.sign(s) == y).astype(float))
    acc = float(corr.mean())
    if return_kernel:
        return acc, kernel(ph, prog)
    return acc


def kernel(ph: Physics, prog: Prog, t_emit: int = 1000) -> dict:
    """Expected echo weight (copies returning, per unit payload) vs round-trip
    lag in ticks, from an emission at a wake (late, so routing has settled)."""
    P = ph.update_period
    offs = np.array(list(range(-ph.radius, 0)) + list(range(1, ph.radius + 1)))
    R = len(offs)
    back = [int(np.flatnonzero(offs == -o)[0]) for o in offs]
    w = np.full(R, 16.0)
    if prog.route == "specimen":
        w[(-7168) % R] = 0
    p = w / w.sum()
    LM, F, s = ph.lm(), ph.fanout, 1 - ph.loss
    J = ph.lat_jitter + 1
    K = {}
    for i, o in enumerate(offs):
        h = abs(o)
        for j1 in range(J):
            d1 = min(max(ph.lat_base + ph.lat_hop * h + j1, 1), LM - 1)
            W1 = _ceil_wake(d1, P)
            for j2 in range(J):
                d2 = min(max(ph.lat_base + ph.lat_hop * h + j2, 1), LM - 1)
                W2 = _ceil_wake(W1 + d2, P) + prog.pipeline * P
                K[W2] = K.get(W2, 0.0) + F * s * p[i] * F * s * p[back[i]] / (J * J)
    return dict(sorted(K.items()))
