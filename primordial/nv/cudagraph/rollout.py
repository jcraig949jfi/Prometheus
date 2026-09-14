"""U2: lane E7's closed-loop rollout on device -- brain forward, codebook decode, descriptor
counters and the U1 world step -- judged against E7.rollout (primordial/qd/e7_run.py, read-only).

Family `linear` first. Exactness is by construction, not by tolerance: E7 takes argmax of
np.einsum("nd,nda->na", xs, W) + b in float32, and non-optimized einsum accumulates the
products in feature order from zero, then adds b. The torch forward does the same sequence of
float32 ops (no fused multiply-add), so logits are bitwise equal, not merely argmax-equal.

tick() is the per-step body: fixed shapes, in-place state, no host sync -- the unit a CUDA
graph captures next (U3). Counters are int64 (E7's float64 sums of integers are exact).

usage: python -m primordial.nv.cudagraph.rollout --worlds 4 --genomes 128 --device cuda
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import torch

from .world import TorchWorld

GRID = 33                                    # lane E's descriptor grid (E4.GRID)
FAMILIES = ("linear",)


def linear_logits(obs: torch.Tensor, W: torch.Tensor, b: torch.Tensor, feat_on: torch.Tensor | None):
    """obs int64 [n,S,D]; W float32 [n,D,A]; b [n,A] -> float32 [n,S,A], bitwise == E7's numpy."""
    xs = obs.to(torch.float32) / 65535.0 - 0.5
    if feat_on is not None:
        xs = torch.where(feat_on, xs, 0.0)
    s = torch.zeros(obs.shape[:2] + (W.shape[2],), dtype=torch.float32, device=obs.device)
    for d in range(W.shape[1]):
        s = s + xs[:, :, d, None] * W[:, None, d, :]
    return s + b[:, None, :]


class TorchRollout:
    """g7: lane E's G7 (spec.mech, spec.wid, W, fam). One world, P genomes x k seeds."""

    def __init__(self, g7, device="cuda", world_cheat: str = ""):
        if g7.fam.name not in FAMILIES:
            raise ValueError(f"family must be one of {FAMILIES}")
        self.g7, self.device = g7, torch.device(device)
        self.world = TorchWorld(g7.spec.mech, g7.spec.wid, device=device, cheat=world_cheat)

    def load(self, g, seeds, cheat: bool = False) -> None:
        (W, b), C = g
        dev, P, k = self.device, len(C), len(seeds)
        self.P, self.k = P, k
        self.obs = self.world.reset(np.tile(np.asarray(seeds, np.int64), P))
        genv = torch.arange(P, device=dev).repeat_interleave(k)
        self.W = torch.from_numpy(np.ascontiguousarray(W, np.float32)).to(dev)[genv]
        self.b = torch.from_numpy(np.ascontiguousarray(b, np.float32)).to(dev)[genv]
        self.C = torch.from_numpy(np.ascontiguousarray(C, np.int64)).to(dev)[genv]     # [n,A,Wd]
        D = self.W.shape[1]
        self.feat_on = (torch.arange(D, device=dev) % 2 == 0) if cheat else None       # E7 cheat: xs[:, 1::2] = 0
        n = P * k
        self.abst, self.mag, self.cnt = (torch.zeros(n, dtype=torch.int64, device=dev) for _ in range(3))

    def tick(self) -> None:
        w = self.world
        logits = linear_logits(self.obs, self.W, self.b, self.feat_on)
        idx = logits.argmax(-1)                                                          # [n,S], first max
        a = torch.gather(self.C, 1, idx[:, :, None].expand(-1, -1, self.C.shape[2]))    # [n,S,Wd]
        live = w.alive & ~w.done[:, None]
        x = torch.remainder(a, 8).sum(-1)
        self.abst.add_(((x == 0) & live).sum(1))
        self.mag.add_((x * live).sum(1))
        self.cnt.add_(live.sum(1))
        w.step(a)
        self.obs.copy_(w.observe())                  # in place: a captured graph owns this tensor

    def result(self):
        P, k, Wd = self.P, self.k, self.g7.W
        fit = torch.clamp_min(self.world.charge, 0).sum(1).view(P, k).sum(1).to(torch.int32)
        tot = torch.clamp_min(self.cnt.view(P, k).sum(1), 1).to(torch.float64)
        ab = self.abst.view(P, k).sum(1).to(torch.float64) / tot
        mg = self.mag.view(P, k).sum(1).to(torch.float64) / (tot * Wd * 7)
        cells = torch.round(ab * 32) * GRID + torch.round(torch.clamp(mg, 0, 1) * 32)
        return fit.cpu().numpy(), cells.cpu().numpy().astype(np.uint32)

    def run(self, g, seeds, cheat: bool = False):
        self.load(g, seeds, cheat)
        for _ in range(self.g7.T):
            self.tick()
        return self.result()


def genomes(g7, P: int, seed: int, mutate_steps: int = 3):
    rng = np.random.Generator(np.random.PCG64([770, g7.spec.gen_seed, seed]))
    g = g7.init(rng, P)
    for _ in range(mutate_steps):
        g = g7.mutate(rng, g)
    return g


def compare(gen_seed: int, P: int, seeds, device="cuda", fam: str = "linear", world_cheat: str = "",
            cheat: bool = False, seed: int = 0) -> dict:
    from primordial.qd import e7_run as E7
    g7 = E7.G7(gen_seed, fam)
    g = genomes(g7, P, seed)
    fit_ref, cells_ref, _, _ = E7.rollout(g7, g, np.asarray(seeds, np.int64), world_cheat=world_cheat, cheat=cheat)
    fit, cells = TorchRollout(g7, device, world_cheat).run(g, seeds, cheat)
    return {"gen_seed": gen_seed, "family": fam, "device": str(device), "genomes": P, "seeds": len(seeds),
            "world_cheat": world_cheat or None, "brain_cheat": cheat,
            "fitness_eq": int((fit == fit_ref).sum()), "cells_eq": int((cells == cells_ref).sum())}


def main(argv=None):
    from primordial.qd import e6_run as E6
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="4,1,3")
    ap.add_argument("--genomes", type=int, default=128)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    torch.set_num_threads(1)
    rows = []
    for gs in (int(x) for x in a.worlds.split(",")):
        for name, seeds in (("train", E6.TRAIN), ("held64", E6.HELD64)):
            r = {"seed_set": name, **compare(gs, a.genomes, seeds, a.device)}
            rows.append(r)
            print(json.dumps(r), flush=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")
    return 0 if all(r["fitness_eq"] == r["genomes"] and r["cells_eq"] == r["genomes"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
