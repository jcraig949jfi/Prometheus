"""R5 revised (ChatGPT round 3): counterfactual control is a rung only when RELATIONAL.

Their demotion, adopted with the severity requested: independent counterfactual evaluation
decomposes into branch-generation + R4 execution + comparison — not a new rung. R5 earns
independence in two forms, both built here:

1. COUPLED EXECUTION: a_{k+1} = F(a_k, b_k), b_{k+1} = G(b_k, a_k). Neither branch can be
   run to completion alone; the PAIR is the state. Run-twice-then-diff is impossible by
   construction, not by resource accounting.
2. RELATIONAL INVARIANTS: prove R(s0_k, s1_k) holds THROUGH the computation (e.g.
   noninterference: "flipping premise p can change y but never z"). Endpoint comparison
   certifies a false invariant whenever a violation is TRANSIENT — the executable gap
   between relational execution and run-twice.

The cycle-007 single-pass separation survives as a RESOURCE result (replay is a smuggled
blackboard); this module carries the BEHAVIORAL result their critique demanded.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

State = Tuple[float, float]  # (y, z)


@dataclass
class CoupledBranches:
    """The pair-as-state executor: steps both branches jointly under coupled dynamics."""

    f: Callable[[float, float], float]  # a' = f(a, b)
    g: Callable[[float, float], float]  # b' = g(b, a)
    a: float
    b: float

    def step(self, n: int = 1) -> "CoupledBranches":
        for _ in range(n):
            self.a, self.b = self.f(self.a, self.b), self.g(self.b, self.a)
        return self

    def diff(self) -> float:
        return self.a - self.b


def run_twice_attempt(f, g, a0: float, b0: float, steps: int) -> Optional[float]:
    """The decomposed strategy, tried honestly: run branch A alone, then branch B alone.
    Under coupled dynamics each step of A needs B's CURRENT value, which a sequential
    isolated run does not have — the only sound move is abstention. (Feeding stale b0
    forever is the liar variant; we return None, and a test shows the liar is wrong.)"""
    needs_other = True  # coupled by construction
    return None if needs_other else 0.0


@dataclass
class RelationalExecutor:
    """Maintains and CHECKS a relation R(s0, s1) at every step of a paired execution."""

    invariant: Callable[[State, State], bool]
    violations: List[int] = field(default_factory=list)

    def run(self, s0: State, s1: State, step: Callable[[State], State], n: int) -> Tuple[State, State, bool]:
        for k in range(n):
            s0, s1 = step(s0), step(s1)
            if not self.invariant(s0, s1):
                self.violations.append(k)
        return s0, s1, not self.violations


@dataclass
class GuardedProductState:
    """Their toy, exactly (round 3 restated): a_{k+1} = a_k + 1; b advances by 2 ONLY WHEN
    a_k == b_k. The admissible next step depends on a RELATION between components, not on
    either state alone — so the object is genuinely S x S with guards over relations, and
    run(A); run(B); diff cannot reproduce it (B's transition needs A's contemporaneous value).
    Sharper than cycle-008's arithmetic coupling because the coupling sits in the GUARD."""

    a: int
    b: int

    def step(self, n: int = 1) -> "GuardedProductState":
        for _ in range(n):
            advance_b = (self.a == self.b)
            self.a = self.a + 1
            if advance_b:
                self.b = self.b + 2
        return self


def independent_b_run(b0: int, n: int, a_snapshot: int) -> int:
    """Branch B run in isolation with a FIXED snapshot of A (the only thing a sequential
    strategy has). Whatever snapshot it picks, the guard fires on the wrong steps."""
    b = b0
    for _ in range(n):
        if a_snapshot == b:
            b += 2
    return b


def endpoint_checker(s0: State, s1: State, step: Callable[[State], State], n: int,
                     invariant: Callable[[State, State], bool]) -> bool:
    """Run-twice-and-compare-endpoints: the strategy the transient-violation probe kills."""
    for _ in range(n):
        s0 = step(s0)
    for _ in range(n):
        s1 = step(s1)
    return invariant(s0, s1)
