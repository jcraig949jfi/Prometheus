"""B6: lane E's closed-loop rollout (primordial/qd/e5_run.rollout) fused into ONE numba call.

prange over envs; each env runs every tick serially:
  observe   NpEncounter.observe_all semantics: obs_delay history ring, charge bucket
            min(15, charge // 32), per-(env, slot) corruption stream (second draw adopted only
            on a hit), channel permutation. Values reach the brain as uint16 (low 16 bits),
            exactly as E5's forward casts them before taking digits.
  brain     lane C's njit row kernel genomes.tt_digits_act_row (commit 36dacd589, imported
            read-only): one genome, one obs row -> action index; stride 2 = C's skip-odd cheat
  act       lane E's codebook C[p, idx, i]
  books     E5's descriptor counters on live slots, before the step
  step      B1 world semantics (proved == wforge in B1) + the obs history ring
An env stops at its done tick: E5 keeps stepping finished envs, but their charge and
counters can no longer change, so fitness and cells are unaffected.

Nothing in primordial/brain or primordial/qd is edited.
"""
from __future__ import annotations

import numpy as np
from numba import njit, prange

from primordial.brain.genomes import tt_digits_act_row          # lane C, read-only
from primordial.soup.b1.common import M, init_regs, stream_state

C64 = np.uint64(0x2545F4914F6CDD1D)
GRID = 33                                                        # lane E's descriptor grid (E4.GRID)


@njit(inline="always")
def _xs(s):
    s ^= s << np.uint64(13)
    s ^= s >> np.uint64(7)
    s ^= s << np.uint64(17)
    return s, s * C64


