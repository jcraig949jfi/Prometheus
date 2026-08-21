"""R6: error detection + local repair — provenance-sensitive diagnosis (round 4, item 1).

Their construction, adopted: rederive-and-diff can be killed BEHAVIOURALLY, no work metering
needed, because proofs are not unique. A from-scratch solver returns a different valid proof
and the diff says "everything changed"; a true localizer names the FIRST INVALID TRANSITION
and repairs minimally, preserving the valid prefix and suffix.

The sharper case, also built: a corrupted derivation whose FINAL ANSWER IS CORRECT (an
invalid step later cancels). Endpoint checking passes. Rederivation produces a clean proof.
Only stepwise validation finds the fault — so R6's object is diagnosis over PROVENANCE, not
the ability to produce a correct derivation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

import sympy as sp


@dataclass(frozen=True)
class Step:
    """One derivation step: a rule name and the expression it claims to produce."""

    rule: str
    result: sp.Expr


#: A rule's semantics: expr -> expr (None = not applicable).
RULES: dict[str, Callable[[sp.Expr], Optional[sp.Expr]]] = {
    "expand": lambda e: sp.expand(e),
    "factor": lambda e: sp.factor(e),
    "add_one": lambda e: e + 1,
    "sub_one": lambda e: e - 1,
    "double": lambda e: sp.expand(2 * e),
    "halve": lambda e: sp.together(e / 2),
    "square": lambda e: sp.expand(e**2),
}


@dataclass
class Derivation:
    start: sp.Expr
    steps: List[Step] = field(default_factory=list)

    @property
    def result(self) -> sp.Expr:
        return self.steps[-1].result if self.steps else self.start


def validate(deriv: Derivation) -> Optional[int]:
    """Stepwise validation: index of the FIRST invalid step, or None if all steps are sound.

    'Valid' = the claimed result equals what the named rule actually produces from the
    previous expression. This is the provenance check; it is blind to the final answer."""
    cur = deriv.start
    for i, step in enumerate(deriv.steps):
        fn = RULES.get(step.rule)
        if fn is None:
            return i
        try:
            expected = fn(cur)
        except Exception:
            return i
        if expected is None or sp.simplify(expected - step.result) != 0:
            return i
        cur = step.result
    return None


def localize_and_repair(deriv: Derivation) -> Tuple[Optional[int], Optional[Derivation]]:
    """R6 behaviour: find the first invalid step and repair it MINIMALLY — recompute that
    one step from its own predecessor, keep the prefix, and re-run the suffix's rules."""
    idx = validate(deriv)
    if idx is None:
        return None, deriv
    cur = deriv.start if idx == 0 else deriv.steps[idx - 1].result
    repaired: List[Step] = list(deriv.steps[:idx])
    for step in deriv.steps[idx:]:
        fn = RULES.get(step.rule)
        if fn is None:
            return idx, None  # unrepairable: unknown rule
        cur = fn(cur)
        repaired.append(Step(step.rule, cur))
    return idx, Derivation(start=deriv.start, steps=repaired)


def rederive_and_diff(deriv: Derivation, fresh_proof: Sequence[str]) -> List[int]:
    """The strategy under test: solve from scratch with a DIFFERENT valid route, then diff
    step-by-step against the corrupted derivation. Returns the indices it flags."""
    cur = deriv.start
    fresh: List[sp.Expr] = []
    for rule in fresh_proof:
        cur = RULES[rule](cur)
        fresh.append(cur)
    flagged = []
    for i in range(max(len(fresh), len(deriv.steps))):
        a = deriv.steps[i].result if i < len(deriv.steps) else None
        b = fresh[i] if i < len(fresh) else None
        if a is None or b is None or sp.simplify(a - b) != 0:
            flagged.append(i)
    return flagged
