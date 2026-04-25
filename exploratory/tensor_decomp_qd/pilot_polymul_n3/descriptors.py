"""Gauge-invariant descriptors for polymul n=3 over F_2.

All descriptors are computed on canonical-form (post-gauge-quotient)
factor matrices, so they are invariant by construction.

Forbidden-cell discipline:
  Hopcroft-Kerr lower bound on bilinear complexity of polymul-3 over a
  field with at least 5 elements is 5; over F_2 it is 6 (Brown-Dobkin
  / Winograd-style argument: lacking enough distinct interpolation
  points forces 2n = 6 multiplications). We treat rank < 6 as a hard
  forbidden cell — if a candidate canonicalizes to rank < 6, it is a
  canonicalizer bug, not a discovery. Rank 5 is on the soft-watch list;
  if it ever appears we halt and audit.
"""
from __future__ import annotations
import numpy as np

from .gauge import effective_rank, stabilizer_order


# Lower-bound rank we treat as forbidden. 6 over F_2 (per published
# bounds on polymul of degree-2 over F_2). See PILOT_REPORT.md for refs.
RANK_MIN_HARD = 6
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
    """12-element gauge: divisors of 12 are 1, 2, 3, 4, 6, 12. 6 bins."""
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
