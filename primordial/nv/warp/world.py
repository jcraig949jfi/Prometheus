"""N3: lane B's world step (B1 semantics, proved == wforge in B1) as one Warp kernel, CPU or CUDA.

Semantics are primordial/soup/b1/nb_world.run_all line for line (read-only; not imported so the
kernel stays numba-free). One launch advances every env over ticks [t0, t1); state lives in
device arrays, so run(t, t + 1) is one world tick and run(0, horizon) is the whole episode.
An env whose slots are all dead gets done_tick = t + 1 and is skipped from then on.

Assumes every operand of % is non-negative (Warp % truncates; numba and wforge floor). True for
wforge worlds: registers in [0, M), coefficients >= 0, actions >= 0.
"""
from __future__ import annotations

import numpy as np
import warp as wp

from primordial.soup.b1.common import hash_log, init_regs, stream_state   # lane B, read-only

wp.config.quiet = True


@wp.kernel
def world_ticks(lin: wp.array2d(dtype=wp.int64), tgts: wp.array(dtype=wp.int64),
                acts: wp.array4d(dtype=wp.int32),
                reg: wp.array2d(dtype=wp.int64), charge: wp.array2d(dtype=wp.int64),
                alive: wp.array2d(dtype=wp.int32), pend: wp.array3d(dtype=wp.int64),
                st: wp.array(dtype=wp.uint64), done_tick: wp.array(dtype=wp.int64),
                rec_slot: wp.array(dtype=wp.int64), log_regs: wp.array3d(dtype=wp.int64),
                log_charge: wp.array3d(dtype=wp.int64), log_alive: wp.array3d(dtype=wp.int32),
                t0: wp.int32, t1: wp.int32, horizon: wp.int64, regime_period: wp.int64,
                stoch_rate: wp.int64, delay: wp.int64, act_cost: wp.int64, step_cost: wp.int64,
                yield_reg: wp.int64, ylo: wp.int64, yhi: wp.int64, yield_amt: wp.int64,
                skip_lin: wp.int32):
    e = wp.tid()
    Mm = wp.int64(65536)
    R = reg.shape[1]
    S = charge.shape[1]
    W = tgts.shape[0]
    L = lin.shape[0]
    D1 = delay + wp.int64(1)
    k = rec_slot[e]
    C64 = wp.uint64(0x2545F4914F6CDD1D)
    for ti in range(t0, t1):
        t = wp.int64(ti)
        if done_tick[e] == wp.int64(0):
            ps = (t + delay) % D1
            for s in range(S):
                if alive[e, s] != 0:
                    mag = wp.int64(0)
                    for i in range(W):
                        mag += wp.int64(acts[t, e, s, i] % 8)
                    cost = mag * act_cost
                    if cost <= charge[e, s]:
                        charge[e, s] = charge[e, s] - cost
                    for i in range(W):
                        pend[e, ps, tgts[i]] = pend[e, ps, tgts[i]] + wp.int64(acts[t, e, s, i] % 8) * wp.int64(251)
            land = t % D1
            for r in range(R):
                reg[e, r] = (reg[e, r] + pend[e, land, r]) % Mm
                pend[e, land, r] = wp.int64(0)
            if skip_lin == 0:
                flip = bool(False)
                if regime_period > wp.int64(0):
                    if (t // regime_period) % wp.int64(2) == wp.int64(1):
                        flip = True
                for o in range(L):
                    a = lin[o, 1]
                    if flip:
                        a = (Mm - a) % Mm
                    reg[e, lin[o, 0]] = (a * reg[e, lin[o, 2]] + lin[o, 3] * reg[e, lin[o, 4]] + lin[o, 5]) % Mm
            if stoch_rate > wp.int64(0):
                x = st[e]
                x = x ^ (x << wp.uint64(13))
                x = x ^ (x >> wp.uint64(7))
                x = x ^ (x << wp.uint64(17))
                if (x * C64) % wp.uint64(stoch_rate) == wp.uint64(0):
                    x = x ^ (x << wp.uint64(13))
                    x = x ^ (x >> wp.uint64(7))
                    x = x ^ (x << wp.uint64(17))
                    o2 = x * C64
                    x = x ^ (x << wp.uint64(13))
                    x = x ^ (x >> wp.uint64(7))
                    x = x ^ (x << wp.uint64(17))
                    o3 = x * C64
                    # RHS evaluates first in wforge: draw 2 = value, draw 3 = index
                    reg[e, wp.int64(o3 % wp.uint64(R))] = wp.int64(o2 % wp.uint64(65536))
                st[e] = x
            v = reg[e, yield_reg]
            inw = bool(False)
            if ylo < yhi:
                if ylo <= v:
                    if v < yhi:
                        inw = True
            else:
                if v >= ylo:
                    inw = True
                if v < yhi:
                    inw = True
            nl = wp.int64(0)
            for s in range(S):
                if alive[e, s] != 0:
                    nl += wp.int64(1)
            share = wp.int64(0)
            if nl > wp.int64(0):
                share = yield_amt // nl
            any_alive = bool(False)
            for s in range(S):
                if alive[e, s] != 0:
                    c = charge[e, s] - step_cost
                    if inw:
                        c = c + share
                    charge[e, s] = c
                    if c <= wp.int64(0):
                        alive[e, s] = 0
                    else:
                        any_alive = True
            if k >= wp.int64(0):
                for r in range(R):
                    log_regs[t, k, r] = reg[e, r]
                for s in range(S):
                    log_charge[t, k, s] = charge[e, s]
                    log_alive[t, k, s] = alive[e, s]
            if not any_alive:
                done_tick[e] = t + wp.int64(1)
            elif t + wp.int64(1) >= horizon:
                done_tick[e] = horizon


class WpEncounter:
    """NbEncounter's interface (prepare / run / trace_hashes) on a Warp device.
    record: env indices whose post-step state is logged (for trace hashes); None = all when log."""

    def __init__(self, mech, world_id: str, cheat: str = "", device: str = "cpu"):
        self.m, self.world_id, self.cheat, self.device = mech, world_id, cheat, device

    def prepare(self, seeds: np.ndarray, log: bool = False, record=None):
        m, n, dev = self.m, len(seeds), self.device
        self.n_envs = n
        rec = np.arange(n) if (log and record is None) else np.asarray(record if record is not None else [], np.int64)
        self.record = rec
        rec_slot = np.full(n, -1, np.int64)
        rec_slot[rec] = np.arange(len(rec))
        T, nr = m.horizon, max(1, len(rec))
        arr = lambda x, dt: wp.array(np.ascontiguousarray(x), dtype=dt, device=dev)
        self._reg0 = np.ascontiguousarray(init_regs(m, self.world_id, seeds), np.int64)
        self._st0 = np.array([stream_state("stoch", self.world_id, int(s)) for s in seeds], np.uint64)
        self.reg = arr(self._reg0, wp.int64)
        self.charge = arr(np.full((n, m.n_slots), m.start_charge, np.int64), wp.int64)
        self.alive = arr(np.ones((n, m.n_slots), np.int32), wp.int32)
        self.pend = wp.zeros((n, m.delay + 1, m.n_regs), dtype=wp.int64, device=dev)
        self.st = arr(self._st0, wp.uint64)
        self.done_tick = wp.zeros(n, dtype=wp.int64, device=dev)
        self.rec_slot = arr(rec_slot, wp.int64)
        self.lin = arr(np.array(m.lin_ops, np.int64).reshape(-1, 6), wp.int64)
        self.tgts = arr(np.array(m.act_targets, np.int64), wp.int64)
        Tl = T if len(rec) else 1
        self.log_regs = wp.zeros((Tl, nr, m.n_regs), dtype=wp.int64, device=dev)
        self.log_charge = wp.zeros((Tl, nr, m.n_slots), dtype=wp.int64, device=dev)
        self.log_alive = wp.zeros((Tl, nr, m.n_slots), dtype=wp.int32, device=dev)
        self.acts = None

    def reset(self):
        """Back to tick 0 from the host initial state kept by prepare (no stream re-seeding)."""
        self.reg.assign(self._reg0)
        self.charge.fill_(self.m.start_charge)
        self.alive.fill_(1)
        self.pend.zero_()
        self.st.assign(self._st0)
        self.done_tick.zero_()
        wp.synchronize_device(self.device)

    def load_actions(self, acts: np.ndarray):
        """acts int32 [T, n_envs, n_slots, act_width], values >= 0; copied to the device once."""
        self.acts = wp.array(np.ascontiguousarray(acts, np.int32), dtype=wp.int32, device=self.device)

    def run(self, acts: np.ndarray | None = None, t0: int = 0, t1: int | None = None, sync: bool = True):
        if acts is not None:
            self.load_actions(acts)
        m = self.m
        t1 = m.horizon if t1 is None else t1
        wp.launch(world_ticks, dim=self.n_envs, device=self.device, inputs=[
            self.lin, self.tgts, self.acts, self.reg, self.charge, self.alive, self.pend, self.st,
            self.done_tick, self.rec_slot, self.log_regs, self.log_charge, self.log_alive,
            t0, t1, m.horizon, m.regime_period, m.stoch_rate, m.delay, m.act_cost, m.step_cost,
            m.yield_reg, m.yield_lo, m.yield_hi, m.yield_amt, int(self.cheat == "skip_lin")])
        if sync:
            wp.synchronize_device(self.device)

    def step(self, t: int):
        """One world tick for every env."""
        self.run(None, t, t + 1)

    def final_charge(self) -> np.ndarray:
        return self.charge.numpy()

    def trace_hashes(self) -> list[bytes]:
        R, C, A, dt = self.log_regs.numpy(), self.log_charge.numpy(), self.log_alive.numpy(), self.done_tick.numpy()
        return [hash_log(R[:, j], C[:, j], A[:, j], int(dt[e])).encode() for j, e in enumerate(self.record)]
