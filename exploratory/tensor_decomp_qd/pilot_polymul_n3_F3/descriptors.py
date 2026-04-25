"""Gauge-invariant descriptors for polymul n=3 over F_3.

Forbidden-cell discipline:
  Polymul-3 has 5 output coefficients, so by counting the bilinear rank
  is at least 5. Over Q with Toom-Cook 3-way the rank is exactly 5
  (using 5 evaluation points 0, 1, -1, 2, infinity); over F_3 we have
  only 3 finite elements + infinity = 4 evaluation points so Toom-Cook
  3-way does not apply. The published F_3-rank of polymul-3 is 6
  (Karatsuba-3-way still works mod 3); whether rank 5 is achievable
  over F_3 by a non-evaluation algorithm is, to our knowledge, unsettled.

  We treat rank < 5 as a HARD forbidden cell — by counting impossible.
  Rank 5 itself, if found, would be a discovery — we soft-watch and let
  it through but the diagnosis-print will flag it.

Descriptors (all gauge-invariant by construction since computed on
canonical form):
  rank, sparsity_bin, stabilizer_bin
"""
from __future__ import annotations
import numpy as np

from .gauge import effective_rank, stabilizer_order, GAUGE_SIZE


RANK_MIN_HARD = 5
NAIVE_RANK = 9
RANK_MAX_GRID = 12

SPARSITY_BINS = 5


def canonical_sparsity(U_c: np.ndarray, V_c: np.ndarray, W_c: np.ndarray) -> float:
    total = U_c.size + V_c.size + W_c.size
    if total == 0:
        return 0.0
    zeros = (U_c == 0).sum() + (V_c == 0).sum() + (W_c == 0).sum()
    return float(zeros) / total


def sparsity_bin(s: float) -> int:
    b = int(s * SPARSITY_BINS)
    return min(max(b, 0), SPARSITY_BINS - 1)


def stabilizer_bin(stab: int) -> int:
    """Gauge size 48. Divisors: 1, 2, 3, 4, 6, 8, 12, 16, 24, 48. Use 6 bins."""
    if stab <= 1:
        return 0
    if stab <= 2:
        return 1
    if stab <= 4:
        return 2
    if stab <= 8:
        return 3
    if stab <= 16:
        return 4
    return 5


STABILIZER_LABELS = ["|stab|=1", "|stab|=2", "|stab|<=4",
                     "|stab|<=8", "|stab|<=16", "|stab|<=48"]


def cell_of(U_c, V_c, W_c, stab) -> tuple[int, int, int]:
    r = effective_rank(U_c, V_c, W_c)
    s = canonical_sparsity(U_c, V_c, W_c)
    return (r, sparsity_bin(s), stabilizer_bin(stab))
