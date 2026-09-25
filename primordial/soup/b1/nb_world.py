"""Form (c): Encounter semantics compiled with numba; envs in prange (independent
episodes), ticks sequential per env. Open-loop: the action tensor is an input."""
from __future__ import annotations

import numpy as np
from numba import njit, prange

from .common import M, init_regs, stream_state

C64 = np.uint64(0x2545F4914F6CDD1D)


@njit(cache=True, inline="always")
def _xs(s):
    s ^= s << np.uint64(13)
    s ^= s >> np.uint64(7)
    s ^= s << np.uint64(17)
    return s, s * C64


@njit(parallel=True, cache=True)
def run_all(lin, tgts, n_regs, horizon, regime_period, stoch_rate, delay, act_cost, step_cost,
            yield_reg, ylo, yhi, yield_amt, regs0, charge0, st0, acts, skip_lin,
            do_log, log_regs, log_charge, log_alive, done_tick):
    n, S = charge0.shape
    W = tgts.shape[0]
    L = lin.shape[0]
    D1 = delay + 1
    for e in prange(n):
        reg = regs0[e].copy()
        charge = charge0[e].copy()
        alive = np.ones(S, dtype=np.bool_)
        pend = np.zeros((D1, n_regs), dtype=np.int64)
        st = st0[e]
        T = horizon
        for t in range(horizon):
            ps = (t + delay) % D1
            for s in range(S):
                if alive[s]:
                    mag = 0
                    for i in range(W):
                        mag += acts[t, e, s, i] % 8
                    cost = mag * act_cost
                    if cost <= charge[s]:
                        charge[s] -= cost
                    for i in range(W):
                        pend[ps, tgts[i]] += (acts[t, e, s, i] % 8) * 251
            land = t % D1
            for r in range(n_regs):
                reg[r] = (reg[r] + pend[land, r]) % M
                pend[land, r] = 0
            if not skip_lin:
                flip = regime_period > 0 and (t // regime_period) % 2 == 1
                for o in range(L):
                    a = lin[o, 1]
                    if flip:
                        a = (M - a) % M
                    reg[lin[o, 0]] = (a * reg[lin[o, 2]] + lin[o, 3] * reg[lin[o, 4]] + lin[o, 5]) % M
            if stoch_rate > 0:
                st, out = _xs(st)
                if out % np.uint64(stoch_rate) == 0:
                    st, o2 = _xs(st)
                    st, o3 = _xs(st)
                    # RHS evaluates first in wforge: draw 2 = value, draw 3 = index
                    reg[np.int64(o3 % np.uint64(n_regs))] = np.int64(o2 % np.uint64(M))
            v = reg[yield_reg]
            if ylo < yhi:
                inw = ylo <= v and v < yhi
            else:
                inw = v >= ylo or v < yhi
            nl = 0
            for s in range(S):
                if alive[s]:
                    nl += 1
            share = yield_amt // nl if nl > 0 else 0
            any_alive = False
            for s in range(S):
                if alive[s]:
                    charge[s] -= step_cost
                    if inw:
                        charge[s] += share
                    if charge[s] <= 0:
                        alive[s] = False
                    else:
                        any_alive = True
            if do_log:
                log_regs[t, e] = reg
                log_charge[t, e] = charge
                log_alive[t, e] = alive
            if not any_alive:
                T = t + 1
                break
        done_tick[e] = T


class NbEncounter:
    def __init__(self, mech, world_id: str, cheat: str = ""):
        self.m, self.world_id, self.cheat = mech, world_id, cheat

    def prepare(self, seeds: np.ndarray, log: bool = False):
        m, n = self.m, len(seeds)
        self.n_envs = n
        self.regs0 = init_regs(m, self.world_id, seeds)
        self.charge0 = np.full((n, m.n_slots), m.start_charge, dtype=np.int64)
        self.st0 = np.array([stream_state("stoch", self.world_id, int(s)) for s in seeds], dtype=np.uint64)
        self.lin = np.array(m.lin_ops, dtype=np.int64).reshape(-1, 6)
        self.tgts = np.array(m.act_targets, dtype=np.int64)
        T = m.horizon
        k = n if log else 1
        self.log_regs = np.zeros((T if log else 1, k, m.n_regs), dtype=np.int64)
        self.log_charge = np.zeros((T if log else 1, k, m.n_slots), dtype=np.int64)
        self.log_alive = np.zeros((T if log else 1, k, m.n_slots), dtype=np.bool_)
        self.done_tick = np.zeros(n, dtype=np.int64)
        self.log = log

    def run(self, acts: np.ndarray):
        m = self.m
        run_all(self.lin, self.tgts, m.n_regs, m.horizon, m.regime_period, m.stoch_rate, m.delay,
                m.act_cost, m.step_cost, m.yield_reg, m.yield_lo, m.yield_hi, m.yield_amt,
                self.regs0, self.charge0, self.st0, acts, self.cheat == "skip_lin",
                self.log, self.log_regs, self.log_charge, self.log_alive, self.done_tick)

    def trace_hashes(self) -> list[bytes]:
        from .common import hash_log
        return [hash_log(self.log_regs[:, e], self.log_charge[:, e], self.log_alive[:, e],
                         int(self.done_tick[e])).encode() for e in range(self.n_envs)]
