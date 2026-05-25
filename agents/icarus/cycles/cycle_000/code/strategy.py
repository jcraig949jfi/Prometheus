"""
Icarus strategy module -- composition + search policy.

This module IS mutable. Icarus modifies it each cycle to improve how the
reasoner composes primitives or selects strategies.

Phase 0 starting line: no composition. Just a passthrough.
"""
from __future__ import annotations

from typing import Callable, Any


class Strategy:
    """Phase 0 stub. Higher tiers will add primitive selection, composition
    graphs, MCTS / bandit policies, etc."""

    def __init__(self):
        self.version = "0.1.0-bootstrap"

    def select_primitives(self, problem: dict) -> list[Callable]:
        """Phase 0: return empty list (no composition yet)."""
        return []

    def compose(self, primitives: list[Callable]) -> Callable:
        """Phase 0: identity (returns first primitive or no-op)."""
        if not primitives:
            return lambda x: x
        return primitives[0]
