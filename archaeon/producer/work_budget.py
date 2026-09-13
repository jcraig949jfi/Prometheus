"""A deterministic, interruptible work budget for producer selection (S5 phase 0).

S4's computational bound was checked only after a selection returned, so
a single slow selection ran for 30 minutes and the L 32 regime produced
no evidence. This module makes the bound a property of the WORK, not of
the clock: every unit of search (a DFS node in the feasible-set solver, a
(solution x block) convolution step in a partition, a probe scored) is
charged against a budget, and the first charge that exceeds it raises
BudgetExhausted carrying the provenance of what was attempted. The
outcome is explicit (a producer returns BUDGET_EXHAUSTED, never a probe
it did not finish choosing), deterministic (units, not seconds; an
optional wall-clock ceiling exists for safety and is reported as such),
and target-free (the budget sees counts only).

Usage: producers wrap their selection in `with WorkBudget(max_units)`;
the inference and acquisition functions call `charge()` at their inner
loops. With no active budget, charge() is a no-op.
"""
from __future__ import annotations

import contextvars
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

_ACTIVE: contextvars.ContextVar = contextvars.ContextVar("archaeon_work_budget", default=None)


class BudgetExhausted(RuntimeError):
    def __init__(self, provenance: Dict[str, object]):
        super().__init__("work budget exhausted: {}".format(provenance))
        self.provenance = provenance


@dataclass
class WorkBudget:
    max_units: int
    max_seconds: Optional[float] = None
    units: int = 0
    counters: Dict[str, int] = field(default_factory=dict)
    started: float = 0.0
    _token: object = None

    def __enter__(self):
        self.started = time.perf_counter(); self._token = _ACTIVE.set(self); return self

    def __exit__(self, *exc):
        _ACTIVE.reset(self._token); return False

    def provenance(self, phase: str) -> Dict[str, object]:
        return {"outcome": "BUDGET_EXHAUSTED", "phase": phase, "units_used": self.units, "max_units": self.max_units,
                "counters": dict(self.counters), "elapsed_seconds": time.perf_counter() - self.started,
                "wall_ceiling_seconds": self.max_seconds}

    def charge(self, n: int, phase: str) -> None:
        self.units += n
        self.counters[phase] = self.counters.get(phase, 0) + n
        if self.units > self.max_units:
            raise BudgetExhausted(self.provenance(phase))
        if self.max_seconds is not None and (time.perf_counter() - self.started) > self.max_seconds:
            p = self.provenance(phase); p["outcome"] = "BUDGET_EXHAUSTED_WALL"; raise BudgetExhausted(p)


def charge(n: int, phase: str) -> None:
    b = _ACTIVE.get()
    if b is not None:
        b.charge(n, phase)


def active() -> Optional[WorkBudget]:
    return _ACTIVE.get()