@njit(parallel=True, nogil=True, boundscheck=False)
def _fused(T, R, S, W, D, delay, regime_period, stoch_rate, act_cost, step_cost, yield_reg, ylo, yhi,
           yield_amt, corrupt_rate, obs_delay, lin, tgts, obs_regs, perm,
           regs0, charge0, st_stoch0, st_corr0, genome_of_env,
           al, G, Wo, codebook, brain_stride, skip_lin,
           fit_charge, abst, mag, cnt, done_tick,
           rec_slot, log_acts, log_obs, log_idx, log_regs, log_charge, log_alive):
    n = regs0.shape[0]
    L = lin.shape[0]
    D1 = delay + 1
    r = al.shape[1]
    for e in prange(n):
        p = genome_of_env[e]
        reg = regs0[e].copy()
        charge = charge0[e].copy()
        alive = np.ones(S, dtype=np.bool_)
        pend = np.zeros((D1, R), dtype=np.int64)
        hist = np.zeros((8, R), dtype=np.int64)
        st = st_stoch0[e]
        stc = st_corr0[e].copy()
        vals = np.empty(D, dtype=np.int64)
        obs_all = np.empty((S, D), dtype=np.uint16)
        obs_row = np.empty(D, dtype=np.uint16)
        idx = np.empty(S, dtype=np.int64)
        act = np.empty((S, W), dtype=np.int64)
        v = np.empty(r, dtype=np.float32)
        u = np.empty(r, dtype=np.float32)
        k = rec_slot[e]
        tick = 0
        while True:
            # ---------------- observe at `tick`
            use_hist = obs_delay > 0 and tick > obs_delay
            hrow = (tick - 1 - obs_delay) % 8
            for s in range(S):
                for j in range(D - 1):
                    if use_hist:
                        vals[j] = hist[hrow, obs_regs[j]]
                    else:
                        vals[j] = reg[obs_regs[j]]
                q = charge[s] // 32
                vals[D - 1] = 15 if q > 15 else q
                if corrupt_rate > 0:
                    sc = stc[s]
                    for j in range(D):
                        sc, o1 = _xs(sc)
                        if o1 % np.uint64(corrupt_rate) == 0:
                            sc, o2 = _xs(sc)
                            vals[j] ^= np.int64(o2 % np.uint64(M))
                    stc[s] = sc
                for c in range(D):
                    obs_all[s, c] = np.uint16(vals[perm[c]] & 0xFFFF)
            # ---------------- brain + codebook
            for s in range(S):
                for c in range(D):
                    obs_row[c] = obs_all[s, c]
                idx[s] = tt_digits_act_row(obs_row, al[p], G[p], Wo[p], brain_stride, v, u)
                for i in range(W):
                    act[s, i] = codebook[p, idx[s], i]
            # ---------------- descriptor counters (live slots, before the step)
            for s in range(S):
                if alive[s]:
                    x = 0
                    for i in range(W):
                        x += act[s, i] % 8
                    if x == 0:
                        abst[e] += 1.0
                    mag[e] += x
                    cnt[e] += 1.0
            if k >= 0:
                for s in range(S):
                    log_idx[tick, k, s] = idx[s]
                    for c in range(D):
                        log_obs[tick, k, s, c] = obs_all[s, c]
                    for i in range(W):
                        log_acts[tick, k, s, i] = act[s, i]
            # ---------------- world step
            ps = (tick + delay) % D1
            for s in range(S):
                if alive[s]:
                    m8 = 0
                    for i in range(W):
                        m8 += act[s, i] % 8
                    cost = m8 * act_cost
                    if cost <= charge[s]:
                        charge[s] -= cost
                    for i in range(W):
                        pend[ps, tgts[i]] += (act[s, i] % 8) * 251
            land = tick % D1
            for rr in range(R):
                reg[rr] = (reg[rr] + pend[land, rr]) % M
                pend[land, rr] = 0
            if not skip_lin:
                flip = regime_period > 0 and (tick // regime_period) % 2 == 1
                for o in range(L):
                    a = lin[o, 1]
                    if flip:
                        a = (M - a) % M
                    reg[lin[o, 0]] = (a * reg[lin[o, 2]] + lin[o, 3] * reg[lin[o, 4]] + lin[o, 5]) % M
            if stoch_rate > 0:
                st, o1 = _xs(st)
                if o1 % np.uint64(stoch_rate) == 0:
                    st, o2 = _xs(st)
                    st, o3 = _xs(st)
                    reg[np.int64(o3 % np.uint64(R))] = np.int64(o2 % np.uint64(M))   # value drawn before index
            yv = reg[yield_reg]
            if ylo < yhi:
                inw = ylo <= yv and yv < yhi
            else:
                inw = yv >= ylo or yv < yhi
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
            for rr in range(R):
                hist[tick % 8, rr] = reg[rr]
            if k >= 0:
                for rr in range(R):
                    log_regs[tick, k, rr] = reg[rr]
                for s in range(S):
                    log_charge[tick, k, s] = charge[s]
                    log_alive[tick, k, s] = alive[s]
            tick += 1
            if tick >= T or not any_alive:
                break
        done_tick[e] = tick
        for s in range(S):
            if charge[s] > 0:
                fit_charge[e] += charge[s]


class FusedRollout:
    """bs: lane E's E5 BrainSpec; P genomes x the given seeds; env e = genome e // k, seed e % k."""

    def __init__(self, bs, P: int, seeds: np.ndarray):
        m = bs.mech
        self.bs, self.P, self.k = bs, P, len(seeds)
        self.seeds_env = np.tile(np.asarray(seeds, np.int64), P)
        n = P * self.k
        self.n = n
        self.regs0 = np.ascontiguousarray(init_regs(m, bs.wid, self.seeds_env), np.int64)
        self.charge0 = np.full((n, m.n_slots), m.start_charge, dtype=np.int64)
        self.st_stoch0 = np.array([stream_state("stoch", bs.wid, int(s)) for s in self.seeds_env], dtype=np.uint64)
        self.st_corr0 = np.array([[stream_state("corrupt", bs.wid, int(s), i) for i in range(m.n_slots)]
                                  for s in self.seeds_env], dtype=np.uint64).reshape(n, m.n_slots)
        self.genome_of_env = np.repeat(np.arange(P, dtype=np.int64), self.k)
        self.lin = np.array(m.lin_ops, dtype=np.int64).reshape(-1, 6)
        self.tgts = np.array(m.act_targets, dtype=np.int64)
        self.obs_regs = np.array(m.obs_regs, dtype=np.int64)
        self.perm = np.array(m.obs_perm, dtype=np.int64)
        self.D = len(m.obs_perm)

    def run(self, g, world_cheat: str = "", brain_stride: int = 1, record=None):
        m, bs, n = self.bs.mech, self.bs, self.n
        al, G, Wo, Cb = g
        al = np.ascontiguousarray(al, np.float32)
        G = np.ascontiguousarray(G, np.float32)
        Wo = np.ascontiguousarray(Wo, np.float32)
        Cb = np.ascontiguousarray(Cb, np.uint8)
        S, W, D, T, R = m.n_slots, m.act_width, self.D, m.horizon, m.n_regs
        rec = np.asarray(record if record is not None else [], np.int64)
        nr = max(1, len(rec))
        rec_slot = np.full(n, -1, np.int64)
        rec_slot[rec] = np.arange(len(rec))
        logs = dict(acts=np.zeros((T, nr, S, W), np.int64), obs=np.zeros((T, nr, S, D), np.uint16),
                    idx=np.zeros((T, nr, S), np.int64), regs=np.zeros((T, nr, R), np.int64),
                    charge=np.zeros((T, nr, S), np.int64), alive=np.zeros((T, nr, S), np.bool_))
        fit_charge = np.zeros(n, np.int64)
        abst, mag, cnt = np.zeros(n), np.zeros(n), np.zeros(n)
        done_tick = np.zeros(n, np.int64)
        _fused(T, R, S, W, D, m.delay, m.regime_period, m.stoch_rate, m.act_cost, m.step_cost, m.yield_reg,
               m.yield_lo, m.yield_hi, m.yield_amt, m.corrupt_rate, m.obs_delay, self.lin, self.tgts,
               self.obs_regs, self.perm, self.regs0, self.charge0, self.st_stoch0, self.st_corr0,
               self.genome_of_env, al, G, Wo, Cb, brain_stride, world_cheat == "skip_lin",
               fit_charge, abst, mag, cnt, done_tick,
               rec_slot, logs["acts"], logs["obs"], logs["idx"], logs["regs"], logs["charge"], logs["alive"])
        P, k = self.P, self.k
        fit = fit_charge.reshape(P, k).sum(1).astype(np.int32)
        c = cnt.reshape(P, k).sum(1)
        ab = abst.reshape(P, k).sum(1) / np.maximum(c, 1)
        mg = mag.reshape(P, k).sum(1) / np.maximum(c * bs.W * 7, 1)
        cells = (np.rint(ab * 32) * GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
        return fit, cells, done_tick, logs, rec
