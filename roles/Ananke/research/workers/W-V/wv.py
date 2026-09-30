"""W-V (T-INS-18): per-sensor carrier census. PLAN.md s1.

TagWorld: normal physics + exact per-emitter-group decomposition of the in-flight packets addressed to
the readout. Fork runner: per (trial k, offset o) tile the base state after tick t0+o, apply each arm's
swap, run to trial k's readout. Nothing in prometheus/ananke is edited.

python wv.py <spec> <M> <ns hex> <offsets comma> <tag>     spec in {4781b0a1, PMAJ, PDICT}
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
for p in (str(REPO), str(HERE.parent / "W-R"), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("WV_THREADS", "1")))
from prometheus.ananke import assays, envs, lens_swap as LS  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402
import plants_wv  # noqa: E402

OUT = HERE / "out"
K5 = 5
NOT_RUN = LS.NOT_RUN


def load(name):
    import specs as WRS                       # W-R loader (read-only import)
    ph, env, g, meta = WRS.load("4781b0a1")
    torch.set_num_threads(int(os.environ.get("WV_THREADS", "1")))
    if name == "4781b0a1":
        return ph, env, g, meta
    php = plants_wv.physics(ph)
    return php, env, plants_wv.genome(php, name), {"plant": name, "physics": "plants_wv.physics(4781b0a1)"}


# ------------------------------------------------------------------ tagging
class TagWorld(World):
    """Groups: 0..K-1 = sensor j (sense_idx[:, j]), K = every other site. Tsum [LM, B, K+1, C, P],
    Tcnt [LM, B, K+1, C]: in-flight packets addressed to the readout read_idx[:, 0], by emitter group."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        B, N, dev = self.B, self.N, self.dev
        C, P = self.ph.channels, self.ph.payload_width
        sidx = self.sch_idx
        K = sidx.shape[1]
        self.K = K
        masks = torch.zeros(K + 1, B, N, dtype=torch.bool, device=dev)
        bi = torch.arange(B, device=dev)
        for j in range(K):
            masks[j, bi, sidx[:, j]] = True
        masks[K] = ~masks[:K].any(0)
        self.gmask = masks
        self.ro = self.read_idx[:, 0]
        self.Tsum = torch.zeros(self.LM, B, K + 1, C, P, dtype=torch.int32, device=dev)
        self.Tcnt = torch.zeros(self.LM, B, K + 1, C, dtype=torch.int32, device=dev)
        self._scr = (torch.zeros_like(self.Msum), torch.zeros_like(self.Mcnt))

    def _emit(self, want, chan, pay):
        super()._emit(want, chan, pay)
        slot = self.t % self.LM
        self.Tsum[slot] = 0
        self.Tcnt[slot] = 0
        real = (self.Msum, self.Mcnt)
        st = {k: v.clone() for k, v in self.stats.items()}
        bi = torch.arange(self.B, device=self.dev)
        try:
            for g in range(self.K + 1):
                s, c = self._scr
                s.zero_()
                c.zero_()
                self.Msum, self.Mcnt = s, c
                World._emit(self, want & self.gmask[g], chan, pay)
                self.Tsum[:, :, g] += s[:, bi, self.ro]
                self.Tcnt[:, :, g] += c[:, bi, self.ro]
        finally:
            self.Msum, self.Mcnt = real
            for k, v in st.items():
                self.stats[k].copy_(v)

    def state_arrays(self):          # never tile the tags into forks
        return World.state_arrays(self)


def _tile_state(src, dst, K):
    for n, v in src.state_arrays().items():
        d = getattr(dst, n)
        if n in ("Msum", "Mcnt"):
            d.copy_(v.repeat(1, K, *([1] * (v.dim() - 2))))
        else:
            d.copy_(v.repeat(K, *([1] * (v.dim() - 1))))
    dst.t = src.t
    dst.t_dev.fill_(src.t)


def arm_list(K=K5):
    """(label, kind, set) ; kind 'tag' uses sensor set, 'fla' = W-S flight_a."""
    arms = [(f"s{j}", "tag", (j,)) for j in range(K)]
    arms += [(f"c{j}", "tag", tuple(i for i in range(K) if i != j)) for j in range(K)]
    arms += [("ALL5", "tag", tuple(range(K))), ("FLA", "fla", ())]
    return arms


