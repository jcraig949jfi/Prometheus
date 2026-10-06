"""AIM02 POST-HOC probe (NOT preregistered; descriptive; does not enter the disposition).

Localizes AIM02's measured failure mode -- changing non-AIM site-fields hold ~2 values -- before the next physics is
designed. For each target (site, field in opcode/arg1/payload) on the AIM02 sample grid, over the final OBS ticks:
  held     distinct values the target holds
  offered  distinct values carried by WINNING writes into it (from the frozen kernel's observer: winner slot ->
           source payload; energy-field transfers excluded since energy is not in the channel)
  writers  distinct winning source positions (slots)
If offered ~ held ~ 2 while writers > 2, the bound is upstream: the rotating writers that reach a target carry
(nearly) the same payloads, so retargeting cannot raise the repertoire.

    python posthoc_offer_probe.py --cond L1D50 --seed 0 --out production/posthoc_offer_L1D50_s0.json
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aim02_run as B  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--ticks", type=int, default=3000)
    ap.add_argument("--obs", type=int, default=500)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    xp, K = B.load_backend("gpu")
    law, dens, en = B.CONDS[a.cond]
    energy = B.ENERGIES[en]
    fields, _ = R.build_initial(R.SPARSE_SOUP, a.n, a.n, B.RNG_SEED_BASE + a.seed, write_density=dens,
                                energy_mode=R.ENERGY_UNIFORM)
    s = [xp.asarray(f) for f in fields]
    phys = B.PHYS_SEED_BASE + a.seed
    n = a.n
    held, offv, offw = {f: [] for f in (0, 2, 3)}, {f: [] for f in (0, 2, 3)}, {f: [] for f in (0, 2, 3)}
    for t in range(a.ticks):
        obs = []
        out = K.gpu_step(n, n, phys, t + 1, energy["write_cost"], energy["maintenance_cost"],
                         energy["replenish_numer"], energy["replenish_amount"], 0, *s, observer=obs)
        nxt = list(out[:5])
        if law == "L1":
            won = xp.zeros((n, n), dtype=bool)
            for f in range(5):
                for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
                    won |= xp.roll(obs[f][0] == sl, (dr, dc), axis=(0, 1))
            reaim = won & ~(obs[1][0] != 255)
            nxt[1] = xp.where(reaim, (nxt[1].astype(xp.uint16) + 1).astype(xp.uint8), nxt[1])
        if t >= a.ticks - a.obs:
            for f in (0, 2, 3):
                slot = obs[f][0]
                # payload offered by the winning source in each slot
                pay = xp.full((n, n), -1, dtype=xp.int16)
                for sl, (dr, dc, _q) in enumerate(K._NEIGHBOR_SLOTS):
                    srcpay = xp.roll(s[3], (-dr, -dc), axis=(0, 1)).astype(xp.int16)
                    pay = xp.where(slot == sl, srcpay, pay)
                held[f].append(nxt[f][::2, ::2])
                offv[f].append(pay[::2, ::2])
                offw[f].append(xp.where(slot == 255, -1, slot.astype(xp.int16))[::2, ::2])
        s = nxt
    res = {"cond": a.cond, "seed": a.seed, "n": n, "ticks": a.ticks, "obs": a.obs, "posthoc": True, "fields": {}}
    for f in (0, 2, 3):
        H = xp.stack(held[f]).reshape(a.obs, -1)
        V = xp.stack(offv[f]).reshape(a.obs, -1).astype(xp.int32)
        Wr = xp.stack(offw[f]).reshape(a.obs, -1).astype(xp.int32)
        chg = (H[1:] != H[:-1]).sum(axis=0) >= 2
        idx = xp.nonzero(chg)[0]
        if idx.size == 0:
            res["fields"][f] = {"changing": 0}
            continue
        H, V, Wr = H[:, idx].astype(xp.int32), V[:, idx], Wr[:, idx]

        def distinct(A, skip_neg=False):
            S = xp.sort(A, axis=0)
            nd = (S[1:] != S[:-1]) & ((S[1:] >= 0) if skip_neg else True)
            first = (S[:1] >= 0) if skip_neg else xp.ones((1, S.shape[1]), dtype=bool)
            return B.np.asarray((xp.concatenate([first, nd], axis=0)).sum(axis=0).get()
                                if hasattr(S, "get") else xp.concatenate([first, nd], axis=0).sum(axis=0))
        h, o, w = distinct(H), distinct(V, True), distinct(Wr, True)
        res["fields"][["opcode", "", "arg1", "payload"][f]] = {
            "changing": int(idx.size), "held_mean": float(h.mean()), "offered_mean": float(o.mean()),
            "writers_mean": float(w.mean()),
            "share_offered_le2": float((o <= 2).mean()), "share_writers_ge3": float((w >= 3).mean())}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["fields"]), file=sys.stderr)


if __name__ == "__main__":
    main()
