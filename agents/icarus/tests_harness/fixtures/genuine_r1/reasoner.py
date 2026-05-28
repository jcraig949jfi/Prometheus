"""Fixture: a GENUINE R1 reasoner. Infers operand roles from value type
regardless of key names, so it survives the blind holdout (arbitrary key
renaming, negatives, consistent non-commutative ordering)."""
from __future__ import annotations
from typing import Any


class Reasoner:
    def __init__(self):
        self.version = "fixture-genuine-r1"
        self.supported_ops = ("add", "mul", "sub")

    def _infer(self, problem: dict):
        if not isinstance(problem, dict):
            return None, None, None
        op = None
        for v in problem.values():
            if isinstance(v, str) and v in self.supported_ops:
                op = v
                break
        nums = []
        for k, v in problem.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                nums.append((k, v))
        nums.sort(key=lambda kv: kv[0])  # deterministic operand order by key
        vals = [v for _, v in nums]
        if op is None or len(vals) < 2:
            return None, None, None
        return op, vals[0], vals[1]

    def apply(self, problem: dict) -> Any:
        op, a, b = self._infer(problem)
        if op is None:
            return None
        if op == "add":
            return a + b
        if op == "mul":
            return a * b
        if op == "sub":
            return a - b
        return None

    def apply_batch(self, problems: list) -> list:
        return [self.apply(p) for p in problems]
