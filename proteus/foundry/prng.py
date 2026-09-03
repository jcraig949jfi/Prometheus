"""Deterministic pseudo-random source for the Foundry. splitmix64, pure integer arithmetic.

Python's `random` module is deliberately NOT used anywhere in proteus/foundry: its algorithm is
version-stable but its float and choice paths are not something we want to depend on for
bit-exact replay. Everything here is 64-bit integer arithmetic and reproduces on any Python.

Hierarchical seeding: `derive(tag)` yields an independent stream keyed by (state, tag) through
sha256, so a population seed can be split per organism, per mutation, per probe, without any
stream ever being consumed twice.
"""
from __future__ import annotations

import hashlib

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1


def seed_from(*parts) -> int:
    """64-bit seed from arbitrary parts (ints, strs, bytes), via sha256. Order-sensitive."""
    h = hashlib.sha256()
    for p in parts:
        if isinstance(p, bytes):
            h.update(b"b:" + p)
        elif isinstance(p, int):
            h.update(b"i:" + str(p).encode())
        else:
            h.update(b"s:" + str(p).encode("utf-8"))
        h.update(b"\x00")
    return int.from_bytes(h.digest()[:8], "big")


class SplitMix64:
    __slots__ = ("state",)

    def __init__(self, seed: int):
        self.state = seed & MASK64

    def next_u64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)

    def next_u32(self) -> int:
        return self.next_u64() >> 32

    def randbelow(self, n: int) -> int:
        """Uniform in [0, n). Rejection sampling; no modulo bias."""
        if n <= 0:
            raise ValueError("randbelow needs n > 0")
        limit = (MASK64 + 1) - ((MASK64 + 1) % n)
        while True:
            x = self.next_u64()
            if x < limit:
                return x % n

    def randint(self, lo: int, hi: int) -> int:
        """Uniform in [lo, hi] inclusive."""
        return lo + self.randbelow(hi - lo + 1)

    def unit(self) -> float:
        """Float in [0, 1) from the top 53 bits. Used only for weighted choice."""
        return (self.next_u64() >> 11) / float(1 << 53)

    def choice(self, seq):
        return seq[self.randbelow(len(seq))]

    def weighted(self, items, weights):
        """Choose by integer or float weights. Deterministic given the stream."""
        total = float(sum(weights))
        u = self.unit() * total
        acc = 0.0
        for it, w in zip(items, weights):
            acc += w
            if u < acc:
                return it
        return items[-1]

    def derive(self, *tags) -> "SplitMix64":
        """Independent child stream keyed by current state and tags. Does not advance self."""
        return SplitMix64(seed_from(self.state, *tags))
