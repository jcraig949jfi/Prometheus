"""Fixture: a GOODHART reasoner. Hardcodes the visible-test key names ('a','b')
so it passes the visible R1 falsification test, but fails the blind holdout
(arbitrary key renaming). This is what the harness must catch."""
from __future__ import annotations
from typing import Any


class Reasoner:
    def __init__(self):
        self.version = "fixture-goodhart-r1"
        self.supported_ops = ("add", "mul", "sub")

    def apply(self, problem: dict) -> Any:
        if not isinstance(problem, dict):
            return None
        op = problem.get("op")
        a = problem.get("a")   # hardcoded key names -- the Goodhart
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

    def apply_batch(self, problems: list) -> list:
        return [self.apply(p) for p in problems]
