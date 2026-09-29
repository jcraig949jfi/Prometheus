"""ARB receiver operator for PTE (W-J variant; engine.py untouched).

Aether-like arbitration: among all packets arriving at (slot, recipient,
channel), the one with the largest state-free hash priority wins and its
payload REPLACES the recipient's inbox for that channel; the count is
exposed only as presence (0/1). Priority = hash(world seed, ARB stream,
emission tick, sender, copy index) with the packet index in the low bits
(distinct within a contest). Everything else is copied from World._emit.
Install with install() to make assays/lens/search build ArbWorld.
"""
from __future__ import annotations

import torch

from prometheus.ananke import engine, rng
from prometheus.ananke.engine import World, I32, I64

ARB_STREAM = 0x5EF0


class ArbWorld(World):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.Mprio = torch.full((self.LM, self.B, self.N, self.ph.channels), -1,
                                dtype=I64, device=self.dev)

    def state_arrays(self):
        d = super().state_arrays()
        d["Mprio"] = self.Mprio
        return d

    def digest(self, per_world=False):
        # Mprio has the [LM,B,...] layout like Msum
        return super().digest(per_world) if not per_world else _digest_pw(self)

    def _tick(self):
        slot = torch.remainder(self.t_dev, self.LM).reshape(1)
        arrive = self.Mcnt.index_select(0, slot)[0] > 0            # [B,N,C]
        self.Acc_sum.masked_fill_(arrive[..., None], 0)             # replace, not add
        self.Acc_cnt.masked_fill_(arrive, 0)
        self.Mprio.index_fill_(0, slot, -1)                         # slot is delivered now
        super()._tick()

    def _emit(self, want, chan, pay):
        ph, ctrl = self.ph, self.ctrl
        B, N, C, P = self.B, self.N, ph.channels, ph.payload_width
        F = ph.copies()
        dev, t = self.dev, self.t_dev
        fidx = torch.arange(F, device=dev, dtype=I64)

        def draws(stream, extra=0):
            return rng.chain(rng.site_base(self.ws, stream, t, self.sites)[..., None], fidx + extra)

        assert ph.topology != "global" or True
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
            q = (q + torch.remainder(hn, 2 * ph.noise + 1) - ph.noise).clamp(-32767, 32767)
        assert not (ctrl.shuffle_dest or ctrl.shuffle_time or ctrl.randomize_payload)
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
        base = (bidx * N + rec) * C + chan[..., None]
        per_slot = B * N * C
        rows, keeps, prios, pays = [], [], [], []
        pk = (self.sites[None, :, None] * (2 * F) + fidx[None, None, :])     # packet id < 2^20
        hp = rng.chain(rng.site_base(self.ws, ARB_STREAM, t, self.sites)[..., None], fidx)
        for j, (keep, dl) in enumerate(((k1, delay), (k2, delay2))):
            row = (torch.remainder(t + dl, self.LM) * per_slot + base).reshape(-1)
            prio = ((rng.chain(hp, j) << 20) | (pk + j * F)).expand(B, N, F).reshape(-1)
            rows.append(row); keeps.append(keep.reshape(-1))
            prios.append(torch.where(keeps[-1], prio, torch.full_like(prio, -1)))
            pays.append(q.to(I32).reshape(-1, P))
        row, kk, pr, qv = (torch.cat(rows), torch.cat(keeps), torch.cat(prios), torch.cat(pays))
        mp = self.Mprio.view(-1)
        mp.scatter_reduce_(0, row, pr, reduce="amax", include_self=True)
        win = kk & (pr == mp.index_select(0, row))                   # unique per row
        fl = torch.zeros(mp.numel(), dtype=I32, device=dev)
        fl.scatter_reduce_(0, row, win.to(I32), reduce="amax", include_self=True)
        ms = self.Msum.view(-1, P)
        ms.mul_((1 - fl)[:, None])                                   # a new winner replaces
        ms.index_add_(0, row, qv * win[:, None].to(I32))
        self.Mcnt.view(-1).scatter_reduce_(0, row, kk.to(I32), reduce="amax", include_self=True)

def _digest_pw(w):
    import hashlib
    res = []
    arrs = sorted(w.state_arrays().items())
    for b in range(w.B):
        h = hashlib.sha256()
        for k, v in arrs:
            x = v[:, b] if k in ("Msum", "Mcnt", "Mprio") else v[b]
            h.update(k.encode()); h.update(x.to(I64).cpu().numpy().tobytes())
        res.append(h.hexdigest()[:16])
    return res


def install(on: bool):
    """Point every module that builds a World at ArbWorld (or back)."""
    from prometheus.ananke import assays, lens
    cls = ArbWorld if on else engine.World
    assays.World = cls
    lens.World = cls
