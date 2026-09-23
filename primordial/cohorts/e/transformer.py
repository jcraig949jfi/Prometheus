"""E-T2: a basic Transformer brain behind lane C's genome Family interface (SWARM_R2 s3 E).

The genome is a packed float32 parameter vector plus lane E's A x W action codebook (E7.G7), so
the Transformer runs through the SAME rollout (E7.rollout), world oracle (wforge trace hash +
final charge) and brain oracle (ref_logits on clear-margin rows) as every C4 family.

Architecture (one pre-norm-free encoder block, argmax is scale invariant so no final norm):
  tokens   one per obs feature f: h_f = (x_f / 65535 - 0.5) * e_val + e_pos[f]          [D, d]
  attn     H heads, dh = d / H; q, k, v = h Wq, h Wk, h Wv; a = softmax(q k^T / sqrt(dh)) v
           h = h + concat(a) Wo
  mlp      h = h + relu(h W1 + b1) W2 + b2
  pool     mean over tokens, logits = pool Wh + bh                                        [A]
Defaults d = 8, H = 2, hidden = 16: the parameter count and bytes are reported by the Family
(`nf`, `nbytes`), never quoted.

Implementations:
  logits      population-batched numpy float32 (gidx picks each row's genome)
  ref_logits  one genome, one row at a time, float64, explicit loops over tokens and heads
cheat=True zeroes the odd features' values (Linear's cheat), so the brain oracle must mismatch.

  python -m primordial.cohorts.e.transformer --world 4 [--gens 50] [--batch 64] [--run-seeds 0-7]
"""
from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np

from primordial.brain import genomes as gm
from primordial.qd import e7_run as E7


class Transformer(gm.Family):
    name = "transformer"

    def __init__(self, D: int, A: int = 8, d: int = 8, heads: int = 2, hidden: int = 16):
        super().__init__(D, A)
        if d % heads:
            raise ValueError("d must be divisible by heads")
        self.d, self.H, self.h = d, heads, hidden

    def shapes(self):
        D, A, d, h = self.D, self.A, self.d, self.h
        return [(d,), (D, d),                      # e_val, e_pos
                (d, d), (d, d), (d, d), (d, d),    # Wq, Wk, Wv, Wo
                (d, h), (h,), (h, d), (d,),        # W1, b1, W2, b2
                (d, A), (A,)]                      # Wh, bh

    def init(self, rng, P):
        out = []
        for s in self.shapes():
            fan_in = s[0] if len(s) == 2 else 1
            scale = 1.0 / math.sqrt(fan_in) if len(s) == 2 else 0.1
            out.append((scale * rng.standard_normal((P,) + s)).astype(np.float32))
        out[0] = rng.standard_normal((P, self.d)).astype(np.float32)          # value embedding at unit scale
        return tuple(out)

    def _tokens(self, obs, cheat):
        xs = obs.astype(np.float32) / np.float32(65535.0) - np.float32(0.5)
        if cheat:
            xs[:, 1::2] = 0.0
        return xs

    def logits(self, g, obs, gidx, cheat=False):
        ev, ep, Wq, Wk, Wv, Wo, W1, b1, W2, b2, Wh, bh = (x[gidx] for x in g)
        n, D, d, H = len(obs), self.D, self.d, self.H
        dh = d // H
        h = self._tokens(obs, cheat)[:, :, None] * ev[:, None, :] + ep                      # [n, D, d]
        q = np.einsum("nfd,nde->nfe", h, Wq).reshape(n, D, H, dh)
        k = np.einsum("nfd,nde->nfe", h, Wk).reshape(n, D, H, dh)
        v = np.einsum("nfd,nde->nfe", h, Wv).reshape(n, D, H, dh)
        s = np.einsum("nfhe,nghe->nhfg", q, k) / np.float32(math.sqrt(dh))
        s = s - s.max(-1, keepdims=True)
        w = np.exp(s)
        w /= w.sum(-1, keepdims=True)
        a = np.einsum("nhfg,nghe->nfhe", w, v).reshape(n, D, d)
        h = h + np.einsum("nfd,nde->nfe", a, Wo)
        z = np.maximum(np.einsum("nfd,ndh->nfh", h, W1) + b1[:, None, :], 0)
        h = h + np.einsum("nfh,nhd->nfd", z, W2) + b2[:, None, :]
        return np.einsum("nd,nda->na", h.mean(1), Wh) + bh

    def ref_logits(self, g1, obs):
        ev, ep, Wq, Wk, Wv, Wo, W1, b1, W2, b2, Wh, bh = (x.astype(np.float64) for x in g1)
        D, d, H, A = self.D, self.d, self.H, self.A
        dh = d // H
        out = np.zeros((len(obs), A))
        for i, row in enumerate(obs):
            tok = [(int(row[f]) / 65535.0 - 0.5) * ev + ep[f] for f in range(D)]
            q = [t @ Wq for t in tok]
            k = [t @ Wk for t in tok]
            v = [t @ Wv for t in tok]
            new = []
            for f in range(D):
                cat = np.zeros(d)
                for hd in range(H):
                    sl = slice(hd * dh, (hd + 1) * dh)
                    sc = [float(q[f][sl] @ k[j][sl]) / math.sqrt(dh) for j in range(D)]
                    m = max(sc)
                    ex = [math.exp(x - m) for x in sc]
                    tot = sum(ex)
                    for j in range(D):
                        cat[sl] += (ex[j] / tot) * v[j][sl]
                t = tok[f] + cat @ Wo
                t = t + np.maximum(t @ W1 + b1, 0.0) @ W2 + b2
                new.append(t)
            pool = sum(new) / D
            out[i] = pool @ Wh + bh
        return out