def apply_arm(w, kind, gset, rows, ro, Tsum, Tcnt):
    """Swap for world rows `rows` (one block of M, aligned to mirror pairs). Tsum/Tcnt: base tags [LM,M,G,..]."""
    p = rows ^ 1
    if kind == "fla":
        for n in ("Msum", "Mcnt"):
            a = getattr(w, n)
            a[:, rows, ro] = a[:, p, ro]
        return
    if not gset:
        return
    M = len(rows)
    loc = torch.arange(M, device=w.dev)
    idx = torch.as_tensor(gset, device=w.dev)
    cs = Tsum.index_select(2, idx).sum(2)              # [LM, M, C, P]
    cc = Tcnt.index_select(2, idx).sum(2)              # [LM, M, C]
    ds = cs[:, loc ^ 1] - cs
    dc = cc[:, loc ^ 1] - cc
    w.Msum[:, rows, ro] = w.Msum[:, rows, ro] + ds.to(w.Msum.dtype)
    w.Mcnt[:, rows, ro] = w.Mcnt[:, rows, ro] + dc.to(w.Mcnt.dtype)


def run(ph, genome, env, seeds, offsets, trials, arms=None, device="cpu", log=None, max_block=16):
    """Returns dict(normal_s0 [M,nt], arm_s0 [A, O, M, nt], votes [M,nt,K], ...)."""
    arms = arms or arm_list()
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd, T = env.period(), env.T()
    nt = env.trials
    base = TagWorld(ph, np.repeat(genome[None], M, 0), ws1, device=device, ctrl=Controls(), schedule=ep.schedule)
    ro = base.ro
    at = {}
    for k in trials:
        for oi, o in enumerate(offsets):
            at.setdefault(k * Pd + o, []).append((k, oi))
    A, O = len(arms), len(offsets)
    arm_s0 = np.full((A, O, M, nt), NOT_RUN, np.int64)
    t_start = time.time()
    for t in range(T):
        base.step()
        for k, oi in at.get(t, ()):
            rt = int(ep.ro_tick[:, k].max())
            Ts, Tc = base.Tsum.clone(), base.Tcnt.clone()
            for c0 in range(0, A, max_block):
                part = arms[c0:c0 + max_block]
                Kb = len(part)
                w = World(ph, np.repeat(genome[None], M * Kb, 0), ws1 * Kb, device=device, ctrl=Controls(),
                          schedule=LS.tile_schedule(ep.schedule, Kb))
                _tile_state(base, w, Kb)
                rot = ro.repeat(1)
                for j, (_lab, kind, gset) in enumerate(part):
                    rows = torch.arange(j * M, (j + 1) * M, device=w.dev)
                    apply_arm(w, kind, gset, rows, rot, Ts, Tc)
                for _ in range(t + 1, rt + 1):
                    w.step()
                tr = w.trace.cpu().numpy()
                for j in range(Kb):
                    trj = tr[:, j * M:(j + 1) * M]
                    arm_s0[c0 + j, oi, :, k] = trj[ep.ro_tick[:, k], np.arange(M), ep.ro_slot[:, k]]
            if log:
                log(f"t{t} trial {k} o{offsets[oi]} done {time.time() - t_start:.0f}s")
    tr = base.trace.cpu().numpy()
    ns0 = tr[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot].astype(np.int64)
    sv = ep.schedule.sense_val.numpy()
    votes = np.zeros((M, nt, base.K), np.int64)
    for k in range(nt):
        votes[:, k] = np.sign(sv[k * Pd:k * Pd + env.cue_len].sum(0))
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    dm = envs.dist_matrix(ph)
    sdist = dm[ridx[:, None], sidx]
    return {"normal_s0": ns0, "arm_s0": arm_s0, "votes": votes, "y": ep.y, "scored": ep.scored,
            "sense_idx": sidx, "ro_site": ridx, "sdist": sdist, "arms": [a[0] for a in arms],
            "offsets": np.array(offsets), "trials": np.array(trials), "Pd": Pd}


def main(argv):
    name, M, ns = argv[0], int(argv[1]), int(argv[2], 16)
    offsets = [int(x) for x in argv[3].split(",")]
    tag = argv[4]
    ph, env, g, meta = load(name)
    seeds = assays.world_seeds(ns, M)
    trials = list(range(1, env.trials))
    t = time.time()
    r = run(ph, g, env, seeds, offsets, trials, log=lambda s: print(name, s, flush=True))
    wall = time.time() - t
    arms = r.pop("arms")
    np.savez_compressed(OUT / f"raw_{tag}.npz", **r)
    meta_out = {"spec": name, "meta": meta, "M": M, "ns": hex(ns), "offsets": offsets, "trials": trials,
                "arms": arms, "wall_s": wall, "threads": torch.get_num_threads(), "physics": ph.to_dict(),
                "env": env.to_dict(), "pid": os.getpid()}
    (OUT / f"meta_{tag}.json").write_text(json.dumps(meta_out, indent=1, default=str))
    print(f"{name} DONE wall {wall:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
