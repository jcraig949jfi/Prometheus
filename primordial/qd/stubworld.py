"""Stub world for lane E until lane B's batched world lands (owner: lane E).

Genome: 64 bits packed as 8 bytes (big-endian bit order, np.packbits).
Fitness: integer NK landscape, N=64, K=4 (circular neighbourhood), table of
uint16 drawn from a fixed PCG64 seed. Integer-only, deterministic, vectorised.
Descriptor: (popcount of bits 0..31, popcount of bits 32..63) -> 33x33 grid,
cell = d0 * 33 + d1.
"""
from __future__ import annotations

import numpy as np

N_BITS = 64
GLEN = 8
K = 4
GRID = 33
N_CELLS = GRID * GRID


class NKWorld:
    def __init__(self, seed: int = 20260914):
        rng = np.random.Generator(np.random.PCG64(seed))
        self.table = rng.integers(0, 1 << 16, size=(N_BITS, 1 << (K + 1)), dtype=np.int64)
        self._cols = (np.arange(N_BITS)[:, None] + np.arange(K + 1)[None, :]) % N_BITS
        self._w = (1 << np.arange(K + 1)).astype(np.int64)

    def evaluate(self, genomes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """genomes uint8 [B, 8] -> (fit int32 [B], cell uint32 [B])."""
        bits = np.unpackbits(genomes, axis=1).astype(np.int64)          # [B, 64]
        idx = bits[:, self._cols] @ self._w                              # [B, 64]
        fit = self.table[np.arange(N_BITS)[None, :], idx].sum(axis=1)
        d0 = bits[:, :32].sum(axis=1)
        d1 = bits[:, 32:].sum(axis=1)
        return fit.astype(np.int32), (d0 * GRID + d1).astype(np.uint32)


def random_genomes(rng: np.random.Generator, n: int) -> np.ndarray:
    return rng.integers(0, 256, size=(n, GLEN), dtype=np.uint8)


def mutate(rng: np.random.Generator, parents: np.ndarray, p: float = 1.0 / N_BITS) -> np.ndarray:
    bits = np.unpackbits(parents, axis=1)
    flip = (rng.random(bits.shape) < p).astype(np.uint8)
    return np.packbits(bits ^ flip, axis=1)


class BitGenome:
    """Contract Genome adapter (off the hot path)."""

    def __init__(self, g: bytes, world: NKWorld):
        self._g, self._w = bytes(g), world

    def to_bytes(self) -> bytes:
        return self._g

    def descriptor(self) -> np.ndarray:
        bits = np.unpackbits(np.frombuffer(self._g, dtype=np.uint8))
        return np.array([bits[:32].sum(), bits[32:].sum()], dtype=np.float32)
