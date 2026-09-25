"""Form (b): Encounter semantics batched over n_envs episodes of ONE world, numpy.

Loops run over lin_ops / action channels / obs channels (all <= 13), never over envs.
Semantics copied from wforge world.py including its quirks, e.g. a slot that cannot
afford its action is charged 0 but its writes STILL land (phase 1 appends pending
writes regardless of the forced abstain).
"""
from __future__ import annotations

import numpy as np

from .common import M, init_regs, stream_state

_C = np.uint64(0x2545F4914F6CDD1D)
_S13, _S7, _S17 = np.uint64(13), np.uint64(7), np.uint64(17)


def xs_next(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    s = s ^ (s << _S13)
    s = s ^ (s >> _S7)
    s = s ^ (s << _S17)
    return s, s * _C


class NpEncounter:
    """Contract World over n_envs episodes. cheat='skip_lin' drops the transition ops."""

    def __init__(self, mech, world_id: str, record: np.ndarray | None = None, cheat: str = "",
                 with_obs: bool = True):
        self.m, self.world_id, self.cheat = mech, world_id, cheat
        self.n_slots, self.act_dim = mech.n_slots, mech.act_width
        self.obs_dim = len(mech.obs_perm)
        self.record = record          # env indices whose state is logged, or None
        self.with_obs = with_obs

    def reset(self, seeds: np.ndarray) -> np.ndarray:
        m, n = self.m, len(seeds)
        self.n_envs = n
        self.regs = init_regs(m, self.world_id, seeds)
        self.charge = np.full((n, m.n_slots), m.start_charge, dtype=np.int64)
        self.alive = np.ones((n, m.n_slots), dtype=bool)
        self.done = np.zeros(n, dtype=bool)
        self.done_tick = np.full(n, -1, dtype=np.int64)
        self.tick = 0
        self.unpaid = np.zeros(n, dtype=np.int64)
        self.kicks = np.zeros(n, dtype=np.int64)
        self.pend =np.zeros((m.delay + 1, n, m.n_regs), dtype=np.int64)
        self.hist = np.zeros((8, n, m.n_regs), dtype=np.int64)
        w = self.world_id
        self.st_stoch = np.array([stream_state("stoch", w, int(s)) for s in seeds], dtype=np.uint64)
        self.st_corr = np.array([[stream_state("corrupt", w, int(s), i) for i in range(m.n_slots)]
                                 for s in seeds], dtype=np.uint64).reshape(n, m.n_slots)
        self.obs_regs = np.array(m.obs_regs, dtype=np.int64)
        self.perm = np.array(m.obs_perm, dtype=np.int64)
        self.act_targets = list(m.act_targets)
        self.lin = [tuple(int(v) for v in op) for op in m.lin_ops]
        if self.record is not None:
            k, T = len(self.record), m.horizon
            self.log_regs = np.zeros((T, k, m.n_regs), dtype=np.int64)
            self.log_charge = np.zeros((T, k, m.n_slots), dtype=np.int64)
            self.log_alive = np.zeros((T, k, m.n_slots), dtype=bool)
        return self.observe_all() if self.with_obs else None

    # ------------------------------------------------------------ observation
    def observe_all(self) -> np.ndarray:
        """int64 [n_envs, n_slots, obs_dim] (reference values; contract dtype is uint16)."""
        m = self.m
        src = self.regs
        if m.obs_delay and self.tick > m.obs_delay:
            src = self.hist[(self.tick - 1 - m.obs_delay) % 8]
        n, S, D = self.n_envs, m.n_slots, self.obs_dim
        vals = np.empty((n, S, D), dtype=np.int64)
        vals[:, :, :D - 1] = src[:, self.obs_regs][:, None, :]
        vals[:, :, D - 1] = np.minimum(15, self.charge // 32)
        if m.corrupt_rate:
            st = self.st_corr
            rate = np.uint64(m.corrupt_rate)
            for j in range(D):
                st, out = xs_next(st)
                hit = (out % rate) == 0
                st2, out2 = xs_next(st)
                st = np.where(hit, st2, st)
                vals[:, :, j] ^= np.where(hit, (out2 % np.uint64(M)).astype(np.int64), 0)
            self.st_corr = st
        return vals[:, :, self.perm]

    # ------------------------------------------------------------------- step
    def step(self, actions: np.ndarray):
        m, t = self.m, self.tick
        live = self.alive
        # phase 1: intake
        x = actions.astype(np.int64) % 8                       # [n,S,W]
        cost = x.sum(-1) * m.act_cost
        afford = cost <= self.charge
        self.unpaid += (live & ~afford & (cost > 0)).any(1) & ~self.done   # exercise counter, in-episode only
        self.charge -= np.where(live & afford, cost, 0)
        slot = self.pend[(t + m.delay) % (m.delay + 1)]
        xw = x * live[:, :, None]
        if self.cheat == "fix_unaffordable":        # one-semantic cheat: unpaid writes dropped
            xw = xw * afford[:, :, None]
        for i, tgt in enumerate(self.act_targets):
            slot[:, tgt] += xw[:, :, i].sum(1) * 251
        # phase 2: world transition
        land = t % (m.delay + 1)
        self.regs += self.pend[land]
        self.regs %= M
        self.pend[land] = 0
        regs = self.regs
        if self.cheat != "skip_lin":
            flip = bool(m.regime_period) and (t // m.regime_period) % 2 == 1 \
                and self.cheat != "no_regime_flip"
            for dst, a, s1, b, s2, c in self.lin:
                aa = (M - a) % M if flip else a
                regs[:, dst] = (aa * regs[:, s1] + b * regs[:, s2] + c) % M
        if m.stoch_rate:
            st, out = xs_next(self.st_stoch)
            hit = (out % np.uint64(m.stoch_rate)) == 0
            if hit.any():
                st2, o2 = xs_next(st)
                st3, o3 = xs_next(st2)
                idx = np.nonzero(hit)[0]
                self.kicks += hit & ~self.done
                # wforge: `regs[below(n_regs)] = below(M)` evaluates the RHS first,
                # so draw 2 is the VALUE and draw 3 the INDEX
                vd, xd = (o3, o2) if self.cheat == "stoch_swap" else (o2, o3)
                regs[idx, (xd[idx] % np.uint64(m.n_regs)).astype(np.int64)] = \
                    (vd[idx] % np.uint64(M)).astype(np.int64)
                st = np.where(hit, st3, st)
            self.st_stoch = st
        # phase 3: economy
        v = regs[:, m.yield_reg]
        in_win = ((m.yield_lo <= v) & (v < m.yield_hi)) if m.yield_lo < m.yield_hi \
            else ((v >= m.yield_lo) | (v < m.yield_hi))
        nwin = live.sum(1)
        share = m.yield_amt // np.maximum(nwin, 1)
        self.charge -= m.step_cost * live
        self.charge += (live & in_win[:, None]) * share[:, None]
        self.alive = live & (self.charge > 0)
        # bookkeeping
        if self.with_obs:
            self.hist[t % 8] = regs
        if self.record is not None:
            r = self.record
            self.log_regs[t], self.log_charge[t], self.log_alive[t] = regs[r], self.charge[r], self.alive[r]
        self.tick = t + 1
        newly = ~self.done & ((self.tick >= m.horizon) | ~self.alive.any(1))
        self.done_tick[newly] = self.tick
        self.done |= newly
        return (self.observe_all() if self.with_obs else None), self.charge, self.done

    def trace_hashes(self) -> list[bytes]:
        from .common import hash_log
        out = []
        for k, e in enumerate(self.record):
            T = int(self.done_tick[e])
            out.append(hash_log(self.log_regs[:, k], self.log_charge[:, k], self.log_alive[:, k], T).encode())
        return out
