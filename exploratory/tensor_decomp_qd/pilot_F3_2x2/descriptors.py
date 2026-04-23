"""Gauge-invariant behavior descriptors for 2x2 matmul over F_3."""
from __future__ import annotations
import numpy as np

from .gauge import effective_rank, stabilizer_order, ISO_SIZE


SPARSITY_BINS = 5
RANK_MIN_THEORY = 7   # Hopcroft-Kerr 1971: rank of 2x2 matmul = 7 over any field
RANK_MAX_GRID = 10
NAIVE_RANK = 8


def canonical_sparsity(U_c, V_c, W_c) -> float:
    total = U_c.size + V_c.size + W_c.size
    zeros = (U_c == 0).sum() + (V_c == 0).sum() + (W_c == 0).sum()
    return float(zeros) / total


def sparsity_bin(s: float) -> int:
    b = int(s * SPARSITY_BINS)
    return min(max(b, 0), SPARSITY_BINS - 1)


def stabilizer_bin(stab: int) -> int:
    if stab <= 2: return 0
    if stab <= 4: return 1
    if stab <= 8: return 2
    if stab <= 16: return 3
    if stab <= 32: return 4
    if stab <= 64: return 5
    return 6


STABILIZER_LABELS = [
    "|stab|<=2", "|stab|=3-4", "|stab|=5-8", "|stab|=9-16",
    "|stab|=17-32", "|stab|=33-64", "|stab|>64",
]


def cell_of(U_c, V_c, W_c, stab):
    r = effective_rank(U_c, V_c, W_c)
    s = canonical_sparsity(U_c, V_c, W_c)
    return (r, sparsity_bin(s), stabilizer_bin(stab))
