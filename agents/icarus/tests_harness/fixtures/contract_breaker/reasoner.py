"""Fixture: a CONTRACT-BREAKER reasoner. Its apply_batch silently drops
'distractor' steps, returning a shorter list than its input -- the exact
Cycle 14 cardinality break. The Contract Lens must catch this deterministically."""
from __future__ import annotations
from typing import Any


class Reasoner:
    def __init__(self):
        self.version = "fixture-contract-breaker"
        self.supported_ops = ("add", "mul", "sub")

    def apply(self, problem: dict) -> Any:
        if not isinstance(problem, dict):
            return None
        op = None
        for v in problem.values():
            if isinstance(v, str) and v in self.supported_ops:
                op = v
                break
        nums = sorted(
            [(k, v) for k, v in problem.items()
             if isinstance(v, (int, float)) and not isinstance(v, bool)],
            key=lambda kv: kv[0],
        )
        vals = [v for _, v in nums]
        if op is None or len(vals) < 2:
            return None
        if op == "add":
            return vals[0] + vals[1]
        if op == "mul":
            return vals[0] * vals[1]
        if op == "sub":
            return vals[0] - vals[1]
        return None

    def apply_batch(self, problems: list) -> list:
        # BUG (intentional): drops entries whose op is unsupported, breaking
        # positional alignment with the input.
        out = []
        for p in problems:
            r = self.apply(p)
            if r is not None:
                out.append(r)   # <-- distractor steps vanish -> len(out) < len(in)
        return out
