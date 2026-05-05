"""Bond-rank distribution descriptors.

avg_rank is a scalar summary that loses the shape of the rank profile.
Two TTs with the same avg_rank but different profiles (e.g., (1,1,16,1,1)
vs (4,4,4,4,4)) have the same parameter count ceiling but different
representational structure.

Candidate rank-orthogonal axes for the MAP-Elites grid:
  rank_entropy: Shannon entropy of the normalized rank profile (high =
                uniform distribution; low = concentrated at one bond)
  rank_concentration: max(ranks) / mean(ranks) (1.0 = uniform; higher =
                      peaked)
"""
from __future__ import annotations
import numpy as np


def rank_entropy(ranks: tuple[int, ...]) -> float:
    """Shannon entropy (base-e) of the normalized rank distribution.

    For a uniform profile across b bonds, entropy = log(b); for a profile
    concentrated on one bond, entropy -> 0. Normalize by log(b) for
    comparability across dimensions if needed.
    """
    r = np.array(ranks, dtype=np.float64)
    total = r.sum()
    if total <= 0:
        return 0.0
    p = r / total
    p = np.clip(p, 1e-15, 1.0)
    return float(-np.sum(p * np.log(p)))


def rank_concentration(ranks: tuple[int, ...]) -> float:
    """Peak-to-mean ratio of the rank profile. Uniform -> 1.0; peaked -> > 1.0."""
    r = np.array(ranks, dtype=np.float64)
    mean_r = r.mean()
    if mean_r <= 0:
        return 0.0
    return float(r.max() / mean_r)


def rank_profile_summary(ranks: tuple[int, ...]) -> dict:
    return {
        "avg_rank": float(np.mean(ranks)),
        "max_rank": int(np.max(ranks)),
        "min_rank": int(np.min(ranks)),
        "rank_entropy": rank_entropy(ranks),
        "rank_concentration": rank_concentration(ranks),
    }
