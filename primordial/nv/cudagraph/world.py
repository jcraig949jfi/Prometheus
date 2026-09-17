"""U1: the B world step as torch integer ops, batched over n_envs episodes of ONE world.

Semantics are NpEncounter's (primordial/soup/b1/np_world.py, proved == wforge in B1), quirks
included: an unaffordable slot is charged 0 but its writes still land. Equality to wforge is
checked by trace and obs hash in primordial.nv.cudagraph.oracle, not inherited.

Graph-ready by construction: state tensors are updated in place, the tick is a 0-d device
tensor, and step()/observe() have no host sync and no data-dependent Python branching (every
per-env or per-tick choice is a torch.where or a ring mask). Per-world mechanics are static.

uint64 xorshift on int64: left shift and multiply wrap identically in two's complement; the
logical right shift masks the sign-extended bits; unsigned modulo splits off the sign bit.
unpaid/kicks exercise counters are not ported (not part of any hash, fitness or cell).
"""
from __future__ import annotations

import numpy as np
import torch

from primordial.soup.b1.common import M, init_regs, stream_state

I64_MAX = (1 << 63) - 1
C64 = 0x2545F4914F6CDD1D          # < 2**63, so a valid int64 scalar
_SR7_MASK = (1 << 57) - 1
MMASK = M - 1                     # M = 2**16: `u % M` == `s & MMASK` on the bit pattern
CHEATS = ("", "skip_lin", "fix_unaffordable", "no_regime_flip", "stoch_swap")


