"""
Gauge-invariant behavior descriptors for 3x3 matmul over F_2.

Descriptors operate on canonical (post-gauge-quotient) decompositions.
"""
from __future__ import annotations
import numpy as np

from .gauge import effective_rank, stabilizer_order, ISO_SIZE


SPARSITY_BINS = 5
RANK_MIN_THEORY = 19   # Blaeser 2003 lower bound for 3x3 matmul rank (any field)
RANK_MAX_GRID = 30     # archive upper bound
NAIVE_RANK = 27


def canonical_sparsity(U_c: np.ndarray, V_c: np.ndarray, W_c: np.ndarray) -> float:
    total = U_c.size + V_c.size + W_c.size
    zeros = (U_c == 0).sum() + (V_c == 0).sum() + (W_c == 0).sum()
    return float(zeros) / total


def sparsity_bin(s: float) -> int:
    b = int(s * SPARSITY_BINS)
    return min(max(b, 0), SPARSITY_BINS - 1)


# Stabilizer order divides |Iso| = 6048. Divisors: 1, 2, 3, ..., 6048.
# Bin by log2 buckets for interpretability.
def stabilizer_bin(stab: int) -> int:
    if stab == 1: return 0
    if stab <= 2: return 1
    if stab <= 4: return 2
    if stab <= 8: return 3
    if stab <= 16: return 4
    if stab <= 32: return 5
    if stab <= 64: return 6
    if stab <= 128: return 7
    if stab <= 256: return 8
    return 9   # stabilizers above 256 (up to 6048)


STABILIZER_LABELS = [
    "|stab|=1", "|stab|=2", "|stab|=3-4", "|stab|=5-8",
    "|stab|=9-16", "|stab|=17-32", "|stab|=33-64",
    "|stab|=65-128", "|stab|=129-256", "|stab|>256",
]


def cell_of(U_c: np.ndarray, V_c: np.ndarray, W_c: np.ndarray,
            stab: int) -> tuple[int, int, int]:
    r = effective_rank(U_c, V_c, W_c)
    s = canonical_sparsity(U_c, V_c, W_c)
    return (r, sparsity_bin(s), stabilizer_bin(stab))
