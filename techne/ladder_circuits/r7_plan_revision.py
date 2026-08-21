"""R7: global plan revision — abandon a failing strategy and adopt a different one.

Canon Band A. Kill separation (v0.1 probe table): set a problem where the obvious approach
fails PARTWAY. R7 abandons and re-plans; R6 keeps repairing locally.

The hard part is not switching — it is knowing that switching is warranted. Three circuits,
because the interesting content is what separates them:

- LocalRepairer (R6): on failure, fixes the last step and retries the SAME plan. On a
  strategy that is wrong in principle it repairs forever — the executable form of
  "R6 keeps repairing locally".
- PlanReviser (R7): detects that the current plan cannot reach the goal from here and
  switches to a different plan, keeping what the failed attempt TAUGHT (the exhausted set).
- ThrashingSwitcher (the gaming trap): switches on every failure with no memory. It escapes
  the doomed plan by luck and, on adversarial orderings, cycles forever between plans it has
  already tried — passing naive "did it switch?" batteries while never terminating.

The cheaper-mechanism slice for this rung (5th instance of the recurring law): on batteries
where the FIRST alternative plan always works, the thrasher is indistinguishable from a
genuine reviser. Batteries must include problems where several plans fail before one works.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

#: A plan maps a problem to a solution, or None if it cannot solve it.
Plan = Callable[[str], Optional[str]]


@dataclass
class Attempt:
    plan: str
    solved: bool


@dataclass
class LocalRepairer:
    """R6 behaviour: never abandons the plan; repairs and retries, bounded by patience."""

    plans: Dict[str, Plan]
    first_plan: str
    patience: int = 8
    log: List[Attempt] = field(default_factory=list)

    def solve(self, problem: str) -> Tuple[Optional[str], List[Attempt]]:
        plan = self.first_plan
        for _ in range(self.patience):
            out = self.plans[plan](problem)
            self.log.append(Attempt(plan, out is not None))
            if out is not None:
                return out, self.log
            # "local repair": perturb the attempt, same plan
        return None, self.log


@dataclass
class PlanReviser:
    """R7 behaviour: on failure, mark the plan EXHAUSTED for this problem and choose an
    untried one. Terminates: the exhausted set grows monotonically, so no plan is retried."""

    plans: Dict[str, Plan]
    order: List[str]
    log: List[Attempt] = field(default_factory=list)
    exhausted: Set[str] = field(default_factory=set)

    def solve(self, problem: str) -> Tuple[Optional[str], List[Attempt]]:
        for plan in self.order:
            if plan in self.exhausted:
                continue
            out = self.plans[plan](problem)
            self.log.append(Attempt(plan, out is not None))
            if out is not None:
                return out, self.log
            self.exhausted.add(plan)   # the failure TAUGHT something and it is retained
        return None, self.log


@dataclass
class ThrashingSwitcher:
    """The trap: switches eagerly, remembers nothing. Cycles on adversarial orderings."""

    plans: Dict[str, Plan]
    order: List[str]
    budget: int = 12
    log: List[Attempt] = field(default_factory=list)

    def solve(self, problem: str) -> Tuple[Optional[str], List[Attempt]]:
        i = 0
        for _ in range(self.budget):
            plan = self.order[i % len(self.order)]
            out = self.plans[plan](problem)
            self.log.append(Attempt(plan, out is not None))
            if out is not None:
                return out, self.log
            i += 2  # a switching policy with no memory: strides, revisits, never records
        return None, self.log


def distinct_plans_tried(log: List[Attempt]) -> int:
    return len({a.plan for a in log})


def wasted_retries(log: List[Attempt]) -> int:
    """Attempts on a plan already known to fail for this problem — the thrasher's signature."""
    seen_failed: Set[str] = set()
    waste = 0
    for a in log:
        if a.plan in seen_failed:
            waste += 1
        if not a.solved:
            seen_failed.add(a.plan)
    return waste
