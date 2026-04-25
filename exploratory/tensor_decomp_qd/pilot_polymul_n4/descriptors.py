"""Gauge-invariant descriptors for polymul n=4 over F_2.

Forbidden-cell discipline:
  Polymul of two degree-(n-1) polynomials over a sufficiently large field
  has bilinear complexity 2n - 1. Over F_2 the lower bound is higher
  because F_2 lacks evaluation points; for n=4 the best published F_2
  upper bound is 9 (Karatsuba-composed; 3-way also gives 9). Empirical
  lower bound for F_2 polymul-n4 is unsettled; conservative published
  lower bounds give around 7. We treat any canonical rank < 7 as a hard
  forbidden cell — not impossible in principle, but if MAP-Elites lands
  there it is overwhelmingly more likely a canonicalizer / fitness bug.

Note: this is a softer hard kill than polymul-n3 (where 6 was a tight
lower bound). If you genuinely find rank-7 or rank-8 here, that would
be a major result — but we set RANK_MIN_HARD = 7 to keep the discipline.
"""
from __future__ import annotations
import numpy as np

from .gauge import effective_rank, stabilizer_order


# Forbidden hard floor. 7 is below all published rank-9 algorithms; if a
# decomp lands strictly below 7 we treat it as a bug for further inspection.
RANK_MIN_HARD = 7
NAIVE_RANK = 16
RANK_MAX_GRID = 18

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
    """Gauge size 12 (D_3 x Z_2). Divisors: 1, 2, 3, 4, 6, 12."""
    if stab <= 1:
        return 0
    if stab <= 2:
        return 1
    if stab <= 3:
        return 2
    if stab <= 4:
        return 3
    if stab <= 6:
        return 4
    return 5


STABILIZER_LABELS = ["|stab|=1", "|stab|=2", "|stab|=3",
                     "|stab|=4", "|stab|=6", "|stab|=12"]


def cell_of(U_c, V_c, W_c, stab) -> tuple[int, int, int]:
    r = effective_rank(U_c, V_c, W_c)
    s = canonical_sparsity(U_c, V_c, W_c)
    return (r, sparsity_bin(s), stabilizer_bin(stab))
