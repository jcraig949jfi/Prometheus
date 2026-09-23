"""Deterministic seed derivation for campaign attempts.

Q4 contract: every stochastic draw derives from the attempt_id alone. No clock,
no PYTHONHASHSEED, no id(), no set/dict iteration order. A replay must be
reconstructible from the attempt_id with zero runtime state.

Kept deliberately tiny and dependency-free so it can be folded into an existing
utility if the reuse survey finds one (see CW01-D005 / VI: one definition).
"""
from __future__ import annotations
import hashlib


def seed(attempt_id: str, component: str, index: int = 0) -> int:
    """Return a uint64 seed derived only from (attempt_id, component, index)."""
    if not isinstance(index, int):
        raise TypeError("index must be int; floats are not reproducible across platforms")
    payload = f"{attempt_id}|{component}|{index}".encode("utf-8")
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")


def rng(attempt_id: str, component: str, index: int = 0):
    """numpy Generator seeded from `seed`. PCG64 is stable across numpy versions."""
    import numpy as np
    return np.random.Generator(np.random.PCG64(seed(attempt_id, component, index)))


def draws(attempt_id: str, component: str, n: int, index: int = 0) -> list:
    """n float64 draws; the canonical thing Q4 compares between processes."""
    return rng(attempt_id, component, index).random(n).tolist()
