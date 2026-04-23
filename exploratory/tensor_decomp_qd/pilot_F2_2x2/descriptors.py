"""
Gauge-invariant behavior descriptors for MAP-Elites.

All descriptors operate on a CANONICAL form (post-gauge-quotient), so they
are invariant under the gauge group by construction.

Over F_2 with 2x2 matmul, we defer the Jacobian / moduli-dimension descriptor
per James's scope call — combinatorial invariants only in this pilot.
"""
from __future__ import annotations
import numpy as np

from .gauge import effective_rank, stabilizer_order


SPARSITY_BINS = 5   # quintiles: 0..20%, 20..40%, 40..60%, 60..80%, 80..100%
RANK_MIN = 7        # matmul-2x2 has rank exactly 7 over any field
RANK_MAX = 12       # upper bound for archive grid


def canonical_sparsity(U_c: np.ndarray, V_c: np.ndarray, W_c: np.ndarray) -> float:
    """Fraction of zero entries across the three factor matrices (canonical form).

    Gauge-invariant when computed on canonical-form (U_c, V_c, W_c) because
    canonicalization is a function of the gauge orbit.
    """
    total = U_c.size + V_c.size + W_c.size
    zeros = (U_c == 0).sum() + (V_c == 0).sum() + (W_c == 0).sum()
    return float(zeros) / total


def sparsity_bin(s: float) -> int:
    """Bin canonical sparsity into SPARSITY_BINS quintiles."""
    b = int(s * SPARSITY_BINS)
    return min(max(b, 0), SPARSITY_BINS - 1)


def stabilizer_bin(stab: int) -> int:
    """Bin stabilizer order. Divisors of 24: 1, 2, 3, 4, 6, 8, 12, 24.

    We collapse to: 1, 2, 3, 4-6, 8-12, 24 (6 bins).
    """
    if stab == 1: return 0
    if stab == 2: return 1
    if stab == 3: return 2
    if stab <= 6: return 3
    if stab <= 12: return 4
    return 5


STABILIZER_LABELS = ["|stab|=1", "|stab|=2", "|stab|=3", "|stab|=4-6",
                     "|stab|=8-12", "|stab|=24"]


def cell_of(U_c: np.ndarray, V_c: np.ndarray, W_c: np.ndarray,
            stab: int) -> tuple[int, int, int]:
    """Return (rank_cell, sparsity_cell, stabilizer_cell) for an elite.

    Rank cell is the effective rank directly (no binning needed at this scope).
    """
    r = effective_rank(U_c, V_c, W_c)
    s = canonical_sparsity(U_c, V_c, W_c)
    return (r, sparsity_bin(s), stabilizer_bin(stab))
