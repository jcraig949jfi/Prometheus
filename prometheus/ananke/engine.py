"""PTE GPU engine: batched worlds, one physics per batch (DESIGN.md s4-s6).

All state is integer. One World holds B worlds; step() advances every
world by one tick in the normative order of DESIGN.md s6.

The tick is written to be CUDA-graph capturable: no host synchronisation,
static shapes, the tick counter lives on the device (t_dev), and the
environment is a sparse schedule indexed in-graph. run() captures one
tick once and replays it; step() executes the same code eagerly. Tests
assert eager == graph digests.

Assay switches (Controls) never touch any random stream other than
their own (CTRL), so a control run differs from its twin only in the
channel it ablates.
"""
from __future__ import annotations

import dataclasses
import hashlib

import numpy as np
import torch

from . import rng
from . import topology
from .physics import Physics, REG_MAX

ACC_MAX = 2 ** 20
NOPS = 16
I32, I64 = torch.int32, torch.int64


@dataclasses.dataclass
class Controls:
    """Assay switches (all default = normal physics).

    zero_comm         no packet is ever delivered (emission still costs)
    shuffle_dest      recipient := uniform random site of the same world
    shuffle_time      delay := uniform in [1, LM-1]
    randomize_payload payload := uniform in [-REG_MAX, REG_MAX]
    freeze_routing    routing-table writes ignored
    no_adapt          routing writes, SETRULE, WIMM, site mutation off
    reset_state_at    ticks at which S := 0 (memory ablation), optionally
                      only where reset_state_mask [B, N] is True
    drop_packets_at   ticks at which the arriving mailbox slot is emptied
    distractor_chan   >= 0: every site also receives one random packet
                      per tick on this channel (irrelevant traffic)
    reset_parts       which carriers reset_state_at resets (C1b):
                      "S" (C1's only one), "inbox" (Acc_sum/Acc_cnt),
                      "Kp", "w" (to 16), "En" (to e_max), "r" (to its
                      initial rule)
    flush_inflight_at ticks at which EVERY in-flight slot (Msum/Mcnt) is
                      emptied, after that tick's emission (C1b)
    freeze_rule       SETRULE writes ignored (C1b; routing unaffected)
    """
    zero_comm: bool = False
    shuffle_dest: bool = False
    shuffle_time: bool = False
    randomize_payload: bool = False
    freeze_routing: bool = False
    no_adapt: bool = False
    reset_state_at: tuple = ()
    reset_state_mask: object = None
    drop_packets_at: tuple = ()
    distractor_chan: int = -1
    reset_parts: tuple = ("S",)
    flush_inflight_at: tuple = ()
    freeze_rule: bool = False

    def label(self) -> str:
        on = [f.name for f in dataclasses.fields(self)
              if f.name != "reset_parts" and getattr(self, f.name) not in (False, (), None, -1)]
        if self.reset_state_at and tuple(self.reset_parts) != ("S",):
            on.append("reset_parts=" + ",".join(self.reset_parts))
        return "+".join(on) if on else "none"


@dataclasses.dataclass
class Schedule:
    """Sparse environment I/O for one batch.

    sense_idx [B, K]      sites that receive SENSE (duplicates add)
    sense_val [T, B, K]   values written at each tick (0 = silent)
    read_idx  [B, A]      sites whose S0 is traced every tick
    """
    sense_idx: torch.Tensor
    sense_val: torch.Tensor
    read_idx: torch.Tensor

    @property
    def T(self) -> int:
        return self.sense_val.shape[0]


