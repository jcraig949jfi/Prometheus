"""U4: lane C's brain families as torch forwards whose float32 logits are BITWISE equal to
the numpy forward lane E7 actually runs (primordial/brain/genomes.py, read-only).

Bitwise, not argmax-tolerant, because each forward repeats numpy's op sequence:
non-optimized np.einsum accumulates products in index order starting from zero, and every
other op is elementwise IEEE float32. No fused multiply-add is used, so torch on cpu and cuda
produces the same bits.

  linear     xs = obs/65535 - 0.5 (odd features zeroed under the cheat);
             logits = sum_d xs_d W[d] (from zero), then + b
  tt_digits  digits of obs & 0xFFFF, most significant first, core c = feature c//4;
             v = alpha; per core (odd cores skipped under the cheat):
             v = sum_r v_r G[c, digit][r] (from zero); v /= max(max|v|, 1e-30);
             logits = sum_r v_r Wo[r] (from zero)

Every tensor a captured CUDA graph reads is listed by tensors(); the forward allocates
nothing persistent and never syncs.
"""
from __future__ import annotations

import numpy as np
import torch

EPS = 1e-30


def _t(x, dtype, dev):
    return torch.from_numpy(np.ascontiguousarray(x, dtype)).to(dev)


def linear_logits(obs: torch.Tensor, W: torch.Tensor, b: torch.Tensor, feat_on: torch.Tensor | None):
    """obs int64 [n,S,D]; W float32 [n,D,A]; b [n,A] -> float32 [n,S,A]."""
    xs = obs.to(torch.float32) / 65535.0 - 0.5
    if feat_on is not None:
        xs = torch.where(feat_on, xs, 0.0)
    s = torch.zeros(obs.shape[:2] + (W.shape[2],), dtype=torch.float32, device=obs.device)
    for d in range(W.shape[1]):
        s = s + xs[:, :, d, None] * W[:, None, d, :]
    return s + b[:, None, :]


class LinearBrain:
    name = "linear"

    def __init__(self, params, genv: torch.Tensor, cheat: bool = False):
        W, b = params
        dev = genv.device
        self.W = _t(W, np.float32, dev)[genv]                                # [n,D,A]
        self.b = _t(b, np.float32, dev)[genv]                                # [n,A]
        D = self.W.shape[1]
        self.feat_on = (torch.arange(D, device=dev) % 2 == 0) if cheat else None

    def tensors(self) -> list[torch.Tensor]:
        return [self.W, self.b]

    def logits(self, obs: torch.Tensor) -> torch.Tensor:
        """obs int64 [n,S,D] -> float32 [n,S,A]."""
        return linear_logits(obs, self.W, self.b, self.feat_on)


class TTDigitsBrain:
    name = "tt_digits"

    def __init__(self, params, genv: torch.Tensor, cheat: bool = False):
        al, G, Wo = params
        dev = genv.device
        self.al = _t(al, np.float32, dev)[genv]                              # [n,r]
        self.G = _t(G, np.float32, dev)                                      # [P,4D,16,r,r], not replicated
        self.Wo = _t(Wo, np.float32, dev)[genv]                              # [n,r,A]
        self.genv = genv[:, None].clone()                                    # [n,1]
        self.shift = torch.tensor([12, 8, 4, 0], dtype=torch.int64, device=dev)
        self.cores = list(range(0, self.G.shape[1], 2 if cheat else 1))

    def tensors(self) -> list[torch.Tensor]:
        return [self.al, self.G, self.Wo, self.genv]

    def logits(self, obs: torch.Tensor) -> torch.Tensor:
        n, S, D = obs.shape
        r = self.al.shape[1]
        dig = ((obs & 0xFFFF)[:, :, :, None] >> self.shift & 15).reshape(n, S, 4 * D)
        v = self.al[:, None, :].expand(n, S, r)
        for c in self.cores:
            g = self.G[self.genv, c, dig[:, :, c]]                           # [n,S,r,r]
            u = torch.zeros((n, S, r), dtype=torch.float32, device=obs.device)
            for a in range(r):
                u = u + v[:, :, a, None] * g[:, :, a, :]
            v = u / torch.clamp_min(u.abs().amax(-1, keepdim=True), EPS)
        out = torch.zeros((n, S, self.Wo.shape[2]), dtype=torch.float32, device=obs.device)
        for a in range(r):
            out = out + v[:, :, a, None] * self.Wo[:, None, a, :]
        return out


BRAINS = {b.name: b for b in (LinearBrain, TTDigitsBrain)}
