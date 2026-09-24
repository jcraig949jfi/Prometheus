"""Counter-based hash randomness (DESIGN.md s2), torch and host forms.

H(k1..kn) chains hash32 over its keys. All values are int64 tensors
holding uint32 bit patterns; the masked low 32 bits of a wrapped int64
product are exact, so GPU, CPU and the oracle agree bit for bit.
"""
from __future__ import annotations

import torch

M32 = 0xFFFFFFFF
C1 = 0x7FEB352D
C2 = 0x846CA68B
H0 = 0x811C9DC5

WAKE, ROUTE, LOSS, LAT, DUP, NOISE, RANDOP, MUT, INIT, ENV, CTRL = range(1, 12)


def hash32_int(x: int) -> int:
    x &= M32
    x ^= x >> 16
    x = (x * C1) & M32
    x ^= x >> 15
    x = (x * C2) & M32
    x ^= x >> 16
    return x


def H_int(*keys: int) -> int:
    h = H0
    for k in keys:
        h = hash32_int(h ^ (int(k) & M32))
    return h


def hash32(x: torch.Tensor) -> torch.Tensor:
    x = x & M32
    x = x ^ (x >> 16)
    x = (x * C1) & M32
    x = x ^ (x >> 15)
    x = (x * C2) & M32
    x = x ^ (x >> 16)
    return x


def chain(h: torch.Tensor, k) -> torch.Tensor:
    """One more key: hash32(h ^ (k & M32)). k: int or int64 tensor."""
    if isinstance(k, torch.Tensor):
        return hash32(h ^ (k & M32))
    return hash32(h ^ (int(k) & M32))


def world_base(ws: torch.Tensor, stream: int, t: int) -> torch.Tensor:
    """H(ws, stream, t) for a [B] int64 tensor of world seeds -> [B]."""
    h = hash32(torch.full_like(ws, H0) ^ (ws & M32))
    h = chain(h, stream)
    return chain(h, t)


def site_base(ws: torch.Tensor, stream: int, t: int, sites: torch.Tensor) -> torch.Tensor:
    """H(ws, stream, t, n) -> [B, N]."""
    return chain(world_base(ws, stream, t)[:, None], sites[None, :])