class World:
    def __init__(self, ph: Physics, genomes, world_seeds, device="cuda",
                 ctrl: Controls | None = None, schedule: Schedule | None = None,
                 census: bool = False):
        ph.validate()
        self.ph = ph
        self.dev = torch.device(device)
        self.ctrl = ctrl or Controls()
        self.census = census
        bad = set(self.ctrl.reset_parts) - {"S", "inbox", "Kp", "w", "En", "r"}
        assert not bad, bad
        g = torch.as_tensor(np.array(genomes), dtype=I64, device=self.dev)
        assert g.dim() == 4 and g.shape[1:] == (ph.rules, ph.prog_len, 5), g.shape
        self.genome = g
        B = g.shape[0]
        N, D, C, P, L = ph.n_sites, ph.state_dim, ph.channels, ph.payload_width, ph.prog_len
        self.B, self.N = B, N
        dev = self.dev
        self.ws = torch.as_tensor(np.asarray(world_seeds, dtype=np.int64), device=dev)
        assert self.ws.shape == (B,)
        self.sites = torch.arange(N, device=dev, dtype=I64)
        # pre-reduced instruction fields (DESIGN s5), [B, G, L]
        NW, NR = ph.n_write(), ph.n_read()
        self.NW, self.NR = NW, NR
        self.g_op = g[..., 0] % NOPS
        self.g_d = g[..., 1] % NW
        self.g_a = g[..., 2] % NR
        self.g_b = g[..., 3] % NR
        self.g_bf = g[..., 3]
        self.g_imm = g[..., 4]
        nbr, dist = topology.build(ph)
        if nbr is None:
            self.nbr = self.dist = None
            self.R = 0
        else:
            self.nbr = torch.as_tensor(nbr, device=dev)
            self.dist = torch.as_tensor(dist, device=dev)
            self.R = nbr.shape[1]
        self.LM = ph.lm()
        base = 1.0 - ph.loss
        surv = [int(round((base ** d if ph.loss_per_hop else base) * 65536))
                for d in range(ph.max_dist() + 1)]
        self.surv16 = torch.tensor(surv, device=dev, dtype=I64)
        self.p_wake, self.p_dup, self.p_mut = ph.p16(ph.update_p), ph.p16(ph.dup), ph.p16(ph.mut_site)
        # ---- state
        self.S = torch.zeros(B, N, D, dtype=I32, device=dev)
        self.E = torch.full((B, N), ph.e_max, dtype=I32, device=dev)
        h = rng.chain(rng.site_base(self.ws, rng.INIT, 0, self.sites), 7)
        self.r = (h % ph.rules).to(I64)
        self.r0 = self.r.clone()
        self.w = torch.full((B, N, max(self.R, 1)), 16, dtype=I32, device=dev)
        self.Kp = torch.zeros(B, N, L, dtype=I32, device=dev)
        self.Acc_sum = torch.zeros(B, N, C, P, dtype=I32, device=dev)
        self.Acc_cnt = torch.zeros(B, N, C, dtype=I32, device=dev)
        self.Msum = torch.zeros(self.LM, B, N, C, P, dtype=I32, device=dev)
        self.Mcnt = torch.zeros(self.LM, B, N, C, dtype=I32, device=dev)
        self.t_dev = torch.zeros((), dtype=I64, device=dev)
        self.t = 0
        self.stats = {k: torch.zeros(B, dtype=I64, device=dev)
                      for k in ("attempted", "delivered", "lost", "collided", "emitters",
                                "awake", "nonnop", "route_writes", "energy_spent")}
        # last-tick observables for telemetry
        self.last_emit = torch.zeros(B, N, dtype=torch.bool, device=dev)
        self.last_chan = torch.zeros(B, N, dtype=I64, device=dev)
        self.last_pay = torch.zeros(B, N, P, dtype=I32, device=dev)
        self.last_awake = torch.zeros(B, N, dtype=torch.bool, device=dev)
        # cheap continuous telemetry (in-graph accumulators; telemetry.py reads them)
        self.tel = {
            "pay_hist": torch.zeros(B, 16, dtype=I64, device=dev),     # payload0 of emissions
            "chan_hist": torch.zeros(B, C, dtype=I64, device=dev),
            "ever_emit": torch.zeros(B, N, dtype=torch.bool, device=dev),
            "s0_changes": torch.zeros(B, dtype=I64, device=dev),
            "s0_prev": torch.zeros(B, N, dtype=I32, device=dev),
            "emit_trace": torch.zeros(max(1, 1), B, dtype=I64, device=dev),
        }
        # ---- schedule
        self.set_schedule(schedule)
        # ---- control tick tables
        Tc = max([0, *self.ctrl.reset_state_at, *self.ctrl.drop_packets_at,
                  *self.ctrl.flush_inflight_at]) + 1
        self._reset_tab = torch.zeros(Tc + 1, dtype=torch.bool, device=dev)
        self._drop_tab = torch.zeros(Tc + 1, dtype=torch.bool, device=dev)
        self._flush_tab = torch.zeros(Tc + 1, dtype=torch.bool, device=dev)
        for x in self.ctrl.flush_inflight_at:
            self._flush_tab[x] = True
        for x in self.ctrl.reset_state_at:
            self._reset_tab[x] = True
        for x in self.ctrl.drop_packets_at:
            self._drop_tab[x] = True
        self._Tc = Tc
        m = self.ctrl.reset_state_mask
        self._reset_mask = (torch.ones(B, N, dtype=torch.bool, device=dev) if m is None
                            else torch.as_tensor(m, device=dev).bool())
        self._graph = None

    def set_schedule(self, sch: Schedule | None):
        dev = self.dev
        if sch is None:
            sch = Schedule(torch.zeros(self.B, 1, dtype=I64), torch.zeros(1, self.B, 1, dtype=I32),
                           torch.zeros(self.B, 1, dtype=I64))
        self.sch_idx = sch.sense_idx.to(dev, I64)
        self.sch_val = sch.sense_val.to(dev, I32)
        self.read_idx = sch.read_idx.to(dev, I64)
        self.Tsch = self.sch_val.shape[0]
        self.trace = torch.zeros(max(self.Tsch, 1), self.B, self.read_idx.shape[1], dtype=I32, device=dev)
        self.tel["emit_trace"] = torch.zeros(max(self.Tsch, 1), self.B, dtype=I64, device=dev)
        if self.census:
            for k in ("c_inflight_cnt", "c_inflight_sum", "c_inflight_sum_ro", "c_inbox_sum_ro",
                      "c_rule_changes", "c_r_ro"):
                self.tel[k] = torch.zeros(max(self.Tsch, 1), self.B, dtype=I64, device=dev)
        self._graph = None

    # ------------------------------------------------------------------ io
    def state_arrays(self) -> dict:
        out = {"S": self.S, "E": self.E, "r": self.r, "Kp": self.Kp,
               "Acc_sum": self.Acc_sum, "Acc_cnt": self.Acc_cnt,
               "Msum": self.Msum, "Mcnt": self.Mcnt}
        if self.R:
            out["w"] = self.w
        return out

    def digest(self, per_world: bool = False):
        arrs = sorted(self.state_arrays().items())
        if per_world:
            res = []
            for b in range(self.B):
                h = hashlib.sha256()
                for k, v in arrs:
                    x = v[:, b] if k in ("Msum", "Mcnt") else v[b]
                    h.update(k.encode())
                    h.update(x.to(I64).cpu().numpy().tobytes())
                res.append(h.hexdigest()[:16])
            return res
        h = hashlib.sha256()
        for k, v in arrs:
            h.update(k.encode())
            h.update(v.to(I64).cpu().numpy().tobytes())
        return h.hexdigest()[:16]

    def checkpoint(self) -> dict:
        return {"t": self.t, "ph": self.ph.to_dict(), "genome": self.genome.cpu(),
                "ws": self.ws.cpu(), "state": {k: v.cpu().clone() for k, v in self.state_arrays().items()},
                "stats": {k: v.cpu().clone() for k, v in self.stats.items()},
                "trace": self.trace.cpu().clone(),
                "tel": {k: v.cpu().clone() for k, v in self.tel.items()}}

    def restore(self, ck: dict) -> None:
        assert ck["ph"] == self.ph.to_dict()
        assert torch.equal(ck["genome"], self.genome.cpu()) and torch.equal(ck["ws"], self.ws.cpu())
        self.t = ck["t"]
        self.t_dev.fill_(ck["t"])
        for k, v in self.state_arrays().items():
            v.copy_(ck["state"][k].to(self.dev))
        for k, v in self.stats.items():
            v.copy_(ck["stats"][k].to(self.dev))
        self.trace.copy_(ck["trace"].to(self.dev))
        for k, v in self.tel.items():
            v.copy_(ck["tel"][k].to(self.dev))

    # ---------------------------------------------------------------- tick
    def _tick(self) -> None:
        ph, ctrl = self.ph, self.ctrl
        B, N, D, C, P, L = self.B, self.N, ph.state_dim, ph.channels, ph.payload_width, ph.prog_len
        dev, t = self.dev, self.t_dev
        NW, NR = self.NW, self.NR
        # 1. DELIVERY -----------------------------------------------------
        slot = torch.remainder(t, self.LM).reshape(1)
        msum = self.Msum.index_select(0, slot)[0]
        mcnt = self.Mcnt.index_select(0, slot)[0]
        if ctrl.drop_packets_at:
            keep = ~self._drop_tab.index_select(0, t.clamp(max=self._Tc).reshape(1))
            msum = msum * keep.to(I32)
            mcnt = mcnt * keep.to(I32)
        tot = mcnt.sum(-1)
        if ph.cap > 0 and ph.collision == "aloha":
            over = tot > ph.cap
            self.stats["collided"] += torch.where(over, tot, 0).sum(-1).to(I64)
            msum = msum.masked_fill(over[..., None, None], 0)
            mcnt = mcnt.masked_fill(over[..., None], 0)
        elif ph.cap > 0 and ph.collision == "saturate":
            over = tot > ph.cap
            tt = tot.clamp(min=1).to(I64)
            s2 = torch.div(msum.to(I64) * ph.cap, tt[..., None, None], rounding_mode="floor")
            c2 = torch.div(mcnt.to(I64) * ph.cap, tt[..., None], rounding_mode="floor")
            msum = torch.where(over[..., None, None], s2, msum.to(I64)).to(I32)
            mcnt = torch.where(over[..., None], c2, mcnt.to(I64)).to(I32)
        if ctrl.distractor_chan >= 0:
            msum, mcnt = self._distractor(msum, mcnt)
        self.Acc_sum.add_(msum).clamp_(-ACC_MAX, ACC_MAX)
        self.Acc_cnt.add_(mcnt).clamp_(0, ACC_MAX)
        self.Msum.index_fill_(0, slot, 0)
        self.Mcnt.index_fill_(0, slot, 0)
        # 2. ENVIRONMENT ---------------------------------------------------
        tv = t.clamp(max=self.Tsch - 1)
        vals = self.sch_val.index_select(0, tv.reshape(1))[0] * (t < self.Tsch)
        sense = torch.zeros(B, N, dtype=I32, device=dev).scatter_add_(1, self.sch_idx, vals)
        # 3. WAKE ----------------------------------------------------------
        if ph.update_mode == "sync":
            awake = (torch.remainder(t, ph.update_period) == 0).expand(B, N)
        else:
            hw = rng.chain(rng.site_base(self.ws, rng.WAKE, t, self.sites), 0)
            awake = (hw & 0xFFFF) < self.p_wake
        # 4. RUN -----------------------------------------------------------
        regs = torch.cat([
            self.S,
            torch.zeros(B, N, 8 + P, dtype=I32, device=dev),
            self.Acc_sum.clamp(-REG_MAX, REG_MAX).reshape(B, N, C * P),
            self.Acc_cnt.clamp(0, REG_MAX),
            sense.clamp(-REG_MAX, REG_MAX)[..., None],
            self.E.clamp(max=REG_MAX)[..., None],
            torch.zeros(B, N, 1, dtype=I32, device=dev),
        ], dim=-1)
        aw = awake[..., None]
        self.Acc_sum.masked_fill_(aw[..., None], 0)
        self.Acc_cnt.masked_fill_(aw, 0)
        adapt_ok = not ctrl.no_adapt
        do_rule = adapt_ok and ph.setrule and ph.rules > 1 and not ctrl.freeze_rule
        do_wimm = adapt_ok and ph.wimm
        r_next = self.r.clone()
        Kp_next = self.Kp.clone()
        nonnop = torch.zeros(B, N, dtype=I32, device=dev)
        h_rand = rng.chain(rng.site_base(self.ws, rng.RANDOP, t, self.sites)[..., None],
                           torch.arange(L, device=dev, dtype=I64))           # [B,N,L]
        if ph.rules == 1:
            F = [x[:, 0][:, None, :].expand(B, N, L)
                 for x in (self.g_op, self.g_d, self.g_a, self.g_b, self.g_bf, self.g_imm)]
        else:
            ridx = self.r[..., None].expand(B, N, L)
            F = [torch.gather(x, 1, ridx) for x in (self.g_op, self.g_d, self.g_a, self.g_b,
                                                     self.g_bf, self.g_imm)]
        f_op, f_d, f_a, f_b, f_bf, f_imm = F
        I_all = (f_imm + self.Kp.to(I64)).clamp(-REG_MAX, REG_MAX).to(I32)  # uses pre-program Kp
        sh_c = (f_bf & 7)
        sh_r = (f_bf & 15).to(I32)
        for i in range(L):
            op = f_op[..., i]
            d = f_d[..., i:i + 1]
            A = torch.gather(regs, 2, f_a[..., i:i + 1])[..., 0]
            Bv = torch.gather(regs, 2, f_b[..., i:i + 1])[..., 0]
            I = I_all[..., i]
            old = torch.gather(regs, 2, d)[..., 0]
            m = A.abs().to(I64)
            cand = torch.stack([
                old,                                                    # 0 NOP
                A,                                                      # 1 MOV
                (A + Bv).clamp(-REG_MAX, REG_MAX),                      # 2 ADD
                (A - Bv).clamp(-REG_MAX, REG_MAX),                      # 3 SUB
                ((A * Bv) >> 8).clamp(-REG_MAX, REG_MAX),               # 4 MULQ
                (A + I).clamp(-REG_MAX, REG_MAX),                       # 5 ADDI
                (I.to(I64) << sh_c[..., i]).clamp(-REG_MAX, REG_MAX).to(I32),  # 6 CONST
                (A > Bv).to(I32) * 256,                                 # 7 GT
                torch.where(old > 0, A, Bv),                            # 8 SEL
                torch.maximum(A, Bv),                                   # 9 MAX
                A >> sh_r[..., i],                                      # 10 SHR
                (A ^ Bv).clamp(-REG_MAX, REG_MAX),                      # 11 XOR
                torch.remainder(A, Bv.abs() + 1),                       # 12 MOD
                (torch.remainder(h_rand[..., i], 2 * m + 1) - m).to(I32),  # 13 RAND
                old,                                                    # 14 SETRULE
                old,                                                    # 15 WIMM
            ], dim=0)
            res = torch.gather(cand, 0, op[None])[0]
            res = torch.where(awake, res, old)
            regs.scatter_(2, d, res[..., None])
            nonnop += (awake & (op != 0)).to(I32)
            if do_rule:
                r_next = torch.where(awake & (op == 14), torch.remainder(A.to(I64), ph.rules), r_next)
            if do_wimm:
                idx = torch.remainder(A.to(I64), L)[..., None]
                cur = torch.gather(Kp_next, 2, idx)[..., 0]
                Kp_next.scatter_(2, idx, torch.where(awake & (op == 15), Bv, cur)[..., None])
        self.S.copy_(regs[..., :D])
        if self.census:
            rule_changes = (r_next != self.r).sum(-1)
        self.r.copy_(r_next)
        self.Kp.copy_(Kp_next)
        O = regs[..., D + 4: D + 8 + P]
        o_emit, o_chan, o_rport, o_rval, o_pay = O[..., 0], O[..., 1], O[..., 2], O[..., 3], O[..., 4:]
        # 5. ECONOMY -------------------------------------------------------
        want = awake & (o_emit > 0)
        copies = ph.copies()
        if ph.economy_on:
            emit_cost = ph.c_emit * copies
            want = want & (self.E >= emit_cost)
            spend = (want.to(I64) * emit_cost + awake.to(I64) * ph.c_op * nonnop.to(I64)
                     + ph.c_mem * (self.S != 0).sum(-1).to(I64))
            self.E.copy_((self.E.to(I64) + ph.e_income - spend).clamp(0, ph.e_max))
            self.stats["energy_spent"] += spend.sum(-1)
        self.stats["awake"] += awake.sum(-1)
        self.stats["nonnop"] += nonnop.sum(-1).to(I64)
        # 6. ROUTING WRITE -------------------------------------------------
        if ph.plastic_route and self.R and adapt_ok and not ctrl.freeze_routing:
            msk = awake & (o_rval != 0)
            j = torch.remainder(o_rport.to(I64), self.R)[..., None]
            cur = torch.gather(self.w, 2, j)[..., 0]
            new = (cur + (o_rval >> ph.adapt_shift)).clamp(0, 1023)
            self.w.scatter_(2, j, torch.where(msk, new, cur)[..., None])
            self.stats["route_writes"] += msk.sum(-1)
        # 7. EMISSION ------------------------------------------------------
        chan = torch.remainder(o_chan.to(I64), C)
        self.last_emit.copy_(want)
        self.last_awake.copy_(awake)
        self.last_chan.copy_(chan)
        self.last_pay.copy_(o_pay)
        self.stats["emitters"] += want.sum(-1)
        self._emit(want, chan, o_pay)
        # 8. LOCAL MUTATION ------------------------------------------------
        if self.p_mut > 0 and adapt_ok:
            hm = rng.site_base(self.ws, rng.MUT, t, self.sites)
            fire = (rng.chain(hm, 0) & 0xFFFF) < self.p_mut
            si = torch.remainder(rng.chain(hm, 1), L)[..., None]
            val = (torch.remainder(rng.chain(hm, 2), 257) - 128).to(I32)
            cur = torch.gather(self.Kp, 2, si)[..., 0]
            self.Kp.scatter_(2, si, torch.where(fire, val, cur)[..., None])
        # ablation hook (not normal physics): memory reset before decay
        if ctrl.reset_state_at:
            hit = self._reset_tab.index_select(0, t.clamp(max=self._Tc).reshape(1)) & self._reset_mask
            parts = ctrl.reset_parts
            if "S" in parts:
                self.S.masked_fill_(hit[..., None], 0)
            if "inbox" in parts:
                self.Acc_sum.masked_fill_(hit[..., None, None], 0)
                self.Acc_cnt.masked_fill_(hit[..., None], 0)
            if "Kp" in parts:
                self.Kp.masked_fill_(hit[..., None], 0)
            if "w" in parts and self.R:
                self.w.masked_fill_(hit[..., None], 16)
            if "En" in parts:
                self.E.masked_fill_(hit, ph.e_max)
            if "r" in parts:
                self.r.copy_(torch.where(hit, self.r0, self.r))
        if ctrl.flush_inflight_at:
            fl = self._flush_tab.index_select(0, t.clamp(max=self._Tc).reshape(1))
            keep = (~fl).to(I32)
            self.Msum.mul_(keep)
            self.Mcnt.mul_(keep)
        # 9. DECAY ---------------------------------------------------------
        if ph.decay_shift > 0:
            self.S.sub_(self.S >> ph.decay_shift)
        # 10. READOUT trace ------------------------------------------------
        s0 = torch.gather(self.S[..., 0], 1, self.read_idx)
        self.trace.index_copy_(0, tv.reshape(1), s0[None])
        # telemetry ---------------------------------------------------------
        tel = self.tel
        pb = ((self.last_pay[..., 0].to(I64) + 32768) >> 12).clamp(0, 15)
        tel["pay_hist"].scatter_add_(1, pb, want.to(I64))
        tel["chan_hist"].scatter_add_(1, chan, want.to(I64))
        tel["ever_emit"] |= want
        s0n = self.S[..., 0]
        tel["s0_changes"] += (s0n != tel["s0_prev"]).sum(-1)
        tel["s0_prev"].copy_(s0n)
        tel["emit_trace"].index_copy_(0, tv.reshape(1), want.sum(-1)[None].to(I64))
        if self.census:
            ro = self.read_idx[:, 0]
            bi = torch.arange(B, device=dev)
            cen = {
                "c_inflight_cnt": self.Mcnt.sum((0, 2, 3)).to(I64),
                "c_inflight_sum": self.Msum[..., 0].sum((0, 2, 3)).to(I64),
                "c_inflight_sum_ro": self.Msum[:, bi, ro, :, 0].sum((0, 2)).to(I64),
                "c_inbox_sum_ro": self.Acc_sum[bi, ro, :, 0].sum(-1).to(I64),
                "c_rule_changes": rule_changes.to(I64),
                "c_r_ro": self.r[bi, ro].to(I64),
            }
            for k, v in cen.items():
                tel[k].index_copy_(0, tv.reshape(1), v[None])
        self.t_dev.add_(1)

    def _emit(self, want, chan, pay):
        ph, ctrl = self.ph, self.ctrl
        B, N, C, P = self.B, self.N, ph.channels, ph.payload_width
        F = ph.copies()
        dev, t = self.dev, self.t_dev
        fidx = torch.arange(F, device=dev, dtype=I64)

        def draws(stream, extra=0):
            return rng.chain(rng.site_base(self.ws, stream, t, self.sites)[..., None], fidx + extra)

        if ph.topology == "global":
            h = draws(rng.ROUTE)
            rec = torch.remainder(self.sites[None, :, None] + 1 + torch.remainder(h, N - 1), N)
            dist = torch.ones_like(rec)
        elif ph.dest_mode == "all":
            rec = self.nbr[None].expand(B, N, F)
            dist = self.dist[None].expand(B, N, F)
        else:
            h = draws(rng.ROUTE)
            w = self.w.to(I64)
            W = w.sum(-1, keepdim=True)
            cs = torch.cumsum(w, -1)
            u = torch.remainder(h, W.clamp(min=1))
            j_w = (cs[:, :, None, :] <= u[..., None]).sum(-1)
            j = torch.where(W > 0, j_w, torch.remainder(h, self.R))
            rec = torch.gather(self.nbr[None].expand(B, N, self.R), 2, j)
            dist = torch.gather(self.dist[None].expand(B, N, self.R), 2, j)
        surv = self.surv16[dist]
        alive = (draws(rng.LOSS) & 0xFFFF) < surv
        delay = (ph.lat_base + ph.lat_hop * dist
                 + torch.remainder(draws(rng.LAT), ph.lat_jitter + 1)).clamp(1, self.LM - 1)
        q = pay.to(I64)[:, :, None, :].expand(B, N, F, P)
        if ph.noise > 0:
            pidx = fidx[:, None] * 16 + torch.arange(P, device=dev)[None, :]
            hn = rng.chain(rng.site_base(self.ws, rng.NOISE, t, self.sites)[..., None, None], pidx)
            q = (q + torch.remainder(hn, 2 * ph.noise + 1) - ph.noise).clamp(-REG_MAX, REG_MAX)
        if ctrl.shuffle_dest or ctrl.shuffle_time or ctrl.randomize_payload:
            hc = draws(rng.CTRL)
            if ctrl.shuffle_dest:
                rec = torch.remainder(rng.chain(hc, 1), N)
            if ctrl.shuffle_time:
                delay = 1 + torch.remainder(rng.chain(hc, 2), self.LM - 1)
            if ctrl.randomize_payload:
                hp = rng.chain(rng.chain(hc, 3)[..., None], torch.arange(P, device=dev))
                q = torch.remainder(hp, 2 * REG_MAX + 1) - REG_MAX
        isdup = (draws(rng.DUP) & 0xFFFF) < self.p_dup
        alive2 = (draws(rng.LOSS, 4096) & 0xFFFF) < surv
        delay2 = (delay + 1 + torch.remainder(draws(rng.DUP, 4096), ph.lat_jitter + 1)).clamp(1, self.LM - 1)
        em = want[..., None].expand(B, N, F)
        dup = em & isdup
        self.stats["attempted"] += em.sum((1, 2)) + dup.sum((1, 2))
        if ctrl.zero_comm:
            self.stats["lost"] += em.sum((1, 2)) + dup.sum((1, 2))
            return
        k1, k2 = em & alive, dup & alive2
        self.stats["delivered"] += k1.sum((1, 2)) + k2.sum((1, 2))
        self.stats["lost"] += (em & ~alive).sum((1, 2)) + (dup & ~alive2).sum((1, 2))
        bidx = torch.arange(B, device=dev)[:, None, None]
        cc = chan[..., None]
        base = (bidx * N + rec) * C + cc                       # [B,N,F] row within a slot
        per_slot = B * N * C
        qv = q.to(I32).reshape(-1, P)
        for keep, dl in ((k1, delay), (k2, delay2)):
            row = (torch.remainder(t + dl, self.LM) * per_slot + base).reshape(-1)
            kk = keep.reshape(-1)
            self.Msum.view(-1, P).index_add_(0, row, qv * kk[:, None].to(I32))
            self.Mcnt.view(-1).index_add_(0, row, kk.to(I32))

    def _distractor(self, msum, mcnt):
        ph = self.ph
        c = self.ctrl.distractor_chan % ph.channels
        hc = rng.site_base(self.ws, rng.CTRL, self.t_dev, self.sites)
        pidx = torch.arange(ph.payload_width, device=self.dev) + 100
        v = (torch.remainder(rng.chain(hc[..., None], pidx), 513) - 256).to(I32)
        msum = msum.clone()
        mcnt = mcnt.clone()
        msum[:, :, c, :] += v
        mcnt[:, :, c] += 1
        return msum, mcnt

    # ------------------------------------------------------------- drivers
    def step(self) -> None:
        """One eager tick."""
        self._tick()
        self.t += 1

    def run(self, T: int, graph: bool = True) -> None:
        """Advance T ticks; captures the tick as a CUDA graph on first use."""
        if not graph or self.dev.type != "cuda":
            for _ in range(T):
                self.step()
            return
        if self._graph is None:
            self._capture()
        for _ in range(T):
            self._graph.replay()
        self.t += T

    def _capture(self):
        snap = self.checkpoint()
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            for _ in range(2):
                self._tick()
        torch.cuda.current_stream().wait_stream(s)
        self.restore(snap)
        g = torch.cuda.CUDAGraph()
        with torch.cuda.graph(g):
            self._tick()
        self.restore(snap)  # capture does not execute, but be explicit
        self._graph = g
