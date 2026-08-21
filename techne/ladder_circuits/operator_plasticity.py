"""Operator plasticity — the proposed SIXTH coordinate (ChatGPT round 3, item 3).

Their argument, adopted as claim v6-candidate: coordinates 1-5 describe state MECHANICS of a
fixed transition algebra R = {r_1..r_m}. Bands S/G demand constructing NEW operators from
experience — R_t -> R_{t+1}: the machine modifies the language its later reasoning runs in.
(Independently, this is Prometheus's gen-30-wall doctrine: menus must GROW; and it is the
Hephaestus forge stated as a rung axis. External convergence noted — and per doctrine,
convergence is a warning to test, not proof. Hence the kill test, built here.)

Their brutal fake-synthesis kill, implemented: same low-level traces in training, but only a
REUSABLE subprogram survives held-out substitutions.

- TraceCache: memorizes concrete two-step trajectories a->?->c. Perfect on seen inputs,
  dead on unseen ones. (A cached macro without abstraction: "cached macros" rung of their
  plasticity scale, lower half.)
- OperatorSynthesizer: observes that the two-step pattern is f∘f, INSTALLS g := f∘f into
  its rule set, and applies g to inputs never seen in training. The vocabulary changed:
  len(rules) grows, and the new rule is INTENSIONAL (a composition), not a lookup table.

Plasticity scale (theirs): fixed rules -> parameterized compositions -> cached macros ->
induced operators -> revisable abstractions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

Rule = Callable[[int], int]


@dataclass
class TraceCache:
    """Memorizes endpoint pairs of observed two-step chunks. No abstraction anywhere."""

    table: Dict[int, int] = field(default_factory=dict)

    def observe_chunk(self, x: int, fx2: int) -> None:
        self.table[x] = fx2

    def answer_two_step(self, x: int) -> Optional[int]:
        return self.table.get(x)


@dataclass
class OperatorSynthesizer:
    """Starts with rules = {f}. From repeated two-step usage it INDUCES g = f∘f and installs
    it — the transition system itself changes. Held-out substitutions then come free."""

    f: Rule
    rules: Dict[str, Rule] = field(default_factory=dict)
    chunk_observations: int = 0
    install_threshold: int = 3

    def __post_init__(self) -> None:
        self.rules["f"] = self.f

    def observe_chunk(self, x: int, fx2: int) -> None:
        # audit the observation against its own primitive (no blind trust in traces),
        # then count it as evidence for the chunk's reusability
        if self.f(self.f(x)) == fx2:
            self.chunk_observations += 1
        if self.chunk_observations >= self.install_threshold and "g" not in self.rules:
            f = self.f
            self.rules["g"] = lambda v: f(f(v))  # the induced operator: intensional, total

    def answer_two_step(self, x: int) -> Optional[int]:
        g = self.rules.get("g")
        return g(x) if g is not None else None

    def vocabulary(self) -> List[str]:
        return sorted(self.rules)