class GT(E7.G7):
    """E7's genome (family params + lane E codebook) with the Transformer family."""

    def __init__(self, gen_seed: int, **kw):
        self.spec = E7.E4.Spec(gen_seed)
        m = self.spec.mech
        self.D, self.S, self.W, self.T = len(m.obs_perm), m.n_slots, m.act_width, m.horizon
        self.fam = Transformer(self.D, E7.A, **kw)
        self.pb, self.cb = self.fam.nbytes, E7.A * self.W
        self.glen = (self.pb + self.cb + 3) // 4 * 4


def main(argv=None) -> int:
    from primordial.cohorts.e.transfer import ROWS_DIR, NpArchive, parse_seeds
    from primordial.fabric.rows import RowWriter

    ap = argparse.ArgumentParser()
    ap.add_argument("--world", type=int, default=4); ap.add_argument("--gens", type=int, default=50)
    ap.add_argument("--batch", type=int, default=64); ap.add_argument("--run-seeds", default="0-7")
    ap.add_argument("--tag", default="full"); ap.add_argument("--exp", default="E-T2-transformer-baseline")
    ap.add_argument("--skip-oracles", action="store_true")
    a = ap.parse_args(argv)
    gt = GT(a.world)
    seeds = parse_seeds(a.run_seeds)
    with RowWriter(ROWS_DIR / f"{a.exp}.jsonl", a.exp) as w:
        for rs in seeds:
            t0 = time.perf_counter()
            rng = np.random.Generator(np.random.PCG64([2701, rs, a.world]))
            arch = NpArchive(gt.glen)
            for t in range(a.gens):
                g = gt.init(rng, a.batch) if t == 0 else gt.mutate(rng, gt.unpack(arch.sample(rng, a.batch)))
                fit, cells = E7.rollout(gt, g, E7.TRAIN)[:2]
                arch.insert(cells, fit, gt.pack(g))
            top = arch.top(E7.TOP)
            tg = gt.unpack(top)
            row = {"status": "record" if a.tag == "full" else "dev", "tag": a.tag, "family": "transformer",
                   "world": a.world, "run_seed": rs, "gens": a.gens, "batch": a.batch,
                   "genomes": a.gens * a.batch, "param_count": gt.fam.nf, "param_bytes": gt.pb,
                   "genome_bytes": gt.glen, "d": gt.fam.d, "heads": gt.fam.H, "hidden": gt.fam.h,
                   "cells": len(arch),
                   "train_per_seed": float(E7.rollout(gt, tg, E7.TRAIN)[0].mean() / len(E7.TRAIN)),
                   "held64_per_seed": float(E7.rollout(gt, tg, E7.HELD64)[0].mean() / len(E7.HELD64))}
            if rs == seeds[0] and not a.skip_oracles:
                row["world_oracle_honest"] = E7.world_oracle(gt, tg, E7.HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(gt, tg, E7.HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(gt, tg, E7.HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(gt, tg, E7.HELD8, cheat=True)
            row["wall_s"] = round(time.perf_counter() - t0, 1)
            w.write(row)
            print(json.dumps(row), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