def xs_next(s: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    s = s ^ (s << 13)
    s = s ^ ((s >> 7) & _SR7_MASK)
    s = s ^ (s << 17)
    return s, s * C64


def umod(s: torch.Tensor, r: int) -> torch.Tensor:
    """(s read as uint64) % r, for a Python int 0 < r < 2**63."""
    lo = (s & I64_MAX) % r
    return torch.where(s < 0, (lo + (1 << 63) % r) % r, lo)


def u64_as_i64(a: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(a, dtype=np.uint64).view(np.int64)


class TorchWorld:
    def __init__(self, mech, world_id: str, device="cpu", cheat: str = ""):
        if cheat not in CHEATS:
            raise ValueError(f"cheat must be one of {CHEATS}")
        self.m, self.world_id, self.cheat = mech, world_id, cheat
        self.device = torch.device(device)
        self.S, self.W, self.R = mech.n_slots, mech.act_width, mech.n_regs
        self.D = len(mech.obs_perm)
        self.D1 = mech.delay + 1
        dev = self.device
        self.obs_regs = torch.tensor(list(mech.obs_regs), dtype=torch.int64, device=dev)
        self.perm = torch.tensor(list(mech.obs_perm), dtype=torch.int64, device=dev)
        self.tgts = [int(v) for v in mech.act_targets]
        self.lin = [tuple(int(v) for v in op) for op in mech.lin_ops]
        self.ring_d1 = torch.arange(self.D1, device=dev)
        self.ring_8 = torch.arange(8, device=dev)
        self.reg_ar = torch.arange(self.R, device=dev)
        self.flips = bool(mech.regime_period) and cheat != "no_regime_flip"

    def reset(self, seeds) -> torch.Tensor:
        m, dev, w = self.m, self.device, self.world_id
        seeds = np.asarray(seeds, dtype=np.int64)
        n = self.n_envs = len(seeds)
        t64 = dict(dtype=torch.int64, device=dev)
        self.regs = torch.from_numpy(init_regs(m, w, seeds)).to(dev)
        self.charge = torch.full((n, self.S), m.start_charge, **t64)
        self.alive = torch.ones((n, self.S), dtype=torch.bool, device=dev)
        self.done = torch.zeros(n, dtype=torch.bool, device=dev)
        self.done_tick = torch.full((n,), -1, **t64)
        self.tick = torch.zeros((), **t64)
        self.pend = torch.zeros((self.D1, n, self.R), **t64)
        self.hist = torch.zeros((8, n, self.R), **t64)
        st = np.array([stream_state("stoch", w, int(s)) for s in seeds], dtype=np.uint64)
        sc = np.array([[stream_state("corrupt", w, int(s), i) for i in range(self.S)] for s in seeds],
                      dtype=np.uint64).reshape(n, self.S)
        self.st_stoch = torch.from_numpy(u64_as_i64(st)).to(dev)
        self.st_corr = torch.from_numpy(u64_as_i64(sc)).to(dev)
        return self.observe()

    # ------------------------------------------------------------ observation
    def observe(self) -> torch.Tensor:
        """int64 [n_envs, n_slots, obs_dim]; advances the corruption streams like observe_all."""
        m, S, D = self.m, self.S, self.D
        src = self.regs
        if m.obs_delay:
            hrow = torch.remainder(self.tick - 1 - m.obs_delay, 8)
            h = (self.hist * (self.ring_8 == hrow)[:, None, None]).sum(0)
            src = torch.where(self.tick > m.obs_delay, h, self.regs)
        n = self.regs.shape[0]
        vals = torch.empty((n, S, D), dtype=torch.int64, device=self.device)
        vals[:, :, :D - 1] = src[:, self.obs_regs][:, None, :]
        vals[:, :, D - 1] = torch.clamp_max(torch.div(self.charge, 32, rounding_mode="floor"), 15)
        if m.corrupt_rate:
            st = self.st_corr
            for j in range(D):
                st, out = xs_next(st)
                hit = umod(out, m.corrupt_rate) == 0
                st2, out2 = xs_next(st)
                st = torch.where(hit, st2, st)
                vals[:, :, j] ^= torch.where(hit, out2 & MMASK, 0)
            self.st_corr.copy_(st)
        return vals[:, :, self.perm]

    # ------------------------------------------------------------------- step
    def step(self, actions: torch.Tensor) -> None:
        """actions: integer [n_envs, n_slots, act_width] on the device. State updates in place."""
        m, t, cheat = self.m, self.tick, self.cheat
        live = self.alive.clone()
        charge = self.charge
        # phase 1: intake
        x = torch.remainder(actions.to(torch.int64), 8)
        cost = x.sum(-1) * m.act_cost
        afford = cost <= charge
        charge.sub_(torch.where(live & afford, cost, 0))
        xw = x * live[:, :, None]
        if cheat == "fix_unaffordable":
            xw = xw * afford[:, :, None]
        add = torch.zeros_like(self.regs)
        for i, tgt in enumerate(self.tgts):
            add[:, tgt] += xw[:, :, i].sum(1) * 251
        ps = torch.remainder(t + m.delay, self.D1)
        self.pend.add_((self.ring_d1 == ps)[:, None, None] * add[None])
        # phase 2: world transition
        land_mask = (self.ring_d1 == torch.remainder(t, self.D1))[:, None, None]
        regs = torch.remainder(self.regs + (self.pend * land_mask).sum(0), M)
        self.pend.mul_(~land_mask)
        if cheat != "skip_lin":
            if self.flips:
                flip = torch.remainder(torch.div(t, m.regime_period, rounding_mode="floor"), 2).to(torch.int64)
            for dst, a, s1, b, s2, c in self.lin:
                aa = a + flip * ((M - a) % M - a) if self.flips else a
                regs[:, dst] = torch.remainder(aa * regs[:, s1] + b * regs[:, s2] + c, M)
        if m.stoch_rate:
            st, out = xs_next(self.st_stoch)
            hit = umod(out, m.stoch_rate) == 0
            st2, o2 = xs_next(st)
            st3, o3 = xs_next(st2)
            # wforge evaluates `regs[below(n_regs)] = below(M)` RHS first: draw 2 VALUE, draw 3 INDEX
            vd, xd = (o3, o2) if cheat == "stoch_swap" else (o2, o3)
            mask = hit[:, None] & (self.reg_ar[None, :] == umod(xd, self.R)[:, None])
            regs = torch.where(mask, (vd & MMASK)[:, None], regs)
            self.st_stoch.copy_(torch.where(hit, st3, st))
        self.regs.copy_(regs)
        # phase 3: economy
        v = regs[:, m.yield_reg]
        in_win = ((m.yield_lo <= v) & (v < m.yield_hi)) if m.yield_lo < m.yield_hi \
            else ((v >= m.yield_lo) | (v < m.yield_hi))
        share = m.yield_amt // torch.clamp_min(live.sum(1), 1)
        charge.sub_(m.step_cost * live)
        charge.add_((live & in_win[:, None]) * share[:, None])
        self.alive.copy_(live & (charge > 0))
        # bookkeeping
        self.hist.copy_(torch.where((self.ring_8 == torch.remainder(t, 8))[:, None, None], regs[None], self.hist))
        self.tick.add_(1)
        newly = ~self.done & ((self.tick >= m.horizon) | ~self.alive.any(1))
        self.done_tick.copy_(torch.where(newly, self.tick, self.done_tick))
        self.done.logical_or_(newly)
