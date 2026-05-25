"""
Icarus baseline reasoner -- the bootstrap target of self-improvement.

This module IS mutable. Icarus modifies this file (and strategy.py +
generated_tests/) every cycle to climb the Reasoning Ladder.

Starting point: a minimal reasoner that applies one arithmetic operation.
Tier challenge: pass R1's falsification test (apply correctly to
structurally-identical problems with variables renamed).
"""
from __future__ import annotations

from typing import Any


class Reasoner:
    """Minimal baseline reasoner. Phase 0 starting line for R1.

    Method: takes a problem dict {"op": str, "a": int, "b": int}
            applies the operation, returns the result.
    Supported ops: "add", "mul", "sub". (Subset until R2.)
    """

    def __init__(self):
        self.version = "0.1.0-bootstrap"
        self.supported_ops = ("add", "mul", "sub")

    def apply(self, problem: dict) -> Any:
        """Apply the reasoner to one problem. Returns the answer or None."""
        if not isinstance(problem, dict):
            return None
        op = problem.get("op")
        a = problem.get("a")
        b = problem.get("b")
        if op not in self.supported_ops:
            return None
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return None
        if op == "add":
            return a + b
        if op == "mul":
            return a * b
        if op == "sub":
            return a - b
        return None

    def apply_batch(self, problems: list[dict]) -> list[Any]:
        return [self.apply(p) for p in problems]
